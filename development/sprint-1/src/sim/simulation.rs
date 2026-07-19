//! The simulation loop (Phase 2 / 4): advances the clock and moves residents
//! through their routines. Deterministic; every state change is observable via
//! the event log.

use std::collections::{BTreeMap, BTreeSet};

use crate::sim::clock::{WorldClock, TICKS_PER_DAY};
use crate::sim::intention;
use crate::sim::resident::{Memory, Resident, Status};
use crate::sim::routine::Routine;
use crate::sim::social::{self, Relationships};
use crate::world::location::LocationId;
use crate::world::navigation::NavGraph;
use crate::world::{build_world, World};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Event {
    pub tick: u64,
    pub day: u64,
    pub hour: u64,
    pub resident: &'static str,
    pub message: String,
}

pub struct Simulation {
    pub world: World,
    pub clock: WorldClock,
    pub residents: Vec<Resident>,
    pub relationships: Relationships,
    pub log: Vec<Event>,
    /// Structured record of every interaction (observability / tests / Oak).
    pub interactions: Vec<social::Interaction>,
    last_day: u64,
    /// Pairs that have already interacted today (once-per-day cap).
    social_seen_today: BTreeSet<(&'static str, &'static str)>,
}

fn edge_weight(nav: &NavGraph, a: LocationId, b: LocationId) -> u32 {
    nav.neighbors(a)
        .into_iter()
        .find(|(n, _)| *n == b)
        .map(|(_, w)| w)
        .unwrap_or_else(|| nav.travel_time(a, b).unwrap_or(1))
}

impl Simulation {
    pub fn new(residents: Vec<Resident>) -> Self {
        Simulation {
            world: build_world(),
            clock: WorldClock::new(),
            residents,
            relationships: Relationships::seeded(),
            log: Vec::new(),
            interactions: Vec::new(),
            last_day: 0,
            social_seen_today: BTreeSet::new(),
        }
    }

    pub fn run(&mut self, days: u64) {
        for _ in 0..(days * TICKS_PER_DAY) {
            self.step();
        }
    }

    /// Advance one tick.
    pub fn step(&mut self) {
        let day = self.clock.day();
        let day_rolled = day != self.last_day;
        if day_rolled {
            for r in &mut self.residents {
                r.done_today.clear();
                r.deviations_today = 0;
            }
            self.social_seen_today.clear();
            self.last_day = day;
        }
        let hour = self.clock.hour();
        let weekday = self.clock.weekday();

        // Snapshot of where everyone is at the start of the tick (for the
        // intention layer to read without borrowing residents mutably).
        let presence: Vec<crate::sim::intention::Presence> = self
            .residents
            .iter()
            .map(|r| (r.id, r.name, r.place, r.is_present()))
            .collect();

        // --- movement + activity selection ---
        // Disjoint borrows: nav (read) + residents (write) + log (write) + clock.
        {
        let Simulation { world, residents, log, clock, relationships, .. } = self;
        let nav: &NavGraph = &world.nav;

        for r in residents.iter_mut() {
            // 1) advance the current status by one step.
            let status = std::mem::replace(&mut r.status, Status::Idle);
            match status {
                Status::Performing { activity, left } => {
                    if left > 1 {
                        r.status = Status::Performing { activity, left: left - 1 };
                    } else if !day_rolled {
                        // finished -> Idle (selects below)
                        r.done_today.push(activity);
                    }
                    // If the day just rolled over, this activity was carried in
                    // from yesterday; let it finish without marking today's list,
                    // so the resident may still do it again today (e.g. go home).
                }
                Status::Traveling { activity, purpose, dest, dur, path, mut idx, leg_left } => {
                    if leg_left > 1 {
                        r.status = Status::Traveling {
                            activity, purpose, dest, dur, path, idx, leg_left: leg_left - 1,
                        };
                    } else {
                        idx += 1;
                        r.place = path[idx];
                        if r.place == dest {
                            r.status = Status::Performing { activity, left: dur };
                            log.push(Event {
                                tick: clock.tick, day: clock.day(), hour: clock.hour(),
                                resident: r.name,
                                message: format!("{purpose} — at {}", r.place),
                            });
                        } else {
                            let leg = edge_weight(nav, path[idx], path[idx + 1]);
                            r.status = Status::Traveling {
                                activity, purpose, dest, dur, path, idx, leg_left: leg,
                            };
                        }
                    }
                }
                Status::Idle => {}
            }

            // 2) if idle, select the next activity and start it (this tick).
            if let Status::Idle = r.status {
                // Resolve to owned values so the immutable borrow of `r` ends
                // before we mutate its status/place below.
                let choice = r
                    .select(hour, weekday, world)
                    .map(|a| (a.id, a.purpose, a.duration, Routine::target_location(a, r.home)));

                // Intention layer: a resident about to head home may instead
                // detour to join a nearby friend (Phase 5). The routine remains
                // the default; deviation only overrides a plan to go home.
                let plan = match choice {
                    Some((aid, apurpose, adur, Some(dest))) => {
                        let heading_home = dest == r.home;
                        let deviation = if heading_home {
                            intention::consider_social_detour(
                                r, hour, clock.tick, &presence, relationships, world, nav,
                            )
                        } else {
                            None
                        };
                        match deviation {
                            Some(dev) => {
                                log.push(Event {
                                    tick: clock.tick, day: clock.day(), hour: clock.hour(),
                                    resident: r.name, message: dev.reason,
                                });
                                r.deviations_today += 1;
                                Some((dev.activity_id, dev.purpose, dev.duration, dev.dest))
                            }
                            None => Some((aid, apurpose, adur, dest)),
                        }
                    }
                    _ => None,
                };

                if let Some((aid, apurpose, adur, dest)) = plan {
                    {
                        if dest == r.place {
                            r.status = Status::Performing { activity: aid, left: adur };
                            log.push(Event {
                                tick: clock.tick, day: clock.day(), hour: clock.hour(),
                                resident: r.name,
                                message: format!("{apurpose} — at {}", r.place),
                            });
                        } else if let Some(path) = nav.shortest_path(r.place, dest) {
                            let leg = edge_weight(nav, path[0], path[1]);
                            let route = path.join(" -> ");
                            log.push(Event {
                                tick: clock.tick, day: clock.day(), hour: clock.hour(),
                                resident: r.name,
                                message: format!("sets out for {dest} ({apurpose}) via {route}"),
                            });
                            r.status = Status::Traveling {
                                activity: aid, purpose: apurpose, dest, dur: adur,
                                path, idx: 0, leg_left: leg,
                            };
                        }
                    }
                }
            }
        }
        } // end movement borrow scope

        // --- social interactions among co-located residents ---
        self.social_pass();

        self.clock.advance();
    }

    /// Co-located residents at a public place during a compatible window may
    /// interact. Deterministic; consequences applied through the owners
    /// (relationships store + each resident's own memories).
    fn social_pass(&mut self) {
        let hour = self.clock.hour();
        // Compatible window: daytime and evening only (not the small hours).
        if !(7..=21).contains(&hour) {
            return;
        }
        let day = self.clock.day();
        let tick = self.clock.tick;

        // Group present residents by public place (skip travellers & residences).
        let mut by_place: BTreeMap<LocationId, Vec<usize>> = BTreeMap::new();
        for (i, r) in self.residents.iter().enumerate() {
            if !r.is_present() {
                continue;
            }
            let residential = self
                .world
                .location(r.place)
                .map(|l| l.is_residential())
                .unwrap_or(false);
            if residential {
                continue;
            }
            by_place.entry(r.place).or_default().push(i);
        }

        // Phase 1 — decide (immutable reads only). Deterministic order.
        struct Apply {
            a: &'static str,
            b: &'static str,
            place: LocationId,
            kind: social::InteractionKind,
            reason: &'static str,
        }
        let mut applies: Vec<Apply> = Vec::new();
        let mut busy = vec![false; self.residents.len()];
        for (place, idxs) in &by_place {
            for x in 0..idxs.len() {
                for y in (x + 1)..idxs.len() {
                    let (ia, ib) = (idxs[x], idxs[y]);
                    if busy[ia] || busy[ib] {
                        continue;
                    }
                    let (aid, bid) = (self.residents[ia].id, self.residents[ib].id);
                    let pair = if aid <= bid { (aid, bid) } else { (bid, aid) };
                    if self.social_seen_today.contains(&pair) {
                        continue;
                    }
                    let rel = self.relationships.get(pair.0, pair.1);
                    if let Some(outcome) = social::decide(pair.0, pair.1, place, tick, rel) {
                        busy[ia] = true;
                        busy[ib] = true;
                        applies.push(Apply {
                            a: pair.0,
                            b: pair.1,
                            place,
                            kind: outcome.kind,
                            reason: outcome.reason,
                        });
                    }
                }
            }
        }

        // Phase 2 — apply consequences through the owners.
        for ap in applies {
            let (d_aff, d_trust) = ap.kind.deltas();
            let (before, after) = self.relationships.adjust(ap.a, ap.b, d_aff, d_trust);
            let a_name = self.name_of(ap.a);
            let b_name = self.name_of(ap.b);
            let place_name = self.world.location(ap.place).map(|l| l.name).unwrap_or(ap.place);
            let verb = ap.kind.verb();

            if let Some(ra) = self.residents.iter_mut().find(|r| r.id == ap.a) {
                ra.memories.push(Memory {
                    day,
                    hour,
                    note: format!("{verb} with {b_name} at the {place_name}"),
                    other: Some(ap.b),
                });
            }
            if let Some(rb) = self.residents.iter_mut().find(|r| r.id == ap.b) {
                rb.memories.push(Memory {
                    day,
                    hour,
                    note: format!("{verb} with {a_name} at the {place_name}"),
                    other: Some(ap.a),
                });
            }
            self.social_seen_today.insert((ap.a, ap.b));
            self.interactions.push(social::Interaction {
                tick,
                day,
                hour,
                a: ap.a,
                b: ap.b,
                kind: ap.kind,
                place: ap.place,
            });
            self.log.push(Event {
                tick,
                day,
                hour,
                resident: a_name,
                message: format!(
                    "{a_name} and {b_name} {verb} at the {place_name} — {reason} \
                     (affinity {}→{}, trust {}→{})",
                    before.affinity, after.affinity, before.trust, after.trust,
                    reason = ap.reason,
                ),
            });
        }
    }

    fn name_of(&self, id: &str) -> &'static str {
        self.residents.iter().find(|r| r.id == id).map(|r| r.name).unwrap_or("someone")
    }

    pub fn resident(&self, id: &str) -> Option<&Resident> {
        self.residents.iter().find(|r| r.id == id)
    }
}

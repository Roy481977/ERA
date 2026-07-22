//! The simulation loop (Phase 2 / 4): advances the clock and moves residents
//! through their routines. Deterministic; every state change is observable via
//! the event log.

use std::collections::{BTreeMap, BTreeSet};

use crate::sim::ambient::{self, Ambient, AmbientKind};
use crate::sim::clock::{WorldClock, DAYS_PER_WEEK, MINUTES_PER_TICK, TICKS_PER_DAY, TICKS_PER_HOUR, TRAVEL_TICKS_PER_WEIGHT};
use crate::sim::dog::Dog;
use crate::sim::festival;
use crate::sim::intention;
use crate::sim::matchday::{self, MatchResult};
use crate::sim::oak::{OakEvent, OakEventKind, OldOak, Season};
use crate::sim::possessions::Possessions;
use crate::sim::resident::{Memory, Resident, Status};
use crate::sim::rng::Rng;
use crate::sim::routine::Routine;
use crate::sim::social::{self, Bonds, Relationships};
use crate::sim::weather::Weather;
use crate::sim::wildlife::Wildlife;
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
    pub bonds: Bonds,
    pub oak: OldOak,
    pub dog: Dog,
    /// The district's animals — persistent, living entities.
    pub wildlife: Wildlife,
    /// Seeded generator for the small, genuine unpredictability of wildlife. A
    /// given seed always replays the same animal life; a different seed grows a
    /// different one. Residents do not draw from it and stay deterministic.
    pub rng: Rng,
    pub world_seed: u64,
    /// Today's weather — deterministic in (day, season, seed). Re-dressed at each
    /// day roll. A wet or cold day dampens outdoor dawdling.
    pub weather: Weather,
    /// What residents own and, by derivation, wear — evolving over the seasons.
    pub possessions: Possessions,
    pub log: Vec<Event>,
    /// Ambient life — the town's routines, micro-life, and residents' small
    /// moments. A layer over the behavioural log (Sprint 3 — density).
    pub ambient: Vec<Ambient>,
    /// Structured record of every interaction (observability / tests / Oak).
    pub interactions: Vec<social::Interaction>,
    last_day: u64,
    /// Pairs that have already interacted today (once-per-day cap).
    social_seen_today: BTreeSet<(&'static str, &'static str)>,
    /// Matchdays whose Oak consequence (scarf / flowers) has been recorded.
    oak_matchday_days: BTreeSet<u64>,
}

const LINGER_CAP: u32 = 2;
/// How many ticks a linger adds each time (a short "little longer").
const LINGER_TICKS: u32 = 2;

/// Convert a whole-hour duration (as routines are authored) into ticks.
fn hours_to_ticks(hours: u32) -> u32 {
    hours * TICKS_PER_HOUR as u32
}

/// Whether a resident whose activity is ending should linger — a close friend is
/// present at the same public place, it isn't yet night, and they haven't lingered
/// too much today. Returns the friend's name for the log.
fn linger_with_friend(
    r: &Resident,
    hour: u64,
    weather_appeal: i32,
    presence: &[intention::Presence],
    rels: &Relationships,
    world: &World,
) -> Option<&'static str> {
    if hour >= 18 || r.lingered_today >= LINGER_CAP {
        return None;
    }
    // Someone tired, out of sorts, or caught in poor weather doesn't dawdle.
    if r.social_readiness() + weather_appeal < 0 {
        return None;
    }
    if world.location(r.place).map(|l| l.is_residential()).unwrap_or(true) {
        return None; // only linger in public places, not at home
    }
    presence
        .iter()
        .find(|(fid, _, fplace, present)| {
            *present && *fid != r.id && *fplace == r.place && rels.get(r.id, fid).affinity >= 3
        })
        .map(|(_, fname, _, _)| *fname)
}

/// If the activity a resident just began is a visit to the Old Oak, record it as
/// an Oak event and give the resident a memory of it.
fn record_oak_visit(
    r: &mut Resident,
    activity_id: &str,
    clock: &WorldClock,
    out: &mut Vec<OakEvent>,
) {
    if r.affordance_of(activity_id) != Some("VISIT_OAK") {
        return;
    }
    let kind = if r.is_child() {
        OakEventKind::ChildrenPlay
    } else {
        OakEventKind::Visit
    };
    out.push(OakEvent {
        day: clock.day(),
        hour: clock.hour(),
        kind,
        who: Some(r.id),
        with: None,
    });
    r.memories.push(Memory {
        day: clock.day(),
        hour: clock.hour(),
        note: "sat with the Old Oak by the riverside".to_string(),
        other: None,
    });
}

fn edge_weight(nav: &NavGraph, a: LocationId, b: LocationId) -> u32 {
    nav.neighbors(a)
        .into_iter()
        .find(|(n, _)| *n == b)
        .map(|(_, w)| w)
        .unwrap_or_else(|| nav.travel_time(a, b).unwrap_or(1))
}

const COMPANION_AFFINITY: i32 = 3;
const WAIT_CAP: u32 = 3;
/// How long a spontaneous shared outing lasts (ticks) — long enough to be "a
/// while together", not a token stop.
const SHARED_TICKS: u32 = 4;
/// A shared plan must let both friends get there, stay, and reach home by here.
const LEISURE_END: u64 = 22;
/// A friend is "finishing up" during the last stretch of their activity — a
/// short window (not a single five-minute tick), so a companion can catch them.
const FINISHING_TICKS: u32 = 3;

/// A resident's intended next action, formed in the DECIDE phase before anyone
/// moves — so friends can coordinate in RECONCILE before they ACT.
struct Intent {
    idx: usize,
    aid: &'static str,
    purpose: &'static str,
    dur: u32,
    dest: LocationId,
    /// True if this intent is a spontaneous deviation (reason set).
    deviation: bool,
    reason: Option<String>,
}

/// The outcome of reconciliation: who leaves together, and who waits for whom.
#[derive(Default)]
struct Coord {
    /// idx -> partner idx: they set off together (same place, same destination).
    together: BTreeMap<usize, usize>,
    /// idx -> (partner idx, split place): two friends bound for *different* places
    /// whose routes share the first stretch — they walk it together, then part at
    /// the split place. Companionable travel without a shared plan.
    partial: BTreeMap<usize, (usize, LocationId)>,
    /// idx -> friend name: this resident waits this tick to leave with them.
    waiting: BTreeMap<usize, &'static str>,
}

/// The default world seed — so `Simulation::new` is fully reproducible. Pass a
/// different seed (`with_seed`) to grow a different wildlife life.
pub const DEFAULT_WORLD_SEED: u64 = 0x0E5A_1F00_D0_u64;

impl Simulation {
    pub fn new(residents: Vec<Resident>) -> Self {
        Self::with_seed(residents, DEFAULT_WORLD_SEED)
    }

    /// A simulation whose wildlife is grown from a specific seed. Everything else
    /// (the residents, the town) is identical regardless of seed.
    pub fn with_seed(residents: Vec<Resident>, seed: u64) -> Self {
        Simulation {
            world: build_world(),
            clock: WorldClock::new(),
            residents,
            relationships: Relationships::seeded(),
            bonds: Bonds::default(),
            oak: OldOak::new(),
            dog: Dog::new(),
            wildlife: Wildlife::new(),
            rng: Rng::new(seed),
            world_seed: seed,
            weather: Weather::for_day(0, Season::for_day(0), seed),
            possessions: Possessions::new(),
            log: Vec::new(),
            ambient: Vec::new(),
            interactions: Vec::new(),
            last_day: 0,
            social_seen_today: BTreeSet::new(),
            oak_matchday_days: BTreeSet::new(),
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
                r.lingered_today = 0;
                r.waited_today = 0;
                r.energy = 1.0; // woke rested
            }
            self.social_seen_today.clear();
            self.last_day = day;
            // Re-dress the world for the new day: today's weather; and, at the
            // start of each week, any lasting keepsakes residents have gathered.
            let season = Season::for_day(day);
            self.weather = Weather::for_day(day, season, self.world_seed);
            if day % DAYS_PER_WEEK == 0 {
                let ids: Vec<&'static str> = self.residents.iter().map(|r| r.id).collect();
                self.possessions.accrete(&ids, day / DAYS_PER_WEEK, self.world_seed);
            }
        }
        // How inviting it is to be outdoors today — folds into the spontaneous
        // outdoor-social gates below, so a wet day changes how the town moves.
        let weather_appeal = self.weather.outdoor_appeal();

        // Disposition drifts a little each tick before anyone decides anything:
        // energy wanes or recovers with where they are, mood eases toward neutral.
        // Every social gate below reads the result, so the same town behaves
        // differently morning vs. night, and person to person.
        for r in &mut self.residents {
            r.tick_disposition();
        }
        let hour = self.clock.hour();
        let minute = self.clock.minute();
        let weekday = self.clock.weekday();
        let match_result = MatchResult::for_week(day / DAYS_PER_WEEK);

        // Matchday buildup: district-wide announcements as the day unfolds. Once
        // per hour (on the hour), not every five-minute tick.
        if matchday::is_matchday(weekday) && self.clock.on_the_hour() {
            let note = match hour {
                8 => Some("Matchday. The Bakery opens early and scarves come out along the High Street.".to_string()),
                14 => Some("Supporters are making their way to the Stadium.".to_string()),
                h if h == matchday::KICKOFF => Some("Kick-off at the Stadium.".to_string()),
                h if h == matchday::FULL_TIME => {
                    Some(format!("Full time — Rain Town {} today.", match_result.verb()))
                }
                _ => None,
            };
            if let Some(message) = note {
                self.log.push(Event {
                    tick: self.clock.tick, day, hour, resident: "Matchday", message,
                });
            }
        }

        // Monday-night festival buildup — a separate town event from the football.
        if festival::is_festival_day(weekday) && self.clock.on_the_hour() {
            let note = match hour {
                17 => Some("Tonight the town gathers in the Main Square — music and dancing after dark.".to_string()),
                h if h == festival::START_HOUR => Some("The Monday-night gathering begins in the Main Square.".to_string()),
                h if h == festival::END_HOUR => Some("The gathering winds up; the town drifts home.".to_string()),
                _ => None,
            };
            if let Some(message) = note {
                self.log.push(Event {
                    tick: self.clock.tick, day, hour, resident: "Festival", message,
                });
            }
        }

        // Snapshot of where everyone is at the start of the tick (for the
        // intention layer to read without borrowing residents mutably).
        let presence: Vec<crate::sim::intention::Presence> = self
            .residents
            .iter()
            .map(|r| (r.id, r.name, r.place, r.is_present()))
            .collect();

        // ======================= PHASE 1 — ADVANCE =======================
        // Everyone continues what they are already doing: perform a tick (perhaps
        // lingering with a friend), walk a leg, or arrive. Some fall Idle.
        let mut oak_events: Vec<OakEvent> = Vec::new();
        {
            let Simulation { world, residents, log, clock, relationships, .. } = self;
            let nav: &NavGraph = &world.nav;
            for r in residents.iter_mut() {
                let status = std::mem::replace(&mut r.status, Status::Idle);
                match status {
                    Status::Performing { activity, left, start_day } => {
                        if left > 1 {
                            r.status = Status::Performing { activity, left: left - 1, start_day };
                        } else if let Some(friend) = linger_with_friend(r, hour, weather_appeal, &presence, relationships, world) {
                            r.lingered_today += 1;
                            r.status = Status::Performing { activity, left: LINGER_TICKS, start_day };
                            log.push(Event {
                                tick: clock.tick, day, hour, resident: r.name,
                                message: format!("lingers a little longer, enjoying {friend}'s company"),
                            });
                        } else if start_day == clock.day() {
                            r.done_today.push(activity);
                        }
                    }
                    Status::Traveling { activity, purpose, dest, dur, path, mut idx, leg_left } => {
                        if leg_left > 1 {
                            r.status = Status::Traveling { activity, purpose, dest, dur, path, idx, leg_left: leg_left - 1 };
                        } else {
                            idx += 1;
                            r.place = path[idx];
                            if r.place == dest {
                                r.status = Status::Performing { activity, left: dur, start_day: clock.day() };
                                log.push(Event {
                                    tick: clock.tick, day, hour, resident: r.name,
                                    message: format!("{purpose} — at {}", r.place),
                                });
                                record_oak_visit(r, activity, clock, &mut oak_events);
                            } else {
                                let leg = edge_weight(nav, path[idx], path[idx + 1]) * TRAVEL_TICKS_PER_WEIGHT;
                                r.status = Status::Traveling { activity, purpose, dest, dur, path, idx, leg_left: leg };
                            }
                        }
                    }
                    Status::Idle => {}
                }
            }
        }
        for ev in oak_events.drain(..) {
            self.oak.record(ev);
        }

        // ======================= PHASE 2 — DECIDE =======================
        // Every idle resident forms an intention without moving. Seeing where all
        // of them *mean* to go is what makes coordination possible.
        //
        // First, chosen togetherness: close friends at a loose end together may
        // agree to go somewhere as a pair. That agreement, formed before anyone
        // decides alone, overrides each of their solo plans below.
        let outings = self.plan_shared_outings(hour, weekday, match_result, self.clock.tick);
        let mut intents: Vec<Intent> = Vec::new();
        for (i, r) in self.residents.iter().enumerate() {
            if !matches!(r.status, Status::Idle) {
                continue;
            }
            if let Some(&(partner, dest, dur)) = outings.get(&i) {
                // One of the pair carries the log line; both get the same plan, so
                // RECONCILE pairs them into a joint departure.
                let reason = if i < partner {
                    let place_name = self.world.location(dest).map(|l| l.name).unwrap_or(dest);
                    Some(format!(
                        "{} and {} are close, and neither wants the afternoon to end — they decide to head to the {} together",
                        r.name, self.residents[partner].name, place_name
                    ))
                } else {
                    None
                };
                intents.push(Intent {
                    idx: i, aid: "dev_shared_plan", purpose: "a while together",
                    dur, dest, deviation: true, reason,
                });
                continue;
            }
            if let Some(fa) = festival::consider(r, weekday, hour) {
                intents.push(Intent { idx: i, aid: fa.id, purpose: fa.purpose, dur: hours_to_ticks(fa.duration), dest: fa.dest, deviation: false, reason: None });
                continue;
            }
            if let Some(m) = matchday::consider(r, weekday, hour, match_result) {
                intents.push(Intent { idx: i, aid: m.id, purpose: m.purpose, dur: hours_to_ticks(m.duration), dest: m.dest, deviation: false, reason: None });
                continue;
            }
            let Some(act) = r.select(hour, weekday, &self.world) else { continue };
            let Some(dest) = Routine::target_location(act, r.home) else { continue };
            if dest == r.home {
                // First: a friend is here now (join them). Else: our usual place
                // (go there on the memory of past meetings, expecting them).
                let readiness = r.social_readiness() + weather_appeal;
                let dev = intention::consider_social_detour(
                    r, hour, self.clock.tick, &presence, &self.relationships, &self.world, &self.world.nav, readiness,
                )
                .or_else(|| {
                    intention::consider_reunion(
                        r, hour, self.clock.tick, &presence, &self.bonds, &self.relationships, &self.world, &self.world.nav, readiness,
                    )
                });
                if let Some(dev) = dev {
                    intents.push(Intent { idx: i, aid: dev.activity_id, purpose: dev.purpose, dur: hours_to_ticks(dev.duration), dest: dev.dest, deviation: true, reason: Some(dev.reason) });
                    continue;
                }
            }
            intents.push(Intent { idx: i, aid: act.id, purpose: act.purpose, dur: hours_to_ticks(act.duration), dest, deviation: false, reason: None });
        }

        // ===================== PHASE 3 — RECONCILE ======================
        // Friends together, bound the same way, leave together; and a resident
        // briefly waits for a close friend who is just finishing up.
        let coord = self.reconcile_companionship(&intents);

        // ======================== PHASE 4 — ACT =========================
        // Where each intending resident means to go — so a partial-path companion
        // can name their friend's onward destination in the log.
        let intent_dest: BTreeMap<usize, LocationId> =
            intents.iter().map(|it| (it.idx, it.dest)).collect();
        let mut oak_events2: Vec<OakEvent> = Vec::new();
        for intent in &intents {
            let i = intent.idx;
            // Wait: hold off this tick to leave with a friend.
            if let Some(friend) = coord.waiting.get(&i) {
                self.residents[i].waited_today += 1;
                let name = self.residents[i].name;
                self.log.push(Event {
                    tick: self.clock.tick, day, hour, resident: name,
                    message: format!("waits for {friend} to finish up"),
                });
                continue;
            }
            if intent.deviation {
                if let Some(reason) = &intent.reason {
                    let name = self.residents[i].name;
                    self.log.push(Event { tick: self.clock.tick, day, hour, resident: name, message: reason.clone() });
                }
                self.residents[i].deviations_today += 1;
            }
            let place = self.residents[i].place;
            let name = self.residents[i].name;
            if intent.dest == place {
                self.residents[i].status = Status::Performing { activity: intent.aid, left: intent.dur, start_day: day };
                self.log.push(Event {
                    tick: self.clock.tick, day, hour, resident: name,
                    message: format!("{} — at {}", intent.purpose, place),
                });
                record_oak_visit(&mut self.residents[i], intent.aid, &self.clock, &mut oak_events2);
            } else if let Some(path) = self.world.nav.shortest_path(place, intent.dest) {
                let leg = edge_weight(&self.world.nav, path[0], path[1]) * TRAVEL_TICKS_PER_WEIGHT;
                let route = path.join(" -> ");
                if let Some(&partner) = coord.together.get(&i) {
                    if i < partner {
                        let pname = self.residents[partner].name;
                        self.log.push(Event {
                            tick: self.clock.tick, day, hour, resident: name,
                            message: format!("sets off with {pname} for {} ({}) via {route}", intent.dest, intent.purpose),
                        });
                    } // else: the earlier partner already logged the joint departure
                } else if let Some(&(partner, split)) = coord.partial.get(&i) {
                    if i < partner {
                        let pname = self.residents[partner].name;
                        let split_name = self.world.location(split).map(|l| l.name).unwrap_or(split);
                        let mine = self.world.location(intent.dest).map(|l| l.name).unwrap_or(intent.dest);
                        let their_dest = intent_dest.get(&partner).copied().unwrap_or(split);
                        let theirs = self.world.location(their_dest).map(|l| l.name).unwrap_or(their_dest);
                        let msg = if intent.dest == split {
                            // I arrive at the fork; my friend carries on past it.
                            format!("{name} and {pname} walk out together to the {split_name}, where {name} stops and {pname} carries on to the {theirs}")
                        } else if their_dest == split {
                            // My friend arrives at the fork; I carry on past it.
                            format!("{name} and {pname} walk out together to the {split_name}, where {pname} stops and {name} carries on to the {mine}")
                        } else {
                            // The road forks at the split and each takes their own.
                            format!("{name} and {pname} walk out together as far as the {split_name}, then part — {name} to the {mine}, {pname} to the {theirs}")
                        };
                        self.log.push(Event {
                            tick: self.clock.tick, day, hour, resident: name, message: msg,
                        });
                    } // else: the earlier partner already logged the shared stretch
                } else {
                    self.log.push(Event {
                        tick: self.clock.tick, day, hour, resident: name,
                        message: format!("sets out for {} ({}) via {route}", intent.dest, intent.purpose),
                    });
                }
                self.residents[i].status = Status::Traveling {
                    activity: intent.aid, purpose: intent.purpose, dest: intent.dest, dur: intent.dur,
                    path, idx: 0, leg_left: leg,
                };
            }
        }
        for ev in oak_events2 {
            self.oak.record(ev);
        }

        // --- the old dog keeps his own gentle rhythm through the district ---
        self.dog_pass(day, hour);

        // --- social interactions among co-located residents ---
        self.social_pass();

        // --- ambient life: the town's routines, micro-life, residents' moments ---
        self.density_pass(day, hour, weekday, minute);

        // --- the animals: living entities keeping their own (day and night) rhythm ---
        self.wildlife_pass(day, hour, minute);

        // Matchday's mark on the Old Oak — once, in the evening.
        if matchday::is_matchday(weekday) && hour == 18 && !self.oak_matchday_days.contains(&day) {
            let mark = match match_result {
                MatchResult::Win => Some(("res_tomas", OakEventKind::ScarfTied,
                    "ties a club scarf to a branch of the Old Oak after the win")),
                MatchResult::Loss => Some(("res_agnes", OakEventKind::FlowersLeft,
                    "leaves flowers at the roots of the Old Oak after the defeat")),
                MatchResult::Draw => None,
            };
            if let Some((who, kind, phrase)) = mark {
                self.oak.record(OakEvent { day, hour, kind, who: Some(who), with: None });
                let name = self.name_of(who);
                self.log.push(Event {
                    tick: self.clock.tick, day, hour, resident: name,
                    message: format!("{name} {phrase}."),
                });
            }
            self.oak_matchday_days.insert(day);
        }

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
                    let familiarity = self.bonds.meetings(pair.0, pair.1);
                    // Both people's current readiness for company shifts the odds.
                    let social_lift =
                        (self.residents[ia].social_readiness() + self.residents[ib].social_readiness()) * 2;
                    if let Some(outcome) =
                        social::decide(pair.0, pair.1, place, tick, rel, familiarity, social_lift)
                    {
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

            // A warm exchange lifts both moods; a sour one dents them. This is how
            // a day's encounters colour how ready someone is for the next.
            let mood_delta = if ap.kind == social::InteractionKind::Disagreement { -0.15 } else { 0.10 };

            if let Some(ra) = self.residents.iter_mut().find(|r| r.id == ap.a) {
                ra.nudge_mood(mood_delta);
                ra.memories.push(Memory {
                    day,
                    hour,
                    note: format!("{verb} with {b_name} at the {place_name}"),
                    other: Some(ap.b),
                });
            }
            if let Some(rb) = self.residents.iter_mut().find(|r| r.id == ap.b) {
                rb.nudge_mood(mood_delta);
                rb.memories.push(Memory {
                    day,
                    hour,
                    note: format!("{verb} with {a_name} at the {place_name}"),
                    other: Some(ap.a),
                });
            }
            // A meeting beside the Oak becomes part of its history.
            if ap.place == crate::sim::oak::OAK_LOCATION {
                self.oak.record(OakEvent {
                    day,
                    hour,
                    kind: OakEventKind::Gathering,
                    who: Some(ap.a),
                    with: Some(ap.b),
                });
            }
            // Remember the shared experience: this meeting, and where it was.
            self.bonds.record(ap.a, ap.b, ap.place, day);
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

    fn push_ambient(&mut self, day: u64, hour: u64, l: ambient::Line) {
        self.ambient.push(Ambient {
            tick: self.clock.tick,
            day,
            hour,
            minute: l.minute,
            kind: l.kind,
            actor: l.actor,
            text: l.text.to_string(),
        });
    }

    /// The density layer: the town's own routines, the micro-life moving through
    /// the district, and the residents' small incidental moments. All ambient,
    /// all deterministic — the life that fills an hour.
    fn density_pass(&mut self, day: u64, hour: u64, weekday: u64, minute: u64) {
        // The town's routines and micro-life are authored with a minute within the
        // hour; emit each on the five-minute tick its minute falls into, so the
        // hour's life is spread across it rather than dumped on the hour.
        let in_slot = |m: u8| (m as u64) >= minute && (m as u64) < minute + MINUTES_PER_TICK;
        for l in ambient::background(day, hour, weekday) {
            if in_slot(l.minute) {
                self.push_ambient(day, hour, l);
            }
        }
        for l in ambient::microlife(day, hour, weekday) {
            if in_slot(l.minute) {
                self.push_ambient(day, hour, l);
            }
        }
        self.moments_pass(day, hour, minute);
    }

    /// Residents' small incidental moments. Each hour, a present resident evaluates
    /// what is around them — who else is here, the children, an open shop window,
    /// the old dog — and may have a small moment; a traveller may pause on the
    /// bridge or take a shortcut. Emergent from co-presence and place, bounded,
    /// deterministic, and pure texture (it changes no world truth).
    fn moments_pass(&mut self, day: u64, hour: u64, minute: u64) {
        let tick = self.clock.tick;
        let dog_place = self.dog.place;

        // Who is present (not travelling, not at home) and where.
        let mut present_here: std::collections::BTreeMap<LocationId, Vec<usize>> = BTreeMap::new();
        for (i, r) in self.residents.iter().enumerate() {
            let public = self.world.location(r.place).map(|l| !l.is_residential()).unwrap_or(false);
            if public && !matches!(r.status, Status::Traveling { .. }) {
                present_here.entry(r.place).or_default().push(i);
            }
        }

        let mut out: Vec<(u8, &'static str, String)> = Vec::new();
        for (i, r) in self.residents.iter().enumerate() {
            // Seed once per resident *per hour* so each has at most a couple of
            // moments in the hour, each pinned to a fixed five-minute slot — the
            // moments spread across the hour instead of all landing at once.
            let seed = social::seed_hash(&[r.id, "moment"], day * 24 + hour);
            let travelling = matches!(r.status, Status::Traveling { .. });
            let public = self.world.location(r.place).map(|l| !l.is_residential()).unwrap_or(false);
            if !travelling && !public {
                continue; // asleep or at home — no public moment
            }
            // Quieter deep at night.
            let chance = if (0..=4).contains(&hour) || hour == 23 { 30 } else { 72 };
            if (seed % 100) as u32 >= chance {
                continue;
            }
            let primary_slot = (seed / 7 % TICKS_PER_HOUR) * MINUTES_PER_TICK; // 0,5,…,55
            let has_second = (seed / 1_000 % 100) < 30;
            let second_slot = (seed / 11 % TICKS_PER_HOUR) * MINUTES_PER_TICK;
            let is_primary = minute == primary_slot;
            let is_second = has_second && minute == second_slot && second_slot != primary_slot;
            if !is_primary && !is_second {
                continue;
            }

            if is_second {
                let opts = ["checks the time", "shifts in the light", "watches a moment longer"];
                out.push((minute as u8, r.name, opts[(seed / 97 % 3) as usize].to_string()));
                continue;
            }

            let text = if travelling {
                let opts = [
                    "pauses on the old bridge a moment, watching the water",
                    "takes the familiar shortcut behind the bakery",
                    "steps aside to let a cyclist by",
                    "nods to a passing face without slowing",
                    "stops to read a notice pinned to a post",
                ];
                opts[(seed / 100 % opts.len() as u64) as usize].to_string()
            } else {
                let place_name = self.world.location(r.place).map(|l| l.name).unwrap_or(r.place);
                // Build applicable, context-aware candidates.
                let mut cands: Vec<String> = Vec::new();
                if dog_place == r.place {
                    cands.push("stops to scratch the old dog behind the ears".to_string());
                }
                // children present (other than self)
                if self.residents.iter().enumerate().any(|(j, o)| j != i && o.place == r.place && o.is_child() && !matches!(o.status, Status::Traveling { .. })) {
                    cands.push("watches the children chase a ball across the square".to_string());
                }
                // a co-present other they know a little
                if let Some(&j) = present_here.get(r.place).and_then(|v| v.iter().find(|&&j| j != i && self.relationships.get(r.id, self.residents[j].id).affinity >= 1)) {
                    let other = self.residents[j].name;
                    let opts = [
                        format!("shares a brief word with {other}"),
                        format!("catches {other}'s eye and nods"),
                        format!("waits a moment while {other} finishes up"),
                    ];
                    cands.push(opts[(seed / 13 % 3) as usize].clone());
                }
                // an open shop window
                let open_shop = self.world.location(r.place).map(|l| l.hours.map(|h| h.is_open(hour)).unwrap_or(false)).unwrap_or(false);
                if open_shop {
                    cands.push(format!("pauses at the {place_name} window"));
                }
                // fallbacks — always available
                cands.push(format!("lingers a moment at the {place_name}"));
                cands.push("glances up at the sky, reading the light".to_string());
                cands[(seed / 100 % cands.len() as u64) as usize].clone()
            };
            out.push((minute as u8, r.name, text));
        }

        for (minute_stamp, actor, text) in out {
            self.ambient.push(Ambient { tick, day, hour, minute: minute_stamp, kind: AmbientKind::Moment, actor, text });
        }
    }

    /// The district's animals take their turn. Each is a persistent entity keeping
    /// its own rhythm — several of them nocturnal, so the small hours have life.
    /// Their choices draw from the seeded `rng`; their narration joins the ambient
    /// stream (kind `Wild`). They read resident presence but never change it.
    fn wildlife_pass(&mut self, day: u64, hour: u64, minute: u64) {
        let mut occ: BTreeMap<LocationId, usize> = BTreeMap::new();
        for r in &self.residents {
            if r.is_present() {
                *occ.entry(r.place).or_default() += 1;
            }
        }
        let tick = self.clock.tick;
        let lines = self.wildlife.tick(&mut self.rng, hour, &self.world.nav, &occ);
        for (actor, text) in lines {
            self.ambient.push(Ambient {
                tick,
                day,
                hour,
                minute: minute as u8,
                kind: AmbientKind::Wild,
                actor,
                text,
            });
        }
    }

    /// The old dog ambles slowly toward the place he'd rather be, settling for a
    /// while when he arrives, and sometimes the child finds him there. He is not a
    /// resident with a job and has no end-of-day duty; he is simply part of the
    /// district. Deterministic; no reward, no mechanic.
    fn dog_pass(&mut self, day: u64, hour: u64) {
        use crate::sim::dog::{Dog, CHILD_ID};
        self.dog.roll_day(day);

        let pref = self.dog.preferred_spot(hour);
        if self.dog.place != pref && self.dog.cooldown() == 0 {
            if let Some(path) = self.world.nav.shortest_path(self.dog.place, pref) {
                if path.len() >= 2 {
                    let next = path[1];
                    self.dog.arrive(next);
                    if next == pref {
                        self.log.push(Event {
                            tick: self.clock.tick, day, hour, resident: crate::sim::dog::DOG_NAME,
                            message: Dog::settle_phrase(next).to_string(),
                        });
                    }
                }
            }
        } else {
            // Resting (at his spot, or between ambles) — the wait counts down so he
            // is ready to move when the day turns.
            self.dog.tick_cooldown();
        }

        // The child sometimes finds him — they don't always meet.
        if !self.dog.met_child_today() && self.world.location(self.dog.place).map(|l| !l.is_residential()).unwrap_or(false) {
            // The child need only be *at* the dog's place — settled there, or just
            // crossing it. A boy passing a dog stops to say hello.
            let child_here = self
                .residents
                .iter()
                .any(|r| r.id == CHILD_ID && r.place == self.dog.place);
            if child_here && social::seed_hash(&["dog-child", self.dog.place], day) % 100 < 60 {
                let child = self.name_of(CHILD_ID);
                self.dog.meet_child();
                let message = if self.dog.bond_with_child <= 1 {
                    format!("{child} crouches to say hello to the old dog")
                } else {
                    format!("{child} finds the old dog and sits with him a while")
                };
                self.log.push(Event {
                    tick: self.clock.tick, day, hour, resident: crate::sim::dog::DOG_NAME, message,
                });
            }
        }
    }

    /// Chosen togetherness. Two close friends who are at a loose end together in
    /// public — both idle, with no errand pulling them anywhere but home — may
    /// *decide* to spend a while somewhere together instead of drifting off
    /// separately. Returns, per participant index, their partner and the shared
    /// destination; DECIDE then gives both the same outing so RECONCILE walks them
    /// out side by side.
    ///
    /// Gated by closeness and by how ready each is for company right now (two
    /// tired or withdrawn people just head home), bounded to one deviation each
    /// per day, time-safe (they can always get home), and deterministic (a seeded
    /// choice, no RNG).
    fn plan_shared_outings(
        &self,
        hour: u64,
        weekday: u64,
        match_result: MatchResult,
        tick: u64,
    ) -> BTreeMap<usize, (usize, LocationId, u32)> {
        let mut out: BTreeMap<usize, (usize, LocationId, u32)> = BTreeMap::new();
        // The unhurried end of the day, when "shall we?" happens.
        if !(15..=19).contains(&hour) {
            return out;
        }
        let rs = &self.residents;
        // "Free enough" to say yes: idle, out in public, up for company, not
        // already spent today's spontaneity, no pressing errand (nothing to do,
        // or only home left), and not caught up in the matchday pull.
        let is_free = |r: &Resident| -> bool {
            if !matches!(r.status, Status::Idle) || r.deviations_today > 0 {
                return false;
            }
            if r.social_readiness() < 1 {
                return false;
            }
            let public = self.world.location(r.place).map(|l| !l.is_residential()).unwrap_or(false);
            if !public {
                return false;
            }
            if matchday::consider(r, weekday, hour, match_result).is_some() {
                return false;
            }
            if festival::consider(r, weekday, hour).is_some() {
                return false;
            }
            match r.select(hour, weekday, &self.world) {
                None => true,
                Some(act) => Routine::target_location(act, r.home) == Some(r.home),
            }
        };
        let mut taken = vec![false; rs.len()];
        for i in 0..rs.len() {
            if taken[i] || !is_free(&rs[i]) {
                continue;
            }
            for j in (i + 1)..rs.len() {
                if taken[j] || rs[j].place != rs[i].place || !is_free(&rs[j]) {
                    continue;
                }
                if self.relationships.get(rs[i].id, rs[j].id).affinity < COMPANION_AFFINITY {
                    continue;
                }
                let Some((dest, dur)) = self.pick_shared_leisure(&rs[i], &rs[j], hour) else {
                    continue;
                };
                // Even willing friends don't always make a plan — a seeded choice,
                // likelier the more up for company the two of them are.
                let readiness = rs[i].social_readiness() + rs[j].social_readiness();
                let gate = (40 + readiness * 4).clamp(15, 85) as u64;
                if social::seed_hash(&[rs[i].id, rs[j].id, dest, "shared"], tick) % 100 >= gate {
                    continue;
                }
                out.insert(i, (j, dest, dur));
                out.insert(j, (i, dest, dur));
                taken[i] = true;
                taken[j] = true;
                break;
            }
        }
        out
    }

    /// Choose a public place two friends can go to now and still both get home in
    /// time. Prefers the café, then the square. Returns (destination, stay-ticks).
    fn pick_shared_leisure(&self, ra: &Resident, rb: &Resident, hour: u64) -> Option<(LocationId, u32)> {
        let nav = &self.world.nav;
        for dest in ["loc_cafe", "loc_main_square"] {
            if dest == ra.place || !self.world.is_open(dest, hour) {
                continue;
            }
            let (Some(to), Some(home_a), Some(home_b)) = (
                nav.travel_time(ra.place, dest),
                nav.travel_time(dest, ra.home),
                nav.travel_time(dest, rb.home),
            ) else {
                continue;
            };
            let latest_home = home_a.max(home_b) as u64;
            if hour + to as u64 + SHARED_TICKS as u64 + latest_home > LEISURE_END {
                continue;
            }
            return Some((dest, SHARED_TICKS));
        }
        None
    }

    /// Companionship: from everyone's intentions, decide who leaves together and
    /// who waits. Deterministic (residents and intents in stable order); reads
    /// only positions, statuses, and relationships.
    fn reconcile_companionship(&self, intents: &[Intent]) -> Coord {
        let mut coord = Coord::default();

        // Leave together: two close friends at the same place, bound for the same
        // destination this tick, set off as a pair.
        for a in 0..intents.len() {
            let ia = intents[a].idx;
            let ra = &self.residents[ia];
            if intents[a].dest == ra.place || coord.together.contains_key(&ia) {
                continue; // performing in place, or already paired
            }
            for b in intents.iter().skip(a + 1) {
                let ib = b.idx;
                let rb = &self.residents[ib];
                if b.dest == rb.place || coord.together.contains_key(&ib) {
                    continue;
                }
                if ra.place == rb.place
                    && intents[a].dest == b.dest
                    && self.relationships.get(ra.id, rb.id).affinity >= COMPANION_AFFINITY
                {
                    coord.together.insert(ia, ib);
                    coord.together.insert(ib, ia);
                    break;
                }
            }
        }

        // Walk partway together: two close friends leaving the same place for
        // *different* destinations, whose shortest routes share the opening
        // stretch, keep each other company as far as the fork, then part. Their
        // paths already coincide on that stretch, so this only recognises and
        // narrates what the movement does anyway.
        for a in 0..intents.len() {
            let ia = intents[a].idx;
            let ra = &self.residents[ia];
            if intents[a].dest == ra.place
                || coord.together.contains_key(&ia)
                || coord.partial.contains_key(&ia)
            {
                continue;
            }
            for b in intents.iter().skip(a + 1) {
                let ib = b.idx;
                let rb = &self.residents[ib];
                if b.dest == rb.place
                    || coord.together.contains_key(&ib)
                    || coord.partial.contains_key(&ib)
                {
                    continue;
                }
                if ra.place != rb.place || intents[a].dest == b.dest {
                    continue; // different start, or same dest (that's `together`)
                }
                if self.relationships.get(ra.id, rb.id).affinity < COMPANION_AFFINITY {
                    continue;
                }
                let (Some(pa), Some(pb)) = (
                    self.world.nav.shortest_path(ra.place, intents[a].dest),
                    self.world.nav.shortest_path(rb.place, b.dest),
                ) else {
                    continue;
                };
                // Longest shared leading run of nodes; they part at its last node.
                let mut split = 0usize;
                while split + 1 < pa.len() && split + 1 < pb.len() && pa[split + 1] == pb[split + 1] {
                    split += 1;
                }
                if split >= 1 {
                    let split_node = pa[split];
                    coord.partial.insert(ia, (ib, split_node));
                    coord.partial.insert(ib, (ia, split_node));
                    break;
                }
            }
        }

        // Wait: a resident about to travel waits a moment for a close friend who
        // is co-located and just finishing up (Performing with one tick left), so
        // they can leave together next tick.
        for it in intents {
            let i = it.idx;
            let ri = &self.residents[i];
            if it.dest == ri.place || coord.together.contains_key(&i) || ri.waited_today >= WAIT_CAP {
                continue;
            }
            // You linger to leave with a friend only if you're up for company.
            if ri.social_readiness() < 1 {
                continue;
            }
            for (j, rj) in self.residents.iter().enumerate() {
                if j == i || rj.place != ri.place {
                    continue;
                }
                if self.relationships.get(ri.id, rj.id).affinity < COMPANION_AFFINITY {
                    continue;
                }
                if matches!(rj.status, Status::Performing { left, .. } if left <= FINISHING_TICKS) {
                    coord.waiting.insert(i, rj.name);
                    break;
                }
            }
        }

        coord
    }

    pub fn resident(&self, id: &str) -> Option<&Resident> {
        self.residents.iter().find(|r| r.id == id)
    }
}

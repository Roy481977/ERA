//! The simulation loop (Phase 2 / 4): advances the clock and moves residents
//! through their routines. Deterministic; every state change is observable via
//! the event log.

use std::collections::{BTreeMap, BTreeSet};

use crate::sim::clock::{WorldClock, DAYS_PER_WEEK, TICKS_PER_DAY};
use crate::sim::dog::Dog;
use crate::sim::intention;
use crate::sim::matchday::{self, MatchResult};
use crate::sim::oak::{OakEvent, OakEventKind, OldOak};
use crate::sim::resident::{Memory, Resident, Status};
use crate::sim::routine::Routine;
use crate::sim::social::{self, Bonds, Relationships};
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
    pub log: Vec<Event>,
    /// Structured record of every interaction (observability / tests / Oak).
    pub interactions: Vec<social::Interaction>,
    last_day: u64,
    /// Pairs that have already interacted today (once-per-day cap).
    social_seen_today: BTreeSet<(&'static str, &'static str)>,
    /// Matchdays whose Oak consequence (scarf / flowers) has been recorded.
    oak_matchday_days: BTreeSet<u64>,
}

const LINGER_CAP: u32 = 2;

/// Whether a resident whose activity is ending should linger — a close friend is
/// present at the same public place, it isn't yet night, and they haven't lingered
/// too much today. Returns the friend's name for the log.
fn linger_with_friend(
    r: &Resident,
    hour: u64,
    presence: &[intention::Presence],
    rels: &Relationships,
    world: &World,
) -> Option<&'static str> {
    if hour >= 18 || r.lingered_today >= LINGER_CAP {
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
const WAIT_CAP: u32 = 2;

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
    /// idx -> friend name: this resident waits this tick to leave with them.
    waiting: BTreeMap<usize, &'static str>,
}

impl Simulation {
    pub fn new(residents: Vec<Resident>) -> Self {
        Simulation {
            world: build_world(),
            clock: WorldClock::new(),
            residents,
            relationships: Relationships::seeded(),
            bonds: Bonds::default(),
            oak: OldOak::new(),
            dog: Dog::new(),
            log: Vec::new(),
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
            }
            self.social_seen_today.clear();
            self.last_day = day;
        }
        let hour = self.clock.hour();
        let weekday = self.clock.weekday();
        let match_result = MatchResult::for_week(day / DAYS_PER_WEEK);

        // Matchday buildup: district-wide announcements as the day unfolds.
        if matchday::is_matchday(weekday) {
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
                        } else if let Some(friend) = linger_with_friend(r, hour, &presence, relationships, world) {
                            r.lingered_today += 1;
                            r.status = Status::Performing { activity, left: 1, start_day };
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
                                let leg = edge_weight(nav, path[idx], path[idx + 1]);
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
        let mut intents: Vec<Intent> = Vec::new();
        for (i, r) in self.residents.iter().enumerate() {
            if !matches!(r.status, Status::Idle) {
                continue;
            }
            if let Some(m) = matchday::consider(r, weekday, hour, match_result) {
                intents.push(Intent { idx: i, aid: m.id, purpose: m.purpose, dur: m.duration, dest: m.dest, deviation: false, reason: None });
                continue;
            }
            let Some(act) = r.select(hour, weekday, &self.world) else { continue };
            let Some(dest) = Routine::target_location(act, r.home) else { continue };
            if dest == r.home {
                // First: a friend is here now (join them). Else: our usual place
                // (go there on the memory of past meetings, expecting them).
                let dev = intention::consider_social_detour(
                    r, hour, self.clock.tick, &presence, &self.relationships, &self.world, &self.world.nav,
                )
                .or_else(|| {
                    intention::consider_reunion(
                        r, hour, self.clock.tick, &presence, &self.bonds, &self.relationships, &self.world, &self.world.nav,
                    )
                });
                if let Some(dev) = dev {
                    intents.push(Intent { idx: i, aid: dev.activity_id, purpose: dev.purpose, dur: dev.duration, dest: dev.dest, deviation: true, reason: Some(dev.reason) });
                    continue;
                }
            }
            intents.push(Intent { idx: i, aid: act.id, purpose: act.purpose, dur: act.duration, dest, deviation: false, reason: None });
        }

        // ===================== PHASE 3 — RECONCILE ======================
        // Friends together, bound the same way, leave together; and a resident
        // briefly waits for a close friend who is just finishing up.
        let coord = self.reconcile_companionship(&intents);

        // ======================== PHASE 4 — ACT =========================
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
                let leg = edge_weight(&self.world.nav, path[0], path[1]);
                let route = path.join(" -> ");
                match coord.together.get(&i) {
                    Some(&partner) if i < partner => {
                        let pname = self.residents[partner].name;
                        self.log.push(Event {
                            tick: self.clock.tick, day, hour, resident: name,
                            message: format!("sets off with {pname} for {} ({}) via {route}", intent.dest, intent.purpose),
                        });
                    }
                    Some(_) => { /* the earlier partner already logged the joint departure */ }
                    None => {
                        self.log.push(Event {
                            tick: self.clock.tick, day, hour, resident: name,
                            message: format!("sets out for {} ({}) via {route}", intent.dest, intent.purpose),
                        });
                    }
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
                    if let Some(outcome) = social::decide(pair.0, pair.1, place, tick, rel, familiarity) {
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
            let child_here = self
                .residents
                .iter()
                .any(|r| r.id == CHILD_ID && r.place == self.dog.place && r.is_present());
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

        // Wait: a resident about to travel waits a moment for a close friend who
        // is co-located and just finishing up (Performing with one tick left), so
        // they can leave together next tick.
        for it in intents {
            let i = it.idx;
            let ri = &self.residents[i];
            if it.dest == ri.place || coord.together.contains_key(&i) || ri.waited_today >= WAIT_CAP {
                continue;
            }
            for (j, rj) in self.residents.iter().enumerate() {
                if j == i || rj.place != ri.place {
                    continue;
                }
                if self.relationships.get(ri.id, rj.id).affinity < COMPANION_AFFINITY {
                    continue;
                }
                if matches!(rj.status, Status::Performing { left: 1, .. }) {
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

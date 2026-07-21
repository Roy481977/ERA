//! The ERA engine: a continuously-ticking world with persistent entities and a
//! live, inspectable snapshot.
//!
//! This is the transition from a *prototype* (run N days, export a trace, replay
//! it) to the *beginning of the actual engine*. The world here is not a recording
//! played back — it is a persistent, running thing. You hold an `Engine`, you
//! `tick()` it forward one hour at a time, and at any moment you `snapshot()` its
//! live state. Nothing about a snapshot advances the world; it is a pure window
//! onto whatever the world is *right now*.
//!
//! A renderer observes the world by reading snapshots. It owns no simulation
//! logic of its own — every position, every occupancy count, every callout is
//! computed here, from authoritative state, so that "rendering is driven from
//! state" is true by construction. Determinism is inherited from the core
//! `Simulation` (no clocks, no RNG); the same tick sequence always yields the
//! same snapshots.

use std::collections::BTreeMap;

use crate::behaviour::{Behaviour, Choreographer};
use crate::sim::clock::WEEKDAY_NAMES;
use crate::sim::matchday;
use crate::sim::resident::Status;
use crate::sim::{cast, Simulation};
use crate::view::layout;
use crate::world::location::LocationId;

mod snapshot_json;

/// A single persistent entity as the world sees it right now — position *and*
/// observable behaviour (heading, pose, gesture, who it attends to), so the
/// renderer draws a living thing rather than a labelled dot.
#[derive(Debug, Clone)]
pub struct EntityView {
    pub id: &'static str,
    pub name: &'static str,
    /// "resident" | "dog" | a species tag ("fox", "owl", …).
    pub kind: &'static str,
    pub color: &'static str,
    pub x: f64,
    pub y: f64,
    pub place: LocationId,
    pub place_name: &'static str,
    /// What they are doing, in words (the current activity, or transit).
    pub doing: String,
    pub traveling: bool,
    // --- behaviour ---
    /// Facing direction in radians.
    pub heading: f64,
    /// Movement this tick, 0..1.
    pub speed: f64,
    /// Body pose tag ("walk", "stand", "talk", "sit", "lie", …).
    pub pose: &'static str,
    /// Momentary gesture tag ("laugh", "gesture", "glance", …).
    pub gesture: &'static str,
    /// Who they are attending to, if anyone.
    pub partner: Option<&'static str>,
    /// Progress through a bounded state (a conversation), 0..1.
    pub phase: f64,
    // --- disposition (residents; the renderer makes temperament visible) ---
    /// Stable sociability trait (~ -2..3). 0 for non-residents.
    pub soc: i32,
    /// Current mood, -1..1. 0 for non-residents.
    pub mood: f64,
    /// Current energy, ~0.05..1. 1 for non-residents.
    pub energy: f64,
    /// What the resident visibly has on now (coat, umbrella, club_scarf, a
    /// keepsake…) — the possessions layer. Empty for non-residents.
    pub worn: Vec<&'static str>,
}

/// The day's weather, as a live reading.
#[derive(Debug, Clone)]
pub struct WeatherView {
    pub sky: &'static str,
    pub temp: &'static str,
    pub wet: bool,
    pub windy: bool,
    pub phrase: &'static str,
}

/// The Old Oak, as a live reading.
#[derive(Debug, Clone)]
pub struct OakView {
    pub age_years: u32,
    pub season: &'static str,
    pub appearance: &'static str,
    pub visits: u32,
    pub scarves: u32,
    pub bouquets: u32,
}

/// An inspectable bond between two residents (for the state panel).
#[derive(Debug, Clone)]
pub struct BondView {
    pub a: &'static str,
    pub b: &'static str,
    pub affinity: i32,
    pub trust: i32,
    pub meetings: u32,
    pub usual_place: Option<&'static str>,
}

/// One thing worth calling out this hour (busy place, a match beat, a meeting).
#[derive(Debug, Clone)]
pub struct Callout {
    pub kind: &'static str, // "place" | "match" | "oak" | "social"
    pub text: String,
}

/// A pure, self-contained window onto the live world at one instant.
#[derive(Debug, Clone)]
pub struct Snapshot {
    pub tick: u64,
    pub day: u64,
    pub hour: u64,
    pub minute: u64,
    pub weekday: &'static str,
    pub phase: &'static str,
    /// The season the world is dressed in right now.
    pub season: &'static str,
    /// The day's weather.
    pub weather: WeatherView,
    pub entities: Vec<EntityView>,
    pub occupancy: BTreeMap<LocationId, u32>,
    pub busiest: Option<(LocationId, &'static str, u32)>,
    pub callouts: Vec<Callout>,
    pub oak: OakView,
    /// Behavioural + ambient lines emitted during the tick that produced this
    /// state (actor, text, kind-tag).
    pub events: Vec<(String, String, &'static str)>,
    pub bonds: Vec<BondView>,
}

/// The running world. Persistent; ticked forward; observed via snapshots.
pub struct Engine {
    sim: Simulation,
    /// The Behaviour Layer: translates simulation state into observable behaviour.
    choreo: Choreographer,
}

impl Default for Engine {
    fn default() -> Self {
        Self::new()
    }
}

impl Engine {
    /// A fresh First Breath district at the first breath (tick 0), before any
    /// time has passed.
    pub fn new() -> Self {
        Self::with_seed(crate::sim::simulation::DEFAULT_WORLD_SEED)
    }

    /// A fresh district whose wildlife is grown from a specific seed.
    pub fn with_seed(seed: u64) -> Self {
        let sim = Simulation::with_seed(cast(), seed);
        let mut choreo = Choreographer::new();
        choreo.observe(&sim); // behaviour baseline at tick 0
        Engine { sim, choreo }
    }

    /// Direct read access to the underlying simulation (for native consumers and
    /// tests that want the full state, not just a snapshot).
    pub fn sim(&self) -> &Simulation {
        &self.sim
    }

    /// Advance the world one tick (five minutes), then let the Behaviour Layer
    /// observe the new state.
    pub fn tick(&mut self) {
        self.sim.step();
        self.choreo.observe(&self.sim);
    }

    /// Advance the world `n` hours.
    pub fn tick_n(&mut self, n: u64) {
        for _ in 0..n {
            self.tick();
        }
    }

    pub fn tick_count(&self) -> u64 {
        self.sim.clock.tick
    }

    pub fn day(&self) -> u64 {
        self.sim.clock.day()
    }

    pub fn hour(&self) -> u64 {
        self.sim.clock.hour()
    }

    fn phase_of_day(hour: u64) -> &'static str {
        match hour {
            0..=4 => "the small hours",
            5..=7 => "dawn",
            8..=11 => "morning",
            12..=16 => "afternoon",
            17..=20 => "evening",
            _ => "night",
        }
    }

    /// The index of the tick whose processing produced the current state (i.e.
    /// the most recently completed tick), if any.
    fn last_completed_tick(&self) -> Option<u64> {
        self.sim.clock.tick.checked_sub(1)
    }

    /// A pure window onto the live world right now.
    pub fn snapshot(&self) -> Snapshot {
        let sim = &self.sim;
        let day = sim.clock.day();
        let hour = sim.clock.hour();
        let minute = sim.clock.minute();
        let weekday = WEEKDAY_NAMES[(sim.clock.weekday()) as usize];

        // ---- persistent entities, each with its observable behaviour ----
        // The Behaviour Layer has already observed this tick; look each entity's
        // behaviour up by id and attach it (position, heading, pose, gesture).
        let bmap: BTreeMap<&str, &Behaviour> =
            self.choreo.frame().iter().map(|b| (b.id, b)).collect();

        let mut entities: Vec<EntityView> =
            Vec::with_capacity(sim.residents.len() + 1 + sim.wildlife.animals.len());
        let mut occupancy: BTreeMap<LocationId, u32> = BTreeMap::new();

        let make = |id: &'static str,
                    name: &'static str,
                    kind: &'static str,
                    color: &'static str,
                    place: LocationId,
                    place_name: &'static str,
                    doing: String|
         -> EntityView {
            let b = bmap.get(id).copied();
            EntityView {
                id,
                name,
                kind,
                color,
                x: b.map(|b| b.x).unwrap_or(0.0),
                y: b.map(|b| b.y).unwrap_or(0.0),
                place,
                place_name,
                doing,
                traveling: b.map(|b| b.moving).unwrap_or(false),
                heading: b.map(|b| b.heading).unwrap_or(0.0),
                speed: b.map(|b| b.speed).unwrap_or(0.0),
                pose: b.map(|b| b.pose.tag()).unwrap_or("stand"),
                gesture: b.map(|b| b.gesture.tag()).unwrap_or("none"),
                partner: b.and_then(|b| b.partner),
                phase: b.map(|b| b.phase).unwrap_or(0.0),
                soc: 0,
                mood: 0.0,
                energy: 1.0,
                worn: Vec::new(),
            }
        };

        // Season and matchday are the same for everyone this tick — compute once.
        let season = crate::sim::oak::Season::for_day(day);
        let is_match = matchday::is_matchday(sim.clock.weekday());

        for r in &sim.residents {
            let traveling = matches!(r.status, Status::Traveling { .. });
            let doing = match &r.status {
                Status::Idle => "between things".to_string(),
                Status::Performing { activity, .. } => {
                    r.purpose_of(activity).unwrap_or("here a while").to_string()
                }
                Status::Traveling { purpose, dest, .. } => {
                    let dn = sim.world.location(dest).map(|l| l.name).unwrap_or(dest);
                    format!("on the way — {purpose} (to {dn})")
                }
            };
            let place_name = sim.world.location(r.place).map(|l| l.name).unwrap_or(r.place);
            let mut ev = make(r.id, r.name, "resident", layout::color_of(r.id), r.place, place_name, doing);
            ev.soc = r.sociability;
            ev.mood = r.mood as f64;
            ev.energy = r.energy as f64;
            let working = matches!(&r.status, Status::Performing { activity, .. }
                if r.affordance_of(activity)
                    .map(|a| a.starts_with("WORK") || a == "KIOSK" || a == "MARKET" || a == "BUSK")
                    .unwrap_or(false));
            ev.worn = sim.possessions.worn_tags(r.id, season, sim.weather, working, is_match);
            entities.push(ev);
            // Occupancy counts settled/idle residents at their node.
            if !traveling {
                *occupancy.entry(r.place).or_default() += 1;
            }
        }
        let dog_place_name = sim.world.location(sim.dog.place).map(|l| l.name).unwrap_or(sim.dog.place);
        entities.push(make(
            "the_old_dog", "the old dog", "dog", layout::color_of("the_old_dog"),
            sim.dog.place, dog_place_name, "about the district".to_string(),
        ));
        for a in &sim.wildlife.animals {
            let place_name = sim.world.location(a.place).map(|l| l.name).unwrap_or(a.place);
            entities.push(make(a.id, a.name, a.species.tag(), a.color, a.place, place_name, a.doing()));
        }

        // ---- busiest place ----
        // A gathering is a *public* thing. A house full of sleepers is not the
        // town being busy, so residential nodes never count as "busiest".
        let busiest = occupancy
            .iter()
            .filter(|(p, _)| !sim.world.location(p).map(|l| l.is_residential()).unwrap_or(false))
            .max_by_key(|(_, n)| **n)
            .filter(|(_, n)| **n >= 2)
            .map(|(p, n)| {
                let name = sim.world.location(p).map(|l| l.name).unwrap_or(p);
                (*p, name, *n)
            });

        // ---- oak ----
        let season = sim.oak.season(day);
        let oak = OakView {
            age_years: sim.oak.age_years,
            season: season.name(),
            appearance: season.appearance(),
            visits: sim.oak.visit_count,
            scarves: sim.oak.scarves,
            bouquets: sim.oak.bouquets,
        };

        // ---- events emitted during the tick that produced this state ----
        let mut events: Vec<(String, String, &'static str)> = Vec::new();
        if let Some(t) = self.last_completed_tick() {
            for e in sim.log.iter().filter(|e| e.tick == t) {
                events.push((e.resident.to_string(), e.message.clone(), event_tag(&e.message)));
            }
            for a in sim.ambient.iter().filter(|a| a.tick == t) {
                events.push((a.actor.to_string(), a.text.clone(), a.kind.tag()));
            }
        }

        // ---- callouts: what an observer would notice this hour ----
        let mut callouts: Vec<Callout> = Vec::new();
        if let Some((_, name, n)) = busiest {
            if n >= 3 {
                callouts.push(Callout {
                    kind: "place",
                    text: format!("{name} is busy right now — {n} gathered"),
                });
            }
        }
        for (_who, msg, _tag) in &events {
            let hit = if msg.contains("Kick-off") || msg.contains("Full time") || msg.contains("Matchday") {
                Some("match")
            } else if msg.contains("scarf") || msg.contains("flowers at the roots") {
                Some("oak")
            } else if msg.contains("half-expecting to find") || msg.contains("old friends, and it shows") {
                Some("social")
            } else {
                None
            };
            if let Some(kind) = hit {
                callouts.push(Callout { kind, text: msg.clone() });
            }
        }

        // ---- inspectable bonds (top handful by shared history) ----
        let mut bonds: Vec<BondView> = Vec::new();
        for i in 0..sim.residents.len() {
            for j in (i + 1)..sim.residents.len() {
                let (a, b) = (sim.residents[i].id, sim.residents[j].id);
                if let Some(bond) = sim.bonds.get(a, b) {
                    if bond.meetings >= 1 {
                        let rel = sim.relationships.get(a, b);
                        bonds.push(BondView {
                            a: sim.residents[i].name,
                            b: sim.residents[j].name,
                            affinity: rel.affinity,
                            trust: rel.trust,
                            meetings: bond.meetings,
                            usual_place: bond.usual_place().map(|p| {
                                sim.world.location(p).map(|l| l.name).unwrap_or(p)
                            }),
                        });
                    }
                }
            }
        }
        bonds.sort_by(|x, y| y.meetings.cmp(&x.meetings).then(y.affinity.cmp(&x.affinity)));
        bonds.truncate(6);

        Snapshot {
            tick: sim.clock.tick,
            day,
            hour,
            minute,
            weekday,
            phase: Self::phase_of_day(hour),
            season: season.name(),
            weather: WeatherView {
                sky: sim.weather.sky.tag(),
                temp: sim.weather.temp.tag(),
                wet: sim.weather.is_wet(),
                windy: sim.weather.windy,
                phrase: sim.weather.sky.phrase(),
            },
            entities,
            occupancy,
            busiest,
            callouts,
            oak,
            events,
            bonds,
        }
    }
}

/// Classify a behavioural log line into a renderer kind-tag.
fn event_tag(msg: &str) -> &'static str {
    if msg.contains("Kick-off") || msg.contains("Full time") || msg.contains("Matchday") || msg.contains("match") {
        "match"
    } else if msg.contains("Old Oak") || msg.contains("the oak") {
        "oak"
    } else {
        "b"
    }
}

/// Whether the world is currently on a matchday (exposed for observers).
pub fn is_matchday(weekday: u64) -> bool {
    matchday::is_matchday(weekday)
}

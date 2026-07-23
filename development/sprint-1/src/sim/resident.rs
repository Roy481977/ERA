//! Resident entities (Phase 2) and their live movement/activity state.

use std::cmp::Reverse;

use crate::sim::routine::{Activity, Routine};
use crate::world::location::LocationId;
use crate::world::World;

/// Affordances that bypass a destination's opening hours: staff opening/working
/// their own premises, and going home to rest. Everything else is a visitor and
/// must find the destination open.
fn ignores_hours(affordance: &str) -> bool {
    affordance.starts_with("WORK") || affordance == "HOME" || affordance == "REST"
}

/// A small remembered event, owned by the resident it happened to.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Memory {
    pub day: u64,
    pub hour: u64,
    /// Short description, e.g. "shared a coffee with Victor at the Café".
    pub note: String,
    /// The other resident involved, if any (id).
    pub other: Option<&'static str>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Status {
    /// Not doing anything; will select next tick.
    Idle,
    /// Walking a path toward `dest` to perform `activity`.
    Traveling {
        activity: &'static str,
        purpose: &'static str,
        dest: LocationId,
        dur: u32,
        path: Vec<LocationId>,
        idx: usize, // currently leaving path[idx], heading to path[idx+1]
        leg_left: u32,
    },
    /// Performing `activity` at the current place.
    Performing {
        activity: &'static str,
        left: u32,
        /// The day this activity was begun (so a task that runs past midnight is
        /// credited to the day it started, not the new one).
        start_day: u64,
    },
}

/// A discrete, hand-authored piece of flavour that makes a resident *memorable* —
/// read in how they move (a limp, a cane, a carried load). Only a memorable subset
/// of the cast has one; scarcity is what makes them characters. See
/// design/resident-traits-and-signatures.md. Rendered by the compositor from the
/// entity's `sig` tag; every variant has a stable tag and is explainable.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum Signature {
    #[default]
    None,
    /// An old injury — an uneven gait, favouring one leg (Victor's footballer knee).
    Limp,
    /// Age and a walking stick — a stoop and a cane stroke (Agnes, Otto).
    Cane,
}

impl Signature {
    /// A stable tag emitted in the snapshot for the renderer.
    pub fn tag(&self) -> &'static str {
        match self {
            Signature::None => "none",
            Signature::Limp => "limp",
            Signature::Cane => "cane",
        }
    }
}

#[derive(Debug, Clone)]
pub struct Resident {
    pub id: &'static str,
    pub name: &'static str,
    pub age: u32,
    pub occupation: &'static str,
    pub home: LocationId,
    pub routine: Routine,
    /// A memorable, hand-authored physical signature (or `None`). Stable.
    pub signature: Signature,

    // disposition — social personality and the shape of a day
    /// A stable trait: how much this person seeks company. Roughly -2..=3.
    /// Set once, deterministically, at construction; it never changes.
    pub sociability: i32,
    /// How they feel right now: -1.0 (low) .. 1.0 (bright). Drifts toward 0 each
    /// tick and is lifted by good encounters, dented by bad ones. Carries a
    /// little from day to day.
    pub mood: f32,
    /// How much they have left in them: 1.0 rested .. ~0.05 spent. Wanes while
    /// out and about, recovers while resting at home, resets fresh each morning.
    pub energy: f32,

    // live state
    pub place: LocationId,
    pub status: Status,
    pub done_today: Vec<&'static str>,
    pub memories: Vec<Memory>,
    /// Deviations taken today (bounds spontaneity to keep the day coherent).
    pub deviations_today: u32,
    /// Extra ticks spent lingering with friends today (bounded).
    pub lingered_today: u32,
    /// Ticks spent waiting for a friend before setting out today (bounded).
    pub waited_today: u32,
}

/// A resident's stable sociability, decided once from their id. The known cast
/// gets hand-set personalities (a busker is outgoing; a man who keeps his corner
/// is not); anyone else derives a small, deterministic value from their id, so
/// any cast has a spread of temperaments without special-casing.
pub fn default_sociability(id: &str) -> i32 {
    match id {
        "res_milo" => 3,   // the busker — lives for a crowd
        "res_sofia" => 2,  // young apprentice, eager
        "res_tomas" => 2,  // a boy, out among everyone
        "res_hana" => 1,   // the baker, a warm word for each customer
        "res_karim" => 1,  // the kiosk — talks to all who pass
        "res_eva" => 1,    // the stall neighbour
        "res_agnes" => 0,  // the elder — present, unhurried
        "res_elias" => 0,
        "res_luca" => -1,  // keeps his corner
        "res_victor" => -1, // solitary by habit
        other => {
            // A stable −1..=2 spread from the id's bytes.
            let mut h: u32 = 2166136261;
            for b in other.bytes() {
                h ^= b as u32;
                h = h.wrapping_mul(16777619);
            }
            (h % 4) as i32 - 1
        }
    }
}

impl Resident {
    pub fn new(
        id: &'static str,
        name: &'static str,
        age: u32,
        occupation: &'static str,
        home: LocationId,
        activities: Vec<Activity>,
    ) -> Self {
        Resident {
            id,
            name,
            age,
            occupation,
            home,
            routine: Routine::new(activities),
            signature: Signature::None,
            sociability: default_sociability(id),
            mood: 0.0,
            energy: 1.0,
            place: home,
            status: Status::Idle,
            done_today: Vec::new(),
            memories: Vec::new(),
            deviations_today: 0,
            lingered_today: 0,
            waited_today: 0,
        }
    }

    /// Author a memorable physical signature onto this resident (chainable in the
    /// cast). Only a handful of the cast get one.
    pub fn with_sig(mut self, signature: Signature) -> Self {
        self.signature = signature;
        self
    }

    /// Whether the resident is socially available (present and not travelling).
    pub fn is_present(&self) -> bool {
        !matches!(self.status, Status::Traveling { .. })
    }

    /// The affordance a routine activity needs, by id (None for non-routine
    /// activities such as spontaneous deviations).
    pub fn affordance_of(&self, activity_id: &str) -> Option<&'static str> {
        self.routine
            .activities
            .iter()
            .find(|a| a.id == activity_id)
            .map(|a| a.affordance)
    }

    /// The human-readable purpose of one of this resident's routine activities.
    pub fn purpose_of(&self, activity_id: &str) -> Option<&'static str> {
        self.routine
            .activities
            .iter()
            .find(|a| a.id == activity_id)
            .map(|a| a.purpose)
    }

    /// Whether this resident is a child.
    pub fn is_child(&self) -> bool {
        self.age < 18
    }

    /// How ready this person is, right now, for company: their stable sociability
    /// lifted or dampened by how they feel and how much they have left. Roughly
    /// -7..=8. Zero is an average person in an ordinary mood with half a day's
    /// energy in them. This is the single dial every social gate reads, so a
    /// tired introvert and a bright extravert behave visibly differently.
    pub fn social_readiness(&self) -> i32 {
        let mood_pts = (self.mood.clamp(-1.0, 1.0) * 3.0).round() as i32; // -3..=3
        let energy_pts = ((self.energy.clamp(0.0, 1.0) - 0.5) * 4.0).round() as i32; // -2..=2
        self.sociability + mood_pts + energy_pts
    }

    /// Advance disposition by one tick. Energy wanes while out, recovers while
    /// resting at home; mood eases back toward neutral. Pure and deterministic.
    pub fn tick_disposition(&mut self) {
        let travelling = matches!(self.status, Status::Traveling { .. });
        let resting_home = self.place == self.home && !travelling;
        if resting_home {
            self.energy = (self.energy + 0.03).min(1.0);
        } else if travelling {
            self.energy = (self.energy - 0.005).max(0.05);
        } else {
            self.energy = (self.energy - 0.003).max(0.05);
        }
        // Feeling fades toward neutral unless something renews it.
        self.mood = (self.mood * 0.98).clamp(-1.0, 1.0);
    }

    /// A good (or poor) encounter colours the mood; bounded.
    pub fn nudge_mood(&mut self, delta: f32) {
        self.mood = (self.mood + delta).clamp(-1.0, 1.0);
    }

    /// Choose the most appropriate eligible, not-yet-done activity for this hour.
    ///
    /// Eligible means: its condition holds, it hasn't been done today, the hour
    /// lies inside its flexibility window, and its destination is open (unless
    /// the activity bypasses hours — staff/home). Among the eligible, the
    /// resident prefers the one it wants to be doing *soonest* (earliest
    /// preferred arrival), breaking ties by higher priority, then by routine
    /// order — so selection is fully deterministic.
    pub fn select(&self, hour: u64, weekday: u64, world: &World) -> Option<&Activity> {
        self.routine
            .activities
            .iter()
            .enumerate()
            .filter(|(_, a)| {
                a.condition.holds(weekday)
                    && !self.done_today.contains(&a.id)
                    && a.in_window(hour)
                    && self.destination_open(a, hour, world)
            })
            .min_by_key(|(i, a)| (a.preferred_arrival, Reverse(a.priority), *i))
            .map(|(_, a)| a)
    }

    /// Whether the activity's destination is open at `hour` (or exempt).
    fn destination_open(&self, a: &Activity, hour: u64, world: &World) -> bool {
        if ignores_hours(a.affordance) {
            return true;
        }
        match Routine::target_location(a, self.home) {
            Some(dest) => world.is_open(dest, hour),
            None => true,
        }
    }
}

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
    },
}

#[derive(Debug, Clone)]
pub struct Resident {
    pub id: &'static str,
    pub name: &'static str,
    pub age: u32,
    pub occupation: &'static str,
    pub home: LocationId,
    pub routine: Routine,

    // live state
    pub place: LocationId,
    pub status: Status,
    pub done_today: Vec<&'static str>,
    pub memories: Vec<Memory>,
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
            place: home,
            status: Status::Idle,
            done_today: Vec::new(),
            memories: Vec::new(),
        }
    }

    /// Whether the resident is socially available (present and not travelling).
    pub fn is_present(&self) -> bool {
        !matches!(self.status, Status::Traveling { .. })
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

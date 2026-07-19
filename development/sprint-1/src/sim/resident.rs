//! Resident entities (Phase 2) and their live movement/activity state.

use std::cmp::Reverse;

use crate::sim::routine::{Activity, Routine};
use crate::world::location::LocationId;

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
        }
    }

    /// Choose the most appropriate eligible, not-yet-done activity for this hour.
    ///
    /// Eligible means: its condition holds, it hasn't been done today, and the
    /// hour lies inside its flexibility window. Among the eligible, the resident
    /// prefers the one it wants to be doing *soonest* (earliest preferred
    /// arrival), breaking ties by higher priority, then by routine order — so
    /// selection is fully deterministic.
    pub fn select(&self, hour: u64) -> Option<&Activity> {
        self.routine
            .activities
            .iter()
            .enumerate()
            .filter(|(_, a)| {
                a.condition.holds() && !self.done_today.contains(&a.id) && a.in_window(hour)
            })
            .min_by_key(|(i, a)| (a.preferred_arrival, Reverse(a.priority), *i))
            .map(|(_, a)| a)
    }
}

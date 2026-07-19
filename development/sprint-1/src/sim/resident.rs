//! Resident entities (Phase 2) and their live movement/activity state.

use crate::sim::clock::Block;
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

    /// Choose the highest-priority eligible, not-yet-done activity for this block.
    /// Deterministic: ties broken by the activity's order in the routine.
    pub fn select(&self, block: Block) -> Option<&Activity> {
        self.routine
            .activities
            .iter()
            .filter(|a| a.window.contains(&block) && !self.done_today.contains(&a.id))
            .max_by_key(|a| a.priority)
    }
}

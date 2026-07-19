//! Routines (Phase 2): goal-and-time models, NOT fixed clock->place schedules.
//!
//! A routine is a set of *activities*, each defined by the affordance it needs,
//! the time-blocks in which it is appropriate, a priority, and a duration. Each
//! tick a resident selects the highest-priority eligible activity it has not yet
//! done today. This is deliberately a proto-intention (CD-006): future
//! decision-making (needs, mood, relationships, interruptions) can modify
//! *selection* without changing the structure — so behaviour can evolve
//! naturally rather than being hard-coded to the clock.

use crate::sim::clock::Block;
use crate::world::location::LocationId;

#[derive(Debug, Clone)]
pub struct Activity {
    pub id: &'static str,
    pub purpose: &'static str,
    /// Affordance the activity needs. The special value "HOME" resolves to the
    /// resident's own home location.
    pub affordance: &'static str,
    /// Time-blocks in which this activity is appropriate.
    pub window: &'static [Block],
    /// Higher wins when several activities are eligible.
    pub priority: u32,
    /// Ticks to perform once at the location.
    pub duration: u32,
}

#[derive(Debug, Clone)]
pub struct Routine {
    pub activities: Vec<Activity>,
}

impl Routine {
    pub fn new(activities: Vec<Activity>) -> Self {
        Routine { activities }
    }

    /// Resolve the affordance to a concrete location (HOME -> the resident's home).
    pub fn target_location(activity: &Activity, home: LocationId) -> Option<LocationId> {
        if activity.affordance == "HOME" {
            Some(home)
        } else {
            crate::world::location::location_for_affordance(activity.affordance)
        }
    }
}

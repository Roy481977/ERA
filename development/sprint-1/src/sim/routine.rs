//! Routines (Phase 2): proto-intentions, NOT fixed clock->place schedules.
//!
//! A routine is a set of *activities*. Each activity says what a resident wants
//! to do, where (a preferred destination), *when* they'd prefer to arrive, how
//! much slack that time has (a flexibility window), and an optional condition
//! that must hold for it to be considered at all. Each idle tick a resident
//! selects the most appropriate eligible activity it has not yet done today.
//!
//! This is deliberately a proto-intention (CD-006). The shape already carries
//! the hooks a future decision-making layer needs — a preferred time it can slip
//! within, a place it can override, and a condition gate — so needs, mood,
//! relationships, and interruptions can change *selection* later without a
//! redesign. Today every condition is `Always`; the door is simply left open.

use crate::world::location::LocationId;

/// A gate that must hold for an activity to be eligible. This is the seam where
/// future needs/mood/relationship conditions attach without changing the routine
/// structure. Today: `Always`, plus weekday gating so routines vary by day.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Condition {
    /// Always eligible.
    Always,
    /// Eligible only on the listed weekdays (0 = Monday … 6 = Sunday).
    OnWeekdays(&'static [u64]),
}

impl Condition {
    /// Whether the condition holds on the given weekday. Deterministic and
    /// side-effect free.
    pub fn holds(&self, weekday: u64) -> bool {
        match self {
            Condition::Always => true,
            Condition::OnWeekdays(days) => days.contains(&weekday),
        }
    }
}

#[derive(Debug, Clone)]
pub struct Activity {
    pub id: &'static str,
    pub purpose: &'static str,
    /// Affordance the activity needs. The special value "HOME" resolves to the
    /// resident's own home location. Used only when `dest` is `None`.
    pub affordance: &'static str,
    /// Optional preferred destination. When set, it overrides affordance
    /// resolution — this is how an activity pins an exact place even when its
    /// affordance is shared by several locations.
    pub dest: Option<LocationId>,
    /// Preferred arrival hour (0..24). The resident aims to be doing this around
    /// here; it is a preference, not a hard timestamp.
    pub preferred_arrival: u64,
    /// Slack around the preferred arrival, in hours. The activity is eligible
    /// while the hour lies within `[preferred_arrival - flexibility,
    /// preferred_arrival + flexibility]` (clamped at 0).
    pub flexibility: u64,
    /// Breaks ties when several activities are eligible at once (higher wins).
    pub priority: u32,
    /// Ticks to perform once at the location.
    pub duration: u32,
    /// Gate that must hold for the activity to be considered.
    pub condition: Condition,
}

impl Activity {
    /// Whether `hour` falls inside this activity's flexibility window.
    pub fn in_window(&self, hour: u64) -> bool {
        let lo = self.preferred_arrival.saturating_sub(self.flexibility);
        let hi = self.preferred_arrival + self.flexibility;
        hour >= lo && hour <= hi
    }

    /// Restrict this activity to the given weekdays (0 = Mon … 6 = Sun).
    pub fn on_weekdays(mut self, days: &'static [u64]) -> Self {
        self.condition = Condition::OnWeekdays(days);
        self
    }
}

#[derive(Debug, Clone)]
pub struct Routine {
    pub activities: Vec<Activity>,
}

impl Routine {
    pub fn new(activities: Vec<Activity>) -> Self {
        Routine { activities }
    }

    /// Resolve an activity to a concrete location: an explicit `dest` wins;
    /// otherwise "HOME" resolves to the resident's home and any other affordance
    /// is resolved against the world.
    pub fn target_location(activity: &Activity, home: LocationId) -> Option<LocationId> {
        if let Some(dest) = activity.dest {
            Some(dest)
        } else if activity.affordance == "HOME" {
            Some(home)
        } else {
            crate::world::location::location_for_affordance(activity.affordance)
        }
    }
}

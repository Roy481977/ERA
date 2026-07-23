//! The old dog (Book of ERA, Book IV — "The old dog").
//!
//! He belongs to no one and to the entire district. He is not a mascot, helper,
//! guide or quest giver — he is simply *there*. He keeps his own gentle daily
//! rhythm through the public places, forms a quiet bond with a child, and ages.
//! He grants nothing. His value is presence, continuity and memory.
//!
//! Deliberately NOT a mechanic: he has no reward, no unlock, no gameplay effect.
//! He is ambient life the world carries whether or not anyone is watching.

use crate::world::location::LocationId;
use crate::sim::wildlife::Trip;

pub const DOG_ID: &str = "the_old_dog";
pub const DOG_NAME: &str = "the old dog";

/// The child he may come to know (Book IV: "He may form a quiet bond with a child").
pub const CHILD_ID: &str = "res_tomas";

/// After roaming this many days he tires of the long walk to the Stadium and keeps
/// closer to the Oak. (Compressed for observability — see the repo status note.)
const STADIUM_STOP_DAY: u64 = 28;
/// He slows by one rest-tick roughly every fortnight.
const SLOW_EVERY: u64 = 14;

#[derive(Debug, Clone)]
pub struct Dog {
    pub place: LocationId,
    /// Days since the world opened. He is already old when we meet him; this is
    /// how his ageing *shows*, not his true age.
    pub age_days: u64,
    /// A quiet bond with the child, deepened by shared moments (never a score the
    /// player reads; only its consequences are meant to be seen).
    pub bond_with_child: u32,
    /// Ticks he rests between ambles (grows as he ages).
    move_cooldown: u32,
    met_child_today: bool,
    last_day: u64,
    /// A current amble-leg between two adjacent places (None when settled).
    trip: Option<Trip>,
}

impl Default for Dog {
    fn default() -> Self {
        Dog {
            place: "loc_riverside", // beneath the Old Oak
            age_days: 0,
            bond_with_child: 0,
            move_cooldown: 0,
            met_child_today: false,
            last_day: 0,
            trip: None,
        }
    }
}

impl Dog {
    pub fn new() -> Self {
        Self::default()
    }

    /// Where he would rather be at this hour. Older, he skips the far Stadium and
    /// keeps to the Oak and the square.
    pub fn preferred_spot(&self, hour: u64) -> LocationId {
        let roams_far = self.age_days < STADIUM_STOP_DAY;
        match hour {
            6..=11 => "loc_cafe",         // by the café door, where they set down water
            12..=15 => "loc_main_square", // a patch of warm light by the fountain
            16..=18 => {
                if roams_far {
                    "loc_stadium" // lies outside the Club
                } else {
                    "loc_main_square"
                }
            }
            19..=21 => "loc_bridge", // an evening by the old bridge
            _ => "loc_riverside",    // night, beneath the Old Oak
        }
    }

    /// How long he rests between amble-steps — a gentle ~10 minutes per step, a
    /// little longer as he ages. Short enough that he actually reaches the spot he
    /// wants and then dwells there (once at his spot he simply stays).
    fn move_interval(&self) -> u32 {
        2 + (self.age_days / SLOW_EVERY) as u32
    }

    /// A gentle description of him settling somewhere.
    pub fn settle_phrase(place: LocationId) -> &'static str {
        match place {
            "loc_riverside" => "settles beneath the Old Oak",
            "loc_cafe" => "curls by the café door, where they set down water for him",
            "loc_main_square" => "finds a patch of warm light on the square",
            "loc_stadium" => "lies in the long shade outside the Club",
            "loc_bridge" => "settles by the old bridge, watching the water go by",
            _ => "settles down a while",
        }
    }

    // --- internals used by the simulation ---

    pub(crate) fn roll_day(&mut self, day: u64) {
        if day != self.last_day {
            self.age_days = day;
            self.met_child_today = false;
            self.last_day = day;
        }
    }

    pub(crate) fn cooldown(&self) -> u32 {
        self.move_cooldown
    }
    pub(crate) fn tick_cooldown(&mut self) {
        if self.move_cooldown > 0 {
            self.move_cooldown = self.move_cooldown.saturating_sub(1);
        }
    }
    pub(crate) fn arrive(&mut self, place: LocationId) {
        self.place = place;
        self.trip = None;
        self.move_cooldown = self.move_interval();
    }
    /// Set out along one nav edge, walked over `total` ticks (like residents/wildlife).
    pub(crate) fn begin_trip(&mut self, to: LocationId, total: u32) {
        let total = total.max(1);
        self.trip = Some(Trip { from: self.place, to, total, left: total });
    }
    pub(crate) fn stepping(&self) -> bool { self.trip.is_some() }
    /// Advance the current leg one tick; returns the destination the tick he arrives.
    pub(crate) fn step_trip(&mut self) -> Option<LocationId> {
        if let Some(t) = self.trip.as_mut() {
            t.left = t.left.saturating_sub(1);
            if t.left == 0 { let dest = t.to; self.trip = None; return Some(dest); }
        }
        None
    }
    pub(crate) fn trip(&self) -> Option<Trip> { self.trip }
    pub(crate) fn met_child_today(&self) -> bool {
        self.met_child_today
    }
    pub(crate) fn meet_child(&mut self) {
        self.met_child_today = true;
        self.bond_with_child += 1;
    }
}

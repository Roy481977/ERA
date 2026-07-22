//! Monday-night town festival: a separate town event (NOT the football matchday).
//!
//! One evening a week — Monday — the whole town gathers in the Main Square for
//! music, dancing and fun for a few hours. Unlike matchday (which only pulls the
//! supporters to the ground), the festival draws *everyone*: every resident sets
//! aside their evening routine and heads to the square, then home when it winds up.
//!
//! Deterministic and self-contained. The renderer lights the square and dances the
//! crowd on the same schedule (see the compositor's `festivalOn`).

use crate::sim::resident::Resident;

pub const FESTIVAL_WEEKDAY: u64 = 0; // Monday (0 = Monday)
pub const START_HOUR: u64 = 19; // gathering runs 19:00–22:00
pub const END_HOUR: u64 = 22;
pub const GATHER_FROM: u64 = 18; // people start drifting in from 18:00 so they're there by 19

pub fn is_festival_day(weekday: u64) -> bool {
    weekday == FESTIVAL_WEEKDAY
}

/// True during the lit, dancing window (used by the behaviour layer to pose the
/// crowd, and mirrored by the renderer for the lights).
pub fn is_festival_time(weekday: u64, hour: u64) -> bool {
    is_festival_day(weekday) && (START_HOUR..END_HOUR).contains(&hour)
}

/// A synthetic festival action injected ahead of the normal routine — for
/// everyone, not a select list.
pub struct FestAct {
    pub dest: &'static str,
    pub purpose: &'static str,
    pub id: &'static str,
    pub duration: u32,
}

/// Consider a festival action for a resident. `None` off-Monday, outside the
/// windows, or once they've gone home — then the ordinary routine runs.
pub fn consider(me: &Resident, weekday: u64, hour: u64) -> Option<FestAct> {
    if !is_festival_day(weekday) {
        return None;
    }
    let went = me.done_today.contains(&"fest_attend");
    let homed = me.done_today.contains(&"fest_home");

    // Head to the square from early evening and stay through the gathering. A short,
    // re-issued action (not one long block) so late arrivers don't linger past the end —
    // everyone leaves together when it winds up, with time to get home before the day ends.
    if (GATHER_FROM..END_HOUR).contains(&hour) && !homed {
        return Some(FestAct {
            dest: "loc_main_square",
            purpose: "at the town gathering — music and dancing in the square",
            id: "fest_attend",
            duration: 1,
        });
    }

    // When it winds up, everyone makes their way home.
    if hour >= END_HOUR && went && !homed {
        return Some(FestAct {
            dest: me.home,
            purpose: "heads home after the town gathering",
            id: "fest_home",
            duration: 1,
        });
    }

    None
}

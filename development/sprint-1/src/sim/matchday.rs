//! Matchday (Phase 7): one event that changes the whole district.
//!
//! Every Saturday the club plays. Football itself is deliberately minimal — the
//! result is seeded per week — because the point is the *town's* reaction:
//! supporters drift to the stadium, others keep the café open, and win, draw, or
//! loss changes how the evening goes and what the Old Oak receives.

use crate::sim::resident::Resident;
use crate::sim::social::seed_hash;

pub const MATCH_WEEKDAY: u64 = 5; // Saturday (0 = Monday)
pub const KICKOFF: u64 = 15;
pub const FULL_TIME: u64 = 17;

pub fn is_matchday(weekday: u64) -> bool {
    weekday == MATCH_WEEKDAY
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MatchResult {
    Win,
    Draw,
    Loss,
}

impl MatchResult {
    /// Seeded, deterministic result for a given week index.
    pub fn for_week(week: u64) -> MatchResult {
        match seed_hash(&["rain-town-match"], week) % 3 {
            0 => MatchResult::Win,
            1 => MatchResult::Draw,
            _ => MatchResult::Loss,
        }
    }

    pub fn verb(&self) -> &'static str {
        match self {
            MatchResult::Win => "won",
            MatchResult::Draw => "drew",
            MatchResult::Loss => "lost",
        }
    }
}

/// Who goes to the football. A deliberately individual list — not everyone.
pub fn is_supporter(id: &str) -> bool {
    matches!(
        id,
        "res_victor" | "res_elias" | "res_agnes" | "res_tomas" | "res_milo" | "res_karim"
    )
}

/// A synthetic matchday action injected ahead of the normal routine.
pub struct MatchAct {
    pub dest: &'static str,
    pub purpose: &'static str,
    pub id: &'static str,
    pub duration: u32,
}

/// Consider a matchday action for a supporter. Returns `None` on non-matchdays,
/// for non-supporters, or outside the match windows (then the routine runs).
pub fn consider(me: &Resident, weekday: u64, hour: u64, result: MatchResult) -> Option<MatchAct> {
    if !is_matchday(weekday) || !is_supporter(me.id) {
        return None;
    }
    let attended = me.done_today.contains(&"match_attend");
    let aftered = me.done_today.contains(&"match_after");

    // Pre-match: head to the ground in time for kick-off.
    if (12..=14).contains(&hour) && !attended {
        return Some(MatchAct {
            dest: "loc_stadium",
            purpose: "heads to the match",
            id: "match_attend",
            duration: 3,
        });
    }

    // After full time: the result shapes the evening.
    if (FULL_TIME..=19).contains(&hour) && attended && !aftered {
        // Post-match gatherings happen in the square, next to the ground, so
        // supporters still have time to get home before the day ends.
        return Some(match result {
            MatchResult::Win => MatchAct {
                dest: "loc_main_square",
                purpose: "celebrates the win in the square",
                id: "match_after",
                duration: 2,
            },
            MatchResult::Draw => MatchAct {
                dest: "loc_main_square",
                purpose: "lingers in the square after the draw",
                id: "match_after",
                duration: 1,
            },
            MatchResult::Loss => MatchAct {
                dest: me.home,
                purpose: "heads home quietly after the defeat",
                id: "match_after",
                duration: 1,
            },
        });
    }

    // Once the post-match gathering is done, a supporter makes their way home
    // and skips the rest of the day's routine (they spent it at the football).
    if aftered && me.place != me.home {
        return Some(MatchAct {
            dest: me.home,
            purpose: "makes their way home after the football",
            id: "match_home",
            duration: 1,
        });
    }

    None
}

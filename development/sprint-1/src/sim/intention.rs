//! Intentions & small deviations (Phase 5).
//!
//! The routine is still the default plan. But before a resident who is winding
//! down for the day simply heads home, a lightweight, deterministic intention
//! layer asks: is there a reason in the *world right now* to do something else?
//! The one implemented deviation is social — if a friend is nearby at an open
//! public place and there is still time, the resident may detour to join them.
//!
//! Every deviation is deterministic (seeded, no RNG), bounded (once per day), and
//! explainable (it returns the reason it happened). It never strands a resident:
//! it only triggers when there is provably time to visit and still get home.

use crate::sim::resident::Resident;
use crate::sim::social::{seed_hash, Bonds, Relationships};
use crate::world::navigation::NavGraph;
use crate::world::World;

/// A snapshot entry of where a resident is at the start of the tick.
pub type Presence = (&'static str, &'static str, &'static str, bool); // (id, name, place, present)

/// A chosen deviation from routine.
pub struct Deviation {
    pub dest: &'static str,
    pub purpose: &'static str,
    pub activity_id: &'static str,
    pub duration: u32,
    /// Full, human-readable explanation for the event log.
    pub reason: String,
}

const AFFINITY_TO_VISIT: i32 = 2;
const VISIT_TICKS: u32 = 2;
const END_OF_DAY: u64 = 23;
/// How many shared meetings make a place *theirs* — worth going to on the
/// chance of meeting again.
const REUNION_MIN_MEETINGS: u32 = 6;

fn is_social_place(place: &str) -> bool {
    place == "loc_cafe" || place == "loc_main_square"
}

/// Consider a deviation for a resident who is idle and whose routine would next
/// send them home. Returns `Some(Deviation)` to override that plan.
#[allow(clippy::too_many_arguments)]
pub fn consider_social_detour(
    me: &Resident,
    hour: u64,
    tick: u64,
    presence: &[Presence],
    rels: &Relationships,
    world: &World,
    nav: &NavGraph,
    readiness: i32,
) -> Option<Deviation> {
    if me.deviations_today > 0 {
        return None;
    }
    // Late afternoon / early evening: the natural window for "one more stop".
    if !(15..=19).contains(&hour) {
        return None;
    }

    // Find the best present friend at a reachable, open, public place.
    let mut best: Option<(&'static str, &'static str, &'static str, i32, u32)> = None; // id,name,place,affinity,travel
    for &(fid, fname, fplace, present) in presence {
        if fid == me.id || !present || fplace == me.place {
            continue;
        }
        if !is_social_place(fplace) || !world.is_open(fplace, hour) {
            continue;
        }
        let affinity = rels.get(me.id, fid).affinity;
        if affinity < AFFINITY_TO_VISIT {
            continue;
        }
        let to = match nav.travel_time(me.place, fplace) {
            Some(t) => t,
            None => continue,
        };
        let home = match nav.travel_time(fplace, me.home) {
            Some(t) => t,
            None => continue,
        };
        // Must still get there, visit, and reach home before the day ends.
        if hour + to as u64 + VISIT_TICKS as u64 + home as u64 > END_OF_DAY {
            continue;
        }
        // Prefer the closest bond, then the nearer place, then id (deterministic).
        let better = match best {
            None => true,
            Some((_, _, _, a, t)) => (affinity, std::cmp::Reverse(to)) > (a, std::cmp::Reverse(t)),
        };
        if better {
            best = Some((fid, fname, fplace, affinity, to));
        }
    }

    let (fid, fname, fplace, _aff, _to) = best?;

    // Deterministic gate: even with a friend present, they don't always detour.
    // Someone bright and full of energy turns aside for a friend far more readily
    // than someone spent and withdrawn.
    let gate = (55 + readiness * 4).clamp(15, 90) as u64;
    if seed_hash(&[me.id, fid, fplace, "detour"], tick) % 100 >= gate {
        return None;
    }

    let place_name = world.location(fplace).map(|l| l.name).unwrap_or(fplace);
    let reason = format!(
        "{} meant to head home, but {} was at the {} and the two are close — {} detours to join them",
        me.name, fname, place_name, me.name
    );
    Some(Deviation {
        dest: fplace,
        purpose: "a spur-of-the-moment visit",
        activity_id: "dev_social_visit",
        duration: VISIT_TICKS,
        reason,
    })
}

/// Consider going to a place two residents have made *theirs* — heading there on
/// the memory of past meetings, expecting (not knowing) a friend might be there.
/// This is remembered shared experience shaping where someone goes.
#[allow(clippy::too_many_arguments)]
pub fn consider_reunion(
    me: &Resident,
    hour: u64,
    tick: u64,
    presence: &[Presence],
    bonds: &Bonds,
    rels: &Relationships,
    world: &World,
    nav: &NavGraph,
    readiness: i32,
) -> Option<Deviation> {
    if me.deviations_today > 0 {
        return None;
    }
    if !(15..=19).contains(&hour) {
        return None;
    }
    // The friend with the strongest shared place worth going to.
    let mut best: Option<(&'static str, &'static str, &'static str, u32)> = None; // fid, fname, place, meetings
    for &(fid, fname, _fplace, _present) in presence {
        if fid == me.id || rels.get(me.id, fid).affinity < AFFINITY_TO_VISIT {
            continue;
        }
        let meetings = bonds.meetings(me.id, fid);
        if meetings < REUNION_MIN_MEETINGS {
            continue;
        }
        let Some(place) = bonds.usual_place(me.id, fid) else { continue };
        if place == me.place || !is_social_place(place) || !world.is_open(place, hour) {
            continue;
        }
        let (Some(to), Some(home)) = (nav.travel_time(me.place, place), nav.travel_time(place, me.home)) else {
            continue;
        };
        if hour + to as u64 + VISIT_TICKS as u64 + home as u64 > END_OF_DAY {
            continue;
        }
        let better = best.map(|(_, _, _, m)| meetings > m).unwrap_or(true);
        if better {
            best = Some((fid, fname, place, meetings));
        }
    }

    let (fid, fname, place, _m) = best?;
    let gate = (45 + readiness * 4).clamp(15, 90) as u64;
    if seed_hash(&[me.id, fid, place, "reunion"], tick) % 100 >= gate {
        return None;
    }
    let place_name = world.location(place).map(|l| l.name).unwrap_or(place);
    let reason = format!(
        "{} drifts to the {}, half-expecting to find {} — it's where they always meet",
        me.name, place_name, fname
    );
    Some(Deviation {
        dest: place,
        purpose: "their usual corner",
        activity_id: "dev_reunion",
        duration: VISIT_TICKS,
        reason,
    })
}

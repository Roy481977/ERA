//! Ambient life (Sprint 3 — density).
//!
//! A layer *over* the existing behavioural systems, not a replacement. It carries
//! the small, continuous life that makes an hour feel lived rather than scheduled:
//! the town's own routines (the bakery opening, the train passing, bells, school),
//! the micro-life that moves whether or not anyone is watching (sparrows, pigeons,
//! a cat, the fox), and — assembled in the simulation — the incidental *moments*
//! of the residents themselves.
//!
//! These are not gameplay events. They are texture. Everything here is a pure,
//! deterministic function of the day and hour (plus a seed), so replays are
//! identical.

use crate::sim::social::seed_hash;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AmbientKind {
    /// The town's own routines and institutions.
    Town,
    /// Small living things moving through the district.
    Micro,
    /// A resident's small incidental moment.
    Moment,
}

impl AmbientKind {
    pub fn tag(&self) -> &'static str {
        match self {
            AmbientKind::Town => "town",
            AmbientKind::Micro => "micro",
            AmbientKind::Moment => "moment",
        }
    }
}

/// One ambient line, timestamped within the hour so an hour has inner order.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Ambient {
    pub tick: u64,
    pub day: u64,
    pub hour: u64,
    pub minute: u8,
    pub kind: AmbientKind,
    pub actor: &'static str,
    pub text: String,
}

/// A generated line before it is stamped with tick/day/hour.
pub struct Line {
    pub minute: u8,
    pub kind: AmbientKind,
    pub actor: &'static str,
    pub text: &'static str,
}

fn line(minute: u8, kind: AmbientKind, actor: &'static str, text: &'static str) -> Line {
    Line { minute, kind, actor, text }
}

const MON_TO_FRI: [u64; 5] = [0, 1, 2, 3, 4];

/// The town's own day: institutions and routines that run on the clock,
/// independent of any named resident. Weekday-aware (school on weekdays, bells on
/// Sunday, the ground readied on matchday Saturdays).
pub fn background(_day: u64, hour: u64, weekday: u64) -> Vec<Line> {
    use AmbientKind::Town;
    let mut v = Vec::new();
    let is_school_day = MON_TO_FRI.contains(&weekday);
    let is_sunday = weekday == 6;
    let is_matchday = weekday == 5;

    match hour {
        4 => {
            v.push(line(0, Town, "the bakery", "the baker's light reaches the wet street; the ovens are lit"));
            v.push(line(40, Town, "the newspapers", "a van drops a bound stack of papers at the kiosk"));
        }
        5 => {
            v.push(line(0, Town, "the bakery", "the bakery rolls up its shutter"));
            if is_matchday {
                v.push(line(30, Town, "the stadium", "the first stadium staff arrive; a gate is unlocked"));
            }
        }
        6 => {
            v.push(line(10, Town, "the café", "the café sets out its tables and lights the urn"));
            v.push(line(45, Town, "a delivery", "a delivery of milk and crates is left at the café door"));
        }
        7 => {
            v.push(line(0, Town, "the train", "the morning train passes, dividing the day"));
            if is_matchday {
                v.push(line(30, Town, "the stadium", "vans unload barrels and pies at the ground"));
            }
        }
        8 => {
            if is_school_day {
                v.push(line(0, Town, "the school", "the school bell rings; children file in"));
            }
            v.push(line(20, Town, "the groundsman", "the roller is dragged the length of the pitch"));
        }
        9 => {
            if is_sunday {
                v.push(line(0, Town, "the church", "church bells call across the district"));
            }
            v.push(line(30, Town, "the museum", "the museum unlocks its doors and props them open"));
        }
        12 => {
            v.push(line(0, Town, "the train", "the midday train passes"));
        }
        13 => {
            v.push(line(0, Town, "the church", "the bells sound the hour over the rooftops"));
        }
        15 => {
            if is_school_day {
                v.push(line(0, Town, "the school", "the school empties; children spill toward the square"));
            }
        }
        17 => {
            v.push(line(0, Town, "the bakery", "the bakery draws in its shutter for the day"));
        }
        18 => {
            v.push(line(0, Town, "the train", "the evening train passes; the day tips toward night"));
        }
        20 => {
            v.push(line(0, Town, "the café", "the café stacks its outdoor chairs"));
            v.push(line(30, Town, "the lamps", "the lamps come on one by one along the High Street"));
        }
        22 => {
            v.push(line(0, Town, "the café", "the café dims its lights and turns the sign"));
        }
        _ => {}
    }
    v
}

/// Small living things. Mostly scheduled to the time of day, with a little seeded
/// variation so the district is never quite the same twice — yet always the same
/// for a given seed.
pub fn microlife(day: u64, hour: u64, _weekday: u64) -> Vec<Line> {
    use AmbientKind::Micro;
    let mut v = Vec::new();
    let r = seed_hash(&["micro"], day * 24 + hour) % 100;

    match hour {
        5 => v.push(line(15, Micro, "sparrows", "sparrows start up an argument in the Old Oak")),
        6 => v.push(line(20, Micro, "gulls", "two gulls follow the river inland and wheel back")),
        7 => {
            v.push(line(5, Micro, "a cyclist", "a cyclist rattles over the old bridge"));
            if r < 50 {
                v.push(line(40, Micro, "pigeons", "pigeons lift from the square and settle again"));
            }
        }
        8..=10 => {
            if r < 60 {
                v.push(line(25, Micro, "a cat", "a tabby watches the street from the bakery sill"));
            }
        }
        11..=13 => {
            v.push(line(10, Micro, "pigeons", "pigeons gather at the fountain for crumbs"));
            if r < 45 {
                v.push(line(50, Micro, "a cat", "a cat crosses, unhurried, from one warm sill to another"));
            }
        }
        14..=16 => {
            if r < 55 {
                v.push(line(30, Micro, "a dog", "somewhere a dog barks twice and stops"));
            }
        }
        18 => v.push(line(20, Micro, "crows", "crows return to the museum chimney, one after another")),
        19 => {
            if r < 50 {
                v.push(line(15, Micro, "bats", "bats stitch the air above the riverside"));
            }
        }
        23 | 0 => {
            if r < 70 {
                v.push(line(30, Micro, "a fox", "a fox slips along the riverside path, and is gone"));
            }
        }
        _ => {}
    }
    v
}

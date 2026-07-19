//! The Old Oak (Phase 6): a persistent living world object.
//!
//! The Oak is not a resident and makes no decisions. It is a piece of world
//! truth that *accumulates* — visits, gatherings, and the marks left by important
//! events (a scarf after a victory, flowers after a loss). It owns its own age,
//! seasonal state, and history; other systems record into it through `record`,
//! but never rewrite what is already there. Its history is append-only and ready
//! to be serialised later.

use crate::sim::clock::DAYS_PER_WEEK;

pub const OAK_ID: &str = "obj_old_oak";
pub const OAK_LOCATION: &str = "loc_riverside";

/// The Oak's seasonal/visual state (data, not graphics).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Season {
    Summer,
    Autumn,
    Winter,
    Spring,
}

impl Season {
    /// Season for a given day. Seasons last four weeks; day 0 is high summer
    /// (the world opens in July). Purely a function of the day — deterministic.
    pub fn for_day(day: u64) -> Season {
        let weeks = day / DAYS_PER_WEEK;
        match (weeks / 4) % 4 {
            0 => Season::Summer,
            1 => Season::Autumn,
            2 => Season::Winter,
            _ => Season::Spring,
        }
    }

    /// How the Oak looks this season.
    pub fn appearance(&self) -> &'static str {
        match self {
            Season::Summer => "in full green leaf",
            Season::Autumn => "turning gold",
            Season::Winter => "bare against the sky",
            Season::Spring => "budding pale green",
        }
    }

    pub fn name(&self) -> &'static str {
        match self {
            Season::Summer => "Summer",
            Season::Autumn => "Autumn",
            Season::Winter => "Winter",
            Season::Spring => "Spring",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OakEventKind {
    Visit,
    ChildrenPlay,
    Gathering,
    ScarfTied,
    FlowersLeft,
}

impl OakEventKind {
    fn phrase(&self) -> &'static str {
        match self {
            OakEventKind::Visit => "sat a while beneath the Oak",
            OakEventKind::ChildrenPlay => "played beneath the Oak",
            OakEventKind::Gathering => "met beside the Oak",
            OakEventKind::ScarfTied => "tied a club scarf to a branch",
            OakEventKind::FlowersLeft => "left flowers at the roots",
        }
    }
}

/// One entry in the Oak's living history.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OakEvent {
    pub day: u64,
    pub hour: u64,
    pub kind: OakEventKind,
    /// Primary resident (id), if any.
    pub who: Option<&'static str>,
    /// A second resident (id) for shared moments.
    pub with: Option<&'static str>,
}

/// The Old Oak — persistent identity, age, seasonal state, and history.
#[derive(Debug, Clone)]
pub struct OldOak {
    pub id: &'static str,
    pub location: &'static str,
    pub age_years: u32,
    pub history: Vec<OakEvent>,
    pub visit_count: u32,
    pub scarves: u32,
    pub bouquets: u32,
}

impl Default for OldOak {
    fn default() -> Self {
        OldOak {
            id: OAK_ID,
            location: OAK_LOCATION,
            age_years: 400,
            history: Vec::new(),
            visit_count: 0,
            scarves: 0,
            bouquets: 0,
        }
    }
}

impl OldOak {
    pub fn new() -> Self {
        Self::default()
    }

    /// The Oak's seasonal state on a given day.
    pub fn season(&self, day: u64) -> Season {
        Season::for_day(day)
    }

    /// Append an event to the Oak's history and update its tallies.
    pub fn record(&mut self, ev: OakEvent) {
        match ev.kind {
            OakEventKind::Visit | OakEventKind::ChildrenPlay => self.visit_count += 1,
            OakEventKind::ScarfTied => self.scarves += 1,
            OakEventKind::FlowersLeft => self.bouquets += 1,
            OakEventKind::Gathering => {}
        }
        self.history.push(ev);
    }

    /// A concise, readable history. `name_of` resolves a resident id to a name.
    pub fn readable_history(&self, name_of: impl Fn(&str) -> String) -> Vec<String> {
        self.history
            .iter()
            .map(|e| {
                let wd = crate::sim::clock::WEEKDAY_NAMES[(e.day % DAYS_PER_WEEK) as usize];
                let who = e.who.map(&name_of).unwrap_or_default();
                match (e.kind, e.with) {
                    (OakEventKind::Gathering, Some(b)) => format!(
                        "Day {} ({}) {:02}:00 — {} and {} {}",
                        e.day, wd, e.hour, who, name_of(b), e.kind.phrase()
                    ),
                    _ => format!(
                        "Day {} ({}) {:02}:00 — {} {}",
                        e.day, wd, e.hour, who, e.kind.phrase()
                    ),
                }
            })
            .collect()
    }
}

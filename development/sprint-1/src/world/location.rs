//! The five semantic locations of the first district (DS-001 §1).
//!
//! A Location is a *logical* place with semantic affordances — not a graphical
//! asset. Affordances (not coordinates) are what routines resolve against.

pub type LocationId = &'static str;

/// A location's opening window, in WorldClock hours: open at `open`, shut at
/// `close` (open ≤ hour < close). Locations without hours are always accessible.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct OpenHours {
    pub open: u64,
    pub close: u64,
}

impl OpenHours {
    pub fn is_open(&self, hour: u64) -> bool {
        hour >= self.open && hour < self.close
    }
}

#[derive(Debug, Clone)]
pub struct Location {
    pub id: LocationId,
    pub name: &'static str,
    pub affordances: &'static [&'static str],
    /// Opening window, if this location opens and closes. `None` = always open.
    pub hours: Option<OpenHours>,
}

impl Location {
    /// Whether this location is accessible at `hour`.
    pub fn is_open(&self, hour: u64) -> bool {
        match self.hours {
            Some(h) => h.is_open(hour),
            None => true,
        }
    }
}

/// The locations of the First Breath district (stable order).
///
/// Five civic/work places plus three residential nodes. Residences carry only
/// `HOME` (and `REST`): they are where residents sleep, so nobody sleeps in a
/// public location. `HOME` still resolves per-resident (a resident's own home),
/// never by affordance scan, so the extra `HOME` locations are harmless to
/// affordance resolution.
pub fn locations() -> Vec<Location> {
    vec![
        Location {
            id: "loc_stadium",
            name: "Stadium",
            affordances: &["WORK_GROUNDSKEEP", "MATCH_GATE", "GATHER"],
            hours: None,
        },
        Location {
            id: "loc_main_square",
            name: "Main Square",
            affordances: &["MARKET", "KIOSK", "SIT_BENCH", "BUSK", "GATHER"],
            hours: None,
        },
        Location {
            id: "loc_bakery",
            name: "Bakery",
            affordances: &["WORK_BAKERY_COUNTER", "BUY_BREAD"],
            hours: Some(OpenHours { open: 5, close: 17 }),
        },
        Location {
            id: "loc_cafe",
            name: "Café",
            affordances: &["WORK", "DRINK_COFFEE", "LEGENDS_CORNER"],
            hours: Some(OpenHours { open: 7, close: 22 }),
        },
        Location {
            id: "loc_riverside",
            name: "Riverside",
            affordances: &["WALK", "SIT_BENCH", "VISIT_OAK"],
            hours: None,
        },
        Location {
            id: "loc_millers_row",
            name: "Miller's Row",
            affordances: &["HOME", "REST"],
            hours: None,
        },
        Location {
            id: "loc_high_street",
            name: "High Street Rooms",
            affordances: &["HOME", "REST"],
            hours: None,
        },
        Location {
            id: "loc_oakside",
            name: "Oakside Cottages",
            affordances: &["HOME", "REST"],
            hours: None,
        },
    ]
}

/// First location that provides the given affordance (deterministic scan).
/// `HOME` is resolved per-resident elsewhere, not here.
pub fn location_for_affordance(affordance: &str) -> Option<LocationId> {
    locations()
        .into_iter()
        .find(|l| l.affordances.contains(&affordance))
        .map(|l| l.id)
}

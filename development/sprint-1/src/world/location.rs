//! The five semantic locations of the first district (DS-001 §1).
//!
//! A Location is a *logical* place with semantic affordances — not a graphical
//! asset. Affordances (not coordinates) are what routines resolve against.

pub type LocationId = &'static str;

#[derive(Debug, Clone)]
pub struct Location {
    pub id: LocationId,
    pub name: &'static str,
    pub affordances: &'static [&'static str],
}

/// The five locations of the First Breath district (stable order).
pub fn locations() -> Vec<Location> {
    vec![
        Location {
            id: "loc_stadium",
            name: "Stadium",
            affordances: &["WORK_GROUNDSKEEP", "MATCH_GATE", "GATHER"],
        },
        Location {
            id: "loc_main_square",
            name: "Main Square",
            affordances: &["MARKET", "KIOSK", "SIT_BENCH", "BUSK", "GATHER", "SQUARE"],
        },
        Location {
            id: "loc_bakery",
            name: "Bakery",
            affordances: &["WORK_BAKERY_COUNTER", "BUY_BREAD", "HOME"],
        },
        Location {
            id: "loc_cafe",
            name: "Café",
            affordances: &["WORK", "DRINK_COFFEE", "LEGENDS_CORNER", "HOME"],
        },
        Location {
            id: "loc_riverside",
            name: "Riverside",
            affordances: &["WALK", "SIT_BENCH", "VISIT_OAK", "HOME"],
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

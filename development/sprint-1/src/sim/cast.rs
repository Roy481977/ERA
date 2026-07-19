//! The ten residents of the First Breath district (DS-001 §2), with routines.
//!
//! Routines are proto-intentions (see `routine.rs`), not fixed schedules. Each
//! activity carries a preferred arrival hour, a flexibility window around it, an
//! optional explicit destination, and a condition gate — so the *when* and
//! *where* can bend without a redesign. Affordances resolve to locations
//! (HOME -> the resident's own home); a `dest` override pins an exact place when
//! an affordance is shared by several locations.

use crate::sim::resident::Resident;
use crate::sim::routine::{Activity, Condition};
use crate::world::location::LocationId;

/// An activity that resolves its place from its affordance.
#[allow(clippy::too_many_arguments)]
fn act(
    id: &'static str,
    purpose: &'static str,
    affordance: &'static str,
    preferred_arrival: u64,
    flexibility: u64,
    priority: u32,
    duration: u32,
) -> Activity {
    Activity {
        id,
        purpose,
        affordance,
        dest: None,
        preferred_arrival,
        flexibility,
        priority,
        duration,
        condition: Condition::Always,
    }
}

/// An activity pinned to an explicit destination (overrides affordance scan).
#[allow(clippy::too_many_arguments)]
fn act_at(
    id: &'static str,
    purpose: &'static str,
    affordance: &'static str,
    dest: LocationId,
    preferred_arrival: u64,
    flexibility: u64,
    priority: u32,
    duration: u32,
) -> Activity {
    Activity {
        id,
        purpose,
        affordance,
        dest: Some(dest),
        preferred_arrival,
        flexibility,
        priority,
        duration,
        condition: Condition::Always,
    }
}

/// The ten residents, in stable order (drives deterministic iteration).
pub fn cast() -> Vec<Resident> {
    vec![
        Resident::new("res_hana", "Hana", 58, "Baker", "loc_bakery", vec![
            act("hana_sleep", "sleeps above the bakery", "HOME", 0, 1, 10, 6),
            act("hana_bake", "bakes the morning bread", "WORK_BAKERY_COUNTER", 7, 2, 9, 3),
            act_at("hana_square", "a midday breath on the square", "GATHER", "loc_main_square", 11, 3, 5, 2),
            act("hana_pm", "the afternoon counter", "WORK_BAKERY_COUNTER", 15, 3, 8, 3),
            act("hana_home", "closes up for the evening", "HOME", 20, 4, 6, 4),
        ]),
        Resident::new("res_sofia", "Sofia", 27, "Baker's assistant", "loc_main_square", vec![
            act("sofia_sleep", "sleeps", "HOME", 0, 1, 10, 6),
            act("sofia_work", "helps open the bakery", "WORK_BAKERY_COUNTER", 7, 2, 9, 3),
            act("sofia_pm", "the afternoon bakery", "WORK_BAKERY_COUNTER", 15, 3, 8, 2),
            act("sofia_cafe", "coffee with a friend", "DRINK_COFFEE", 18, 2, 7, 2),
            act("sofia_home", "home for the night", "HOME", 20, 4, 5, 2),
        ]),
        Resident::new("res_luca", "Luca", 29, "Café owner", "loc_cafe", vec![
            act("luca_sleep", "sleeps above the café", "HOME", 0, 1, 10, 6),
            act("luca_open", "opens the café", "WORK", 7, 2, 9, 3),
            act("luca_mid", "the lunch rush", "WORK", 11, 3, 8, 3),
            act("luca_pm", "the afternoon crowd", "WORK", 15, 3, 8, 3),
            act("luca_home", "closes the café", "HOME", 20, 4, 6, 4),
        ]),
        Resident::new("res_victor", "Victor", 63, "Retired footballer", "loc_cafe", vec![
            act("victor_sleep", "sleeps", "HOME", 0, 1, 10, 6),
            act("victor_walk", "a slow walk past the stadium", "GATHER", 7, 2, 6, 2),
            act("victor_corner", "holds court in his café corner", "LEGENDS_CORNER", 11, 3, 8, 2),
            act("victor_river", "a walk by the river", "WALK", 15, 3, 5, 2),
            act("victor_home", "home for the evening", "HOME", 20, 4, 7, 3),
        ]),
        Resident::new("res_elias", "Elias", 66, "Groundskeeper", "loc_main_square", vec![
            act("elias_sleep", "sleeps", "HOME", 0, 1, 10, 6),
            act("elias_work_am", "mows the pitch", "WORK_GROUNDSKEEP", 7, 2, 9, 3),
            act("elias_coffee", "a quick coffee", "DRINK_COFFEE", 11, 3, 7, 1),
            act("elias_oak", "checks the old oak", "VISIT_OAK", 15, 3, 8, 2),
            act("elias_home", "home for the night", "HOME", 20, 4, 6, 3),
        ]),
        Resident::new("res_eva", "Eva", 41, "Florist", "loc_main_square", vec![
            act("eva_sleep", "sleeps", "HOME", 0, 1, 10, 6),
            act("eva_market", "sets up the flower stall", "MARKET", 7, 2, 9, 3),
            act_at("eva_mid", "the midday market", "GATHER", "loc_main_square", 11, 3, 5, 2),
            act("eva_river", "tends the riverside flowers", "WALK", 15, 3, 7, 2),
            act("eva_home", "home for the evening", "HOME", 20, 4, 6, 3),
        ]),
        Resident::new("res_karim", "Karim", 34, "Kiosk vendor", "loc_main_square", vec![
            act("karim_sleep", "sleeps", "HOME", 0, 1, 10, 6),
            act("karim_am", "opens the kiosk", "KIOSK", 7, 2, 9, 3),
            act("karim_mid", "the midday papers", "KIOSK", 11, 3, 8, 3),
            act("karim_pm", "the afternoon trade", "KIOSK", 15, 3, 7, 3),
            act("karim_home", "shutters the kiosk", "HOME", 20, 4, 6, 3),
        ]),
        Resident::new("res_agnes", "Agnes", 81, "Retired supporter", "loc_main_square", vec![
            act("agnes_sleep", "sleeps", "HOME", 0, 1, 10, 6),
            act("agnes_bench", "her morning bench", "SIT_BENCH", 7, 2, 8, 3),
            act_at("agnes_mid", "watches the square", "GATHER", "loc_main_square", 11, 3, 5, 2),
            act("agnes_oak", "visits the old oak", "VISIT_OAK", 15, 3, 7, 2),
            act("agnes_home", "home before dark", "HOME", 20, 4, 9, 4),
        ]),
        Resident::new("res_milo", "Milo", 22, "Street musician", "loc_main_square", vec![
            act("milo_sleep", "sleeps", "HOME", 0, 1, 10, 6),
            act("milo_coffee", "a slow morning coffee", "DRINK_COFFEE", 7, 2, 6, 2),
            act("milo_busk", "busks by the fountain", "BUSK", 15, 3, 8, 3),
            act("milo_eve", "the evening crowd", "BUSK", 18, 2, 8, 2),
            act("milo_home", "home late", "HOME", 20, 4, 5, 2),
        ]),
        Resident::new("res_tomas", "Tomas", 9, "Schoolchild", "loc_riverside", vec![
            act("tomas_sleep", "sleeps", "HOME", 0, 1, 10, 6),
            act("tomas_roll", "gets a warm roll", "BUY_BREAD", 7, 2, 8, 1),
            act_at("tomas_play", "plays in the square", "GATHER", "loc_main_square", 11, 3, 5, 3),
            act("tomas_oak", "visits the Old Oak", "VISIT_OAK", 15, 3, 7, 2),
            act("tomas_home", "home for the evening", "HOME", 20, 4, 9, 4),
        ]),
    ]
}

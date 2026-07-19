//! The ten residents of the First Breath district (DS-001 §2), with routines.
//!
//! Routines are goal-and-time models (see `routine.rs`), not fixed schedules.
//! Affordances resolve to locations (HOME -> the resident's own home).

use crate::sim::clock::Block::{Afternoon, Evening, Late, Midday, Morning, Night};
use crate::sim::clock::Block;
use crate::sim::resident::Resident;
use crate::sim::routine::Activity;

fn act(
    id: &'static str,
    purpose: &'static str,
    affordance: &'static str,
    window: &'static [Block],
    priority: u32,
    duration: u32,
) -> Activity {
    Activity { id, purpose, affordance, window, priority, duration }
}

/// The ten residents, in stable order (drives deterministic iteration).
pub fn cast() -> Vec<Resident> {
    vec![
        Resident::new("res_hana", "Hana", 58, "Baker", "loc_bakery", vec![
            act("hana_sleep", "sleeps above the bakery", "HOME", &[Night], 10, 6),
            act("hana_bake", "bakes the morning bread", "WORK_BAKERY_COUNTER", &[Morning], 9, 3),
            act("hana_square", "a midday breath on the square", "SQUARE", &[Midday], 5, 2),
            act("hana_pm", "the afternoon counter", "WORK_BAKERY_COUNTER", &[Afternoon], 8, 3),
            act("hana_home", "closes up for the evening", "HOME", &[Evening, Late], 6, 4),
        ]),
        Resident::new("res_sofia", "Sofia", 27, "Baker's assistant", "loc_main_square", vec![
            act("sofia_sleep", "sleeps", "HOME", &[Night], 10, 6),
            act("sofia_work", "helps open the bakery", "WORK_BAKERY_COUNTER", &[Morning], 9, 3),
            act("sofia_pm", "the afternoon bakery", "WORK_BAKERY_COUNTER", &[Afternoon], 8, 2),
            act("sofia_cafe", "coffee with a friend", "DRINK_COFFEE", &[Evening], 7, 2),
            act("sofia_home", "home for the night", "HOME", &[Evening, Late], 5, 2),
        ]),
        Resident::new("res_luca", "Luca", 29, "Café owner", "loc_cafe", vec![
            act("luca_sleep", "sleeps above the café", "HOME", &[Night], 10, 6),
            act("luca_open", "opens the café", "WORK", &[Morning], 9, 3),
            act("luca_mid", "the lunch rush", "WORK", &[Midday], 8, 3),
            act("luca_pm", "the afternoon crowd", "WORK", &[Afternoon], 8, 3),
            act("luca_home", "closes the café", "HOME", &[Evening, Late], 6, 4),
        ]),
        Resident::new("res_victor", "Victor", 63, "Retired footballer", "loc_cafe", vec![
            act("victor_sleep", "sleeps", "HOME", &[Night], 10, 6),
            act("victor_walk", "a slow walk past the stadium", "GATHER", &[Morning], 6, 2),
            act("victor_corner", "holds court in his café corner", "LEGENDS_CORNER", &[Midday], 8, 2),
            act("victor_river", "a walk by the river", "WALK", &[Afternoon], 5, 2),
            act("victor_home", "home for the evening", "HOME", &[Evening, Late], 7, 3),
        ]),
        Resident::new("res_elias", "Elias", 66, "Groundskeeper", "loc_main_square", vec![
            act("elias_sleep", "sleeps", "HOME", &[Night], 10, 6),
            act("elias_work_am", "mows the pitch", "WORK_GROUNDSKEEP", &[Morning], 9, 3),
            act("elias_coffee", "a quick coffee", "DRINK_COFFEE", &[Midday], 7, 1),
            act("elias_oak", "checks the old oak", "VISIT_OAK", &[Afternoon], 8, 2),
            act("elias_home", "home for the night", "HOME", &[Evening, Late], 6, 3),
        ]),
        Resident::new("res_eva", "Eva", 41, "Florist", "loc_main_square", vec![
            act("eva_sleep", "sleeps", "HOME", &[Night], 10, 6),
            act("eva_market", "sets up the flower stall", "MARKET", &[Morning], 9, 3),
            act("eva_mid", "the midday market", "SQUARE", &[Midday], 5, 2),
            act("eva_river", "tends the riverside flowers", "WALK", &[Afternoon], 7, 2),
            act("eva_home", "home for the evening", "HOME", &[Evening, Late], 6, 3),
        ]),
        Resident::new("res_karim", "Karim", 34, "Kiosk vendor", "loc_main_square", vec![
            act("karim_sleep", "sleeps", "HOME", &[Night], 10, 6),
            act("karim_am", "opens the kiosk", "KIOSK", &[Morning], 9, 3),
            act("karim_mid", "the midday papers", "KIOSK", &[Midday], 8, 3),
            act("karim_pm", "the afternoon trade", "KIOSK", &[Afternoon], 7, 3),
            act("karim_home", "shutters the kiosk", "HOME", &[Evening, Late], 6, 3),
        ]),
        Resident::new("res_agnes", "Agnes", 81, "Retired supporter", "loc_main_square", vec![
            act("agnes_sleep", "sleeps", "HOME", &[Night], 10, 6),
            act("agnes_bench", "her morning bench", "SIT_BENCH", &[Morning], 8, 3),
            act("agnes_mid", "watches the square", "SQUARE", &[Midday], 5, 2),
            act("agnes_oak", "visits the old oak", "VISIT_OAK", &[Afternoon], 7, 2),
            act("agnes_home", "home before dark", "HOME", &[Evening, Late], 9, 4),
        ]),
        Resident::new("res_milo", "Milo", 22, "Street musician", "loc_main_square", vec![
            act("milo_sleep", "sleeps", "HOME", &[Night], 10, 6),
            act("milo_coffee", "a slow morning coffee", "DRINK_COFFEE", &[Morning], 6, 2),
            act("milo_busk", "busks by the fountain", "BUSK", &[Afternoon], 8, 3),
            act("milo_eve", "the evening crowd", "BUSK", &[Evening], 8, 2),
            act("milo_home", "home late", "HOME", &[Evening, Late], 5, 2),
        ]),
        Resident::new("res_tomas", "Tomas", 9, "Schoolchild", "loc_riverside", vec![
            act("tomas_sleep", "sleeps", "HOME", &[Night], 10, 6),
            act("tomas_roll", "gets a warm roll", "BUY_BREAD", &[Morning], 8, 1),
            act("tomas_play", "plays in the square", "SQUARE", &[Midday], 5, 3),
            act("tomas_oak", "visits the Old Oak", "VISIT_OAK", &[Afternoon], 7, 2),
            act("tomas_home", "home for the evening", "HOME", &[Evening, Late], 9, 4),
        ]),
    ]
}

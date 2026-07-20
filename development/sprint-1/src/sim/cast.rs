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

/// Working week: Monday–Saturday (0–5). The shops rest on Sunday (6).
const WORKING_DAYS: &[u64] = &[0, 1, 2, 3, 4, 5];
const SUNDAY: &[u64] = &[6];
/// School week: Monday–Friday.
const MON_FRI: &[u64] = &[0, 1, 2, 3, 4];
/// The weekend.
const WEEKEND: &[u64] = &[5, 6];
/// Friday — a night at the pub.
const FRIDAY: &[u64] = &[4];

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
///
/// Wake time is set by each resident's sleep duration (sleep is selected at
/// tick 0 and runs for `duration` ticks), so the district rises in a natural
/// spread rather than all at once: Hana the baker before dawn (04:00), the
/// working residents around 05:00–06:00, young Tomas at 07:00, Milo the musician
/// sleeping off the late crowd until 09:00. Homes on the Main Square are narrated
/// as rooms *beside* the square (no residential node yet — a Sprint-1 reduction).
pub fn cast() -> Vec<Resident> {
    vec![
        Resident::new("res_hana", "Hana", 58, "Baker", "loc_millers_row", vec![
            act("hana_sleep", "sleeps on Miller's Row", "HOME", 0, 1, 10, 3),
            act("hana_bake", "fires the ovens before dawn", "WORK_BAKERY_COUNTER", 5, 2, 9, 3).on_weekdays(WORKING_DAYS),
            act_at("hana_square", "a midday breath on the square", "GATHER", "loc_main_square", 11, 3, 5, 2).on_weekdays(WORKING_DAYS),
            act("hana_pm", "the afternoon counter", "WORK_BAKERY_COUNTER", 15, 3, 8, 3).on_weekdays(WORKING_DAYS),
            act_at("hana_rest", "a slow Sunday walk to the river", "WALK", "loc_riverside", 11, 3, 5, 2).on_weekdays(SUNDAY),
            act("hana_home", "home to Miller's Row", "HOME", 20, 4, 6, 3),
        ]),
        Resident::new("res_sofia", "Sofia", 27, "Baker's assistant", "loc_millers_row", vec![
            act("sofia_sleep", "sleeps on Miller's Row", "HOME", 0, 1, 10, 5),
            act("sofia_work", "helps open the bakery", "WORK_BAKERY_COUNTER", 6, 2, 9, 3),
            act("sofia_pm", "the afternoon bakery", "WORK_BAKERY_COUNTER", 15, 3, 8, 2),
            act("sofia_cafe", "coffee with a friend", "DRINK_COFFEE", 17, 2, 7, 2),
            act("sofia_home", "home to Miller's Row", "HOME", 20, 4, 5, 2),
        ]),
        Resident::new("res_luca", "Luca", 29, "Café owner", "loc_high_street", vec![
            act("luca_sleep", "sleeps in the High Street rooms", "HOME", 0, 1, 10, 6),
            act("luca_open", "opens the café", "WORK", 7, 2, 9, 3),
            act("luca_mid", "the lunch rush", "WORK", 11, 3, 8, 3),
            act("luca_pm", "the afternoon crowd", "WORK", 15, 3, 8, 3),
            act("luca_home", "home above the High Street", "HOME", 20, 4, 6, 3),
        ]),
        Resident::new("res_victor", "Victor", 63, "Retired footballer", "loc_high_street", vec![
            act("victor_sleep", "wakes slowly in the High Street rooms", "HOME", 0, 1, 10, 6),
            act("victor_walk", "a slow walk past the stadium", "GATHER", 8, 2, 6, 2),
            act("victor_corner", "holds court in his café corner", "LEGENDS_CORNER", 12, 3, 8, 2),
            act("victor_pub", "a pint at the Anchor", "DRINK", 18, 1, 6, 1).on_weekdays(FRIDAY),
            act("victor_home", "home for the evening", "HOME", 20, 4, 7, 3),
        ]),
        Resident::new("res_elias", "Elias", 66, "Groundskeeper", "loc_oakside", vec![
            act("elias_sleep", "sleeps at Oakside Cottages", "HOME", 0, 1, 10, 5),
            act("elias_work_am", "mows the pitch at first light", "WORK_GROUNDSKEEP", 6, 2, 9, 3),
            act("elias_oak", "checks the old oak", "VISIT_OAK", 14, 4, 8, 2),
            act("elias_home", "home to Oakside", "HOME", 20, 5, 6, 2),
        ]),
        Resident::new("res_eva", "Eva", 41, "Florist", "loc_millers_row", vec![
            act("eva_sleep", "sleeps on Miller's Row", "HOME", 0, 1, 10, 6),
            act("eva_market", "sets up the flower stall", "MARKET", 7, 2, 9, 3),
            act_at("eva_mid", "the midday market", "GATHER", "loc_main_square", 11, 3, 5, 2),
            act("eva_river", "tends the riverside flowers", "WALK", 15, 3, 7, 2),
            act("eva_home", "home to Miller's Row", "HOME", 20, 4, 6, 3),
        ]),
        Resident::new("res_karim", "Karim", 34, "Kiosk vendor", "loc_high_street", vec![
            act("karim_sleep", "sleeps in the High Street rooms", "HOME", 0, 1, 10, 6),
            act("karim_am", "opens the kiosk", "KIOSK", 7, 2, 9, 3).on_weekdays(WORKING_DAYS),
            act("karim_mid", "the midday papers", "KIOSK", 11, 3, 8, 3).on_weekdays(WORKING_DAYS),
            act("karim_pm", "the afternoon trade", "KIOSK", 15, 3, 7, 3).on_weekdays(WORKING_DAYS),
            act_at("karim_sun", "a quiet Sunday on the square", "GATHER", "loc_main_square", 11, 4, 5, 3).on_weekdays(SUNDAY),
            act("karim_pub", "a pint at the Anchor after work", "DRINK", 18, 1, 6, 1).on_weekdays(FRIDAY),
            act("karim_home", "home above the High Street", "HOME", 20, 4, 6, 3),
        ]),
        Resident::new("res_agnes", "Agnes", 81, "Retired supporter", "loc_oakside", vec![
            act("agnes_sleep", "sleeps at Oakside Cottages", "HOME", 0, 1, 10, 6),
            act("agnes_bench", "her morning bench", "SIT_BENCH", 7, 2, 8, 3),
            act_at("agnes_mid", "watches the square", "GATHER", "loc_main_square", 11, 3, 5, 2),
            act("agnes_oak", "visits the old oak", "VISIT_OAK", 15, 3, 7, 2).on_weekdays(&[0, 1, 3, 6]),
            act("agnes_museum", "revisits the club museum", "VISIT_MUSEUM", 14, 3, 7, 2).on_weekdays(&[2, 4]),
            act("agnes_home", "home before dark", "HOME", 20, 4, 9, 3),
        ]),
        Resident::new("res_milo", "Milo", 22, "Street musician", "loc_high_street", vec![
            act("milo_sleep", "sleeps off the late crowd", "HOME", 0, 1, 10, 9),
            act("milo_coffee", "a slow late-morning coffee", "DRINK_COFFEE", 9, 2, 6, 2),
            act("milo_busk", "busks by the fountain", "BUSK", 16, 3, 8, 3),
            act("milo_eve", "the evening crowd", "BUSK", 19, 2, 8, 2),
            act("milo_home", "home to the High Street", "HOME", 21, 3, 5, 2),
        ]),
        Resident::new("res_tomas", "Tomas", 9, "Schoolchild", "loc_oakside", vec![
            act("tomas_sleep", "sleeps at Oakside Cottages", "HOME", 0, 1, 10, 7),
            act("tomas_school", "goes to school", "SCHOOL", 9, 2, 8, 4).on_weekdays(MON_FRI),
            act("tomas_roll", "runs for a warm roll", "BUY_BREAD", 8, 2, 8, 1).on_weekdays(WEEKEND),
            act_at("tomas_play", "plays in the square", "GATHER", "loc_main_square", 11, 3, 5, 3).on_weekdays(WEEKEND),
            act("tomas_oak", "visits the Old Oak", "VISIT_OAK", 15, 3, 7, 2),
            act("tomas_home", "home to Oakside", "HOME", 20, 4, 9, 4),
        ]),
    ]
}

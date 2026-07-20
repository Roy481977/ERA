//! Wildlife tests: the animals are living entities with their own rhythm — some
//! nocturnal — and their life is seeded (reproducible, yet variable by seed).

use era_first_breath::sim::ambient::AmbientKind;
use era_first_breath::sim::{cast, Simulation};

fn wild_lines(sim: &Simulation) -> Vec<(u64, String)> {
    sim.ambient
        .iter()
        .filter(|a| a.kind == AmbientKind::Wild)
        .map(|a| (a.hour, a.text.clone()))
        .collect()
}

#[test]
fn animals_live_through_the_small_hours() {
    // The night is not empty: nocturnal animals (fox, owl, hedgehog, a cat) are
    // about in the small hours.
    let mut sim = Simulation::new(cast());
    sim.run(3);
    let at_night = wild_lines(&sim).iter().any(|(h, _)| *h <= 4 || *h >= 22);
    assert!(at_night, "no animal stirred in the small hours");
}

#[test]
fn the_district_has_animals_as_entities() {
    let mut sim = Simulation::new(cast());
    sim.run(1);
    let ids: Vec<_> = sim.wildlife.animals.iter().map(|a| a.id).collect();
    assert!(ids.contains(&"ani_fox"), "no fox");
    assert!(ids.contains(&"ani_owl"), "no owl");
    assert!(ids.contains(&"ani_crows"), "no crows");
    assert_eq!(sim.wildlife.animals.len(), 7);
}

#[test]
fn wildlife_stays_within_each_animal_range() {
    // An animal never appears somewhere outside its home range.
    let mut sim = Simulation::new(cast());
    for _ in 0..(4 * 288) {
        for a in &sim.wildlife.animals {
            let ok = a_range(a.id).contains(&a.place);
            assert!(ok, "{} strayed to {}", a.name, a.place);
        }
        sim.step();
    }
}

fn a_range(id: &str) -> Vec<&'static str> {
    match id {
        "ani_fox" => vec!["loc_riverside", "loc_bridge", "loc_oakside", "loc_main_square", "loc_high_street"],
        "ani_tabby" => vec!["loc_bakery", "loc_millers_row", "loc_main_square", "loc_high_street"],
        "ani_blackcat" => vec!["loc_cafe", "loc_main_square", "loc_high_street", "loc_pub"],
        "ani_owl" => vec!["loc_museum", "loc_cafe", "loc_main_square", "loc_oakside"],
        "ani_heron" => vec!["loc_riverside", "loc_bridge"],
        "ani_crows" => vec!["loc_museum", "loc_cafe", "loc_main_square"],
        "ani_hedgehog" => vec!["loc_oakside", "loc_riverside", "loc_bridge"],
        _ => vec![],
    }
}

#[test]
fn the_same_seed_replays_the_same_life() {
    let mut a = Simulation::with_seed(cast(), 42);
    let mut b = Simulation::with_seed(cast(), 42);
    a.run(3);
    b.run(3);
    assert_eq!(wild_lines(&a), wild_lines(&b), "same seed diverged");
}

#[test]
fn a_different_seed_grows_a_different_life() {
    let mut a = Simulation::with_seed(cast(), 1);
    let mut b = Simulation::with_seed(cast(), 999);
    a.run(3);
    b.run(3);
    assert_ne!(wild_lines(&a), wild_lines(&b), "different seeds gave identical wildlife");
}

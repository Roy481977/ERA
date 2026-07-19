//! Phase 2 tests: residents complete believable routines through the world.

use era_first_breath::sim::{cast, Simulation};
use era_first_breath::world::build_world;

#[test]
fn day_is_deterministic() {
    let mut a = Simulation::new(cast());
    a.run(2);
    let mut b = Simulation::new(cast());
    b.run(2);
    assert_eq!(a.log, b.log);
}

#[test]
fn residents_complete_believable_routines() {
    let mut sim = Simulation::new(cast());
    sim.run(1); // one full day; done_today reflects day 0

    let tomas = sim.resident("res_tomas").unwrap();
    assert!(tomas.done_today.contains(&"tomas_roll"), "Tomas never got his roll");
    assert!(tomas.done_today.contains(&"tomas_play"), "Tomas never played");
    assert!(tomas.done_today.contains(&"tomas_oak"), "Tomas never visited the oak");

    let elias = sim.resident("res_elias").unwrap();
    assert!(elias.done_today.contains(&"elias_work_am"), "Elias never worked");
    assert!(elias.done_today.contains(&"elias_oak"), "Elias never checked the oak");
}

#[test]
fn everyone_ends_the_day_at_home() {
    let mut sim = Simulation::new(cast());
    sim.run(1);
    for r in &sim.residents {
        assert_eq!(r.place, r.home, "{} did not end the day at home", r.name);
    }
}

#[test]
fn nobody_teleports() {
    // Track Tomas tick-by-tick; every place change must be along a graph edge.
    let world = build_world();
    let mut sim = Simulation::new(cast());
    let mut prev = sim.resident("res_tomas").unwrap().place;
    for _ in 0..(2 * 24) {
        sim.step();
        let now = sim.resident("res_tomas").unwrap().place;
        if now != prev {
            let adjacent: Vec<_> = world.nav.neighbors(prev).into_iter().map(|(n, _)| n).collect();
            assert!(adjacent.contains(&now), "teleport detected: {prev} -> {now}");
            prev = now;
        }
    }
}

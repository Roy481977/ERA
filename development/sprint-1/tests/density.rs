//! Sprint 3 tests: the district is continuously alive (ambient density).

use era_first_breath::sim::ambient::AmbientKind;
use era_first_breath::sim::{cast, Simulation};

#[test]
fn an_hour_is_richly_populated() {
    let mut sim = Simulation::new(cast());
    sim.run(1);
    // Small moments should vastly outnumber major (behavioural) events.
    let behavioural = sim.log.iter().filter(|e| e.day == 0).count();
    let ambient = sim.ambient.len();
    assert!(ambient > behavioural, "ambient life ({ambient}) should outweigh behavioural ({behavioural})");
    assert!(ambient > 100, "a day felt thin: only {ambient} ambient events");
}

#[test]
fn the_town_the_micro_life_and_moments_all_occur() {
    let mut sim = Simulation::new(cast());
    sim.run(2);
    let has = |k: AmbientKind| sim.ambient.iter().any(|a| a.kind == k);
    assert!(has(AmbientKind::Town), "the town never stirred on its own");
    assert!(has(AmbientKind::Micro), "no micro-life moved through the district");
    assert!(has(AmbientKind::Moment), "residents had no small moments");
}

#[test]
fn the_town_keeps_its_own_routines() {
    let mut sim = Simulation::new(cast());
    sim.run(1);
    let train = sim
        .ambient
        .iter()
        .any(|a| a.hour == 7 && a.text.contains("train"));
    assert!(train, "the morning train never passed");
}

#[test]
fn ambient_life_is_deterministic() {
    let mut a = Simulation::new(cast());
    a.run(3);
    let mut b = Simulation::new(cast());
    b.run(3);
    assert_eq!(a.ambient, b.ambient, "the ambient life diverged between identical runs");
}

#[test]
fn ambient_does_not_disturb_the_behavioural_world() {
    // The density layer is texture: it must not change positions, endings, or the
    // deterministic behavioural log. Checked at the end of an ordinary day — day 1
    // (Tuesday), since day 0 (Monday) is the town festival, where residents may still
    // be out past midnight by design.
    let mut sim = Simulation::new(cast());
    sim.run(2);
    for r in &sim.residents {
        assert_eq!(r.place, r.home, "{} not home — ambient layer disturbed movement", r.name);
    }
}

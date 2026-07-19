//! Phase 6 tests: the Old Oak is a persistent, accumulating world object.

use era_first_breath::sim::oak::OakEventKind;
use era_first_breath::sim::{cast, Simulation};

#[test]
fn oak_accumulates_history_across_days() {
    let mut sim = Simulation::new(cast());
    sim.run(3);
    assert!(!sim.oak.history.is_empty(), "the Oak recorded nothing");
    let days: std::collections::BTreeSet<_> = sim.oak.history.iter().map(|e| e.day).collect();
    assert!(days.len() >= 2, "the Oak's history spans only one day");
    assert!(sim.oak.visit_count >= 3, "too few visits recorded");
}

#[test]
fn oak_history_is_deterministic() {
    let mut a = Simulation::new(cast());
    a.run(4);
    let mut b = Simulation::new(cast());
    b.run(4);
    assert_eq!(a.oak.history, b.oak.history);
    assert_eq!(a.oak.visit_count, b.oak.visit_count);
}

#[test]
fn the_child_plays_beneath_the_oak() {
    let mut sim = Simulation::new(cast());
    sim.run(1);
    assert!(
        sim.oak.history.iter().any(|e| e.kind == OakEventKind::ChildrenPlay),
        "Tomas never played beneath the Oak"
    );
}

#[test]
fn residents_meet_beside_the_oak() {
    let mut sim = Simulation::new(cast());
    sim.run(5);
    assert!(
        sim.oak.history.iter().any(|e| e.kind == OakEventKind::Gathering),
        "no gathering was ever recorded at the Oak"
    );
}

#[test]
fn visitors_carry_a_memory_of_the_oak() {
    let mut sim = Simulation::new(cast());
    sim.run(1);
    assert!(
        sim.residents
            .iter()
            .any(|r| r.memories.iter().any(|m| m.note.contains("Old Oak"))),
        "no resident remembered the Oak"
    );
}

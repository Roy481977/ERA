//! Phase 4 tests: residents form a small social life.

use std::collections::BTreeSet;

use era_first_breath::sim::{cast, Simulation};

#[test]
fn co_located_residents_do_not_always_ignore_each_other() {
    let mut sim = Simulation::new(cast());
    sim.run(1);
    assert!(!sim.interactions.is_empty(), "a whole day passed with no interactions");
}

#[test]
fn interactions_are_deterministic() {
    let mut a = Simulation::new(cast());
    a.run(3);
    let mut b = Simulation::new(cast());
    b.run(3);
    assert_eq!(a.interactions, b.interactions, "interactions diverged between runs");
    assert_eq!(
        a.relationships.get("res_hana", "res_sofia"),
        b.relationships.get("res_hana", "res_sofia"),
        "relationship state diverged between runs"
    );
}

#[test]
fn relationships_strengthen_through_interaction() {
    let mut sim = Simulation::new(cast());
    let before = sim.relationships.get("res_hana", "res_sofia");
    sim.run(2);
    let after = sim.relationships.get("res_hana", "res_sofia");
    assert!(
        after.affinity > before.affinity,
        "Hana & Sofia work side by side yet their bond never grew ({} -> {})",
        before.affinity,
        after.affinity
    );
}

#[test]
fn a_pair_interacts_at_most_once_per_day() {
    let mut sim = Simulation::new(cast());
    sim.run(4);
    for day in 0..4 {
        let mut seen: BTreeSet<(&str, &str)> = BTreeSet::new();
        for it in sim.interactions.iter().filter(|i| i.day == day) {
            let pair = if it.a <= it.b { (it.a, it.b) } else { (it.b, it.a) };
            assert!(seen.insert(pair), "pair {pair:?} interacted twice on day {day}");
        }
    }
}

#[test]
fn interactions_leave_memories() {
    let mut sim = Simulation::new(cast());
    sim.run(1);
    let total_memories: usize = sim.residents.iter().map(|r| r.memories.len()).sum();
    assert!(total_memories > 0, "no resident remembered anything from the day");
    // A memory names the other party.
    assert!(
        sim.residents.iter().any(|r| r.memories.iter().any(|m| m.other.is_some())),
        "no memory recorded who it was with"
    );
}

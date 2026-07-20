//! Sprint 2 Step 1 tests: relationships change behaviour (lingering with friends).

use std::collections::BTreeMap;

use era_first_breath::sim::{cast, Simulation};

fn linger_events(sim: &Simulation) -> Vec<(u64, &'static str)> {
    sim.log
        .iter()
        .filter(|e| e.message.contains("lingers a little longer"))
        .map(|e| (e.day, e.resident))
        .collect()
}

#[test]
fn close_friends_linger_when_they_are_together() {
    let mut sim = Simulation::new(cast());
    sim.run(3);
    assert!(!linger_events(&sim).is_empty(), "no one ever lingered with a friend");
}

#[test]
fn lingering_is_bounded_per_resident_per_day() {
    let mut sim = Simulation::new(cast());
    sim.run(5);
    let mut counts: BTreeMap<(u64, &str), u32> = BTreeMap::new();
    for (day, who) in linger_events(&sim) {
        *counts.entry((day, who)).or_default() += 1;
    }
    for ((day, who), n) in counts {
        assert!(n <= 2, "{who} lingered {n} times on day {day} (cap is 2)");
    }
}

#[test]
fn lingering_is_deterministic() {
    let mut a = Simulation::new(cast());
    a.run(5);
    let mut b = Simulation::new(cast());
    b.run(5);
    assert_eq!(linger_events(&a), linger_events(&b));
}

#[test]
fn lingering_never_strands_anyone() {
    let mut sim = Simulation::new(cast());
    for _ in 0..7 {
        for _ in 0..24 {
            sim.step();
        }
        for r in &sim.residents {
            assert_eq!(r.place, r.home, "{} stranded after lingering", r.name);
        }
    }
}

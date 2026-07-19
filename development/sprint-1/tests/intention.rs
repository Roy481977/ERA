//! Phase 5 tests: residents form intentions and sometimes deviate from routine.

use std::collections::BTreeSet;

use era_first_breath::sim::{cast, Simulation};

fn deviation_events(sim: &Simulation) -> Vec<(u64, &'static str)> {
    sim.log
        .iter()
        .filter(|e| e.message.contains("detours to join"))
        .map(|e| (e.day, e.resident))
        .collect()
}

#[test]
fn residents_deviate_from_their_routine() {
    let mut sim = Simulation::new(cast());
    sim.run(5);
    let devs = deviation_events(&sim);
    assert!(!devs.is_empty(), "nobody ever deviated from routine in five days");
    // Several distinct residents deviate across the run.
    let who: BTreeSet<_> = devs.iter().map(|(_, r)| *r).collect();
    assert!(who.len() >= 2, "expected several residents to deviate, got {}", who.len());
}

#[test]
fn deviations_are_deterministic() {
    let mut a = Simulation::new(cast());
    a.run(5);
    let mut b = Simulation::new(cast());
    b.run(5);
    assert_eq!(deviation_events(&a), deviation_events(&b));
}

#[test]
fn a_resident_deviates_at_most_once_per_day() {
    let mut sim = Simulation::new(cast());
    sim.run(5);
    for day in 0..5 {
        let mut seen: BTreeSet<&str> = BTreeSet::new();
        for (_, who) in deviation_events(&sim).into_iter().filter(|(d, _)| *d == day) {
            assert!(seen.insert(who), "{who} deviated twice on day {day}");
        }
    }
}

#[test]
fn deviations_never_strand_a_resident() {
    // Even with detours, everyone still reaches home at the end of every day.
    let mut sim = Simulation::new(cast());
    for _ in 0..5 {
        for _ in 0..24 {
            sim.step();
        }
        for r in &sim.residents {
            assert_eq!(r.place, r.home, "{} stranded away from home", r.name);
        }
    }
    assert!(!deviation_events(&sim).is_empty(), "no deviations occurred to test");
}

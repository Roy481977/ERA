//! Sprint 2 Step 3 tests: social memory & continuity between residents.

use era_first_breath::sim::clock::TICKS_PER_DAY;
use era_first_breath::sim::{cast, Simulation};

#[test]
fn residents_accumulate_shared_history() {
    let mut sim = Simulation::new(cast());
    sim.run(7);
    // Karim and Milo cross paths on the square; they should have a real history.
    let bond = sim.bonds.get("res_karim", "res_milo").expect("no bond formed");
    assert!(bond.meetings >= 3, "too few remembered meetings: {}", bond.meetings);
    assert!(bond.usual_place().is_some(), "no shared place emerged");
}

#[test]
fn familiarity_warms_encounters_over_time() {
    // Early meetings between near-strangers are cool nods; with shared history,
    // encounters warm up. Over weeks, some encounter is explicitly "old friends".
    let mut sim = Simulation::new(cast());
    sim.run(21);
    assert!(
        sim.log.iter().any(|e| e.message.contains("old friends, and it shows")),
        "no encounter ever warmed into old friendship"
    );
}

#[test]
fn residents_return_to_a_shared_place_expecting_a_friend() {
    let mut sim = Simulation::new(cast());
    sim.run(21);
    assert!(
        sim.log.iter().any(|e| e.message.contains("half-expecting to find")),
        "no one ever went looking for a friend at their usual place"
    );
}

#[test]
fn social_memory_is_deterministic() {
    let mut a = Simulation::new(cast());
    a.run(14);
    let mut b = Simulation::new(cast());
    b.run(14);
    assert_eq!(
        a.bonds.get("res_karim", "res_milo"),
        b.bonds.get("res_karim", "res_milo")
    );
    let reunions = |s: &Simulation| -> usize {
        s.log.iter().filter(|e| e.message.contains("half-expecting to find")).count()
    };
    assert_eq!(reunions(&a), reunions(&b));
}

#[test]
fn continuity_never_strands_anyone() {
    // Reunions and detours may run late, but no one drifts indefinitely: over a
    // fortnight everyone is home asleep in the small hours, every day.
    let mut sim = Simulation::new(cast());
    for _ in 0..(14 * TICKS_PER_DAY) {
        sim.step();
        if sim.clock.hour() == 3 && sim.clock.minute() == 0 {
            for r in &sim.residents {
                assert_eq!(r.place, r.home, "{} stranded (day {})", r.name, sim.clock.day());
            }
        }
    }
}

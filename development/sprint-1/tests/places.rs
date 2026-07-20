//! Sprint 3 (places) tests: the new district locations are genuinely lived-in,
//! not decorative. Over a week the School, Museum and Pub are visited and the
//! Old Bridge is crossed — each one shows up as a place a resident actually
//! occupies (arrives at, or passes through).

use std::collections::BTreeSet;

use era_first_breath::sim::clock::TICKS_PER_DAY;
use era_first_breath::sim::{cast, Simulation};

/// Every location any resident occupies across a full week.
fn occupied_places(days: u64) -> BTreeSet<&'static str> {
    let mut sim = Simulation::new(cast());
    let mut seen: BTreeSet<&'static str> = BTreeSet::new();
    for _ in 0..(days * TICKS_PER_DAY) {
        for r in &sim.residents {
            seen.insert(r.place);
        }
        sim.step();
    }
    seen
}

#[test]
fn the_new_places_are_lived_in() {
    let seen = occupied_places(7);
    assert!(seen.contains("loc_school"), "no one ever went to school");
    assert!(seen.contains("loc_museum"), "no one ever visited the museum");
    assert!(seen.contains("loc_pub"), "no one ever went to the Anchor");
}

#[test]
fn the_old_bridge_is_crossed() {
    // The bridge sits on the path between the square and the riverside, so a
    // resident walking to the river actually steps onto it.
    let seen = occupied_places(7);
    assert!(seen.contains("loc_bridge"), "no one ever crossed the old bridge");
}

#[test]
fn school_is_a_weekday_thing() {
    // Tomas goes to school Mon–Fri; the weekend keeps him out of it.
    let mut sim = Simulation::new(cast());
    sim.run(7);
    let schooled_on = |day: u64| {
        sim.log
            .iter()
            .any(|e| e.day == day && e.resident == "Tomas" && e.message.contains("school"))
    };
    assert!(schooled_on(0), "Tomas skipped school on Monday");
    assert!(!schooled_on(5), "Tomas went to school on Saturday");
    assert!(!schooled_on(6), "Tomas went to school on Sunday");
}

//! Social realism (maturity gaps #1 and #3): a resident's disposition — a stable
//! sociability, plus a mood and an energy that move through the day — and the
//! chosen togetherness it enables. Two close friends at a loose end may decide to
//! go somewhere together; two leaving the same way may walk part of the road
//! together and then part. All deterministic.

use era_first_breath::sim::clock::TICKS_PER_DAY;
use era_first_breath::sim::resident::default_sociability;
use era_first_breath::sim::{cast, Simulation};

fn events_with<'a>(sim: &'a Simulation, needle: &str) -> Vec<(u64, &'a str, String)> {
    sim.log
        .iter()
        .filter(|e| e.message.contains(needle))
        .map(|e| (e.day, e.resident, e.message.clone()))
        .collect()
}

// ------------------------------------------------------------- disposition

#[test]
fn sociability_is_seeded_and_stable() {
    // The hand-set cast personalities: a busker is outgoing; a solitary man is not.
    assert_eq!(default_sociability("res_milo"), 3);
    assert_eq!(default_sociability("res_sofia"), 2);
    assert_eq!(default_sociability("res_victor"), -1);
    // Unknown ids still get a stable value in range.
    let v = default_sociability("res_unknown_person");
    assert!((-1..=2).contains(&v));
    assert_eq!(v, default_sociability("res_unknown_person"), "not stable");

    // Sociability is a trait: it never drifts over a run.
    let before: Vec<i32> = cast().iter().map(|r| r.sociability).collect();
    let mut sim = Simulation::new(cast());
    sim.run(4);
    let after: Vec<i32> = sim.residents.iter().map(|r| r.sociability).collect();
    assert_eq!(before, after, "sociability changed during the run");
}

#[test]
fn energy_arcs_through_the_day_and_recovers() {
    let mut sim = Simulation::new(cast());
    let mut min_ever = 1.0f32;
    let mut tired_in_evening = false;
    let mut rested_in_morning = true;
    for _ in 0..(4 * TICKS_PER_DAY) {
        sim.step();
        let h = sim.clock.hour();
        for r in &sim.residents {
            min_ever = min_ever.min(r.energy);
            if (18..=20).contains(&h) && r.energy < 0.85 {
                tired_in_evening = true;
            }
            // By pre-dawn everyone has been resting at home a long while.
            if h == 5 && r.energy < 0.8 {
                rested_in_morning = false;
            }
        }
    }
    assert!(tired_in_evening, "no one ever tired through the day");
    assert!(rested_in_morning, "someone woke unrested");
    assert!(min_ever > 0.1, "energy collapsed to the floor ({min_ever:.3})");
}

#[test]
fn mood_moves_with_encounters() {
    let mut sim = Simulation::new(cast());
    sim.run(4);
    assert!(
        sim.residents.iter().any(|r| r.mood.abs() > 0.02),
        "no one's mood ever moved off neutral"
    );
    for r in &sim.residents {
        assert!((-1.0..=1.0).contains(&r.mood), "{} mood out of range", r.name);
    }
}

#[test]
fn disposition_is_deterministic() {
    let mut a = Simulation::new(cast());
    a.run(5);
    let mut b = Simulation::new(cast());
    b.run(5);
    let dispo = |s: &Simulation| -> Vec<(i32, u32, u32)> {
        s.residents
            .iter()
            .map(|r| (r.sociability, (r.mood * 1000.0) as u32, (r.energy * 1000.0) as u32))
            .collect()
    };
    assert_eq!(dispo(&a), dispo(&b));
}

// ---------------------------------------------------- chosen togetherness

#[test]
fn close_friends_form_shared_outings() {
    let mut sim = Simulation::new(cast());
    sim.run(8);
    let outings = events_with(&sim, "decide to head to the");
    assert!(!outings.is_empty(), "no two friends ever chose an outing together");
    // A shared plan is always followed by a joint departure to that place.
    assert!(
        !events_with(&sim, "a while together").is_empty(),
        "an outing was chosen but never taken"
    );
}

#[test]
fn friends_walk_partway_together_then_part() {
    let mut sim = Simulation::new(cast());
    sim.run(8);
    assert!(
        !events_with(&sim, "walk out together").is_empty(),
        "no two friends ever shared a stretch of road"
    );
}

#[test]
fn togetherness_is_deterministic() {
    let mut a = Simulation::new(cast());
    a.run(8);
    let mut b = Simulation::new(cast());
    b.run(8);
    assert_eq!(events_with(&a, "decide to head to the"), events_with(&b, "decide to head to the"));
    assert_eq!(events_with(&a, "walk out together"), events_with(&b, "walk out together"));
}

#[test]
fn chosen_togetherness_never_strands_anyone() {
    // Outings and shared walks may reshape an evening, but by the small hours
    // everyone must still be home. (Small deviations are welcome; stranding is not.)
    let mut sim = Simulation::new(cast());
    for _ in 0..(8 * TICKS_PER_DAY) {
        sim.step();
        if sim.clock.hour() == 3 && sim.clock.minute() == 0 {
            for r in &sim.residents {
                assert_eq!(r.place, r.home, "{} stranded at 03:00 (day {})", r.name, sim.clock.day());
            }
        }
    }
}

#[test]
fn shared_outings_are_bounded_per_resident_per_day() {
    // A spontaneous outing counts as the day's one deviation, so no resident
    // should be swept into more than one on any day.
    let mut sim = Simulation::new(cast());
    sim.run(8);
    use std::collections::BTreeMap;
    let mut counts: BTreeMap<(u64, &str), u32> = BTreeMap::new();
    for e in sim.log.iter().filter(|e| e.message.contains("a while together — at")) {
        *counts.entry((e.day, e.resident)).or_default() += 1;
    }
    for ((day, who), n) in counts {
        assert!(n <= 1, "{who} joined {n} outings on day {day} (cap 1)");
    }
}

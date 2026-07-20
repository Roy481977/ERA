//! Phase 7 tests: matchday changes the whole district.

use std::collections::BTreeSet;

use era_first_breath::sim::{cast, Simulation};

fn attenders(sim: &Simulation, day: u64) -> BTreeSet<&'static str> {
    sim.log
        .iter()
        .filter(|e| e.day == day && e.message.contains("heads to the match"))
        .map(|e| e.resident)
        .collect()
}

#[test]
fn matchday_is_observably_different_from_a_normal_day() {
    let mut sim = Simulation::new(cast());
    sim.run(6); // through Saturday (day 5)
    let kickoff_sat = sim.log.iter().any(|e| e.day == 5 && e.message.contains("Kick-off"));
    let kickoff_tue = sim.log.iter().any(|e| e.day == 1 && e.message.contains("Kick-off"));
    assert!(kickoff_sat, "no kick-off on Saturday");
    assert!(!kickoff_tue, "there should be no match on Tuesday");
    assert!(attenders(&sim, 5).len() >= 3, "hardly anyone went to the match");
}

#[test]
fn residents_stay_individual_not_a_synchronized_crowd() {
    let mut sim = Simulation::new(cast());
    sim.run(6);
    let went = attenders(&sim, 5);
    assert!(went.len() < 10, "the whole town moved as one crowd");
    // The café owner keeps the café open rather than going to the match.
    assert!(!went.contains("Luca"), "Luca abandoned the café for the match");
}

#[test]
fn matchday_is_deterministic() {
    let mut a = Simulation::new(cast());
    a.run(6);
    let mut b = Simulation::new(cast());
    b.run(6);
    let day5 = |s: &Simulation| -> Vec<String> {
        s.log.iter().filter(|e| e.day == 5).map(|e| format!("{}:{}", e.resident, e.message)).collect()
    };
    assert_eq!(day5(&a), day5(&b));
}

#[test]
fn the_result_leaves_its_mark_on_the_oak() {
    // Four weeks cover a win (week 3) and losses (weeks 1–2).
    let mut sim = Simulation::new(cast());
    sim.run(28);
    assert!(sim.oak.scarves >= 1, "a victory left no scarf on the Oak");
    assert!(sim.oak.bouquets >= 1, "a defeat left no flowers at the Oak");
}

#[test]
fn everyone_still_gets_home_on_matchday() {
    // A win can keep supporters in the square late, but the night still ends the
    // same way for everyone: home asleep in the small hours.
    let mut sim = Simulation::new(cast());
    for _ in 0..(7 * 24) {
        sim.step();
        if sim.clock.hour() == 3 {
            for r in &sim.residents {
                assert_eq!(r.place, r.home, "{} stranded on day {}", r.name, sim.clock.day());
            }
        }
    }
}

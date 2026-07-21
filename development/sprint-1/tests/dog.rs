//! The old dog: a persistent, ambient presence — routines, a bond, and ageing.
//! He is not a resident with a job and grants nothing; these tests hold him to
//! being *alive in the district*, not a mechanic.

use era_first_breath::sim::{cast, Simulation};

fn dog_lines(sim: &Simulation) -> Vec<(u64, u64, &str)> {
    sim.log
        .iter()
        .filter(|e| e.resident == "the old dog")
        .map(|e| (e.day, e.hour, e.message.as_str()))
        .collect()
}

#[test]
fn the_dog_keeps_a_daily_rhythm() {
    let mut sim = Simulation::new(cast());
    sim.run(1);
    let settles = dog_lines(&sim)
        .iter()
        .filter(|(_, _, m)| m.contains("settles") || m.contains("curls") || m.contains("patch") || m.contains("shade"))
        .count();
    assert!(settles >= 2, "the dog barely moved through his day ({settles} settles)");
}

#[test]
fn the_dog_is_not_a_resident() {
    let sim = Simulation::new(cast());
    // He is his own thing — the town's residents, and a dog beside them.
    assert_eq!(sim.residents.len(), 20);
    assert!(sim.residents.iter().all(|r| r.id != "the_old_dog"));
}

#[test]
fn the_child_comes_to_know_the_dog() {
    let mut sim = Simulation::new(cast());
    sim.run(14);
    assert!(sim.dog.bond_with_child > 0, "the dog and the child never met");
    // The bond deepens through repeated meetings, not a single unlock.
    assert!(sim.dog.bond_with_child >= 3, "their bond hardly grew: {}", sim.dog.bond_with_child);
}

#[test]
fn the_dog_ages_and_roams_less() {
    let mut sim = Simulation::new(cast());
    sim.run(42);
    assert_eq!(sim.dog.age_days, 41, "the dog did not age with the days");
    // Once old, he stops making the long walk to the Club.
    let late_stadium = dog_lines(&sim)
        .iter()
        .any(|(day, _, m)| *day >= 30 && m.contains("Club"));
    assert!(!late_stadium, "the old dog was still walking to the Club late in life");
}

#[test]
fn the_dog_is_deterministic() {
    let mut a = Simulation::new(cast());
    a.run(21);
    let mut b = Simulation::new(cast());
    b.run(21);
    assert_eq!(dog_lines(&a), dog_lines(&b));
    assert_eq!(a.dog.bond_with_child, b.dog.bond_with_child);
}

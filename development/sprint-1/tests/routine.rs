//! Phase 2 tests: residents complete believable routines through the world.

use era_first_breath::sim::resident::Resident;
use era_first_breath::sim::routine::{Activity, Condition};
use era_first_breath::sim::{cast, Simulation};
use era_first_breath::world::build_world;

fn coffee_only(home: &'static str) -> Resident {
    // A resident whose sole activity is a café visit, in-window all day.
    Resident::new("res_test", "Tester", 30, "Tester", home, vec![Activity {
        id: "test_coffee",
        purpose: "wants coffee",
        affordance: "DRINK_COFFEE",
        dest: None,
        preferred_arrival: 10,
        flexibility: 12,
        priority: 5,
        duration: 1,
        condition: Condition::Always,
    }])
}

#[test]
fn resident_will_not_select_a_closed_destination() {
    let world = build_world();
    let r = coffee_only("loc_high_street");
    // Café shut at 06:00 -> nothing selectable even though the window allows it.
    assert!(r.select(6, 0, &world).is_none(), "chose the café while it was closed");
    // Café open at 10:00 -> the coffee activity is now selectable.
    assert!(r.select(10, 0, &world).is_some(), "failed to choose the open café");
}

#[test]
fn weekdays_produce_different_routines() {
    // Karim works the kiosk Mon–Sat and rests on Sunday.
    let mut week = Simulation::new(cast());
    week.run(7);
    let monday: Vec<_> = week.log.iter().filter(|e| e.day == 0 && e.resident == "Karim").collect();
    let sunday: Vec<_> = week.log.iter().filter(|e| e.day == 6 && e.resident == "Karim").collect();
    let did_kiosk = |es: &[&era_first_breath::sim::Event]| es.iter().any(|e| e.message.contains("kiosk"));
    let did_sunday = |es: &[&era_first_breath::sim::Event]| es.iter().any(|e| e.message.contains("Sunday"));
    assert!(did_kiosk(&monday), "Karim did not work the kiosk on Monday");
    assert!(!did_kiosk(&sunday), "Karim worked the kiosk on Sunday");
    assert!(did_sunday(&sunday), "Karim had no distinct Sunday");
}

#[test]
fn everyone_is_home_asleep_in_the_small_hours() {
    // Ordinary human variation in the evening is *desirable* — someone may get
    // home late after the match or after lingering with a friend, and that is not
    // a flaw to optimise away. The believable invariant is weaker and truer: no
    // runaway drift and no impossible schedule, i.e. everyone is home asleep in
    // the small hours. Checked at 03:00 each day across a week.
    let mut sim = Simulation::new(cast());
    for _ in 0..(7 * 24) {
        sim.step();
        if sim.clock.hour() == 3 {
            for r in &sim.residents {
                assert_eq!(
                    r.place, r.home,
                    "{} not home at 03:00 on day {}", r.name, sim.clock.day()
                );
            }
        }
    }
}

#[test]
fn day_is_deterministic() {
    let mut a = Simulation::new(cast());
    a.run(2);
    let mut b = Simulation::new(cast());
    b.run(2);
    assert_eq!(a.log, b.log);
}

#[test]
fn residents_complete_believable_routines() {
    let mut sim = Simulation::new(cast());
    sim.run(1); // one full day; done_today reflects day 0

    let tomas = sim.resident("res_tomas").unwrap();
    // Day 0 is a Monday: school, and the Old Oak after. (The warm-roll run is a
    // weekend thing now that school fills his weekday mornings.)
    assert!(tomas.done_today.contains(&"tomas_school"), "Tomas never went to school on a weekday");
    assert!(tomas.done_today.contains(&"tomas_oak"), "Tomas never visited the oak");

    let elias = sim.resident("res_elias").unwrap();
    assert!(elias.done_today.contains(&"elias_work_am"), "Elias never worked");
    assert!(elias.done_today.contains(&"elias_oak"), "Elias never checked the oak");
}

#[test]
fn everyone_ends_the_day_at_home() {
    let mut sim = Simulation::new(cast());
    sim.run(1);
    for r in &sim.residents {
        assert_eq!(r.place, r.home, "{} did not end the day at home", r.name);
    }
}

#[test]
fn nobody_teleports() {
    // Track Tomas tick-by-tick; every place change must be along a graph edge.
    let world = build_world();
    let mut sim = Simulation::new(cast());
    let mut prev = sim.resident("res_tomas").unwrap().place;
    for _ in 0..(2 * 24) {
        sim.step();
        let now = sim.resident("res_tomas").unwrap().place;
        if now != prev {
            let adjacent: Vec<_> = world.nav.neighbors(prev).into_iter().map(|(n, _)| n).collect();
            assert!(adjacent.contains(&now), "teleport detected: {prev} -> {now}");
            prev = now;
        }
    }
}

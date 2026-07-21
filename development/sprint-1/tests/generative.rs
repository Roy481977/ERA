//! The first World-Generator increments: weather, seasonal re-dressing, and
//! possessions. All deterministic; the world evolves without drifting.

use era_first_breath::engine::Engine;
use era_first_breath::sim::clock::TICKS_PER_DAY;
use era_first_breath::sim::possessions::{Item, Possessions};
use era_first_breath::sim::weather::{Sky, Temp, Weather};
use era_first_breath::sim::Season;

// --------------------------------------------------------------- weather

#[test]
fn weather_is_deterministic() {
    for day in [0u64, 5, 33, 72, 140] {
        let s = Season::for_day(day);
        assert_eq!(Weather::for_day(day, s, 42), Weather::for_day(day, s, 42));
    }
    // A whole engine run replays the same weather sequence.
    let seq = |()| {
        let mut e = Engine::new();
        let mut v = Vec::new();
        for _ in 0..30 {
            e.tick_n(TICKS_PER_DAY);
            let s = e.snapshot();
            v.push((s.season, s.weather.sky, s.weather.temp, s.weather.wet));
        }
        v
    };
    assert_eq!(seq(()), seq(()));
}

#[test]
fn weather_varies_within_a_season() {
    // Winter is roughly days 56..84 (weeks 8..12). Sample it.
    let mut skies = std::collections::BTreeSet::new();
    for day in 56..84 {
        assert_eq!(Season::for_day(day), Season::Winter, "expected winter at day {day}");
        skies.insert(Weather::for_day(day, Season::Winter, 0).sky.tag());
    }
    assert!(skies.len() >= 3, "winter weather barely varied: {skies:?}");
}

#[test]
fn wet_or_cold_days_are_less_inviting_than_bright_ones() {
    // The mechanism behind the engine's "a rainy day changes place use" proof.
    let bright = Weather { sky: Sky::Clear, temp: Temp::Mild, windy: false };
    let rainy = Weather { sky: Sky::Rain, temp: Temp::Cold, windy: true };
    assert!(bright.outdoor_appeal() > rainy.outdoor_appeal());
    assert!(rainy.outdoor_appeal() < 0, "a cold wet day should suppress dawdling");
    assert!(bright.outdoor_appeal() >= 0, "a bright mild day should invite it");
}

// --------------------------------------------------------------- possessions

#[test]
fn residents_dress_for_the_cold_the_wet_and_the_day() {
    let p = Possessions::new();
    let snow = Weather { sky: Sky::Snow, temp: Temp::Cold, windy: true };
    let worn = p.worn("res_hana", Season::Winter, snow, false, false);
    assert!(worn.contains(&Item::Coat), "no coat in the snow");
    assert!(worn.contains(&Item::Gloves), "no gloves when cold");
    assert!(worn.contains(&Item::Boots), "no boots in snow");

    let rain = Weather { sky: Sky::Rain, temp: Temp::Cool, windy: false };
    assert!(p.worn("res_milo", Season::Autumn, rain, false, false).contains(&Item::Umbrella));

    // Matchday puts a club scarf on; working puts an apron on.
    let fair = Weather { sky: Sky::Fair, temp: Temp::Mild, windy: false };
    let match_worn = p.worn("res_tomas", Season::Spring, fair, true, true);
    assert!(match_worn.contains(&Item::ClubScarf));
    assert!(match_worn.contains(&Item::Apron));
}

#[test]
fn possessions_accrete_over_time_deterministically_and_bounded() {
    let grow = |()| {
        let mut p = Possessions::new();
        let ids = ["res_hana", "res_milo", "res_agnes", "res_tomas", "res_eva"];
        for week in 0..40 {
            p.accrete(&ids, week, 0);
        }
        ids.iter().map(|id| p.owned(id).to_vec()).collect::<Vec<_>>()
    };
    let a = grow(());
    assert_eq!(a, grow(()), "accretion is not deterministic");
    assert!(a.iter().any(|v| !v.is_empty()), "no one ever gathered a keepsake");
    for v in &a {
        assert!(v.len() <= 4, "owned set exceeded its bound: {}", v.len());
    }
}

// --------------------------------------------------------------- stream

#[test]
fn snapshot_carries_season_weather_and_worn() {
    let mut e = Engine::new();
    e.tick_n(70 * TICKS_PER_DAY); // into winter
    let s = e.snapshot();
    assert!(!s.season.is_empty());
    assert!(!s.weather.sky.is_empty());
    // On a cold winter day at least one resident should be wearing something.
    let anyone_dressed = s.entities.iter().any(|x| !x.worn.is_empty());
    assert!(anyone_dressed, "no resident carried any possession");
    let j = s.to_json();
    assert!(j.contains("\"season\"") && j.contains("\"weather\"") && j.contains("\"worn\""));
}

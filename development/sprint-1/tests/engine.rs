//! Engine tests: the world is a persistent, continuously-ticking thing, and a
//! snapshot is a pure, deterministic window onto its live state.

use era_first_breath::engine::Engine;

#[test]
fn a_fresh_engine_starts_at_the_first_breath() {
    let e = Engine::new();
    assert_eq!(e.tick_count(), 0);
    assert_eq!(e.day(), 0);
    assert_eq!(e.hour(), 0);
    let snap = e.snapshot();
    // Eleven persistent entities: ten residents and the old dog.
    assert_eq!(snap.entities.len(), 11);
    // At the first breath, nothing has happened yet.
    assert!(snap.events.is_empty(), "no events should have fired before the first tick");
}

#[test]
fn ticking_advances_the_world_one_hour() {
    let mut e = Engine::new();
    e.tick();
    assert_eq!(e.tick_count(), 1);
    assert_eq!(e.hour(), 1);
    e.tick_n(24);
    assert_eq!(e.tick_count(), 25);
    assert_eq!(e.day(), 1);
    assert_eq!(e.hour(), 1);
}

#[test]
fn snapshot_is_pure_it_does_not_advance_the_world() {
    let mut e = Engine::new();
    e.tick_n(10);
    let before = e.tick_count();
    let _ = e.snapshot();
    let _ = e.snapshot();
    let _ = e.snapshot();
    assert_eq!(e.tick_count(), before, "taking a snapshot moved the clock");
}

#[test]
fn entities_persist_by_identity_across_ticks() {
    let mut e = Engine::new();
    let ids_at = |e: &Engine| -> Vec<&'static str> {
        e.snapshot().entities.iter().map(|x| x.id).collect()
    };
    let first = ids_at(&e);
    e.tick_n(72); // three days
    let later = ids_at(&e);
    assert_eq!(first, later, "the cast of entities changed identity/order across time");
}

#[test]
fn two_engines_ticked_alike_are_identical() {
    let mut a = Engine::new();
    let mut b = Engine::new();
    a.tick_n(120);
    b.tick_n(120);
    assert_eq!(a.snapshot().to_json(), b.snapshot().to_json(), "the engine is not deterministic");
    assert_eq!(a.world_json(), b.world_json());
}

#[test]
fn the_snapshot_stream_matches_stepping_the_engine() {
    // A snapshot taken live at tick N equals a fresh engine ticked N times — the
    // world is the same whether observed continuously or reconstructed.
    let mut live = Engine::new();
    live.tick_n(50);
    let live_json = live.snapshot().to_json();

    let mut rebuilt = Engine::new();
    for _ in 0..50 {
        rebuilt.tick();
    }
    assert_eq!(live_json, rebuilt.snapshot().to_json());
}

#[test]
fn snapshots_carry_live_positions_and_occupancy() {
    let mut e = Engine::new();
    e.tick_n(12); // to midday — the town is out and about
    let snap = e.snapshot();
    // Every entity has a screen position.
    for ent in &snap.entities {
        assert!(ent.pos.x() > 0.0 && ent.pos.y() > 0.0, "{} has no position", ent.name);
    }
    // Someone is somewhere: occupancy is non-empty by midday.
    let total: u32 = snap.occupancy.values().sum();
    assert!(total > 0, "no one is anywhere at midday");
}

#[test]
fn the_world_json_describes_the_full_stage() {
    let e = Engine::new();
    let world = e.world_json();
    assert!(world.contains("\"locations\""));
    assert!(world.contains("\"edges\""));
    assert!(world.contains("\"entities\""));
    assert!(world.contains("the_old_dog"));
    assert!(world.contains("loc_school") && world.contains("loc_bridge"));
}

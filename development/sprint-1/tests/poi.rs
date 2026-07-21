//! Points of interest — the fine spatial layer. A settled entity drifts to a spot
//! within its place (a bench, the shade under the stadium's east wing) so a place
//! is inhabited at fine grain, not a stack of dots. Deterministic.

use era_first_breath::engine::Engine;
use era_first_breath::sim::clock::TICKS_PER_DAY;
use era_first_breath::view::layout::node_xy;
use era_first_breath::world::poi::{self, PoiKind, Posture};

#[test]
fn catalogue_has_spots_for_the_key_places() {
    for host in ["loc_stadium", "loc_main_square", "loc_cafe", "loc_riverside", "loc_oakside"] {
        assert!(!poi::at(host).is_empty(), "no points of interest at {host}");
    }
    // The stadium's east wing exists and is a resting spot (where the dog naps).
    let wing = poi::POIS.iter().find(|p| p.id == "poi_stadium_wing").expect("east wing");
    assert_eq!(wing.kind, PoiKind::Wing);
    assert_eq!(wing.posture(), Posture::Rest);
}

#[test]
fn assignment_is_deterministic() {
    for id in ["res_milo", "the_old_dog", "res_agnes"] {
        for host in ["loc_stadium", "loc_main_square"] {
            let a = poi::assign(id, host, 3).map(|p| p.id);
            let b = poi::assign(id, host, 3).map(|p| p.id);
            assert_eq!(a, b, "assignment not stable for {id} at {host}");
            assert!(a.is_some(), "{id} got no spot at {host}");
        }
    }
}

#[test]
fn a_spot_lies_off_its_host_node() {
    let p = poi::assign("the_old_dog", "loc_stadium", 0).unwrap();
    let (nx, ny) = node_xy("loc_stadium").unwrap();
    let (px, py) = p.xy();
    assert!((px - nx).hypot(py - ny) > 5.0, "spot sits on top of the node");
}

#[test]
fn settled_figures_are_offset_from_their_node() {
    // Run into the afternoon, when people are out in public, and confirm at least
    // one settled figure has drifted off the exact node centre onto a spot.
    let mut e = Engine::new();
    let mut found_offset = false;
    for _ in 0..(2 * TICKS_PER_DAY) {
        e.tick();
        let s = e.snapshot();
        for ent in &s.entities {
            if ent.traveling {
                continue;
            }
            if let Some((nx, ny)) = node_xy(ent.place) {
                if (ent.x - nx).hypot(ent.y - ny) > 5.0 {
                    found_offset = true;
                }
            }
        }
        if found_offset {
            break;
        }
    }
    assert!(found_offset, "no settled figure ever drifted to a point of interest");
}

#[test]
fn positions_stay_deterministic_with_pois() {
    let snap = |()| {
        let mut e = Engine::new();
        e.tick_n(3 * TICKS_PER_DAY / 1);
        e.snapshot()
            .entities
            .iter()
            .map(|x| (x.id, (x.x * 10.0) as i64, (x.y * 10.0) as i64, x.pose))
            .collect::<Vec<_>>()
    };
    assert_eq!(snap(()), snap(()), "POI placement broke determinism");
}

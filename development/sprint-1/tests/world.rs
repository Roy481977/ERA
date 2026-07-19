//! Phase 1 tests: world representation and navigation graph.

use era_first_breath::world::build_world;
use era_first_breath::world::navigation::NavGraph;

#[test]
fn five_locations() {
    assert_eq!(build_world().locations.len(), 5);
}

#[test]
fn world_is_valid() {
    assert!(build_world().validate().is_empty());
}

#[test]
fn graph_connected() {
    assert!(build_world().nav.is_connected());
}

#[test]
fn no_islands() {
    let world = build_world();
    let loc_ids: std::collections::BTreeSet<_> = world.locations.iter().map(|l| l.id).collect();
    let nodes: std::collections::BTreeSet<_> = world.nav.nodes().into_iter().collect();
    assert_eq!(loc_ids, nodes);
}

#[test]
fn edges_symmetric() {
    let nav = NavGraph::new();
    for node in nav.nodes() {
        for (other, w) in nav.neighbors(node) {
            let back: std::collections::HashMap<_, _> = nav.neighbors(other).into_iter().collect();
            assert_eq!(back.get(node), Some(&w));
        }
    }
}

#[test]
fn travel_time_known() {
    assert_eq!(
        NavGraph::new().travel_time("loc_bakery", "loc_riverside"),
        Some(3)
    );
}

#[test]
fn shortest_path_is_deterministic() {
    let a = NavGraph::new().shortest_path("loc_stadium", "loc_riverside");
    let b = NavGraph::new().shortest_path("loc_stadium", "loc_riverside");
    assert_eq!(a, b);
    let p = a.unwrap();
    assert_eq!(p.first(), Some(&"loc_stadium"));
    assert_eq!(p.last(), Some(&"loc_riverside"));
}

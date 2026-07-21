//! Phase 1 tests: world representation and navigation graph.

use era_first_breath::world::build_world;
use era_first_breath::world::navigation::NavGraph;

#[test]
fn locations_and_residential_nodes() {
    let world = build_world();
    // The district's twelve places plus the wider town's six residential lanes.
    assert_eq!(world.locations.len(), 18);
    // Nine residential nodes now, each offering HOME.
    let homes: Vec<_> = world
        .locations
        .iter()
        .filter(|l| l.affordances.contains(&"HOME"))
        .collect();
    assert_eq!(homes.len(), 9, "expected nine residential locations");
}

#[test]
fn world_is_valid() {
    assert!(build_world().validate().is_empty());
}

#[test]
fn shops_open_and_close() {
    let w = build_world();
    // Bakery 05:00–17:00.
    assert!(!w.is_open("loc_bakery", 4));
    assert!(w.is_open("loc_bakery", 5));
    assert!(w.is_open("loc_bakery", 16));
    assert!(!w.is_open("loc_bakery", 17));
    // Café 07:00–22:00.
    assert!(!w.is_open("loc_cafe", 6));
    assert!(w.is_open("loc_cafe", 7));
    assert!(!w.is_open("loc_cafe", 22));
    // The square never closes; residences never close.
    assert!(w.is_open("loc_main_square", 3));
    assert!(w.is_open("loc_oakside", 3));
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

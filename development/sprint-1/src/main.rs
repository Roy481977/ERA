//! First Breath observer binary.
//!
//!   cargo run          # Phase 1: build + print + validate the district
//!
//! (Phase 2 extends this to run one simulated day; see the `sim` module.)

use std::collections::BTreeSet;

use era_first_breath::world::build_world;

fn main() {
    let world = build_world();

    println!("=== ERA — First Breath · Phase 1: the district ===\n");

    println!("Locations (5):");
    for l in &world.locations {
        println!(
            "  {:<16} {:<12} affordances: {}",
            l.id,
            l.name,
            l.affordances.join(", ")
        );
    }

    println!("\nNavigation graph (undirected; weight = travel ticks):");
    let mut seen: BTreeSet<(&str, &str)> = BTreeSet::new();
    for node in world.nav.nodes() {
        for (other, w) in world.nav.neighbors(node) {
            let key = if node < other { (node, other) } else { (other, node) };
            if seen.insert(key) {
                println!("  {:<16} <-> {:<16} {} tick(s)", key.0, key.1, w);
            }
        }
    }

    println!("\nSample shortest paths:");
    for (a, b) in [("loc_bakery", "loc_riverside"), ("loc_stadium", "loc_cafe")] {
        let path = world.nav.shortest_path(a, b).unwrap();
        let t = world.nav.travel_time(a, b).unwrap();
        println!("  {a} -> {b}: {}  ({t} ticks)", path.join(" -> "));
    }

    let problems = world.validate();
    println!("\nValidation:");
    if problems.is_empty() {
        println!("  OK — 5 locations, graph connected, all affordances present.");
        println!("\nPhase 1 complete: the district can be executed and observed.");
    } else {
        for p in &problems {
            println!("  PROBLEM: {p}");
        }
        std::process::exit(1);
    }
}

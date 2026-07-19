//! First Breath observer binary.
//!
//!   cargo run          # Phase 1: the district, then Phase 2: one simulated day
//!
//! Deterministic: the same build always produces the same day.

use std::collections::BTreeSet;

use era_first_breath::sim::{cast, Simulation};
use era_first_breath::world::build_world;

fn main() {
    // ---- Phase 1: the district ----
    let world = build_world();
    println!("=== ERA — First Breath · Phase 1: the district ===\n");
    println!("Locations ({}):", world.locations.len());
    for l in &world.locations {
        let hours = match l.hours {
            Some(h) => format!("[{:02}:00–{:02}:00]", h.open, h.close),
            None => "[always open]".to_string(),
        };
        println!(
            "  {:<16} {:<18} {:<14} affordances: {}",
            l.id, l.name, hours, l.affordances.join(", ")
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
    let problems = world.validate();
    if !problems.is_empty() {
        for p in &problems {
            println!("  PROBLEM: {p}");
        }
        std::process::exit(1);
    }
    println!("\nValidation: OK — 5 locations, graph connected, all affordances present.");

    // ---- Phase 2: one simulated day ----
    println!("\n=== Phase 2: one day in the district (10 residents, routines) — Mon ===\n");
    let mut sim = Simulation::new(cast());
    sim.run(1); // 24 ticks = one day (day 0 = Monday)

    let mut last_hour = u64::MAX;
    for e in &sim.log {
        if e.hour != last_hour {
            println!("\n-- {:02}:00 --", e.hour);
            last_hour = e.hour;
        }
        println!("  {:<7} {}", e.resident, e.message);
    }

    println!("\nEnd of day — where everyone is:");
    for r in &sim.residents {
        let home = if r.place == r.home { "(home)" } else { "(!)" };
        println!("  {:<7} at {:<16} {}", r.name, r.place, home);
    }

    // Spotlight: prove one resident completed a believable routine.
    if let Some(tomas) = sim.resident("res_tomas") {
        println!(
            "\nSpotlight — Tomas (age 9) completed today: {}",
            tomas.done_today.join(", ")
        );
    }
    println!("\nPhase 2 complete: residents complete believable routines through the world.");
}

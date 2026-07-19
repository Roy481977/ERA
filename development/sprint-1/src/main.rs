//! First Breath — the observer (Phase 8).
//!
//! A structured terminal window onto the living district. Deterministic: the same
//! command always prints the same world.
//!
//!   cargo run                 # a normal day, hour by hour (Monday)
//!   cargo run -- matchday     # a Saturday: how the town reacts to the football
//!   cargo run -- week         # a seven-day summary (interactions, deviations, results)
//!   cargo run -- days 14      # an N-day summary
//!   cargo run -- explain Tomas    # one resident's day, with the reason for every move
//!   cargo run -- district     # just the world (locations, hours, nav graph)

use std::collections::BTreeMap;
use std::env;

use era_first_breath::sim::clock::{TICKS_PER_DAY, WEEKDAY_NAMES};
use era_first_breath::sim::matchday::{self, MatchResult};
use era_first_breath::sim::resident::Status;
use era_first_breath::sim::{cast, Simulation};
use era_first_breath::world::{build_world, World};

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    let mode = args.first().map(|s| s.as_str()).unwrap_or("normal");
    match mode {
        "normal" => normal_day(),
        "matchday" => matchday_view(),
        "week" => summary_view(7),
        "days" => {
            let n = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(7);
            summary_view(n);
        }
        "explain" => explain(args.get(1).cloned().unwrap_or_else(|| "Tomas".to_string())),
        "district" => print_district(&build_world()),
        _ => {
            eprintln!("unknown mode '{mode}'. try: normal | matchday | week | days N | explain NAME | district");
        }
    }
}

// ---------------------------------------------------------------- views

fn normal_day() {
    print_district(&build_world());
    let mut sim = Simulation::new(cast());
    sim.run(1);
    println!("\n=== A day in the district — {} ===", weekday(0));
    print_day_timeline(&sim, 0);
    print_occupancy(12); // midday snapshot
    print_connections(&sim, 0);
    print_oak(&sim);
    print_end_positions(&sim);
    println!("\n(For the football: `cargo run -- matchday`. For a whole week: `cargo run -- week`.)");
}

fn matchday_view() {
    let mut sim = Simulation::new(cast());
    sim.run(6); // through Saturday (day 5)
    let week = 5 / 7;
    println!(
        "=== Matchday — {} (Rain Town {} today) ===",
        weekday(5),
        MatchResult::for_week(week).verb()
    );
    print_day_timeline(&sim, 5);
    print_occupancy_on(&sim, 5, matchday::KICKOFF); // who is where at kick-off
    print_oak(&sim);
    print_end_positions(&sim);
}

fn summary_view(days: u64) {
    let mut sim = Simulation::new(cast());
    sim.run(days);
    println!("=== {days}-day summary ===\n");
    println!("{:<6} {:<5} {:<12} {:<11} {}", "Day", "Wkdy", "Interactions", "Deviations", "Matchday");
    for d in 0..days {
        let interactions = sim.interactions.iter().filter(|i| i.day == d).count();
        let deviations = sim
            .log
            .iter()
            .filter(|e| e.day == d && e.message.contains("detours to join"))
            .count();
        let md = if matchday::is_matchday(d % 7) {
            format!("match: Rain Town {}", MatchResult::for_week(d / 7).verb())
        } else {
            "—".to_string()
        };
        println!("{:<6} {:<5} {:<12} {:<11} {}", d, weekday(d), interactions, deviations, md);
    }
    print_oak(&sim);
    print_strongest_bonds(&sim);
}

fn explain(name: String) {
    let mut sim = Simulation::new(cast());
    sim.run(6);
    let id = sim
        .residents
        .iter()
        .find(|r| r.name.eq_ignore_ascii_case(&name))
        .map(|r| r.id);
    let Some(id) = id else {
        eprintln!("no resident named '{name}'. try one of: {}", cast().iter().map(|r| r.name).collect::<Vec<_>>().join(", "));
        return;
    };
    let who = sim.resident(id).unwrap();
    println!("=== {} ({}, {}) — six days, and why ===", who.name, who.age, who.occupation);
    for d in 0..6 {
        println!("\n-- {} (day {d}) --", weekday(d));
        for e in sim.log.iter().filter(|e| e.day == d && e.resident == who.name) {
            println!("  {:02}:00  {}", e.hour, e.message);
        }
    }
    println!("\n{} remembers, in all:", who.name);
    for m in &who.memories {
        println!("  · day {} {:02}:00 — {}", m.day, m.hour, m.note);
    }
}

// ---------------------------------------------------------------- sections

fn print_district(world: &World) {
    println!("=== The First Breath district ===\n");
    println!("Locations ({}):", world.locations.len());
    for l in &world.locations {
        let hours = match l.hours {
            Some(h) => format!("[{:02}:00–{:02}:00]", h.open, h.close),
            None => "[always open]".to_string(),
        };
        let kind = if l.is_residential() { "home" } else { "civic" };
        println!(
            "  {:<16} {:<18} {:<6} {:<14} {}",
            l.id, l.name, kind, hours, l.affordances.join(", ")
        );
    }
    println!("\nNavigation graph (undirected; weight = travel ticks):");
    let mut seen = std::collections::BTreeSet::new();
    for node in world.nav.nodes() {
        for (other, w) in world.nav.neighbors(node) {
            let key = if node < other { (node, other) } else { (other, node) };
            if seen.insert(key) {
                println!("  {:<16} <-> {:<16} {}", key.0, key.1, w);
            }
        }
    }
    let problems = world.validate();
    if problems.is_empty() {
        println!("\nValidation: OK.");
    } else {
        for p in &problems {
            println!("  PROBLEM: {p}");
        }
    }
}

fn print_day_timeline(sim: &Simulation, day: u64) {
    let mut last_hour = u64::MAX;
    for e in sim.log.iter().filter(|e| e.day == day) {
        if e.hour != last_hour {
            println!("\n-- {:02}:00 --", e.hour);
            last_hour = e.hour;
        }
        println!("  {:<8} {}", e.resident, e.message);
    }
}

/// Occupancy snapshot: rebuild deterministically and read positions at an hour.
fn print_occupancy(hour: u64) {
    let mut sim = Simulation::new(cast());
    // Step to `hour` on day 0.
    for _ in 0..hour {
        sim.step();
    }
    println!("\n-- who is where at {:02}:00 --", hour);
    render_occupancy(&sim);
}

fn print_occupancy_on(_sim: &Simulation, day: u64, hour: u64) {
    let mut sim = Simulation::new(cast());
    for _ in 0..(day * TICKS_PER_DAY + hour) {
        sim.step();
    }
    println!("\n-- who is where at {:02}:00, {} --", hour, weekday(day));
    render_occupancy(&sim);
}

fn render_occupancy(sim: &Simulation) {
    let mut by_place: BTreeMap<&str, Vec<String>> = BTreeMap::new();
    for r in &sim.residents {
        let what = match &r.status {
            Status::Idle => r.name.to_string(),
            Status::Performing { .. } => r.name.to_string(),
            Status::Traveling { dest, .. } => format!("{}→{}", r.name, dest),
        };
        by_place.entry(r.place).or_default().push(what);
    }
    for (place, who) in by_place {
        let name = sim.world.location(place).map(|l| l.name).unwrap_or(place);
        println!("  {:<18} {}", name, who.join(", "));
    }
}

fn print_connections(sim: &Simulation, day: u64) {
    let today: Vec<_> = sim.interactions.iter().filter(|i| i.day == day).collect();
    println!("\n-- connections today ({}) --", today.len());
    for it in today {
        let a = sim.resident(it.a).map(|r| r.name).unwrap_or(it.a);
        let b = sim.resident(it.b).map(|r| r.name).unwrap_or(it.b);
        let rel = sim.relationships.get(it.a, it.b);
        println!(
            "  {:02}:00 {:<7} & {:<7} {:<28} (affinity {}, trust {})",
            it.hour, a, b, it.kind.verb(), rel.affinity, rel.trust
        );
    }
}

fn print_oak(sim: &Simulation) {
    let day = sim.clock.day().saturating_sub(1);
    let season = sim.oak.season(day);
    println!(
        "\n-- The Old Oak ({} yrs, {} this {}) --",
        sim.oak.age_years,
        season.appearance(),
        season.name()
    );
    println!(
        "  {} visits · {} scarves · {} bouquets",
        sim.oak.visit_count, sim.oak.scarves, sim.oak.bouquets
    );
    let history = sim
        .oak
        .readable_history(|id| sim.resident(id).map(|r| r.name.to_string()).unwrap_or_else(|| id.to_string()));
    for line in history.iter().rev().take(8).rev() {
        println!("    · {line}");
    }
}

fn print_strongest_bonds(sim: &Simulation) {
    // Show the warmest relationships that have formed.
    let mut pairs: Vec<(&str, &str, i32, i32)> = Vec::new();
    for i in 0..sim.residents.len() {
        for j in (i + 1)..sim.residents.len() {
            let (a, b) = (sim.residents[i].id, sim.residents[j].id);
            let rel = sim.relationships.get(a, b);
            if rel.affinity > 0 {
                pairs.push((sim.residents[i].name, sim.residents[j].name, rel.affinity, rel.trust));
            }
        }
    }
    pairs.sort_by(|a, b| b.2.cmp(&a.2).then(b.3.cmp(&a.3)));
    println!("\n-- strongest bonds --");
    for (a, b, aff, trust) in pairs.into_iter().take(6) {
        println!("  {:<8} & {:<8} affinity {}, trust {}", a, b, aff, trust);
    }
}

fn print_end_positions(sim: &Simulation) {
    println!("\n-- end of day --");
    for r in &sim.residents {
        let tag = if r.place == r.home { "(home)" } else { "(!)" };
        let name = sim.world.location(r.place).map(|l| l.name).unwrap_or(r.place);
        println!("  {:<8} {:<18} {}", r.name, name, tag);
    }
}

fn weekday(day: u64) -> &'static str {
    WEEKDAY_NAMES[(day % 7) as usize]
}

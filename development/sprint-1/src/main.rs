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
//!   cargo run -- chronicle    # a month watched from afar: habits, bonds, traditions
//!   cargo run -- dog          # the old dog: his day, his places, the child who knows him
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
        "chronicle" => chronicle(args.get(1).and_then(|s| s.parse().ok()).unwrap_or(4)),
        "dog" => dog_view(),
        "district" => print_district(&build_world()),
        _ => {
            eprintln!("unknown mode '{mode}'. try: normal | matchday | week | days N | explain NAME | chronicle | district");
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

/// Watch the town from afar for a few weeks and let its habits, bonds, and
/// traditions surface — as behaviour, not numbers (DEV-000: People, Relationships).
fn chronicle(weeks: u64) {
    let days = weeks * 7;
    let mut sim = Simulation::new(cast());
    sim.run(days);
    println!("=== The town, watched for {weeks} weeks ===\n");

    // -- Habits: each resident's most-repeated daytime pursuit --
    // (resident, purpose) -> (count, hour-sum), read from arrival lines.
    let mut habit: BTreeMap<(&str, String), (u32, u64)> = BTreeMap::new();
    for e in &sim.log {
        if e.resident == "Matchday" {
            continue;
        }
        let Some((purpose, place)) = e.message.split_once(" — at ") else { continue };
        // Skip anything that happens at home (sleeping, waking, ending the day):
        // a habit worth knowing someone for happens out in the town.
        if matches!(place, "loc_millers_row" | "loc_high_street" | "loc_oakside") {
            continue;
        }
        let p = purpose.to_string();
        let ent = habit.entry((e.resident, p)).or_default();
        ent.0 += 1;
        ent.1 += e.hour;
    }
    println!("What each of them is known for:");
    for r in &sim.residents {
        let best = habit
            .iter()
            .filter(|((who, _), _)| *who == r.name)
            .max_by_key(|(_, (count, _))| *count);
        if let Some(((_, purpose), (count, hoursum))) = best {
            let tod = time_of_day(hoursum / *count as u64);
            println!("  · {:<7} {} — most {}s ({}×)", r.name, purpose, tod, count);
        }
    }

    // -- Bonds: who keeps ending up together, and where --
    let mut pair_place: BTreeMap<(&str, &str), BTreeMap<&str, u32>> = BTreeMap::new();
    for it in &sim.interactions {
        let (a, b) = if it.a <= it.b { (it.a, it.b) } else { (it.b, it.a) };
        *pair_place.entry((a, b)).or_default().entry(it.place).or_default() += 1;
    }
    let mut bonds: Vec<(&str, &str, u32, &str)> = pair_place
        .iter()
        .map(|((a, b), places)| {
            let total: u32 = places.values().sum();
            let (place, _) = places.iter().max_by_key(|(_, n)| **n).unwrap();
            (*a, *b, total, *place)
        })
        .collect();
    bonds.sort_by(|x, y| y.2.cmp(&x.2));
    println!("\nWho keeps finding each other:");
    for (a, b, n, place) in bonds.into_iter().take(6) {
        let an = name(&sim, a);
        let bn = name(&sim, b);
        let pn = sim.world.location(place).map(|l| l.name).unwrap_or(place);
        println!("  · {an} and {bn} keep meeting at the {pn} ({n}×)");
    }

    // -- Companions: who moves through the town together --
    let mut companions: BTreeMap<(&str, &str), u32> = BTreeMap::new();
    for e in &sim.log {
        if let Some(rest) = e.message.strip_prefix("sets off with ") {
            if let Some((partner, _)) = rest.split_once(" for ") {
                let (x, y) = if e.resident <= partner { (e.resident, partner) } else { (partner, e.resident) };
                *companions.entry((x, y)).or_default() += 1;
            }
        }
    }
    if !companions.is_empty() {
        let mut cs: Vec<_> = companions.into_iter().collect();
        cs.sort_by(|a, b| b.1.cmp(&a.1));
        println!("\nWho walks together:");
        for ((a, b), n) in cs.into_iter().take(4) {
            println!("  · {a} and {b} set off together {n}×");
        }
    }

    // -- Places and their identity --
    let mut place_meetings: BTreeMap<&str, u32> = BTreeMap::new();
    for it in &sim.interactions {
        *place_meetings.entry(it.place).or_default() += 1;
    }
    println!("\nWhere the town gathers:");
    let mut pm: Vec<_> = place_meetings.into_iter().collect();
    pm.sort_by(|a, b| b.1.cmp(&a.1));
    for (place, n) in pm.into_iter().take(4) {
        let pn = sim.world.location(place).map(|l| l.name).unwrap_or(place);
        println!("  · the {pn} saw {n} meetings");
    }
    println!(
        "  · the Old Oak drew {} visits, {} scarves, {} bouquets",
        sim.oak.visit_count, sim.oak.scarves, sim.oak.bouquets
    );

    // -- Continuity: shared history changing behaviour --
    let warm = sim.log.iter().filter(|e| e.message.contains("old friends, and it shows")).count();
    let reunions: Vec<&str> = sim
        .log
        .iter()
        .filter(|e| e.message.contains("half-expecting to find"))
        .map(|e| e.resident)
        .collect();
    println!("\nSigns of continuity:");
    println!("  · {warm} encounters warmed into old friendship");
    println!("  · {} times someone went to a shared place hoping to meet a friend", reunions.len());
    // Name the strongest "their place" bonds from remembered history.
    let mut theirs: Vec<(&str, &str, u32, &str)> = Vec::new();
    for i in 0..sim.residents.len() {
        for j in (i + 1)..sim.residents.len() {
            let (a, b) = (sim.residents[i].id, sim.residents[j].id);
            if let Some(bond) = sim.bonds.get(a, b) {
                if let Some(place) = bond.usual_place() {
                    if bond.meetings >= 6 {
                        theirs.push((sim.residents[i].name, sim.residents[j].name, bond.meetings, place));
                    }
                }
            }
        }
    }
    theirs.sort_by(|x, y| y.2.cmp(&x.2));
    for (a, b, n, place) in theirs.into_iter().take(3) {
        let pn = sim.world.location(place).map(|l| l.name).unwrap_or(place);
        println!("  · the {pn} has become {a} and {b}'s place ({n} meetings)");
    }

    // -- Traditions: the matchday rhythm --
    let results: Vec<_> = (0..weeks).map(|w| MatchResult::for_week(w).verb()).collect();
    println!("\nThe weekly rhythm:");
    println!("  · every Saturday the town goes to the football ({} so far)", results.join(", "));
    println!("  · a scarf on the Oak after a win, flowers after a loss");

    // -- The old dog: ambient life the town keeps --
    println!("\nAnd through it all:");
    println!(
        "  · the old dog keeps his rounds (now {} days on, slower than he was); Tomas has come to know him ({} meetings)",
        sim.dog.age_days, sim.dog.bond_with_child
    );
}

fn time_of_day(hour: u64) -> &'static str {
    match hour {
        0..=10 => "morning",
        11..=16 => "afternoon",
        _ => "evening",
    }
}

fn name<'a>(sim: &'a Simulation, id: &'a str) -> &'a str {
    sim.resident(id).map(|r| r.name).unwrap_or(id)
}

/// The old dog: his day, where he tends to be, and the child who has come to know
/// him. He grants nothing — this is simply a window onto ambient life.
fn dog_view() {
    let mut sim = Simulation::new(cast());
    sim.run(42);
    println!("=== The old dog ===\n");
    println!("He belongs to no one and to the whole district.");
    println!(
        "He is {} days into the world's watching, and was already old when we met him.",
        sim.dog.age_days
    );
    if sim.dog.bond_with_child > 0 {
        println!(
            "Tomas has come to know him — {} quiet meetings so far.",
            sim.dog.bond_with_child
        );
    }

    // Where he is most often found (from where he settles).
    let mut spots: BTreeMap<&str, u32> = BTreeMap::new();
    for e in sim.log.iter().filter(|e| e.resident == "the old dog") {
        let spot = if e.message.contains("Oak") {
            Some("beneath the Old Oak")
        } else if e.message.contains("café") {
            Some("by the café door")
        } else if e.message.contains("square") {
            Some("in the sun on the square")
        } else if e.message.contains("Club") {
            Some("outside the Club")
        } else {
            None
        };
        if let Some(s) = spot {
            *spots.entry(s).or_default() += 1;
        }
    }
    println!("\nWhere he is usually found:");
    let mut v: Vec<_> = spots.into_iter().collect();
    v.sort_by(|a, b| b.1.cmp(&a.1));
    for (spot, n) in v {
        println!("  · {spot} ({n} days)");
    }

    // A recent day with him.
    let day = 40;
    println!("\nA day with him ({}):", weekday(day));
    for e in sim.log.iter().filter(|e| e.day == day && e.resident == "the old dog") {
        println!("  {:02}:00  {}", e.hour, e.message);
    }
    println!("\n(He is not a quest, a helper or a mechanic. He is simply here.)");
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
    let dog_place = sim.world.location(sim.dog.place).map(|l| l.name).unwrap_or(sim.dog.place);
    println!("  {:<18} (the old dog)", dog_place);
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

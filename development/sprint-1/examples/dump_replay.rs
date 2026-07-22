//! Dump a replay for the plate compositor: the static world once, then a stream
//! of per-tick snapshots. Plays back as the living layer over plate-v1.
//!
//! Usage: cargo run --example dump_replay [ticks] [seed] > replay.json
//! Default: 288 ticks (one in-game day), seed 0.
use era_first_breath::engine::Engine;

fn main() {
    let mut args = std::env::args().skip(1);
    let ticks: u64 = args.next().and_then(|s| s.parse().ok()).unwrap_or(288);
    let seed: u64 = args.next().and_then(|s| s.parse().ok()).unwrap_or(0);

    let mut engine = Engine::with_seed(seed);
    let mut out = String::new();
    out.push_str("{\"world\":");
    out.push_str(&engine.world_json());
    out.push_str(",\"frames\":[");
    for i in 0..ticks {
        engine.tick();
        if i > 0 {
            out.push(',');
        }
        out.push_str(&engine.snapshot().to_json());
    }
    out.push_str("]}");
    println!("{out}");
}

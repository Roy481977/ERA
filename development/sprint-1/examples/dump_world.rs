//! Dump the static world JSON (locations, edges, entities, pois) for renderers
//! that don't need the ticking sim — e.g. the plate blockout render.
fn main() {
    let engine = era_first_breath::engine::Engine::with_seed(0);
    println!("{}", engine.world_json());
}

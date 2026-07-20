//! WebAssembly bindings — the engine, in the browser.
//!
//! Compiled only under the `wasm` feature (native builds and tests never see
//! this). It exposes the same `Engine` the native world runs, so **each visitor
//! runs their own copy of ERA** in their own browser tab: the deterministic Rust
//! simulation ticks client-side, and the web renderer reads its live state each
//! frame. The exact same artifact runs on localhost today and on any static web
//! host tomorrow.
//!
//! The wire format is identical to the native engine's: `world_json()` for the
//! static stage (once), `snapshot_json()` for the live frame (every tick). The
//! browser renderer is unchanged whether it reads a recording or this live engine.

use wasm_bindgen::prelude::*;

use crate::engine::Engine;

/// A live ERA engine running in the browser. Construct it, `tick()` it forward on
/// a timer, and read `snapshot_json()` each frame.
#[wasm_bindgen]
pub struct WasmEngine {
    inner: Engine,
}

#[wasm_bindgen]
impl WasmEngine {
    /// A fresh district. `seed` varies the wildlife's life (the residents are
    /// deterministic regardless); pass 0 for the default world.
    #[wasm_bindgen(constructor)]
    pub fn new(seed: u32) -> WasmEngine {
        let seed = if seed == 0 {
            crate::sim::simulation::DEFAULT_WORLD_SEED
        } else {
            seed as u64
        };
        WasmEngine { inner: Engine::with_seed(seed) }
    }

    /// Advance the world one tick (five minutes).
    pub fn tick(&mut self) {
        self.inner.tick();
    }

    /// The static stage: locations, edges, entity roster. Send once.
    pub fn world_json(&self) -> String {
        self.inner.world_json()
    }

    /// The live frame: positions and behaviour for every entity, plus occupancy,
    /// callouts, the Oak, events and bonds. Read every tick.
    pub fn snapshot_json(&self) -> String {
        self.inner.snapshot().to_json()
    }

    /// Ticks elapsed since the first breath.
    pub fn tick_count(&self) -> u32 {
        self.inner.tick_count() as u32
    }
}

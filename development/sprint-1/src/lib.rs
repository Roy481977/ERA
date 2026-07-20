//! ERA — First Breath (Sprint 1). Headless, deterministic simulation core.
//!
//! Works from `architecture/system-contracts/world-state-schema.md`:
//! semantic places (affordances, not coordinates), one authoritative world,
//! deterministic behaviour. Language rationale: `creative-decisions/CD-007`.

pub mod behaviour;
pub mod engine;
pub mod sim;
pub mod view;
pub mod world;

/// WebAssembly bindings — only under the `wasm` feature (see `web/`).
#[cfg(feature = "wasm")]
pub mod web;

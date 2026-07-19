//! Simulation (Phase 2): the clock, residents, routines, and the sim loop.

pub mod cast;
pub mod clock;
pub mod resident;
pub mod routine;
pub mod simulation;
pub mod social;

pub use cast::cast;
pub use simulation::{Event, Simulation};
pub use social::{InteractionKind, Rel, Relationships};

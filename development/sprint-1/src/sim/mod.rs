//! Simulation (Phase 2): the clock, residents, routines, and the sim loop.

pub mod ambient;
pub mod cast;
pub mod clock;
pub mod dog;
pub mod intention;
pub mod matchday;
pub mod oak;
pub mod resident;
pub mod routine;
pub mod simulation;
pub mod social;

pub use ambient::{Ambient, AmbientKind};
pub use cast::cast;
pub use dog::Dog;
pub use oak::{OakEventKind, OldOak, Season};
pub use simulation::{Event, Simulation};
pub use social::{Bonds, InteractionKind, Rel, Relationships, SharedBond};

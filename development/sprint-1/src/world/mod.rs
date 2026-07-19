//! World representation (Phase 1): the authoritative container for the district.

pub mod location;
pub mod navigation;

use std::collections::BTreeSet;

use location::{locations, Location};
use navigation::NavGraph;

/// The authoritative world: the five locations + the navigation graph.
pub struct World {
    pub locations: Vec<Location>,
    pub nav: NavGraph,
}

impl World {
    /// Look up a location by id.
    pub fn location(&self, id: &str) -> Option<&Location> {
        self.locations.iter().find(|l| l.id == id)
    }

    /// Validate the Phase-1 single-world-state invariants.
    /// Empty vec == valid.
    pub fn validate(&self) -> Vec<String> {
        let mut problems = Vec::new();
        let loc_ids: BTreeSet<&str> = self.locations.iter().map(|l| l.id).collect();
        let graph_nodes: BTreeSet<&str> = self.nav.nodes().into_iter().collect();

        for n in graph_nodes.difference(&loc_ids) {
            problems.push(format!("nav graph references unknown location: {n}"));
        }
        for l in loc_ids.difference(&graph_nodes) {
            problems.push(format!("location not present in nav graph (island): {l}"));
        }
        if !self.nav.is_connected() {
            problems.push("navigation graph is not connected".to_string());
        }
        for l in &self.locations {
            if l.affordances.is_empty() {
                problems.push(format!("location has no affordances: {}", l.id));
            }
        }
        problems
    }
}

/// Construct the First Breath world. Deterministic.
pub fn build_world() -> World {
    World {
        locations: locations(),
        nav: NavGraph::new(),
    }
}

//! The navigation graph of the first district (DS-001 §1).
//!
//! Undirected, weighted (edge weight = travel time in WorldClock ticks).
//! Movement happens along edges over travel time — no teleporting.
//! Deterministic: adjacency is stored sorted; Dijkstra breaks ties by id.

use std::cmp::Reverse;
use std::collections::{BTreeMap, BinaryHeap, HashMap};

pub type LocationId = &'static str;

/// (a, b, travel_time_ticks). Undirected. Main Square is the hub.
pub const EDGES: &[(LocationId, LocationId, u32)] = &[
    ("loc_main_square", "loc_bakery", 1),
    ("loc_main_square", "loc_cafe", 1),
    ("loc_main_square", "loc_stadium", 2),
    ("loc_main_square", "loc_riverside", 2),
    ("loc_bakery", "loc_cafe", 1),
    ("loc_cafe", "loc_riverside", 2),
    // Residential lanes connected into the district.
    ("loc_millers_row", "loc_main_square", 1),
    ("loc_millers_row", "loc_bakery", 1),
    ("loc_high_street", "loc_main_square", 1),
    ("loc_high_street", "loc_cafe", 1),
    ("loc_oakside", "loc_riverside", 1),
    ("loc_oakside", "loc_main_square", 2),
];

#[derive(Debug, Clone)]
pub struct NavGraph {
    adj: BTreeMap<LocationId, BTreeMap<LocationId, u32>>,
}

impl NavGraph {
    pub fn new() -> Self {
        Self::from_edges(EDGES)
    }

    pub fn from_edges(edges: &[(LocationId, LocationId, u32)]) -> Self {
        let mut adj: BTreeMap<LocationId, BTreeMap<LocationId, u32>> = BTreeMap::new();
        for &(a, b, w) in edges {
            assert!(w > 0, "edge {a}-{b} must have positive travel time");
            adj.entry(a).or_default().insert(b, w);
            adj.entry(b).or_default().insert(a, w);
        }
        NavGraph { adj }
    }

    pub fn nodes(&self) -> Vec<LocationId> {
        self.adj.keys().copied().collect()
    }

    /// Neighbours as (id, travel_time), sorted for determinism.
    pub fn neighbors(&self, node: LocationId) -> Vec<(LocationId, u32)> {
        self.adj
            .get(node)
            .map(|m| m.iter().map(|(k, v)| (*k, *v)).collect())
            .unwrap_or_default()
    }

    fn dijkstra(
        &self,
        src: LocationId,
    ) -> (HashMap<LocationId, u32>, HashMap<LocationId, LocationId>) {
        let mut dist: HashMap<LocationId, u32> = HashMap::new();
        let mut prev: HashMap<LocationId, LocationId> = HashMap::new();
        let mut pq: BinaryHeap<Reverse<(u32, LocationId)>> = BinaryHeap::new();
        dist.insert(src, 0);
        pq.push(Reverse((0, src)));
        while let Some(Reverse((d, u))) = pq.pop() {
            if d > *dist.get(u).unwrap_or(&u32::MAX) {
                continue;
            }
            for (v, w) in self.neighbors(u) {
                let nd = d + w;
                if nd < *dist.get(v).unwrap_or(&u32::MAX) {
                    dist.insert(v, nd);
                    prev.insert(v, u);
                    pq.push(Reverse((nd, v)));
                }
            }
        }
        (dist, prev)
    }

    /// Shortest travel time between a and b (ticks), if reachable.
    pub fn travel_time(&self, a: LocationId, b: LocationId) -> Option<u32> {
        self.dijkstra(a).0.get(b).copied()
    }

    /// Node path from a to b inclusive (deterministic), if reachable.
    pub fn shortest_path(&self, a: LocationId, b: LocationId) -> Option<Vec<LocationId>> {
        if a == b {
            return Some(vec![a]);
        }
        let (dist, prev) = self.dijkstra(a);
        if !dist.contains_key(b) {
            return None;
        }
        let mut path = vec![b];
        while *path.last().unwrap() != a {
            let p = *prev.get(path.last().unwrap())?;
            path.push(p);
        }
        path.reverse();
        Some(path)
    }

    pub fn is_connected(&self) -> bool {
        let nodes = self.nodes();
        if nodes.is_empty() {
            return true;
        }
        let reachable = self.dijkstra(nodes[0]).0;
        nodes.iter().all(|n| reachable.contains_key(n))
    }
}

impl Default for NavGraph {
    fn default() -> Self {
        Self::new()
    }
}

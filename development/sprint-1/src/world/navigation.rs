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
    ("loc_bakery", "loc_cafe", 1),
    ("loc_cafe", "loc_riverside", 2),
    // The Old Bridge sits on the river path: square <-> bridge <-> riverside keeps
    // the same distance (2) as the old direct edge, but people now cross the bridge.
    ("loc_main_square", "loc_bridge", 1),
    ("loc_bridge", "loc_riverside", 1),
    // Residential lanes connected into the district.
    ("loc_millers_row", "loc_main_square", 1),
    ("loc_millers_row", "loc_bakery", 1),
    ("loc_high_street", "loc_main_square", 1),
    ("loc_high_street", "loc_cafe", 1),
    ("loc_oakside", "loc_riverside", 1),
    ("loc_oakside", "loc_main_square", 2),
    // New places (leaves — they do not shorten any existing route).
    ("loc_school", "loc_main_square", 1),
    ("loc_museum", "loc_cafe", 1),
    ("loc_pub", "loc_main_square", 1),
    ("loc_pub", "loc_high_street", 1),
    // The wider town's lanes, each joined to the nearest district node (leaves —
    // they do not shorten any existing route).
    ("loc_elm_row", "loc_school", 1),
    ("loc_elm_row", "loc_bakery", 1),
    ("loc_kiln_yard", "loc_millers_row", 1),
    ("loc_canal_side", "loc_high_street", 1),
    ("loc_north_gate", "loc_stadium", 1),
    ("loc_orchard_close", "loc_museum", 1),
    ("loc_weavers_lane", "loc_oakside", 1),
    // NEW places (leaves — they do not shorten any existing route).
    ("loc_club_offices", "loc_north_gate", 1),
    ("loc_club_shop", "loc_north_gate", 1),
    ("loc_corner_grocer", "loc_high_street", 1),
    ("loc_training_ground", "loc_stadium", 2),
    ("loc_slate_house", "loc_millers_row", 1),
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

    /// Dijkstra restricted to `allowed` nodes — an edge into a node outside the
    /// set is never taken. Used for animals bound to a home range, so a creature
    /// never routes across ground it would not actually walk (the pitch, a private
    /// close) just because the shortest path happens to run through it.
    fn dijkstra_within(
        &self,
        src: LocationId,
        allowed: &[LocationId],
    ) -> (HashMap<LocationId, u32>, HashMap<LocationId, LocationId>) {
        let ok = |n: LocationId| allowed.contains(&n);
        let mut dist: HashMap<LocationId, u32> = HashMap::new();
        let mut prev: HashMap<LocationId, LocationId> = HashMap::new();
        let mut pq: BinaryHeap<Reverse<(u32, LocationId)>> = BinaryHeap::new();
        if !ok(src) {
            return (dist, prev);
        }
        dist.insert(src, 0);
        pq.push(Reverse((0, src)));
        while let Some(Reverse((d, u))) = pq.pop() {
            if d > *dist.get(u).unwrap_or(&u32::MAX) {
                continue;
            }
            for (v, w) in self.neighbors(u) {
                if !ok(v) {
                    continue;
                }
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

    /// Node path from a to b (inclusive) that stays entirely within `allowed`, if
    /// such a path exists. Both endpoints must be in `allowed`.
    pub fn shortest_path_within(
        &self,
        a: LocationId,
        b: LocationId,
        allowed: &[LocationId],
    ) -> Option<Vec<LocationId>> {
        if a == b {
            return if allowed.contains(&a) { Some(vec![a]) } else { None };
        }
        let (dist, prev) = self.dijkstra_within(a, allowed);
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

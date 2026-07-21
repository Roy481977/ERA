//! District layout: the hand-laid 2D coordinates and per-entity colours that a
//! renderer needs to draw the world. This lives in the engine (not the viewer)
//! so that *the engine owns the spatial truth* and a snapshot can carry ready
//! screen positions — the renderer only draws what the engine reports.
//!
//! Coordinates are in viewer space (~1000 x 760). Placing them here keeps the
//! map authoritative and identical across every consumer (live snapshot, batch
//! trace, tests).

use crate::sim::clock::TRAVEL_TICKS_PER_WEIGHT;
use crate::sim::resident::Status;
use crate::world::location::LocationId;
use crate::world::World;

/// Hand-laid 2D coordinates for each district node — plate WORLD units
/// (1 wu = 0.25 m; plate 1800x1000 wu). Derived from the locked composition
/// bible via design/bible/world-coords.json (blockout step 1). Off-frame
/// places (school, weavers, training ground) sit in the left extension.
pub const MAP: &[(&str, f64, f64)] = &[
    ("loc_stadium", 1726.17, 588.67),
    ("loc_school", 430.0, 240.0),
    ("loc_museum", 1636.52, 407.62),
    ("loc_bakery", 1343.85, 379.49),
    ("loc_main_square", 1515.23, 469.14),
    ("loc_cafe", 1481.84, 449.8),
    ("loc_pub", 1603.12, 499.9),
    ("loc_bridge", 1506.45, 564.06),
    ("loc_riverside", 1374.61, 640.53),
    ("loc_millers_row", 1106.54, 936.72),
    ("loc_high_street", 1339.45, 376.86),
    ("loc_oakside", 1727.93, 945.51),
    ("loc_elm_row", 1198.83, 324.12),
    ("loc_kiln_yard", 1121.48, 720.51),
    ("loc_canal_side", 1650.0, 520.0),
    ("loc_north_gate", 1657.62, 544.73),
    ("loc_orchard_close", 1660.0, 260.0),
    ("loc_weavers_lane", 470.0, 720.0),
    ("loc_slate_house", 1040.63, 810.16),
    ("loc_club_offices", 1666.41, 486.72),
    ("loc_club_shop", 1638.28, 516.6),
    ("loc_corner_grocer", 1418.55, 398.83),
    ("loc_training_ground", 180.0, 300.0),
];

/// A distinct colour per resident, plus the old dog.
pub const COLORS: &[(&str, &str)] = &[
    ("res_hana", "#d1495b"),
    ("res_sofia", "#e07a5f"),
    ("res_luca", "#e6b800"),
    ("res_victor", "#81b29a"),
    ("res_elias", "#3d84a8"),
    ("res_eva", "#c05299"),
    ("res_karim", "#6a4c93"),
    ("res_agnes", "#8d99ae"),
    ("res_milo", "#ef8354"),
    ("res_tomas", "#4f9d69"),
    // The wider town's residents.
    ("res_petra", "#b5654a"),
    ("res_bruno", "#5a8a7a"),
    ("res_dan", "#7a6ab0"),
    ("res_nadia", "#d47ba0"),
    ("res_yusuf", "#4a8ac0"),
    ("res_otto", "#9a8a70"),
    ("res_lena", "#c99a3a"),
    ("res_sam", "#5fa85a"),
    ("res_ines", "#c0609a"),
    ("res_mara", "#e0915a"),
    ("the_old_dog", "#8b5a2b"),
];

/// Screen coordinates of a node, if it is on the map.
pub fn node_xy(id: &str) -> Option<(f64, f64)> {
    MAP.iter().find(|(n, _, _)| *n == id).map(|(_, x, y)| (*x, *y))
}

/// Colour for an entity id (falls back to a neutral grey).
pub fn color_of(id: &str) -> &'static str {
    COLORS.iter().find(|(e, _)| *e == id).map(|(_, c)| *c).unwrap_or("#888888")
}

/// A live position: at a node, or a fraction `t` along an edge. Carries the
/// interpolated screen coordinates so the renderer needs no geometry of its own.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Pos {
    At { node: LocationId, x: f64, y: f64 },
    OnEdge { from: LocationId, to: LocationId, t: f64, x: f64, y: f64 },
}

impl Pos {
    pub fn x(&self) -> f64 {
        match self {
            Pos::At { x, .. } | Pos::OnEdge { x, .. } => *x,
        }
    }
    pub fn y(&self) -> f64 {
        match self {
            Pos::At { y, .. } | Pos::OnEdge { y, .. } => *y,
        }
    }
}

fn edge_weight(world: &World, a: LocationId, b: LocationId) -> u32 {
    world.nav.neighbors(a).into_iter().find(|(n, _)| *n == b).map(|(_, w)| w).unwrap_or(1)
}

/// Where an entity is *right now*, as screen-space geometry, from its live
/// movement state. A traveller is placed fractionally along its current leg.
pub fn entity_pos(world: &World, place: LocationId, status: &Status) -> Pos {
    if let Status::Traveling { path, idx, leg_left, .. } = status {
        let from = path[*idx];
        let to = path.get(idx + 1).copied().unwrap_or(from);
        // Total ticks for this leg = edge weight scaled to the travel pace; the
        // fraction done drives the on-map interpolation.
        let w = (edge_weight(world, from, to) * TRAVEL_TICKS_PER_WEIGHT).max(1);
        let done = w.saturating_sub((*leg_left).min(w));
        let t = done as f64 / w as f64;
        if let (Some((fx, fy)), Some((tx, ty))) = (node_xy(from), node_xy(to)) {
            return Pos::OnEdge {
                from,
                to,
                t,
                x: fx + (tx - fx) * t,
                y: fy + (ty - fy) * t,
            };
        }
    }
    let (x, y) = node_xy(place).unwrap_or((500.0, 380.0));
    Pos::At { node: place, x, y }
}

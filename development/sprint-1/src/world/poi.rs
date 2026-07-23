//! Points of interest — the world's *fine* level of detail.
//!
//! A [`Location`](super::location::Location) is a logical place a routine resolves
//! against (the Stadium, the Square). But a place is not a single point: it has
//! *spots within and around it* — a bench, a fountain, the shade under the
//! stadium's east wing, a verge by the river, a den beneath the Old Oak. These
//! **points of interest** are not navigation nodes (nothing routes to them); they
//! are the sub-locations a settled resident, the dog, or an animal drifts to and
//! *inhabits*, so a place reads as lived-in rather than a stack of figures on one
//! dot. The dog naps under the east wing; a child watches from the fountain rail.
//!
//! POIs are deterministic static data here (the first increment of the spatial
//! layer in the generative-world design); later they are themselves generated and
//! evolve (a new bench, a grown tree). Offsets are in the same viewer space as
//! [`crate::view::layout::MAP`].

use crate::view::layout::node_xy;
use crate::world::location::LocationId;

/// The posture a spot invites — a hint the behaviour layer uses to refine a
/// *settled* entity's pose (it never overrides a meaningful one like working or
/// talking). Kept renderer-agnostic so `world` needn't know about `Pose`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Posture {
    /// Sit a while (a bench, a step).
    Sit,
    /// Settle and rest — a nap spot, a den, deep shade.
    Rest,
    /// Stand and watch — a rail, a verge, an overlook.
    Watch,
    /// A spot that invites play (an open corner, around a tree).
    Play,
    /// No particular posture; just a place to stand.
    None,
}

/// What kind of spot this is (for the renderer to dress it, and for its posture).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PoiKind {
    Bench,
    Wing,     // the shaded lee of a big structure (the stadium's east wing)
    Verge,    // a grassy edge / rail by the water
    Fountain,
    Den,      // a hollow / nook an animal beds down in
    Tree,
    PlaySpot,
    Stall,    // a market pitch
    Nook,     // a quiet corner / doorway
}

impl PoiKind {
    /// The posture this kind of spot invites.
    pub fn posture(&self) -> Posture {
        match self {
            PoiKind::Bench => Posture::Sit,
            PoiKind::Wing | PoiKind::Den => Posture::Rest,
            PoiKind::Verge | PoiKind::Fountain | PoiKind::Nook => Posture::Watch,
            PoiKind::Tree | PoiKind::PlaySpot => Posture::Play,
            PoiKind::Stall => Posture::None,
        }
    }

    pub fn tag(&self) -> &'static str {
        match self {
            PoiKind::Bench => "bench",
            PoiKind::Wing => "wing",
            PoiKind::Verge => "verge",
            PoiKind::Fountain => "fountain",
            PoiKind::Den => "den",
            PoiKind::Tree => "tree",
            PoiKind::PlaySpot => "playspot",
            PoiKind::Stall => "stall",
            PoiKind::Nook => "nook",
        }
    }
}

/// A single spot within/around a location.
#[derive(Debug, Clone, Copy)]
pub struct Poi {
    pub id: &'static str,
    pub host: LocationId,
    pub name: &'static str,
    pub kind: PoiKind,
    /// Offset from the host node, in viewer space.
    pub dx: f64,
    pub dy: f64,
}

impl Poi {
    /// Absolute viewer-space position (host node + offset).
    pub fn xy(&self) -> (f64, f64) {
        let (hx, hy) = node_xy(self.host).unwrap_or((500.0, 380.0));
        (hx + self.dx, hy + self.dy)
    }
    pub fn posture(&self) -> Posture {
        self.kind.posture()
    }
}

/// The district's catalogue of points of interest. Stable order; deterministic.
/// Many small spots so a place is inhabited at fine grain, not one crowded dot.
pub const POIS: &[Poi] = &[
    // Stadium — the east wing shade (the dog's nap), a rail to watch from.
    Poi { id: "poi_stadium_wing", host: "loc_stadium", name: "under the east wing", kind: PoiKind::Wing, dx: 58.0, dy: 26.0 },
    Poi { id: "poi_stadium_rail", host: "loc_stadium", name: "the touchline rail", kind: PoiKind::Verge, dx: -40.0, dy: 34.0 },
    Poi { id: "poi_stadium_step", host: "loc_stadium", name: "the terrace steps", kind: PoiKind::Bench, dx: 8.0, dy: -34.0 },
    // Main Square — benches, the fountain, market pitches.
    Poi { id: "poi_square_bench_n", host: "loc_main_square", name: "the north bench", kind: PoiKind::Bench, dx: -46.0, dy: -20.0 },
    Poi { id: "poi_square_bench_s", host: "loc_main_square", name: "the south bench", kind: PoiKind::Bench, dx: 44.0, dy: 26.0 },
    Poi { id: "poi_square_fountain", host: "loc_main_square", name: "the fountain", kind: PoiKind::Fountain, dx: 0.0, dy: 40.0 },
    Poi { id: "poi_square_stall", host: "loc_main_square", name: "a market pitch", kind: PoiKind::Stall, dx: -34.0, dy: 30.0 },
    // Café — a doorway nook, a pavement bench.
    Poi { id: "poi_cafe_nook", host: "loc_cafe", name: "the doorway", kind: PoiKind::Nook, dx: -30.0, dy: 18.0 },
    Poi { id: "poi_cafe_bench", host: "loc_cafe", name: "a pavement table", kind: PoiKind::Bench, dx: 34.0, dy: 12.0 },
    // Riverside — the grassy verge, a willow.
    Poi { id: "poi_river_verge", host: "loc_riverside", name: "the grassy verge", kind: PoiKind::Verge, dx: 44.0, dy: 10.0 },
    Poi { id: "poi_river_willow", host: "loc_riverside", name: "the old willow", kind: PoiKind::Tree, dx: -46.0, dy: -8.0 },
    // Bridge — a spot to lean and watch the water.
    Poi { id: "poi_bridge_rail", host: "loc_bridge", name: "the bridge rail", kind: PoiKind::Verge, dx: 24.0, dy: 14.0 },
    // Oakside — a den beneath the Old Oak, its wide shade.
    Poi { id: "poi_oak_den", host: "loc_oakside", name: "the den under the roots", kind: PoiKind::Den, dx: 40.0, dy: 20.0 },
    Poi { id: "poi_oak_shade", host: "loc_oakside", name: "the Oak's shade", kind: PoiKind::Tree, dx: -38.0, dy: 8.0 },
    // School — the yard (play), a wall to sit on.
    Poi { id: "poi_school_yard", host: "loc_school", name: "the school yard", kind: PoiKind::PlaySpot, dx: 40.0, dy: 30.0 },
    Poi { id: "poi_school_wall", host: "loc_school", name: "the low wall", kind: PoiKind::Bench, dx: -36.0, dy: 20.0 },
    // High Street — a shop doorway.
    Poi { id: "poi_high_nook", host: "loc_high_street", name: "a shop doorway", kind: PoiKind::Nook, dx: 30.0, dy: 18.0 },
    // Pub — a bench outside.
    Poi { id: "poi_pub_bench", host: "loc_pub", name: "the bench out front", kind: PoiKind::Bench, dx: 30.0, dy: 22.0 },
];

/// The points of interest hosted by a location (in catalogue order).
pub fn at(host: &str) -> Vec<&'static Poi> {
    POIS.iter().filter(|p| p.host == host).collect()
}

/// A tiny deterministic hash (FNV-1a) over id + place + a numeric salt, so a
/// settled entity keeps a stable spot within a stretch of time but can drift to
/// another later. No RNG; replays identically.
fn pick_hash(id: &str, host: &str, salt: u64) -> u64 {
    let mut h: u64 = 0xcbf2_9ce4_8422_2325;
    for s in [id, host] {
        for b in s.bytes() {
            h ^= b as u64;
            h = h.wrapping_mul(0x0100_0000_01b3);
        }
        h ^= 0x2c;
        h = h.wrapping_mul(0x0100_0000_01b3);
    }
    h ^= salt;
    h.wrapping_mul(0x0100_0000_01b3)
}

/// Deterministically choose a spot for a settled entity at `host` (or `None` if
/// the place has none). `salt` (e.g. the day) lets the choice drift slowly while
/// staying stable within a visit.
pub fn assign(id: &str, host: &str, salt: u64) -> Option<&'static Poi> {
    let spots = at(host);
    if spots.is_empty() {
        return None;
    }
    let i = (pick_hash(id, host, salt) % spots.len() as u64) as usize;
    Some(spots[i])
}

/// The kinds of spot a species keeps to — its "way" of inhabiting a place. A cat
/// takes a nook, a low branch or an edge; the heron only ever the water's verge;
/// the fox a den or shaded lee. Returns an empty slice for humans (they take any
/// spot — a bench, the fountain — which is exactly what animals should NOT do).
/// See design/animal-territories.md.
pub fn kinds_for(species: &str) -> &'static [PoiKind] {
    use PoiKind::*;
    match species {
        "cat" => &[Nook, Tree, Verge],
        "fox" => &[Den, Verge, Wing, Tree],
        "heron" => &[Verge],
        "hedgehog" => &[Den, Tree],
        "owl" => &[Tree, Wing],
        "crow" => &[Tree, Nook, Verge],
        "dog" => &[Nook, Verge, Wing, Tree],
        _ => &[], // humans: no restriction
    }
}

/// Choose a spot the way `species` does: prefer its characteristic kinds, and fall
/// back to any spot only if the place offers none of them. Humans (empty kind set)
/// get the plain `assign`. Deterministic — same inputs, same spot.
pub fn assign_for(id: &str, host: &str, salt: u64, species: &str) -> Option<&'static Poi> {
    let prefer = kinds_for(species);
    if prefer.is_empty() {
        return assign(id, host, salt);
    }
    let liked: Vec<&'static Poi> = at(host)
        .into_iter()
        .filter(|p| prefer.contains(&p.kind))
        .collect();
    if liked.is_empty() {
        return assign(id, host, salt); // nothing in character here — take what there is
    }
    let i = (pick_hash(id, host, salt) % liked.len() as u64) as usize;
    Some(liked[i])
}

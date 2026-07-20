//! Wildlife: the animals of the district as *living entities*, not scenery.
//!
//! Each animal is persistent, with a species, a character (how bold it is around
//! people, how restless it is), a home range of places it keeps to, and a den it
//! returns to. It keeps its own daily rhythm — and, crucially, several of them
//! live *at night*, so the small hours are no longer empty: the fox works the
//! riverside, the owl calls from the oak, the hedgehog snuffles along the hedges,
//! a cat prowls the square.
//!
//! Behaviour is driven by a *seeded* random generator (`sim::rng`): a given world
//! seed always replays the same animal life, but a different seed grows a different
//! one — the small, genuine unpredictability a living thing needs. The residents
//! stay fully deterministic and are untouched by this.

use std::collections::BTreeMap;

use crate::sim::clock::TRAVEL_TICKS_PER_WEIGHT;
use crate::sim::rng::Rng;
use crate::world::location::LocationId;
use crate::world::navigation::NavGraph;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Species {
    Fox,
    Cat,
    Owl,
    Heron,
    Crow,
    Hedgehog,
}

impl Species {
    pub fn tag(&self) -> &'static str {
        match self {
            Species::Fox => "fox",
            Species::Cat => "cat",
            Species::Owl => "owl",
            Species::Heron => "heron",
            Species::Crow => "crow",
            Species::Hedgehog => "hedgehog",
        }
    }
}

/// When an animal is awake and about.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Diel {
    Diurnal,
    Nocturnal,
    Crepuscular,
}

impl Diel {
    pub fn active_at(&self, hour: u64) -> bool {
        match self {
            Diel::Diurnal => (6..=19).contains(&hour),
            Diel::Nocturnal => !(6..=19).contains(&hour), // 20–23 and 0–5
            Diel::Crepuscular => (5..=8).contains(&hour) || (16..=21).contains(&hour),
        }
    }
}

/// What an animal is doing right now.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Act {
    Rest,
    Roam,
    Hunt,
    Forage,
    Perch,
    Watch,
    Call,
    Flee,
    Play,
    Groom,
}

impl Act {
    fn word(&self) -> &'static str {
        match self {
            Act::Rest => "resting",
            Act::Roam => "exploring",
            Act::Hunt => "hunting",
            Act::Forage => "foraging",
            Act::Perch => "perched, still",
            Act::Watch => "watching",
            Act::Call => "calling",
            Act::Flee => "slipping away",
            Act::Play => "at play",
            Act::Groom => "grooming",
        }
    }
}

/// A single leg of movement between two adjacent nodes.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Trip {
    pub from: LocationId,
    pub to: LocationId,
    pub total: u32,
    pub left: u32,
}

/// One animal — a persistent entity with character and a live state.
#[derive(Debug, Clone)]
pub struct Animal {
    pub id: &'static str,
    pub name: &'static str,
    pub species: Species,
    pub color: &'static str,
    diel: Diel,
    /// How many co-present people it will tolerate before it withdraws.
    boldness: i32,
    /// How often it moves (0 = very still, 3 = restless).
    restlessness: i32,
    /// Ticks per unit of edge weight (a fox is quick; a heron barely moves).
    pace: u32,
    range: &'static [LocationId],
    den: LocationId,
    favourite: LocationId,

    // live state
    pub place: LocationId,
    pub trip: Option<Trip>,
    pub act: Act,
    dwell: u32,
}

impl Animal {
    fn wary(&self) -> bool {
        self.boldness <= 1
    }

    /// A human-readable statement of what it is doing and where.
    pub fn doing(&self) -> String {
        self.act.word().to_string()
    }

    fn begin_trip(&mut self, to: LocationId, nav: &NavGraph) {
        let w = edge_weight(nav, self.place, to).max(1);
        let total = (w * self.pace * TRAVEL_TICKS_PER_WEIGHT).max(1);
        self.trip = Some(Trip { from: self.place, to, total, left: total });
    }

    /// Pick an in-character activity for right now.
    fn choose_act(&self, rng: &mut Rng) -> Act {
        let opts: &[Act] = match self.species {
            Species::Fox => &[Act::Hunt, Act::Hunt, Act::Watch, Act::Roam],
            Species::Cat => &[Act::Watch, Act::Play, Act::Forage, Act::Groom, Act::Watch],
            Species::Owl => &[Act::Perch, Act::Perch, Act::Call, Act::Watch, Act::Groom],
            Species::Heron => &[Act::Hunt, Act::Watch, Act::Watch, Act::Groom],
            Species::Crow => &[Act::Forage, Act::Call, Act::Watch, Act::Groom],
            Species::Hedgehog => &[Act::Forage, Act::Forage, Act::Roam],
        };
        *rng.pick(opts).unwrap_or(&Act::Watch)
    }

    /// Where it drifts next when it decides to move.
    fn choose_target(&self, rng: &mut Rng) -> LocationId {
        if rng.chance(45) {
            self.favourite
        } else {
            *rng.pick(self.range).unwrap_or(&self.place)
        }
    }
}

/// The district's wildlife: a fixed cast of individuals, ticked together.
#[derive(Debug, Clone)]
pub struct Wildlife {
    pub animals: Vec<Animal>,
}

impl Default for Wildlife {
    fn default() -> Self {
        Self::new()
    }
}

impl Wildlife {
    pub fn new() -> Self {
        Wildlife { animals: cast() }
    }

    /// Advance every animal one tick. Returns the narration lines produced this
    /// tick (actor, text) for the ambient stream. `occ` is how many residents are
    /// present at each place (so wary animals can keep their distance). All choices
    /// draw from the seeded `rng`.
    pub fn tick(
        &mut self,
        rng: &mut Rng,
        hour: u64,
        nav: &NavGraph,
        occ: &BTreeMap<LocationId, usize>,
    ) -> Vec<(&'static str, String)> {
        let mut out = Vec::new();
        for a in &mut self.animals {
            if let Some(line) = step_animal(a, rng, hour, nav, occ) {
                out.push(line);
            }
        }
        out
    }
}

/// One animal's tick. Returns an optional narration line.
fn step_animal(
    a: &mut Animal,
    rng: &mut Rng,
    hour: u64,
    nav: &NavGraph,
    occ: &BTreeMap<LocationId, usize>,
) -> Option<(&'static str, String)> {
    // 1. Advance a trip in progress.
    if let Some(mut t) = a.trip {
        t.left = t.left.saturating_sub(1);
        if t.left == 0 {
            a.place = t.to;
            a.trip = None;
            a.act = a.choose_act(rng);
            a.dwell = rng.range(4, 12) as u32;
            if rng.chance(35) {
                return Some((a.name, narrate(a, rng)));
            }
        } else {
            a.trip = Some(t);
        }
        return None;
    }

    // 2. Dwelling — hold, with the occasional small beat.
    if a.dwell > 0 {
        a.dwell -= 1;
        if rng.chance(10) {
            return Some((a.name, narrate(a, rng)));
        }
        return None;
    }

    // 3. Reconsider.
    let active = a.diel.active_at(hour);
    if !active {
        // Head home to the den and settle for a good while.
        if a.place != a.den {
            if let Some(next) = step_toward(a.place, a.den, a.range, nav) {
                a.act = Act::Roam;
                a.begin_trip(next, nav);
                return None;
            }
        }
        a.act = Act::Rest;
        a.dwell = rng.range(14, 40) as u32;
        if rng.chance(25) {
            return Some((a.name, narrate(a, rng)));
        }
        return None;
    }

    // Active. A wary animal withdraws if people crowd its spot.
    let here = *occ.get(a.place).unwrap_or(&0) as i32;
    if a.wary() && here > a.boldness {
        if let Some(next) = quietest_neighbor(a.place, a.range, nav, occ) {
            a.act = Act::Flee;
            a.begin_trip(next, nav);
            if rng.chance(40) {
                return Some((a.name, narrate(a, rng)));
            }
            return None;
        }
    }

    // Otherwise: move on, or do something in character where it is.
    let move_chance = (25 + a.restlessness * 15).clamp(10, 80) as u32;
    if rng.chance(move_chance) {
        let target = a.choose_target(rng);
        if target != a.place {
            if let Some(next) = step_toward(a.place, target, a.range, nav) {
                a.act = Act::Roam;
                a.begin_trip(next, nav);
                return None;
            }
        }
    }
    a.act = a.choose_act(rng);
    a.dwell = rng.range(6, 18) as u32;
    if rng.chance(45) {
        return Some((a.name, narrate(a, rng)));
    }
    None
}

// ------------------------------------------------------------ movement helpers

fn edge_weight(nav: &NavGraph, a: LocationId, b: LocationId) -> u32 {
    nav.neighbors(a).into_iter().find(|(n, _)| *n == b).map(|(_, w)| w).unwrap_or(1)
}

fn range_neighbors(place: LocationId, range: &[LocationId], nav: &NavGraph) -> Vec<LocationId> {
    nav.neighbors(place)
        .into_iter()
        .map(|(n, _)| n)
        .filter(|n| range.contains(n))
        .collect()
}

/// The in-range neighbour that gets closest to `target` (a single step).
fn step_toward(
    place: LocationId,
    target: LocationId,
    range: &[LocationId],
    nav: &NavGraph,
) -> Option<LocationId> {
    if place == target {
        return None;
    }
    let ns = range_neighbors(place, range, nav);
    if ns.is_empty() {
        return None;
    }
    if let Some(&t) = ns.iter().find(|&&n| n == target) {
        return Some(t);
    }
    ns.into_iter()
        .min_by_key(|&n| nav.travel_time(n, target).unwrap_or(u32::MAX))
}

/// The quietest in-range neighbour (fewest people) — where a wary animal slips to.
fn quietest_neighbor(
    place: LocationId,
    range: &[LocationId],
    nav: &NavGraph,
    occ: &BTreeMap<LocationId, usize>,
) -> Option<LocationId> {
    range_neighbors(place, range, nav)
        .into_iter()
        .min_by_key(|n| *occ.get(n).unwrap_or(&0))
}

// ------------------------------------------------------------ narration

fn narrate(a: &Animal, rng: &mut Rng) -> String {
    let opts: &[&str] = match (a.species, a.act) {
        (_, Act::Rest) => &["is curled somewhere out of sight", "sleeps, hidden away"],
        (Species::Cat, Act::Groom) => &["washes a paw and draws it over an ear", "grooms, one leg raised"],
        (_, Act::Groom) => &["preens, settling each feather", "runs its bill along a wing"],

        (Species::Fox, Act::Hunt) => &[
            "noses along the riverside, low and intent",
            "freezes, one paw raised, then pounces at the grass",
            "trots the bank with its brush held level",
        ],
        (Species::Fox, Act::Watch) => &["sits back on its haunches and reads the dark", "watches a lit window for a long moment"],
        (Species::Fox, Act::Flee) => &["melts into the shadow between two walls", "is gone before you are sure it was there"],
        (Species::Fox, _) => &["slips along the edge of the lamplight", "crosses the open ground at an unhurried trot"],

        (Species::Cat, Act::Play) => &["bats a fallen leaf across the cobbles", "chases something only it can see"],
        (Species::Cat, Act::Watch) => &["watches the street from a warm sill, tail curled", "sits in a doorway, unbothered and unhurried"],
        (Species::Cat, Act::Forage) => &["noses at a scrap by the bins, then thinks better of it"],
        (Species::Cat, Act::Flee) => &["flows off the wall and is gone"],
        (Species::Cat, _) => &["pads along the top of the wall", "prowls the quiet street, a shadow among shadows"],

        (Species::Owl, Act::Call) => &["calls once across the rooftops, and waits", "gives a low hoot from the dark of the tower"],
        (Species::Owl, Act::Perch) => &["sits the oak like a knot of the wood itself", "turns its head slowly, surveying the square"],
        (Species::Owl, Act::Hunt) => &["drops from the eave on soundless wings", "glides the length of the street and is gone"],
        (Species::Owl, _) => &["ghosts between the chimneys", "shifts along the branch, blinking"],

        (Species::Heron, Act::Hunt) => &["stands in the shallows, patient as a post", "spears the water and comes up empty, unhurried"],
        (Species::Heron, _) => &["stands one-legged at the water's edge", "lifts, folds itself, and settles a little further along"],

        (Species::Crow, Act::Call) => &["argues with the rooftops in a hard, flat voice", "answers a distant crow, twice"],
        (Species::Crow, Act::Forage) => &["turns over a crust with a sideways eye", "struts the square, inspecting everything"],
        (Species::Crow, _) => &["flaps up to the museum chimney and looks down on it all", "sidles along the ridge tiles"],

        (Species::Hedgehog, Act::Forage) => &["snuffles along the hedge-bottom", "roots in the leaf litter under the oak"],
        (Species::Hedgehog, _) => &["trundles across the path and into the dark", "rustles unseen along the wall"],
    };
    let s = rng.pick(opts).copied().unwrap_or("is about");
    format!("{s}")
}

// ------------------------------------------------------------------------ cast

const FOX_RANGE: &[LocationId] = &["loc_riverside", "loc_bridge", "loc_oakside", "loc_main_square", "loc_high_street"];
const TABBY_RANGE: &[LocationId] = &["loc_bakery", "loc_millers_row", "loc_main_square", "loc_high_street"];
const BLACKCAT_RANGE: &[LocationId] = &["loc_cafe", "loc_main_square", "loc_high_street", "loc_pub"];
const OWL_RANGE: &[LocationId] = &["loc_museum", "loc_cafe", "loc_main_square", "loc_oakside"];
const HERON_RANGE: &[LocationId] = &["loc_riverside", "loc_bridge"];
const CROW_RANGE: &[LocationId] = &["loc_museum", "loc_cafe", "loc_main_square"];
const HEDGEHOG_RANGE: &[LocationId] = &["loc_oakside", "loc_riverside", "loc_bridge"];

/// The district's wildlife, in stable order (drives deterministic iteration).
pub fn cast() -> Vec<Animal> {
    let mk = |id, name, species, color, diel, boldness, restlessness, pace, range: &'static [LocationId], den, favourite| Animal {
        id,
        name,
        species,
        color,
        diel,
        boldness,
        restlessness,
        pace,
        range,
        den,
        favourite,
        place: den,
        trip: None,
        act: Act::Rest,
        dwell: 0,
    };
    vec![
        mk("ani_fox", "the riverside fox", Species::Fox, "#c1502e", Diel::Nocturnal, 1, 3, 1, FOX_RANGE, "loc_oakside", "loc_riverside"),
        mk("ani_tabby", "the bakery cat", Species::Cat, "#b0895f", Diel::Crepuscular, 3, 2, 1, TABBY_RANGE, "loc_bakery", "loc_bakery"),
        mk("ani_blackcat", "the black cat", Species::Cat, "#4b4b52", Diel::Nocturnal, 2, 3, 1, BLACKCAT_RANGE, "loc_high_street", "loc_main_square"),
        mk("ani_owl", "the church owl", Species::Owl, "#d9c9a3", Diel::Nocturnal, 0, 1, 1, OWL_RANGE, "loc_museum", "loc_oakside"),
        mk("ani_heron", "the grey heron", Species::Heron, "#7f8fa0", Diel::Crepuscular, 1, 0, 3, HERON_RANGE, "loc_riverside", "loc_riverside"),
        mk("ani_crows", "the museum crows", Species::Crow, "#2e2e33", Diel::Diurnal, 3, 2, 1, CROW_RANGE, "loc_museum", "loc_museum"),
        mk("ani_hedgehog", "the hedgehog", Species::Hedgehog, "#8a7a5c", Diel::Nocturnal, 0, 1, 2, HEDGEHOG_RANGE, "loc_oakside", "loc_oakside"),
    ]
}

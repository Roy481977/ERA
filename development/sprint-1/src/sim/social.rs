//! Social life (Phase 4): relationships, and deterministic interactions between
//! residents who share a public place at a compatible time.
//!
//! Ownership: the `Relationships` store is the single owner of affinity/trust
//! facts; residents own their own memories. The interaction system *proposes* an
//! interaction from world state (who is co-located, their relationship, the
//! place, the time) and a deterministic seed, then applies consequences through
//! those owners — it never rewrites truth behind their backs.

use std::collections::BTreeMap;

pub type ResId = &'static str;

/// A directed-agnostic relationship between two residents.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub struct Rel {
    pub affinity: i32,
    pub trust: i32,
}

/// The authoritative store of relationship facts (one owner).
#[derive(Debug, Clone, Default)]
pub struct Relationships {
    map: BTreeMap<(ResId, ResId), Rel>,
}

fn key(a: ResId, b: ResId) -> (ResId, ResId) {
    if a <= b {
        (a, b)
    } else {
        (b, a)
    }
}

impl Relationships {
    /// Seed the initial web of relationships (from DS-001 §2).
    pub fn seeded() -> Self {
        let mut r = Relationships::default();
        r.set("res_hana", "res_sofia", 3, 3); // mentor & apprentice
        r.set("res_hana", "res_tomas", 2, 2); // gives him a roll
        r.set("res_luca", "res_victor", 3, 2); // keeps his corner
        r.set("res_elias", "res_agnes", 3, 3); // old friends
        r.set("res_eva", "res_agnes", 2, 2); // leaves flowers
        r.set("res_milo", "res_karim", 2, 1); // busks by the kiosk
        r.set("res_sofia", "res_milo", 1, 1); // young friends
        r.set("res_tomas", "res_agnes", 1, 2); // the boy and the elder
        r.set("res_eva", "res_karim", 2, 2); // stall & kiosk neighbours
        r
    }

    fn set(&mut self, a: ResId, b: ResId, affinity: i32, trust: i32) {
        self.map.insert(key(a, b), Rel { affinity, trust });
    }

    pub fn get(&self, a: ResId, b: ResId) -> Rel {
        self.map.get(&key(a, b)).copied().unwrap_or_default()
    }

    /// Apply a change to a relationship, returning the (before, after) pair.
    pub fn adjust(&mut self, a: ResId, b: ResId, d_aff: i32, d_trust: i32) -> (Rel, Rel) {
        let before = self.get(a, b);
        let after = Rel {
            affinity: (before.affinity + d_aff).clamp(-10, 10),
            trust: (before.trust + d_trust).clamp(-10, 10),
        };
        self.map.insert(key(a, b), after);
        (before, after)
    }
}

/// A small, deterministic FNV-1a hash over string parts plus a numeric salt.
/// Used as the seed for interaction rolls so replays are identical (no RNG).
pub fn seed_hash(parts: &[&str], salt: u64) -> u64 {
    let mut h: u64 = 0xcbf2_9ce4_8422_2325;
    for p in parts {
        for byte in p.bytes() {
            h ^= byte as u64;
            h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
        h ^= 0x2c; // ',' separator
        h = h.wrapping_mul(0x0000_0100_0000_01b3);
    }
    h ^= salt;
    h = h.wrapping_mul(0x0000_0100_0000_01b3);
    h
}

/// The kind of interaction that occurred.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum InteractionKind {
    Greeting,
    Conversation,
    SharedCoffee,
    Encouragement,
    Recognition,
    Disagreement,
}

impl InteractionKind {
    pub fn verb(&self) -> &'static str {
        match self {
            InteractionKind::Greeting => "exchanged a greeting",
            InteractionKind::Conversation => "fell into conversation",
            InteractionKind::SharedCoffee => "shared a coffee",
            InteractionKind::Encouragement => "shared a word of encouragement",
            InteractionKind::Recognition => "traded a nod of recognition",
            InteractionKind::Disagreement => "had a short disagreement",
        }
    }

    /// Consequence on (affinity, trust).
    pub fn deltas(&self) -> (i32, i32) {
        match self {
            InteractionKind::Greeting => (1, 0),
            InteractionKind::Conversation => (1, 1),
            InteractionKind::SharedCoffee => (1, 1),
            InteractionKind::Encouragement => (1, 2),
            InteractionKind::Recognition => (0, 1),
            InteractionKind::Disagreement => (-1, -1),
        }
    }
}

/// The proposed outcome of a co-location, before consequences are applied.
#[derive(Debug, Clone, Copy)]
pub struct Outcome {
    pub kind: InteractionKind,
    pub reason: &'static str,
}

/// A structured record of an interaction that happened (for tests, the observer,
/// and downstream systems such as the Old Oak).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Interaction {
    pub tick: u64,
    pub day: u64,
    pub hour: u64,
    pub a: ResId,
    pub b: ResId,
    pub kind: InteractionKind,
    pub place: &'static str,
}

/// Decide whether residents `a` and `b`, co-located at `place`, interact this
/// tick — and if so, of what kind. Deterministic in (ids, place, tick).
/// `rel` is their current relationship. Returns `None` when they pass without
/// interacting (so not every co-location produces an interaction).
pub fn decide(
    a: ResId,
    b: ResId,
    place: &str,
    tick: u64,
    rel: Rel,
    familiarity: u32,
) -> Option<Outcome> {
    // Shared history warms an encounter: every few past meetings is a point of
    // warmth on top of raw affinity (capped), and it makes people a little more
    // likely to stop at all. This is memory changing behaviour.
    let fam_bonus = (familiarity / 4).min(3) as i32;

    let roll = (seed_hash(&[a, b, place], tick) % 100) as i32;
    let chance = (24 + rel.affinity * 8 + fam_bonus * 4).clamp(6, 95);
    if roll >= chance {
        return None;
    }

    let flavor = seed_hash(&[b, a, place, "kind"], tick) % 100;
    let warmth = rel.affinity + fam_bonus;
    let kind = if rel.affinity <= -2 {
        InteractionKind::Disagreement
    } else if place == "loc_cafe" && warmth >= 2 {
        InteractionKind::SharedCoffee
    } else if warmth >= 4 {
        InteractionKind::Encouragement
    } else if warmth >= 2 {
        InteractionKind::Conversation
    } else if warmth >= 1 {
        InteractionKind::Greeting
    } else if flavor < 55 {
        InteractionKind::Recognition
    } else {
        InteractionKind::Greeting
    };

    // The reason names *why* it was warm — including the weight of shared history.
    let reason = if rel.affinity <= -2 {
        "on poor terms"
    } else if fam_bonus >= 2 {
        "old friends, and it shows"
    } else if warmth >= 3 {
        "close friends"
    } else if warmth >= 1 {
        "familiar faces"
    } else {
        "barely acquainted"
    };

    Some(Outcome { kind, reason })
}

// ---------------------------------------------------------------- shared bonds

/// What two residents remember of their shared experiences: how often they've
/// met, where, and when last. This is the raw material of social continuity —
/// distinct from the affinity/trust summary in `Relationships`.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct SharedBond {
    pub meetings: u32,
    pub last_day: u64,
    /// Where they have met, tallied — the argmax is "their place".
    pub place_counts: std::collections::BTreeMap<ResId, u32>,
}

impl SharedBond {
    /// The place they most often share, if they have one.
    pub fn usual_place(&self) -> Option<ResId> {
        self.place_counts
            .iter()
            .max_by_key(|(place, n)| (**n, **place))
            .map(|(place, _)| *place)
    }
}

/// The store of shared histories (one owner). Keyed by unordered pair.
#[derive(Debug, Clone, Default)]
pub struct Bonds {
    map: BTreeMap<(ResId, ResId), SharedBond>,
}

impl Bonds {
    /// Record that `a` and `b` met at `place` on `day`.
    pub fn record(&mut self, a: ResId, b: ResId, place: ResId, day: u64) {
        let e = self.map.entry(key(a, b)).or_default();
        e.meetings += 1;
        e.last_day = day;
        *e.place_counts.entry(place).or_default() += 1;
    }

    pub fn get(&self, a: ResId, b: ResId) -> Option<&SharedBond> {
        self.map.get(&key(a, b))
    }

    pub fn meetings(&self, a: ResId, b: ResId) -> u32 {
        self.get(a, b).map(|s| s.meetings).unwrap_or(0)
    }

    pub fn usual_place(&self, a: ResId, b: ResId) -> Option<ResId> {
        self.get(a, b).and_then(|s| s.usual_place())
    }
}

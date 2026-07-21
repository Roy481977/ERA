//! Possessions (part of the generative world). What a resident *has* and *wears*
//! is not fixed: it changes with the season and the sky (a coat and gloves in a
//! cold snap, an umbrella in the rain, a sun hat in high summer), with what they
//! are doing (an apron at the counter), with the day (a club scarf on matchday) —
//! and, slowly, it *accretes*: every so often a resident picks up a lasting
//! keepsake (a cap, a basket, a satchel) they carry from then on. That accretion
//! is the "mining" of new possessions over time.
//!
//! Two layers, both deterministic:
//!   * **owned** — the lasting things a resident has gathered (seeded weekly
//!     accretion; append-only, bounded).
//!   * **worn** — what they visibly have on *right now*, derived purely from
//!     season + weather + activity + the day, plus one signature owned keepsake.

use std::collections::BTreeMap;

use crate::sim::oak::Season;
use crate::sim::social::seed_hash;
use crate::sim::weather::{Sky, Temp, Weather};

pub type ResId = &'static str;

/// A thing a resident wears or carries.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Item {
    Coat,
    Gloves,
    Boots,
    Umbrella,
    SunHat,
    ClubScarf,
    Apron,
    // lasting keepsakes (accreting, owned)
    Cap,
    Basket,
    Satchel,
    Scarf,
    Flower,
}

impl Item {
    pub fn tag(&self) -> &'static str {
        match self {
            Item::Coat => "coat",
            Item::Gloves => "gloves",
            Item::Boots => "boots",
            Item::Umbrella => "umbrella",
            Item::SunHat => "sunhat",
            Item::ClubScarf => "club_scarf",
            Item::Apron => "apron",
            Item::Cap => "cap",
            Item::Basket => "basket",
            Item::Satchel => "satchel",
            Item::Scarf => "scarf",
            Item::Flower => "flower",
        }
    }
}

/// The keepsakes a resident may accrete over time (owned, lasting).
const KEEPSAKES: &[Item] = &[Item::Cap, Item::Basket, Item::Satchel, Item::Scarf, Item::Flower];
/// The most lasting keepsakes any one resident gathers.
const OWNED_CAP: usize = 4;

/// The store of what everyone owns. Worn items are derived, not stored.
#[derive(Debug, Clone, Default)]
pub struct Possessions {
    owned: BTreeMap<ResId, Vec<Item>>,
}

impl Possessions {
    pub fn new() -> Self {
        Possessions::default()
    }

    pub fn owned(&self, id: ResId) -> &[Item] {
        self.owned.get(id).map(|v| v.as_slice()).unwrap_or(&[])
    }

    /// The one signature keepsake a resident is known by (their first-gathered).
    pub fn signature(&self, id: ResId) -> Option<Item> {
        self.owned.get(id).and_then(|v| v.first().copied())
    }

    /// Seeded weekly accretion: once in a while a resident gathers a lasting
    /// keepsake. Deterministic in `(id, week, seed)`; append-only and bounded, so
    /// the same seed always grows the same collections. Call once per new week.
    pub fn accrete(&mut self, ids: &[ResId], week: u64, seed: u64) {
        for &id in ids {
            let e = self.owned.entry(id).or_default();
            if e.len() >= OWNED_CAP {
                continue;
            }
            let h = seed_hash(&[id, "acquire"], week ^ seed);
            if h % 100 < 20 {
                let it = KEEPSAKES[(h / 100 % KEEPSAKES.len() as u64) as usize];
                if !e.contains(&it) {
                    e.push(it);
                }
            }
        }
    }

    /// What resident `id` visibly has on right now — a pure function of the
    /// world's state. Order is stable (outer layers first).
    pub fn worn(
        &self,
        id: ResId,
        season: Season,
        weather: Weather,
        working: bool,
        matchday: bool,
    ) -> Vec<Item> {
        let mut w: Vec<Item> = Vec::new();
        // dressed for the cold / the wet
        if weather.is_cold() || season == Season::Winter {
            w.push(Item::Coat);
        }
        if weather.temp == Temp::Cold {
            w.push(Item::Gloves);
        }
        if weather.sky == Sky::Snow {
            w.push(Item::Boots);
        }
        if weather.sky == Sky::Rain {
            w.push(Item::Umbrella);
        }
        // dressed for the sun
        if season == Season::Summer
            && matches!(weather.sky, Sky::Clear | Sky::Fair)
            && matches!(weather.temp, Temp::Warm | Temp::Hot)
        {
            w.push(Item::SunHat);
        }
        // the day / the work
        if matchday {
            w.push(Item::ClubScarf);
        }
        if working {
            w.push(Item::Apron);
        }
        // one signature keepsake they always carry
        if let Some(k) = self.signature(id) {
            if !w.contains(&k) {
                w.push(k);
            }
        }
        w
    }

    /// Convenience: the worn set as renderer tags.
    pub fn worn_tags(
        &self,
        id: ResId,
        season: Season,
        weather: Weather,
        working: bool,
        matchday: bool,
    ) -> Vec<&'static str> {
        self.worn(id, season, weather, working, matchday)
            .iter()
            .map(|i| i.tag())
            .collect()
    }
}

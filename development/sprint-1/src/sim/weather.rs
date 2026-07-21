//! Weather (part of the generative world). The sky over the district changes day
//! to day and season to season — a bright summer morning, a wet autumn, a still
//! cold fog in winter. It is **deterministic**: the weather of a given day is a
//! pure function of `(day, season, world seed)`, so a seed replays the same
//! weather, yet it is not a rigid calendar — two neighbouring days differ, and a
//! different seed grows a different year of weather. Residents draw no RNG from
//! it; the town stays reproducible.
//!
//! Weather is *consequential*, not decoration (per the Weather & Season engine's
//! first proof): a wet or cold day dampens the appetite for lingering outdoors and
//! for spur-of-the-moment detours, so people head home rather than dawdle in the
//! square — place use changes with the sky, without any scripted exception.

use crate::sim::oak::Season;
use crate::sim::social::seed_hash;

/// The state of the sky.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Sky {
    Clear,
    Fair,     // a few clouds, bright
    Cloudy,
    Overcast,
    Rain,
    Snow,
    Fog,
}

impl Sky {
    pub fn tag(&self) -> &'static str {
        match self {
            Sky::Clear => "clear",
            Sky::Fair => "fair",
            Sky::Cloudy => "cloudy",
            Sky::Overcast => "overcast",
            Sky::Rain => "rain",
            Sky::Snow => "snow",
            Sky::Fog => "fog",
        }
    }
    /// A short human phrase (for the ambient/log side-channel).
    pub fn phrase(&self) -> &'static str {
        match self {
            Sky::Clear => "clear skies",
            Sky::Fair => "bright with a few clouds",
            Sky::Cloudy => "grey and clouded over",
            Sky::Overcast => "a low, heavy overcast",
            Sky::Rain => "steady rain",
            Sky::Snow => "falling snow",
            Sky::Fog => "a still, cold fog",
        }
    }
    pub fn is_wet(&self) -> bool {
        matches!(self, Sky::Rain | Sky::Snow)
    }
}

/// How warm it is (coarse; enough to dress by).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Temp {
    Cold,
    Cool,
    Mild,
    Warm,
    Hot,
}

impl Temp {
    pub fn tag(&self) -> &'static str {
        match self {
            Temp::Cold => "cold",
            Temp::Cool => "cool",
            Temp::Mild => "mild",
            Temp::Warm => "warm",
            Temp::Hot => "hot",
        }
    }
}

/// The weather of a day.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Weather {
    pub sky: Sky,
    pub temp: Temp,
    pub windy: bool,
}

impl Weather {
    /// The weather for a day — deterministic in `(day, season, seed)`.
    pub fn for_day(day: u64, season: Season, seed: u64) -> Weather {
        let h = seed_hash(&["weather", season.name()], day ^ seed);
        let r = (h % 100) as u32;
        let sky = match season {
            Season::Summer => match r {
                0..=44 => Sky::Clear,
                45..=72 => Sky::Fair,
                73..=88 => Sky::Cloudy,
                89..=96 => Sky::Rain,
                _ => Sky::Overcast,
            },
            Season::Autumn => match r {
                0..=17 => Sky::Fair,
                18..=40 => Sky::Cloudy,
                41..=62 => Sky::Overcast,
                63..=84 => Sky::Rain,
                85..=95 => Sky::Fog,
                _ => Sky::Clear,
            },
            Season::Winter => match r {
                0..=12 => Sky::Clear,
                13..=33 => Sky::Overcast,
                34..=53 => Sky::Cloudy,
                54..=74 => Sky::Snow,
                75..=90 => Sky::Fog,
                _ => Sky::Rain,
            },
            Season::Spring => match r {
                0..=27 => Sky::Fair,
                28..=48 => Sky::Clear,
                49..=68 => Sky::Cloudy,
                69..=88 => Sky::Rain,
                89..=95 => Sky::Overcast,
                _ => Sky::Fog,
            },
        };
        // temperature: a season band, nudged a step by another hash bit.
        let step = ((h / 100) % 3) as i8 - 1; // -1, 0, +1
        let base = match season {
            Season::Summer => 3, // Warm
            Season::Autumn => 1, // Cool
            Season::Winter => 0, // Cold
            Season::Spring => 2, // Mild
        };
        let mut t = base + step;
        // snow/fog keep it colder; clear summer can tip to hot.
        if matches!(sky, Sky::Snow | Sky::Fog) {
            t -= 1;
        }
        if matches!(sky, Sky::Clear) && season == Season::Summer {
            t += 1;
        }
        let temp = match t.clamp(0, 4) {
            0 => Temp::Cold,
            1 => Temp::Cool,
            2 => Temp::Mild,
            3 => Temp::Warm,
            _ => Temp::Hot,
        };
        let windy = (h / 7) % 100 < 34;
        Weather { sky, temp, windy }
    }

    pub fn is_wet(&self) -> bool {
        self.sky.is_wet()
    }
    pub fn is_cold(&self) -> bool {
        matches!(self.temp, Temp::Cold | Temp::Cool)
    }

    /// How inviting it is to be out and about — folded into the spontaneous
    /// outdoor-social gates (lingering, detours). Wet or cold suppresses dawdling;
    /// a bright mild day encourages it. Range about −4..=+1.
    pub fn outdoor_appeal(&self) -> i32 {
        let mut a = 0;
        a += match self.sky {
            Sky::Clear => 1,
            Sky::Fair => 1,
            Sky::Cloudy => 0,
            Sky::Overcast => -1,
            Sky::Fog => -2,
            Sky::Rain => -3,
            Sky::Snow => -2,
        };
        a += match self.temp {
            Temp::Cold => -2,
            Temp::Cool => -1,
            Temp::Mild => 1,
            Temp::Warm => 1,
            Temp::Hot => 0,
        };
        if self.windy {
            a -= 1;
        }
        a.clamp(-4, 1)
    }
}

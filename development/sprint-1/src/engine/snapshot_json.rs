//! JSON serialization for the engine's live state — the stable wire contract
//! between the world and any renderer. Two shapes:
//!
//!   * `Engine::world_json()`  — the static stage: locations, edges, entities.
//!     Sent once; it never changes during a run.
//!   * `Snapshot::to_json()`   — one live frame: positions, occupancy, callouts,
//!     the Oak, events this tick, inspectable bonds. Sent every tick.
//!
//! Hand-rolled (no serde dependency), matching the codebase's existing style.
//! Whatever produces these snapshots — a native loop here, or the same engine
//! compiled to WebAssembly in a browser — a renderer consumes them identically.

use std::collections::BTreeSet;

use crate::engine::{Engine, Snapshot};
use crate::view::layout::{self, MAP};

/// Minimal JSON string escaping.
pub(crate) fn esc(s: &str) -> String {
    let mut o = String::with_capacity(s.len());
    for c in s.chars() {
        match c {
            '"' => o.push_str("\\\""),
            '\\' => o.push_str("\\\\"),
            '\n' => o.push_str("\\n"),
            _ => o.push(c),
        }
    }
    o
}

impl Engine {
    /// The static stage the renderer needs once: locations (with coordinates and
    /// hours), the navigation edges, and the entity roster (id, name, colour).
    pub fn world_json(&self) -> String {
        let sim = self.sim();
        let mut out = String::new();
        out.push('{');

        // locations
        out.push_str("\"locations\":[");
        for (i, (id, x, y)) in MAP.iter().enumerate() {
            let loc = sim.world.location(id).unwrap();
            let hours = match loc.hours {
                Some(h) => format!("[{},{}]", h.open, h.close),
                None => "null".to_string(),
            };
            if i > 0 {
                out.push(',');
            }
            out.push_str(&format!(
                "{{\"id\":\"{id}\",\"name\":\"{}\",\"x\":{x},\"y\":{y},\"home\":{},\"hours\":{hours}}}",
                esc(loc.name),
                loc.is_residential()
            ));
        }
        out.push(']');

        // edges (unique, undirected)
        out.push_str(",\"edges\":[");
        let mut seen: BTreeSet<(&str, &str)> = BTreeSet::new();
        let mut first = true;
        for node in sim.world.nav.nodes() {
            for (other, _w) in sim.world.nav.neighbors(node) {
                let key = if node < other { (node, other) } else { (other, node) };
                if seen.insert(key) {
                    if !first {
                        out.push(',');
                    }
                    first = false;
                    out.push_str(&format!("[\"{}\",\"{}\"]", key.0, key.1));
                }
            }
        }
        out.push(']');

        // entities roster (residents, the dog, the animals): identity, kind, colour
        out.push_str(",\"entities\":[");
        for (i, r) in sim.residents.iter().enumerate() {
            if i > 0 {
                out.push(',');
            }
            out.push_str(&format!(
                "{{\"id\":\"{}\",\"name\":\"{}\",\"kind\":\"resident\",\"color\":\"{}\"}}",
                r.id,
                esc(r.name),
                layout::color_of(r.id)
            ));
        }
        out.push_str(&format!(
            ",{{\"id\":\"the_old_dog\",\"name\":\"the old dog\",\"kind\":\"dog\",\"color\":\"{}\"}}",
            layout::color_of("the_old_dog")
        ));
        for a in &sim.wildlife.animals {
            out.push_str(&format!(
                ",{{\"id\":\"{}\",\"name\":\"{}\",\"kind\":\"{}\",\"color\":\"{}\"}}",
                a.id,
                esc(a.name),
                a.species.tag(),
                a.color
            ));
        }
        out.push(']');

        // points of interest — the fine spatial layer (benches, the fountain, the
        // shade under the stadium's east wing). Static dressing the renderer draws.
        out.push_str(",\"pois\":[");
        for (i, p) in crate::world::poi::POIS.iter().enumerate() {
            if i > 0 {
                out.push(',');
            }
            let (x, y) = p.xy();
            out.push_str(&format!(
                "{{\"id\":\"{}\",\"host\":\"{}\",\"name\":\"{}\",\"kind\":\"{}\",\"x\":{:.1},\"y\":{:.1}}}",
                p.id, p.host, esc(p.name), p.kind.tag(), x, y
            ));
        }
        out.push(']');

        out.push('}');
        out
    }
}

impl Snapshot {
    /// One live frame as JSON — everything a renderer draws this tick.
    pub fn to_json(&self) -> String {
        let mut out = String::new();
        out.push('{');
        out.push_str(&format!(
            "\"tick\":{},\"day\":{},\"hour\":{},\"minute\":{},\"weekday\":\"{}\",\"phase\":\"{}\"",
            self.tick, self.day, self.hour, self.minute, self.weekday, esc(self.phase)
        ));

        // season and today's weather — the world's dressing.
        out.push_str(&format!(
            ",\"season\":\"{}\",\"weather\":{{\"sky\":\"{}\",\"temp\":\"{}\",\"wet\":{},\"windy\":{},\"phrase\":\"{}\"}}",
            esc(self.season),
            self.weather.sky,
            self.weather.temp,
            self.weather.wet,
            self.weather.windy,
            esc(self.weather.phrase)
        ));

        // live entities — position and *behaviour*: heading (facing), speed, pose,
        // a momentary gesture, and who they attend to. This is what the renderer
        // draws; identity/colour come from the static roster.
        out.push_str(",\"entities\":[");
        for (i, e) in self.entities.iter().enumerate() {
            if i > 0 {
                out.push(',');
            }
            let partner = match e.partner {
                Some(p) => format!("\"{p}\""),
                None => "null".to_string(),
            };
            let mut worn = String::from("[");
            for (k, t) in e.worn.iter().enumerate() {
                if k > 0 {
                    worn.push(',');
                }
                worn.push('"');
                worn.push_str(t);
                worn.push('"');
            }
            worn.push(']');
            let from = match e.from {
                Some(f) => format!("\"{f}\""),
                None => "null".to_string(),
            };
            let to = match e.to {
                Some(t) => format!("\"{t}\""),
                None => "null".to_string(),
            };
            out.push_str(&format!(
                "{{\"id\":\"{}\",\"x\":{:.1},\"y\":{:.1},\"h\":{:.2},\"spd\":{:.2},\"ph\":{:.2},\
                 \"pose\":\"{}\",\"gest\":\"{}\",\"partner\":{},\"place\":\"{}\",\"doing\":\"{}\",\"moving\":{},\
                 \"soc\":{},\"mood\":{:.2},\"energy\":{:.2},\"worn\":{},\"child\":{},\
                 \"from\":{},\"to\":{},\"et\":{:.3}}}",
                e.id,
                e.x,
                e.y,
                e.heading,
                e.speed,
                e.phase,
                e.pose,
                e.gesture,
                partner,
                e.place,
                esc(&e.doing),
                e.traveling,
                e.soc,
                e.mood,
                e.energy,
                worn,
                e.child,
                from,
                to,
                e.edge_t
            ));
        }
        out.push(']');

        // occupancy per place
        out.push_str(",\"occupancy\":{");
        for (i, (place, n)) in self.occupancy.iter().enumerate() {
            if i > 0 {
                out.push(',');
            }
            out.push_str(&format!("\"{place}\":{n}"));
        }
        out.push('}');

        // busiest place
        match &self.busiest {
            Some((place, name, n)) => out.push_str(&format!(
                ",\"busiest\":{{\"place\":\"{place}\",\"name\":\"{}\",\"count\":{n}}}",
                esc(name)
            )),
            None => out.push_str(",\"busiest\":null"),
        }

        // callouts
        out.push_str(",\"callouts\":[");
        for (i, c) in self.callouts.iter().enumerate() {
            if i > 0 {
                out.push(',');
            }
            out.push_str(&format!("{{\"kind\":\"{}\",\"text\":\"{}\"}}", c.kind, esc(&c.text)));
        }
        out.push(']');

        // oak
        out.push_str(&format!(
            ",\"oak\":{{\"ageYears\":{},\"season\":\"{}\",\"appearance\":\"{}\",\"visits\":{},\"scarves\":{},\"bouquets\":{}}}",
            self.oak.age_years,
            esc(self.oak.season),
            esc(self.oak.appearance),
            self.oak.visits,
            self.oak.scarves,
            self.oak.bouquets
        ));

        // events this tick
        out.push_str(",\"events\":[");
        for (i, (actor, text, tag)) in self.events.iter().enumerate() {
            if i > 0 {
                out.push(',');
            }
            out.push_str(&format!("[\"{}\",\"{}\",\"{}\"]", esc(actor), esc(text), tag));
        }
        out.push(']');

        // inspectable bonds
        out.push_str(",\"bonds\":[");
        for (i, b) in self.bonds.iter().enumerate() {
            if i > 0 {
                out.push(',');
            }
            let place = match b.usual_place {
                Some(p) => format!("\"{}\"", esc(p)),
                None => "null".to_string(),
            };
            out.push_str(&format!(
                "{{\"a\":\"{}\",\"b\":\"{}\",\"affinity\":{},\"trust\":{},\"meetings\":{},\"place\":{}}}",
                esc(b.a), esc(b.b), b.affinity, b.trust, b.meetings, place
            ));
        }
        out.push(']');

        out.push('}');
        out
    }
}

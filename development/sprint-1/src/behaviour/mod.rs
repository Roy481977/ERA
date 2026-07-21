//! The Behaviour Layer — between the simulation and the renderer.
//!
//!   Simulation  →  Behaviour Layer  →  Renderer  →  Observer
//!
//! The simulation decides *what happens and why* (Victor and Elias fall into
//! conversation at the café at 12:15). This layer turns that into *observable
//! behaviour with space and time*: they face one another, stand, gesture, laugh,
//! and part. It emits **behaviours, not prose** — typed, timed, spatial state the
//! renderer can visualise directly. The event log becomes a debug side-channel,
//! not the product.
//!
//! It is a stateful *choreographer*: after each simulation tick it observes the
//! world and updates a per-entity behaviour frame — position, heading (which way
//! each thing faces), speed, pose (what its body is doing), a momentary gesture,
//! and who it is attending to. It keeps a little memory (last positions and
//! headings, running conversations) so behaviour is continuous rather than
//! snapped. These are plain Rust types on purpose: the current web viewer reads
//! them as JSON today, and the future Bevy client will read the same types.

use std::collections::BTreeMap;

use crate::sim::social::seed_hash;
use crate::sim::wildlife::{Act, Animal};
use crate::sim::resident::Status;
use crate::sim::Simulation;
use crate::view::layout;

/// What an entity's body is doing.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Pose {
    Walk,
    Stand,
    Work,
    Talk,
    Sit,
    Lie,
    Sniff,
    Play,
    Perch,
    Forage,
    Groom,
    Alert,
}

impl Pose {
    pub fn tag(&self) -> &'static str {
        match self {
            Pose::Walk => "walk",
            Pose::Stand => "stand",
            Pose::Work => "work",
            Pose::Talk => "talk",
            Pose::Sit => "sit",
            Pose::Lie => "lie",
            Pose::Sniff => "sniff",
            Pose::Play => "play",
            Pose::Perch => "perch",
            Pose::Forage => "forage",
            Pose::Groom => "groom",
            Pose::Alert => "alert",
        }
    }
}

/// A momentary expressive beat layered over a pose.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Gesture {
    None,
    Gesture,
    Laugh,
    Wave,
    Nod,
    Glance,
    Point,
}

impl Gesture {
    pub fn tag(&self) -> &'static str {
        match self {
            Gesture::None => "none",
            Gesture::Gesture => "gesture",
            Gesture::Laugh => "laugh",
            Gesture::Wave => "wave",
            Gesture::Nod => "nod",
            Gesture::Glance => "glance",
            Gesture::Point => "point",
        }
    }
}

/// One entity's observable behaviour at an instant — everything the renderer
/// needs to draw it as a living thing.
#[derive(Debug, Clone)]
pub struct Behaviour {
    pub id: &'static str,
    pub x: f64,
    pub y: f64,
    /// Facing direction, radians (atan2(dy, dx) in screen space).
    pub heading: f64,
    /// Movement this tick, 0..1 (drives the walk cadence).
    pub speed: f64,
    pub pose: Pose,
    pub gesture: Gesture,
    /// Who they are attending to (a conversation partner, the dog to the child).
    pub partner: Option<&'static str>,
    pub moving: bool,
    /// Progress through a bounded state (a conversation), 0..1. 0 when not in one.
    /// Lets the renderer play a beginning, a middle and an end.
    pub phase: f64,
}

/// A running conversation between two residents — held for a short window so it
/// can be *watched*: they face each other, gesture, laugh, then part.
#[derive(Debug, Clone)]
struct Convo {
    a: &'static str,
    b: &'static str,
    started: u64,
    ends: u64,
}

/// How long a conversation is staged for (ticks; 1 tick = 5 min).
const CONVO_TICKS: u64 = 4;

/// The choreographer: stateful translator from simulation to behaviour.
#[derive(Debug, Default)]
pub struct Choreographer {
    last_pos: BTreeMap<&'static str, (f64, f64)>,
    heading: BTreeMap<&'static str, f64>,
    convos: Vec<Convo>,
    seen_interactions: usize,
    frame: Vec<Behaviour>,
}

impl Choreographer {
    pub fn new() -> Self {
        Choreographer::default()
    }

    /// The current behaviour frame (one entry per visible entity).
    pub fn frame(&self) -> &[Behaviour] {
        &self.frame
    }

    /// Observe the world after a tick and update the behaviour frame.
    pub fn observe(&mut self, sim: &Simulation) {
        let tick = sim.clock.tick;

        // --- positions of every visible entity this tick ---
        // A settled entity drifts to a nearby point of interest (a bench, the shade
        // under the stadium's east wing) so a place is inhabited at fine grain,
        // not a stack of dots. Travellers keep their on-edge position.
        let day = sim.clock.day();
        let mut pos: BTreeMap<&'static str, (f64, f64)> = BTreeMap::new();
        let mut moving: BTreeMap<&'static str, bool> = BTreeMap::new();
        for r in &sim.residents {
            let p = layout::entity_pos(&sim.world, r.place, &r.status);
            let mv = matches!(r.status, Status::Traveling { .. });
            pos.insert(r.id, settled_xy(r.id, r.place, mv, day, p.x(), p.y()));
            moving.insert(r.id, mv);
        }
        {
            let p = layout::entity_pos(&sim.world, sim.dog.place, &Status::Idle);
            pos.insert("the_old_dog", settled_xy("the_old_dog", sim.dog.place, false, day, p.x(), p.y()));
            moving.insert("the_old_dog", false);
        }
        for a in &sim.wildlife.animals {
            let (xy, mv) = animal_xy(a);
            pos.insert(a.id, settled_xy(a.id, a.place, mv, day, xy.0, xy.1));
            moving.insert(a.id, mv);
        }

        // --- pick up newly-decided conversations and stage them ---
        if sim.interactions.len() > self.seen_interactions {
            for it in &sim.interactions[self.seen_interactions..] {
                self.convos.push(Convo {
                    a: it.a,
                    b: it.b,
                    started: it.tick,
                    ends: it.tick + CONVO_TICKS,
                });
            }
            self.seen_interactions = sim.interactions.len();
        }
        // Expire conversations that have run their course or whose partners parted.
        let here = |id: &str| sim.residents.iter().find(|r| r.id == id).map(|r| r.place);
        self.convos.retain(|c| {
            tick <= c.ends && here(c.a).is_some() && here(c.a) == here(c.b)
        });
        let convo_of = |id: &'static str| -> Option<&Convo> {
            self.convos.iter().find(|c| c.a == id || c.b == id)
        };

        // --- build the behaviour for every entity ---
        let mut frame: Vec<Behaviour> = Vec::with_capacity(pos.len());
        for (&id, &(x, y)) in &pos {
            let mv = *moving.get(id).unwrap_or(&false);
            // heading + speed from motion; keep last heading when still.
            let (last_x, last_y) = *self.last_pos.get(id).unwrap_or(&(x, y));
            let (dx, dy) = (x - last_x, y - last_y);
            let dist = (dx * dx + dy * dy).sqrt();
            let mut heading = *self.heading.get(id).unwrap_or(&0.0);
            if dist > 0.5 {
                heading = dy.atan2(dx);
            }
            let speed = (dist / 40.0).clamp(0.0, 1.0);

            // pose + gesture + partner, and progress through a bounded state
            let cv = convo_of(id);
            let (pose, gesture, partner, face) = self.pose_of(sim, id, &pos, tick, day, mv, cv);
            let phase = cv
                .map(|c| {
                    let span = c.ends.saturating_sub(c.started).max(1) as f64;
                    ((tick.saturating_sub(c.started)) as f64 / span).clamp(0.0, 1.0)
                })
                .unwrap_or(0.0);
            if let Some(h) = face {
                heading = h;
            }
            self.heading.insert(id, heading);
            frame.push(Behaviour { id, x, y, heading, speed, pose, gesture, partner, moving: mv, phase });
        }

        self.last_pos = pos;
        self.frame = frame;
    }

    /// Decide an entity's pose, gesture, who it faces, and an optional forced
    /// heading (e.g. toward a conversation partner).
    fn pose_of(
        &self,
        sim: &Simulation,
        id: &'static str,
        pos: &BTreeMap<&'static str, (f64, f64)>,
        tick: u64,
        day: u64,
        moving: bool,
        convo: Option<&Convo>,
    ) -> (Pose, Gesture, Option<&'static str>, Option<f64>) {
        use crate::world::poi::Posture;
        // A conversation overrides everything: turn to face the partner and talk.
        if let Some(c) = convo {
            let partner = if c.a == id { c.b } else { c.a };
            let face = pos.get(partner).and_then(|&(px, py)| {
                pos.get(id).map(|&(x, y)| (py - y).atan2(px - x))
            });
            // seeded expressive beat, varying through the conversation
            let g = match seed_hash(&[id, partner, "beat"], tick) % 100 {
                0..=17 => Gesture::Laugh,
                18..=55 => Gesture::Gesture,
                56..=70 => Gesture::Nod,
                71..=82 => Gesture::Glance,
                _ => Gesture::None,
            };
            return (Pose::Talk, g, Some(partner), face);
        }

        // Residents.
        if let Some(r) = sim.residents.iter().find(|r| r.id == id) {
            if moving {
                return (Pose::Walk, Gesture::None, None, None);
            }
            let aff = match &r.status {
                Status::Performing { activity, .. } => r.affordance_of(activity),
                _ => None,
            };
            let mut pose = match aff {
                Some(a) if a.starts_with("WORK") || a == "KIOSK" || a == "MARKET" || a == "BUSK" => Pose::Work,
                Some("SIT_BENCH") => Pose::Sit,
                Some("GATHER") | Some("SCHOOL") if r.is_child() => Pose::Play,
                _ => Pose::Stand,
            };
            // If they're just standing about, the spot they drifted to shapes what
            // they do there — sit on the bench, play by the tree.
            if pose == Pose::Stand {
                if let Some(post) = crate::world::poi::assign(id, r.place, day).map(|p| p.posture()) {
                    pose = match post {
                        Posture::Sit => Pose::Sit,
                        Posture::Play if r.is_child() => Pose::Play,
                        _ => Pose::Stand,
                    };
                }
            }
            // an idle glance now and then, so standing isn't frozen
            let g = if pose == Pose::Stand && seed_hash(&[id, "idle"], tick) % 100 < 12 {
                Gesture::Glance
            } else {
                Gesture::None
            };
            return (pose, g, None, None);
        }

        // The old dog: walking, or resting (lie / sniff / a look about).
        if id == "the_old_dog" {
            if moving {
                return (Pose::Walk, Gesture::None, None, None);
            }
            // The spot he's settled at shapes his rest: deep shade or a den is for
            // napping (the east wing of the stadium), a rail is for watching.
            match crate::world::poi::assign(id, sim.dog.place, day).map(|p| p.posture()) {
                Some(Posture::Rest) => return (Pose::Lie, Gesture::None, None, None),
                Some(Posture::Watch) => return (Pose::Alert, Gesture::Glance, None, None),
                _ => {}
            }
            let (pose, g) = match seed_hash(&["dog", "rest"], tick) % 100 {
                0..=54 => (Pose::Lie, Gesture::None),
                55..=79 => (Pose::Sniff, Gesture::None),
                _ => (Pose::Stand, Gesture::Glance),
            };
            return (pose, g, None, None);
        }

        // Animals: pose from their current activity.
        if let Some(a) = sim.wildlife.animals.iter().find(|a| a.id == id) {
            let pose = match a.act {
                Act::Roam | Act::Hunt | Act::Flee => Pose::Walk,
                Act::Forage => Pose::Forage,
                Act::Perch => Pose::Perch,
                Act::Rest => Pose::Lie,
                Act::Watch => Pose::Alert,
                Act::Call => Pose::Alert,
                Act::Groom => Pose::Groom,
                Act::Play => Pose::Play,
            };
            return (pose, Gesture::None, None, None);
        }

        (Pose::Stand, Gesture::None, None, None)
    }
}

/// A settled entity drifts to a nearby point of interest, so a place reads as
/// inhabited at fine grain rather than a stack of figures on one node. Travellers
/// keep their on-edge position. Deterministic (seeded by id + place + day).
fn settled_xy(id: &str, place: &str, moving: bool, day: u64, bx: f64, by: f64) -> (f64, f64) {
    if moving {
        return (bx, by);
    }
    match crate::world::poi::assign(id, place, day) {
        Some(p) => {
            let (px, py) = p.xy();
            let (jx, jy) = jitter(id);
            (px + jx, py + jy)
        }
        None => (bx, by),
    }
}

/// A tiny stable per-id offset (a few px) so two figures sharing a spot don't sit
/// perfectly on top of each other.
fn jitter(id: &str) -> (f64, f64) {
    let mut h: u32 = 2166136261;
    for b in id.bytes() {
        h ^= b as u32;
        h = h.wrapping_mul(16777619);
    }
    let a = (h % 360) as f64 * std::f64::consts::PI / 180.0;
    let r = 4.0 + (h / 360 % 6) as f64;
    (a.cos() * r, a.sin() * r)
}

/// An animal's screen position, and whether it is moving.
fn animal_xy(a: &Animal) -> ((f64, f64), bool) {
    if let Some(t) = a.trip {
        let frac = if t.total == 0 { 0.0 } else { (t.total - t.left) as f64 / t.total as f64 };
        if let (Some((fx, fy)), Some((tx, ty))) = (layout::node_xy(t.from), layout::node_xy(t.to)) {
            return ((fx + (tx - fx) * frac, fy + (ty - fy) * frac), true);
        }
    }
    let (x, y) = layout::node_xy(a.place).unwrap_or((500.0, 380.0));
    ((x, y), false)
}

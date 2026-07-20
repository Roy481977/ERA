//! ERA — the district (Bevy). Behaviour, not art.
//!
//! Two modes share one behavioural grammar:
//!  * the **district** (default) — every figure is driven by the real simulation.
//!  * the **behaviour test lab** (open with `?test` in the URL) — a deterministic
//!    gallery of interaction types (a conversation, a passing glance, strangers who
//!    don't interact, a kid and a dog, a cat and a dog, a flock feeding and
//!    scattering), so we can watch and tune the grammar without waiting for the
//!    right moment to emerge. Nothing in the lab touches the simulation.
//!
//! The grammar is a small set of *intents* (go, idle, talk, approach, flee, circle,
//! watch, glance, feed) that the steering turns into living movement: accelerate,
//! face before walking, arrive softly, keep spacing, converge and part. The library
//! is meant to grow — adding an interaction is adding a scenario, not new plumbing.

use std::collections::HashMap;
use std::f32::consts::{PI, TAU};

use bevy::core_pipeline::tonemapping::Tonemapping;
use bevy::input::mouse::{MouseMotion, MouseWheel};
use bevy::prelude::*;

use era_first_breath::engine::Engine;

const SCALE: f32 = 0.06;
const TICK_SECS: f32 = 0.9;
const CONV_DIST: f32 = 1.6;
const SLOW_RADIUS: f32 = 2.6;
const STOP_RADIUS: f32 = 0.14;
const SEP_RADIUS: f32 = 1.3;

fn main() {
    #[cfg(target_arch = "wasm32")]
    console_error_panic_hook::set_once();

    App::new()
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "ERA — the district".into(),
                canvas: Some("#era-canvas".into()),
                fit_canvas_to_parent: true,
                prevent_default_event_handling: false,
                ..default()
            }),
            ..default()
        }))
        .insert_resource(ClearColor(Color::srgb(0.04, 0.05, 0.07)))
        .insert_resource(AmbientLight { color: Color::srgb(0.7, 0.78, 0.9), brightness: 260.0 })
        .insert_resource(detect_mode())
        .insert_resource(Sim::new())
        .insert_resource(Figures::default())
        .insert_resource(Crowd::default())
        .insert_resource(Rig::default())
        .insert_resource(Lab::default())
        .insert_resource(Caption::default())
        .add_systems(Startup, setup)
        .add_systems(Update, (tick_engine, spawn_figures, district_intents).chain().run_if(is_district))
        .add_systems(Update, test_runner.run_if(is_test))
        .add_systems(Update, (steer_figures, camera_control, sun_cycle, update_label))
        .run();
}

#[derive(Resource, Clone, Copy, PartialEq, Eq)]
enum Mode {
    District,
    Test,
}
fn is_district(m: Res<Mode>) -> bool { *m == Mode::District }
fn is_test(m: Res<Mode>) -> bool { *m == Mode::Test }

fn detect_mode() -> Mode {
    #[cfg(target_arch = "wasm32")]
    {
        if let Some(w) = web_sys::window() {
            if let Ok(s) = w.location().search() {
                if s.contains("test") {
                    return Mode::Test;
                }
            }
        }
    }
    Mode::District
}

// ----------------------------------------------------------------- the grammar

#[derive(Clone, Copy, PartialEq, Eq)]
enum IKind {
    Go,
    Idle,
    Talk,
    Approach,
    Flee,
    Circle,
    Watch,
    Glance,
    Feed,
}

/// What a figure currently intends. Set by the sim (district) or a scenario (lab);
/// the steering turns it into believable motion.
#[derive(Component, Clone)]
struct Intent {
    kind: IKind,
    goal: Vec3,
    other: Option<&'static str>,
    param: f32,
    y: f32,
}
impl Default for Intent {
    fn default() -> Self {
        Intent { kind: IKind::Idle, goal: Vec3::ZERO, other: None, param: 0.0, y: 0.0 }
    }
}
fn go(g: Vec3) -> Intent { Intent { kind: IKind::Go, goal: g, ..default() } }
fn idle_y(y: f32) -> Intent { Intent { kind: IKind::Idle, y, ..default() } }
fn talk(o: &'static str) -> Intent { Intent { kind: IKind::Talk, other: Some(o), ..default() } }
fn watch(o: &'static str) -> Intent { Intent { kind: IKind::Watch, other: Some(o), ..default() } }
fn approach(o: &'static str, d: f32) -> Intent { Intent { kind: IKind::Approach, other: Some(o), param: d, ..default() } }
fn flee(o: &'static str) -> Intent { Intent { kind: IKind::Flee, other: Some(o), ..default() } }
fn circle(o: &'static str, r: f32) -> Intent { Intent { kind: IKind::Circle, other: Some(o), param: r, ..default() } }
fn glance(g: Vec3, o: &'static str) -> Intent { Intent { kind: IKind::Glance, goal: g, other: Some(o), ..default() } }
fn feed() -> Intent { Intent { kind: IKind::Feed, ..default() } }

// ----------------------------------------------------------------- resources

#[derive(Clone)]
struct Snap {
    id: &'static str,
    pos: Vec3,
    pose: &'static str,
    color: Color,
    kind: &'static str,
    partner: Option<&'static str>,
}

#[derive(Resource)]
struct Sim {
    engine: Engine,
    acc: f32,
    from: Vec<Snap>,
    to: Vec<Snap>,
    hour: f32,
}
impl Sim {
    fn new() -> Self {
        let engine = Engine::new();
        let frame = read(&engine);
        let hour = engine.hour() as f32;
        Sim { engine, acc: 0.0, from: frame.clone(), to: frame, hour }
    }
}

#[derive(Resource, Default)]
struct Figures(HashMap<&'static str, Entity>);
#[derive(Resource, Default)]
struct Crowd(HashMap<&'static str, Vec3>);
#[derive(Resource, Default)]
struct Caption {
    title: String,
    step: String,
}

#[derive(Resource)]
struct Lab {
    index: usize,
    elapsed: f32,
    dirty: bool,
    actors: HashMap<&'static str, Entity>,
}
impl Default for Lab {
    fn default() -> Self {
        Lab { index: 0, elapsed: 0.0, dirty: true, actors: HashMap::new() }
    }
}

#[derive(Resource)]
struct Rig {
    focus: Vec3,
    yaw: f32,
    pitch: f32,
    dist: f32,
    follow: Option<&'static str>,
}
impl Default for Rig {
    fn default() -> Self {
        Rig { focus: Vec3::ZERO, yaw: 0.7, pitch: 0.5, dist: 16.0, follow: None }
    }
}

#[derive(Resource)]
struct Kit {
    body: Handle<Mesh>,
    head: Handle<Mesh>,
    small: Handle<Mesh>,
    bird: Handle<Mesh>,
    nose: Handle<Mesh>,
}

#[derive(Component)]
struct Figure {
    id: &'static str,
}

#[derive(Component)]
struct Mover {
    pos: Vec3,
    vel: Vec3,
    facing: f32,
    max_speed: f32,
    accel: f32,
    turn_rate: f32,
    personal: f32,
    hesitation: f32,
    drift: f32,
    seed: f32,
    hesitate: f32,
    watch: f32,
    last_partner: Option<&'static str>,
    was_moving: bool,
}

#[derive(Component)]
struct MainCamera;
#[derive(Component)]
struct Sun;

// --------------------------------------------------------------- sim <-> world

fn world_pos(x: f64, y: f64) -> Vec3 {
    Vec3::new((x as f32 - 500.0) * SCALE, 0.0, (y as f32 - 380.0) * SCALE)
}

fn read(engine: &Engine) -> Vec<Snap> {
    engine
        .snapshot()
        .entities
        .iter()
        .map(|e| Snap { id: e.id, pos: world_pos(e.x, e.y), pose: e.pose, color: hex(e.color), kind: e.kind, partner: e.partner })
        .collect()
}

fn hex(s: &str) -> Color {
    let s = s.trim_start_matches('#');
    let n = u32::from_str_radix(s, 16).unwrap_or(0x888888);
    Color::srgb(((n >> 16) & 0xff) as f32 / 255.0, ((n >> 8) & 0xff) as f32 / 255.0, (n & 0xff) as f32 / 255.0)
}

fn seedf(s: &str) -> f32 {
    let mut h: u32 = 0;
    for b in s.bytes() {
        h = h.wrapping_mul(31).wrapping_add(b as u32);
    }
    (h % 1000) as f32 / 1000.0
}

fn turn_toward(cur: f32, target: f32, max: f32) -> f32 {
    let mut d = (target - cur) % TAU;
    if d > PI { d -= TAU; }
    if d < -PI { d += TAU; }
    if d.abs() <= max { target } else { cur + d.signum() * max }
}
fn ang_diff(a: f32, b: f32) -> f32 {
    let mut d = (b - a) % TAU;
    if d > PI { d -= TAU; }
    if d < -PI { d += TAU; }
    d.abs()
}
fn yaw_of(dir: Vec3) -> f32 {
    dir.x.atan2(dir.z)
}
fn v(x: f32, z: f32) -> Vec3 {
    Vec3::new(x, 0.0, z)
}

// -------------------------------------------------------------------- setup

fn setup(mode: Res<Mode>, mut commands: Commands, mut meshes: ResMut<Assets<Mesh>>, mut materials: ResMut<Assets<StandardMaterial>>) {
    commands.insert_resource(Kit {
        body: meshes.add(Capsule3d::new(0.3, 0.9)),
        head: meshes.add(Sphere::new(0.24)),
        small: meshes.add(Capsule3d::new(0.2, 0.4)),
        bird: meshes.add(Sphere::new(0.18)),
        nose: meshes.add(Sphere::new(0.09)),
    });

    commands.spawn((Camera3d::default(), Msaa::Off, Tonemapping::None, Transform::from_xyz(0.0, 12.0, 16.0).looking_at(Vec3::ZERO, Vec3::Y), MainCamera));
    commands.spawn((
        DirectionalLight { illuminance: 9000.0, color: Color::srgb(1.0, 0.96, 0.9), shadows_enabled: false, ..default() },
        Transform::from_rotation(Quat::from_euler(EulerRot::XYZ, -0.9, 0.4, 0.0)),
        Sun,
    ));
    let ground = materials.add(StandardMaterial { base_color: Color::srgb(0.13, 0.16, 0.15), perceptual_roughness: 1.0, ..default() });
    commands.spawn((Mesh3d(meshes.add(Cuboid::new(120.0, 0.2, 100.0))), MeshMaterial3d(ground), Transform::from_xyz(0.0, -0.11, 0.0)));

    // Place markers + the Old Oak belong to the living district only; the lab is a
    // clean stage.
    if *mode == Mode::District {
        let engine = Engine::new();
        for (id, x, y) in parse_locations(&engine.world_json()) {
            let home = id.contains("millers") || id.contains("oakside") || id.contains("high_street");
            let disc = materials.add(StandardMaterial {
                base_color: if id == "loc_main_square" { Color::srgb(0.3, 0.31, 0.34) } else if home { Color::srgb(0.18, 0.2, 0.24) } else { Color::srgb(0.24, 0.26, 0.3) },
                perceptual_roughness: 1.0,
                ..default()
            });
            commands.spawn((Mesh3d(meshes.add(Cylinder::new(if id == "loc_main_square" { 5.0 } else { 3.0 }, 0.12))), MeshMaterial3d(disc), Transform::from_translation(world_pos(x, y) + Vec3::new(0.0, 0.02, 0.0))));
            if id == "loc_riverside" {
                let trunk = materials.add(StandardMaterial { base_color: Color::srgb(0.32, 0.22, 0.14), ..default() });
                let leaf = materials.add(StandardMaterial { base_color: Color::srgb(0.2, 0.4, 0.22), ..default() });
                let base = world_pos(x, y);
                commands.spawn((Mesh3d(meshes.add(Cylinder::new(0.4, 4.0))), MeshMaterial3d(trunk), Transform::from_translation(base + Vec3::new(1.5, 2.0, 1.0))));
                commands.spawn((Mesh3d(meshes.add(Sphere::new(2.6))), MeshMaterial3d(leaf), Transform::from_translation(base + Vec3::new(1.5, 4.4, 1.0))));
            }
        }
    }
}

// -------------------------------------------------------------- spawning figures

fn personality(id: &str, kind: &str) -> Mover {
    let sd = seedf(id);
    let (base, acc, turn, personal, hes) = match kind {
        "resident" => {
            let child = id == "res_tomas";
            let elder = matches!(id, "res_victor" | "res_agnes" | "res_elias" | "res_hana");
            if child { (3.9, 10.0, 9.0, 1.0, 0.10) } else if elder { (2.2, 4.5, 4.5, 1.1, 0.40) } else { (2.9, 6.5, 6.0, 1.0, 0.28) }
        }
        "dog" => (1.7, 4.0, 5.0, 0.7, 0.25),
        "cat" => (3.2, 9.0, 10.0, 0.5, 0.12),
        "crow" | "owl" | "heron" | "bird" => (3.0, 12.0, 12.0, 0.4, 0.05),
        _ => (2.4, 6.0, 6.0, 0.7, 0.25),
    };
    Mover {
        pos: Vec3::ZERO,
        vel: Vec3::ZERO,
        facing: sd * TAU,
        max_speed: base + sd * 0.5,
        accel: acc + sd * 2.0,
        turn_rate: turn + sd * 2.0,
        personal: personal + sd * 0.2,
        hesitation: hes + sd * 0.12,
        drift: 0.16 + sd * 0.22,
        seed: sd,
        hesitate: 0.0,
        watch: 0.0,
        last_partner: None,
        was_moving: false,
    }
}

fn spawn_actor(commands: &mut Commands, kit: &Kit, materials: &mut Assets<StandardMaterial>, id: &'static str, kind: &'static str, color: Color, pos: Vec3) -> Entity {
    let mut mv = personality(id, kind);
    mv.pos = pos;
    let (body, ry, headed) = match kind {
        "resident" => (kit.body.clone(), 0.85, true),
        "crow" | "owl" | "heron" | "bird" => (kit.bird.clone(), 0.3, false),
        _ => (kit.small.clone(), 0.35, false),
    };
    let mat = materials.add(StandardMaterial { base_color: color, perceptual_roughness: 0.85, ..default() });
    let nose = materials.add(StandardMaterial { base_color: Color::srgb(0.95, 0.95, 0.92), ..default() });
    commands
        .spawn((Transform::from_translation(pos), Visibility::default(), Figure { id }, mv, Intent::default()))
        .with_children(|p| {
            p.spawn((Mesh3d(body), MeshMaterial3d(mat.clone()), Transform::from_xyz(0.0, ry, 0.0)));
            if headed {
                p.spawn((Mesh3d(kit.head.clone()), MeshMaterial3d(mat.clone()), Transform::from_xyz(0.0, ry + 0.75, 0.0)));
            }
            p.spawn((Mesh3d(kit.nose.clone()), MeshMaterial3d(nose), Transform::from_xyz(0.0, if headed { ry + 0.75 } else { ry }, 0.28)));
        })
        .id()
}

// ------------------------------------------------------------- district (real)

fn tick_engine(mut sim: ResMut<Sim>, time: Res<Time>) {
    sim.acc += time.delta_secs();
    let mut guard = 0;
    while sim.acc >= TICK_SECS && guard < 8 {
        sim.engine.tick();
        sim.from = std::mem::take(&mut sim.to);
        sim.to = read(&sim.engine);
        sim.hour = sim.engine.hour() as f32;
        sim.acc -= TICK_SECS;
        guard += 1;
    }
}

fn spawn_figures(mut commands: Commands, mut figures: ResMut<Figures>, sim: Res<Sim>, kit: Res<Kit>, mut materials: ResMut<Assets<StandardMaterial>>) {
    for s in &sim.to {
        if figures.0.contains_key(s.id) {
            continue;
        }
        let e = spawn_actor(&mut commands, &kit, &mut materials, s.id, s.kind, s.color, s.pos);
        figures.0.insert(s.id, e);
    }
}

fn district_intents(sim: Res<Sim>, mut caption: ResMut<Caption>, mut q: Query<(&Figure, &mut Intent)>) {
    let t = (sim.acc / TICK_SECS).clamp(0.0, 1.0);
    let fromm: HashMap<&'static str, &Snap> = sim.from.iter().map(|s| (s.id, s)).collect();
    let mut gh: HashMap<&'static str, (Vec3, &'static str, Option<&'static str>)> = HashMap::new();
    for s in &sim.to {
        let f = fromm.get(s.id).copied().unwrap_or(s);
        gh.insert(s.id, (f.pos.lerp(s.pos, t), s.pose, s.partner));
    }
    for (fig, mut intent) in &mut q {
        if let Some(&(pos, pose, partner)) = gh.get(fig.id) {
            *intent = if pose == "talk" && partner.map(|p| gh.contains_key(p)).unwrap_or(false) {
                talk(partner.unwrap())
            } else {
                let mut i = go(pos);
                i.y = pose_y(pose);
                i
            };
        }
    }
    if caption.title.is_empty() {
        caption.title = "The living district".into();
        caption.step = "everything here comes from the real simulation".into();
    }
}

// ------------------------------------------------------------- the test lab

fn test_runner(
    mut commands: Commands,
    mut lab: ResMut<Lab>,
    time: Res<Time>,
    keys: Res<ButtonInput<KeyCode>>,
    kit: Res<Kit>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    crowd: Res<Crowd>,
    mut caption: ResMut<Caption>,
    mut rig: ResMut<Rig>,
    mut intents: Query<&mut Intent>,
) {
    let n = scenario_count();
    if keys.just_pressed(KeyCode::KeyN) || keys.just_pressed(KeyCode::Space) {
        lab.index = (lab.index + 1) % n;
        lab.dirty = true;
    }
    if keys.just_pressed(KeyCode::KeyP) {
        lab.index = (lab.index + n - 1) % n;
        lab.dirty = true;
    }
    if keys.just_pressed(KeyCode::KeyR) {
        lab.dirty = true;
    }

    if lab.dirty {
        let old: Vec<Entity> = lab.actors.values().copied().collect();
        for e in old {
            commands.entity(e).despawn_recursive();
        }
        lab.actors.clear();
        lab.elapsed = 0.0;
        lab.dirty = false;
        for (id, kind, color, start) in scenario_actors(lab.index) {
            let e = spawn_actor(&mut commands, &kit, &mut materials, id, kind, color, start);
            lab.actors.insert(id, e);
        }
        rig.focus = Vec3::ZERO;
        rig.follow = None;
        let (title, _) = scenario_meta(lab.index);
        caption.title = format!("Behaviour lab {}/{} — {}", lab.index + 1, n, title);
        caption.step = "…".into();
        return; // actors spawn this frame; drive them next
    }

    lab.elapsed += time.delta_secs();
    let dur = scenario_duration(lab.index);
    if lab.elapsed > dur {
        lab.elapsed = 0.0;
    }

    let (assignments, step) = scenario_step(lab.index, lab.elapsed, &crowd.0);
    for (id, intent) in assignments {
        if let Some(&e) = lab.actors.get(id) {
            if let Ok(mut it) = intents.get_mut(e) {
                *it = intent;
            }
        }
    }
    let (title, _) = scenario_meta(lab.index);
    caption.title = format!("Behaviour lab {}/{} — {}", lab.index + 1, n, title);
    caption.step = step.into();
}

// ------------------------------------------------------------- the scenarios

fn scenario_count() -> usize { 6 }

fn scenario_meta(i: usize) -> (&'static str, &'static str) {
    match i {
        0 => ("a conversation", "two who know each other meet, talk, and part"),
        1 => ("a passing glance", "acquaintances cross paths and simply look"),
        2 => ("strangers pass", "no bond, no interaction — they just make way"),
        3 => ("a kid and a dog", "the boy comes over; the dog gets up to play"),
        4 => ("a cat and a dog", "the dog is curious; the cat keeps its distance"),
        _ => ("the flock", "birds land and feed, and scatter when someone crosses"),
    }
}
fn scenario_duration(i: usize) -> f32 {
    match i {
        0 => 20.0,
        1 => 11.0,
        2 => 11.0,
        3 => 17.0,
        4 => 13.0,
        _ => 12.0,
    }
}

const C_BLUE: Color = Color::srgb(0.24, 0.52, 0.66);
const C_GREEN: Color = Color::srgb(0.31, 0.62, 0.41);
const C_WARM: Color = Color::srgb(0.88, 0.55, 0.35);
const C_DOG: Color = Color::srgb(0.55, 0.4, 0.25);
const C_CAT: Color = Color::srgb(0.3, 0.3, 0.33);
const C_BIRD: Color = Color::srgb(0.18, 0.18, 0.2);

fn scenario_actors(i: usize) -> Vec<(&'static str, &'static str, Color, Vec3)> {
    match i {
        0 => vec![("A", "resident", C_BLUE, v(-9.0, -1.0)), ("B", "resident", C_GREEN, v(9.0, 1.0))],
        1 => vec![("A", "resident", C_BLUE, v(-9.0, -2.0)), ("B", "resident", C_WARM, v(9.0, 2.0))],
        2 => vec![("A", "resident", C_BLUE, v(-9.0, -2.0)), ("B", "resident", C_GREEN, v(9.0, 2.0))],
        3 => vec![("kid", "resident", C_GREEN, v(-7.0, 3.0)), ("dog", "dog", C_DOG, v(4.0, -2.0))],
        4 => vec![("cat", "cat", C_CAT, v(-5.0, 0.0)), ("dog", "dog", C_DOG, v(6.0, 0.5))],
        _ => vec![
            ("person", "resident", C_BLUE, v(-11.0, 0.0)),
            ("b0", "bird", C_BIRD, v(-2.0, -6.0)),
            ("b1", "bird", C_BIRD, v(2.0, -6.5)),
            ("b2", "bird", C_BIRD, v(-1.0, -7.0)),
            ("b3", "bird", C_BIRD, v(3.0, -6.0)),
            ("b4", "bird", C_BIRD, v(0.0, -7.5)),
        ],
    }
}

fn dist2(a: Vec3, b: Vec3) -> f32 {
    (a - b).length()
}

/// The heart of the library: each scenario composes the grammar over time. Returns
/// the intent for every actor plus a short label describing the moment.
fn scenario_step(i: usize, t: f32, pos: &HashMap<&'static str, Vec3>) -> (Vec<(&'static str, Intent)>, &'static str) {
    let get = |id: &str| pos.get(id).copied().unwrap_or(Vec3::ZERO);
    match i {
        // ---- 0: a full conversation ----
        0 => {
            if t < 1.6 {
                (vec![("A", idle_y(0.0)), ("B", idle_y(0.0))], "standing in the square")
            } else if t < 2.9 {
                (vec![("A", watch("B")), ("B", watch("A"))], "they notice one another · orient")
            } else if t < 11.0 {
                let close = dist2(get("A"), get("B")) < CONV_DIST + 0.8;
                (vec![("A", talk("B")), ("B", talk("A"))], if close { "in conversation" } else { "converging" })
            } else if t < 15.0 {
                (vec![("A", go(v(-13.0, -1.0))), ("B", watch("A"))], "A takes their leave · B watches them go")
            } else if t < 16.6 {
                (vec![("B", idle_y(0.0))], "a pause")
            } else {
                (vec![("B", go(v(13.0, 1.0)))], "back to the day")
            }
        }
        // ---- 1: a passing glance (acquaintances) ----
        1 => {
            let ga = v(9.0, -2.0);
            let gb = v(-9.0, 2.0);
            let near = dist2(get("A"), get("B")) < 4.5;
            (
                vec![("A", if near { glance(ga, "B") } else { go(ga) }), ("B", if near { glance(gb, "A") } else { go(gb) })],
                if near { "a glance as they pass" } else { "two acquaintances cross paths" },
            )
        }
        // ---- 2: strangers pass (the logic says: no interaction) ----
        2 => (
            vec![("A", go(v(9.0, 2.0))), ("B", go(v(-9.0, -2.0)))],
            "strangers — they yield, but do not interact",
        ),
        // ---- 3: a kid and a dog ----
        3 => {
            let d = dist2(get("kid"), get("dog"));
            if t < 1.6 {
                (vec![("kid", idle_y(0.0)), ("dog", idle_y(-0.5))], "the dog dozes in the sun")
            } else if t < 4.5 {
                let up = d < 4.0;
                (vec![("kid", approach("dog", 1.3)), ("dog", if up { watch("kid") } else { idle_y(-0.5) })], "the boy comes over · the dog looks up")
            } else if t < 9.0 {
                (vec![("kid", watch("dog")), ("dog", circle("kid", 1.7))], "they play")
            } else if t < 11.0 {
                (vec![("kid", idle_y(-0.45)), ("dog", approach("kid", 0.8))], "the boy crouches to say hello")
            } else if t < 14.0 {
                (vec![("kid", go(v(-11.0, 3.0))), ("dog", watch("kid"))], "the boy heads off · the dog watches")
            } else {
                (vec![("dog", idle_y(-0.5))], "the dog settles again")
            }
        }
        // ---- 4: a cat and a dog ----
        4 => {
            if t < 1.6 {
                (vec![("cat", idle_y(0.0)), ("dog", idle_y(0.0))], "a cat on the square")
            } else if t < 3.2 {
                (vec![("dog", approach("cat", 1.4)), ("cat", watch("dog"))], "the dog notices · the cat holds still")
            } else if t < 7.0 {
                (vec![("cat", flee("dog")), ("dog", approach("cat", 1.2))], "the cat slips away · the dog follows")
            } else if t < 9.0 {
                (vec![("dog", idle_y(0.0)), ("cat", watch("dog"))], "the dog loses interest")
            } else {
                (vec![("cat", idle_y(0.0)), ("dog", idle_y(0.0))], "a wary distance is kept")
            }
        }
        // ---- 5: the flock ----
        _ => {
            let spots = [v(-2.0, 0.0), v(1.5, -0.5), v(-0.5, 1.5), v(2.5, 1.0), v(0.0, -1.5)];
            let birds = ["b0", "b1", "b2", "b3", "b4"];
            let person = get("person");
            let scared = |bi: usize| dist2(get(birds[bi]), person) < 3.2;
            if t < 2.0 {
                let mut a: Vec<(&'static str, Intent)> = birds.iter().enumerate().map(|(k, b)| (*b, go(spots[k]))).collect();
                a.push(("person", idle_y(0.0)));
                (a, "the flock comes down")
            } else if t < 6.0 {
                let mut a: Vec<(&'static str, Intent)> = birds.iter().map(|b| (*b, feed())).collect();
                a.push(("person", idle_y(0.0)));
                (a, "feeding")
            } else if t < 9.5 {
                let mut a: Vec<(&'static str, Intent)> = birds
                    .iter()
                    .enumerate()
                    .map(|(k, b)| (*b, if scared(k) { flee("person") } else { feed() }))
                    .collect();
                a.push(("person", go(v(11.0, 0.0))));
                (a, "someone crosses — they scatter")
            } else {
                let mut a: Vec<(&'static str, Intent)> = birds.iter().enumerate().map(|(k, b)| (*b, go(spots[k]))).collect();
                a.push(("person", idle_y(0.0)));
                (a, "and they settle again")
            }
        }
    }
}

// -------------------------------------------------------------- steering (shared)

fn steer_figures(time: Res<Time>, mut crowd: ResMut<Crowd>, mut q: Query<(&Figure, &Intent, &mut Transform, &mut Mover)>) {
    let dt = time.delta_secs().min(0.05);
    let now = time.elapsed_secs();
    let neighbors = crowd.0.clone();
    let mut newpos: HashMap<&'static str, Vec3> = HashMap::new();

    for (fig, intent, mut tr, mut mv) in &mut q {
        let opos = intent.other.and_then(|o| neighbors.get(o).copied());

        // resolve the intent into a goal, an optional thing to face, and extras
        let (goal, face_target, base_y, is_convo) = match intent.kind {
            IKind::Go => (intent.goal, None, intent.y, false),
            IKind::Idle => (mv.pos, None, intent.y, false),
            IKind::Watch => (mv.pos, opos, intent.y, false),
            IKind::Talk => {
                let g = opos.map(|op| op + (mv.pos - op).normalize_or_zero() * CONV_DIST).unwrap_or(mv.pos);
                (g, opos, 0.0, true)
            }
            IKind::Approach => {
                let g = opos.map(|op| op + (mv.pos - op).normalize_or_zero() * intent.param.max(0.4)).unwrap_or(intent.goal);
                (g, opos, intent.y, false)
            }
            IKind::Flee => {
                let g = opos.map(|op| mv.pos + (mv.pos - op).normalize_or_zero() * 7.0).unwrap_or(mv.pos);
                (g, None, 0.0, false)
            }
            IKind::Circle => {
                if let Some(op) = opos {
                    let a = now * 1.5 + mv.seed * 6.28;
                    (op + v(a.cos(), a.sin()) * intent.param.max(1.0), Some(op), 0.0, false)
                } else {
                    (mv.pos, None, 0.0, false)
                }
            }
            IKind::Glance => {
                let face = opos.filter(|op| (*op - mv.pos).length() < 4.5);
                (intent.goal, face, 0.0, false)
            }
            IKind::Feed => (mv.pos, None, -0.1 - (now * 6.0 + mv.seed * 10.0).sin().abs() * 0.16, false),
        };

        // ---- arrive ----
        let mut to_goal = goal - mv.pos; to_goal.y = 0.0;
        let dist = to_goal.length();
        let dir = if dist > 0.001 { to_goal / dist } else { Vec3::ZERO };
        let mut desired_speed = if dist < STOP_RADIUS { 0.0 } else if dist < SLOW_RADIUS { mv.max_speed * (dist / SLOW_RADIUS) } else { mv.max_speed };

        if !mv.was_moving && desired_speed > 0.1 && dist > SLOW_RADIUS && mv.hesitate <= 0.0 && mv.watch <= 0.0 {
            mv.hesitate = mv.hesitation;
        }
        if mv.hesitate > 0.0 { mv.hesitate -= dt; desired_speed *= 0.10; }

        // face the thing (partner / travel), turn at a limited rate, don't stride
        // until roughly aligned
        let target_facing = if let Some(fp) = face_target {
            let mut d = fp - mv.pos; d.y = 0.0;
            if d.length() > 0.05 { yaw_of(d) } else { mv.facing }
        } else if desired_speed > 0.05 {
            yaw_of(dir)
        } else {
            mv.facing
        };
        mv.facing = turn_toward(mv.facing, target_facing, mv.turn_rate * dt);
        if desired_speed > 0.05 && face_target.is_none() {
            let mis = ang_diff(mv.facing, target_facing);
            if mis > 0.8 { desired_speed *= 0.12; } else if mis > 0.35 { desired_speed *= 0.5; }
        }

        // separation (spacing / yielding)
        let mut sep = Vec3::ZERO;
        for (oid, op) in &neighbors {
            if *oid == fig.id { continue; }
            let mut d = mv.pos - *op; d.y = 0.0;
            let l = d.length();
            let range = if is_convo { mv.personal * 0.55 } else { mv.personal.max(0.55) + 0.2 };
            if l > 0.001 && l < range.min(SEP_RADIUS) {
                sep += (d / l) * (1.0 - l / range);
            }
        }

        let mut desired_vel = dir * desired_speed + sep * mv.max_speed * 0.7;
        if desired_speed > 0.6 && !is_convo {
            let perp = v(-dir.z, dir.x);
            desired_vel += perp * (mv.drift * (mv.seed * 6.28 + now * 1.3).sin());
        }
        if desired_vel.length() > mv.max_speed {
            desired_vel = desired_vel.normalize() * mv.max_speed;
        }

        let mut dv = desired_vel - mv.vel; dv.y = 0.0;
        let dvl = dv.length();
        let maxdv = mv.accel * dt;
        if dvl > maxdv { dv = dv / dvl * maxdv; }
        mv.vel += dv;
        if mv.vel.length() < 0.03 { mv.vel = Vec3::ZERO; }
        let step = mv.vel * dt;
        mv.pos += step;
        mv.pos.y = 0.0;
        mv.was_moving = mv.vel.length() > 0.35;

        // watching someone leave after a conversation
        if mv.last_partner.is_some() && !is_convo && matches!(intent.kind, IKind::Idle) && mv.watch <= 0.0 {
            mv.watch = 2.4;
        }
        if is_convo { mv.last_partner = intent.other; }
        if mv.watch > 0.0 && !is_convo {
            mv.watch -= dt;
            if let Some(lp) = mv.last_partner {
                if let Some(&lpp) = neighbors.get(lp) {
                    let mut d = lpp - mv.pos; d.y = 0.0;
                    if d.length() > 0.1 { mv.facing = turn_toward(mv.facing, yaw_of(d), mv.turn_rate * dt * 0.6); }
                }
            }
            if mv.watch <= 0.0 { mv.last_partner = None; }
        }

        // subtle life
        let mut y = base_y;
        if is_convo {
            mv.facing += (now * 1.7 + mv.seed * 9.0).sin() * 0.02;
            y += (now * 1.1 + mv.seed * 4.0).sin().max(0.0) * 0.03;
        } else if mv.vel.length() < 0.12 && mv.watch <= 0.0 {
            mv.facing += (now * 0.5 + mv.seed * 6.0).sin() * 0.004;
        } else {
            y += (mv.vel.length() / mv.max_speed) * (now * 9.0 + mv.seed * 6.0).sin().abs() * 0.05;
        }

        tr.translation = Vec3::new(mv.pos.x, y, mv.pos.z);
        tr.rotation = Quat::from_rotation_y(mv.facing);
        newpos.insert(fig.id, mv.pos);
    }

    crowd.0 = newpos;
}

fn pose_y(pose: &str) -> f32 {
    match pose {
        "sit" => -0.28,
        "lie" => -0.55,
        _ => 0.0,
    }
}

// ---------------------------------------------------------------- camera & sky

fn camera_control(
    mode: Res<Mode>,
    mut rig: ResMut<Rig>,
    sim: Res<Sim>,
    keys: Res<ButtonInput<KeyCode>>,
    mouse: Res<ButtonInput<MouseButton>>,
    mut motion: EventReader<MouseMotion>,
    mut wheel: EventReader<MouseWheel>,
    time: Res<Time>,
    mut cam: Query<&mut Transform, With<MainCamera>>,
) {
    if mouse.pressed(MouseButton::Left) || mouse.pressed(MouseButton::Right) {
        for m in motion.read() {
            rig.yaw -= m.delta.x * 0.006;
            rig.pitch = (rig.pitch - m.delta.y * 0.006).clamp(0.12, 1.45);
        }
    } else {
        motion.clear();
    }
    for w in wheel.read() {
        rig.dist = (rig.dist - w.y * 1.6).clamp(4.0, 80.0);
    }
    let dt = time.delta_secs();
    let speed = rig.dist * 0.9 * dt;
    let fwd = Vec3::new(rig.yaw.sin(), 0.0, rig.yaw.cos());
    let right = Vec3::new(fwd.z, 0.0, -fwd.x);
    let mut pan = Vec3::ZERO;
    if keys.pressed(KeyCode::KeyW) || keys.pressed(KeyCode::ArrowUp) { pan -= fwd; }
    if keys.pressed(KeyCode::KeyS) || keys.pressed(KeyCode::ArrowDown) { pan += fwd; }
    if keys.pressed(KeyCode::KeyA) || keys.pressed(KeyCode::ArrowLeft) { pan -= right; }
    if keys.pressed(KeyCode::KeyD) || keys.pressed(KeyCode::ArrowRight) { pan += right; }
    if pan != Vec3::ZERO { rig.follow = None; rig.focus += pan.normalize() * speed * 10.0; }

    // follow only in the district (Tab cycles residents)
    if *mode == Mode::District {
        if keys.just_pressed(KeyCode::Escape) { rig.follow = None; }
        if keys.just_pressed(KeyCode::Tab) {
            let residents: Vec<&'static str> = sim.to.iter().filter(|s| s.kind == "resident").map(|s| s.id).collect();
            rig.follow = match rig.follow {
                None => residents.first().copied(),
                Some(cur) => {
                    let i = residents.iter().position(|&r| r == cur).map(|i| i + 1).unwrap_or(0);
                    residents.get(i % residents.len().max(1)).copied()
                }
            };
            if rig.follow.is_some() { rig.dist = rig.dist.min(12.0); }
        }
        if let Some(id) = rig.follow {
            if let Some(s) = sim.to.iter().find(|s| s.id == id) {
                rig.focus = rig.focus.lerp(s.pos, 0.08);
            }
        }
    }

    let dir = Vec3::new(rig.pitch.cos() * rig.yaw.sin(), rig.pitch.sin(), rig.pitch.cos() * rig.yaw.cos());
    if let Ok(mut trc) = cam.get_single_mut() {
        let eye = rig.focus + dir * rig.dist;
        *trc = Transform::from_translation(eye).looking_at(rig.focus + Vec3::new(0.0, 1.0, 0.0), Vec3::Y);
    }
}

fn sun_cycle(mode: Res<Mode>, sim: Res<Sim>, mut ambient: ResMut<AmbientLight>, mut q: Query<(&mut Transform, &mut DirectionalLight), With<Sun>>) {
    // the lab is always in clear daylight; the district follows the sim clock
    let h = if *mode == Mode::Test { 13.0 } else { sim.hour };
    let daylight = (((h - 6.0) / 12.0 * PI).sin()).clamp(-1.0, 1.0).max(0.0);
    if let Ok((mut tr, mut light)) = q.get_single_mut() {
        tr.rotation = Quat::from_euler(EulerRot::XYZ, -(daylight * 1.1 + 0.15), 0.5, 0.0);
        light.illuminance = 1500.0 + daylight * 9000.0;
        light.color = Color::srgb(1.0, 0.85 + daylight * 0.12, 0.7 + daylight * 0.25);
    }
    ambient.brightness = 110.0 + daylight * 260.0;
    ambient.color = Color::srgb(0.5 + daylight * 0.35, 0.55 + daylight * 0.32, 0.75);
}

// ---------------------------------------------------------------- label overlay

#[cfg(target_arch = "wasm32")]
fn update_label(cap: Res<Caption>) {
    if !cap.is_changed() {
        return;
    }
    if let Some(doc) = web_sys::window().and_then(|w| w.document()) {
        if let Some(el) = doc.get_element_by_id("label") {
            el.set_inner_html(&format!("<b>{}</b><br><span class=\"step\">{}</span>", cap.title, cap.step));
        }
    }
}
#[cfg(not(target_arch = "wasm32"))]
fn update_label(_cap: Res<Caption>) {}

// ------------------------------------------------------------------- helpers

fn parse_locations(world_json: &str) -> Vec<(&'static str, f64, f64)> {
    const IDS: &[&str] = &[
        "loc_stadium", "loc_school", "loc_museum", "loc_bakery", "loc_main_square", "loc_cafe",
        "loc_pub", "loc_bridge", "loc_riverside", "loc_millers_row", "loc_high_street", "loc_oakside",
    ];
    let mut out = Vec::new();
    for &id in IDS {
        if let Some(p) = world_json.find(&format!("\"id\":\"{id}\"")) {
            let tail = &world_json[p..];
            if let (Some(x), Some(y)) = (json_num(tail, "\"x\":"), json_num(tail, "\"y\":")) {
                out.push((id, x, y));
            }
        }
    }
    out
}
fn json_num(s: &str, key: &str) -> Option<f64> {
    let i = s.find(key)? + key.len();
    let rest = &s[i..];
    let end = rest.find(|c: char| c != '-' && c != '.' && !c.is_ascii_digit()).unwrap_or(rest.len());
    rest[..end].parse().ok()
}

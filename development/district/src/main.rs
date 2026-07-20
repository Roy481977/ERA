//! ERA — the district (Bevy). A visualisation of the living world, driven entirely
//! by the simulation's behaviour stream. The engine is the source of truth: it
//! ticks, and this app reads its per-entity behaviour each frame and moves real
//! figures accordingly, interpolating so nothing snaps between positions.
//!
//! This is the first vertical slice — the square and the Old Oak, residents, the
//! dog and animals, a free camera you can move and use to follow someone, and a
//! day/night sun. Simple shapes on purpose; the point is readable body language,
//! spacing, movement and continuity, not polish.

use std::collections::HashMap;

use bevy::core_pipeline::tonemapping::Tonemapping;
use bevy::input::mouse::{MouseMotion, MouseWheel};
use bevy::prelude::*;

use era_first_breath::engine::Engine;

/// Sim map space (~1000 x 760) → metres in the 3D world.
const SCALE: f32 = 0.06;
/// Real seconds per simulation tick (a tick = five minutes).
const TICK_SECS: f32 = 0.8;

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
        .insert_resource(AmbientLight { color: Color::srgb(0.7, 0.78, 0.9), brightness: 220.0 })
        .insert_resource(Sim::new())
        .insert_resource(Figures::default())
        .insert_resource(Rig::default())
        .add_systems(Startup, setup)
        .add_systems(Update, (tick_engine, sync_figures, camera_control, sun_cycle))
        .run();
}

// ----------------------------------------------------------------- resources

/// One entity's visible state this tick, in world space.
#[derive(Clone)]
struct Snap {
    id: &'static str,
    pos: Vec3,
    heading: f32,
    pose: &'static str,
    color: Color,
    kind: &'static str,
}

/// The simulation, ticking, with the previous and current behaviour frames to
/// interpolate between for continuity.
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

/// id -> the Bevy entity that represents it.
#[derive(Resource, Default)]
struct Figures(HashMap<&'static str, Entity>);

/// The orbit/follow camera.
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
        Rig { focus: Vec3::ZERO, yaw: 0.7, pitch: 0.62, dist: 34.0, follow: None }
    }
}

/// Shared mesh handles.
#[derive(Resource)]
struct Kit {
    body: Handle<Mesh>,
    small: Handle<Mesh>,
    bird: Handle<Mesh>,
    nose: Handle<Mesh>,
}

#[derive(Component)]
struct Figure {
    id: &'static str,
}

#[derive(Component)]
struct MainCamera;

#[derive(Component)]
struct Sun;

// --------------------------------------------------------------- sim <-> world

fn world_pos(x: f64, y: f64, pose: &str) -> Vec3 {
    let base = match pose {
        "sit" => 0.35,
        "lie" => 0.15,
        _ => 0.0,
    };
    Vec3::new((x as f32 - 500.0) * SCALE, base, (y as f32 - 380.0) * SCALE)
}

fn read(engine: &Engine) -> Vec<Snap> {
    engine
        .snapshot()
        .entities
        .iter()
        .map(|e| Snap {
            id: e.id,
            pos: world_pos(e.x, e.y, e.pose),
            // sim heading is atan2(dy,dx) in screen space; map to a Y-rotation.
            heading: -(e.heading as f32),
            pose: e.pose,
            color: hex(e.color),
            kind: e.kind,
        })
        .collect()
}

fn hex(s: &str) -> Color {
    let s = s.trim_start_matches('#');
    let n = u32::from_str_radix(s, 16).unwrap_or(0x888888);
    Color::srgb(
        ((n >> 16) & 0xff) as f32 / 255.0,
        ((n >> 8) & 0xff) as f32 / 255.0,
        (n & 0xff) as f32 / 255.0,
    )
}

fn lerp_angle(a: f32, b: f32, t: f32) -> f32 {
    let mut d = (b - a) % std::f32::consts::TAU;
    if d > std::f32::consts::PI {
        d -= std::f32::consts::TAU;
    }
    if d < -std::f32::consts::PI {
        d += std::f32::consts::TAU;
    }
    a + d * t
}

// -------------------------------------------------------------------- systems

fn setup(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
) {
    // shared figure meshes
    let kit = Kit {
        body: meshes.add(Capsule3d::new(0.35, 1.1)),
        small: meshes.add(Capsule3d::new(0.22, 0.4)),
        bird: meshes.add(Sphere::new(0.2)),
        nose: meshes.add(Sphere::new(0.11)),
    };
    commands.insert_resource(kit);

    // camera
    commands.spawn((
        Camera3d::default(),
        Msaa::Off,
        Tonemapping::None,
        Transform::from_xyz(0.0, 24.0, 34.0).looking_at(Vec3::ZERO, Vec3::Y),
        MainCamera,
    ));

    // the sun
    commands.spawn((
        DirectionalLight { illuminance: 9000.0, color: Color::srgb(1.0, 0.96, 0.9), shadows_enabled: false, ..default() },
        Transform::from_rotation(Quat::from_euler(EulerRot::XYZ, -0.9, 0.4, 0.0)),
        Sun,
    ));

    // ground
    let ground_mat = materials.add(StandardMaterial {
        base_color: Color::srgb(0.13, 0.16, 0.15),
        perceptual_roughness: 1.0,
        ..default()
    });
    commands.spawn((
        Mesh3d(meshes.add(Cuboid::new(120.0, 0.2, 100.0))),
        MeshMaterial3d(ground_mat),
        Transform::from_xyz(0.0, -0.1, 0.0),
    ));

    // place markers (a disc per location; the square lighter, homes darker), and a
    // simple tree for the Old Oak at the riverside.
    let engine = Engine::new();
    let world = engine.world_json();
    for (id, x, y) in parse_locations(&world) {
        let home = id.contains("millers") || id.contains("oakside") || id.contains("high_street");
        let disc = materials.add(StandardMaterial {
            base_color: if id == "loc_main_square" { Color::srgb(0.3, 0.31, 0.34) }
                        else if home { Color::srgb(0.18, 0.2, 0.24) }
                        else { Color::srgb(0.24, 0.26, 0.3) },
            perceptual_roughness: 1.0,
            ..default()
        });
        commands.spawn((
            Mesh3d(meshes.add(Cylinder::new(if id == "loc_main_square" { 5.0 } else { 3.0 }, 0.12))),
            MeshMaterial3d(disc),
            Transform::from_translation(world_pos(x, y, "") + Vec3::new(0.0, 0.02, 0.0)),
        ));
        if id == "loc_riverside" {
            let trunk = materials.add(StandardMaterial { base_color: Color::srgb(0.32, 0.22, 0.14), ..default() });
            let leaf = materials.add(StandardMaterial { base_color: Color::srgb(0.2, 0.4, 0.22), ..default() });
            let base = world_pos(x, y, "");
            commands.spawn((Mesh3d(meshes.add(Cylinder::new(0.4, 4.0))), MeshMaterial3d(trunk), Transform::from_translation(base + Vec3::new(1.5, 2.0, 1.0))));
            commands.spawn((Mesh3d(meshes.add(Sphere::new(2.6))), MeshMaterial3d(leaf), Transform::from_translation(base + Vec3::new(1.5, 4.4, 1.0))));
        }
    }
}

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

fn sync_figures(
    mut commands: Commands,
    mut figures: ResMut<Figures>,
    sim: Res<Sim>,
    kit: Res<Kit>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    mut q: Query<&mut Transform, With<Figure>>,
) {
    let t = (sim.acc / TICK_SECS).clamp(0.0, 1.0);
    let from: HashMap<&'static str, &Snap> = sim.from.iter().map(|s| (s.id, s)).collect();

    for s in &sim.to {
        let f = from.get(s.id).copied().unwrap_or(s);
        let pos = f.pos.lerp(s.pos, t);
        let heading = lerp_angle(f.heading, s.heading, t);
        let rot = Quat::from_rotation_y(heading);

        if let Some(&ent) = figures.0.get(s.id) {
            if let Ok(mut tr) = q.get_mut(ent) {
                tr.translation = pos;
                tr.rotation = rot;
            }
        } else {
            // spawn a figure: a body plus a small "nose" so its facing reads
            let (body, ry, nose_y, nose_z) = match s.kind {
                "resident" => (kit.body.clone(), 0.9, 1.4, 0.4),
                "dog" => (kit.small.clone(), 0.35, 0.45, 0.35),
                "crow" | "owl" | "heron" => (kit.bird.clone(), 0.3, 0.32, 0.22),
                _ => (kit.small.clone(), 0.35, 0.45, 0.3),
            };
            let mat = materials.add(StandardMaterial { base_color: s.color, perceptual_roughness: 0.8, ..default() });
            let nose_mat = materials.add(StandardMaterial { base_color: Color::srgb(0.95, 0.95, 0.95), ..default() });
            let ent = commands
                .spawn((Transform::from_translation(pos).with_rotation(rot), Visibility::default(), Figure { id: s.id }))
                .with_children(|p| {
                    p.spawn((Mesh3d(body), MeshMaterial3d(mat), Transform::from_xyz(0.0, ry, 0.0)));
                    p.spawn((Mesh3d(kit.nose.clone()), MeshMaterial3d(nose_mat), Transform::from_xyz(0.0, nose_y, nose_z)));
                })
                .id();
            figures.0.insert(s.id, ent);
        }
    }
}

fn camera_control(
    mut rig: ResMut<Rig>,
    sim: Res<Sim>,
    keys: Res<ButtonInput<KeyCode>>,
    mouse: Res<ButtonInput<MouseButton>>,
    mut motion: EventReader<MouseMotion>,
    mut wheel: EventReader<MouseWheel>,
    time: Res<Time>,
    mut cam: Query<&mut Transform, With<MainCamera>>,
) {
    // rotate with a held mouse button
    if mouse.pressed(MouseButton::Left) || mouse.pressed(MouseButton::Right) {
        for m in motion.read() {
            rig.yaw -= m.delta.x * 0.006;
            rig.pitch = (rig.pitch - m.delta.y * 0.006).clamp(0.12, 1.45);
        }
    } else {
        motion.clear();
    }
    // zoom with the wheel
    for w in wheel.read() {
        rig.dist = (rig.dist - w.y * 2.0).clamp(6.0, 90.0);
    }
    // pan the focus with WASD / arrows (relative to view)
    let dt = time.delta_secs();
    let speed = rig.dist * 0.6 * dt;
    let fwd = Vec3::new(rig.yaw.sin(), 0.0, rig.yaw.cos());
    let right = Vec3::new(fwd.z, 0.0, -fwd.x);
    let mut pan = Vec3::ZERO;
    if keys.pressed(KeyCode::KeyW) || keys.pressed(KeyCode::ArrowUp) { pan -= fwd; }
    if keys.pressed(KeyCode::KeyS) || keys.pressed(KeyCode::ArrowDown) { pan += fwd; }
    if keys.pressed(KeyCode::KeyA) || keys.pressed(KeyCode::ArrowLeft) { pan -= right; }
    if keys.pressed(KeyCode::KeyD) || keys.pressed(KeyCode::ArrowRight) { pan += right; }
    if pan != Vec3::ZERO { rig.follow = None; rig.focus += pan.normalize() * speed * 12.0; }

    // follow: Tab cycles through the residents, Esc releases
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
    }
    if let Some(id) = rig.follow {
        if let Some(s) = sim.to.iter().find(|s| s.id == id) {
            rig.focus = rig.focus.lerp(s.pos, 0.1);
            rig.dist = rig.dist.min(18.0).max(rig.dist * 0.98).max(8.0);
        }
    }

    // place the camera on its orbit
    let dir = Vec3::new(
        rig.pitch.cos() * rig.yaw.sin(),
        rig.pitch.sin(),
        rig.pitch.cos() * rig.yaw.cos(),
    );
    if let Ok(mut tr) = cam.get_single_mut() {
        let eye = rig.focus + dir * rig.dist;
        *tr = Transform::from_translation(eye).looking_at(rig.focus + Vec3::new(0.0, 1.0, 0.0), Vec3::Y);
    }
}

/// The sun arcs across the day and the light warms/cools; night is dim and blue,
/// so the small hours read as night — with the animals still abroad.
fn sun_cycle(
    sim: Res<Sim>,
    mut ambient: ResMut<AmbientLight>,
    mut q: Query<(&mut Transform, &mut DirectionalLight), With<Sun>>,
) {
    let h = sim.hour; // 0..24
    let day = ((h - 6.0) / 12.0 * std::f32::consts::PI).sin().clamp(-1.0, 1.0); // -1 night .. 1 midday
    let daylight = day.max(0.0);
    if let Ok((mut tr, mut light)) = q.get_single_mut() {
        let angle = (h / 24.0) * std::f32::consts::TAU - std::f32::consts::FRAC_PI_2;
        *tr = Transform::from_rotation(Quat::from_euler(EulerRot::XYZ, -angle.sin().abs().max(0.15) - 0.2, 0.5, 0.0));
        light.illuminance = 1500.0 + daylight * 9000.0;
        light.color = Color::srgb(1.0, 0.85 + daylight * 0.12, 0.7 + daylight * 0.25);
    }
    ambient.brightness = 90.0 + daylight * 260.0;
    ambient.color = Color::srgb(0.5 + daylight * 0.35, 0.55 + daylight * 0.32, 0.75);
}

// ------------------------------------------------------------------- helpers

/// Pull location coordinates out of the engine's world JSON (id, x, y).
fn parse_locations(world_json: &str) -> Vec<(&'static str, f64, f64)> {
    // The ids are a known, fixed set; match them to their coordinates in the JSON.
    const IDS: &[&str] = &[
        "loc_stadium", "loc_school", "loc_museum", "loc_bakery", "loc_main_square", "loc_cafe",
        "loc_pub", "loc_bridge", "loc_riverside", "loc_millers_row", "loc_high_street", "loc_oakside",
    ];
    let mut out = Vec::new();
    for &id in IDS {
        if let Some(pos) = world_json.find(&format!("\"id\":\"{id}\"")) {
            let tail = &world_json[pos..];
            let x = json_num(tail, "\"x\":");
            let y = json_num(tail, "\"y\":");
            if let (Some(x), Some(y)) = (x, y) {
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

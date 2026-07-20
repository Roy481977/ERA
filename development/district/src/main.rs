//! ERA — the district (Bevy). Behaviour, not art.
//!
//! The simulation is the source of truth: it says who intends to go where, and who
//! is in conversation with whom. This app's job is to make the figures *move like
//! living things* — accelerate and slow, turn to face a destination before
//! walking, keep comfortable spacing, drift a little off the straight line,
//! hesitate before setting off, each with their own pace and temperament — and to
//! stage conversations that converge, hold a believable distance, orient, and part
//! naturally. The measure of success is simple: you can watch in silence and
//! understand what is happening. The shapes stay primitive on purpose.

use std::collections::HashMap;
use std::f32::consts::{PI, TAU};

use bevy::core_pipeline::tonemapping::Tonemapping;
use bevy::input::mouse::{MouseMotion, MouseWheel};
use bevy::prelude::*;

use era_first_breath::engine::Engine;

const SCALE: f32 = 0.06; // sim map units -> metres
const TICK_SECS: f32 = 0.9; // real seconds per five-minute tick
const CONV_DIST: f32 = 1.6; // how far apart two people stand to talk
const SLOW_RADIUS: f32 = 2.6; // begin decelerating within this of the goal
const STOP_RADIUS: f32 = 0.14;
const SEP_RADIUS: f32 = 1.3; // personal-space repulsion range

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
        .insert_resource(Crowd::default())
        .insert_resource(Rig::default())
        .add_systems(Startup, setup)
        .add_systems(Update, (tick_engine, spawn_figures, steer_figures, camera_control, sun_cycle).chain())
        .run();
}

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

/// Last-frame positions, so figures can keep their distance from one another.
#[derive(Resource, Default)]
struct Crowd(HashMap<&'static str, Vec3>);

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
        Rig { focus: Vec3::ZERO, yaw: 0.7, pitch: 0.5, dist: 22.0, follow: None }
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

/// A figure's continuous motion state — this is where "alive" lives.
#[derive(Component)]
struct Mover {
    pos: Vec3,
    vel: Vec3,
    facing: f32,
    // temperament (fixed per figure)
    max_speed: f32,
    accel: f32,
    turn_rate: f32,
    personal: f32,
    hesitation: f32,
    drift: f32,
    seed: f32,
    // transient
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
        .map(|e| Snap {
            id: e.id,
            pos: world_pos(e.x, e.y),
            pose: e.pose,
            color: hex(e.color),
            kind: e.kind,
            partner: e.partner,
        })
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

/// Turn `cur` toward `target` by at most `max` radians (shortest way).
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

/// yaw so that the figure's forward (+Z) points along `dir` (on the ground plane).
fn yaw_of(dir: Vec3) -> f32 {
    dir.x.atan2(dir.z)
}

// -------------------------------------------------------------------- systems

fn setup(mut commands: Commands, mut meshes: ResMut<Assets<Mesh>>, mut materials: ResMut<Assets<StandardMaterial>>) {
    commands.insert_resource(Kit {
        body: meshes.add(Capsule3d::new(0.3, 0.9)),
        head: meshes.add(Sphere::new(0.24)),
        small: meshes.add(Capsule3d::new(0.2, 0.4)),
        bird: meshes.add(Sphere::new(0.18)),
        nose: meshes.add(Sphere::new(0.09)),
    });

    commands.spawn((
        Camera3d::default(),
        Msaa::Off,
        Tonemapping::None,
        Transform::from_xyz(0.0, 16.0, 22.0).looking_at(Vec3::ZERO, Vec3::Y),
        MainCamera,
    ));

    commands.spawn((
        DirectionalLight { illuminance: 9000.0, color: Color::srgb(1.0, 0.96, 0.9), shadows_enabled: false, ..default() },
        Transform::from_rotation(Quat::from_euler(EulerRot::XYZ, -0.9, 0.4, 0.0)),
        Sun,
    ));

    let ground = materials.add(StandardMaterial { base_color: Color::srgb(0.13, 0.16, 0.15), perceptual_roughness: 1.0, ..default() });
    commands.spawn((Mesh3d(meshes.add(Cuboid::new(120.0, 0.2, 100.0))), MeshMaterial3d(ground), Transform::from_xyz(0.0, -0.11, 0.0)));

    let engine = Engine::new();
    for (id, x, y) in parse_locations(&engine.world_json()) {
        let home = id.contains("millers") || id.contains("oakside") || id.contains("high_street");
        let disc = materials.add(StandardMaterial {
            base_color: if id == "loc_main_square" { Color::srgb(0.3, 0.31, 0.34) } else if home { Color::srgb(0.18, 0.2, 0.24) } else { Color::srgb(0.24, 0.26, 0.3) },
            perceptual_roughness: 1.0,
            ..default()
        });
        commands.spawn((
            Mesh3d(meshes.add(Cylinder::new(if id == "loc_main_square" { 5.0 } else { 3.0 }, 0.12))),
            MeshMaterial3d(disc),
            Transform::from_translation(world_pos(x, y) + Vec3::new(0.0, 0.02, 0.0)),
        ));
        if id == "loc_riverside" {
            let trunk = materials.add(StandardMaterial { base_color: Color::srgb(0.32, 0.22, 0.14), ..default() });
            let leaf = materials.add(StandardMaterial { base_color: Color::srgb(0.2, 0.4, 0.22), ..default() });
            let base = world_pos(x, y);
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

fn spawn_figures(
    mut commands: Commands,
    mut figures: ResMut<Figures>,
    sim: Res<Sim>,
    kit: Res<Kit>,
    mut materials: ResMut<Assets<StandardMaterial>>,
) {
    for s in &sim.to {
        if figures.0.contains_key(s.id) {
            continue;
        }
        let child = s.id == "res_tomas";
        let elder = matches!(s.id, "res_victor" | "res_agnes" | "res_elias" | "res_hana");
        let sd = seedf(s.id);
        let (base, acc, turn, hes) = if child { (3.9, 10.0, 9.0, 0.10) } else if elder { (2.2, 4.5, 4.5, 0.40) } else { (2.9, 6.5, 6.0, 0.28) };
        let mover = Mover {
            pos: s.pos,
            vel: Vec3::ZERO,
            facing: sd * TAU,
            max_speed: base + sd * 0.6,
            accel: acc + sd * 2.0,
            turn_rate: turn + sd * 2.0,
            personal: if s.kind == "resident" { 1.0 + sd * 0.3 } else { 0.6 },
            hesitation: hes + sd * 0.15,
            drift: 0.18 + sd * 0.22,
            seed: sd,
            hesitate: 0.0,
            watch: 0.0,
            last_partner: None,
            was_moving: false,
        };

        let (body, ry, headed) = match s.kind {
            "resident" => (kit.body.clone(), 0.85, true),
            "dog" => (kit.small.clone(), 0.35, false),
            "crow" | "owl" | "heron" => (kit.bird.clone(), 0.3, false),
            _ => (kit.small.clone(), 0.35, false),
        };
        let mat = materials.add(StandardMaterial { base_color: s.color, perceptual_roughness: 0.85, ..default() });
        let ent = commands
            .spawn((Transform::from_translation(s.pos), Visibility::default(), Figure { id: s.id }, mover))
            .with_children(|p| {
                p.spawn((Mesh3d(body), MeshMaterial3d(mat.clone()), Transform::from_xyz(0.0, ry, 0.0)));
                if headed {
                    p.spawn((Mesh3d(kit.head.clone()), MeshMaterial3d(mat.clone()), Transform::from_xyz(0.0, ry + 0.75, 0.0)));
                }
                // a small pale nose so facing is unmistakable
                p.spawn((Mesh3d(kit.nose.clone()), MeshMaterial3d(materials.add(StandardMaterial { base_color: Color::srgb(0.95, 0.95, 0.92), ..default() })), Transform::from_xyz(0.0, if headed { ry + 0.75 } else { ry }, 0.28)));
            })
            .id();
        figures.0.insert(s.id, ent);
    }
}

/// The heart of it: steer every figure toward what the simulation intends, but do
/// it like a living body — accelerate, face, arrive, keep space, converse, part.
fn steer_figures(
    sim: Res<Sim>,
    time: Res<Time>,
    mut crowd: ResMut<Crowd>,
    mut q: Query<(&Figure, &mut Transform, &mut Mover)>,
) {
    let dt = time.delta_secs().min(0.05);
    let t = (sim.acc / TICK_SECS).clamp(0.0, 1.0);
    let now = time.elapsed_secs();

    // authoritative "ghost" per entity: where the sim says it is, whether it is
    // moving, its pose, and any conversation partner.
    let fromm: HashMap<&'static str, &Snap> = sim.from.iter().map(|s| (s.id, s)).collect();
    let mut gh: HashMap<&'static str, (Vec3, bool, &'static str, Option<&'static str>)> = HashMap::new();
    for s in &sim.to {
        let f = fromm.get(s.id).copied().unwrap_or(s);
        gh.insert(s.id, (f.pos.lerp(s.pos, t), (s.pos - f.pos).length() > 0.05, s.pose, s.partner));
    }

    let neighbors = crowd.0.clone();
    let mut newpos: HashMap<&'static str, Vec3> = HashMap::new();

    for (fig, mut tr, mut mv) in &mut q {
        let Some(&(gpos, _gmoving, pose, partner)) = gh.get(fig.id) else {
            newpos.insert(fig.id, mv.pos);
            continue;
        };

        // conversation? (both present and the sim staged it)
        let talk_partner = if pose == "talk" { partner.filter(|p| gh.contains_key(p)) } else { None };
        let (goal, face_target, in_convo) = if let Some(p) = talk_partner {
            let ppos = gh[p].0;
            let mid = (gpos + ppos) * 0.5;
            let mut axis = ppos - gpos; axis.y = 0.0;
            let axis = if axis.length() > 0.001 { axis.normalize() } else { Vec3::X };
            (mid - axis * (CONV_DIST * 0.5), Some(ppos), true)
        } else {
            (gpos, None, false)
        };

        // ---- arrive steering toward the goal ----
        let mut to_goal = goal - mv.pos; to_goal.y = 0.0;
        let dist = to_goal.length();
        let dir = if dist > 0.001 { to_goal / dist } else { Vec3::ZERO };
        let mut desired_speed = if dist < STOP_RADIUS { 0.0 } else if dist < SLOW_RADIUS { mv.max_speed * (dist / SLOW_RADIUS) } else { mv.max_speed };

        // hesitation: a beat before setting off from rest
        if !mv.was_moving && desired_speed > 0.1 && dist > SLOW_RADIUS && mv.hesitate <= 0.0 && mv.watch <= 0.0 {
            mv.hesitate = mv.hesitation;
        }
        if mv.hesitate > 0.0 { mv.hesitate -= dt; desired_speed *= 0.10; }

        // facing: toward the partner in a conversation, else toward travel; turn at
        // a limited rate so it reads as anticipation, and don't stride until roughly
        // aligned (face the destination before walking).
        let target_facing = if let Some(fp) = face_target {
            let mut d = fp - mv.pos; d.y = 0.0; yaw_of(d)
        } else if desired_speed > 0.05 {
            yaw_of(dir)
        } else {
            mv.facing
        };
        mv.facing = turn_toward(mv.facing, target_facing, mv.turn_rate * dt);
        if !in_convo && desired_speed > 0.05 {
            let mis = ang_diff(mv.facing, target_facing);
            if mis > 0.8 { desired_speed *= 0.12; } else if mis > 0.35 { desired_speed *= 0.5; }
        }

        // separation from neighbours (comfortable spacing, yielding on crossings)
        let mut sep = Vec3::ZERO;
        for (oid, opos) in &neighbors {
            if *oid == fig.id { continue; }
            let mut d = mv.pos - *opos; d.y = 0.0;
            let l = d.length();
            let range = if in_convo { mv.personal * 0.6 } else { mv.personal.max(0.6) + 0.2 };
            if l > 0.001 && l < range.min(SEP_RADIUS) {
                sep += (d / l) * (1.0 - l / range);
            }
        }

        // desired velocity, with a little perpendicular drift while travelling
        let mut desired_vel = dir * desired_speed + sep * mv.max_speed * 0.7;
        if desired_speed > 0.6 && !in_convo {
            let perp = Vec3::new(-dir.z, 0.0, dir.x);
            desired_vel += perp * (mv.drift * (mv.seed * 6.28 + now * 1.3).sin());
        }
        if desired_vel.length() > mv.max_speed { desired_vel = desired_vel.normalize() * mv.max_speed; }

        // accelerate toward desired velocity (no instant changes)
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

        // when a conversation ends, the one left behind watches the other go, then
        // gathers themselves before moving on.
        if mv.last_partner.is_some() && !in_convo && mv.watch <= 0.0 {
            mv.watch = 2.6;
        }
        if in_convo { mv.last_partner = partner; }
        if mv.watch > 0.0 && !in_convo {
            mv.watch -= dt;
            if let Some(lp) = mv.last_partner {
                if let Some(&(lpp, _, _, _)) = gh.get(lp) {
                    let mut d = lpp - mv.pos; d.y = 0.0;
                    if d.length() > 0.1 { mv.facing = turn_toward(mv.facing, yaw_of(d), mv.turn_rate * dt * 0.6); }
                }
            }
            if mv.watch <= 0.0 { mv.last_partner = None; }
        }

        // subtle life: talkers shift weight and glance; idlers sway a touch
        let mut y = pose_y(pose);
        if in_convo {
            mv.facing += (now * 1.7 + mv.seed * 9.0).sin() * 0.02;
            y += (now * 1.1 + mv.seed * 4.0).sin().max(0.0) * 0.03; // small posture shift
        } else if mv.vel.length() < 0.12 && mv.watch <= 0.0 {
            mv.facing += (now * 0.5 + mv.seed * 6.0).sin() * 0.004; // idle sway / looking about
        } else {
            // a gentle walking bob
            y += mv.vel.length().min(mv.max_speed) / mv.max_speed * (now * 9.0 + mv.seed * 6.0).sin().abs() * 0.05;
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

    let dir = Vec3::new(rig.pitch.cos() * rig.yaw.sin(), rig.pitch.sin(), rig.pitch.cos() * rig.yaw.cos());
    if let Ok(mut trc) = cam.get_single_mut() {
        let eye = rig.focus + dir * rig.dist;
        *trc = Transform::from_translation(eye).looking_at(rig.focus + Vec3::new(0.0, 1.0, 0.0), Vec3::Y);
    }
}

fn sun_cycle(sim: Res<Sim>, mut ambient: ResMut<AmbientLight>, mut q: Query<(&mut Transform, &mut DirectionalLight), With<Sun>>) {
    let h = sim.hour;
    let daylight = (((h - 6.0) / 12.0 * PI).sin()).clamp(-1.0, 1.0).max(0.0);
    if let Ok((mut tr, mut light)) = q.get_single_mut() {
        tr.rotation = Quat::from_euler(EulerRot::XYZ, -(daylight * 1.1 + 0.15), 0.5, 0.0);
        light.illuminance = 1500.0 + daylight * 9000.0;
        light.color = Color::srgb(1.0, 0.85 + daylight * 0.12, 0.7 + daylight * 0.25);
    }
    ambient.brightness = 90.0 + daylight * 260.0;
    ambient.color = Color::srgb(0.5 + daylight * 0.35, 0.55 + daylight * 0.32, 0.75);
}

// ------------------------------------------------------------------- helpers

fn parse_locations(world_json: &str) -> Vec<(&'static str, f64, f64)> {
    const IDS: &[&str] = &[
        "loc_stadium", "loc_school", "loc_museum", "loc_bakery", "loc_main_square", "loc_cafe",
        "loc_pub", "loc_bridge", "loc_riverside", "loc_millers_row", "loc_high_street", "loc_oakside",
    ];
    let mut out = Vec::new();
    for &id in IDS {
        if let Some(pos) = world_json.find(&format!("\"id\":\"{id}\"")) {
            let tail = &world_json[pos..];
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

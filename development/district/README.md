# ERA — the district (Bevy)

The primary, immersive view of ERA: a Bevy application that **visualises the
simulation's behaviour stream**. The engine (`era_first_breath`) is the source of
truth — it ticks, and this app reads each entity's behaviour every frame and moves
real figures accordingly, interpolating so nothing snaps between positions. Bevy
never scripts scenes of its own; it draws what the world is doing.

Compiles to native (for development, with compiler verification) **and to
WebAssembly**, so it runs in the browser at the same hosted URL — no install, no
terminal. This is the first vertical slice: the square and the Old Oak, residents,
the dog and animals, a free camera, and a day/night sun. Simple shapes on purpose;
the goal is readable movement, spacing and continuity, not polish.

## Controls

- **drag** to look around, **scroll** to zoom
- **WASD / arrows** to move through the district
- **Tab** to follow a resident (cycles), **Esc** to release

## Where it runs

Built and deployed by GitHub Actions on every push (see the Pages workflow):

- `https://roy481977.github.io/ERA/district/` — the district (this crate)
- `https://roy481977.github.io/ERA/` — the top-down client, kept as a debugging view

## Building locally (optional — CI does this)

```
# native (opens a window):
cargo run -p era_district   # from development/district

# web:
rustup target add wasm32-unknown-unknown
cargo install trunk
cd development/district && trunk serve --release   # then open the shown localhost URL
```

## Status / next

First slice: figures driven by the engine with smooth interpolation and facing, a
movable/follow camera, place markers, the Old Oak, day/night. Next: staged
conversations and gatherings in 3D, sitting/resting poses, richer animal behaviour,
and natural arrival/departure — all still driven by the behaviour stream.

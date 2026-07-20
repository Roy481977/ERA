# ERA — First Breath live viewer

A self-contained HTML/Canvas window that **observes the ERA engine**. The engine
(`src/engine/`) is a continuously-ticking world with persistent entities; at every
hour it reports a **live snapshot** of its state, and the viewer draws only what the
snapshot says: where each resident and the old dog are, how busy each place is, the
busiest gathering right now, activity callouts, the bonds forming between residents,
and the Old Oak. Click anyone to follow them; play/pause, speed, scrub.

The viewer holds **no simulation logic**. Every position, occupancy count and
callout is computed inside the engine, from authoritative state — "rendering is
driven from state" is true by construction (Book of ERA — *The Engine's Place*).

## Regenerate

```bash
cd development/sprint-1
./viewer/build.sh 7 era-first-breath-viewer.html   # 7 days
```

That runs `cargo run -- stream <days>` — which ticks a persistent `Engine` and
records the snapshot it reports each hour — then injects the result into
`viewer.template.html`, producing one self-contained file you can open in any
browser. `cargo run -- snapshot [ticks]` prints a single live snapshot to the
terminal (proof the world can be observed at any instant without replaying anything).

## Snapshot contract

The clock ticks every **5 minutes** (288 ticks/day), so a frame is one five-minute
instant.

```
{ world:  { locations, edges, entities:[{id,name,kind,color}] },   // static stage, sent once
  frames: [ { tick, day, hour, minute, weekday, phase,             // one live frame per tick
              entities:[{id, x, y, place, doing, moving}],         // lean: identity is in the roster
              occupancy:{place:count}, busiest, callouts,
              oak, events:[[who,text,kind]], bonds } ] }
```

Frames are deliberately lean: an entity's name/colour/kind live once in the static
`entities` roster, and each frame carries only what moves — screen coordinates
(`x,y`), current place, what they're doing, and whether they're in transit. The
renderer interpolates `x,y` between frames for smooth walking. Deterministic: same
engine → same snapshots → same week.

The viewer draws a live **"happening" bubble** (the most salient current beat, else
the busiest gathering, else a quiet line), an HH:MM clock, occupancy badges, the
busiest-place highlight, activity callouts, forming bonds, and a click-to-follow
panel — all from frame state.

## Note on "live"

Today the frames are produced by ticking the engine here and embedding the stream,
so the browser plays a faithful recording of a live run on a real-time clock. The
architecture (engine authoritative, snapshot as the sole interface, renderer purely
observing) is the same one a truly in-browser engine would use: the same Rust
engine compiled to WebAssembly would emit these identical snapshots and tick inside
the page. That step is a pending decision (see `development/DS-006`).

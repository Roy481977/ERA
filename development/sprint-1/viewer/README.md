# ERA — First Breath visual viewer

A self-contained HTML/Canvas viewer that **replays** the deterministic simulation:
a live map of the district with the residents and the old dog moving between
places, the day's light and two moons in the sky, the Old Oak accumulating
scarves/flowers on matchday, and an event ticker. Play/pause, speed, timeline scrub.

The viewer renders data only — it holds no game logic. The Rust core is the single
source of truth and emits a JSON trace; the viewer replays it. This keeps
presentation independent from the engine (Book of ERA — *The Engine's Place*).

## Regenerate

```bash
cd development/sprint-1
./viewer/build.sh 7 era-first-breath-viewer.html   # 7 days
```

That runs `cargo run -- trace <days>` (the trace emitter in `src/main.rs`) and
injects the JSON into `viewer.template.html`, producing one self-contained file you
can open in any browser.

## Trace format (per tick = 1 hour)

`{ locations, edges, entities, ticks:[{ d, wd, h, sc, bq, p:{id:{at|e,t}}, ev:[[who,msg]] }] }`
— positions are a node (`at`) or a fraction `t` along an `edge`, so the viewer can
draw true along-road movement. Deterministic: same seed → same trace → same week.

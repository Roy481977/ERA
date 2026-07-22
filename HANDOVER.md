# ERA — Session Handover (2026-07-22)

This doc is a complete handover so a **fresh chat in a fresh cloud container** can pick up ERA with zero loss. Read this first, top to bottom. Everything you need to reach the exact working state and continue is here.

Author: previous session (Claude). Owner/final authority: **Roy** (roy@rain.one).

---

## 0. TL;DR for the next chat — do this first

1. **Get the code.** GitHub `Roy481977/ERA` branch `blockout` may be stale. The true tip is commit **`0baa32b`** ("compositor: weather layer…"). To guarantee you have it:
   - `git clone https://github.com/Roy481977/ERA.git && cd ERA && git checkout blockout`
   - Check: `git log --oneline -1`. If it is **not** `0baa32b` (or later), apply the bundle stored in this project — see **§2.3**.
2. **You cannot `git push` from the cloud container.** The injected token is read-only. All pushes go through Roy on his machine via a bundle. See **§2**. Do not waste time retrying pushes — bundle + hand to Roy.
3. **Build sanity check:** `cd development/sprint-1 && /root/.cargo/bin/cargo build` (~11s native). wasm32 is blocked by the proxy — don't attempt it.
4. **Render/preview:** serve `web/` and open `compositor.html` (see **§4**). The living-plate compositor is the main deliverable.
5. **Where work was left:** the **weather visual layer** was just built and committed (`0baa32b`). It renders correctly under forced-wet frames but **the shipped replay is all-dry** — the last remaining weather step is generating a wet day into the replay. See **§6 (Weather)** and **§7**.

---

## 1. What ERA is (locked context)

ERA is Roy's deterministic **Rust "living world" football-town game**. The town is a pre-rendered AI **"plate"** (a clay-diorama, 2.5D, fixed-camera image, 1376×768). Residents, animals, and life are composited **on top** of that plate as a living layer, driven by a deterministic simulation.

**Locked creative decisions (do not relitigate):**
- **CD-008 (LOCKED): plate world.** The town is `plate-v1` — a fixed pre-rendered image. We do **not** render the town in 3D. Everything living is drawn over the plate. (`era/creative-decisions/CD-008-plate-world.md`)
- **CD-007: core language is Rust.** Deterministic sim.
- **Movement = continuous path network.** Roy explicitly **rejected** an A→B explicit-path model ("I don't want to define paths that may be detoured"). Instead: a **continuous network of paths**; where two networks intersect closely they are joined into one; the resident chooses the route but is **always on paths** (whichever paths fit that kind of being). Beings get **occluded** when they pass behind something between them and the camera.
- Roy is final authority on creative/visual calls. Claude is implementer/architect. When a visual is "off," Roy says so bluntly ("that's awful") — iterate, don't defend.

**Key project docs (in the claude.ai project, not on disk unless cloned):**
`era/BIBLE.md`, `era/VISION.md`, `era/creative-decisions/CD-008-plate-world.md`, `era/creative-decisions/CD-009-the-world-grows-itself.md`, `era/design/*`, `era/architecture/*`. Use `project_read` / `project_search` for these.

---

## 2. GIT — the recurring pain point, and the fix

### 2.1 The reality
- Remote: `origin = https://github.com/Roy481977/ERA.git`. Canonical branch `main`; working branch **`blockout`**.
- **The cloud container can FETCH but cannot PUSH.** The credential in the container (`proxy-injected`, and the env `GITHUB_TOKEN`/`GH_TOKEN`) is **read-only** — a real `git push` fails with *"Password authentication is not supported"* / *"Invalid username or token."* This is why previous handovers "lost" work: commits lived only in the container, never reached GitHub, and the container was later reclaimed.
- As of this handover, GitHub `blockout` was **46 commits behind** the container. Do not assume GitHub is current.

### 2.2 The reliable procedure — how Claude "commits and uploads"
Claude **can** commit locally and **package** the commits. Roy pushes them from his machine. The clean, copy-paste procedure (this is the "one prompt that works" Roy asked for):

**In the container (Claude does this):**
```bash
cd /home/claude/era_repo         # or wherever the repo is
git add -A
git commit -m "your message"     # commit as normal
git bundle create /tmp/era-blockout.bundle blockout
```
Then Claude delivers `/tmp/era-blockout.bundle` to Roy with `SendUserFile`.

**On Roy's machine (Roy does this — give him exactly these lines):**
```bash
cd ~/ERA
git fetch ~/Downloads/era-blockout.bundle blockout
git push origin FETCH_HEAD:refs/heads/blockout
```
Notes that were biting us before:
- Use a **full refname** on the push (`FETCH_HEAD:refs/heads/blockout`), not `FETCH_HEAD:blockout`.
- **No inline `#` comments** on the command lines — they get passed as args and error.
- If Roy's `~/ERA` is behind, the fetch+push still works because the bundle carries full history for `blockout`.

### 2.3 Fallback: reconstruct exact state inside a fresh container without Roy
This project stores a **base64-encoded incremental git bundle** so any new chat can reach the exact tip even if GitHub is stale and Roy hasn't pushed yet.
- Project doc: **`claude/handover/blockout-incremental-bundle.b64.txt`** (base64 of a bundle of `4d97812..0baa32b`, i.e. the 47 commits this session added on top of the last GitHub tip).
- To use it in a fresh container:
  ```bash
  # after: git clone … && git checkout blockout   (this puts you at 4d97812 if GitHub is stale)
  # write the b64 text (from project_read of the doc) to /tmp/inc.b64, then:
  base64 -d /tmp/inc.b64 > /tmp/inc.bundle
  git fetch /tmp/inc.bundle blockout
  git checkout FETCH_HEAD    # you are now at 0baa32b
  ```
- The base64 doc round-trips cleanly via `project_read` (verified). Delete it once GitHub is confirmed current (`project_delete`) so it doesn't linger.
- If GitHub `blockout` is already at `0baa32b` or later, ignore the fallback entirely.

---

## 3. Repo layout (what matters)

- `web/compositor.js` — **the main deliverable.** Canvas-2D compositor: draws the plate, the walkable path graph, occlusion, night lighting, behaviour-driven clay figures, floodlights, festival, game-night crowd, and now weather. ~1400 lines.
- `web/compositor.html` — the viewer shell (clock, scrubber, inspector, pins/names toggles).
- `web/assets/replay.json` — the deterministic replay the compositor plays (864 ticks = 3 days). **Currently all-dry weather.**
- `web/assets/era-plate-map.json` (mirror: `design/bible/era-plate-map.json`) — the hand-authored map: paths, obscured zones, lamps, water areas, stands. Current version tag inside: **`eraplatemap 11`** (22 paths, 44 obscured zones, 2 stands, 54 lamps).
- `development/sprint-1/` — the Rust sim crate `era_first_breath`. Subfolders: `src/sim/` (simulation.rs, weather.rs, festival.rs, matchday.rs…), `src/behaviour/`, `examples/dump_replay.rs`, `tests/`.
- `tools/` — helper scripts: `plate-mapper-template.html` (the map editor), `bundle_compositor.py`, `offpath.mjs` (routing audit), `wxtest.mjs` (weather smoke-render).

---

## 4. Build / replay / render — exact commands

**Native Rust build** (works in cloud, ~11s):
```bash
cd development/sprint-1 && /root/.cargo/bin/cargo build
```
(`cargo` lives at `/root/.cargo/bin/cargo`. wasm32 target is blocked by the proxy — do not try.)

**Regenerate the replay** (after any sim change):
```bash
cd development/sprint-1
/root/.cargo/bin/cargo run --example dump_replay 864 0 > ../../web/assets/replay.json
# 864 ticks = 3 days. day0 = Monday, day1 = Tuesday, day2 = Wednesday.
# 288 ticks/day, 5 min/tick. tick t -> (t+1)*5 minutes of the day.
```

**Serve + render.** The dev server must run in the **same shell** as whatever uses it (background `&` jobs die when a Bash tool call returns):
```bash
cd /home/claude/era_repo
python3 -m http.server 8399 --directory web >/tmp/httpd.log 2>&1 &
SRV=$!
sleep 1.5
node tools/wxtest.mjs          # or offpath.mjs, or your own harness
kill $SRV
```

**Headless render harness** (Playwright, swiftshader): uses `createRequire('/home/claude/plate_tools/')` for `playwright`, launches `/opt/pw-browsers/chromium` with `--use-angle=swiftshader --enable-unsafe-swiftshader --no-sandbox`, navigates to `http://127.0.0.1:8399/compositor.html`, waits for `window.__ready===true`, then drives:
- `window.__seek(t)` — jump to tick `t` and draw.
- `window.__state` — the live state (frames, roster, lastFigs, anim…).
- `window.__draw()` — redraw current frame.
- `window.__getRoute(fromId,toId)` — path routing.
- `window.__debugDraw({paths, markers, obscured, routes})` — overlays.
- To force weather for testing: set `window.__state.frames[*].weather = {sky:'rain',wet:true,windy:true,phrase:'…'}`, set `window.__state.anim` to some seconds, then `__seek(t)`. See `tools/wxtest.mjs`.

**Bundle a standalone single-file HTML** of the compositor (for delivery/preview):
```bash
python3 tools/bundle_compositor.py    # -> /tmp/ERA-living-plate.html (inlines JS + plate + map)
```
Deliver that with `SendUserFile` for Roy to open.

---

## 5. Architecture cheat-sheet

### 5.1 Wire contract (sim → compositor)
`replay.json` = `world_json()` (static roster: id/name/kind/color) + per-tick frames. Each frame entity has: `id, x, y, h (heading), spd, ph (phase), pose, gest, partner, place, doing, moving, soc, mood, energy, worn[], child, from, to, et`. Frame also has: `occupancy, events, bonds, weather{sky,temp,wet,windy,phrase}, day, hour, minute, weekday, season`.
- `weather.sky` ∈ `clear|fair|cloudy|overcast|rain|snow|fog`. `wet` = rain|snow.

### 5.2 compositor.js draw() order (top of file, `function draw()`)
backdrop plate → `drawSky(night, wx)` → `drawWater(night)` → `drawLampPosts(lit)` → `drawFloodPosts(flood)` → `drawStadiumCrowd(f)` → figures (y-sorted, occlusion-faded) → foreground occluder → **`drawWeatherGrade(wx, night)`** → `applyLightMap(night,lit,f)` (night) → `drawFloodBeams(flood)` → `drawFestival(…)` → **`drawPrecip(wx, night)`** → pins → HUD.
- `wx = weatherOf(f)` gives `{sky, grey, rain, snow, fog, wet, windy}`.

### 5.3 Path graph & occlusion
- `buildPlateGraph`: path polylines + segment-intersection junctions + T-junctions (endpoint→nearest path within 34px) + place-pin projection connectors + off-frame edge anchoring. Dijkstra `getRoute`.
- Occlusion is **soft**: `occlusionAlpha(px,py)` = signed distance into obscured polygons, `clamp(0.5 - signed/OCC_FADE, 0, 1)`, `OCC_FADE=12`. Beings fade out behind roofs and reappear. (An earlier "on-path always visible" bypass made figures bleed through roofs — Roy hated it; it was reverted. Keep soft occlusion.)
- Routing is clean: `tools/offpath.mjs` audit found only ~15 off-path samples/day at café/square. "Residents stepping on gardens" that remain are **settled place-pins** sitting on planting (riverside/oakside) — a pin-placement issue, not routing. (Open item: nudge those pins, or let settled residents snap to nearest path.)

### 5.4 Figures
`drawFigure` is fully behaviour-driven from the sim stream: `vigor` from energy, `cheer` from mood, `openness` from soc; poses `stand/sit/work/talk/play/dance`; gait rate scales with speed+vigor; gestures nod/glance/gesture/laugh; role clothing (baker/keeper/clerk/grocer/shop) and worn items (coat/scarf/sunhat/umbrella). Conversation partners are placed a step apart and turned to **face each other** (mutual `partner`).

### 5.5 Sim event pattern (how festival/matchday work)
Template = `matchday.rs`: a `consider(me, …) -> Option<Act>` returns a synthetic intent that `simulation.rs`'s decide loop pushes **ahead** of routine; `done_today` tracks completion; `pose_of` in `behaviour/mod.rs` derives the Pose from the activity. Copy this shape for new scheduled events.

---

## 6. Feature inventory — what's built (all in `0baa32b`)

- **Continuous path network + routing** (Dijkstra, junctions, T-junctions, pin connectors).
- **Soft occlusion** behind buildings.
- **Night lighting**: multiply light-map; lamps on ~19:20, off by morning with an eased dawn fade (windows don't linger lit).
- **Water**: lighter waves, very little foam (per Roy).
- **Stadium floodlights**: 4 corner masts, strong cool beams into the pitch, matchday evening only (`floodOn`: `f.day===1`, ~19–21h). `state.floods` corners + `state.floodAim`.
- **Behaviour-driven figures** + **social legibility** (conversations face each other).
- **Monday-night town festival** (`src/sim/festival.rs` + compositor `festivalOn`/`drawFestival`): everyone gathers in `loc_main_square` 19–22h Monday, dancing/music, strung lanterns + drifting notes, warm-gold light wash. **Deepens bonds**: dancing/talking at the festival raises affinity/trust (sim: `social_lift += 32` at festival, consequence `d_aff/d_trust += 1`). Special events are allowed to slightly break the "everyone home by midnight" rule (Roy approved). Duration is re-issued each hour so all leave together at END_HOUR (fixed an earlier "stranded late-arrivers" bug).
- **Game-night stadium crowd** (`gameCrowdFill`/`drawStadiumCrowd`): anonymous green-and-white supporters (NOT sim residents), random **40–180** per match, fill slowly from the **north gate** starting slightly before floodlights. Built as **little clay figures matching the residents' build** (shaded trapezoid torso + head, faceless, club green `#2e8442`/white `#e9ede7`), seated on the mapper's `stands` polygons (or a built-in estimate). Only on `f.day===1`.
- **Weather (NEW, this session)** — see below.

### Weather layer (the active work — `0baa32b`)
`web/compositor.js` reads `f.weather` per frame and renders:
- `weatherOf(f)` → `{sky, grey, rain, snow, fog, wet, windy}`; `grey` per sky: clear 0, fair .06, cloudy .34, overcast .62, rain .56, snow .40, fog .52.
- `drawSky(night, wx)` — on grey days, denser/slatier/lower cloud cover.
- `drawWeatherGrade(wx, night)` — **(1)** a `saturation`-composite pass that **drains the baked sunshine** proportional to `grey` (this is what makes overcast/rain actually read against the bright sunny plate — a plain grey wash alone was far too subtle), **(2)** a cool grey top-heavy overcast wash, **(3)** drifting low **fog** banks, **(4)** a cool **wet-street sheen** on the lower ground when `wet`.
- `drawPrecip(wx, night)` — parallel **rain** streaks (steeper when windy) or drifting **snow**, recycled deterministic particles scrolled by `state.anim`.
- **Umbrellas**: anyone drawn out in the rain (`f.weather.wet && !sit`) raises an umbrella (the umbrella art already existed, keyed on `worn`; now also triggered by wet weather so it needs no sim change).
- Smoke-test: `tools/wxtest.mjs` force-renders rain/snow/overcast/fog and screenshots to `/tmp/wx-*.png`. **No JS errors; all four read correctly.**

**The one remaining weather step:** the shipped `replay.json` is **all-dry** (`wet:false` everywhere; only "bright"/"grey" phrases). `weather.rs` is deterministic per `(day, season, seed)` — Summer rains only 8%/day, and the current 3-day seed-0 replay rolled dry. To see weather in normal playback you must **get a wet day into the replay**: either regenerate with a seed/length whose early days include rain/overcast, or (cleaner) confirm you still preserve **Monday festival on day0** and **game-night on day1** when you pick the new seed/length. Test by forcing a wet frame first (wxtest), then verify the real replay shows it.

---

## 7. Pending / next tasks (roughly in priority order)

1. **Finish weather**: get a wet (and ideally an overcast + a snow, seasonally) day into `replay.json` without breaking Monday-festival/day0 and game-night/day1. Then regenerate and eyeball real playback. Consider: does Roy want the crowd-thinning to be visibly obvious? (`outdoor_appeal()` already suppresses lingering on wet/cold, so the square empties on rainy evenings automatically.)
2. **Settled-on-gardens pins**: nudge the riverside/oakside place-pins off planting, OR make settled residents snap to nearest path. Offered both to Roy — **awaiting his choice.** (Routing itself is clean.)
3. **Clarify "abstractions"**: Roy said re the stands "I can show them (also some abstractions)" — unresolved what he meant.
4. Deferred bigger tracks Roy has floated: deepen the social layer further; a character-design track (Hana → Meshy). Don't start these without Roy steering.

---

## 8. Roy — working style & preferences

- Blunt, visual, fast. If something looks wrong he'll say so plainly. Take it, iterate, don't defend.
- He hand-authors the map in `tools/plate-mapper-template.html` and uploads new `eraplatemap N` JSONs ("updated slight path", "with stands"). Always take his latest map as truth.
- He wants **continuous path networks**, not defined A→B routes.
- He wants beings **occluded only when something real is between them and the camera**, following known paths, disappearing/reappearing naturally.
- Water: **light** waves, **very** little foam.
- Special events (festival, matchday) may **slightly** bend the everyone-home rule.
- He asked specifically for a git flow where **Claude does the commits** and he just pushes — **§2.2** is that flow. Keep commits clean and hand him the bundle + the three push lines each time.

---

## 9. Latest commit

`0baa32b` — `compositor: weather layer — overcast desaturation, rain/snow, fog, wet sheen & umbrellas`

Everything through `0baa32b` is in: (a) the container repo, (b) the full bundle sent to Roy, (c) the base64 incremental bundle stored in this project (`claude/handover/blockout-incremental-bundle.b64.txt`). Any one of those reaches 100% state.

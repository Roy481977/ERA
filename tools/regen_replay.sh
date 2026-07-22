#!/usr/bin/env bash
# Regenerate the canonical compositor replay (web/assets/replay.json).
#
# The compositor plays a 3-day replay: day0 = Monday, day1 = Tuesday, day2 =
# Wednesday. Weather is deterministic in (day, season, seed) — see
# src/sim/weather.rs — so the seed fixes the weather that plays back.
#
# SEED 88 is the canonical compositor seed: it rolls a Summer arc of
#   day0 Fair  (bright Monday — the town festival plays under clear sky)
#   day1 Cloudy (grey Tuesday — game-night floodlights + crowd still fire)
#   day2 Rain, windy (steady rain — umbrellas, wet-street sheen, steep streaks)
# so the shipped replay actually exercises the weather layer in normal playback
# while preserving Monday-festival (day0) and game-night (day1).
#
# Snow/overcast are season-gated (winter is day 56+), so they need a longer,
# multi-season replay — not this 3-day summer showcase.
#
# replay.json is git-ignored (regenerable); this script IS the source of truth
# for the seed. Run it, then rebuild the standalone HTML with
# tools/bundle_compositor.py.
set -euo pipefail
SEED="${1:-88}"
TICKS="${2:-864}"
CARGO="${CARGO:-/root/.cargo/bin/cargo}"
here="$(cd "$(dirname "$0")/.." && pwd)"
cd "$here/development/sprint-1"
"$CARGO" run --quiet --example dump_replay "$TICKS" "$SEED" > "$here/web/assets/replay.json"
echo "replay.json regenerated: ticks=$TICKS seed=$SEED ($(wc -c < "$here/web/assets/replay.json") bytes)"

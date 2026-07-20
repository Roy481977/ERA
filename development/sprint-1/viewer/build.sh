#!/usr/bin/env bash
# Regenerate the self-contained ERA viewer from the live engine.
#   ./build.sh [days] [out.html]
#
# The viewer observes the engine: we tick the world forward and record the live
# snapshot it reports at each hour, then embed the world + that snapshot stream
# into a single self-contained HTML page that replays them on a real-time clock.
set -euo pipefail
days="${1:-7}"
out="${2:-era-first-breath-viewer.html}"
here="$(cd "$(dirname "$0")" && pwd)"
cargo run --quiet -- stream "$days" > /tmp/era-stream.json
python3 - "$here/viewer.template.html" /tmp/era-stream.json "$out" <<'PY'
import sys
tpl, stream, out = sys.argv[1], sys.argv[2], sys.argv[3]
html = open(tpl).read().replace('__STREAM__', open(stream).read().strip())
open(out, 'w').write(html)
print("wrote", out, "(", len(html), "bytes )")
PY

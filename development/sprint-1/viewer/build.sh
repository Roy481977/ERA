#!/usr/bin/env bash
# Regenerate the self-contained ERA viewer from the deterministic core.
#   ./build.sh [days] [out.html]
set -euo pipefail
days="${1:-7}"
out="${2:-era-first-breath-viewer.html}"
here="$(cd "$(dirname "$0")" && pwd)"
cargo run --quiet -- trace "$days" > /tmp/era-trace.json
python3 - "$here/viewer.template.html" /tmp/era-trace.json "$out" <<'PY'
import sys
tpl, trace, out = sys.argv[1], sys.argv[2], sys.argv[3]
html = open(tpl).read().replace('__TRACE__', open(trace).read().strip())
open(out, 'w').write(html)
print("wrote", out, "(", len(html), "bytes )")
PY

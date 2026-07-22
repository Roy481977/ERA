#!/usr/bin/env bash
set -u
cd /home/claude/era_repo
pkill -9 -f "http.server 8399" 2>/dev/null || true
sleep 1
python3 -m http.server 8399 --directory web >/tmp/httpd.log 2>&1 &
SRV=$!
sleep 2
echo "health: $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8399/compositor.html)"
PORT=8399 node tools/render_compositor.mjs /tmp/comp "$@"
echo "node_rc=$?"
kill -9 "$SRV" 2>/dev/null || true
ls -la /tmp/comp_*.png 2>/dev/null || echo "no frames"

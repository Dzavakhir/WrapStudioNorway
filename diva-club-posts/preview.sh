#!/usr/bin/env bash
# ./preview.sh <html-path-relative-to-this-folder> <width> <height> <out.png>
set -euo pipefail
cd "$(dirname "$0")"
P="${1:?path}"; W="${2:-1000}"; H="${3:-800}"; OUT="${4:-/tmp/preview.png}"
PORT=$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1]);s.close()')
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SRV=$!; trap 'kill $SRV 2>/dev/null || true' EXIT
for _ in $(seq 1 60); do curl -s --noproxy '*' -o /dev/null "http://127.0.0.1:$PORT/base.css" && break; sleep 0.1; done
NODE_PATH=/opt/node22/lib/node_modules node preview.cjs "$PORT" "$P" "$W" "$H" "$OUT"

#!/usr/bin/env bash
# Render variants to PNG.
#   ./build.sh a            -> all three ratios of variant A
#   ./build.sh a:4x5        -> just that one
#   ./build.sh all          -> every variant, every ratio
# Serves the folder on a random free port so parallel runs never collide.
set -euo pipefail
cd "$(dirname "$0")"

args=()
for a in "$@"; do
  case "$a" in
    all) for v in a b c; do for r in 9x16 4x5 1x1; do args+=("$v:$r"); done; done ;;
    *:*) args+=("$a") ;;
    *)   for r in 9x16 4x5 1x1; do args+=("$a:$r"); done ;;
  esac
done
if [ ${#args[@]} -eq 0 ]; then echo "usage: ./build.sh a|b|c|all|<variant>:<ratio>"; exit 1; fi

PORT=$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1]);s.close()')
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT
for _ in $(seq 1 60); do
  curl -s --noproxy '*' -o /dev/null "http://127.0.0.1:$PORT/base.css" && break
  sleep 0.1
done

NODE_PATH=/opt/node22/lib/node_modules node render.cjs "$PORT" "${args[@]}"
python3 finalize.py "${args[@]}"

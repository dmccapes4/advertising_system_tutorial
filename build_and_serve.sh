#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# build_and_serve.sh — serve the tutorial locally (macOS / Linux / WSL).
#
#   ./build_and_serve.sh              # serve the pre-built index.html from git
#   ./build_and_serve.sh --build      # rebuild index.html first, then serve
#
# Most learners do NOT need this script. After git clone, double-click
# index.html (or open it in a browser) — no Python, no venv, no install.
# Use this when you want to share on Wi-Fi (http://YOUR-IP:8000) or when you
# edited files under md/ or html/ and need a fresh build.
# ---------------------------------------------------------------------------

set -euo pipefail

PORT=8000
DO_BUILD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --build|-b) DO_BUILD=1; shift ;;
    --port|-p)  PORT="${2:?port number required}"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--build] [--port N]"
      echo "  --build   run build_reader.py before serving (needs markdown in venv)"
      echo "  --port N  listen on port N (default 8000)"
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

cd "$(dirname "$0")"

if [[ ! -f index.html ]]; then
  echo "index.html is missing — run with --build after: source setup_venv.sh" >&2
  exit 1
fi

if [[ "$DO_BUILD" -eq 1 ]]; then
  echo "Rebuilding index.html from md/ + html/ ..."
  PY="$(command -v python3 || command -v python || true)"
  if [[ -z "$PY" ]]; then
    echo "Python not found. Install Python 3.10+ or run: source setup_venv.sh" >&2
    exit 1
  fi
  if ! "$PY" -c "import markdown" 2>/dev/null; then
    echo "Package 'markdown' not installed. Run: source setup_venv.sh" >&2
    exit 1
  fi
  "$PY" build_reader.py
  echo ""
fi

# Best-effort LAN address for the "Share on Wi-Fi" line.
IP=""
if command -v ip >/dev/null 2>&1; then
  IP="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}' | head -1)"
elif command -v hostname >/dev/null 2>&1; then
  IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
fi

echo "==============================================================="
echo "  Tutorial server — keep this window open while reading."
echo "==============================================================="
echo ""
echo "  On THIS computer :  http://localhost:${PORT}"
if [[ -n "$IP" && "$IP" != "127.0.0.1" ]]; then
  echo "  Share on Wi-Fi   :  http://${IP}:${PORT}"
  echo "                      ^ same network — phone, tablet, another PC"
fi
echo ""
echo "  Press Ctrl+C to stop."
echo ""

# Open browser (best effort).
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://localhost:${PORT}" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
  open "http://localhost:${PORT}" >/dev/null 2>&1 &
fi

exec python3 -m http.server "$PORT" 2>/dev/null || exec python -m http.server "$PORT"

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACTION="${1:-start}"
RUNTIME_DIR="/home/ai-agent/lotus-runtime/operations/fusion-history-mt5"
mkdir -p "$RUNTIME_DIR"/{downloads,home,logs,mt5-prefix}
export LOCAL_UID="$(id -u)" LOCAL_GID="$(id -g)"

case "$ACTION" in
  start)
    docker compose --project-directory "$ROOT_DIR" -f "$ROOT_DIR/compose.fusion-history-mt5.yaml" up -d --build --wait
    echo "Fusion MT5 desktop: http://127.0.0.1:6081/vnc.html?host=127.0.0.1&port=6081"
    ;;
  stop)
    docker compose --project-directory "$ROOT_DIR" -f "$ROOT_DIR/compose.fusion-history-mt5.yaml" down
    ;;
  status)
    docker compose --project-directory "$ROOT_DIR" -f "$ROOT_DIR/compose.fusion-history-mt5.yaml" ps
    ;;
  *)
    echo "Usage: $0 {start|stop|status}" >&2
    exit 2
    ;;
esac

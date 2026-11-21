#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT_DIR/../../1lotus/mt5/FusionCandleHistoryExporter.mq5"
CONTAINER="gold-lotus-fusion-history-mt5"

if [[ ! -f "$SOURCE" ]]; then
  echo "Fusion exporter source not found: $SOURCE" >&2
  exit 1
fi
docker exec "$CONTAINER" bash -lc '
  terminal="/data/mt5-prefix/drive_c/Program Files/Fusion Markets MetaTrader 5"
  test -f "$terminal/terminal64.exe" || { echo "Install MT5 first in the noVNC desktop." >&2; exit 1; }
  mkdir -p "$terminal/MQL5/Scripts"
  cp /opt/1lotus/mt5/FusionCandleHistoryExporter.mq5 "$terminal/MQL5/Scripts/"
  echo "Exporter copied into MT5 Scripts; compile it from MetaEditor."
'

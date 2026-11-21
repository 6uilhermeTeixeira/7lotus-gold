#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ONELOTUS_DIR="$(cd "$ROOT_DIR/../1lotus" && pwd)"
DATA_ROOT="${LOTUS_DATA_ROOT:-$HOME/lotus-data}"
SERVER="${1:-}"
SYMBOL="${2:-XAUUSD}"
TIMEFRAME="${3:-M5}"
CSV_PATH="${4:-}"

if [[ -z "$SERVER" ]]; then
  echo "Usage: $0 <Fusion-MT5-server-name> [symbol] [M1|M5] [ready.csv]" >&2
  exit 2
fi
if [[ "$TIMEFRAME" != "M1" && "$TIMEFRAME" != "M5" ]]; then
  echo "Timeframe must be M1 or M5." >&2
  exit 2
fi

if [[ -z "$CSV_PATH" ]]; then
  COMMON_FILES="/home/ai-agent/lotus-runtime/operations/fusion-history-mt5/mt5-prefix/drive_c/users"
  CSV_PATH="$(find "$COMMON_FILES" -type f -name "XAUUSD-${TIMEFRAME}-candles.ready.csv" -path '*/MetaQuotes/Terminal/Common/Files/1lotus-candles/fusion/*' -printf '%T@ %p\n' 2>/dev/null | sort -nr | sed -n '1s/^[^ ]* //p')"
fi

if [[ -z "$CSV_PATH" || ! -f "$CSV_PATH" || "$CSV_PATH" != *.ready.csv ]]; then
  echo "No completed XAUUSD-${TIMEFRAME}-candles.ready.csv export found. Run the MT5 exporter first." >&2
  exit 1
fi

HASH="$(sha256sum "$CSV_PATH" | cut -d' ' -f1)"
SOURCE_DIR="$DATA_ROOT/fusion-candles/source"
mkdir -p "$SOURCE_DIR"
ARCHIVE="$SOURCE_DIR/${HASH}-$(basename "$CSV_PATH")"
if [[ ! -f "$ARCHIVE" ]]; then
  install -m 0644 "$CSV_PATH" "$ARCHIVE"
fi

"$ONELOTUS_DIR/.venv/bin/python" "$ONELOTUS_DIR/scripts/import_fusion_candles.py" \
  "$ARCHIVE" --data-root "$DATA_ROOT" --server "$SERVER" --symbol "$SYMBOL" --timeframe "$TIMEFRAME"

#!/usr/bin/env bash
set -euo pipefail

WINE_CMD="${WINE_CMD:-wine}"
MT5_URL="${MT5_URL:-https://download.terminal.free/cdn/web/fusion.markets.pty/mt5/fusionmarkets5setup.exe}"
WEBVIEW_URL="${WEBVIEW_URL:-https://msedge.sf.dl.delivery.mp.microsoft.com/filestreamingservice/files/f2910a1e-e5a6-4f17-b52d-7faf525d17f8/MicrosoftEdgeWebview2Setup.exe}"
DOWNLOAD_DIR="${DOWNLOAD_DIR:-/data/downloads}"
PREFIX_DIR="${WINEPREFIX:-/data/mt5-prefix}"
LOG_DIR="${LOG_DIR:-/data/logs}"
HOME_DIR="${HOME_DIR:-/data/home}"
DISPLAY_ID="${DISPLAY_ID:-:99}"

mkdir -p "$DOWNLOAD_DIR" "$PREFIX_DIR" "$LOG_DIR" "$HOME_DIR"
export WINEPREFIX="$PREFIX_DIR" WINEARCH="${WINEARCH:-win64}" DISPLAY="$DISPLAY_ID" HOME="$HOME_DIR" WINEDEBUG=-all

command -v "$WINE_CMD" >/dev/null 2>&1 || { echo "Wine runtime not found" >&2; exit 1; }

for spec in "fusionmarkets5setup.exe|$MT5_URL" "webview2.exe|$WEBVIEW_URL"; do
  filename="${spec%%|*}"
  url="${spec#*|}"
  if [[ ! -f "$DOWNLOAD_DIR/$filename" ]]; then
    curl --fail --location --retry 3 "$url" --output "$DOWNLOAD_DIR/$filename"
  fi
done

terminal="$PREFIX_DIR/drive_c/Program Files/Fusion Markets MetaTrader 5/terminal64.exe"
if ! pgrep -f '[t]erminal64.exe' >/dev/null; then
  timeout 120 "$WINE_CMD" wineboot -i >"$LOG_DIR/wineboot-mt5.log" 2>&1 || true
  if [[ ! -f "$PREFIX_DIR/drive_c/windows/syswow64/kernel32.dll" ]]; then
    helper_prefix="${PREFIX_DIR}-win32-helper"
    mkdir -p "$helper_prefix"
    WINEPREFIX="$helper_prefix" WINEARCH=win32 timeout 120 "$WINE_CMD" wineboot -i \
      >"$LOG_DIR/wineboot-win32-helper.log" 2>&1 || true
    [[ -f "$helper_prefix/drive_c/windows/system32/kernel32.dll" ]] || {
      echo "Wine 32-bit helper prefix did not initialize" >&2; exit 1;
    }
    mkdir -p "$PREFIX_DIR/drive_c/windows/syswow64"
    cp -a "$helper_prefix/drive_c/windows/system32/." "$PREFIX_DIR/drive_c/windows/syswow64/"
    WINEPREFIX="$helper_prefix" "$WINE_CMD" wineserver -k 2>/dev/null || true
    rm -rf -- "$helper_prefix"
  fi
  if [[ ! -f "$terminal" ]]; then
    "$WINE_CMD" "$DOWNLOAD_DIR/webview2.exe" /silent /install >"$LOG_DIR/webview2-mt5.log" 2>&1 || true
    "$WINE_CMD" "$DOWNLOAD_DIR/fusionmarkets5setup.exe" >"$LOG_DIR/mt5setup.log" 2>&1 || true
  fi
  while [[ ! -f "$terminal" ]]; do
    sleep 5
  done
fi

while pgrep -f '[t]erminal64.exe' >/dev/null; do
  sleep 5
done
[[ -f "$terminal" ]] || { echo "MetaTrader terminal not installed yet." >&2; exit 1; }
if [[ -f /data/fusion-history-login.ini ]]; then
  exec "$WINE_CMD" "$terminal" '/config:Z:\data\fusion-history-login.ini'
fi
if [[ -f /data/fusion-history-export.ini ]]; then
  exec "$WINE_CMD" "$terminal" '/config:Z:\data\fusion-history-export.ini'
fi
exec "$WINE_CMD" "$terminal"

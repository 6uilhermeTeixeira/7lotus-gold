#!/usr/bin/env bash
set -euo pipefail

DISPLAY_ID="${DISPLAY_ID:-:99}"
DISPLAY_NUM="${DISPLAY_ID#:}"
SCREEN_GEOMETRY="${SCREEN_GEOMETRY:-1440x900x24}"
RFB_PORT="${RFB_PORT:-5900}"
NOVNC_PORT="${NOVNC_PORT:-6080}"
LOG_DIR="${LOG_DIR:-/data/logs}"
HOME_DIR="${HOME_DIR:-/data/home}"
PREFIX_DIR="${WINEPREFIX:-/data/mt5-prefix}"
mkdir -p "$LOG_DIR" "$HOME_DIR" "$PREFIX_DIR" /data/downloads
export DISPLAY="$DISPLAY_ID" HOME="$HOME_DIR" WINEPREFIX="$PREFIX_DIR" WINEARCH="${WINEARCH:-win64}" WINEDEBUG=-all

rm -f "/tmp/.X${DISPLAY_NUM}-lock" "/tmp/.X11-unix/X${DISPLAY_NUM}"
Xvfb "$DISPLAY" -screen 0 "$SCREEN_GEOMETRY" >"$LOG_DIR/xvfb-remote.log" 2>&1 &
xvfb_pid=$!
sleep 2
openbox >"$LOG_DIR/openbox-remote.log" 2>&1 &
openbox_pid=$!
x11vnc -display "$DISPLAY" -rfbport "$RFB_PORT" -forever -shared -noxrecord -xkb -repeat -nopw -quiet >"$LOG_DIR/x11vnc.log" 2>&1 &
x11vnc_pid=$!
websockify --web /usr/share/novnc/ "$NOVNC_PORT" "127.0.0.1:$RFB_PORT" >"$LOG_DIR/novnc.log" 2>&1 &
websockify_pid=$!
/opt/fusion-history/bootstrap-mt5.sh >"$LOG_DIR/bootstrap-session.log" 2>&1 &
bootstrap_pid=$!

cleanup() {
  kill "$bootstrap_pid" "$websockify_pid" "$x11vnc_pid" "$openbox_pid" "$xvfb_pid" 2>/dev/null || true
}
trap cleanup EXIT
wait -n "$xvfb_pid" "$x11vnc_pid" "$websockify_pid" "$bootstrap_pid"
echo "A critical Fusion MT5 runtime process exited." >&2
exit 1

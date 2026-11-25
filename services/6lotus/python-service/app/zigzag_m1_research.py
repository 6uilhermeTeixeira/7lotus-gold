"""Causal M30 structure with M1 entry/exit, for Fusion research only."""

from __future__ import annotations

from collections import deque
from datetime import datetime


def _pivot(bars: list[dict], side: str) -> float | None:
    # A fractal needs two *completed* bars on each side to be known.
    for index in range(len(bars) - 3, 1, -1):
        value = bars[index][side]
        window = [row[side] for row in bars[index - 2:index + 3]]
        if value == (max(window) if side == "high" else min(window)):
            return value
    return None


def replay(rows: list[tuple], *, year: int, point_size: float = .01,
           stop_points: int = 240, target_points: int = 1000,
           max_hold_minutes: int = 10, volume_lots: float = .1,
           value_per_point_per_lot: float = 1.0,
           slippage_points: float = 2.0,
           commission_per_lot: float = 4.5) -> dict:
    """rows: server_time,open,high,low,close,spread_points in ascending order."""
    completed: deque[dict] = deque(maxlen=200)
    bucket = None
    current = None
    pending = None
    active = None
    trades = []
    signals = 0
    for stamp, opening, high, low, close, spread in rows:
        time = datetime.fromisoformat(str(stamp))
        key = time.replace(minute=(time.minute // 30) * 30, second=0)
        if key != bucket:
            if current is not None:
                completed.append(current)
                bars = list(completed)
                if len(bars) >= 7:
                    previous, latest = bars[-2], bars[-1]
                    pivot_high, pivot_low = _pivot(bars[:-1], "high"), _pivot(bars[:-1], "low")
                    if pivot_high is not None and previous["close"] <= pivot_high < latest["close"]:
                        pending = "buy"
                    elif pivot_low is not None and previous["close"] >= pivot_low > latest["close"]:
                        pending = "sell"
                    else:
                        pending = None
                    if pending:
                        signals += 1
            bucket = key
            current = {"high": high, "low": low, "close": close}
        else:
            current["high"] = max(current["high"], high)
            current["low"] = min(current["low"], low)
            current["close"] = close
        spread_price = max(0, spread) * point_size
        if pending is not None:
            side = pending
            pending = None
            if active is None and time.year == year:
                entry = opening + (spread_price if side == "buy" else 0)
                entry += slippage_points * point_size * (1 if side == "buy" else -1)
                active = {"side": side, "opened": time, "entry": entry, "bars": 0,
                          "stop": entry + stop_points * point_size * (-1 if side == "buy" else 1),
                          "target": entry + target_points * point_size * (1 if side == "buy" else -1)}
        if active is not None:
            active["bars"] += 1
            side = active["side"]
            # OHLC has no intraminute ordering. A stop wins if both levels are touched.
            stop_hit = low <= active["stop"] if side == "buy" else high + spread_price >= active["stop"]
            target_hit = high >= active["target"] if side == "buy" else low + spread_price <= active["target"]
            reason = "stop" if stop_hit else "target" if target_hit else "timeout" if active["bars"] >= max_hold_minutes else None
            if reason:
                raw_exit = active["stop"] if stop_hit else active["target"] if target_hit else close + (spread_price if side == "sell" else 0)
                exit_price = raw_exit + (-slippage_points * point_size if side == "buy" else slippage_points * point_size)
                pnl_points = (exit_price - active["entry"]) / point_size * (1 if side == "buy" else -1)
                net = round(pnl_points * volume_lots * value_per_point_per_lot - commission_per_lot * volume_lots, 2)
                if active["opened"].year == year:
                    trades.append({"opened_server_time": active["opened"].isoformat(sep=" "),
                                   "closed_server_time": time.isoformat(sep=" "), "side": side,
                                   "entry": round(active["entry"], 5), "exit": round(exit_price, 5),
                                   "reason": reason, "net_pnl": net})
                active = None
    net = round(sum(trade["net_pnl"] for trade in trades), 2)
    return {"year": year, "candles_evaluated": sum(datetime.fromisoformat(str(r[0])).year == year for r in rows),
            "signals": signals, "trades_count": len(trades), "net_pnl": net,
            "wins": sum(t["net_pnl"] > 0 for t in trades), "trades": trades}

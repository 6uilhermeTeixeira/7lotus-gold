"""Generate a versioned, local-only Fusion ZigZag M1 research snapshot."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.fusion_research import open_fusion_release
from app.zigzag_m1_research import replay


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--root", type=Path, default=Path(os.getenv("LOTUS_FUSION_CANDLES_ROOT", "/home/ai-agent/lotus-data/fusion-candles")))
    args = parser.parse_args()
    if not 2021 <= args.year <= date.today().year:
        parser.error("year must be within the available historical period")
    release = open_fusion_release(args.root, "M1", verify_hash=True)
    start = (date(args.year, 1, 1) - timedelta(days=4)).isoformat()
    end = date(args.year + 1, 1, 1).isoformat()
    with duckdb.connect(":memory:") as db:
        rows = db.execute(
            "SELECT server_time,open,high,low,close,spread_points FROM read_parquet(?) "
            "WHERE server_time >= ? AND server_time < ? ORDER BY server_time",
            [str(release.parquet), start, end],
        ).fetchall()
    if not rows:
        parser.error("no M1 candles in year")
    parameters = {"signal_timeframe": "M30", "entry_timeframe": "M1", "stop_points": 240,
                  "target_points": 1000, "max_hold_minutes": 10, "volume_lots": .1,
                  "slippage_points": 2, "commission_per_lot": 4.5,
                  "session_filter": "none", "ambiguous_bar": "stop_first"}
    result = replay(rows, year=args.year)
    algorithm = Path(__file__).resolve().parents[1] / "app" / "zigzag_m1_research.py"
    fingerprint = sha256(algorithm.read_bytes() + json.dumps(parameters, sort_keys=True).encode()).hexdigest()[:16]
    snapshot = {"study_id": "zigzag-scalper-m1", "status": "research_only", "source": "Fusion Markets MT5",
                "symbol": "XAUUSD", "timeframe": "M1", "time_basis": "broker_server_time",
                "dataset_version": release.version, "source_sha256": release.manifest["source_sha256"],
                "parameters": parameters, "settings_fingerprint": fingerprint, **result}
    output_dir = args.root.parent / "research" / "fusion-m1" / release.version
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"zigzag-scalper-m1-{args.year}-{fingerprint}.json"
    temporary = output.with_suffix(".json.part")
    temporary.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output)
    pointer = output_dir / f"zigzag-scalper-m1-{args.year}.CURRENT"
    pointer_temp = pointer.with_suffix(".CURRENT.part")
    pointer_temp.write_text(fingerprint + "\n", encoding="utf-8")
    pointer_temp.replace(pointer)
    print(json.dumps({"path": str(output), "year": args.year, "trades_count": result["trades_count"],
                      "net_pnl": result["net_pnl"], "dataset_version": release.version}))


if __name__ == "__main__":
    main()

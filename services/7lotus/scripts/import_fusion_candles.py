"""Import a completed Fusion MT5 M1 or M5 candle export into 7lotus storage."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fusion_candles import FusionCandleError, import_csv


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="completed *.ready.csv from MT5 Common/Files/1lotus-candles/fusion")
    parser.add_argument("--data-root", type=Path, default=Path(os.getenv("LOTUS_DATA_ROOT", "/home/codexops/lotus-data")))
    parser.add_argument("--symbol", default="XAUUSD", help="exact Fusion MT5 symbol, including any suffix")
    parser.add_argument("--server", required=True, help="MT5 account server name, e.g. FusionMarkets-Demo")
    parser.add_argument("--timeframe", choices=("M1", "M5"), default="M5", help="timeframe exported by MT5")
    args = parser.parse_args()
    try:
        result = import_csv(args.csv, args.data_root, symbol=args.symbol, server=args.server, timeframe=args.timeframe)
    except (FusionCandleError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

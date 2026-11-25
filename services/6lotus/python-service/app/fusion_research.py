"""Read immutable Fusion candle releases for local, shadow-only research."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path

import duckdb

from .local_dataset import DatasetError
from .schemas import MarketCandlePoint


@dataclass(frozen=True)
class FusionRelease:
    version: str
    timeframe: str
    parquet: Path
    manifest: dict


def open_fusion_release(root: Path, timeframe: str, *, verify_hash: bool = False) -> FusionRelease:
    if timeframe not in {"M1", "M5"}:
        raise DatasetError("Fusion timeframe must be M1 or M5")
    base = root.expanduser().resolve() / timeframe.lower() / "releases"
    pointer = base / "CURRENT"
    if not pointer.is_file():
        raise DatasetError(f"Fusion {timeframe} release is unavailable")
    version = pointer.read_text(encoding="utf-8").strip()
    if len(version) != 16 or any(c not in "0123456789abcdef" for c in version):
        raise DatasetError("invalid Fusion release pointer")
    release = base / version
    parquet, manifest_path = release / "candles.parquet", release / "manifest.json"
    if not parquet.is_file() or not manifest_path.is_file():
        raise DatasetError("incomplete Fusion release")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DatasetError("invalid Fusion manifest") from exc
    if (manifest.get("version") != version or manifest.get("timeframe") != timeframe
            or manifest.get("schema_version") != f"fusion-{timeframe.lower()}-candles-v1"
            or manifest.get("canonical_symbol") != "XAUUSD"
            or manifest.get("time_basis") != "broker_server_time"):
        raise DatasetError("Fusion release contract mismatch")
    if verify_hash:
        digest = sha256()
        with parquet.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        if digest.hexdigest() != manifest.get("parquet_sha256"):
            raise DatasetError("Fusion Parquet hash mismatch")
    return FusionRelease(version, timeframe, parquet, manifest)


def load_fusion_chart(root: Path, resolution: str, days: int, limit: int = 5000,
                      end_date: date | None = None) -> tuple[FusionRelease, list[MarketCandlePoint]]:
    if resolution not in {"1m", "5m", "1h", "1d"}:
        raise DatasetError("unsupported Fusion resolution")
    release = open_fusion_release(root, "M1" if resolution == "1m" else "M5")
    end = end_date or date.fromisoformat(release.manifest["last_server_time"][:10])
    start = (end - timedelta(days=days - 1)).isoformat()
    exclusive_end = (end + timedelta(days=1)).isoformat()
    if resolution in {"1m", "5m"}:
        sql = "SELECT server_time,open,high,low,close,tick_volume FROM read_parquet(?) WHERE server_time >= ? AND server_time < ? ORDER BY server_time DESC LIMIT ?"
    else:
        interval = "1 hour" if resolution == "1h" else "1 day"
        sql = ("WITH bars AS (SELECT time_bucket(INTERVAL '" + interval + "', CAST(server_time AS TIMESTAMP)) bucket, "
               "server_time,open,high,low,close,tick_volume FROM read_parquet(?) WHERE server_time >= ? AND server_time < ?) "
               "SELECT strftime(bucket,'%Y-%m-%d %H:%M:%S'),arg_min(open,server_time),max(high),min(low),"
               "arg_max(close,server_time),sum(tick_volume) FROM bars GROUP BY bucket ORDER BY bucket DESC LIMIT ?")
    with duckdb.connect(":memory:") as db:
        rows = db.execute(sql, [str(release.parquet), start, exclusive_end, limit]).fetchall()
    # Numeric t is only an axis encoding of the broker's wall clock. No UTC conversion occurs.
    candles = [MarketCandlePoint(
        t=int(datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp() * 1000),
        o=o, h=h, l=low, c=close, volume=volume,
    ) for t, o, h, low, close, volume in reversed(rows)]
    return release, candles

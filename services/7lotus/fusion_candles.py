"""Import and read M1/M5 candles exported by a Fusion Markets MT5 terminal.

Times are preserved as broker server wall time. They are deliberately not
labelled UTC because the historical GMT+2/GMT+3 transition is not in MT5 CSV.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from datetime import date
from pathlib import Path
from time import strftime, strptime
from typing import Any

import duckdb

FIELDS = ("server_time", "open", "high", "low", "close", "tick_volume", "spread_points", "real_volume")


class FusionCandleError(ValueError):
    pass


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sql_path(path: Path) -> str:
    return str(path).replace("'", "''")


def import_csv(source: Path, root: Path, *, symbol: str = "XAUUSD", server: str = "Fusion Markets MT5", timeframe: str = "M5") -> dict[str, Any]:
    """Validate one completed exporter CSV, then publish a versioned Parquet release."""
    source = source.expanduser().resolve()
    root = root.expanduser().resolve()
    if not source.is_file() or not source.name.endswith(".ready.csv"):
        raise FusionCandleError("Informe um arquivo .ready.csv concluído pelo exportador.")
    if timeframe not in {"M1", "M5"}:
        raise FusionCandleError("Timeframe Fusion indisponível; use M1 ou M5.")
    if not symbol.startswith("XAUUSD") or not server.strip():
        raise FusionCandleError("Símbolo ou servidor inválido para o histórico Fusion XAUUSD.")
    source_hash = _digest(source)
    version = hashlib.sha256((source_hash + symbol + server.strip() + timeframe).encode()).hexdigest()[:16]
    release = root / "fusion-candles" / timeframe.lower() / "releases" / version
    parquet = release / "candles.parquet"
    manifest_path = release / "manifest.json"
    if manifest_path.is_file() and parquet.is_file():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    release.mkdir(parents=True, exist_ok=True)
    count = 0
    years: dict[int, int] = {}
    first: str | None = None
    last: str | None = None
    previous: str | None = None
    temporary = parquet.with_suffix(".parquet.part")
    try:
        with duckdb.connect(":memory:") as db, source.open(newline="", encoding="utf-8-sig") as handle:
            db.execute("CREATE TABLE candles (server_time VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, tick_volume BIGINT, spread_points INTEGER, real_volume DOUBLE)")
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or tuple(reader.fieldnames) != FIELDS:
                raise FusionCandleError("Cabeçalho CSV incompatível com o exportador de candles Fusion.")
            for line, row in enumerate(reader, start=2):
                try:
                    timestamp = strptime(row["server_time"], "%Y.%m.%d %H:%M:%S")
                    stamp = strftime("%Y-%m-%d %H:%M:%S", timestamp)
                    o, h, l, c = (float(row[key]) for key in ("open", "high", "low", "close"))
                    volume = int(row["tick_volume"])
                    spread = int(row["spread_points"])
                    real_volume = float(row["real_volume"])
                    if (not all(math.isfinite(value) and value > 0 for value in (o, h, l, c))
                            or h < max(o, c) or l > min(o, c) or l > h
                            or volume < 0 or spread < 0 or not math.isfinite(real_volume) or real_volume < 0):
                        raise ValueError("OHLC ou volume inválido")
                    if previous is not None and stamp >= previous:
                        raise ValueError("candles fora da ordem mais recente → mais antigo ou duplicados")
                except (KeyError, TypeError, ValueError) as exc:
                    raise FusionCandleError(f"Linha {line} inválida: {exc}") from exc
                first = stamp if first is None else min(first, stamp)
                last = stamp if last is None else max(last, stamp)
                previous = stamp
                years[timestamp.tm_year] = years.get(timestamp.tm_year, 0) + 1
                count += 1
            if not count:
                raise FusionCandleError("O arquivo não contém candles.")
            db.execute(
                "INSERT INTO candles SELECT "
                "strftime(strptime(server_time, '%Y.%m.%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'), "
                "open, high, low, close, tick_volume, spread_points, real_volume "
                "FROM read_csv_auto(?, header=true, all_varchar=true)",
                [str(source)],
            )
            db.execute(f"COPY (SELECT * FROM candles ORDER BY server_time) TO '{_sql_path(temporary)}' (FORMAT PARQUET, COMPRESSION ZSTD)")
        os.replace(temporary, parquet)
        manifest = {
            "schema_version": f"fusion-{timeframe.lower()}-candles-v1", "source": "Fusion Markets MT5",
            "symbol": symbol, "canonical_symbol": "XAUUSD", "timeframe": timeframe, "server": server.strip(),
            "time_basis": "broker_server_time", "version": version,
            "source_sha256": source_hash, "parquet_sha256": _digest(parquet),
            "rows": count, "first_server_time": first, "last_server_time": last,
            "years": [{"year": year, "candles": years[year]} for year in sorted(years)],
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        pointer = release.parent / "CURRENT"
        pointer_tmp = pointer.with_suffix(".part")
        pointer_tmp.write_text(version + "\n", encoding="utf-8")
        os.replace(pointer_tmp, pointer)
        return manifest
    finally:
        temporary.unlink(missing_ok=True)


def current_release(root: Path, *, timeframe: str = "M5") -> dict[str, Any]:
    if timeframe not in {"M1", "M5"}:
        return {"available": False, "reason": "Timeframe Fusion indisponível."}
    base = root.expanduser().resolve() / "fusion-candles" / timeframe.lower() / "releases"
    pointer = base / "CURRENT"
    if not pointer.is_file():
        return {"available": False, "reason": "Nenhum candle Fusion importado."}
    version = pointer.read_text(encoding="utf-8").strip()
    if not version or any(char not in "0123456789abcdef" for char in version):
        return {"available": False, "reason": "Ponteiro Fusion inválido."}
    release = base / version
    manifest_path, parquet = release / "manifest.json", release / "candles.parquet"
    if not manifest_path.is_file() or not parquet.is_file():
        return {"available": False, "reason": "Release Fusion incompleto."}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"available": False, "reason": "Manifesto Fusion ilegível."}
    if (not isinstance(manifest, dict) or manifest.get("version") != version
            or manifest.get("schema_version") != f"fusion-{timeframe.lower()}-candles-v1"
            or manifest.get("source") != "Fusion Markets MT5"
            or manifest.get("canonical_symbol") != "XAUUSD" or manifest.get("timeframe") != timeframe):
        return {"available": False, "reason": "Contrato do release Fusion inválido."}
    return {"available": True, "version": version, "manifest": manifest, "parquet": parquet}


def read_day(root: Path, day: date, *, limit: int = 1500, timeframe: str = "M5") -> dict[str, Any]:
    release = current_release(root, timeframe=timeframe)
    if not release["available"]:
        raise FusionCandleError(release["reason"])
    start, end = day.isoformat(), date.fromordinal(day.toordinal() + 1).isoformat()
    try:
        with duckdb.connect(":memory:") as db:
            rows = db.execute(
                "SELECT server_time,open,high,low,close,tick_volume,spread_points,real_volume "
                "FROM read_parquet(?) WHERE server_time >= ? AND server_time < ? ORDER BY server_time LIMIT ?",
                [str(release["parquet"]), start, end, limit],
            ).fetchall()
    except duckdb.Error as exc:
        raise FusionCandleError("Parquet Fusion publicado não pôde ser lido.") from exc
    return {"day": start, "source": "fusion", "timeframe": timeframe, "time_basis": "broker_server_time",
            "version": release["version"],
            "items": [{"server_time": t, "open": o, "high": h, "low": l, "close": c,
                       "tick_volume": volume, "spread_points": spread, "real_volume": real_volume}
                      for t, o, h, l, c, volume, spread, real_volume in rows]}


def read_range(root: Path, start: date, end: date, *, resolution: str = "5m") -> dict[str, Any]:
    if end < start:
        raise FusionCandleError("A data final deve ser igual ou posterior à inicial.")
    if resolution not in {"1m", "5m", "1h", "1d"}:
        raise FusionCandleError("Resolução Fusion indisponível.")
    timeframe = "M1" if resolution == "1m" else "M5"
    release = current_release(root, timeframe=timeframe)
    if not release["available"]:
        raise FusionCandleError(release["reason"])
    next_day = date.fromordinal(end.toordinal() + 1).isoformat()
    source = "FROM read_parquet(?) WHERE server_time >= ? AND server_time < ?"
    if resolution in {"1m", "5m"}:
        sql = ("SELECT server_time,open,high,low,close,tick_volume,spread_points,real_volume "
               + source + " ORDER BY server_time LIMIT 5001")
    else:
        interval = "1 hour" if resolution == "1h" else "1 day"
        sql = ("WITH grouped AS (SELECT time_bucket(INTERVAL '" + interval + "', "
               "CAST(server_time AS TIMESTAMP)) AS bucket, server_time,open,high,low,close,"
               "tick_volume,spread_points,real_volume " + source + ") "
               "SELECT strftime(bucket, '%Y-%m-%d %H:%M:%S'),arg_min(open,server_time),"
               "max(high),min(low),arg_max(close,server_time),sum(tick_volume),"
               "max(spread_points),sum(real_volume) FROM grouped GROUP BY bucket "
               "ORDER BY bucket LIMIT 5001")
    try:
        with duckdb.connect(":memory:") as db:
            rows = db.execute(sql, [str(release["parquet"]), start.isoformat(), next_day]).fetchall()
    except duckdb.Error as exc:
        raise FusionCandleError("Não foi possível consultar o release Fusion.") from exc
    return {"start": start.isoformat(), "end": end.isoformat(), "resolution": resolution,
            "source": "fusion", "time_basis": "broker_server_time", "version": release["version"],
            "truncated": len(rows) > 5000,
            "items": [{"server_time": t, "open": o, "high": h, "low": l, "close": c,
                       "tick_volume": volume, "spread_points": spread, "real_volume": real_volume}
                      for t, o, h, l, c, volume, spread, real_volume in rows[:5000]]}

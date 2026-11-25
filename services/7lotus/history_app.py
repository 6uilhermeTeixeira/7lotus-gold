"""Read-only local viewer for published XAUUSD tick history."""

from __future__ import annotations

import json
import os
import sqlite3
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import duckdb
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from fusion_candles import FusionCandleError
from fusion_candles import current_release as fusion_release
from fusion_candles import read_day as read_fusion_day
from history_progress import load_dukascopy_progress, load_fusion_progress

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="7lotus | Histórico do ouro", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


def data_root() -> Path:
    return Path(os.getenv("LOTUS_DATA_ROOT", "/home/codexops/lotus-data")).expanduser().resolve()


def collection_status(root: Path) -> dict[str, Any]:
    path = root / "manifests" / "dukascopy.sqlite3"
    if not path.is_file():
        return {"available": False, "hours": 0, "years": []}
    try:
        with sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=2) as db:
            rows = db.execute(
                "SELECT substr(hour_utc, 1, 4), status, count(*) FROM downloads "
                "WHERE instrument = ? GROUP BY 1, 2 ORDER BY 1", ("XAUUSD",)
            ).fetchall()
    except sqlite3.Error as exc:
        return {"available": False, "hours": 0, "years": [], "error": f"Manifesto ilegível: {exc}"}
    years: dict[int, dict[str, int]] = defaultdict(lambda: {"completed": 0, "pending": 0})
    for year_text, state, count in rows:
        if not year_text or not year_text.isdigit():
            continue
        key = "completed" if state in {"downloaded", "existing", "missing"} else "pending"
        years[int(year_text)][key] += count
    return {"available": True, "hours": sum(row["completed"] for row in years.values()),
            "years": [{"year": year, **counts} for year, counts in sorted(years.items())]}


def published_release(root: Path) -> dict[str, Any]:
    pointer = root / "releases" / "CURRENT"
    if not pointer.is_file():
        return {"available": False, "reason": "Nenhum release publicado em releases/CURRENT."}
    version = pointer.read_text(encoding="utf-8").strip()
    if not version or "/" in version or "\\" in version or ".." in version:
        return {"available": False, "reason": "Ponteiro CURRENT inválido."}
    manifest_path = root / "releases" / version / "manifest.json"
    if not manifest_path.is_file():
        return {"available": False, "reason": "Manifesto do release não encontrado."}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"available": False, "reason": "Manifesto do release ilegível."}
    if (not isinstance(manifest, dict) or manifest.get("dataset_version") != version
            or manifest.get("schema_version") != "xauusd-ticks-v1"
            or manifest.get("release_status") != "published" or manifest.get("instrument") != "XAUUSD"):
        return {"available": False, "reason": "Release publicado não corresponde ao contrato XAUUSD."}
    return {"available": True, "version": version, "manifest": manifest}


def validated_partitions(root: Path, manifest: dict[str, Any], day: date, resolution: str) -> list[str]:
    if resolution == "ticks":
        entries = manifest.get("partitions", [])
    else:
        aggregations = manifest.get("aggregations", {})
        entries = aggregations.get(resolution, []) if isinstance(aggregations, dict) else []
    if not isinstance(entries, list):
        raise HTTPException(503, "Índice de partições inválido.")
    paths = []
    for item in entries:
        if not isinstance(item, dict) or item.get("day") != day.isoformat():
            continue
        relative = item.get("path")
        if not isinstance(relative, str):
            raise HTTPException(503, "Caminho de partição inválido.")
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise HTTPException(503, "Partição publicada ausente ou fora do armazenamento.")
        paths.append(str(path))
    return paths


@app.get("/")
def index(source: str = "dukascopy") -> HTMLResponse:
    if source not in {"dukascopy", "fusion"}:
        raise HTTPException(404, "Fonte de histórico não encontrada.")
    html = (ROOT / "history.html").read_text(encoding="utf-8")
    if source == "fusion":
        html = html.replace("Dukascopy: acompanhamento anual", "Fusion Markets · MT5: acompanhamento anual")
        html = html.replace("dukascopy-source selected", "dukascopy-source ")
        html = html.replace("fusion-source \"", "fusion-source selected\"")
        html = html.replace("Amostra por dia UTC", "Amostra por dia do servidor Fusion")
        html = html.replace("Horas sem negociação confirmadas pela fonte contam como processadas.",
                            "Horários Fusion são preservados como hora do servidor da corretora.")
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})


@app.get("/history", include_in_schema=False)
def legacy_history(source: str = "dukascopy") -> HTMLResponse:
    return index(source)


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(ROOT / "docs" / "assets" / "lotus-icon.png", media_type="image/png")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "7lotus-history"}


@app.get("/api/status")
def status() -> dict[str, Any]:
    root = data_root()
    collection = collection_status(root)
    release = published_release(root)
    if not root.is_dir():
        state, message = "storage_missing", "Armazenamento não encontrado. Configure LOTUS_DATA_ROOT para o diretório compartilhado."
    elif not release["available"]:
        state, message = "release_missing", release["reason"]
    else:
        state, message = "ready", "Release publicado disponível para consulta."
    summary = ({key: release["manifest"].get(key) for key in
                ("coverage_start", "coverage_end", "ticks", "source", "created_at_utc")}
               if release["available"] else None)
    return {"state": state, "message": message, "data_root": str(root),
            "collection": collection,
            "release": {"available": release["available"], "version": release.get("version"), "summary": summary}}


@app.get("/api/history/progress")
def progress(source: str = "dukascopy") -> dict[str, Any]:
    if source == "dukascopy":
        return load_dukascopy_progress(data_root())
    if source == "fusion":
        spool = Path(os.getenv("LOTUS_FUSION_TICK_SPOOL_ROOT", "/home/codexops/.local/share/mt5-wine/drive_c/users/codexops/AppData/Roaming/MetaQuotes/Terminal/Common/Files"))
        collector = os.getenv("LOTUS_FUSION_HISTORY_COLLECTOR_ID", "2lotus-fusion-demo-history-v1")
        return load_fusion_progress(spool, collector)
    raise HTTPException(404, "Fonte de histórico não encontrada.")


@app.get("/api/fusion/candles/status")
def fusion_candles_status(timeframe: str = Query("M5", pattern="^(M1|M5)$")) -> dict[str, Any]:
    release = fusion_release(data_root(), timeframe=timeframe)
    if not release["available"]:
        return {"available": False, "reason": release["reason"], "time_basis": "broker_server_time"}
    return {"available": True, **release["manifest"]}


@app.get("/api/fusion/candles")
def fusion_candles(day: date, timeframe: str = Query("M5", pattern="^(M1|M5)$")) -> dict[str, Any]:
    try:
        return read_fusion_day(data_root(), day, timeframe=timeframe)
    except FusionCandleError as exc:
        raise HTTPException(503, str(exc)) from exc


@app.get("/api/fusion/candles/range")
def fusion_candles_range(start: date, end: date,
                         resolution: str = Query("5m", pattern="^(1m|5m|1h|1d)$")) -> dict[str, Any]:
    from fusion_candles import read_range
    try:
        return read_range(data_root(), start, end, resolution=resolution)
    except FusionCandleError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/api/candles")
def candles(day: date, resolution: str = Query("5m", pattern="^(1m|5m|1h|1d)$")) -> dict[str, Any]:
    root = data_root()
    release = published_release(root)
    if not release["available"]:
        raise HTTPException(503, release["reason"])
    paths = validated_partitions(root, release["manifest"], day, resolution)
    if not paths:
        return {"day": day.isoformat(), "resolution": resolution, "items": [], "version": release["version"]}
    try:
        with duckdb.connect(":memory:") as db:
            rows = db.execute(
                "SELECT t,o,h,l,c,coalesce(bid_volume,0)+coalesce(ask_volume,0) "
                "FROM read_parquet(?) ORDER BY t LIMIT 1500", [paths]
            ).fetchall()
    except duckdb.Error as exc:
        raise HTTPException(503, "Não foi possível ler a agregação publicada.") from exc
    return {"day": day.isoformat(), "resolution": resolution, "version": release["version"],
            "items": [{"timestamp_ms": t, "open": float(o), "high": float(h), "low": float(l),
                       "close": float(c), "volume": float(volume)}
                      for t, o, h, l, c, volume in rows]}


@app.get("/api/ticks")
def ticks(day: date, limit: int = Query(100, ge=1, le=500)) -> dict[str, Any]:
    root = data_root()
    release = published_release(root)
    if not release["available"]:
        raise HTTPException(503, release["reason"])
    paths = validated_partitions(root, release["manifest"], day, "ticks")
    if not paths:
        return {"day": day.isoformat(), "items": [], "version": release["version"]}
    start = int(datetime.combine(day, datetime.min.time(), tzinfo=UTC).timestamp() * 1000)
    end = start + int(timedelta(days=1).total_seconds() * 1000)
    try:
        with duckdb.connect(":memory:") as db:
            rows = db.execute(
                "SELECT timestamp_ms,bid,ask,bid_volume,ask_volume FROM read_parquet(?) "
                "WHERE timestamp_ms >= ? AND timestamp_ms < ? ORDER BY timestamp_ms LIMIT ?",
                [paths, start, end, limit],
            ).fetchall()
    except duckdb.Error as exc:
        raise HTTPException(503, "Não foi possível ler os ticks publicados.") from exc
    return {"day": day.isoformat(), "version": release["version"],
            "items": [{"timestamp_ms": t, "bid": float(bid), "ask": float(ask),
                       "spread": float(ask - bid), "bid_volume": float(bid_volume),
                       "ask_volume": float(ask_volume)}
                      for t, bid, ask, bid_volume, ask_volume in rows]}

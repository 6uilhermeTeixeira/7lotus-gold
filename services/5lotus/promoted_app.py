"""Read-only catalog of individually promoted strategies."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from promoted_pages import catalog_page, comparison_page, results_page, simulator_page


ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "catalog"
app = FastAPI(title="5lotus Promoted Strategies")


def entries() -> list[dict]:
    result = []
    seen = set()
    for path in sorted(CATALOG.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        strategy_id = record["id"]
        if not isinstance(strategy_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", strategy_id):
            raise ValueError(f"invalid strategy id: {path.name}")
        if strategy_id in seen:
            raise ValueError(f"duplicate strategy id: {strategy_id}")
        seen.add(strategy_id)
        profile_path = ROOT / "profiles" / f"{record['id']}.json"
        if not profile_path.is_file():
            raise ValueError(f"missing profile: {record['id']}")
        digest = hashlib.sha256(profile_path.read_bytes()).hexdigest()
        if record.get("profile_sha256") != digest or not record.get("review_ref") or not record.get("source_ref"):
            raise ValueError(f"invalid promotion: {record['id']}")
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        if profile.get("id") != record["id"] or profile.get("version") != record["version"]:
            raise ValueError(f"profile mismatch: {record['id']}")
        unsigned = dict(profile)
        expected = unsigned.pop("sha256", None)
        canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
        if expected != hashlib.sha256(canonical).hexdigest():
            raise ValueError(f"invalid profile digest: {record['id']}")
        result.append(record)
    return result


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/strategies")
def strategies() -> dict:
    try:
        return {"strategies": entries()}
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def page_items() -> list[tuple[dict, dict]]:
    try:
        records = entries()
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return [
        (record, json.loads((ROOT / "profiles" / f"{record['id']}.json").read_text(encoding="utf-8")))
        for record in records
    ]


@app.get("/", response_class=HTMLResponse)
@app.get("/strategies", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return catalog_page(page_items())


@app.get("/compare", response_class=HTMLResponse)
def compare() -> HTMLResponse:
    return comparison_page(page_items())


@app.get("/results/{strategy_id}", response_class=HTMLResponse)
def results(strategy_id: str) -> HTMLResponse:
    for record, profile in page_items():
        if record["id"] == strategy_id:
            return results_page(record, profile)
    raise HTTPException(status_code=404, detail="Estratégia promovida não encontrada")


@app.get("/growth-simulator", response_class=HTMLResponse)
def growth_simulator() -> HTMLResponse:
    return simulator_page(page_items())

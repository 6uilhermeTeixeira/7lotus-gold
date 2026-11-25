import json
import sqlite3
from datetime import UTC, datetime

import duckdb
import pytest
from fastapi.testclient import TestClient

from fusion_candles import FusionCandleError, import_csv
from history_app import app

client = TestClient(app)


def test_missing_storage_is_explicit_and_research_routes_are_absent(tmp_path, monkeypatch):
    monkeypatch.setenv("LOTUS_DATA_ROOT", str(tmp_path / "missing"))
    page = client.get("/")
    assert page.status_code == 200
    assert "Histórico do ouro" in page.text
    assert 'class="app-sidebar"' in page.text
    assert 'class="source-panel panel"' in page.text
    assert "Conta" not in page.text
    assert "Estratégias" not in page.text
    assert client.get("/static/admin-shell.css").status_code == 200
    assert client.get("/api/history/progress").json()["available"] is False
    assert client.get("/history?source=fusion").status_code == 200
    assert "Fusion Markets · MT5: acompanhamento anual" in client.get("/history?source=fusion").text
    assert client.get("/account").status_code == 404
    assert client.get("/decision").status_code == 404
    status = client.get("/api/status").json()
    assert status["state"] == "storage_missing"
    assert status["release"]["available"] is False
    assert client.get("/api/ticks", params={"day": "2026-11-18"}).status_code == 503


def test_published_history_can_be_read_without_modifying_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("LOTUS_DATA_ROOT", str(tmp_path))
    day = "2026-11-18"
    tick_time = int(datetime(2026, 11, 18, tzinfo=UTC).timestamp() * 1000)
    manifest_dir = tmp_path / "manifests"
    manifest_dir.mkdir()
    with sqlite3.connect(manifest_dir / "dukascopy.sqlite3") as db:
        db.execute("CREATE TABLE downloads (instrument TEXT, hour_utc TEXT, status TEXT)")
        db.execute("INSERT INTO downloads VALUES ('XAUUSD', ?, 'downloaded')", (day + "T00:00:00",))
    tick_file = tmp_path / "ticks.parquet"
    candle_file = tmp_path / "candles.parquet"
    with duckdb.connect(":memory:") as db:
        db.execute("CREATE TABLE ticks AS SELECT ?::BIGINT AS timestamp_ms, 2500.0 AS bid, 2500.2 AS ask, 1.0 AS bid_volume, 2.0 AS ask_volume", [tick_time])
        db.execute("CREATE TABLE candles AS SELECT ?::BIGINT AS t, 2500.0 AS o, 2501.0 AS h, 2499.0 AS l, 2500.5 AS c, 1.0 AS bid_volume, 2.0 AS ask_volume", [tick_time])
        db.execute(f"COPY ticks TO '{tick_file}' (FORMAT PARQUET)")
        db.execute(f"COPY candles TO '{candle_file}' (FORMAT PARQUET)")
    version = "test-release"
    release_dir = tmp_path / "releases" / version
    release_dir.mkdir(parents=True)
    (tmp_path / "releases" / "CURRENT").write_text(version)
    (release_dir / "manifest.json").write_text(json.dumps({
        "dataset_version": version, "schema_version": "xauusd-ticks-v1",
        "release_status": "published", "instrument": "XAUUSD", "source": "dukascopy",
        "coverage_start": day, "coverage_end": day, "ticks": 1,
        "partitions": [{"day": day, "path": tick_file.name}],
        "aggregations": {"5m": [{"day": day, "path": candle_file.name}]},
    }))
    status = client.get("/api/status").json()
    assert status["state"] == "ready"
    assert status["collection"]["hours"] == 1
    assert client.get("/api/candles", params={"day": day}).json()["items"][0]["close"] == 2500.5
    assert client.get("/api/ticks", params={"day": day}).json()["items"][0]["spread"] == pytest.approx(0.2)
    assert client.get("/api/ticks", params={"day": day, "limit": 501}).status_code == 422
    assert client.get("/api/candles", params={"day": day, "resolution": "bad"}).status_code == 422
    assert set(tmp_path.rglob("*.parquet")) == {tick_file, candle_file}


def test_fusion_m5_export_is_imported_with_broker_time_and_queried(tmp_path, monkeypatch):
    monkeypatch.setenv("LOTUS_DATA_ROOT", str(tmp_path / "storage"))
    source = tmp_path / "XAUUSD-M5-candles.ready.csv"
    source.write_text(
        "server_time,open,high,low,close,tick_volume,spread_points,real_volume\n"
        "2026.11.18 00:05:00,2501,2502,2500,2501.5,8,12,0\n"
        "2026.11.18 00:00:00,2500,2501,2499,2500.5,7,11,0\n",
        encoding="utf-8",
    )
    manifest = import_csv(source, tmp_path / "storage", server="FusionMarkets-Demo")
    assert manifest["rows"] == 2
    assert manifest["time_basis"] == "broker_server_time"
    status = client.get("/api/fusion/candles/status").json()
    assert status["available"] is True
    assert status["server"] == "FusionMarkets-Demo"
    rows = client.get("/api/fusion/candles", params={"day": "2026-11-18"}).json()["items"]
    assert [row["server_time"] for row in rows] == ["2026-11-18 00:00:00", "2026-11-18 00:05:00"]
    assert rows[0]["close"] == 2500.5
    assert client.get("/api/fusion/candles", params={"day": "2026-11-17"}).json()["items"] == []
    assert import_csv(source, tmp_path / "storage", server="FusionMarkets-Demo")["version"] == manifest["version"]


def test_fusion_import_rejects_unfinished_and_invalid_candles(tmp_path):
    source = tmp_path / "candles.part.csv"
    source.write_text("server_time,open,high,low,close,tick_volume,spread_points,real_volume\n")
    with pytest.raises(FusionCandleError, match="ready.csv"):
        import_csv(source, tmp_path / "storage")
    ready = tmp_path / "candles.ready.csv"
    ready.write_text(
        "server_time,open,high,low,close,tick_volume,spread_points,real_volume\n"
        "2026.11.18 00:00:00,2500,2499,2498,2501,7,11,0\n",
        encoding="utf-8",
    )
    with pytest.raises(FusionCandleError, match="Linha 2"):
        import_csv(ready, tmp_path / "storage")
    assert not (tmp_path / "storage" / "fusion-candles" / "releases" / "CURRENT").exists()

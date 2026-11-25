import json
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import unittest

from app.fusion_research import open_fusion_release
from app.local_dataset import DatasetError
from app.zigzag_m1_research import replay


class FusionResearchTest(unittest.TestCase):
    def test_rejects_mismatched_release(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder) / "m1" / "releases"
            version = "a" * 16
            release = base / version
            release.mkdir(parents=True)
            (base / "CURRENT").write_text(version)
            (release / "candles.parquet").write_bytes(b"fixture")
            (release / "manifest.json").write_text(json.dumps({
                "version": version, "timeframe": "M5", "schema_version": "fusion-m5-candles-v1",
                "canonical_symbol": "XAUUSD", "time_basis": "broker_server_time",
            }))
            with self.assertRaises(DatasetError):
                open_fusion_release(Path(folder), "M1")

    def test_m30_signal_uses_completed_bars_and_stop_wins_ambiguous_m1(self):
        start = datetime(2026, 1, 5)
        # Pivot high at the third M30 bar is confirmed by two subsequent bars.
        highs = [10, 12, 15, 12, 11, 12, 16, 30]
        closes = [9, 11, 14, 11, 10, 11, 16, 16]
        rows = [((start + timedelta(minutes=30 * i)).isoformat(sep=" "),
                 16 if i == 7 else closes[i], highs[i], 10 if i == 7 else 8,
                 closes[i], 0) for i in range(8)]
        result = replay(rows, year=2026)
        self.assertEqual(result["trades_count"], 1)
        self.assertEqual(result["trades"][0]["opened_server_time"], rows[7][0])
        self.assertEqual(result["trades"][0]["reason"], "stop")
        self.assertLess(result["trades"][0]["net_pnl"], 0)


if __name__ == "__main__":
    unittest.main()

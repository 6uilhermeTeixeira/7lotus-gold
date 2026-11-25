"""Build a pinned composition from reviewed 5lotus profiles.

This is a provenance artifact. The runner must explicitly support its routing
policy before it can become an active strategy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMOTED = ROOT.parent / "5lotus"
sys.path.insert(0, str(PROMOTED))
from promoted_app import entries  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--composition", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    composition = json.loads(args.composition.read_text(encoding="utf-8"))
    if composition.get("schema_version") != "1.0" or not composition.get("id") or not composition.get("version"):
        raise SystemExit("invalid composition identity")
    if composition.get("execution_enabled") is not False:
        raise SystemExit("composition must start with execution_enabled=false")
    if composition.get("routing_policy") not in {"shadow_only"}:
        raise SystemExit("routing policy has not been validated for runner execution")
    catalog = {record["id"]: record for record in entries()}
    approved = {strategy_id: record for strategy_id, record in catalog.items() if record.get("composition_eligible", True)}
    selected = composition.get("strategies", [])
    if not selected or len(selected) != len(set(selected)):
        raise SystemExit("composition requires distinct promoted strategies")
    for strategy_id in selected:
        if strategy_id in catalog and strategy_id not in approved:
            raise SystemExit(f"strategy is not eligible for composition yet: {strategy_id}")
        if strategy_id not in approved:
            raise SystemExit(f"strategy is not promoted: {strategy_id}")
    manifest = {"schema_version": "1.0", "source": "4lotus", "composition": composition,
                "dependencies": [approved[strategy_id] for strategy_id in selected]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
        for strategy_id in selected:
            path = PROMOTED / "profiles" / f"{strategy_id}.json"
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != approved[strategy_id]["profile_sha256"]:
                raise SystemExit(f"profile changed during build: {strategy_id}")
            archive.write(path, f"strategies/{path.name}")


if __name__ == "__main__":
    main()

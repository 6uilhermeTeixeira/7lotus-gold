"""Package reviewed individual profiles without activating them."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from promoted_app import entries  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = [record for record in entries() if record.get("composition_eligible", True)]
    if not records:
        raise SystemExit("no composition-eligible promoted strategies in catalog")
    manifest = {"schema_version": "1.0", "source": "5lotus", "strategies": records}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, sort_keys=True, indent=2))
        for record in records:
            path = ROOT / "profiles" / f"{record['id']}.json"
            if hashlib.sha256(path.read_bytes()).hexdigest() != record["profile_sha256"]:
                raise SystemExit(f"profile changed during build: {record['id']}")
            archive.write(path, f"strategies/{path.name}")


if __name__ == "__main__":
    main()

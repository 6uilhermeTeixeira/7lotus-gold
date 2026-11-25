"""Canonical strategy IDs and compatibility aliases for persisted data."""

from __future__ import annotations

import json
from pathlib import Path


_IDENTITIES_PATH = Path(__file__).parents[1] / "data" / "strategy-identities.json"
_IDENTITIES = json.loads(_IDENTITIES_PATH.read_text(encoding="utf-8"))["strategies"]
LEGACY_IDS_BY_CANONICAL_ID = {
    item["canonical_id"]: tuple(item.get("legacy_ids", ()))
    for item in _IDENTITIES
}
CANONICAL_ID_BY_LEGACY_ID = {
    legacy_id: canonical_id
    for canonical_id, legacy_ids in LEGACY_IDS_BY_CANONICAL_ID.items()
    for legacy_id in legacy_ids
}


def canonical_strategy_id(strategy_id: str) -> str:
    return CANONICAL_ID_BY_LEGACY_ID.get(strategy_id, strategy_id)


def legacy_strategy_ids(strategy_id: str) -> tuple[str, ...]:
    return LEGACY_IDS_BY_CANONICAL_ID.get(canonical_strategy_id(strategy_id), ())

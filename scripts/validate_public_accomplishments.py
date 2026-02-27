#!/usr/bin/env python3
"""
Validate website/accomplishments.yml against claims/CLAIM_STATUS_MATRIX.yml.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "claims" / "CLAIM_STATUS_MATRIX.yml"
ACCOMPLISH_PATH = ROOT / "website" / "accomplishments.yml"


def _read_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return {}
    return loaded


def main() -> int:
    errors: list[str] = []
    if not MATRIX_PATH.exists():
        print(f"ERROR: missing {MATRIX_PATH}")
        return 1
    if not ACCOMPLISH_PATH.exists():
        print(f"ERROR: missing {ACCOMPLISH_PATH}")
        return 1

    matrix = _read_yaml(MATRIX_PATH)
    accom = _read_yaml(ACCOMPLISH_PATH)
    rows = matrix.get("rows", {})
    cards = accom.get("cards", [])

    if not isinstance(rows, dict):
        print("ERROR: matrix rows missing/invalid")
        return 1
    if not isinstance(cards, list):
        print("ERROR: accomplishments cards missing/invalid")
        return 1

    seen_card_ids: set[str] = set()
    for idx, card in enumerate(cards):
        if not isinstance(card, dict):
            errors.append(f"card[{idx}] is not a mapping")
            continue
        card_id = str(card.get("card_id", "")).strip()
        claim_id = str(card.get("claim_id", "")).strip()
        status = str(card.get("status", "")).strip()
        evidence = card.get("evidence", {})
        if not card_id:
            errors.append(f"card[{idx}] missing card_id")
        elif card_id in seen_card_ids:
            errors.append(f"duplicate card_id: {card_id}")
        else:
            seen_card_ids.add(card_id)
        if not claim_id:
            errors.append(f"{card_id or f'card[{idx}]'} missing claim_id")
            continue
        if claim_id not in rows:
            errors.append(f"{card_id}: unknown claim_id {claim_id}")
            continue
        matrix_status = str(rows[claim_id].get("status", ""))
        if status != matrix_status:
            errors.append(f"{card_id}: status mismatch for {claim_id}: card={status}, matrix={matrix_status}")
        if matrix_status != "supported" and not card.get("gap_metric"):
            errors.append(f"{card_id}: non-supported claim must include gap_metric")
        if not isinstance(evidence, dict) or not evidence.get("claim_file"):
            errors.append(f"{card_id}: evidence.claim_file required")

    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"OK: validated {len(cards)} accomplishment cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

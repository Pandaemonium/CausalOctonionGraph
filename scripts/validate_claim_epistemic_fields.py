#!/usr/bin/env python3
"""
Validate epistemic governance fields in claims/*.yml.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CLAIMS_DIR = ROOT / "claims"
MATRIX_NAME = "CLAIM_STATUS_MATRIX.yml"

ALLOWED_DERIVATION = {"core_derived", "bridge_assumed", "falsified", "untested"}


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"WARN: skipping malformed claim YAML: {path.name} ({exc})")
        return {}
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _is_nonempty_str(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _extract_claim_id(path: Path, data: dict[str, Any]) -> str:
    for key in ("id", "claim_id", "name"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return path.stem.upper()


def main() -> int:
    errors: list[str] = []
    validated = 0
    for path in sorted(CLAIMS_DIR.glob("*.yml")):
        if path.name == MATRIX_NAME:
            continue

        data = _read_yaml(path)
        if not data:
            continue

        claim_id = _extract_claim_id(path, data)
        validated += 1

        if "derivation_status" not in data:
            errors.append(f"{claim_id}: missing derivation_status")
            continue
        if "bridge_assumptions" not in data:
            errors.append(f"{claim_id}: missing bridge_assumptions")
            continue
        if "falsification_condition" not in data:
            errors.append(f"{claim_id}: missing falsification_condition")
            continue

        derivation_status = data.get("derivation_status")
        bridge_assumptions = data.get("bridge_assumptions")
        falsification_condition = data.get("falsification_condition")

        if derivation_status not in ALLOWED_DERIVATION:
            errors.append(f"{claim_id}: invalid derivation_status '{derivation_status}'")

        if not isinstance(bridge_assumptions, list):
            errors.append(f"{claim_id}: bridge_assumptions must be a list")
        else:
            bad_items = [x for x in bridge_assumptions if not _is_nonempty_str(x)]
            if bad_items:
                errors.append(f"{claim_id}: bridge_assumptions contains non-string/empty entries")

        if not _is_nonempty_str(falsification_condition):
            errors.append(f"{claim_id}: falsification_condition must be non-empty string")

        if derivation_status == "core_derived" and isinstance(bridge_assumptions, list) and bridge_assumptions:
            errors.append(f"{claim_id}: core_derived requires empty bridge_assumptions")

        if derivation_status == "bridge_assumed" and isinstance(bridge_assumptions, list) and not bridge_assumptions:
            errors.append(f"{claim_id}: bridge_assumed requires non-empty bridge_assumptions")

    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"OK: validated epistemic fields for {validated} claim file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


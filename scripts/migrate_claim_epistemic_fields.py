#!/usr/bin/env python3
"""
Backfill epistemic governance fields in claims/*.yml.

Adds (if missing):
1) derivation_status
2) bridge_assumptions
3) falsification_condition
"""

from __future__ import annotations

import argparse
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


def _normalized_status(data: dict[str, Any]) -> str:
    raw = data.get("status")
    if not isinstance(raw, str):
        return "stub"
    return raw.strip().lower()


def _default_derivation_status(status: str) -> str:
    if status == "falsified":
        return "falsified"
    if status in {"supported", "proved", "partial"}:
        return "bridge_assumed"
    return "untested"


def _default_falsification_condition(status: str) -> str:
    if status in {"stub", "active_hypothesis", "active", "open", "hypothesis"}:
        return "Claim is falsified if deterministic tests contradict the stated claim conditions."
    return (
        "Claim is falsified if replayable evidence and deterministic verification fail to reproduce "
        "the stated prediction or constraint."
    )


def _normalize_derivation(value: Any, status: str) -> str:
    if isinstance(value, str):
        v = value.strip()
        if v in ALLOWED_DERIVATION:
            return v
    return _default_derivation_status(status)


def _normalize_bridge_assumptions(value: Any, derivation_status: str) -> list[str]:
    out: list[str] = []
    if isinstance(value, list):
        out = [str(v).strip() for v in value if isinstance(v, str) and str(v).strip()]
    elif isinstance(value, str) and value.strip():
        out = [value.strip()]

    if derivation_status == "bridge_assumed" and not out:
        return ["not_yet_documented_bridge_assumption"]
    if derivation_status != "bridge_assumed":
        return out
    return out


def _normalize_falsification_condition(value: Any, status: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return _default_falsification_condition(status)


def migrate_claim(path: Path) -> tuple[bool, bool]:
    """
    Returns (processed, changed).
    """
    data = _read_yaml(path)
    if not data:
        return False, False

    status = _normalized_status(data)
    before = yaml.safe_dump(data, sort_keys=False)

    derivation_status = _normalize_derivation(data.get("derivation_status"), status)
    bridge_assumptions = _normalize_bridge_assumptions(data.get("bridge_assumptions"), derivation_status)
    falsification_condition = _normalize_falsification_condition(data.get("falsification_condition"), status)

    data["derivation_status"] = derivation_status
    data["bridge_assumptions"] = bridge_assumptions
    data["falsification_condition"] = falsification_condition

    after = yaml.safe_dump(data, sort_keys=False)
    changed = before != after
    if changed:
        path.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=False, width=120),
            encoding="utf-8",
        )
    return True, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write back changes in place (default: dry-run).",
    )
    args = parser.parse_args()

    processed = 0
    changed = 0
    candidate_changes: list[str] = []
    for path in sorted(CLAIMS_DIR.glob("*.yml")):
        if path.name == MATRIX_NAME:
            continue
        data = _read_yaml(path)
        if not data:
            continue
        status = _normalized_status(data)
        derivation_status = _normalize_derivation(data.get("derivation_status"), status)
        bridge_assumptions = _normalize_bridge_assumptions(data.get("bridge_assumptions"), derivation_status)
        falsification_condition = _normalize_falsification_condition(data.get("falsification_condition"), status)

        snapshot = dict(data)
        snapshot["derivation_status"] = derivation_status
        snapshot["bridge_assumptions"] = bridge_assumptions
        snapshot["falsification_condition"] = falsification_condition

        if yaml.safe_dump(snapshot, sort_keys=False) != yaml.safe_dump(data, sort_keys=False):
            candidate_changes.append(path.name)

    if not args.write:
        print(f"Dry run: {len(candidate_changes)} claim file(s) need epistemic-field backfill.")
        for name in candidate_changes:
            print(f"- {name}")
        print("Re-run with --write to apply.")
        return 0

    for path in sorted(CLAIMS_DIR.glob("*.yml")):
        if path.name == MATRIX_NAME:
            continue
        p, c = migrate_claim(path)
        if not p:
            continue
        processed += 1
        changed += int(c)

    print(f"Processed {processed} claim file(s); updated {changed}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


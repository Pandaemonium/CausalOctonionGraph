#!/usr/bin/env python3
"""
Validate sources/qn_claim_ledger.json governance fields.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "sources" / "qn_claim_ledger.json"

ALLOWED_ROW_STATUS = {"core_derived", "bridge_assumed"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
REQUIRED_ROW_FIELDS = {
    "claim_id",
    "status",
    "assumptions",
    "theorem_refs",
    "tests",
    "confidence",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "generated_at_utc",
    "generated_by",
    "source_script",
    "source_script_sha256",
    "preconditions",
    "claim_count",
    "rows",
}

PLACEHOLDER_PREFIX = "not_yet_lean_backed"


def _split_csv(raw: str) -> set[str]:
    return {x.strip() for x in raw.split(",") if x.strip()}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"ledger root must be an object: {path}")
    return loaded


def _validate_top_level(ledger: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL_FIELDS - set(ledger.keys()))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")

    if ledger.get("schema_version") != "qn_claim_ledger_v1":
        errors.append(f"unsupported schema_version: {ledger.get('schema_version')!r}")

    if not isinstance(ledger.get("rows"), list):
        errors.append("rows must be a list")

    claim_count = ledger.get("claim_count")
    if not isinstance(claim_count, int) or claim_count < 0:
        errors.append("claim_count must be a non-negative integer")

    preconditions = ledger.get("preconditions")
    if not isinstance(preconditions, dict):
        errors.append("preconditions must be an object")
    else:
        for key in ("N_c", "N_gen", "N_w"):
            value = preconditions.get(key)
            if not isinstance(value, int) or value <= 0:
                errors.append(f"preconditions.{key} must be positive integer")

    source_script = ledger.get("source_script")
    if isinstance(source_script, str) and source_script.strip():
        source_path = Path(source_script)
        if not source_path.is_absolute():
            source_path = ROOT / source_path
        if not source_path.exists():
            errors.append(f"source_script path does not exist: {source_script}")
        else:
            expected_hash = ledger.get("source_script_sha256")
            if not isinstance(expected_hash, str) or not expected_hash.strip():
                errors.append("source_script_sha256 must be a non-empty string")
            else:
                actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
                if actual_hash != expected_hash:
                    errors.append("source_script_sha256 does not match source_script contents")
    else:
        errors.append("source_script must be a non-empty string")


def _validate_theorem_ref_exists(theorem_ref: str, errors: list[str], claim_id: str) -> None:
    if theorem_ref.startswith(PLACEHOLDER_PREFIX):
        return
    path_part = theorem_ref.split("#", maxsplit=1)[0]
    if not path_part:
        errors.append(f"{claim_id}: empty theorem ref path in {theorem_ref!r}")
        return
    path = ROOT / path_part
    if not path.exists():
        errors.append(f"{claim_id}: theorem ref path does not exist: {path_part}")


def _validate_test_ref_exists(test_ref: str, errors: list[str], claim_id: str) -> None:
    test_file = test_ref.split("::", maxsplit=1)[0]
    if not test_file:
        errors.append(f"{claim_id}: empty test ref path in {test_ref!r}")
        return
    path = ROOT / test_file
    if not path.exists():
        errors.append(f"{claim_id}: test ref path does not exist: {test_file}")


def _validate_rows(
    ledger: dict[str, Any],
    *,
    require_lean_backed_statuses: set[str],
    errors: list[str],
) -> None:
    rows = ledger.get("rows")
    if not isinstance(rows, list):
        return

    if isinstance(ledger.get("claim_count"), int) and ledger["claim_count"] != len(rows):
        errors.append(f"claim_count={ledger['claim_count']} does not match len(rows)={len(rows)}")

    seen_claim_ids: set[str] = set()
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"rows[{idx}] must be an object")
            continue

        row_missing = sorted(REQUIRED_ROW_FIELDS - set(row.keys()))
        if row_missing:
            errors.append(f"rows[{idx}] missing fields: {', '.join(row_missing)}")
            continue

        claim_id = row.get("claim_id")
        status = row.get("status")
        confidence = row.get("confidence")

        if not isinstance(claim_id, str) or not claim_id.strip():
            errors.append(f"rows[{idx}].claim_id must be a non-empty string")
            continue
        if claim_id in seen_claim_ids:
            errors.append(f"duplicate claim_id: {claim_id}")
        seen_claim_ids.add(claim_id)

        if status not in ALLOWED_ROW_STATUS:
            errors.append(f"{claim_id}: invalid status {status!r}")

        if confidence not in ALLOWED_CONFIDENCE:
            errors.append(f"{claim_id}: invalid confidence {confidence!r}")

        assumptions = row.get("assumptions")
        theorem_refs = row.get("theorem_refs")
        tests = row.get("tests")

        if not isinstance(assumptions, list) or not assumptions or not all(
            isinstance(a, str) and a.strip() for a in assumptions
        ):
            errors.append(f"{claim_id}: assumptions must be non-empty list of strings")

        if not isinstance(theorem_refs, list) or not theorem_refs or not all(
            isinstance(t, str) and t.strip() for t in theorem_refs
        ):
            errors.append(f"{claim_id}: theorem_refs must be non-empty list of strings")
        else:
            for theorem_ref in theorem_refs:
                _validate_theorem_ref_exists(theorem_ref, errors, claim_id)

            if status in require_lean_backed_statuses:
                placeholders = [t for t in theorem_refs if t.startswith(PLACEHOLDER_PREFIX)]
                if placeholders:
                    errors.append(
                        f"{claim_id}: status={status} forbids placeholder theorem_refs: {', '.join(placeholders)}"
                    )

        if not isinstance(tests, list) or not tests or not all(isinstance(t, str) and t.strip() for t in tests):
            errors.append(f"{claim_id}: tests must be non-empty list of strings")
        else:
            for test_ref in tests:
                _validate_test_ref_exists(test_ref, errors, claim_id)


def validate(
    ledger_path: Path,
    *,
    require_lean_backed_statuses: set[str],
) -> list[str]:
    errors: list[str] = []

    if not ledger_path.exists():
        return [f"ledger file not found: {ledger_path}"]

    try:
        ledger = _load_json(ledger_path)
    except ValueError as exc:
        return [str(exc)]

    _validate_top_level(ledger, errors)
    _validate_rows(
        ledger,
        require_lean_backed_statuses=require_lean_backed_statuses,
        errors=errors,
    )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        default=str(DEFAULT_LEDGER),
        help=f"Path to ledger JSON (default: {DEFAULT_LEDGER}).",
    )
    parser.add_argument(
        "--require-lean-backed-statuses",
        default="core_derived",
        help=(
            "Comma-separated row statuses that must not contain placeholder theorem refs. "
            "Default: core_derived"
        ),
    )
    args = parser.parse_args()

    ledger_path = Path(args.path)
    require_statuses = _split_csv(args.require_lean_backed_statuses)
    unknown_statuses = require_statuses - ALLOWED_ROW_STATUS
    if unknown_statuses:
        print(f"ERROR: unknown statuses in --require-lean-backed-statuses: {', '.join(sorted(unknown_statuses))}")
        return 2

    errors = validate(
        ledger_path,
        require_lean_backed_statuses=require_statuses,
    )
    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"OK: {ledger_path} validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

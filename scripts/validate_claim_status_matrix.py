#!/usr/bin/env python3
"""
Validate claims/CLAIM_STATUS_MATRIX.yml against RFC-050 + follow-on metadata gates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CLAIMS_DIR = ROOT / "claims"
MATRIX_PATH = CLAIMS_DIR / "CLAIM_STATUS_MATRIX.yml"

ALLOWED_STATUS = {
    "stub",
    "active_hypothesis",
    "partial",
    "supported_bridge",
    "proved_core",
    # Backward-compatible alias; should be migrated by sync.
    "supported",
    "falsified",
    "superseded",
}
ALLOWED_DERIVATION_STATUS = {"core_derived", "bridge_assumed", "falsified", "untested"}
ALLOWED_PI_OBS_PROFILE = {"minimal", "with_sector"}
ALLOWED_PROJECTION_SENSITIVITY = {"unknown", "insensitive", "sensitive"}
ALLOWED_EQUIVALENCE_MODE = {"none", "static", "one_step", "horizon"}
ALLOWED_CONFINEMENT_STATUS = {"not_applicable", "open", "pass", "fail"}
ALLOWED_SPIN_MODE = {"none", "parity", "label", "algebraic"}
ALLOWED_SPIN_SENSITIVITY = {"unknown", "insensitive", "sensitive"}
ALLOWED_CALIBRATION_MODE = {"native_only", "calibrated"}
ALLOWED_REDUCTION_MODE = {"none", "exact", "approx"}

REQUIRED_FIELDS = [
    # RFC-050 core fields
    "claim_id",
    "status",
    "lean_artifacts",
    "python_artifacts",
    "battery_artifacts",
    "motif_id",
    "rule_profile",
    "pi_obs_profile",
    "projection_sensitivity",
    "equivalence_mode",
    "evidence_level",
    "derivation_status",
    "bridge_assumptions",
    "falsification_condition",
    "last_verified_at",
    "owner_rfc",
    "notes",
    "confinement_gate_status",
    "confinement_artifact",
    "ensemble_policy_id",
    "spin_mode",
    "spin_artifact",
    "spin_sensitivity",
    # RFC-051 / RFC-052 / RFC-053 / RFC-055 extensions
    "scheduler_mode",
    "scheduler_profile_version",
    "many_body_relevant",
    "pair_extraction_mode",
    "reduction_mode",
    "reduction_horizon",
    "reduction_artifact_ref",
    "physical_units_relevant",
    "calibration_mode",
    "scale_profile_id",
    "uncertainty_relevant",
    "entropy_functional_id",
    "entropy_artifact_ref",
]


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"WARN: skipping malformed claim YAML: {path.name} ({exc})")
        return {}
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _extract_claim_id(path: Path, data: dict[str, Any]) -> str:
    for key in ("id", "claim_id", "name"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return path.stem.upper()


def _collect_claim_ids_from_files() -> set[str]:
    claim_ids: set[str] = set()
    for path in sorted(CLAIMS_DIR.glob("*.yml")):
        if path.name == MATRIX_PATH.name:
            continue
        claim_ids.add(_extract_claim_id(path, _read_yaml(path)))
    return claim_ids


def _collect_claim_docs_by_id() -> dict[str, list[dict[str, Any]]]:
    docs: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(CLAIMS_DIR.glob("*.yml")):
        if path.name == MATRIX_PATH.name:
            continue
        data = _read_yaml(path)
        claim_id = _extract_claim_id(path, data)
        docs.setdefault(claim_id, []).append(data)
    return docs


def _is_nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_row_key(claim_id: str, row: dict[str, Any], errors: list[str]) -> None:
    row_claim_id = row.get("claim_id")
    if row_claim_id != claim_id:
        errors.append(f"{claim_id}: row key and claim_id mismatch ({row_claim_id!r})")


def _validate_required_fields(claim_id: str, row: dict[str, Any], errors: list[str]) -> None:
    for field in REQUIRED_FIELDS:
        if field not in row:
            errors.append(f"{claim_id}: missing required field '{field}'")


def _validate_enums(claim_id: str, row: dict[str, Any], errors: list[str]) -> None:
    status = row.get("status")
    if status not in ALLOWED_STATUS:
        errors.append(f"{claim_id}: invalid status '{status}'")

    pi_obs = row.get("pi_obs_profile")
    if pi_obs not in ALLOWED_PI_OBS_PROFILE:
        errors.append(f"{claim_id}: invalid pi_obs_profile '{pi_obs}'")

    proj = row.get("projection_sensitivity")
    if proj not in ALLOWED_PROJECTION_SENSITIVITY:
        errors.append(f"{claim_id}: invalid projection_sensitivity '{proj}'")

    eq_mode = row.get("equivalence_mode")
    if eq_mode not in ALLOWED_EQUIVALENCE_MODE:
        errors.append(f"{claim_id}: invalid equivalence_mode '{eq_mode}'")

    conf_status = row.get("confinement_gate_status")
    if conf_status not in ALLOWED_CONFINEMENT_STATUS:
        errors.append(f"{claim_id}: invalid confinement_gate_status '{conf_status}'")

    spin_mode = row.get("spin_mode")
    if spin_mode not in ALLOWED_SPIN_MODE:
        errors.append(f"{claim_id}: invalid spin_mode '{spin_mode}'")

    spin_sensitivity = row.get("spin_sensitivity")
    if spin_sensitivity not in ALLOWED_SPIN_SENSITIVITY:
        errors.append(f"{claim_id}: invalid spin_sensitivity '{spin_sensitivity}'")

    calibration_mode = row.get("calibration_mode")
    if calibration_mode not in ALLOWED_CALIBRATION_MODE:
        errors.append(f"{claim_id}: invalid calibration_mode '{calibration_mode}'")

    reduction_mode = row.get("reduction_mode")
    if reduction_mode not in ALLOWED_REDUCTION_MODE:
        errors.append(f"{claim_id}: invalid reduction_mode '{reduction_mode}'")

    derivation_status = row.get("derivation_status")
    if derivation_status not in ALLOWED_DERIVATION_STATUS:
        errors.append(f"{claim_id}: invalid derivation_status '{derivation_status}'")


def _validate_semantics(
    claim_id: str,
    row: dict[str, Any],
    errors: list[str],
    source_docs: dict[str, list[dict[str, Any]]],
) -> None:
    bridge_assumptions = row.get("bridge_assumptions")
    if not isinstance(bridge_assumptions, list):
        errors.append(f"{claim_id}: bridge_assumptions must be a list")
        bridge_assumptions = []
    elif not all(_is_nonempty_str(x) for x in bridge_assumptions):
        errors.append(f"{claim_id}: bridge_assumptions entries must be non-empty strings")

    falsification_condition = row.get("falsification_condition")
    if not _is_nonempty_str(falsification_condition):
        errors.append(f"{claim_id}: falsification_condition must be non-empty string")

    derivation_status = row.get("derivation_status")
    if derivation_status == "core_derived" and bridge_assumptions:
        errors.append(f"{claim_id}: core_derived requires empty bridge_assumptions")
    if derivation_status == "bridge_assumed" and not bridge_assumptions:
        errors.append(f"{claim_id}: bridge_assumed requires non-empty bridge_assumptions")

    if row.get("equivalence_mode") != "none" and not _is_nonempty_str(row.get("equivalence_artifact", "")):
        errors.append(f"{claim_id}: equivalence_mode != none requires equivalence_artifact")

    status = row.get("status")
    promoted = status in {"supported", "supported_bridge", "proved_core"}
    if promoted:
        has_any_evidence = bool(row.get("lean_artifacts")) or bool(row.get("python_artifacts")) or bool(
            row.get("battery_artifacts")
        )
        if not has_any_evidence:
            errors.append(f"{claim_id}: promoted status requires at least one evidence artifact list non-empty")
        if str(row.get("evidence_level", "")).strip().lower() == "hypothesis":
            errors.append(f"{claim_id}: promoted status cannot use evidence_level=hypothesis")
        if derivation_status == "untested":
            errors.append(f"{claim_id}: promoted status cannot use derivation_status=untested")
        # Tightened gate: supported claims must have battery evidence.
        if not bool(row.get("battery_artifacts")):
            errors.append(f"{claim_id}: promoted status requires non-empty battery_artifacts")
        # Tightened gate: promoted claims must not keep unknown projection sensitivity.
        if row.get("projection_sensitivity") == "unknown":
            errors.append(f"{claim_id}: promoted status requires projection_sensitivity != unknown")
        # Tightened gate: source claim file must not still report a blocked_reason.
        docs = source_docs.get(claim_id, [])
        for d in docs:
            blocked_reason = d.get("blocked_reason")
            if _is_nonempty_str(blocked_reason):
                errors.append(f"{claim_id}: promoted status conflicts with non-empty blocked_reason in source claim")
                break

    if status == "supported":
        errors.append(f"{claim_id}: legacy status 'supported' is deprecated; use supported_bridge or proved_core")
    if status == "supported_bridge" and derivation_status != "bridge_assumed":
        errors.append(f"{claim_id}: supported_bridge requires derivation_status=bridge_assumed")
    if status == "proved_core":
        if derivation_status != "core_derived":
            errors.append(f"{claim_id}: proved_core requires derivation_status=core_derived")
        if bridge_assumptions:
            errors.append(f"{claim_id}: proved_core requires empty bridge_assumptions")

    confinement_relevant = bool(row.get("confinement_relevant", False))
    if confinement_relevant:
        if row.get("confinement_gate_status") not in {"open", "pass", "fail"}:
            errors.append(f"{claim_id}: confinement_relevant requires confinement_gate_status in open/pass/fail")
        if not _is_nonempty_str(row.get("confinement_artifact", "")):
            errors.append(f"{claim_id}: confinement_relevant requires confinement_artifact")
        if not _is_nonempty_str(row.get("ensemble_policy_id", "")):
            errors.append(f"{claim_id}: confinement_relevant requires ensemble_policy_id")
        if promoted and row.get("confinement_gate_status") != "pass":
            errors.append(f"{claim_id}: promoted confinement-relevant claim requires confinement_gate_status=pass")

    spin_sensitive = bool(row.get("spin_sensitive", False))
    if spin_sensitive:
        if row.get("spin_mode") == "none":
            errors.append(f"{claim_id}: spin_sensitive requires non-none spin_mode")
        if not _is_nonempty_str(row.get("spin_artifact", "")):
            errors.append(f"{claim_id}: spin_sensitive requires spin_artifact")
        if row.get("spin_sensitivity") not in {"insensitive", "sensitive", "unknown"}:
            errors.append(f"{claim_id}: spin_sensitive has invalid spin_sensitivity")
        if promoted and row.get("spin_mode") != "algebraic":
            errors.append(f"{claim_id}: promoted spin-sensitive claim requires spin_mode=algebraic")

    scheduler_mode = row.get("scheduler_mode")
    if not _is_nonempty_str(scheduler_mode):
        errors.append(f"{claim_id}: scheduler_mode is required")

    if not _is_nonempty_str(row.get("scheduler_profile_version")):
        errors.append(f"{claim_id}: scheduler_profile_version is required")

    many_body_relevant = bool(row.get("many_body_relevant", False))
    if many_body_relevant and row.get("pair_extraction_mode") in {"", "not_applicable", None}:
        errors.append(f"{claim_id}: many_body_relevant requires pair_extraction_mode")
    if promoted and many_body_relevant:
        if row.get("reduction_mode") not in {"exact", "approx"}:
            errors.append(f"{claim_id}: promoted many_body_relevant claim requires reduction_mode in exact/approx")
        if not _is_nonempty_str(row.get("reduction_artifact_ref", "")):
            errors.append(f"{claim_id}: promoted many_body_relevant claim requires reduction_artifact_ref")

    reduction_mode = row.get("reduction_mode")
    if reduction_mode in {"exact", "approx"}:
        horizon = row.get("reduction_horizon")
        if not isinstance(horizon, int) or horizon <= 0:
            errors.append(f"{claim_id}: reduction_mode={reduction_mode} requires reduction_horizon > 0")

    physical_units_relevant = bool(row.get("physical_units_relevant", False))
    # Physical-units relevance can be true before calibration is closed; enforce
    # calibrated mode at promotion time.
    if promoted and physical_units_relevant and row.get("calibration_mode") != "calibrated":
        errors.append(f"{claim_id}: promoted physical_units_relevant claim requires calibration_mode=calibrated")
    if row.get("calibration_mode") == "calibrated" and not _is_nonempty_str(row.get("scale_profile_id", "")):
        errors.append(f"{claim_id}: calibration_mode=calibrated requires scale_profile_id")

    uncertainty_relevant = bool(row.get("uncertainty_relevant", False))
    if uncertainty_relevant and not _is_nonempty_str(row.get("entropy_functional_id", "")):
        errors.append(f"{claim_id}: uncertainty_relevant requires entropy_functional_id")
    if promoted and uncertainty_relevant and not _is_nonempty_str(row.get("entropy_artifact_ref", "")):
        errors.append(f"{claim_id}: promoted uncertainty_relevant claim requires entropy_artifact_ref")


def validate_matrix(matrix: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    rows = matrix.get("rows")
    if not isinstance(rows, dict):
        return ["matrix.rows must be a mapping keyed by claim_id"]

    claim_ids_in_files = _collect_claim_ids_from_files()
    source_docs = _collect_claim_docs_by_id()
    row_ids = set(rows.keys())

    missing_rows = sorted(claim_ids_in_files - row_ids)
    if missing_rows:
        errors.append(f"missing matrix rows for claim IDs: {', '.join(missing_rows)}")

    extra_rows = sorted(row_ids - claim_ids_in_files)
    if extra_rows:
        errors.append(f"matrix has rows for unknown claim IDs: {', '.join(extra_rows)}")

    for claim_id in sorted(rows):
        row = rows[claim_id]
        if not isinstance(row, dict):
            errors.append(f"{claim_id}: row must be mapping")
            continue
        _validate_row_key(claim_id, row, errors)
        _validate_required_fields(claim_id, row, errors)
        _validate_enums(claim_id, row, errors)
        _validate_semantics(claim_id, row, errors, source_docs)

    return errors


def main() -> int:
    if not MATRIX_PATH.exists():
        print(f"ERROR: matrix file not found: {MATRIX_PATH}")
        return 1

    matrix = _read_yaml(MATRIX_PATH)
    errors = validate_matrix(matrix)
    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"- {err}")
        return 1

    row_count = len(matrix.get("rows", {}))
    print(f"OK: {MATRIX_PATH} validated ({row_count} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

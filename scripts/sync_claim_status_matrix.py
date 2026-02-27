#!/usr/bin/env python3
"""
Build or refresh claims/CLAIM_STATUS_MATRIX.yml from claims/*.yml.

This is a conservative bootstrap sync:
1. one row per claim_id
2. default governance metadata is explicit
3. duplicate claim IDs are preserved via source_files + notes
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CLAIMS_DIR = ROOT / "claims"
MATRIX_PATH = CLAIMS_DIR / "CLAIM_STATUS_MATRIX.yml"

MATRIX_VERSION = "2.1.0"

ALLOWED_STATUS = {
    "stub",
    "active_hypothesis",
    "partial",
    "supported",
    "falsified",
    "superseded",
}

STATUS_MAP = {
    "open": "active_hypothesis",
    "active": "active_hypothesis",
    "hypothesis": "active_hypothesis",
    "revised_pending": "active_hypothesis",
    # Keep this conservative to avoid automatic status inflation.
    "proved": "partial",
}

# High-priority governance backfill for matrix rows.
# These overrides are intentionally explicit so sync remains deterministic.
CLAIM_BACKFILL: dict[str, dict[str, Any]] = {
    "WEINBERG-UV-001": {
        "motif_id": "ew_mixing_uv_structural_v1",
        "owner_rfc": "rfc/RFC-029_Weinberg_Angle_Gap_Closure.md",
        "projection_sensitivity": "sensitive",
        "battery_artifacts": [
            "calc/test_weinberg_h2_governance.py::test_expected_baseline_values",
            "CausalGraphTheory/WeakMixingObservable.lean",
        ],
        "physical_units_relevant": False,
        "calibration_mode": "native_only",
    },
    "WEINBERG-001": {
        "motif_id": "ew_mixing_projector_v1",
        "owner_rfc": "rfc/RFC-029_Weinberg_Angle_Gap_Closure.md",
        "projection_sensitivity": "sensitive",
        "battery_artifacts": [
            "calc/test_weinberg_h2_governance.py",
            "sources/weinberg_h2_ablation_results.md",
            "sources/weinberg_associator_ensemble_results.md",
        ],
        "physical_units_relevant": True,
        "calibration_mode": "native_only",
    },
    "STRONG-001": {
        "motif_id": "vacuum_stabilizer_ratio_v1",
        "owner_rfc": "rfc/STRONG-001_Closure_Tasklist.md",
        "projection_sensitivity": "sensitive",
        "battery_artifacts": [
            "calc/test_constants.py::TestAlphaStrong::test_alpha_strong_candidate_is_stab_ratio",
            "calc/estimate_alpha_strong.py",
        ],
        "physical_units_relevant": True,
        "calibration_mode": "native_only",
    },
    "LEPTON-001": {
        "motif_id": "furey_lepton_orbit_v1",
        "owner_rfc": "rfc/RFC-034_Electron_Mass_Mechanism.md",
        "battery_artifacts": [
            "calc/test_furey_electron_orbit.py",
            "CausalGraphTheory/LeptonOrbits.lean",
        ],
        "physical_units_relevant": True,
        "calibration_mode": "native_only",
    },
    "PHOTON-001": {
        "motif_id": "vacuum_orbit_colorless_v1",
        "owner_rfc": "rfc/RFC-015_Photon_Energy_COG.md",
        "projection_sensitivity": "insensitive",
        "battery_artifacts": [
            "CausalGraphTheory/PhotonMasslessness.lean",
            "sources/photon_energy_discrete_models.md",
        ],
        "physical_units_relevant": True,
        "calibration_mode": "native_only",
    },
    "ALPHA-001": {
        "motif_id": "u1_phase_penalty_v1",
        "owner_rfc": "rfc/RFC-061_Fine_Structure_Constant_from_Fano_Counting.md",
        "projection_sensitivity": "sensitive",
        "battery_artifacts": [
            "calc/test_constants.py::TestAlphaFineStructure::test_alpha_target_value",
            "CausalGraphTheory/Constants.lean",
        ],
        "physical_units_relevant": True,
        "calibration_mode": "native_only",
    },
    "MASS-001": {
        "motif_id": "tick_mass_drag_v1",
        "owner_rfc": "rfc/RFC-045_Energy_Mass_Observable_Unification.md",
        "projection_sensitivity": "insensitive",
        "battery_artifacts": [
            "calc/test_koide.py",
            "calc/mass_ratios.py",
            "CausalGraphTheory/Mass.lean",
        ],
        "physical_units_relevant": True,
        "calibration_mode": "native_only",
    },
    "MU-001": {
        "motif_id": "proton_electron_drag_ratio_v1",
        "owner_rfc": "rfc/RFC-009_Spinor_Representations_and_Triality_Overhead.md",
        "projection_sensitivity": "sensitive",
        "battery_artifacts": [
            "calc/test_mass_drag_v2.py",
            "calc/mass_drag_v2.py",
            "calc/test_constants.py::TestProtonElectronRatio::test_mu_target_value",
        ],
        "physical_units_relevant": True,
        "calibration_mode": "native_only",
    },
    "GAUGE-001": {
        "motif_id": "vacuum_stabilizer_s4_v1",
        "owner_rfc": "rfc/RFC-017_Vacuum_Stabilizer_Reconciliation.md",
        "projection_sensitivity": "sensitive",
        "battery_artifacts": [
            "calc/test_gauge.py",
            "calc/gauge_check.py",
            "CausalGraphTheory/GaugeGroup.lean",
        ],
    },
}


@dataclass
class ClaimDoc:
    path: Path
    claim_id: str
    data: dict[str, Any]


def _read_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _normalize_status(raw_status: Any) -> str:
    if not isinstance(raw_status, str):
        return "stub"
    s = raw_status.strip().lower()
    s = STATUS_MAP.get(s, s)
    return s if s in ALLOWED_STATUS else "stub"


def _to_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = value.strip()
        return [value] if value else []
    if isinstance(value, list):
        out: list[str] = []
        for v in value:
            if isinstance(v, str) and v.strip():
                out.append(v.strip())
        return out
    return []


def _extract_claim_id(path: Path, data: dict[str, Any]) -> str:
    for key in ("id", "claim_id", "name"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return path.stem.upper()


def _select_canonical(docs: list[ClaimDoc], claim_id: str) -> ClaimDoc:
    exact_name = f"{claim_id}.yml"
    for doc in docs:
        if doc.path.name.lower() == exact_name.lower():
            return doc
    return sorted(docs, key=lambda d: d.path.name.lower())[0]


def _derive_evidence_level(data: dict[str, Any]) -> str:
    has_lean = bool(_to_list(data.get("lean_theorems"))) or bool(data.get("lean_file")) or bool(
        data.get("proof")
    )
    has_python = bool(data.get("python_test")) or bool(data.get("python_check")) or bool(
        _to_list(data.get("simulation_records"))
    )
    if has_lean and has_python:
        return "mixed:lean_proved+python_verified"
    if has_lean:
        return "lean_proved"
    if has_python:
        return "python_verified"
    return "hypothesis"


def _rfc_owner_from_claim(data: dict[str, Any]) -> str:
    depends = _to_list(data.get("depends_on"))
    # depends_on commonly uses claim IDs, not RFC IDs. Keep stable fallback.
    for dep in depends:
        if dep.startswith("RFC-"):
            return f"rfc/{dep}.md"
    return "rfc/MASTER_IMPLEMENTATION_PLAN_V2.md"


def _row_from_claim(claim_id: str, canonical: ClaimDoc, all_docs: list[ClaimDoc]) -> dict[str, Any]:
    data = canonical.data
    source_files = sorted(doc.path.name for doc in all_docs)
    pi_obs = data.get("pi_obs_profile") or data.get("projection_profile") or "minimal"
    if not isinstance(pi_obs, str) or not pi_obs.strip():
        pi_obs = "minimal"
    pi_obs = pi_obs.strip()

    lean_artifacts: list[str] = []
    lean_file = data.get("lean_file") or data.get("proof")
    if isinstance(lean_file, str) and lean_file.strip():
        lean_artifacts.append(lean_file.strip())
    lean_artifacts.extend(_to_list(data.get("lean_theorems")))

    python_artifacts: list[str] = []
    python_test = data.get("python_test")
    python_check = data.get("python_check")
    if isinstance(python_test, str) and python_test.strip():
        python_artifacts.append(python_test.strip())
    if isinstance(python_check, str) and python_check.strip():
        python_artifacts.append(python_check.strip())
    python_artifacts.extend(_to_list(data.get("simulation_records")))

    status = _normalize_status(data.get("status"))
    now = datetime.fromtimestamp(canonical.path.stat().st_mtime, tz=timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )

    note_fragments = [f"source={canonical.path.name}"]
    if len(source_files) > 1:
        note_fragments.append(f"aliases={','.join(source_files)}")

    default_battery_artifacts = sorted(set([*lean_artifacts, *python_artifacts]))

    row = {
        "claim_id": claim_id,
        "status": status,
        "lean_artifacts": lean_artifacts,
        "python_artifacts": python_artifacts,
        "battery_artifacts": default_battery_artifacts,
        "motif_id": "unassigned",
        "rule_profile": "default_multiplicative_markov",
        "pi_obs_profile": pi_obs,
        "projection_sensitivity": str(data.get("projection_sensitivity", "unknown")),
        "equivalence_mode": str(data.get("equivalence_mode", "none")),
        "equivalence_artifact": "",
        "evidence_level": _derive_evidence_level(data),
        "last_verified_at": now,
        "owner_rfc": _rfc_owner_from_claim(data),
        "notes": " | ".join(note_fragments),
        "confinement_relevant": False,
        "confinement_gate_status": "not_applicable",
        "confinement_artifact": "",
        "ensemble_policy_id": "",
        "spin_sensitive": False,
        "spin_mode": "none",
        "spin_artifact": "",
        "spin_sensitivity": "unknown",
        # RFC-051 / RFC-052 / RFC-053 / RFC-055 metadata
        "scheduler_mode": "snapshot_sync_v1",
        "scheduler_profile_version": "v1",
        "many_body_relevant": False,
        "pair_extraction_mode": "not_applicable",
        "reduction_mode": "none",
        "reduction_horizon": 0,
        "reduction_artifact_ref": "",
        "physical_units_relevant": False,
        "calibration_mode": "native_only",
        "scale_profile_id": "",
        "uncertainty_relevant": False,
        "entropy_functional_id": "",
        "entropy_artifact_ref": "",
        "source_files": source_files,
    }

    overrides = CLAIM_BACKFILL.get(claim_id)
    if overrides:
        row.update(overrides)
        row["notes"] = f"{row['notes']} | backfill=priority_v1"

    return row


def build_matrix() -> dict[str, Any]:
    claim_docs_by_id: dict[str, list[ClaimDoc]] = {}
    for path in sorted(CLAIMS_DIR.glob("*.yml")):
        if path.name == MATRIX_PATH.name:
            continue
        data = _read_yaml(path)
        claim_id = _extract_claim_id(path, data)
        claim_docs_by_id.setdefault(claim_id, []).append(ClaimDoc(path=path, claim_id=claim_id, data=data))

    rows: dict[str, Any] = {}
    for claim_id in sorted(claim_docs_by_id):
        docs = claim_docs_by_id[claim_id]
        canonical = _select_canonical(docs, claim_id)
        rows[claim_id] = _row_from_claim(claim_id, canonical, docs)

    return {
        "schema_version": MATRIX_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "row_count": len(rows),
        "rows": rows,
    }


def main() -> int:
    matrix = build_matrix()
    MATRIX_PATH.write_text(
        yaml.safe_dump(matrix, sort_keys=False, allow_unicode=False, width=120),
        encoding="utf-8",
    )
    print(f"Wrote {MATRIX_PATH} with {matrix['row_count']} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

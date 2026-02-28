#!/usr/bin/env python3
"""
Shared contract-gate validation helpers for RFC-080/081/082/083 controls.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


PROMOTED_STATUSES = {"supported", "supported_bridge", "proved_core"}

RUNNING_GATE_CLAIMS = {"WEINBERG-001", "STRONG-001"}
MASS_GATE_CLAIMS = {"MASS-001", "LEPTON-001", "MU-001"}
THETA_GATE_CLAIMS = {"THETA-001"}

ALLOWED_RUNNING_MODE = {"theorem_first", "simulation_first"}
ALLOWED_DISTRIBUTION_MODE = {"fixed_rollout", "stationary_distribution"}
ALLOWED_ORACLE_MODE = {"hard_fail", "two_lane"}
ALLOWED_THETA_CLOSURE_SCOPE = {"structure_first", "full_value_closure"}
ALLOWED_THETA_SKEPTIC_VERDICT = {"pending", "PASS", "PASS_WITH_LIMITS", "FAIL"}


@dataclass(frozen=True)
class GateIssue:
    claim_id: str
    severity: str  # "error" | "warn"
    message: str


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return {"__yaml_error__": str(exc)}
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _read_json(path: Path) -> dict[str, Any]:
    import json

    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
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


def load_claim_docs(claims_dir: Path) -> dict[str, dict[str, Any]]:
    docs: dict[str, dict[str, Any]] = {}
    for path in sorted(claims_dir.glob("*.yml")):
        if path.name == "CLAIM_STATUS_MATRIX.yml":
            continue
        data = _read_yaml(path)
        claim_id = _extract_claim_id(path, data)
        data["__path__"] = str(path)
        docs[claim_id] = data
    return docs


def _is_nonempty_str(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _as_map(v: Any) -> dict[str, Any]:
    return v if isinstance(v, dict) else {}


def _canonical_status(status: Any) -> str:
    s = str(status or "").strip()
    if s == "supported":
        return "supported_bridge"
    return s


def _required_contracts_for_claim(claim_id: str, claim_doc: dict[str, Any]) -> set[str]:
    required: set[str] = set()

    if claim_id in RUNNING_GATE_CLAIMS:
        required.add("rfc080")
    if claim_id in MASS_GATE_CLAIMS:
        required.add("rfc081")
    if claim_id in THETA_GATE_CLAIMS:
        required.add("rfc083")
    if claim_id.startswith("CKM-") or claim_id.startswith("PMNS-"):
        required.add("rfc082")

    gates = _as_map(claim_doc.get("contract_gates"))
    required_from_doc = gates.get("required")
    if isinstance(required_from_doc, list):
        for item in required_from_doc:
            if _is_nonempty_str(item):
                required.add(str(item).strip().lower())

    return required


def _is_waived(gates: dict[str, Any], contract_id: str) -> bool:
    """
    A waiver requires both a non-empty waiver_reason AND an explicit waiver_approved_by
    field naming a human supervisor. A worker-generated waiver_reason alone is insufficient.
    """
    c = _as_map(gates.get(contract_id))
    if not bool(c.get("waived", False)):
        return False
    reason = c.get("waiver_reason")
    approved_by = c.get("waiver_approved_by")
    # Both fields required; automated/self-approval is not sufficient
    return _is_nonempty_str(reason) and _is_nonempty_str(approved_by)


def _validate_rfc080(claim_id: str, gates: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    c = _as_map(gates.get("rfc080"))
    if not c:
        return [f"{claim_id}: missing contract_gates.rfc080 block"]

    policy_id = c.get("policy_id")
    if not _is_nonempty_str(policy_id):
        errs.append(f"{claim_id}: rfc080.policy_id is required")

    running_mode = c.get("running_mode")
    if running_mode not in ALLOWED_RUNNING_MODE:
        errs.append(
            f"{claim_id}: rfc080.running_mode must be one of {sorted(ALLOWED_RUNNING_MODE)}"
        )

    distribution_mode = c.get("distribution_mode")
    if distribution_mode not in ALLOWED_DISTRIBUTION_MODE:
        errs.append(
            f"{claim_id}: rfc080.distribution_mode must be one of {sorted(ALLOWED_DISTRIBUTION_MODE)}"
        )

    if not _is_nonempty_str(c.get("cold_start_policy")):
        errs.append(f"{claim_id}: rfc080.cold_start_policy is required")

    oracle_mode = c.get("oracle_mode")
    if oracle_mode not in ALLOWED_ORACLE_MODE:
        errs.append(
            f"{claim_id}: rfc080.oracle_mode must be one of {sorted(ALLOWED_ORACLE_MODE)}"
        )

    if not _is_nonempty_str(c.get("replay_artifact")):
        errs.append(f"{claim_id}: rfc080.replay_artifact is required")

    return errs


def _validate_rfc081(claim_id: str, gates: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    c = _as_map(gates.get("rfc081"))
    if not c:
        return [f"{claim_id}: missing contract_gates.rfc081 block"]

    if not _is_nonempty_str(c.get("anchor_policy_id")):
        errs.append(f"{claim_id}: rfc081.anchor_policy_id is required")

    if not _is_nonempty_str(c.get("mass_observable_contract_id")):
        errs.append(f"{claim_id}: rfc081.mass_observable_contract_id is required")

    if c.get("anti_circularity_ack") is not True:
        errs.append(f"{claim_id}: rfc081.anti_circularity_ack must be true")

    return errs


def _validate_rfc082(claim_id: str, gates: dict[str, Any], root: Path) -> list[str]:
    errs: list[str] = []
    c = _as_map(gates.get("rfc082"))
    if not c:
        return [f"{claim_id}: missing contract_gates.rfc082 block"]

    if c.get("matrix_first") is not True:
        errs.append(f"{claim_id}: rfc082.matrix_first must be true")

    if c.get("forbid_per_angle_tuning") is not True:
        errs.append(f"{claim_id}: rfc082.forbid_per_angle_tuning must be true")

    matrix_artifact = c.get("matrix_artifact")
    if not _is_nonempty_str(matrix_artifact):
        errs.append(f"{claim_id}: rfc082.matrix_artifact is required")
    else:
        p = root / str(matrix_artifact).strip()
        if not p.exists():
            errs.append(f"{claim_id}: rfc082.matrix_artifact path not found: {matrix_artifact}")

    if not _is_nonempty_str(c.get("basis_ordering_id")):
        errs.append(f"{claim_id}: rfc082.basis_ordering_id is required")

    if not _is_nonempty_str(c.get("phase_gauge_convention_id")):
        errs.append(f"{claim_id}: rfc082.phase_gauge_convention_id is required")

    return errs


def _gate_done(claim_doc: dict[str, Any], gate_id: str) -> bool:
    gates = claim_doc.get("gates")
    if not isinstance(gates, list):
        return False
    for gate in gates:
        if not isinstance(gate, dict):
            continue
        if str(gate.get("id", "")).strip() == gate_id:
            return bool(gate.get("done", False))
    return False


def _validate_rfc083(
    claim_id: str,
    gates: dict[str, Any],
    root: Path,
    status: str,
    claim_doc: dict[str, Any],
) -> list[str]:
    errs: list[str] = []
    c = _as_map(gates.get("rfc083"))
    if not c:
        return [f"{claim_id}: missing contract_gates.rfc083 block"]

    closure_scope = c.get("closure_scope")
    if closure_scope not in ALLOWED_THETA_CLOSURE_SCOPE:
        errs.append(
            f"{claim_id}: rfc083.closure_scope must be one of {sorted(ALLOWED_THETA_CLOSURE_SCOPE)}"
        )

    if not _is_nonempty_str(c.get("bridge_contract_id")):
        errs.append(f"{claim_id}: rfc083.bridge_contract_id is required")

    if not _is_nonempty_str(c.get("bridge_observable_id")):
        errs.append(f"{claim_id}: rfc083.bridge_observable_id is required")

    discrete_residual_artifact = c.get("discrete_residual_artifact")
    if not _is_nonempty_str(discrete_residual_artifact):
        errs.append(f"{claim_id}: rfc083.discrete_residual_artifact is required")
    else:
        p = root / str(discrete_residual_artifact).strip()
        if not p.exists():
            errs.append(
                f"{claim_id}: rfc083.discrete_residual_artifact path not found: {discrete_residual_artifact}"
            )

    weak_leakage_artifact = c.get("weak_leakage_artifact")
    weak_payload: dict[str, Any] = {}
    if not _is_nonempty_str(weak_leakage_artifact):
        errs.append(f"{claim_id}: rfc083.weak_leakage_artifact is required")
    else:
        p = root / str(weak_leakage_artifact).strip()
        if not p.exists():
            errs.append(f"{claim_id}: rfc083.weak_leakage_artifact path not found: {weak_leakage_artifact}")
        else:
            weak_payload = _read_json(p)
            if not weak_payload:
                errs.append(f"{claim_id}: rfc083.weak_leakage_artifact must be valid JSON object")

    eft_bridge_artifact = c.get("eft_bridge_artifact")
    eft_payload: dict[str, Any] = {}
    if not _is_nonempty_str(eft_bridge_artifact):
        errs.append(f"{claim_id}: rfc083.eft_bridge_artifact is required")
    else:
        p = root / str(eft_bridge_artifact).strip()
        if not p.exists():
            errs.append(f"{claim_id}: rfc083.eft_bridge_artifact path not found: {eft_bridge_artifact}")
        else:
            eft_payload = _read_json(p)
            if not eft_payload:
                errs.append(f"{claim_id}: rfc083.eft_bridge_artifact must be valid JSON object")

    skeptic_review_artifact = c.get("skeptic_review_artifact")
    if not _is_nonempty_str(skeptic_review_artifact):
        errs.append(f"{claim_id}: rfc083.skeptic_review_artifact is required")
        skeptic_payload = {}
    else:
        p = root / str(skeptic_review_artifact).strip()
        if not p.exists():
            errs.append(f"{claim_id}: rfc083.skeptic_review_artifact path not found: {skeptic_review_artifact}")
            skeptic_payload = {}
        else:
            skeptic_payload = _read_json(p)
            if not skeptic_payload:
                errs.append(f"{claim_id}: rfc083.skeptic_review_artifact must be valid JSON object")

    if c.get("skeptic_model_diversity_required") is not True:
        errs.append(f"{claim_id}: rfc083.skeptic_model_diversity_required must be true")

    skeptic_verdict = c.get("skeptic_verdict")
    if skeptic_verdict not in ALLOWED_THETA_SKEPTIC_VERDICT:
        errs.append(
            f"{claim_id}: rfc083.skeptic_verdict must be one of {sorted(ALLOWED_THETA_SKEPTIC_VERDICT)}"
        )

    falsification = str(claim_doc.get("falsification_condition", "")).strip()
    if len(falsification) < 50:
        errs.append(
            f"{claim_id}: falsification_condition must be a substantive, physically testable statement (>= 50 chars)"
        )

    bridge_assumptions = claim_doc.get("bridge_assumptions", [])
    if closure_scope == "structure_first":
        if not isinstance(bridge_assumptions, list) or len(bridge_assumptions) == 0:
            errs.append(f"{claim_id}: structure_first claims must declare at least one explicit bridge_assumption")
        elif not all(_is_nonempty_str(x) for x in bridge_assumptions):
            errs.append(f"{claim_id}: bridge_assumptions must contain non-empty strings")

    # Check falsification_attempts field is present (RFC-075 §4.1)
    if "falsification_attempts" not in claim_doc:
        errs.append(f"{claim_id}: missing falsification_attempts field (RFC-075 §4.1 — list, may be empty)")

    artifact_verdict: str | None = None
    if skeptic_payload:
        # Bug fix: empty string is NOT a valid claim_id — must match exactly or key must be absent
        artifact_claim_id = skeptic_payload.get("claim_id")
        if artifact_claim_id is not None and artifact_claim_id != claim_id:
            errs.append(
                f"{claim_id}: skeptic review artifact claim_id mismatch "
                f"(artifact has '{artifact_claim_id}', expected '{claim_id}')"
            )

        artifact_verdict = skeptic_payload.get("verdict")
        if isinstance(artifact_verdict, str) and artifact_verdict.strip():
            if artifact_verdict != skeptic_verdict:
                errs.append(
                    f"{claim_id}: skeptic verdict mismatch between contract_gates ({skeptic_verdict}) "
                    f"and artifact ({artifact_verdict})"
                )
        elif skeptic_verdict not in {"pending", None}:
            # Verdict set in YAML but artifact has no verdict field
            errs.append(
                f"{claim_id}: skeptic_verdict is '{skeptic_verdict}' but artifact has no verdict field"
            )

        if c.get("skeptic_model_diversity_required") is True:
            if skeptic_payload.get("independent_from_builder") is not True:
                errs.append(f"{claim_id}: skeptic review artifact must set independent_from_builder=true")
            reviewer_family = skeptic_payload.get("reviewer_model_family")
            builder_family = skeptic_payload.get("builder_model_family")
            # Require both fields to be present, not just check equality when both happen to exist
            if not _is_nonempty_str(reviewer_family):
                errs.append(f"{claim_id}: skeptic artifact missing reviewer_model_family")
            if not _is_nonempty_str(builder_family):
                errs.append(f"{claim_id}: skeptic artifact missing builder_model_family")
            if _is_nonempty_str(reviewer_family) and reviewer_family == builder_family:
                errs.append(f"{claim_id}: reviewer_model_family must differ from builder_model_family")

        # Required content fields (RFC-083 §5.6)
        if not _is_nonempty_str(skeptic_payload.get("timestamp")):
            errs.append(f"{claim_id}: skeptic artifact missing timestamp (ISO-8601 required)")
        summary = str(skeptic_payload.get("review_summary", "")).strip()
        if len(summary) < 200:
            errs.append(
                f"{claim_id}: skeptic artifact review_summary too short "
                f"({len(summary)} chars; minimum 200 — RFC-083 §5.6)"
            )
        if not _is_nonempty_str(skeptic_payload.get("bridge_comment")):
            errs.append(f"{claim_id}: skeptic artifact missing bridge_comment (RFC-083 §5.6)")
        if not _is_nonempty_str(skeptic_payload.get("falsification_comment")):
            errs.append(f"{claim_id}: skeptic artifact missing falsification_comment (RFC-083 §5.6)")
        if artifact_verdict == "PASS_WITH_LIMITS":
            limits = skeptic_payload.get("limits")
            if not isinstance(limits, list) or not limits:
                errs.append(f"{claim_id}: PASS_WITH_LIMITS verdict requires non-empty limits list")

    promoted = status in PROMOTED_STATUSES or status == "supported_bridge"
    if promoted:
        if closure_scope == "structure_first" and status == "proved_core":
            errs.append(f"{claim_id}: closure_scope=structure_first cannot be promoted to proved_core")
        if skeptic_verdict not in {"PASS", "PASS_WITH_LIMITS"}:
            errs.append(
                f"{claim_id}: promoted THETA claim requires skeptic_verdict in PASS/PASS_WITH_LIMITS"
            )
        if not _gate_done(claim_doc, "gate_3"):
            errs.append(f"{claim_id}: promoted THETA claim requires gates.gate_3 done=true")
        if weak_payload:
            suite = weak_payload.get("weak_leakage_suite", {})
            if not isinstance(suite, dict):
                errs.append(f"{claim_id}: weak_leakage_artifact missing weak_leakage_suite object")
            elif suite.get("all_zero") is not True:
                errs.append(f"{claim_id}: promoted THETA claim requires weak_leakage_suite.all_zero=true")
            if isinstance(suite, dict):
                case_count = int(suite.get("case_count", 0))
                if case_count < 3:
                    errs.append(
                        f"{claim_id}: promoted THETA claim requires weak_leakage_suite.case_count >= 3 "
                        f"(preregistered multi-case deep-cone coverage)"
                    )
            ckm_suite = weak_payload.get("ckm_like_weak_leakage_suite", {})
            if not isinstance(ckm_suite, dict):
                errs.append(f"{claim_id}: weak_leakage_artifact missing ckm_like_weak_leakage_suite object")
            elif ckm_suite.get("all_zero") is not True:
                errs.append(
                    f"{claim_id}: promoted THETA claim requires ckm_like_weak_leakage_suite.all_zero=true"
                )
            if isinstance(ckm_suite, dict):
                case_count = int(ckm_suite.get("case_count", 0))
                if case_count < 3:
                    errs.append(
                        f"{claim_id}: promoted THETA claim requires ckm_like_weak_leakage_suite.case_count >= 3 "
                        f"(preregistered multi-case deep-cone coverage)"
                    )
            periodic_lane = weak_payload.get("periodic_angle_lane")
            if periodic_lane is not None:
                if not isinstance(periodic_lane, dict):
                    errs.append(f"{claim_id}: periodic_angle_lane must be a JSON object when present")
                else:
                    if periodic_lane.get("promotion_blocking") is not False:
                        errs.append(
                            f"{claim_id}: periodic_angle_lane must be non-blocking "
                            f"(promotion_blocking=false)"
                        )
                    if not _is_nonempty_str(periodic_lane.get("status")):
                        errs.append(f"{claim_id}: periodic_angle_lane.status is required when lane is present")
            conjugate_lane = weak_payload.get("ckm_conjugate_falsifier_lane")
            if conjugate_lane is not None:
                if not isinstance(conjugate_lane, dict):
                    errs.append(f"{claim_id}: ckm_conjugate_falsifier_lane must be a JSON object when present")
                else:
                    if conjugate_lane.get("promotion_blocking") is not False:
                        errs.append(
                            f"{claim_id}: ckm_conjugate_falsifier_lane must be non-blocking "
                            f"(promotion_blocking=false)"
                        )
                    if not _is_nonempty_str(conjugate_lane.get("status")):
                        errs.append(
                            f"{claim_id}: ckm_conjugate_falsifier_lane.status is required when lane is present"
                        )
                    diag = conjugate_lane.get("max_case_diagnostics")
                    if not isinstance(diag, dict):
                        errs.append(
                            f"{claim_id}: ckm_conjugate_falsifier_lane.max_case_diagnostics "
                            f"is required as a JSON object"
                        )
                    any_nonzero = conjugate_lane.get("any_nonzero") is True
                    if any_nonzero and isinstance(diag, dict):
                        if diag.get("first_nonzero_tick") is None:
                            errs.append(
                                f"{claim_id}: conjugate falsifier any_nonzero=true requires "
                                f"first_nonzero_tick in diagnostics"
                            )
                        if int(diag.get("max_abs_tick_delta", 0)) <= 0:
                            errs.append(
                                f"{claim_id}: conjugate falsifier any_nonzero=true requires "
                                f"max_abs_tick_delta > 0 in diagnostics"
                            )
                        ranked = diag.get("strong_channel_ranked")
                        if not isinstance(ranked, list) or not ranked:
                            errs.append(
                                f"{claim_id}: conjugate falsifier any_nonzero=true requires "
                                f"non-empty strong_channel_ranked diagnostics"
                            )
                    if conjugate_lane.get("any_nonzero") is True:
                        if skeptic_verdict != "PASS_WITH_LIMITS":
                            errs.append(
                                f"{claim_id}: ckm_conjugate_falsifier_lane.any_nonzero=true "
                                f"requires skeptic_verdict=PASS_WITH_LIMITS"
                            )
                        if skeptic_payload:
                            limits = skeptic_payload.get("limits")
                            if not isinstance(limits, list) or not any(
                                isinstance(x, str)
                                and ("conjugate" in x.lower() or "ckm" in x.lower())
                                for x in limits
                            ):
                                errs.append(
                                    f"{claim_id}: skeptic limits must mention CKM-conjugate falsifier signal "
                                    f"when any_nonzero=true"
                                )
        if eft_payload:
            contract = eft_payload.get("continuum_bridge_contract", {})
            if not isinstance(contract, dict):
                errs.append(f"{claim_id}: eft_bridge_artifact missing continuum_bridge_contract object")
            else:
                if contract.get("conditional_conclusion_theta_zero") is not True:
                    errs.append(
                        f"{claim_id}: promoted THETA claim requires conditional_conclusion_theta_zero=true"
                    )
                theorems = contract.get("lean_theorems", [])
                if not isinstance(theorems, list) or not any(
                    isinstance(t, str) and "theta_zero_if_linear_bridge" in t for t in theorems
                ):
                    errs.append(
                        f"{claim_id}: eft_bridge_artifact must reference theta_zero_if_linear_bridge theorem"
                    )
                linear_lane = contract.get("linear_map_lane")
                if not isinstance(linear_lane, dict):
                    errs.append(f"{claim_id}: continuum_bridge_contract.linear_map_lane is required")
                else:
                    if linear_lane.get("promotion_blocking") is not True:
                        errs.append(
                            f"{claim_id}: continuum_bridge_contract.linear_map_lane must be promotion-blocking "
                            f"(promotion_blocking=true)"
                        )
                    if linear_lane.get("cp_odd_all_hold") is not True:
                        errs.append(
                            f"{claim_id}: continuum_bridge_contract.linear_map_lane requires cp_odd_all_hold=true"
                        )
                    if linear_lane.get("zero_anchor_all_hold") is not True:
                        errs.append(
                            f"{claim_id}: continuum_bridge_contract.linear_map_lane requires zero_anchor_all_hold=true"
                        )

    return errs


def evaluate_contract_gates(
    rows: dict[str, Any],
    claim_docs: dict[str, dict[str, Any]],
    root: Path,
    enforce_for_statuses: set[str] | None = None,
) -> list[GateIssue]:
    statuses = enforce_for_statuses or PROMOTED_STATUSES
    issues: list[GateIssue] = []

    for claim_id, row in rows.items():
        if not isinstance(row, dict):
            continue
        status = _canonical_status(row.get("status"))
        if status not in statuses:
            continue

        claim_doc = claim_docs.get(claim_id, {})
        if "__yaml_error__" in claim_doc:
            issues.append(
                GateIssue(
                    claim_id=claim_id,
                    severity="error",
                    message=f"{claim_id}: malformed claim YAML ({claim_doc['__yaml_error__']})",
                )
            )
            continue

        gates = _as_map(claim_doc.get("contract_gates"))
        required_contracts = _required_contracts_for_claim(claim_id, claim_doc)

        for contract_id in sorted(required_contracts):
            if _is_waived(gates, contract_id):
                c_block = _as_map(gates.get(contract_id))
                approved_by = c_block.get("waiver_approved_by", "")
                issues.append(
                    GateIssue(
                        claim_id=claim_id,
                        severity="warn",
                        message=(
                            f"{claim_id}: {contract_id} waived "
                            f"(approved_by='{approved_by}', reason='{c_block.get('waiver_reason', '')[:80]}')"
                        ),
                    )
                )
                continue
            # Detect partial waiver (waived=true but missing waiver_approved_by — fails _is_waived check)
            c_block = _as_map(gates.get(contract_id))
            if bool(c_block.get("waived", False)):
                issues.append(
                    GateIssue(
                        claim_id=claim_id,
                        severity="error",
                        message=(
                            f"{claim_id}: {contract_id} has waived=true but missing "
                            f"waiver_approved_by (human supervisor required)"
                        ),
                    )
                )
                continue

            errs: list[str]
            if contract_id == "rfc080":
                errs = _validate_rfc080(claim_id, gates)
            elif contract_id == "rfc081":
                errs = _validate_rfc081(claim_id, gates)
            elif contract_id == "rfc082":
                errs = _validate_rfc082(claim_id, gates, root)
            elif contract_id == "rfc083":
                errs = _validate_rfc083(
                    claim_id=claim_id,
                    gates=gates,
                    root=root,
                    status=status,
                    claim_doc=claim_doc,
                )
            else:
                # Unknown contract IDs should warn — not silently pass
                issues.append(GateIssue(
                    claim_id=claim_id,
                    severity="warn",
                    message=f"{claim_id}: required contract '{contract_id}' has no validator (unknown RFC ID)",
                ))
                errs = []

            for err in errs:
                issues.append(GateIssue(claim_id=claim_id, severity="error", message=err))

    return issues

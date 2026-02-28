#!/usr/bin/env python3
"""Validate v2 claim contract gates for canonical-axiom lane."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


PROMOTED_STATUSES = {"supported_bridge", "proved_core"}


@dataclass(frozen=True)
class Issue:
    claim_id: str
    severity: str  # error | warn
    message: str


def _read_yaml(path: Path) -> Dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return {"__yaml_error__": str(exc)}
    return loaded if isinstance(loaded, dict) else {}


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _is_nonempty_str(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _claim_id(path: Path, doc: Dict[str, Any]) -> str:
    return str(doc.get("id") or doc.get("claim_id") or path.stem).strip().upper()


def _validate_canonical_profile(claim_id: str, doc: Dict[str, Any], issues: List[Issue]) -> None:
    cp = doc.get("canonical_profile")
    if not isinstance(cp, dict):
        issues.append(Issue(claim_id, "error", f"{claim_id}: missing canonical_profile block"))
        return

    axioms = cp.get("axioms")
    expected = {"dag", "cxo_over_unity", "projective_lightcone_update"}
    if not isinstance(axioms, list) or set(str(x) for x in axioms) != expected:
        issues.append(
            Issue(
                claim_id,
                "error",
                f"{claim_id}: canonical_profile.axioms must equal {sorted(expected)}",
            )
        )

    if not _is_nonempty_str(cp.get("kernel_profile")):
        issues.append(Issue(claim_id, "error", f"{claim_id}: canonical_profile.kernel_profile required"))
    if not _is_nonempty_str(cp.get("projector_id")):
        issues.append(Issue(claim_id, "error", f"{claim_id}: canonical_profile.projector_id required"))


def _validate_theta_claim(root: Path, claim_id: str, doc: Dict[str, Any], issues: List[Issue]) -> None:
    if claim_id != "THETA-001":
        return

    if not _is_nonempty_str(doc.get("falsification_condition")) or len(str(doc["falsification_condition"]).strip()) < 50:
        issues.append(Issue(claim_id, "error", f"{claim_id}: falsification_condition must be >= 50 chars"))

    bridge_assumptions = doc.get("bridge_assumptions")
    if not isinstance(bridge_assumptions, list) or not bridge_assumptions:
        issues.append(Issue(claim_id, "error", f"{claim_id}: bridge_assumptions must be a non-empty list"))

    if "falsification_attempts" not in doc:
        issues.append(Issue(claim_id, "error", f"{claim_id}: missing falsification_attempts field"))

    contract = doc.get("contract_gates", {})
    rfc083 = contract.get("rfc083", {}) if isinstance(contract, dict) else {}
    if not isinstance(rfc083, dict):
        issues.append(Issue(claim_id, "error", f"{claim_id}: contract_gates.rfc083 must be object"))
        return

    closure_scope = str(doc.get("closure_scope", "")).strip()
    if closure_scope not in {"structure_first", "full_value_closure"}:
        issues.append(Issue(claim_id, "error", f"{claim_id}: closure_scope must be structure_first/full_value_closure"))

    if not _is_nonempty_str(doc.get("lean_file")):
        issues.append(Issue(claim_id, "error", f"{claim_id}: lean_file is required"))
    else:
        lean_path = root / str(doc["lean_file"])
        if not lean_path.exists():
            issues.append(Issue(claim_id, "error", f"{claim_id}: lean_file not found: {doc['lean_file']}"))

    lean_theorems = doc.get("lean_theorems")
    if not isinstance(lean_theorems, list) or not lean_theorems:
        issues.append(Issue(claim_id, "error", f"{claim_id}: lean_theorems must be a non-empty list"))
    else:
        required_bridge = {
            "CausalGraphV2.theta_zero_if_direct_bridge",
            "CausalGraphV2.theta_zero_if_linear_bridge",
            "CausalGraphV2.theta_zero_if_affine_bridge",
        }
        if not required_bridge.issubset(set(str(x) for x in lean_theorems)):
            issues.append(
                Issue(
                    claim_id,
                    "error",
                    f"{claim_id}: lean_theorems must include direct/linear/affine bridge theorems",
                )
            )

    for key in ("weak_leakage_artifact", "eft_bridge_artifact", "skeptic_review_artifact"):
        value = rfc083.get(key)
        if not _is_nonempty_str(value):
            issues.append(Issue(claim_id, "error", f"{claim_id}: rfc083.{key} required"))
            continue
        artifact_path = root / str(value)
        if not artifact_path.exists():
            issues.append(Issue(claim_id, "error", f"{claim_id}: artifact not found: {value}"))

    status = str(doc.get("status", "")).strip()
    if status in PROMOTED_STATUSES:
        if status == "proved_core" and closure_scope == "structure_first":
            issues.append(Issue(claim_id, "error", f"{claim_id}: structure_first claims cannot be proved_core"))

        bridge_art = rfc083.get("weak_leakage_artifact")
        if _is_nonempty_str(bridge_art):
            payload = _read_json(root / str(bridge_art))
            if not payload:
                issues.append(Issue(claim_id, "error", f"{claim_id}: weak_leakage_artifact must be valid JSON"))
            else:
                if payload.get("bridge_ready_supported_bridge") is not True:
                    issues.append(Issue(claim_id, "error", f"{claim_id}: bridge_ready_supported_bridge must be true"))
                contract = payload.get("continuum_bridge_contract", {})
                if not isinstance(contract, dict):
                    issues.append(Issue(claim_id, "error", f"{claim_id}: continuum_bridge_contract missing"))
                else:
                    lt = contract.get("lean_theorems", [])
                    if not isinstance(lt, list) or not any(
                        isinstance(t, str) and "theta_zero_if_linear_bridge" in t for t in lt
                    ):
                        issues.append(
                            Issue(
                                claim_id,
                                "error",
                                f"{claim_id}: bridge artifact must reference theta_zero_if_linear_bridge theorem",
                            )
                        )

        skeptic_art = rfc083.get("skeptic_review_artifact")
        if _is_nonempty_str(skeptic_art):
            payload_path = root / str(skeptic_art)
            payload = _read_json(payload_path)
            if not payload:
                issues.append(Issue(claim_id, "error", f"{claim_id}: skeptic_review_artifact must be valid JSON"))
                return

            artifact_claim_id = str(payload.get("claim_id", "")).strip()
            if artifact_claim_id and artifact_claim_id != claim_id:
                issues.append(
                    Issue(
                        claim_id,
                        "error",
                        f"{claim_id}: skeptic review artifact claim_id mismatch ({artifact_claim_id})",
                    )
                )

            verdict = str(payload.get("verdict", "")).strip()
            if verdict not in {"PASS", "PASS_WITH_LIMITS"}:
                issues.append(Issue(claim_id, "error", f"{claim_id}: skeptic verdict must be PASS/PASS_WITH_LIMITS"))

            contract_verdict = str(rfc083.get("skeptic_verdict", "")).strip()
            if contract_verdict and contract_verdict != verdict:
                issues.append(
                    Issue(
                        claim_id,
                        "error",
                        f"{claim_id}: contract skeptic_verdict ({contract_verdict}) does not match artifact ({verdict})",
                    )
                )

            if payload.get("independent_from_builder") is not True:
                issues.append(Issue(claim_id, "error", f"{claim_id}: skeptic artifact must set independent_from_builder=true"))

            reviewer_family = str(payload.get("reviewer_model_family", "")).strip()
            builder_family = str(payload.get("builder_model_family", "")).strip()
            if not reviewer_family:
                issues.append(Issue(claim_id, "error", f"{claim_id}: reviewer_model_family required"))
            if not builder_family:
                issues.append(Issue(claim_id, "error", f"{claim_id}: builder_model_family required"))
            if reviewer_family and builder_family and reviewer_family == builder_family:
                issues.append(Issue(claim_id, "error", f"{claim_id}: reviewer_model_family must differ from builder_model_family"))

            if not _is_nonempty_str(payload.get("timestamp")):
                issues.append(Issue(claim_id, "error", f"{claim_id}: skeptic artifact timestamp required"))

            summary = str(payload.get("review_summary", "")).strip()
            if len(summary) < 200:
                issues.append(Issue(claim_id, "error", f"{claim_id}: skeptic review_summary must be >= 200 chars"))

            if not _is_nonempty_str(payload.get("bridge_comment")):
                issues.append(Issue(claim_id, "error", f"{claim_id}: skeptic bridge_comment required"))
            if not _is_nonempty_str(payload.get("falsification_comment")):
                issues.append(Issue(claim_id, "error", f"{claim_id}: skeptic falsification_comment required"))

            if verdict == "PASS_WITH_LIMITS":
                limits = payload.get("limits")
                if not isinstance(limits, list) or not limits:
                    issues.append(Issue(claim_id, "error", f"{claim_id}: PASS_WITH_LIMITS requires non-empty limits list"))


def validate_claims(root: Path, claims_dir: Path) -> List[Issue]:
    issues: List[Issue] = []
    for path in sorted(claims_dir.glob("*.yml")):
        doc = _read_yaml(path)
        claim_id = _claim_id(path, doc)

        if "__yaml_error__" in doc:
            issues.append(Issue(claim_id, "error", f"{claim_id}: malformed yaml ({doc['__yaml_error__']})"))
            continue

        if not _is_nonempty_str(doc.get("status")):
            issues.append(Issue(claim_id, "error", f"{claim_id}: status is required"))

        _validate_canonical_profile(claim_id, doc, issues)
        _validate_theta_claim(root, claim_id, doc, issues)

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate COG v2 claim contracts")
    parser.add_argument("--root", default=".", help="Repository root (default: current dir)")
    parser.add_argument("--claims-dir", default="cog_v2/claims", help="Claims directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    claims_dir = (root / args.claims_dir).resolve()
    if not claims_dir.exists():
        raise SystemExit(f"Claims directory not found: {claims_dir}")

    issues = validate_claims(root, claims_dir)
    errors = [x for x in issues if x.severity == "error"]
    warns = [x for x in issues if x.severity == "warn"]

    for issue in issues:
        prefix = "ERROR" if issue.severity == "error" else "WARN"
        print(f"{prefix}: {issue.message}")

    print(
        f"v2_claim_contract_validation: total={len(issues)} errors={len(errors)} warnings={len(warns)}"
    )
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

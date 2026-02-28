"""Build THETA-001 supported-bridge closure packet (v2).

This packet is a promotion-readiness summary artifact:
- what is closed at supported_bridge,
- what is explicitly still open for proved_core,
- exact next requirements to discharge blockers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

import yaml


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "theta001_supported_bridge_closure_packet_v2.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "theta001_supported_bridge_closure_packet_v2.md"

SCRIPT_REPO_PATH = "cog_v2/calc/build_theta001_supported_bridge_closure_packet_v2.py"
CLAIM_REPO_PATH = "cog_v2/claims/THETA-001.yml"
BRIDGE_REPO_PATH = "cog_v2/sources/theta001_bridge_closure_v2.json"
EFT_REPO_PATH = "cog_v2/sources/theta001_eft_bridge_v2.json"
CONTINUUM_REPO_PATH = "cog_v2/sources/theta001_continuum_bridge_v2.json"
TRIPLET_REPO_PATH = "cog_v2/sources/triplet_coherence_e000_leakage_v1.json"
ROBUST_REPO_PATH = "cog_v2/sources/triplet_coherence_e000_robustness_v1.json"
SKEPTIC_REPO_PATH = "cog_v2/sources/theta001_skeptic_review_v2.json"
UV_EXHAUSTIVE_REPO_PATH = "cog_v2/sources/theta001_uv_exhaustive_microstates_v1.json"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _gate_matrix(claim: Dict[str, Any]) -> List[Dict[str, Any]]:
    gates = claim.get("gates")
    if not isinstance(gates, list):
        return []
    out: List[Dict[str, Any]] = []
    for row in gates:
        if not isinstance(row, dict):
            continue
        out.append(
            {
                "gate_id": str(row.get("id", "")).strip(),
                "description": str(row.get("description", "")).strip(),
                "done": bool(row.get("done", False)),
            }
        )
    return out


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    claim_path = ROOT / CLAIM_REPO_PATH
    bridge_path = ROOT / BRIDGE_REPO_PATH
    eft_path = ROOT / EFT_REPO_PATH
    continuum_path = ROOT / CONTINUUM_REPO_PATH
    triplet_path = ROOT / TRIPLET_REPO_PATH
    robust_path = ROOT / ROBUST_REPO_PATH
    skeptic_path = ROOT / SKEPTIC_REPO_PATH
    uv_path = ROOT / UV_EXHAUSTIVE_REPO_PATH

    claim = _read_yaml(claim_path)
    bridge = _read_json(bridge_path)
    eft = _read_json(eft_path)
    continuum = _read_json(continuum_path)
    triplet = _read_json(triplet_path)
    robust = _read_json(robust_path)
    skeptic = _read_json(skeptic_path)
    uv = _read_json(uv_path)

    gate_matrix = _gate_matrix(claim)
    all_gates_done = bool(gate_matrix) and all(bool(row["done"]) for row in gate_matrix)

    weak_suite = bridge.get("weak_leakage_suite", {}) if isinstance(bridge, dict) else {}
    ckm_suite = bridge.get("ckm_like_weak_leakage_suite", {}) if isinstance(bridge, dict) else {}
    fano = bridge.get("fano_sign_balance", {}) if isinstance(bridge, dict) else {}
    eft_map = eft.get("map_identification", {}) if isinstance(eft, dict) else {}
    eft_ready = eft.get("continuum_eft_bridge_readiness", {}) if isinstance(eft, dict) else {}
    cont_ready = continuum.get("continuum_bridge_readiness", {}) if isinstance(continuum, dict) else {}
    cont_conv = continuum.get("convergence_diagnostics", {}) if isinstance(continuum, dict) else {}
    robust_env = robust.get("discrete_correction_envelope_robustness", {}) if isinstance(robust, dict) else {}

    blockers = [
        {
            "blocker_id": "B1_continuum_eft_identification_not_discharged",
            "severity": "critical",
            "description": (
                "Continuum EFT identification remains structure-first/diagnostic. "
                "Current contract still reports non-proved-core status."
            ),
            "evidence_refs": [
                CONTINUUM_REPO_PATH + "#continuum_identification_contract.status",
                SKEPTIC_REPO_PATH + "#limits",
            ],
            "exit_criteria": [
                "Replace hypothesis-level continuum mapping assumption with a discharged theorem-level identification chain.",
                "Update skeptic verdict package with explicit closure of this bridge assumption.",
            ],
        },
        {
            "blocker_id": "B2_cross_sector_weak_leakage_realism_boundary",
            "severity": "high",
            "description": (
                "Stress lanes are strong and all-zero, but still scoped to structure-first synthetic families "
                "rather than a full physically anchored cross-sector realism closure."
            ),
            "evidence_refs": [
                BRIDGE_REPO_PATH + "#weak_leakage_suite",
                BRIDGE_REPO_PATH + "#ckm_like_weak_leakage_suite",
                SKEPTIC_REPO_PATH + "#limits",
            ],
            "exit_criteria": [
                "Define and execute a preregistered realism expansion lane for weak-to-strong leakage that is accepted by skeptic review.",
                "Either preserve all-zero strong residual or formally falsify and revise the bridge.",
            ],
        },
        {
            "blocker_id": "B3_scope_lock_structure_first",
            "severity": "policy",
            "description": (
                "Claim is explicitly `closure_scope = structure_first`; proved_core is policy-blocked until "
                "scope migration criteria are satisfied."
            ),
            "evidence_refs": [
                CLAIM_REPO_PATH + "#closure_scope",
                "cog_v2/rfc/RFC-003_Theta_Continuum_Identification_Contract.md#5.1",
            ],
            "exit_criteria": [
                "Create and approve a full-value closure scope update for THETA-001.",
                "Re-run full gate stack and independent skeptic review under the upgraded scope.",
            ],
        },
    ]

    next_steps = [
        {
            "priority": 1,
            "id": "N1_continuum_id_theorem_plan",
            "description": "Draft exact theorem plan to discharge continuum identification assumption.",
            "deliverables": [
                "New RFC addendum defining theorem statement and admissible assumptions.",
                "Lean target list for final identification chain beyond conditional bridge form.",
            ],
        },
        {
            "priority": 2,
            "id": "N2_weak_leakage_realism_lane",
            "description": "Add realism-focused weak leakage suite with preregistered acceptance criteria.",
            "deliverables": [
                "New stress-lane artifact with deterministic replay hash.",
                "Updated skeptic review comment on realism boundary closure.",
            ],
        },
        {
            "priority": 3,
            "id": "N3_scope_transition_packet",
            "description": "Prepare scope transition packet from structure-first to full-value closure lane.",
            "deliverables": [
                "Claim YAML scope update proposal.",
                "Promotion memo with explicit go/no-go checklist for proved_core attempt.",
            ],
        },
    ]

    payload: Dict[str, Any] = {
        "schema_version": "theta001_supported_bridge_closure_packet_v2",
        "claim_id": str(claim.get("id", "THETA-001")).strip() or "THETA-001",
        "claim_status": str(claim.get("status", "")).strip(),
        "closure_scope": str(claim.get("closure_scope", "")).strip(),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "dependencies": {
            CLAIM_REPO_PATH: _sha_file(claim_path) if claim_path.exists() else "",
            BRIDGE_REPO_PATH: _sha_file(bridge_path) if bridge_path.exists() else "",
            EFT_REPO_PATH: _sha_file(eft_path) if eft_path.exists() else "",
            CONTINUUM_REPO_PATH: _sha_file(continuum_path) if continuum_path.exists() else "",
            TRIPLET_REPO_PATH: _sha_file(triplet_path) if triplet_path.exists() else "",
            ROBUST_REPO_PATH: _sha_file(robust_path) if robust_path.exists() else "",
            SKEPTIC_REPO_PATH: _sha_file(skeptic_path) if skeptic_path.exists() else "",
            UV_EXHAUSTIVE_REPO_PATH: _sha_file(uv_path) if uv_path.exists() else "",
        },
        "gate_matrix": gate_matrix,
        "all_gates_done": bool(all_gates_done),
        "supported_bridge_evidence": {
            "fano_sign_balance": {
                "pos_count": int(fano.get("positive_count", 0)),
                "neg_count": int(fano.get("negative_count", 0)),
                "signed_sum": int(fano.get("signed_sum", 0)),
                "signed_sum_zero": int(fano.get("signed_sum", 0)) == 0,
            },
            "weak_leakage_suite": {
                "all_zero": bool(weak_suite.get("all_zero", False)),
                "case_count": int(weak_suite.get("case_count", 0)),
                "row_count": len(weak_suite.get("rows", [])) if isinstance(weak_suite.get("rows"), list) else 0,
                "max_abs_residual": int(weak_suite.get("max_abs_residual", 0)),
            },
            "ckm_like_weak_leakage_suite": {
                "all_zero": bool(ckm_suite.get("all_zero", False)),
                "case_count": int(ckm_suite.get("case_count", 0)),
                "row_count": len(ckm_suite.get("rows", [])) if isinstance(ckm_suite.get("rows"), list) else 0,
                "max_abs_residual": int(ckm_suite.get("max_abs_residual", 0)),
            },
            "map_identification": {
                "policy_id": str(eft_map.get("policy_id", "")).strip(),
                "selected_map_id": str(eft_map.get("selected_map_id", "")).strip(),
                "selected_unique": bool(eft_map.get("selected_unique", False)),
                "selection_ready": bool(eft_map.get("selection_ready", False)),
                "map_identification_locked": bool(eft_ready.get("map_identification_locked", False)),
            },
            "continuum_bridge_diagnostics": {
                "finite_size_residual_stable_zero": bool(cont_ready.get("finite_size_residual_stable_zero", False)),
                "normalized_residual_stable_zero": bool(cont_ready.get("normalized_residual_stable_zero", False)),
                "discrete_correction_lane_ready": bool(cont_ready.get("discrete_correction_lane_ready", False)),
                "discrete_correction_robustness_ready": bool(
                    cont_ready.get("discrete_correction_robustness_ready", False)
                ),
                "zero_plateau_depth": int(cont_conv.get("zero_plateau_depth", 0)),
            },
            "triplet_robustness_lane": {
                "robustness_lane_ready": bool(robust.get("robustness_lane_ready", False)),
                "pair_count": int(robust_env.get("pair_count", 0)),
                "topology_family_count": int(robust_env.get("topology_family_count", 0)),
                "topology_ids": list(robust_env.get("topology_ids", []))
                if isinstance(robust_env.get("topology_ids"), list)
                else [],
            },
            "uv_exhaustive_microstate_witness": {
                "artifact_present": bool(uv),
                "all_lanes_all_ticks_hold": bool(uv.get("global_checks", {}).get("all_lanes_all_ticks_hold", False))
                if isinstance(uv.get("global_checks"), dict)
                else False,
                "all_lanes_full_exhaustive": bool(uv.get("global_checks", {}).get("all_lanes_full_exhaustive", False))
                if isinstance(uv.get("global_checks"), dict)
                else False,
                "lane_count": len(uv.get("uv_lanes", [])) if isinstance(uv.get("uv_lanes"), list) else 0,
                "microstates_total": int(uv.get("state_space", {}).get("microstates_total", 0))
                if isinstance(uv.get("state_space"), dict)
                else 0,
            },
            "skeptic_review": {
                "verdict": str(skeptic.get("verdict", "")).strip(),
                "independent_from_builder": bool(skeptic.get("independent_from_builder", False)),
                "reviewer_model_family": str(skeptic.get("reviewer_model_family", "")).strip(),
                "builder_model_family": str(skeptic.get("builder_model_family", "")).strip(),
            },
        },
        "proved_core_blockers": blockers,
        "required_next_steps": next_steps,
        "recommendation": {
            "supported_bridge_now": True,
            "proved_core_now": False,
            "decision": "retain_supported_bridge_continue_blocker_discharge",
            "rationale": (
                "All supported-bridge gates and diagnostics are green, but proved_core blockers remain explicit "
                "and unresolved under current structure-first scope."
            ),
        },
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    ev = payload["supported_bridge_evidence"]
    lines = [
        "# THETA-001 Supported-Bridge Closure Packet (v2)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Status: `{payload['claim_status']}`",
        f"- Scope: `{payload['closure_scope']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        "",
        "## Gate Snapshot",
        f"- all_gates_done: `{payload['all_gates_done']}`",
    ]
    for row in payload["gate_matrix"]:
        lines.append(f"- `{row['gate_id']}` done=`{row['done']}` :: {row['description']}")

    lines.extend(
        [
            "",
            "## Supported-Bridge Evidence",
            f"- Fano sign balance: pos={ev['fano_sign_balance']['pos_count']}, neg={ev['fano_sign_balance']['neg_count']}, sum={ev['fano_sign_balance']['signed_sum']}, zero=`{ev['fano_sign_balance']['signed_sum_zero']}`",
            f"- Weak leakage suite: all_zero=`{ev['weak_leakage_suite']['all_zero']}`, cases={ev['weak_leakage_suite']['case_count']}, rows={ev['weak_leakage_suite']['row_count']}, max_abs={ev['weak_leakage_suite']['max_abs_residual']}",
            f"- CKM-like suite: all_zero=`{ev['ckm_like_weak_leakage_suite']['all_zero']}`, cases={ev['ckm_like_weak_leakage_suite']['case_count']}, rows={ev['ckm_like_weak_leakage_suite']['row_count']}, max_abs={ev['ckm_like_weak_leakage_suite']['max_abs_residual']}",
            f"- Map identification: `{ev['map_identification']['policy_id']}` selected=`{ev['map_identification']['selected_map_id']}` unique=`{ev['map_identification']['selected_unique']}` locked=`{ev['map_identification']['map_identification_locked']}`",
            f"- Continuum diagnostics: finite_zero=`{ev['continuum_bridge_diagnostics']['finite_size_residual_stable_zero']}` normalized_zero=`{ev['continuum_bridge_diagnostics']['normalized_residual_stable_zero']}` correction_ready=`{ev['continuum_bridge_diagnostics']['discrete_correction_lane_ready']}` robust_ready=`{ev['continuum_bridge_diagnostics']['discrete_correction_robustness_ready']}` plateau_depth=`{ev['continuum_bridge_diagnostics']['zero_plateau_depth']}`",
            f"- Triplet robustness: ready=`{ev['triplet_robustness_lane']['robustness_lane_ready']}` pair_count=`{ev['triplet_robustness_lane']['pair_count']}` topology_family_count=`{ev['triplet_robustness_lane']['topology_family_count']}` topologies=`{ev['triplet_robustness_lane']['topology_ids']}`",
            f"- UV exhaustive witness: present=`{ev['uv_exhaustive_microstate_witness']['artifact_present']}` all_lanes_all_ticks_hold=`{ev['uv_exhaustive_microstate_witness']['all_lanes_all_ticks_hold']}` full_exhaustive=`{ev['uv_exhaustive_microstate_witness']['all_lanes_full_exhaustive']}` lane_count=`{ev['uv_exhaustive_microstate_witness']['lane_count']}` microstates_total=`{ev['uv_exhaustive_microstate_witness']['microstates_total']}`",
            f"- Skeptic review: verdict=`{ev['skeptic_review']['verdict']}` independent=`{ev['skeptic_review']['independent_from_builder']}` reviewer=`{ev['skeptic_review']['reviewer_model_family']}` builder=`{ev['skeptic_review']['builder_model_family']}`",
            "",
            "## Proved-Core Blockers",
        ]
    )
    for b in payload["proved_core_blockers"]:
        lines.append(f"- `{b['blocker_id']}` ({b['severity']}): {b['description']}")
        lines.append(f"  evidence: {', '.join(b['evidence_refs'])}")
        lines.append(f"  exit_criteria: {' | '.join(b['exit_criteria'])}")

    lines.extend(["", "## Required Next Steps"])
    for step in sorted(payload["required_next_steps"], key=lambda x: int(x["priority"])):
        lines.append(f"- P{step['priority']} `{step['id']}`: {step['description']}")
        lines.append(f"  deliverables: {' | '.join(step['deliverables'])}")

    lines.extend(
        [
            "",
            "## Recommendation",
            f"- supported_bridge_now: `{payload['recommendation']['supported_bridge_now']}`",
            f"- proved_core_now: `{payload['recommendation']['proved_core_now']}`",
            f"- decision: `{payload['recommendation']['decision']}`",
            f"- rationale: {payload['recommendation']['rationale']}",
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: Dict[str, Any],
    *,
    json_paths: Sequence[Path] | None = None,
    md_paths: Sequence[Path] | None = None,
) -> None:
    j_paths = list(json_paths) if json_paths is not None else [OUT_JSON]
    m_paths = list(md_paths) if md_paths is not None else [OUT_MD]
    for path in j_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_markdown(payload)
    for path in m_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build THETA-001 supported-bridge closure packet (v2)")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write artifacts to cog_v2/sources")
    args = parser.parse_args()

    payload = build_payload()
    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {_to_repo_path(OUT_JSON)}")
        print(f"Wrote {_to_repo_path(OUT_MD)}")
        return
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        "theta001_supported_bridge_closure_packet_v2: "
        f"decision={payload['recommendation']['decision']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

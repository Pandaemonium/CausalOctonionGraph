"""Build WEINBERG-001 supported-bridge closure packet (v1).

This packet summarizes:
1) what is closed for supported_bridge,
2) what remains open for proved_core,
3) exact replay/bridge artifacts for external review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

import yaml


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "weinberg001_supported_bridge_closure_packet_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "weinberg001_supported_bridge_closure_packet_v1.md"

SCRIPT_REPO_PATH = "cog_v2/calc/build_weinberg001_supported_bridge_closure_packet_v1.py"
CLAIM_REPO_PATH = "claims/weinberg_angle.yml"
BRIDGE_REPO_PATH = "cog_v2/sources/weinberg_ir_bridge_combinatoric_exact_v2.json"
BRIDGE_MD_REPO_PATH = "cog_v2/sources/weinberg_ir_bridge_combinatoric_exact_v2.md"
LEAN_REPO_PATH = "CausalGraphTheory/WeinbergCombinatoricBridge.lean"
RFC_REPO_PATH = "cog_v2/rfc/RFC-011_Weinberg_Combinatoric_Bridge_Contract.md"


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


def _contract_gate_snapshot(claim: Dict[str, Any]) -> Dict[str, Any]:
    gates = claim.get("contract_gates")
    if not isinstance(gates, dict):
        return {}
    required = gates.get("required", [])
    if not isinstance(required, list):
        required = []
    out: Dict[str, Any] = {"required": [str(x) for x in required]}
    for k, v in gates.items():
        if k == "required":
            continue
        if isinstance(v, dict):
            out[str(k)] = {str(kk): vv for kk, vv in v.items()}
    return out


def _proved_core_blockers() -> List[Dict[str, Any]]:
    return [
        {
            "blocker_id": "B1_continuum_identification_not_discharged",
            "severity": "critical",
            "description": (
                "Current lane is bridge-based; theorem-level identification from discrete bridge "
                "observable to continuum sin^2(theta_W)(M_Z) remains open."
            ),
            "exit_criteria": [
                "Formalize and prove theorem-level continuum identification map.",
                "Replace bridge-assumed status with discharged assumptions.",
            ],
        },
        {
            "blocker_id": "B2_robustness_family_expansion",
            "severity": "high",
            "description": (
                "Supported bridge is replay-exact for preregistered microstate family; broader "
                "family robustness remains insufficiently closed for proved_core."
            ),
            "exit_criteria": [
                "Add preregistered topology/seed family expansion lane.",
                "Show stable estimate behavior under allowed perturbation envelope.",
            ],
        },
    ]


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    claim_path = ROOT / CLAIM_REPO_PATH
    bridge_path = ROOT / BRIDGE_REPO_PATH
    bridge_md_path = ROOT / BRIDGE_MD_REPO_PATH
    lean_path = ROOT / LEAN_REPO_PATH
    rfc_path = ROOT / RFC_REPO_PATH

    claim = _read_yaml(claim_path)
    bridge = _read_json(bridge_path)

    checks = bridge.get("checks", {}) if isinstance(bridge, dict) else {}
    constants = bridge.get("combinatoric_constants", {}) if isinstance(bridge, dict) else {}
    summary = bridge.get("stationary_summary", {}) if isinstance(bridge, dict) else {}

    required_checks = [
        "uv_anchor_exact_at_tick0",
        "stationary_period_detected",
        "combinatoric_constants_exact",
        "no_output_tuned_parameter",
        "ir_bridge_within_2pct_target",
    ]
    required_checks_pass = all(bool(checks.get(k, False)) for k in required_checks)

    recommendation = {
        "supported_bridge_now": bool(required_checks_pass and bridge.get("bridge_pass", False)),
        "proved_core_now": False,
        "decision": "promote_supported_bridge_keep_proved_core_blocked",
        "rationale": (
            "Combinatoric constants and replay gates are closed for bridge scope; "
            "continuum-identification theorem remains open."
        ),
    }

    payload: Dict[str, Any] = {
        "schema_version": "weinberg001_supported_bridge_closure_packet_v1",
        "claim_id": str(claim.get("id", "WEINBERG-001")).strip() or "WEINBERG-001",
        "claim_status": str(claim.get("status", "")).strip(),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "dependencies": {
            CLAIM_REPO_PATH: _sha_file(claim_path) if claim_path.exists() else "",
            BRIDGE_REPO_PATH: _sha_file(bridge_path) if bridge_path.exists() else "",
            BRIDGE_MD_REPO_PATH: _sha_file(bridge_md_path) if bridge_md_path.exists() else "",
            LEAN_REPO_PATH: _sha_file(lean_path) if lean_path.exists() else "",
            RFC_REPO_PATH: _sha_file(rfc_path) if rfc_path.exists() else "",
        },
        "contract_gate_snapshot": _contract_gate_snapshot(claim),
        "supported_bridge_evidence": {
            "bridge_pass": bool(bridge.get("bridge_pass", False)),
            "required_checks": {k: bool(checks.get(k, False)) for k in required_checks},
            "required_checks_all_true": bool(required_checks_pass),
            "uv_anchor": constants.get("uv_anchor", {}),
            "leakage_coeff": constants.get("leakage_coeff", {}),
            "ir_bridge_estimate": summary.get("ir_bridge_estimate", {}),
            "target_gap": float(summary.get("target_gap", 0.0)),
            "detected_period_ticks": summary.get("detected_period_ticks"),
            "replay_hash": str(bridge.get("replay_hash", "")).strip(),
        },
        "proved_core_blockers": _proved_core_blockers(),
        "required_next_steps": [
            {
                "priority": 1,
                "id": "N1_continuum_identification_theorem",
                "description": "Prove theorem-level continuum identification for sin^2(theta_W)(M_Z).",
            },
            {
                "priority": 2,
                "id": "N2_family_robustness_lane",
                "description": "Expand preregistered topology/seed family robustness lane and re-evaluate bridge stability.",
            },
            {
                "priority": 3,
                "id": "N3_claim_governance_refresh",
                "description": "Refresh WEINBERG-001 governance notes and prune deprecated legacy 4/24 diagnostics from promotion path.",
            },
        ],
        "recommendation": recommendation,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    ev = payload["supported_bridge_evidence"]
    lines = [
        "# WEINBERG-001 Supported-Bridge Closure Packet (v1)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Status: `{payload['claim_status']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        "",
        "## Contract Gate Snapshot",
        f"- required: `{payload['contract_gate_snapshot'].get('required', [])}`",
    ]
    for k, v in payload["contract_gate_snapshot"].items():
        if k == "required":
            continue
        lines.append(f"- `{k}`: `{v}`")

    lines.extend(
        [
            "",
            "## Supported-Bridge Evidence",
            f"- bridge_pass: `{ev['bridge_pass']}`",
            f"- required_checks_all_true: `{ev['required_checks_all_true']}`",
            f"- uv_anchor: `{ev['uv_anchor']}`",
            f"- leakage_coeff: `{ev['leakage_coeff']}`",
            f"- ir_bridge_estimate: `{ev['ir_bridge_estimate']}`",
            f"- target_gap: `{ev['target_gap']:+.10f}`",
            f"- detected_period_ticks: `{ev['detected_period_ticks']}`",
            f"- bridge replay_hash: `{ev['replay_hash']}`",
            "",
            "## Proved-Core Blockers",
        ]
    )
    for b in payload["proved_core_blockers"]:
        lines.append(f"- `{b['blocker_id']}` ({b['severity']}): {b['description']}")
        lines.append(f"  exit_criteria: {' | '.join(b['exit_criteria'])}")

    lines.extend(
        [
            "",
            "## Required Next Steps",
        ]
    )
    for n in payload["required_next_steps"]:
        lines.append(f"- P{n['priority']} `{n['id']}`: {n['description']}")

    rec = payload["recommendation"]
    lines.extend(
        [
            "",
            "## Recommendation",
            f"- supported_bridge_now: `{rec['supported_bridge_now']}`",
            f"- proved_core_now: `{rec['proved_core_now']}`",
            f"- decision: `{rec['decision']}`",
            f"- rationale: {rec['rationale']}",
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
    parser = argparse.ArgumentParser(description="Build WEINBERG-001 supported-bridge closure packet (v1)")
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
        "weinberg001_supported_bridge_closure_packet_v1: "
        f"supported_bridge_now={payload['recommendation']['supported_bridge_now']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

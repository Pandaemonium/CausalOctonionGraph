"""Build THETA-001 bridge-closure artifacts (weak leakage + EFT bridge contract)."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from calc.theta001_cp_invariant import fano_sign_balance_counts, weak_leakage_strong_residual

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "sources" / "theta001_bridge_closure.json"
OUT_MD = ROOT / "sources" / "theta001_bridge_closure.md"

SCRIPT_REPO_PATH = "calc/build_theta001_bridge_closure.py"
WITNESS_MODULE_REPO_PATH = "calc/theta001_cp_invariant.py"
LEAN_BRIDGE_REPO_PATH = "CausalGraphTheory/ThetaEFTBridge.lean"

INITIAL_STATE: Tuple[int, ...] = (1, -2, 3, -4, 5, -6, 7, -1)
OP_SEQUENCE: Tuple[int, ...] = (7, 1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4, 5)
WEAK_KICKS: Tuple[int, ...] = (-7, -5, -3, -1, 1, 3, 5, 7)
PHASE_SHIFTS: Tuple[int, ...] = (1, 2, 3, 4, 5)


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _weak_leakage_grid() -> List[Dict[str, int]]:
    rows: List[Dict[str, int]] = []
    for weak_kick in WEAK_KICKS:
        for phase_shift in PHASE_SHIFTS:
            residual = weak_leakage_strong_residual(
                INITIAL_STATE,
                OP_SEQUENCE,
                weak_kick=weak_kick,
                phase_shift=phase_shift,
            )
            rows.append(
                {
                    "weak_kick": int(weak_kick),
                    "phase_shift": int(phase_shift),
                    "strong_residual": int(residual),
                }
            )
    return rows


def build_bridge_closure_payload(
    *,
    policy_id: str = "theta001_bridge_closure_v1",
) -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    witness_module_path = ROOT / WITNESS_MODULE_REPO_PATH
    lean_bridge_path = ROOT / LEAN_BRIDGE_REPO_PATH

    pos_count, neg_count, signed_sum = fano_sign_balance_counts()
    weak_grid = _weak_leakage_grid()
    max_abs_residual = max(abs(int(row["strong_residual"])) for row in weak_grid)

    payload: Dict[str, Any] = {
        "schema_version": "theta001_bridge_closure_v1",
        "claim_id": "THETA-001",
        "policy_id": policy_id,
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "witness_module": WITNESS_MODULE_REPO_PATH,
        "witness_module_sha256": _sha_file(witness_module_path),
        "lean_bridge_file": LEAN_BRIDGE_REPO_PATH,
        "lean_bridge_file_sha256": _sha_file(lean_bridge_path),
        "discrete_cp_residual": {
            "positive_count": int(pos_count),
            "negative_count": int(neg_count),
            "signed_sum": int(signed_sum),
            "is_zero": int(signed_sum) == 0,
        },
        "weak_leakage_suite": {
            "initial_state": list(INITIAL_STATE),
            "op_sequence": list(OP_SEQUENCE),
            "weak_kicks": list(WEAK_KICKS),
            "phase_shifts": list(PHASE_SHIFTS),
            "rows": weak_grid,
            "max_abs_residual": int(max_abs_residual),
            "all_zero": int(max_abs_residual) == 0,
        },
        "continuum_bridge_contract": {
            "bridge_mode": "conditional_linear_map_v1",
            "map_form": "theta_continuum = scale * discrete_cp_residual",
            "assumptions": [
                "Discrete CP map corresponds to continuum CP transformation under locked group-theoretic identification.",
                "Continuum theta coefficient is linear in the discrete CP residual at bridge scale.",
            ],
            "lean_theorems": [
                "CausalGraph.discreteCpResidual_zero",
                "CausalGraph.theta_zero_if_direct_bridge",
                "CausalGraph.theta_zero_if_linear_bridge",
                "CausalGraph.theta_zero_if_affine_bridge",
            ],
            "conditional_conclusion_theta_zero": True,
        },
    }
    payload["bridge_ready_supported_bridge"] = bool(
        payload["discrete_cp_residual"]["is_zero"] and payload["weak_leakage_suite"]["all_zero"]
    )
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    disc = payload["discrete_cp_residual"]
    wl = payload["weak_leakage_suite"]
    bridge = payload["continuum_bridge_contract"]
    lines = [
        "# THETA-001 Bridge Closure Artifact",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Policy: `{payload['policy_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        "",
        "## Discrete Residual",
        f"- Positive count: {disc['positive_count']}",
        f"- Negative count: {disc['negative_count']}",
        f"- Signed sum: {disc['signed_sum']}",
        f"- Residual zero: `{disc['is_zero']}`",
        "",
        "## Weak Leakage Suite",
        f"- Cases: {len(wl['rows'])}",
        f"- Deep-cone length: {len(wl['op_sequence'])}",
        f"- Max abs strong residual: {wl['max_abs_residual']}",
        f"- All zero: `{wl['all_zero']}`",
        "",
        "## Continuum Bridge Contract",
        f"- Mode: `{bridge['bridge_mode']}`",
        f"- Map form: `{bridge['map_form']}`",
        f"- Conditional conclusion theta=0: `{bridge['conditional_conclusion_theta_zero']}`",
        "",
        "### Lean Theorems",
    ]
    for thm in bridge["lean_theorems"]:
        lines.append(f"- `{thm}`")
    lines.extend(
        [
            "",
            "## Promotion Signal",
            f"- bridge_ready_supported_bridge: `{payload['bridge_ready_supported_bridge']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: Dict[str, Any],
    *,
    json_paths: Sequence[Path] | None = None,
    md_paths: Sequence[Path] | None = None,
) -> None:
    json_out = list(json_paths) if json_paths is not None else [OUT_JSON]
    md_out = list(md_paths) if md_paths is not None else [OUT_MD]

    for path in json_out:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_markdown(payload)
    for path in md_out:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build THETA-001 bridge closure artifacts")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write sources artifacts")
    args = parser.parse_args()

    payload = build_bridge_closure_payload()
    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {_to_repo_path(OUT_JSON)}")
        print(f"Wrote {_to_repo_path(OUT_MD)}")
        return
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        "theta001_bridge_closure: "
        f"all_zero={payload['weak_leakage_suite']['all_zero']}, "
        f"bridge_ready={payload['bridge_ready_supported_bridge']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

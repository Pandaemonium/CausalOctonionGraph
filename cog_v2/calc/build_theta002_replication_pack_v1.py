"""Build collaborator replication pack for robust THETA-002 anchors.

Outputs:
1) pack manifest JSON + markdown summary,
2) compact per-scenario JSON bundles for selected anchors,
3) expected outputs/checksums for deterministic replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.calc import theta001_cp_invariant_v2 as t
from cog_v2.calc.build_theta001_nonzero_candidate_probe_v1 import oriented_fano_cubic
from cog_v2.calc.build_theta001_nonzero_robust_casebook_v1 import (
    SCRIPT_REPO_PATH as CASEBOOK_SCRIPT_REPO_PATH,
    build_payload as build_casebook_payload,
)
from cog_v2.calc.build_theta001_nonzero_search_v1 import (
    SCRIPT_REPO_PATH as SEARCH_SCRIPT_REPO_PATH,
    build_payload as build_search_payload,
)


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "theta002_replication_pack_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "theta002_replication_pack_v1.md"
SCENARIO_DIR = ROOT / "cog_v2" / "sources" / "theta002_replication_pack_v1"
SCRIPT_REPO_PATH = "cog_v2/calc/build_theta002_replication_pack_v1.py"
TARGET_WEAK = 2
TARGET_CKM = 2


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _trace_delta_oriented_cubic(
    orig_trace: Sequence[t.State8], dual_trace: Sequence[t.State8], *, exclude_t0: bool
) -> int:
    offset = 1 if exclude_t0 else 0
    return int(
        sum(
            oriented_fano_cubic(s1) - oriented_fano_cubic(s2)
            for s1, s2 in zip(orig_trace[offset:], dual_trace[offset:])
        )
    )


def _run_lane(
    *,
    lane: str,
    initial_state: Tuple[int, ...],
    weak_kick: int,
    op_sequence: Tuple[int, ...],
    ckm_phase: int,
    transport_period: int,
) -> Dict[str, int]:
    init = list(initial_state)
    init[7] += int(weak_kick)
    init_t = tuple(int(x) for x in init)
    ops = tuple(int(x) for x in op_sequence)

    if lane == "weak":
        orig = t.run_update_trace(init_t, ops, t.FANO_SIGN)
        dual = t.run_update_trace(t.cp_map(init_t), ops, t.flipped_sign_table())
        sq = int(t.cp_weighted_trace_delta(init_t, ops, t.STRONG_SECTOR_WEIGHTS))
    elif lane == "ckm":
        orig = t.run_update_trace_ckm_transport(
            init_t,
            ops,
            t.FANO_SIGN,
            ckm_phase=int(ckm_phase),
            transport_period=int(transport_period),
        )
        dual = t.run_update_trace_ckm_transport(
            t.cp_map(init_t),
            ops,
            t.flipped_sign_table(),
            ckm_phase=int(ckm_phase),
            transport_period=int(transport_period),
        )
        sq = int(
            t.weak_leakage_ckm_like_strong_residual(
                init_t,
                ops,
                weak_kick=0,
                ckm_phase=int(ckm_phase),
                transport_period=int(transport_period),
            )
        )
    else:
        raise ValueError(f"unknown lane {lane}")

    cubic = _trace_delta_oriented_cubic(orig, dual, exclude_t0=False)
    cubic_ex_t0 = _trace_delta_oriented_cubic(orig, dual, exclude_t0=True)
    return {
        "squared_residual": int(sq),
        "oriented_cubic_residual": int(cubic),
        "oriented_cubic_residual_excluding_t0": int(cubic_ex_t0),
    }


def _rank_key(row: Dict[str, Any]) -> Tuple[float, float, int]:
    return (
        float(row.get("nonzero_rate_excluding_t0", 0.0)),
        float(row.get("sign_stability_rate", 0.0)),
        int(row.get("max_abs_excluding_t0", 0)),
    )


def _select_anchors(casebook: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], bool]:
    rows = list(casebook.get("developed_candidates", []))
    weak_robust = [r for r in rows if r.get("lane") == "weak" and bool(r.get("robust_nonzero_candidate"))]
    ckm_robust = [r for r in rows if r.get("lane") == "ckm" and bool(r.get("robust_nonzero_candidate"))]
    weak_all = [r for r in rows if r.get("lane") == "weak"]
    ckm_all = [r for r in rows if r.get("lane") == "ckm"]

    weak_sel = sorted(weak_robust, key=_rank_key, reverse=True)[:TARGET_WEAK]
    ckm_sel = sorted(ckm_robust, key=_rank_key, reverse=True)[:TARGET_CKM]
    fallback_used = False
    if len(weak_sel) < TARGET_WEAK:
        fallback_used = True
        missing = TARGET_WEAK - len(weak_sel)
        fill = [r for r in sorted(weak_all, key=_rank_key, reverse=True) if r not in weak_sel][:missing]
        weak_sel.extend(fill)
    if len(ckm_sel) < TARGET_CKM:
        fallback_used = True
        missing = TARGET_CKM - len(ckm_sel)
        fill = [r for r in sorted(ckm_all, key=_rank_key, reverse=True) if r not in ckm_sel][:missing]
        ckm_sel.extend(fill)
    return weak_sel + ckm_sel, fallback_used


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    casebook_script_path = ROOT / CASEBOOK_SCRIPT_REPO_PATH
    search_script_path = ROOT / SEARCH_SCRIPT_REPO_PATH
    casebook = build_casebook_payload()
    search = build_search_payload()

    rows_by_sample = {int(r["sample_id"]): r for r in search["top_weak_nonzero_excluding_t0"] + search["top_ckm_nonzero_excluding_t0"]}
    selected, fallback_used = _select_anchors(casebook)

    scenarios: List[Dict[str, Any]] = []
    for idx, anchor in enumerate(selected, start=1):
        sample_id = int(anchor["sample_id"])
        search_row = rows_by_sample.get(sample_id)
        if search_row is None:
            # deterministic fallback: scan full rows by regenerating search payload core list
            full_rows = build_search_payload().get("top_weak_nonzero_excluding_t0", []) + build_search_payload().get(
                "top_ckm_nonzero_excluding_t0", []
            )
            found = None
            for r in full_rows:
                if int(r["sample_id"]) == sample_id:
                    found = r
                    break
            if found is None:
                raise ValueError(f"sample_id {sample_id} not found in search payload")
            search_row = found

        lane = str(anchor["lane"])
        init_state = tuple(int(x) for x in search_row["initial_state"])
        weak_kick = int(search_row["weak_kick"])
        op_sequence = tuple(int(x) for x in search_row["op_sequence"])
        ckm_phase = int(search_row["ckm_phase"])
        transport_period = int(search_row["transport_period"])

        expected = _run_lane(
            lane=lane,
            initial_state=init_state,
            weak_kick=weak_kick,
            op_sequence=op_sequence,
            ckm_phase=ckm_phase,
            transport_period=transport_period,
        )

        scenario = {
            "schema_version": "theta002_replication_scenario_v1",
            "scenario_id": f"theta002_replica_{lane}_{idx:02d}_sample{sample_id}",
            "claim_id": "THETA-002",
            "lane": lane,
            "sample_id": int(sample_id),
            "input": {
                "initial_state": [int(x) for x in init_state],
                "weak_kick": int(weak_kick),
                "op_sequence": [int(x) for x in op_sequence],
                "ckm_phase": int(ckm_phase),
                "transport_period": int(transport_period),
            },
            "expected_output": expected,
            "acceptance": {
                "squared_residual_equals": int(expected["squared_residual"]),
                "oriented_cubic_residual_excluding_t0_nonzero": int(expected["oriented_cubic_residual_excluding_t0"]) != 0,
            },
            "anchor_metrics": {
                "nonzero_rate_excluding_t0": float(anchor["nonzero_rate_excluding_t0"]),
                "sign_stability_rate": float(anchor["sign_stability_rate"]),
                "robust_nonzero_candidate": bool(anchor["robust_nonzero_candidate"]),
            },
        }
        scenario["scenario_hash"] = _sha_payload(scenario)
        scenarios.append(scenario)

    payload: Dict[str, Any] = {
        "schema_version": "theta002_replication_pack_v1",
        "claim_id": "THETA-002",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "upstream_refs": {
            "casebook_script": CASEBOOK_SCRIPT_REPO_PATH,
            "casebook_script_sha256": _sha_file(casebook_script_path),
            "search_script": SEARCH_SCRIPT_REPO_PATH,
            "search_script_sha256": _sha_file(search_script_path),
        },
        "selection": {
            "target_weak": int(TARGET_WEAK),
            "target_ckm": int(TARGET_CKM),
            "selected_total": int(len(scenarios)),
            "fallback_used": bool(fallback_used),
        },
        "scenarios": scenarios,
        "smoke_test": {
            "all_squared_zero_expected": all(int(s["expected_output"]["squared_residual"]) == 0 for s in scenarios),
            "all_oriented_cubic_excluding_t0_nonzero_expected": all(
                int(s["expected_output"]["oriented_cubic_residual_excluding_t0"]) != 0 for s in scenarios
            ),
            "scenario_count": int(len(scenarios)),
        },
        "collaborator_instructions": {
            "runner_command": "python -m cog_v2.calc.build_theta002_replication_pack_v1 --write-sources",
            "verification": "Compare replay_hash and each scenario_hash against published pack.",
            "upload_format": "Return JSON with per-scenario observed outputs and pass/fail flags.",
        },
        "limits": [
            "Replication pack is for THETA-002 exploratory lane.",
            "Does not modify THETA-001 supported_bridge contract.",
            "Any promotion requires independent skeptical review.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# THETA-002 Replication Pack (v1)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        f"- Selected scenarios: `{payload['selection']['selected_total']}`",
        f"- Fallback used: `{payload['selection']['fallback_used']}`",
        "",
        "## Smoke Test",
        f"- all_squared_zero_expected: `{payload['smoke_test']['all_squared_zero_expected']}`",
        f"- all_oriented_cubic_excluding_t0_nonzero_expected: `{payload['smoke_test']['all_oriented_cubic_excluding_t0_nonzero_expected']}`",
        "",
        "## Scenarios",
        "",
        "| scenario_id | lane | sample_id | weak_kick | ckm_phase | period | sq_expected | cubic_ex_t0_expected | robust_anchor |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for s in payload["scenarios"]:
        lines.append(
            f"| {s['scenario_id']} | {s['lane']} | {s['sample_id']} | "
            f"{s['input']['weak_kick']} | {s['input']['ckm_phase']} | {s['input']['transport_period']} | "
            f"{s['expected_output']['squared_residual']} | "
            f"{s['expected_output']['oriented_cubic_residual_excluding_t0']} | "
            f"{s['anchor_metrics']['robust_nonzero_candidate']} |"
        )
    lines.extend(["", "## Verification"])
    lines.append(f"- Runner: `{payload['collaborator_instructions']['runner_command']}`")
    lines.append(f"- Verify: {payload['collaborator_instructions']['verification']}")
    lines.extend(["", "## Limits"])
    for lim in payload["limits"]:
        lines.append(f"- {lim}")
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: Dict[str, Any],
    *,
    json_paths: Sequence[Path] | None = None,
    md_paths: Sequence[Path] | None = None,
    scenario_root: Path | None = None,
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

    root = scenario_root if scenario_root is not None else SCENARIO_DIR
    root.mkdir(parents=True, exist_ok=True)
    for s in payload["scenarios"]:
        sp = root / f"{s['scenario_id']}.json"
        sp.write_text(json.dumps(s, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build THETA-002 replication pack")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write artifacts to cog_v2/sources")
    args = parser.parse_args()

    payload = build_payload()
    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {_to_repo_path(OUT_JSON)}")
        print(f"Wrote {_to_repo_path(OUT_MD)}")
        print(f"Wrote scenario bundle to {_to_repo_path(SCENARIO_DIR)}")
        return
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        "theta002_replication_pack_v1: "
        f"scenarios={payload['selection']['selected_total']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()


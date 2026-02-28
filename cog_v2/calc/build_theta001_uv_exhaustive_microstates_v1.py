"""Build UV-boundary exhaustive microstate/event witness for THETA-001 (v1).

States are treated as events:
- an event at tick `t` is exactly the microstate at tick `t`.
- no coarse-graining in this witness lane.

This is an exhaustive finite witness over the unity microstate lattice for a
small number of ticks, intended as a UV boundary extension of the structure-first
proof package.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

try:
    from cog_v2.python import kernel_projective_unity as k
except ModuleNotFoundError:
    REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "theta001_uv_exhaustive_microstates_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "theta001_uv_exhaustive_microstates_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_theta001_uv_exhaustive_microstates_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"

# Two short UV lanes (few ticks, exact exhaustive state enumeration).
UV_LANES: Tuple[Tuple[str, Tuple[int, ...]], ...] = (
    ("uv_lane_a", (1, 2, 3, 4)),
    ("uv_lane_b", (7, 1, 7, 2)),
)

UNITY_ALPHABET: Tuple[k.GInt, ...] = tuple(k.UNITY_ALPHABET)
FLIPPED_SIGN_TABLE: Dict[Tuple[int, int], int] = {(i, j): -s for (i, j), s in k.XOR_SIGN_TABLE.items()}
STRONG_WEIGHTS: Tuple[int, ...] = (0, 1, 1, 1, 1, 1, 1, 0)


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _coeff_to_pair(z: k.GInt) -> List[int]:
    return [int(z.re), int(z.im)]


def _alphabet_pairs() -> List[List[int]]:
    return [_coeff_to_pair(z) for z in UNITY_ALPHABET]


def _basis_mul_custom(i: int, j: int, table: Dict[Tuple[int, int], int]) -> Tuple[int, int]:
    if i == 0:
        return 1, j
    if j == 0:
        return 1, i
    if i == j:
        return -1, 0
    return table[(i, j)], (i ^ j)


def _decode_state(idx: int, alphabet: Sequence[k.GInt]) -> k.CxO:
    vals = [alphabet[0]] * 8
    cur = int(idx)
    base = len(alphabet)
    for i in range(8):
        cur, r = divmod(cur, base)
        vals[i] = alphabet[r]
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _cp_map_state(state: k.CxO) -> k.CxO:
    vals = list(state)
    for i in range(1, 8):
        vals[i] = k.g_neg(vals[i])
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _neg_state(state: k.CxO) -> k.CxO:
    vals = [k.g_neg(z) for z in state]
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _left_mul_basis_projected(op_idx: int, state: k.CxO, table: Dict[Tuple[int, int], int]) -> k.CxO:
    # For basis-left multiply, channel map is a signed permutation.
    # We keep the projection call to lock to the canonical update contract.
    out = [k.ZERO_G] * 8
    for j, coeff in enumerate(state):
        if k.g_is_zero(coeff):
            continue
        sign, out_idx = _basis_mul_custom(op_idx, j, table)
        term = coeff if sign > 0 else k.g_neg(coeff)
        out[out_idx] = term
    return k.project_cxo_to_unity((out[0], out[1], out[2], out[3], out[4], out[5], out[6], out[7]))


def _strong_action(state: k.CxO, weights: Sequence[int] = STRONG_WEIGHTS) -> int:
    total = 0
    for w, z in zip(weights, state):
        total += int(w) * int(z.re * z.re + z.im * z.im)
    return int(total)


def _tick_mode_expected(tick: int) -> str:
    # Empirically and structurally in this lane:
    # even tick -> cp(orig) == dual, odd tick -> cp(orig) == -dual.
    return "cp_equals_dual" if (tick % 2 == 0) else "cp_equals_neg_dual"


def _evaluate_lane(
    lane_id: str,
    op_sequence: Sequence[int],
    *,
    max_states: int | None = None,
) -> Dict[str, Any]:
    alphabet = UNITY_ALPHABET
    total_microstates = int(len(alphabet) ** 8)
    enumerate_count = total_microstates if max_states is None else int(min(total_microstates, max_states))
    full_exhaustive = enumerate_count == total_microstates

    tick_count = len(op_sequence) + 1
    exact_counts = [0] * tick_count
    neg_counts = [0] * tick_count
    parity_ok_counts = [0] * tick_count
    strong_cp_delta_sums = [0] * tick_count
    strong_dual_delta_sums = [0] * tick_count
    witness_failure: Dict[str, Any] | None = None

    for idx in range(enumerate_count):
        s0 = _decode_state(idx, alphabet)
        orig_trace = [s0]
        dual_trace = [_cp_map_state(s0)]

        cur_orig = orig_trace[0]
        cur_dual = dual_trace[0]
        for op in op_sequence:
            cur_orig = _left_mul_basis_projected(int(op), cur_orig, k.XOR_SIGN_TABLE)
            cur_dual = _left_mul_basis_projected(int(op), cur_dual, FLIPPED_SIGN_TABLE)
            orig_trace.append(cur_orig)
            dual_trace.append(cur_dual)

        for t, (s_orig, s_dual) in enumerate(zip(orig_trace, dual_trace)):
            cp_orig = _cp_map_state(s_orig)
            neg_dual = _neg_state(s_dual)
            is_exact = cp_orig == s_dual
            is_neg = cp_orig == neg_dual
            parity_ok = bool(is_exact or is_neg)

            if is_exact:
                exact_counts[t] += 1
            if is_neg:
                neg_counts[t] += 1
            if parity_ok:
                parity_ok_counts[t] += 1
            elif witness_failure is None:
                witness_failure = {
                    "state_index": int(idx),
                    "tick": int(t),
                    "op_sequence": [int(x) for x in op_sequence],
                    "state_t": [_coeff_to_pair(z) for z in s_orig],
                    "dual_state_t": [_coeff_to_pair(z) for z in s_dual],
                    "cp_state_t": [_coeff_to_pair(z) for z in cp_orig],
                }

            strong_cp_delta_sums[t] += int(_strong_action(s_orig) - _strong_action(_cp_map_state(s_orig)))
            strong_dual_delta_sums[t] += int(_strong_action(s_orig) - _strong_action(s_dual))

    tick_rows: List[Dict[str, Any]] = []
    for t in range(tick_count):
        expected_mode = _tick_mode_expected(t)
        expected_mode_holds = (
            exact_counts[t] == enumerate_count if expected_mode == "cp_equals_dual" else neg_counts[t] == enumerate_count
        )
        tick_rows.append(
            {
                "tick": int(t),
                "event_count": int(enumerate_count),
                "cp_dual_exact_count": int(exact_counts[t]),
                "cp_dual_neg_count": int(neg_counts[t]),
                "cp_dual_parity_holds_count": int(parity_ok_counts[t]),
                "cp_dual_parity_holds_all": int(parity_ok_counts[t]) == int(enumerate_count),
                "expected_mode": expected_mode,
                "expected_mode_holds_all": bool(expected_mode_holds),
                "strong_cp_delta_sum": int(strong_cp_delta_sums[t]),
                "strong_dual_delta_sum": int(strong_dual_delta_sums[t]),
            }
        )

    lane_all_ticks_hold = all(bool(r["cp_dual_parity_holds_all"]) for r in tick_rows) and all(
        bool(r["expected_mode_holds_all"]) for r in tick_rows
    )

    return {
        "lane_id": lane_id,
        "op_sequence": [int(x) for x in op_sequence],
        "ticks": int(len(op_sequence)),
        "total_microstates": int(total_microstates),
        "enumerated_microstates": int(enumerate_count),
        "full_exhaustive": bool(full_exhaustive),
        "tick_rows": tick_rows,
        "lane_all_ticks_hold": bool(lane_all_ticks_hold),
        "witness_failure": witness_failure,
    }


def build_payload(*, max_states: int | None = None) -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH

    lane_rows = [_evaluate_lane(lane_id, op_seq, max_states=max_states) for lane_id, op_seq in UV_LANES]
    all_lanes_hold = all(bool(l["lane_all_ticks_hold"]) for l in lane_rows)
    all_full_exhaustive = all(bool(l["full_exhaustive"]) for l in lane_rows)

    payload: Dict[str, Any] = {
        "schema_version": "theta001_uv_exhaustive_microstates_v1",
        "claim_id": "THETA-001",
        "closure_scope": "structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "event_semantics": {
            "states_are_events": True,
            "event_definition": "event_at_tick_t_is_exact_microstate_state_t",
            "time_definition": "tick_depth_in_dag",
            "lightcone_scope": "parents_only_per_tick_update",
        },
        "state_space": {
            "basis_labels": list(k.BASIS_LABELS),
            "unity_alphabet": _alphabet_pairs(),
            "channels": 8,
            "microstates_total": int(len(UNITY_ALPHABET) ** 8),
            "enumeration_mode": "full_exhaustive" if all_full_exhaustive else "bounded_subset",
            "max_states_override": None if max_states is None else int(max_states),
        },
        "uv_lanes": lane_rows,
        "global_checks": {
            "all_lanes_all_ticks_hold": bool(all_lanes_hold),
            "all_lanes_full_exhaustive": bool(all_full_exhaustive),
        },
        "limits": [
            "UV witness is exact and exhaustive over a finite microstate lattice for short tick horizons.",
            "This extends structure-first evidence; it does not alone discharge full continuum EFT identification.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# THETA-001 UV Exhaustive Microstate/Event Witness (v1)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Scope: `{payload['closure_scope']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        f"- states_are_events: `{payload['event_semantics']['states_are_events']}`",
        f"- enumeration_mode: `{payload['state_space']['enumeration_mode']}`",
        f"- microstates_total: `{payload['state_space']['microstates_total']}`",
        "",
        "## Global Checks",
        f"- all_lanes_all_ticks_hold: `{payload['global_checks']['all_lanes_all_ticks_hold']}`",
        f"- all_lanes_full_exhaustive: `{payload['global_checks']['all_lanes_full_exhaustive']}`",
    ]
    for lane in payload["uv_lanes"]:
        lines.extend(
            [
                "",
                f"## Lane `{lane['lane_id']}`",
                f"- op_sequence: `{lane['op_sequence']}`",
                f"- ticks: `{lane['ticks']}`",
                f"- enumerated_microstates: `{lane['enumerated_microstates']}`",
                f"- full_exhaustive: `{lane['full_exhaustive']}`",
                f"- lane_all_ticks_hold: `{lane['lane_all_ticks_hold']}`",
                "",
                "| Tick | Events | cp==dual | cp==-dual | parity holds all | expected mode | expected mode holds all | strong_cp_delta_sum | strong_dual_delta_sum |",
                "|---:|---:|---:|---:|---|---|---|---:|---:|",
            ]
        )
        for row in lane["tick_rows"]:
            lines.append(
                f"| {row['tick']} | {row['event_count']} | {row['cp_dual_exact_count']} | {row['cp_dual_neg_count']} | "
                f"{row['cp_dual_parity_holds_all']} | {row['expected_mode']} | {row['expected_mode_holds_all']} | "
                f"{row['strong_cp_delta_sum']} | {row['strong_dual_delta_sum']} |"
            )
        if lane.get("witness_failure") is not None:
            lines.append("")
            lines.append(f"- witness_failure: `{lane['witness_failure']}`")
    lines.extend(["", "## Limits"])
    for lim in payload["limits"]:
        lines.append(f"- {lim}")
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
    parser = argparse.ArgumentParser(description="Build THETA-001 UV exhaustive microstate witness")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write artifacts to cog_v2/sources")
    parser.add_argument(
        "--max-states",
        type=int,
        default=None,
        help="Optional cap for enumeration (for quick checks). Omit for full 5^8 exhaustive run.",
    )
    args = parser.parse_args()

    payload = build_payload(max_states=args.max_states)
    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {_to_repo_path(OUT_JSON)}")
        print(f"Wrote {_to_repo_path(OUT_MD)}")
        return
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        "theta001_uv_exhaustive_microstates_v1: "
        f"all_lanes_all_ticks_hold={payload['global_checks']['all_lanes_all_ticks_hold']}, "
        f"full_exhaustive={payload['global_checks']['all_lanes_full_exhaustive']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

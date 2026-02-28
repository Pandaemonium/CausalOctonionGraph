"""Build exact repeating-pattern files for all canonical motif IDs.

Outputs full per-motif cycle data with XOR/sign bit-switch decomposition
for e111 (legacy e7) left/right action.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from calc.xor_furey_ideals import (
    StateGI,
    detect_period,
    e7_left,
    e7_right,
    gi_add,
    gi_is_zero,
)
from calc.xor_octonion_gate import mul_basis_fast
from calc.xor_scenario_loader import canonical_motif_state_map


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "particle_motifs_exact_patterns_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "particle_motifs_exact_patterns_v1.md"

SCRIPT_REPO_PATH = "cog_v2/calc/build_particle_motif_exact_patterns_v1.py"
MOTIF_SOURCE_REPO_PATH = "calc/xor_scenario_loader.py::canonical_motif_state_map"
KERNEL_REPO_PATH = "calc/xor_octonion_gate.py"
MAX_PERIOD_SCAN = 64
E111_INDEX = 7


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _channel_label(idx: int) -> str:
    if not (0 <= idx <= 7):
        raise ValueError(f"channel idx out of range: {idx}")
    return f"e{idx:03b}"


def _serialize_state(state: StateGI) -> List[List[int]]:
    return [[int(re), int(im)] for re, im in state]


def _state_sparse_e000(state: StateGI) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    for i, (re, im) in enumerate(state):
        if re == 0 and im == 0:
            continue
        out[_channel_label(i)] = {"re": int(re), "im": int(im)}
    return out


def _support_indices(state: StateGI) -> List[int]:
    return [i for i, coeff in enumerate(state) if not gi_is_zero(coeff)]


def _support_labels(state: StateGI) -> List[str]:
    return [_channel_label(i) for i in _support_indices(state)]


def _gi_scale(coeff: Tuple[int, int], sign: int) -> Tuple[int, int]:
    if sign >= 0:
        return (int(coeff[0]), int(coeff[1]))
    return (-int(coeff[0]), -int(coeff[1]))


def _bitswitch_step_detail(state: StateGI, *, hand: str) -> Dict[str, Any]:
    if hand not in {"left", "right"}:
        raise ValueError("hand must be left or right")
    paths: List[Dict[str, Any]] = []
    accum: List[Tuple[int, int]] = [(0, 0) for _ in range(8)]

    for in_idx in _support_indices(state):
        coeff_in = state[in_idx]
        core = mul_basis_fast(E111_INDEX, in_idx) if hand == "left" else mul_basis_fast(in_idx, E111_INDEX)
        coeff_out = _gi_scale(coeff_in, core.sign)
        accum[core.out_idx] = gi_add(accum[core.out_idx], coeff_out)
        paths.append(
            {
                "in_idx": int(in_idx),
                "in_label": _channel_label(in_idx),
                "coeff_in": [int(coeff_in[0]), int(coeff_in[1])],
                "xor_out_idx": int(core.out_idx),
                "xor_out_label": _channel_label(core.out_idx),
                "sign": int(core.sign),
                "coeff_out_path": [int(coeff_out[0]), int(coeff_out[1])],
            }
        )

    predicted = tuple((int(re), int(im)) for re, im in accum)
    return {
        "hand": hand,
        "op_label": _channel_label(E111_INDEX),
        "component_paths": paths,
        "predicted_next_state": _serialize_state(predicted),  # type: ignore[arg-type]
    }


def _cycle_rows(initial: StateGI, *, hand: str, period: int) -> Dict[str, Any]:
    if hand == "left":
        step_fn = e7_left
    elif hand == "right":
        step_fn = e7_right
    else:
        raise ValueError("hand must be left or right")

    states: List[StateGI] = [initial]
    cur = initial
    for _ in range(period):
        cur = step_fn(cur)
        states.append(cur)

    tick_rows: List[Dict[str, Any]] = []
    step_rows: List[Dict[str, Any]] = []
    for t, st in enumerate(states):
        tick_rows.append(
            {
                "tick": int(t),
                "state_exact": _serialize_state(st),
                "state_sparse": _state_sparse_e000(st),
                "support_indices": _support_indices(st),
                "support_labels": _support_labels(st),
            }
        )

    for t in range(period):
        detail = _bitswitch_step_detail(states[t], hand=hand)
        expected_next = _serialize_state(states[t + 1])
        detail["expected_next_state"] = expected_next
        detail["predicted_matches_expected"] = detail["predicted_next_state"] == expected_next
        detail["step_index"] = int(t)
        step_rows.append(detail)

    return {
        "period": int(period),
        "cycle_closed": states[0] == states[-1],
        "tick_rows": tick_rows,
        "step_rows": step_rows,
        "all_steps_match_bitswitch_rule": all(bool(r["predicted_matches_expected"]) for r in step_rows),
    }


def _motif_family(motif_id: str) -> str:
    if motif_id.startswith("su_"):
        return "spinor_Su"
    if motif_id.startswith("sd_"):
        return "spinor_Sd"
    if motif_id.startswith("vector_"):
        return "vector"
    if motif_id.startswith("left_spinor_"):
        return "particle_alias_left"
    if motif_id.startswith("right_spinor_"):
        return "particle_alias_right"
    return "other"


def _is_particle_candidate(motif_id: str) -> bool:
    keys = ("electron", "muon", "tau", "proton", "vacuum", "neutrino")
    lower = motif_id.lower()
    return any(k in lower for k in keys)


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    motifs = canonical_motif_state_map()

    motif_rows: List[Dict[str, Any]] = []
    for motif_id in sorted(motifs):
        state = motifs[motif_id]
        p_left = detect_period(state, e7_left, max_steps=MAX_PERIOD_SCAN)
        p_right = detect_period(state, e7_right, max_steps=MAX_PERIOD_SCAN)
        period_left = int(p_left) if p_left is not None else None
        period_right = int(p_right) if p_right is not None else None

        left_cycle = _cycle_rows(state, hand="left", period=period_left if period_left is not None else 1)
        right_cycle = _cycle_rows(state, hand="right", period=period_right if period_right is not None else 1)

        motif_rows.append(
            {
                "motif_id": motif_id,
                "family": _motif_family(motif_id),
                "particle_candidate": _is_particle_candidate(motif_id),
                "initial_state_exact": _serialize_state(state),
                "initial_state_sparse": _state_sparse_e000(state),
                "support_indices": _support_indices(state),
                "support_labels": _support_labels(state),
                "period_left_e111": period_left,
                "period_right_e111": period_right,
                "left_cycle": left_cycle,
                "right_cycle": right_cycle,
                "period_left_eq_right": period_left == period_right,
            }
        )

    all_match_left = all(bool(m["left_cycle"]["all_steps_match_bitswitch_rule"]) for m in motif_rows)
    all_match_right = all(bool(m["right_cycle"]["all_steps_match_bitswitch_rule"]) for m in motif_rows)
    all_period4 = all(int(m["period_left_e111"]) == 4 and int(m["period_right_e111"]) == 4 for m in motif_rows)

    payload: Dict[str, Any] = {
        "schema_version": "particle_motifs_exact_patterns_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "motif_source": MOTIF_SOURCE_REPO_PATH,
        "kernel_source": KERNEL_REPO_PATH,
        "kernel_source_sha256": _sha_file(kernel_path),
        "basis_labels": [_channel_label(i) for i in range(8)],
        "op_bitswitch_label": _channel_label(E111_INDEX),
        "motif_count": len(motif_rows),
        "particle_candidate_ids": [m["motif_id"] for m in motif_rows if bool(m["particle_candidate"])],
        "motifs": motif_rows,
        "global_checks": {
            "all_steps_match_bitswitch_rule_left": bool(all_match_left),
            "all_steps_match_bitswitch_rule_right": bool(all_match_right),
            "all_periods_equal_4": bool(all_period4),
        },
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# Particle Motifs Exact Patterns (v1)",
        "",
        f"- motif_count: `{payload['motif_count']}`",
        f"- op_bitswitch_label: `{payload['op_bitswitch_label']}`",
        f"- replay_hash: `{payload['replay_hash']}`",
        f"- all_steps_match_bitswitch_rule_left: `{payload['global_checks']['all_steps_match_bitswitch_rule_left']}`",
        f"- all_steps_match_bitswitch_rule_right: `{payload['global_checks']['all_steps_match_bitswitch_rule_right']}`",
        f"- all_periods_equal_4: `{payload['global_checks']['all_periods_equal_4']}`",
        "",
        "## Particle-Candidate IDs",
    ]
    for mid in payload["particle_candidate_ids"]:
        lines.append(f"- `{mid}`")

    lines.extend(["", "## Motif Summary", "| Motif ID | Family | Left Period | Right Period | Support |", "|---|---:|---:|---:|---|"])
    for m in payload["motifs"]:
        lines.append(
            f"| `{m['motif_id']}` | `{m['family']}` | `{m['period_left_e111']}` | `{m['period_right_e111']}` | `{m['support_labels']}` |"
        )
    lines.extend(
        [
            "",
            "Full exact cycle states and per-step XOR/sign bit-switch decomposition are in JSON under:",
            "1. `motifs[*].left_cycle.tick_rows` / `step_rows`",
            "2. `motifs[*].right_cycle.tick_rows` / `step_rows`",
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
    parser = argparse.ArgumentParser(description="Build exact particle motif pattern artifacts (v1)")
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
        "particle_motifs_exact_patterns_v1: "
        f"motif_count={payload['motif_count']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

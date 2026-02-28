"""Formalize triplet-coherence vs e000-leakage hypothesis under COG v2 kernel.

Hypothesis (v1):
1) 3-cycle coherent source motifs preserve triplet occupancy coherence.
2) Off-cycle/broken motifs show stronger e000-axis leakage.
3) Broken motifs reduce terminal non-e000 mass proxy and transport proxy.

This is a deterministic structure-first probe, not a full physical closure claim.
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
OUT_JSON = ROOT / "cog_v2" / "sources" / "triplet_coherence_e000_leakage_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "triplet_coherence_e000_leakage_v1.md"

SCRIPT_REPO_PATH = "cog_v2/calc/build_triplet_coherence_e000_leakage_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
TICKS = 120
DISTANCE_TAIL_WINDOW_START = 20
NEAR_FIELD_END_D = 20
FAR_FIELD_START_D = 60
CORRECTION_ONSET_WINDOW = 5
CORRECTION_ONSET_THRESHOLD = 0.6

NODE_IDS: Tuple[str, ...] = ("s", "b", "m", "t")
PARENTS: Dict[str, List[str]] = {
    "s": [],
    "b": [],
    "m": ["s", "b"],
    "t": ["m", "b"],
}


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _state_from_map(vals: Dict[int, k.GInt]) -> k.CxO:
    data = [k.ZERO_G] * 8
    for idx, value in vals.items():
        data[int(idx)] = value
    return (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])


def _abs2(z: k.GInt) -> int:
    return int(z.re * z.re + z.im * z.im)


def _triplet_occupancy_fraction(state: k.CxO, channels: Tuple[int, int, int] = (1, 2, 3)) -> float:
    triplet_power = float(sum(_abs2(state[idx]) for idx in channels))
    non_e000_power = float(sum(_abs2(z) for z in state[1:]))
    if non_e000_power == 0.0:
        return 0.0
    return triplet_power / non_e000_power


def _e000_share(state: k.CxO) -> float:
    e000 = float(_abs2(state[0]))
    non_e000 = float(sum(_abs2(z) for z in state[1:]))
    total = e000 + non_e000
    if total == 0.0:
        return 0.0
    return e000 / total


def _terminal_non_e000_mass_proxy(state: k.CxO) -> float:
    return float(sum(_abs2(z) for z in state[1:]))


def _transport_proxy(state: k.CxO) -> float:
    source_power = float(sum(_abs2(state[idx]) for idx in (1, 2, 3)))
    target_power = float(sum(_abs2(state[idx]) for idx in (4, 5, 6)))
    denom = source_power + target_power
    if denom == 0.0:
        return 0.0
    return target_power / denom


def _coherence_score(source: k.CxO, mediator: k.CxO, terminal: k.CxO) -> float:
    return (
        _triplet_occupancy_fraction(source)
        + _triplet_occupancy_fraction(mediator)
        + _triplet_occupancy_fraction(terminal)
    ) / 3.0


def _scenario_worlds() -> Dict[str, k.World]:
    coherent_states = {
        "s": _state_from_map(
            {
                1: k.ONE_G,
                2: k.I_G,
                3: k.MINUS_I_G,
                4: k.ONE_G,
                5: k.ONE_G,
            }
        ),
        "b": _state_from_map(
            {
                4: k.ONE_G,
                5: k.I_G,
                6: k.MINUS_I_G,
            }
        ),
        "m": k.cxo_one(),
        "t": k.cxo_one(),
    }
    broken_states = {
        "s": _state_from_map(
            {
                1: k.ONE_G,
                4: k.I_G,
                7: k.MINUS_ONE_G,
            }
        ),
        "b": _state_from_map(
            {
                0: k.ONE_G,
                7: k.ONE_G,
            }
        ),
        "m": k.cxo_one(),
        "t": k.cxo_one(),
    }
    return {
        "coherent_triplet_v1": k.World(
            node_ids=list(NODE_IDS),
            parents={k1: list(v1) for k1, v1 in PARENTS.items()},
            states=coherent_states,
            event_order=None,
            tick=0,
        ),
        "broken_off_cycle_v1": k.World(
            node_ids=list(NODE_IDS),
            parents={k1: list(v1) for k1, v1 in PARENTS.items()},
            states=broken_states,
            event_order=None,
            tick=0,
        ),
    }


def _mean(xs: Sequence[float]) -> float:
    if not xs:
        return 0.0
    return float(sum(xs) / float(len(xs)))


def _run_scenario(world: k.World) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    coherence_series: List[float] = []
    mass_series: List[float] = []
    e000_series: List[float] = []
    transport_series: List[float] = []
    leakage_series: List[float] = []
    prev_e000_power: float | None = None

    cur = world
    for _ in range(TICKS):
        source = cur.states["s"]
        mediator = cur.states["m"]
        terminal = cur.states["t"]

        c_t = _coherence_score(source, mediator, terminal)
        m_t = _terminal_non_e000_mass_proxy(terminal)
        e_t = _e000_share(terminal)
        t_t = _transport_proxy(terminal)
        e000_power = float(_abs2(terminal[0]))
        l_t = 0.0 if prev_e000_power is None else float(e000_power - prev_e000_power)

        rows.append(
            {
                "tick": int(cur.tick),
                "d": int(cur.tick),
                "C_t": float(c_t),
                "M_t": float(m_t),
                "E_t": float(e_t),
                "T_t": float(t_t),
                "L_t": float(l_t),
            }
        )
        coherence_series.append(float(c_t))
        mass_series.append(float(m_t))
        e000_series.append(float(e_t))
        transport_series.append(float(t_t))
        if prev_e000_power is not None:
            leakage_series.append(float(l_t))
        prev_e000_power = e000_power
        cur = k.step(cur)

    return {
        "rows": rows,
        "distance_profile": [
            {
                "d": int(r["d"]),
                "C_d": float(r["C_t"]),
                "M_d": float(r["M_t"]),
                "E_d": float(r["E_t"]),
                "T_d": float(r["T_t"]),
                "L_d": float(r["L_t"]),
            }
            for r in rows
        ],
        "summary": {
            "mean_C_t": _mean(coherence_series),
            "mean_M_t": _mean(mass_series),
            "mean_E_t": _mean(e000_series),
            "mean_T_t": _mean(transport_series),
            "positive_L_t_fraction": _mean([1.0 if x > 0.0 else 0.0 for x in leakage_series]),
            "mean_positive_L_t": _mean([x for x in leakage_series if x > 0.0]),
            "mean_abs_L_t": _mean([abs(x) for x in leakage_series]),
        },
    }


def _is_contiguous_nonnegative_integer_axis(ds: Sequence[int]) -> bool:
    if not ds:
        return False
    if any((not isinstance(d, int)) or d < 0 for d in ds):
        return False
    expected = list(range(len(ds)))
    return list(ds) == expected


def _mean_abs_leakage_tail(rows: Sequence[Dict[str, Any]], start_d: int) -> float:
    tail = [abs(float(r["L_t"])) for r in rows if int(r["d"]) >= int(start_d)]
    return _mean(tail)


def _forward_diff(xs: Sequence[float]) -> List[float]:
    return [float(xs[i + 1] - xs[i]) for i in range(len(xs) - 1)]


def _fraction_first_order_dominant(delta1: Sequence[float], delta2: Sequence[float], lo: int, hi: int) -> float:
    idx = [i for i in range(min(len(delta1), len(delta2))) if int(lo) <= i < int(hi)]
    if not idx:
        return 0.0
    return _mean([1.0 if abs(delta1[i]) >= abs(delta2[i]) else 0.0 for i in idx])


def _correction_onset_d(delta1: Sequence[float], delta2: Sequence[float]) -> int | None:
    ind = [1.0 if abs(delta2[i]) > abs(delta1[i]) else 0.0 for i in range(min(len(delta1), len(delta2)))]
    w = int(CORRECTION_ONSET_WINDOW)
    if len(ind) < w:
        return None
    for i in range(0, len(ind) - w + 1):
        if _mean(ind[i : i + w]) >= float(CORRECTION_ONSET_THRESHOLD):
            return int(i)
    return None


def _transfer_shape_from_profile(distance_profile: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    es = [float(r["E_d"]) for r in distance_profile]
    ls = [float(r["L_d"]) for r in distance_profile]
    d1e = _forward_diff(es)
    d2e = _forward_diff(d1e)
    d3e = _forward_diff(d2e)
    d1l = _forward_diff(ls)
    d2l = _forward_diff(d1l)
    d3l = _forward_diff(d2l)

    near_first_order_fraction = _fraction_first_order_dominant(d1e, d2e, 0, int(NEAR_FIELD_END_D))
    far_first_order_fraction = _fraction_first_order_dominant(
        d1e,
        d2e,
        int(FAR_FIELD_START_D),
        max(len(d2e), int(FAR_FIELD_START_D)),
    )
    near_high_order_fraction = 1.0 - near_first_order_fraction
    far_high_order_fraction = 1.0 - far_first_order_fraction

    return {
        "near_field_end_d": int(NEAR_FIELD_END_D),
        "far_field_start_d": int(FAR_FIELD_START_D),
        "correction_onset_window": int(CORRECTION_ONSET_WINDOW),
        "correction_onset_threshold": float(CORRECTION_ONSET_THRESHOLD),
        "E_d": {
            "delta1": [float(x) for x in d1e],
            "delta2": [float(x) for x in d2e],
            "delta3": [float(x) for x in d3e],
        },
        "L_d": {
            "delta1": [float(x) for x in d1l],
            "delta2": [float(x) for x in d2l],
            "delta3": [float(x) for x in d3l],
        },
        "near_field_first_order_fraction_E": float(near_first_order_fraction),
        "near_field_high_order_fraction_E": float(near_high_order_fraction),
        "far_field_first_order_fraction_E": float(far_first_order_fraction),
        "far_field_high_order_fraction_E": float(far_high_order_fraction),
        "correction_onset_d_E": _correction_onset_d(d1e, d2e),
    }


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    scenarios = _scenario_worlds()
    scenario_runs = {name: _run_scenario(world) for name, world in scenarios.items()}

    coherent = scenario_runs["coherent_triplet_v1"]["summary"]
    broken = scenario_runs["broken_off_cycle_v1"]["summary"]
    coherent_rows = scenario_runs["coherent_triplet_v1"]["rows"]
    broken_rows = scenario_runs["broken_off_cycle_v1"]["rows"]
    coherent_profile = scenario_runs["coherent_triplet_v1"]["distance_profile"]
    broken_profile = scenario_runs["broken_off_cycle_v1"]["distance_profile"]
    coherent_transfer = _transfer_shape_from_profile(coherent_profile)
    broken_transfer = _transfer_shape_from_profile(broken_profile)

    coherent_ds = [int(r["d"]) for r in coherent_rows]
    broken_ds = [int(r["d"]) for r in broken_rows]
    distance_axis_discrete = _is_contiguous_nonnegative_integer_axis(coherent_ds) and _is_contiguous_nonnegative_integer_axis(
        broken_ds
    )

    paired_count = min(len(coherent_rows), len(broken_rows))
    idxs = list(range(1, paired_count))
    leakage_nonstrict_fraction = _mean(
        [1.0 if float(broken_rows[i]["L_t"]) >= float(coherent_rows[i]["L_t"]) else 0.0 for i in idxs]
    )
    abs_leakage_nonstrict_fraction = _mean(
        [
            1.0
            if abs(float(broken_rows[i]["L_t"])) >= abs(float(coherent_rows[i]["L_t"]))
            else 0.0
            for i in idxs
        ]
    )
    coherent_tail_abs = _mean_abs_leakage_tail(coherent_rows, DISTANCE_TAIL_WINDOW_START)
    broken_tail_abs = _mean_abs_leakage_tail(broken_rows, DISTANCE_TAIL_WINDOW_START)

    checks = {
        "coherence_higher_in_coherent_triplet": coherent["mean_C_t"] > broken["mean_C_t"],
        "e000_share_higher_in_broken_state": broken["mean_E_t"] > coherent["mean_E_t"],
        "positive_leakage_frequency_higher_in_broken_state": (
            broken["positive_L_t_fraction"] > coherent["positive_L_t_fraction"]
        ),
        "terminal_mass_lower_in_broken_state": broken["mean_M_t"] < coherent["mean_M_t"],
        "transport_lower_in_broken_state": broken["mean_T_t"] < coherent["mean_T_t"],
        "distance_axis_discrete_and_contiguous": bool(distance_axis_discrete),
        "distance_tail_abs_leakage_higher_in_broken_state": broken_tail_abs > coherent_tail_abs,
        "distancewise_abs_leakage_nonstrict_majority_broken": abs_leakage_nonstrict_fraction >= 0.75,
        "coherent_nearfield_first_order_fraction_ge_0p6": float(
            coherent_transfer["near_field_first_order_fraction_E"]
        )
        >= 0.6,
        "broken_correction_onset_not_later_than_coherent": (
            coherent_transfer["correction_onset_d_E"] is not None
            and broken_transfer["correction_onset_d_E"] is not None
            and int(broken_transfer["correction_onset_d_E"]) <= int(coherent_transfer["correction_onset_d_E"])
        ),
        "coherent_farfield_high_order_fraction_gt_nearfield": float(
            coherent_transfer["far_field_high_order_fraction_E"]
        )
        > float(coherent_transfer["near_field_high_order_fraction_E"]),
    }

    payload: Dict[str, Any] = {
        "schema_version": "triplet_coherence_e000_leakage_v1",
        "axiom_profile": {
            "spacetime": "dag",
            "state_domain": "cxo_over_unity",
            "update_rule": "projective_lightcone_update",
            "kernel_profile": k.KERNEL_PROFILE,
            "projector_id": k.PROJECTOR_ID,
        },
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "hypothesis_id": "triplet_coherence_e000_leakage_v1",
        "hypothesis": (
            "Triplet-coherent motifs maintain higher triplet occupancy coherence and lower e000-axis leakage, "
            "while broken off-cycle motifs show higher e000 leakage, lower terminal non-e000 mass proxy, and lower transport proxy."
        ),
        "observables": {
            "C_t": "mean triplet occupancy fraction across source/mediator/terminal nodes",
            "M_t": "terminal node non-e000 mass proxy (sum abs2 over channels 1..7)",
            "E_t": "terminal e000 share abs2(e000)/(abs2(e000)+non_e000_power)",
            "L_t": "tick-wise terminal e000 power increment",
            "T_t": "terminal transport proxy target(4..6)/(source(1..3)+target(4..6))",
            "D_t": "discrete graph-distance index from initial state (integer tick depth)",
            "L_d": "distance-indexed leakage ladder value at discrete distance d",
        },
        "distance_contract": {
            "distance_axis_id": "graph_distance_tick_index_v1",
            "domain": "nonnegative_integers",
            "contiguous_from_zero": bool(distance_axis_discrete),
            "tail_window_start_d": int(DISTANCE_TAIL_WINDOW_START),
        },
        "distance_comparison": {
            "paired_distance_count": int(max(0, paired_count - 1)),
            "leakage_nonstrict_fraction_broken_ge_coherent": float(leakage_nonstrict_fraction),
            "abs_leakage_nonstrict_fraction_broken_ge_coherent": float(abs_leakage_nonstrict_fraction),
            "coherent_tail_mean_abs_L": float(coherent_tail_abs),
            "broken_tail_mean_abs_L": float(broken_tail_abs),
        },
        "discrete_transfer_function": {
            "model_id": "discrete_transfer_function_v1",
            "coherent_triplet_v1": coherent_transfer,
            "broken_off_cycle_v1": broken_transfer,
            "interpretation": [
                "Near-field is evaluated on integer depth bins without interpolation.",
                "Higher-order corrections are tracked through forward differences of E_d and L_d.",
            ],
        },
        "ticks": int(TICKS),
        "scenarios": {
            name: {
                "summary": data["summary"],
                "rows": data["rows"],
                "distance_profile": data["distance_profile"],
            }
            for name, data in scenario_runs.items()
        },
        "hypothesis_checks": checks,
        "all_checks_pass": bool(all(checks.values())),
        "limits": [
            "Toy 4-node DAG probe, not full physical closure.",
            "Observables are proxy metrics designed for falsifiable directionality tests.",
            "Does not by itself select a unique continuum bridge law.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    coherent = payload["scenarios"]["coherent_triplet_v1"]["summary"]
    broken = payload["scenarios"]["broken_off_cycle_v1"]["summary"]
    lines = [
        "# Triplet Coherence vs e000 Leakage Probe (v1)",
        "",
        f"- Hypothesis ID: `{payload['hypothesis_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        f"- Kernel profile: `{payload['axiom_profile']['kernel_profile']}`",
        f"- Projector ID: `{payload['axiom_profile']['projector_id']}`",
        f"- Ticks: {payload['ticks']}",
        "",
        "## Scenario Summary",
        "| Metric | coherent_triplet_v1 | broken_off_cycle_v1 |",
        "|---|---:|---:|",
        f"| mean_C_t | {coherent['mean_C_t']} | {broken['mean_C_t']} |",
        f"| mean_M_t | {coherent['mean_M_t']} | {broken['mean_M_t']} |",
        f"| mean_E_t | {coherent['mean_E_t']} | {broken['mean_E_t']} |",
        f"| mean_T_t | {coherent['mean_T_t']} | {broken['mean_T_t']} |",
        f"| positive_L_t_fraction | {coherent['positive_L_t_fraction']} | {broken['positive_L_t_fraction']} |",
        f"| mean_positive_L_t | {coherent['mean_positive_L_t']} | {broken['mean_positive_L_t']} |",
        "",
        "## Discrete Distance Contract",
        f"- distance_axis_id: `{payload['distance_contract']['distance_axis_id']}`",
        f"- domain: `{payload['distance_contract']['domain']}`",
        f"- contiguous_from_zero: `{payload['distance_contract']['contiguous_from_zero']}`",
        f"- tail_window_start_d: `{payload['distance_contract']['tail_window_start_d']}`",
        f"- abs_leakage_nonstrict_fraction_broken_ge_coherent: `{payload['distance_comparison']['abs_leakage_nonstrict_fraction_broken_ge_coherent']}`",
        "",
        "## Discrete Transfer Shape (E_d)",
        f"- coherent near_field_first_order_fraction_E: `{payload['discrete_transfer_function']['coherent_triplet_v1']['near_field_first_order_fraction_E']}`",
        f"- coherent far_field_high_order_fraction_E: `{payload['discrete_transfer_function']['coherent_triplet_v1']['far_field_high_order_fraction_E']}`",
        f"- coherent correction_onset_d_E: `{payload['discrete_transfer_function']['coherent_triplet_v1']['correction_onset_d_E']}`",
        f"- broken correction_onset_d_E: `{payload['discrete_transfer_function']['broken_off_cycle_v1']['correction_onset_d_E']}`",
        "",
        "## Hypothesis Checks",
    ]
    for key, value in payload["hypothesis_checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            f"- `all_checks_pass`: `{payload['all_checks_pass']}`",
            "",
            "## Limits",
        ]
    )
    for item in payload["limits"]:
        lines.append(f"- {item}")
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
    parser = argparse.ArgumentParser(description="Build triplet coherence vs e000 leakage probe artifact")
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
        "triplet_coherence_e000_leakage_v1: "
        f"all_checks_pass={payload['all_checks_pass']}, replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

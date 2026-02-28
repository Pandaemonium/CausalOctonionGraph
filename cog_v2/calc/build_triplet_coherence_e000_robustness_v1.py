"""Build robustness sweep for triplet-coherence vs e000-leakage (v1).

This extends the single-pair probe with multiple deterministic scenario pairs
to ensure directional checks are stable under phase-pattern variation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

try:
    from cog_v2.calc import build_triplet_coherence_e000_leakage_v1 as v1
    from cog_v2.python import kernel_projective_unity as k
except ModuleNotFoundError:
    REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from cog_v2.calc import build_triplet_coherence_e000_leakage_v1 as v1
    from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "triplet_coherence_e000_robustness_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "triplet_coherence_e000_robustness_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_triplet_coherence_e000_robustness_v1.py"
BASELINE_ARTIFACT_REPO_PATH = "cog_v2/sources/triplet_coherence_e000_leakage_v1.json"


PARENTS_BASELINE: Dict[str, List[str]] = {
    "s": [],
    "b": [],
    "m": ["s", "b"],
    "t": ["m", "b"],
}

PARENTS_ALT_BRANCH: Dict[str, List[str]] = {
    "s": [],
    "b": [],
    "m": ["s", "b"],
    "t": ["m", "s"],
}

SCENARIO_PAIRS: Tuple[Dict[str, Any], ...] = (
    {
        "pair_id": "pair_1",
        "topology_id": "baseline_v1",
        "parents": PARENTS_BASELINE,
        "coherent_s": {
            1: k.ONE_G,
            2: k.I_G,
            3: k.MINUS_I_G,
            4: k.ONE_G,
            5: k.ONE_G,
        },
        "coherent_b": {
            4: k.ONE_G,
            5: k.I_G,
            6: k.MINUS_I_G,
        },
        "broken_s": {
            1: k.ONE_G,
            4: k.I_G,
            7: k.MINUS_ONE_G,
        },
        "broken_b": {
            0: k.ONE_G,
            7: k.ONE_G,
        },
    },
    {
        "pair_id": "pair_2",
        "topology_id": "baseline_v1",
        "parents": PARENTS_BASELINE,
        "coherent_s": {
            1: k.MINUS_ONE_G,
            2: k.I_G,
            3: k.MINUS_I_G,
            4: k.ONE_G,
            5: k.ONE_G,
        },
        "coherent_b": {
            4: k.MINUS_ONE_G,
            5: k.I_G,
            6: k.MINUS_I_G,
        },
        "broken_s": {
            1: k.MINUS_ONE_G,
            4: k.I_G,
            7: k.MINUS_ONE_G,
        },
        "broken_b": {
            0: k.ONE_G,
            7: k.MINUS_ONE_G,
        },
    },
    {
        "pair_id": "pair_3",
        "topology_id": "baseline_v1",
        "parents": PARENTS_BASELINE,
        "coherent_s": {
            1: k.I_G,
            2: k.ONE_G,
            3: k.MINUS_I_G,
            4: k.I_G,
            5: k.ONE_G,
        },
        "coherent_b": {
            4: k.I_G,
            5: k.ONE_G,
            6: k.MINUS_I_G,
        },
        "broken_s": {
            1: k.I_G,
            4: k.ONE_G,
            7: k.ONE_G,
        },
        "broken_b": {
            0: k.ONE_G,
            7: k.I_G,
        },
    },
    {
        "pair_id": "pair_4",
        "topology_id": "alt_branch_v1",
        "parents": PARENTS_ALT_BRANCH,
        "coherent_s": {
            1: k.MINUS_I_G,
            2: k.MINUS_ONE_G,
            3: k.MINUS_ONE_G,
            4: k.MINUS_I_G,
        },
        "coherent_b": {
            4: k.I_G,
            5: k.MINUS_I_G,
            6: k.I_G,
        },
        "broken_s": {
            1: k.ONE_G,
            4: k.ONE_G,
            7: k.ONE_G,
        },
        "broken_b": {
            0: k.MINUS_I_G,
            5: k.MINUS_I_G,
            7: k.MINUS_ONE_G,
        },
    },
)

CHECK_KEYS_CRITICAL_ALL_PAIRS: Tuple[str, ...] = (
    "coherence_higher_in_coherent_triplet",
    "e000_share_higher_in_broken_state",
    "terminal_mass_lower_in_broken_state",
    "transport_lower_in_broken_state",
    "distance_axis_discrete_and_contiguous",
)

CHECK_KEYS_SUPPORTING_MAJORITY: Tuple[str, ...] = (
    "positive_leakage_frequency_higher_in_broken_state",
    "distance_tail_abs_leakage_higher_in_broken_state",
    "distancewise_abs_leakage_nonstrict_majority_broken",
    "coherent_nearfield_first_order_fraction_ge_0p6",
    "broken_correction_onset_not_later_than_coherent",
    "coherent_farfield_high_order_fraction_gt_nearfield",
)


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _mean(xs: Sequence[float]) -> float:
    if not xs:
        return 0.0
    return float(sum(xs) / float(len(xs)))


def _state_from_map(vals: Dict[int, k.GInt]) -> k.CxO:
    data = [k.ZERO_G] * 8
    for idx, value in vals.items():
        data[int(idx)] = value
    return (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])


def _world_pair(pair: Dict[str, Any]) -> Tuple[k.World, k.World]:
    parents = pair.get("parents")
    if not isinstance(parents, dict):
        raise ValueError("scenario pair missing parents map")
    coherent_states = {
        "s": _state_from_map(pair["coherent_s"]),
        "b": _state_from_map(pair["coherent_b"]),
        "m": k.cxo_one(),
        "t": k.cxo_one(),
    }
    broken_states = {
        "s": _state_from_map(pair["broken_s"]),
        "b": _state_from_map(pair["broken_b"]),
        "m": k.cxo_one(),
        "t": k.cxo_one(),
    }
    coherent_world = k.World(
        node_ids=list(v1.NODE_IDS),
        parents={str(k1): [str(x) for x in v1_] for k1, v1_ in parents.items()},
        states=coherent_states,
        event_order=None,
        tick=0,
    )
    broken_world = k.World(
        node_ids=list(v1.NODE_IDS),
        parents={str(k1): [str(x) for x in v1_] for k1, v1_ in parents.items()},
        states=broken_states,
        event_order=None,
        tick=0,
    )
    return coherent_world, broken_world


def _pair_checks(
    coherent_run: Dict[str, Any],
    broken_run: Dict[str, Any],
) -> Dict[str, bool]:
    coherent = coherent_run["summary"]
    broken = broken_run["summary"]
    coherent_rows = coherent_run["rows"]
    broken_rows = broken_run["rows"]
    coherent_profile = coherent_run["distance_profile"]
    broken_profile = broken_run["distance_profile"]
    coherent_transfer = v1._transfer_shape_from_profile(coherent_profile)
    broken_transfer = v1._transfer_shape_from_profile(broken_profile)

    coherent_ds = [int(r["d"]) for r in coherent_rows]
    broken_ds = [int(r["d"]) for r in broken_rows]
    distance_axis_discrete = v1._is_contiguous_nonnegative_integer_axis(coherent_ds) and v1._is_contiguous_nonnegative_integer_axis(
        broken_ds
    )

    paired_count = min(len(coherent_rows), len(broken_rows))
    idxs = list(range(1, paired_count))
    abs_leakage_nonstrict_fraction = _mean(
        [
            1.0 if abs(float(broken_rows[i]["L_t"])) >= abs(float(coherent_rows[i]["L_t"])) else 0.0
            for i in idxs
        ]
    )
    coherent_tail_abs = v1._mean_abs_leakage_tail(coherent_rows, v1.DISTANCE_TAIL_WINDOW_START)
    broken_tail_abs = v1._mean_abs_leakage_tail(broken_rows, v1.DISTANCE_TAIL_WINDOW_START)

    return {
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


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    baseline_artifact_path = ROOT / BASELINE_ARTIFACT_REPO_PATH

    pair_rows: List[Dict[str, Any]] = []
    coherent_near_first: List[float] = []
    coherent_near_high: List[float] = []
    coherent_far_high: List[float] = []
    coherent_onsets: List[int] = []
    broken_onsets: List[int] = []
    topology_ids: List[str] = []

    for idx, pair in enumerate(SCENARIO_PAIRS):
        coherent_world, broken_world = _world_pair(pair)
        coherent_run = v1._run_scenario(coherent_world)
        broken_run = v1._run_scenario(broken_world)
        coherent_transfer = v1._transfer_shape_from_profile(coherent_run["distance_profile"])
        broken_transfer = v1._transfer_shape_from_profile(broken_run["distance_profile"])
        checks = _pair_checks(coherent_run, broken_run)

        coherent_near_first.append(float(coherent_transfer["near_field_first_order_fraction_E"]))
        coherent_near_high.append(float(coherent_transfer["near_field_high_order_fraction_E"]))
        coherent_far_high.append(float(coherent_transfer["far_field_high_order_fraction_E"]))
        if coherent_transfer["correction_onset_d_E"] is not None:
            coherent_onsets.append(int(coherent_transfer["correction_onset_d_E"]))
        if broken_transfer["correction_onset_d_E"] is not None:
            broken_onsets.append(int(broken_transfer["correction_onset_d_E"]))
        topology_ids.append(str(pair.get("topology_id", f"topology_{idx + 1}")))

        pair_rows.append(
            {
                "pair_id": str(pair.get("pair_id", f"pair_{idx + 1}")),
                "topology_id": str(pair.get("topology_id", f"topology_{idx + 1}")),
                "parents": {k1: list(v1_) for k1, v1_ in pair["parents"].items()},
                "coherent_summary": coherent_run["summary"],
                "broken_summary": broken_run["summary"],
                "coherent_transfer_shape": coherent_transfer,
                "broken_transfer_shape": broken_transfer,
                "checks": checks,
                "all_checks_pass": bool(all(checks.values())),
            }
        )

    check_keys = sorted({key for row in pair_rows for key in row["checks"].keys()})
    check_pass_rates = {
        key: _mean([1.0 if bool(row["checks"].get(key, False)) else 0.0 for row in pair_rows])
        for key in check_keys
    }
    critical_all_pairs_hold = all(check_pass_rates.get(key, 0.0) == 1.0 for key in CHECK_KEYS_CRITICAL_ALL_PAIRS)
    supporting_majority_hold = all(check_pass_rates.get(key, 0.0) >= (2.0 / 3.0) for key in CHECK_KEYS_SUPPORTING_MAJORITY)
    topology_family_count = len(set(topology_ids))

    envelope = {
        "envelope_id": "theta_discrete_correction_envelope_robustness_v1",
        "distance_axis_id": "graph_distance_tick_index_v1",
        "pair_count": int(len(pair_rows)),
        "topology_ids": sorted(set(topology_ids)),
        "topology_family_count": int(topology_family_count),
        "coherent_near_first_order_fraction_mean_E": _mean(coherent_near_first),
        "coherent_near_high_order_fraction_mean_E": _mean(coherent_near_high),
        "coherent_far_high_order_fraction_mean_E": _mean(coherent_far_high),
        "coherent_correction_onset_d_E_mean": _mean([float(x) for x in coherent_onsets]),
        "broken_correction_onset_d_E_mean": _mean([float(x) for x in broken_onsets]),
        "coherent_correction_onset_d_E_min": int(min(coherent_onsets)) if coherent_onsets else None,
        "broken_correction_onset_d_E_min": int(min(broken_onsets)) if broken_onsets else None,
        "critical_all_pairs_hold": bool(critical_all_pairs_hold),
        "supporting_majority_hold": bool(supporting_majority_hold),
    }
    envelope["robustness_lane_ready"] = bool(
        envelope["coherent_near_first_order_fraction_mean_E"] >= 0.6
        and envelope["coherent_far_high_order_fraction_mean_E"] > envelope["coherent_near_high_order_fraction_mean_E"]
        and critical_all_pairs_hold
        and supporting_majority_hold
        and topology_family_count >= 2
    )

    payload: Dict[str, Any] = {
        "schema_version": "triplet_coherence_e000_robustness_v1",
        "axiom_profile": {
            "spacetime": "dag",
            "state_domain": "cxo_over_unity",
            "update_rule": "projective_lightcone_update",
            "kernel_profile": k.KERNEL_PROFILE,
            "projector_id": k.PROJECTOR_ID,
        },
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "baseline_artifact": BASELINE_ARTIFACT_REPO_PATH,
        "baseline_artifact_sha256": _sha_file(baseline_artifact_path) if baseline_artifact_path.exists() else "",
        "ticks": int(v1.TICKS),
        "pair_rows": pair_rows,
        "check_pass_rates": check_pass_rates,
        "critical_checks_required_all_pairs": list(CHECK_KEYS_CRITICAL_ALL_PAIRS),
        "supporting_checks_required_majority": list(CHECK_KEYS_SUPPORTING_MAJORITY),
        "discrete_correction_envelope_robustness": envelope,
        "robustness_lane_ready": bool(envelope["robustness_lane_ready"]),
        "limits": [
            "Deterministic scenario family sweep, not full physical closure.",
            "This artifact stress-tests directional stability of the structure-first proxy checks.",
            "Pair-family coverage can be extended without changing acceptance semantics.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    envelope = payload["discrete_correction_envelope_robustness"]
    lines = [
        "# Triplet Coherence e000 Robustness Sweep (v1)",
        "",
        f"- Replay hash: `{payload['replay_hash']}`",
        f"- Kernel profile: `{payload['axiom_profile']['kernel_profile']}`",
        f"- Pair count: `{len(payload['pair_rows'])}`",
        f"- Topology families: `{payload['discrete_correction_envelope_robustness']['topology_ids']}`",
        f"- Robustness lane ready: `{payload['robustness_lane_ready']}`",
        "",
        "## Envelope",
        f"- envelope_id: `{envelope['envelope_id']}`",
        f"- coherent_near_first_order_fraction_mean_E: `{envelope['coherent_near_first_order_fraction_mean_E']}`",
        f"- coherent_far_high_order_fraction_mean_E: `{envelope['coherent_far_high_order_fraction_mean_E']}`",
        f"- coherent_near_high_order_fraction_mean_E: `{envelope['coherent_near_high_order_fraction_mean_E']}`",
        f"- critical_all_pairs_hold: `{envelope['critical_all_pairs_hold']}`",
        f"- supporting_majority_hold: `{envelope['supporting_majority_hold']}`",
        "",
        "## Pair Summary",
        "| Pair | Topology | all_checks_pass | coherent mean_C_t | broken mean_E_t | broken mean_M_t |",
        "|---|---|---|---:|---:|---:|",
    ]
    for row in payload["pair_rows"]:
        lines.append(
            f"| {row['pair_id']} | {row['topology_id']} | {row['all_checks_pass']} | "
            f"{row['coherent_summary']['mean_C_t']} | "
            f"{row['broken_summary']['mean_E_t']} | "
            f"{row['broken_summary']['mean_M_t']} |"
        )

    lines.extend(
        [
            "",
            "## Check Pass Rates",
            "| Check | Pass rate |",
            "|---|---:|",
        ]
    )
    for key in sorted(payload["check_pass_rates"].keys()):
        lines.append(f"| {key} | {payload['check_pass_rates'][key]} |")
    lines.extend(
        [
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
    parser = argparse.ArgumentParser(description="Build triplet coherence e000 robustness sweep artifact")
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
        "triplet_coherence_e000_robustness_v1: "
        f"robustness_lane_ready={payload['robustness_lane_ready']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

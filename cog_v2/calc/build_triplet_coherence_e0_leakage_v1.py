"""Formalize triplet-coherence vs e0-leakage hypothesis under COG v2 kernel.

Hypothesis (v1):
1) 3-cycle coherent source motifs preserve triplet occupancy coherence.
2) Off-cycle/broken motifs show stronger e0-axis leakage.
3) Broken motifs reduce terminal non-e0 mass proxy and transport proxy.

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
OUT_JSON = ROOT / "cog_v2" / "sources" / "triplet_coherence_e0_leakage_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "triplet_coherence_e0_leakage_v1.md"

SCRIPT_REPO_PATH = "cog_v2/calc/build_triplet_coherence_e0_leakage_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
TICKS = 120

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
    non_e0_power = float(sum(_abs2(z) for z in state[1:]))
    if non_e0_power == 0.0:
        return 0.0
    return triplet_power / non_e0_power


def _e0_share(state: k.CxO) -> float:
    e0 = float(_abs2(state[0]))
    non_e0 = float(sum(_abs2(z) for z in state[1:]))
    total = e0 + non_e0
    if total == 0.0:
        return 0.0
    return e0 / total


def _terminal_non_e0_mass_proxy(state: k.CxO) -> float:
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
            }
        ),
        "b": _state_from_map(
            {
                1: k.ONE_G,
                2: k.ONE_G,
                3: k.ONE_G,
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
    e0_series: List[float] = []
    transport_series: List[float] = []
    leakage_series: List[float] = []
    prev_e0_power: float | None = None

    cur = world
    for _ in range(TICKS):
        source = cur.states["s"]
        mediator = cur.states["m"]
        terminal = cur.states["t"]

        c_t = _coherence_score(source, mediator, terminal)
        m_t = _terminal_non_e0_mass_proxy(terminal)
        e_t = _e0_share(terminal)
        t_t = _transport_proxy(terminal)
        e0_power = float(_abs2(terminal[0]))
        l_t = 0.0 if prev_e0_power is None else float(e0_power - prev_e0_power)

        rows.append(
            {
                "tick": int(cur.tick),
                "C_t": float(c_t),
                "M_t": float(m_t),
                "E_t": float(e_t),
                "T_t": float(t_t),
                "L_t": float(l_t),
            }
        )
        coherence_series.append(float(c_t))
        mass_series.append(float(m_t))
        e0_series.append(float(e_t))
        transport_series.append(float(t_t))
        if prev_e0_power is not None:
            leakage_series.append(float(l_t))
        prev_e0_power = e0_power
        cur = k.step(cur)

    return {
        "rows": rows,
        "summary": {
            "mean_C_t": _mean(coherence_series),
            "mean_M_t": _mean(mass_series),
            "mean_E_t": _mean(e0_series),
            "mean_T_t": _mean(transport_series),
            "positive_L_t_fraction": _mean([1.0 if x > 0.0 else 0.0 for x in leakage_series]),
            "mean_positive_L_t": _mean([x for x in leakage_series if x > 0.0]),
            "mean_abs_L_t": _mean([abs(x) for x in leakage_series]),
        },
    }


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    scenarios = _scenario_worlds()
    scenario_runs = {name: _run_scenario(world) for name, world in scenarios.items()}

    coherent = scenario_runs["coherent_triplet_v1"]["summary"]
    broken = scenario_runs["broken_off_cycle_v1"]["summary"]

    checks = {
        "coherence_higher_in_coherent_triplet": coherent["mean_C_t"] > broken["mean_C_t"],
        "e0_share_higher_in_broken_state": broken["mean_E_t"] > coherent["mean_E_t"],
        "positive_leakage_frequency_higher_in_broken_state": (
            broken["positive_L_t_fraction"] > coherent["positive_L_t_fraction"]
        ),
        "terminal_mass_lower_in_broken_state": broken["mean_M_t"] < coherent["mean_M_t"],
        "transport_lower_in_broken_state": broken["mean_T_t"] < coherent["mean_T_t"],
    }

    payload: Dict[str, Any] = {
        "schema_version": "triplet_coherence_e0_leakage_v1",
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
        "hypothesis_id": "triplet_coherence_e0_leakage_v1",
        "hypothesis": (
            "Triplet-coherent motifs maintain higher triplet occupancy coherence and lower e0-axis leakage, "
            "while broken off-cycle motifs show higher e0 leakage, lower terminal non-e0 mass proxy, and lower transport proxy."
        ),
        "observables": {
            "C_t": "mean triplet occupancy fraction across source/mediator/terminal nodes",
            "M_t": "terminal node non-e0 mass proxy (sum abs2 over channels 1..7)",
            "E_t": "terminal e0 share abs2(e0)/(abs2(e0)+non_e0_power)",
            "L_t": "tick-wise terminal e0 power increment",
            "T_t": "terminal transport proxy target(4..6)/(source(1..3)+target(4..6))",
        },
        "ticks": int(TICKS),
        "scenarios": {
            name: {
                "summary": data["summary"],
                "rows": data["rows"],
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
        "# Triplet Coherence vs e0 Leakage Probe (v1)",
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
    parser = argparse.ArgumentParser(description="Build triplet coherence vs e0 leakage probe artifact")
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
        "triplet_coherence_e0_leakage_v1: "
        f"all_checks_pass={payload['all_checks_pass']}, replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

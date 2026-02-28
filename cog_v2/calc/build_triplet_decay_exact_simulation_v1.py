"""Exact triplet-decay simulation under canonical v2 projection kernel.

Purpose:
1) Start from a stable triplet motif (quark-like resonance),
2) Introduce a high-energy perturbing motif (including a hypothetical GUT X/Y proxy),
3) Decrease graph-distance over ticks so interaction strength rises,
4) Record exact per-tick microstates and decay diagnostics.

All arithmetic is exact over Gaussian integers with deterministic projection to
the unity alphabet via `kernel_projective_unity`.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "triplet_decay_exact_simulation_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "triplet_decay_exact_simulation_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_triplet_decay_exact_simulation_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"

BASIS_LABELS: Tuple[str, ...] = tuple(k.BASIS_LABELS)
TRIPLET_CHANNELS: Tuple[int, int, int] = (1, 2, 3)


@dataclass(frozen=True)
class SimulationParams:
    ticks: int = 96
    d_start: int = 12
    d_min: int = 0
    approach_speed: int = 1
    interaction_radius: int = 6
    energy_scale: int = 2
    weak_kick_e111: int = 1
    coherence_decay_threshold: float = 0.45
    e000_decay_threshold: float = 0.20


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _safe_path_label(path: Path) -> str:
    try:
        return _to_repo_path(path)
    except Exception:
        return str(path).replace("\\", "/")


def _coeff(re: int, im: int = 0) -> k.GInt:
    return k.GInt(int(re), int(im))


def _state_from_sparse(mapping: Dict[int, k.GInt]) -> k.CxO:
    vals = [k.ZERO_G] * 8
    for idx, z in mapping.items():
        vals[int(idx)] = z
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _serialize_state(state: k.CxO) -> List[List[int]]:
    return [[int(z.re), int(z.im)] for z in state]


def _state_to_map(state: k.CxO) -> Dict[str, List[int]]:
    return {BASIS_LABELS[i]: [int(z.re), int(z.im)] for i, z in enumerate(state)}


def _abs2(z: k.GInt) -> int:
    return int(z.re * z.re + z.im * z.im)


def _triplet_coherence(state: k.CxO) -> float:
    trip = float(sum(_abs2(state[i]) for i in TRIPLET_CHANNELS))
    non_e000 = float(sum(_abs2(state[i]) for i in range(1, 8)))
    if non_e000 == 0.0:
        return 0.0
    return trip / non_e000


def _e000_share(state: k.CxO) -> float:
    e0 = float(_abs2(state[0]))
    non = float(sum(_abs2(state[i]) for i in range(1, 8)))
    total = e0 + non
    if total == 0.0:
        return 0.0
    return e0 / total


def _dominant_nontriplet_channels(state: k.CxO, top_k: int = 3) -> List[str]:
    rows: List[Tuple[int, int]] = []
    for idx in range(1, 8):
        if idx in TRIPLET_CHANNELS:
            continue
        rows.append((idx, _abs2(state[idx])))
    rows.sort(key=lambda x: x[1], reverse=True)
    return [BASIS_LABELS[idx] for idx, power in rows[:top_k] if power > 0]


def _basis_state(op_idx: int) -> k.CxO:
    vals = [k.ZERO_G] * 8
    vals[int(op_idx)] = k.ONE_G
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _left_mul_projected(op_idx: int, state: k.CxO) -> k.CxO:
    return k.project_cxo_to_unity(k.cxo_mul(_basis_state(int(op_idx)), state))


def _distance_at_tick(params: SimulationParams, tick: int) -> int:
    d = int(params.d_start) - int(params.approach_speed) * int(tick)
    return max(int(params.d_min), d)


def _coupling_multiplicity(params: SimulationParams, distance: int) -> int:
    if int(distance) > int(params.interaction_radius):
        return 0
    return int(params.energy_scale) * (int(params.interaction_radius) - int(distance) + 1)


def _motif_library() -> Dict[str, Dict[str, List[int]]]:
    return {
        "stable_triplet_quark_v1": {
            "e001": [1, 0],
            "e010": [0, 1],
            "e011": [0, -1],
        },
        "high_energy_perturber_v1": {
            "e001": [1, 0],
            "e010": [1, 0],
            "e011": [1, 0],
            "e111": [0, 1],
        },
        # Hypothetical GUT mediator proxy (X/Y boson-like). Proton decay is not
        # experimentally observed; this motif is an exploratory high-energy lane.
        "xy_gut_boson_proxy_v1": {
            "e100": [1, 0],
            "e101": [0, 1],
            "e110": [0, -1],
            "e111": [1, 0],
        },
    }


def _state_from_motif(motif_id: str) -> k.CxO:
    lib = _motif_library()
    if motif_id not in lib:
        raise ValueError(f"Unknown motif_id: {motif_id}")
    sparse = lib[motif_id]
    mapping: Dict[int, k.GInt] = {}
    for i, label in enumerate(BASIS_LABELS):
        if label in sparse:
            re, im = sparse[label]
            mapping[i] = _coeff(re, im)
    return _state_from_sparse(mapping)


def _inject_e111_kick(state: k.CxO, kick: int) -> k.CxO:
    vals = list(state)
    cur = vals[7]
    vals[7] = k.GInt(cur.re + int(kick), cur.im)
    return k.project_cxo_to_unity((vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7]))


def _simulate_single(
    *,
    scenario_id: str,
    quark_motif_id: str,
    perturber_motif_id: str,
    params: SimulationParams,
    quark_ops: Sequence[int],
    perturber_ops: Sequence[int],
) -> Dict[str, Any]:
    q = _state_from_motif(quark_motif_id)
    p = _state_from_motif(perturber_motif_id)
    q = k.project_cxo_to_unity(q)
    p = k.project_cxo_to_unity(p)

    rows: List[Dict[str, Any]] = []
    first_decay_tick: int | None = None
    first_motif_break_tick: int | None = None
    first_vacuum_coupled_tick: int | None = None
    first_daughter_tick: int | None = None
    for tick in range(int(params.ticks)):
        q_op = int(quark_ops[tick % len(quark_ops)])
        p_op = int(perturber_ops[tick % len(perturber_ops)])

        q_internal = _left_mul_projected(q_op, q)
        p_internal = _left_mul_projected(p_op, p)

        distance = _distance_at_tick(params, tick)
        multiplicity = _coupling_multiplicity(params, distance)

        q_seed = q_internal
        if multiplicity > 0 and int(params.weak_kick_e111) != 0:
            q_seed = _inject_e111_kick(q_seed, int(params.weak_kick_e111))

        q_next = k.update_rule(q_seed, [p_internal for _ in range(multiplicity)])
        p_next = p_internal

        coherence = _triplet_coherence(q_next)
        e000 = _e000_share(q_next)
        off_motif = float(coherence) < float(params.coherence_decay_threshold)
        dominant_nontriplet = _dominant_nontriplet_channels(q_next)
        daughter_channels_present = len(dominant_nontriplet) > 0
        vacuum_coupled = int(multiplicity) > 0 and float(e000) >= float(params.e000_decay_threshold)
        decay_active = off_motif and (vacuum_coupled or daughter_channels_present)
        if off_motif and first_motif_break_tick is None:
            first_motif_break_tick = int(tick)
        if vacuum_coupled and first_vacuum_coupled_tick is None:
            first_vacuum_coupled_tick = int(tick)
        if daughter_channels_present and first_daughter_tick is None:
            first_daughter_tick = int(tick)
        if decay_active and first_decay_tick is None:
            first_decay_tick = int(tick)

        rows.append(
            {
                "tick": int(tick),
                "distance": int(distance),
                "coupling_multiplicity": int(multiplicity),
                "quark_op": int(q_op),
                "perturber_op": int(p_op),
                "quark_state": _state_to_map(q_next),
                "quark_state_vector": _serialize_state(q_next),
                "perturber_state": _state_to_map(p_next),
                "perturber_state_vector": _serialize_state(p_next),
                "triplet_coherence": float(coherence),
                "e000_share": float(e000),
                "off_motif": bool(off_motif),
                "vacuum_coupled": bool(vacuum_coupled),
                "daughter_channels_present": bool(daughter_channels_present),
                "decay_active": bool(decay_active),
                "dominant_nontriplet_channels": dominant_nontriplet,
            }
        )

        q = q_next
        p = p_next

    summary = {
        "first_decay_tick": first_decay_tick,
        "first_motif_break_tick": first_motif_break_tick,
        "first_vacuum_coupled_tick": first_vacuum_coupled_tick,
        "first_daughter_tick": first_daughter_tick,
        "any_decay": bool(first_decay_tick is not None),
        "any_motif_break": bool(first_motif_break_tick is not None),
        "any_vacuum_coupled": bool(first_vacuum_coupled_tick is not None),
        "any_daughter_channels": bool(first_daughter_tick is not None),
        "final_triplet_coherence": float(rows[-1]["triplet_coherence"]),
        "final_e000_share": float(rows[-1]["e000_share"]),
        "decay_tick_count": int(sum(1 for r in rows if bool(r["decay_active"]))),
        "vacuum_coupled_tick_count": int(sum(1 for r in rows if bool(r["vacuum_coupled"]))),
        "daughter_tick_count": int(sum(1 for r in rows if bool(r["daughter_channels_present"]))),
        "max_coupling_multiplicity": int(max(int(r["coupling_multiplicity"]) for r in rows)),
    }

    return {
        "scenario_id": scenario_id,
        "quark_motif_id": quark_motif_id,
        "perturber_motif_id": perturber_motif_id,
        "params": {
            "ticks": int(params.ticks),
            "d_start": int(params.d_start),
            "d_min": int(params.d_min),
            "approach_speed": int(params.approach_speed),
            "interaction_radius": int(params.interaction_radius),
            "energy_scale": int(params.energy_scale),
            "weak_kick_e111": int(params.weak_kick_e111),
            "coherence_decay_threshold": float(params.coherence_decay_threshold),
            "e000_decay_threshold": float(params.e000_decay_threshold),
        },
        "quark_ops": [int(x) for x in quark_ops],
        "perturber_ops": [int(x) for x in perturber_ops],
        "summary": summary,
        "tick_rows": rows,
    }


def _iter_op_sequences(length: int) -> Iterable[Tuple[int, ...]]:
    if int(length) <= 0:
        yield (1, 2, 3, 1, 2, 3, 4, 5)
        return
    alphabet = tuple(range(1, 8))
    for seq in itertools.product(alphabet, repeat=int(length)):
        yield tuple(int(x) for x in seq)


def build_payload(
    *,
    params: SimulationParams | None = None,
    exhaustive_op_length: int = 0,
    max_scenarios: int = 32,
    checkpoint_every: int = 0,
    checkpoint_dir: str | None = None,
) -> Dict[str, Any]:
    p = params if params is not None else SimulationParams()
    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH

    quark_motif_id = "stable_triplet_quark_v1"
    perturber_pool = ("high_energy_perturber_v1", "xy_gut_boson_proxy_v1")

    scenarios: List[Dict[str, Any]] = []
    ckpt_root = None
    if checkpoint_dir is not None and str(checkpoint_dir).strip():
        ckpt_root = Path(checkpoint_dir)
        ckpt_root.mkdir(parents=True, exist_ok=True)

    scenario_index = 0
    for pert in perturber_pool:
        for pert_seq in _iter_op_sequences(int(exhaustive_op_length)):
            sid = f"triplet_decay_{scenario_index:06d}_{pert}"
            sc = _simulate_single(
                scenario_id=sid,
                quark_motif_id=quark_motif_id,
                perturber_motif_id=pert,
                params=p,
                quark_ops=(1, 2, 3, 1, 2, 3, 6, 7),
                perturber_ops=pert_seq,
            )
            scenarios.append(sc)
            scenario_index += 1

            if ckpt_root is not None and int(checkpoint_every) > 0 and (scenario_index % int(checkpoint_every) == 0):
                ckpt_file = ckpt_root / f"triplet_decay_exact_checkpoint_{scenario_index:06d}.json"
                ckpt_payload = {
                    "schema_version": "triplet_decay_exact_checkpoint_v1",
                    "scenario_count": int(len(scenarios)),
                    "scenarios": scenarios,
                }
                ckpt_payload["replay_hash"] = _sha_payload(ckpt_payload)
                ckpt_file.write_text(json.dumps(ckpt_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            if int(max_scenarios) > 0 and len(scenarios) >= int(max_scenarios):
                break
        if int(max_scenarios) > 0 and len(scenarios) >= int(max_scenarios):
            break

    decay_hits = [s for s in scenarios if bool(s["summary"]["any_decay"])]
    xy_hits = [s for s in decay_hits if str(s["perturber_motif_id"]) == "xy_gut_boson_proxy_v1"]

    payload: Dict[str, Any] = {
        "schema_version": "triplet_decay_exact_simulation_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "projector_id": k.PROJECTOR_ID,
        "basis_labels": list(BASIS_LABELS),
        "motif_library": _motif_library(),
        "scenario_profile": {
            "quark_motif": quark_motif_id,
            "perturber_pool": list(perturber_pool),
            "exhaustive_op_length": int(exhaustive_op_length),
            "max_scenarios": int(max_scenarios),
            "checkpoint_every": int(checkpoint_every),
            "checkpoint_dir": None if ckpt_root is None else _safe_path_label(ckpt_root),
            "params": {
                "ticks": int(p.ticks),
                "d_start": int(p.d_start),
                "d_min": int(p.d_min),
                "approach_speed": int(p.approach_speed),
                "interaction_radius": int(p.interaction_radius),
                "energy_scale": int(p.energy_scale),
                "weak_kick_e111": int(p.weak_kick_e111),
                "coherence_decay_threshold": float(p.coherence_decay_threshold),
                "e000_decay_threshold": float(p.e000_decay_threshold),
            },
        },
        "summary": {
            "scenario_count": int(len(scenarios)),
            "decay_hit_count": int(len(decay_hits)),
            "xy_proxy_decay_hit_count": int(len(xy_hits)),
            "all_exact_integer_states": True,
            "simulation_exactness": (
                "Deterministic exact Gaussian-integer arithmetic with deterministic unity projection; "
                "no floating-point integration or stochastic terms."
            ),
            "proton_decay_note": (
                "X/Y motif is a hypothetical GUT mediator proxy for exploratory proton-decay-like perturbation lanes."
            ),
        },
        "scenarios": scenarios,
        "limits": [
            "This is an exact finite simulation family, not a proof that physical proton decay occurs in nature.",
            "X/Y lane is explicitly hypothetical and used as a high-energy perturbation proxy.",
            "Full universe-scale exhaustive time crystal closure may be computationally intractable; this package keeps exact local dynamics.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Triplet Decay Exact Simulation (v1)",
        "",
        f"- replay_hash: `{payload['replay_hash']}`",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- projector_id: `{payload['projector_id']}`",
        f"- scenario_count: `{s['scenario_count']}`",
        f"- decay_hit_count: `{s['decay_hit_count']}`",
        f"- xy_proxy_decay_hit_count: `{s['xy_proxy_decay_hit_count']}`",
        "",
        "## Scenario Summary",
        "",
        "| scenario_id | perturber | any_decay | first_decay_tick | final_coherence | final_e000_share | max_coupling |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for sc in payload["scenarios"]:
        ss = sc["summary"]
        lines.append(
            f"| {sc['scenario_id']} | {sc['perturber_motif_id']} | {ss['any_decay']} | "
            f"{'' if ss['first_decay_tick'] is None else ss['first_decay_tick']} | "
            f"{ss['final_triplet_coherence']:.6f} | {ss['final_e000_share']:.6f} | "
            f"{ss['max_coupling_multiplicity']} |"
        )
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
    parser = argparse.ArgumentParser(description="Build exact triplet-decay simulation artifact")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write artifacts to cog_v2/sources")
    parser.add_argument("--ticks", type=int, default=96, help="Tick count per scenario")
    parser.add_argument("--exhaustive-op-length", type=int, default=0, help="If >0, enumerate all 7^L perturbor op sequences exactly")
    parser.add_argument("--max-scenarios", type=int, default=32, help="Max scenario count (0 means unlimited)")
    parser.add_argument("--checkpoint-every", type=int, default=0, help="Write checkpoint JSON every N scenarios")
    parser.add_argument("--checkpoint-dir", type=str, default="", help="Checkpoint directory")
    args = parser.parse_args()

    params = SimulationParams(ticks=int(args.ticks))
    payload = build_payload(
        params=params,
        exhaustive_op_length=int(args.exhaustive_op_length),
        max_scenarios=int(args.max_scenarios),
        checkpoint_every=int(args.checkpoint_every),
        checkpoint_dir=str(args.checkpoint_dir).strip() or None,
    )
    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {_to_repo_path(OUT_JSON)}")
        print(f"Wrote {_to_repo_path(OUT_MD)}")
        return
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        "triplet_decay_exact_simulation_v1: "
        f"scenario_count={payload['summary']['scenario_count']}, "
        f"decay_hit_count={payload['summary']['decay_hit_count']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

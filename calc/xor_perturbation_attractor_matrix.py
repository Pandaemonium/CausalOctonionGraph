"""
calc/xor_perturbation_attractor_matrix.py

Perturbation-to-attractor transition matrix over canonical XOR motifs.

Workflow:
1) Start from canonical motif seeds (vector and spinor registry).
2) Apply one deterministic perturbation (left/right basis hit, e1..e7).
3) Evolve with a fixed deterministic policy (vacuum-pass e7 left).
4) Detect the resulting cycle attractor and map to known baseline attractors.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from calc.xor_furey_ideals import (
    StateGI,
    ideal_sd_basis_doubled,
    ideal_su_basis_doubled,
    oct_mul_xor,
    state_basis,
)
from calc.xor_vector_spinor_phase_cycles import vector_motif_state


def apply_basis_hit(state: StateGI, op_idx: int, hand: str) -> StateGI:
    if not (1 <= op_idx <= 7):
        raise ValueError(f"op_idx must be in [1,7], got {op_idx}")
    op = state_basis(op_idx, (1, 0))
    if hand == "left":
        return oct_mul_xor(op, state)
    if hand == "right":
        return oct_mul_xor(state, op)
    raise ValueError(f"hand must be 'left' or 'right', got {hand}")


def _step_vacuum_left(state: StateGI) -> StateGI:
    return apply_basis_hit(state, 7, "left")


def _flatten_state(state: StateGI) -> tuple[int, ...]:
    flat: list[int] = []
    for re, im in state:
        flat.append(re)
        flat.append(im)
    return tuple(flat)


def detect_cycle(
    initial: StateGI,
    step_fn: Callable[[StateGI], StateGI],
    max_steps: int = 128,
) -> dict[str, Any]:
    seen: dict[StateGI, int] = {}
    history: list[StateGI] = []
    cur = initial

    for step in range(max_steps + 1):
        if cur in seen:
            start = seen[cur]
            period = step - start
            cycle_states = history[start:step]
            return {
                "cycle_found": True,
                "cycle_start": start,
                "period": period,
                "steps_to_repeat": step,
                "cycle_states": cycle_states,
            }
        seen[cur] = step
        history.append(cur)
        cur = step_fn(cur)

    return {
        "cycle_found": False,
        "cycle_start": None,
        "period": None,
        "steps_to_repeat": None,
        "cycle_states": [],
    }


def canonical_cycle_key(cycle_states: list[StateGI]) -> str:
    if not cycle_states:
        return "no_cycle"

    seq = [_flatten_state(s) for s in cycle_states]
    rots: list[tuple[int, ...]] = []
    n = len(seq)
    for r in range(n):
        rot = seq[r:] + seq[:r]
        flat: list[int] = []
        for st in rot:
            flat.extend(st)
        rots.append(tuple(flat))
    best = min(rots)
    payload = ",".join(str(x) for x in best)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _canonical_seed_states() -> dict[str, StateGI]:
    out: dict[str, StateGI] = {}

    # Vector line motifs in canonical orientation.
    vector_triads = [
        (1, 2, 3),
        (1, 4, 5),
        (1, 7, 6),
        (2, 4, 6),
        (2, 5, 7),
        (3, 4, 7),
        (3, 6, 5),
    ]
    for idx, triad in enumerate(vector_triads, start=1):
        out[f"vector_fano_line_l{idx}"] = vector_motif_state(triad, coeff=1)

    out["vector_electron_favored"] = vector_motif_state((1, 2, 3), coeff=1)
    out["vector_proton_proto_t124"] = vector_motif_state((1, 2, 4), coeff=1)

    # Spinor motifs from Furey ideal scaffolds.
    out.update(ideal_su_basis_doubled())
    out.update(ideal_sd_basis_doubled())

    # Stable aliases.
    out["left_spinor_electron_ideal"] = out["su_triple_electron"]
    out["right_spinor_electron_ideal"] = out["sd_triple_dual_electron"]
    return out


def _baseline_attractor_index(
    seeds: dict[str, StateGI],
    max_steps: int,
) -> tuple[dict[str, str], dict[str, list[str]], dict[str, dict[str, Any]]]:
    """
    Returns:
    1) motif_id -> baseline_key
    2) baseline_key -> motif_ids that share this attractor
    3) baseline_key -> baseline metadata
    """
    motif_to_key: dict[str, str] = {}
    key_to_ids: dict[str, list[str]] = {}
    key_meta: dict[str, dict[str, Any]] = {}

    for motif_id in sorted(seeds):
        cyc = detect_cycle(seeds[motif_id], _step_vacuum_left, max_steps=max_steps)
        key = canonical_cycle_key(cyc["cycle_states"])
        motif_to_key[motif_id] = key
        key_to_ids.setdefault(key, []).append(motif_id)
        if key not in key_meta:
            key_meta[key] = {
                "period": cyc["period"],
                "cycle_state_count": len(cyc["cycle_states"]),
            }
    return motif_to_key, key_to_ids, key_meta


def _perturbations() -> list[tuple[str, int, str]]:
    out: list[tuple[str, int, str]] = []
    for hand in ("left", "right"):
        for op_idx in range(1, 8):
            out.append((f"{hand}_hit_e{op_idx}", op_idx, hand))
    return out


def build_xor_perturbation_attractor_dataset(max_steps: int = 128) -> dict[str, Any]:
    seeds = _canonical_seed_states()
    motif_to_key, key_to_ids, key_meta = _baseline_attractor_index(seeds, max_steps=max_steps)
    key_to_rep = {k: sorted(v)[0] for k, v in key_to_ids.items()}

    transitions: list[dict[str, Any]] = []
    matrix: dict[str, dict[str, int]] = {}

    for source_id, source_state in sorted(seeds.items()):
        source_key = motif_to_key[source_id]
        source_rep = key_to_rep[source_key]
        matrix[source_id] = {}
        for pert_id, op_idx, hand in _perturbations():
            perturbed = apply_basis_hit(source_state, op_idx, hand)
            cyc = detect_cycle(perturbed, _step_vacuum_left, max_steps=max_steps)
            key = canonical_cycle_key(cyc["cycle_states"])
            if key in key_to_rep:
                attractor_id = key_to_rep[key]
                attractor_class = "known"
            else:
                attractor_id = f"novel::{key[:12]}"
                attractor_class = "novel"

            matrix[source_id][attractor_id] = matrix[source_id].get(attractor_id, 0) + 1
            transitions.append(
                {
                    "source_motif_id": source_id,
                    "source_attractor_rep_id": source_rep,
                    "perturbation_id": pert_id,
                    "op_idx": op_idx,
                    "hand": hand,
                    "attractor_rep_id": attractor_id,
                    "attractor_class": attractor_class,
                    "period": cyc["period"],
                    "cycle_found": cyc["cycle_found"],
                    "cycle_state_count": len(cyc["cycle_states"]),
                }
            )

    retention_rows = []
    for source_id in sorted(seeds):
        source_rep = key_to_rep[motif_to_key[source_id]]
        total = sum(matrix[source_id].values())
        retained = matrix[source_id].get(source_rep, 0)
        retention_rows.append(
            {
                "source_motif_id": source_id,
                "source_attractor_rep_id": source_rep,
                "retained_count": retained,
                "total_perturbations": total,
                "retention_fraction": (retained / total) if total else 0.0,
            }
        )

    known_attractor_count = len(key_to_rep)
    novel_hits = sum(1 for t in transitions if t["attractor_class"] == "novel")

    csv_rows = [
        {
            "source_motif_id": t["source_motif_id"],
            "perturbation_id": t["perturbation_id"],
            "attractor_rep_id": t["attractor_rep_id"],
            "attractor_class": t["attractor_class"],
            "period": t["period"],
            "cycle_found": t["cycle_found"],
        }
        for t in transitions
    ]

    return {
        "schema_version": "xor_perturbation_attractor_matrix_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "policy": {
            "perturbations": [p[0] for p in _perturbations()],
            "evolution_policy": "vacuum_pass_e7_left",
            "max_steps": max_steps,
        },
        "baseline": {
            "seed_count": len(seeds),
            "known_attractor_count": known_attractor_count,
            "attractor_representatives": key_to_rep,
            "attractor_meta": key_meta,
        },
        "summary": {
            "transition_count": len(transitions),
            "novel_attractor_hits": novel_hits,
            "known_attractor_hits": len(transitions) - novel_hits,
        },
        "matrix": matrix,
        "retention": retention_rows,
        "transitions": transitions,
        "csv_rows": csv_rows,
    }


def write_xor_perturbation_attractor_artifacts(
    dataset: dict[str, Any],
    json_paths: list[Path] | None = None,
    csv_paths: list[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_perturbation_attractor_matrix.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_perturbation_attractor_matrix.csv")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "source_motif_id",
        "perturbation_id",
        "attractor_rep_id",
        "attractor_class",
        "period",
        "cycle_found",
    ]
    for path in csv_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in dataset["csv_rows"]:
                writer.writerow(row)


def main() -> int:
    dataset = build_xor_perturbation_attractor_dataset(max_steps=128)
    write_xor_perturbation_attractor_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_perturbation_attractor_matrix.json"),
            Path("website/data/xor_perturbation_attractor_matrix.json"),
        ],
        csv_paths=[
            Path("calc/xor_perturbation_attractor_matrix.csv"),
            Path("website/data/xor_perturbation_attractor_matrix.csv"),
        ],
    )
    print("Wrote calc/xor_perturbation_attractor_matrix.json")
    print("Wrote calc/xor_perturbation_attractor_matrix.csv")
    print("Wrote website/data/xor_perturbation_attractor_matrix.json")
    print("Wrote website/data/xor_perturbation_attractor_matrix.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


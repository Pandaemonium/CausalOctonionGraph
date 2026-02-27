"""
calc/xor_motif_registry.py

Canonical motif registry for XOR simulations.

Purpose:
1) Provide one source-of-truth registry for vector and spinor motif seeds.
2) Attach deterministic metadata (support, charge proxy, cycle invariants).
3) Emit JSON/CSV artifacts for downstream simulations and website viewers.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from calc.conftest import FANO_CYCLES
from calc.xor_charge_sign_interaction_matrix import u1_charge
from calc.xor_furey_ideals import (
    StateGI,
    furey_dual_electron_doubled,
    furey_electron_doubled,
    ideal_sd_basis_doubled,
    ideal_su_basis_doubled,
    nonzero_support,
    state_sparse,
)
from calc.xor_vector_spinor_phase_cycles import run_cycle_trace, vector_motif_state


def one_index_to_bits(idx: int) -> str:
    if not (1 <= idx <= 7):
        raise ValueError(f"idx must be in [1,7], got {idx}")
    return format(idx, "03b")


def _support_bits_from_state(state: StateGI) -> list[str]:
    return [one_index_to_bits(i) for i in nonzero_support(state) if i != 0]


def _periods_under_e7(state: StateGI, max_steps: int = 64) -> tuple[int | None, int | None]:
    left = run_cycle_trace(state, op_cycle=[7], hand="left", max_steps=max_steps)
    right = run_cycle_trace(state, op_cycle=[7], hand="right", max_steps=max_steps)
    return left["period"], right["period"]


def _registry_hash(motifs: list[dict[str, Any]]) -> str:
    lines = []
    for m in motifs:
        lines.append(
            json.dumps(
                {
                    "motif_id": m["motif_id"],
                    "representation": m["representation"],
                    "support": m["support"],
                    "u1_charge_proxy": m["u1_charge_proxy"],
                    "period_left_e7": m["period_left_e7"],
                    "period_right_e7": m["period_right_e7"],
                },
                sort_keys=True,
            )
        )
    payload = "\n".join(lines)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _build_vector_registry_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for idx, cyc in enumerate(FANO_CYCLES, start=1):
        triad = (cyc[0] + 1, cyc[1] + 1, cyc[2] + 1)
        state = vector_motif_state(triad, coeff=1)
        p_left, p_right = _periods_under_e7(state)
        rows.append(
            {
                "motif_id": f"vector_fano_line_l{idx}",
                "representation": "vector",
                "family": "fano_line",
                "construction": f"vector_motif_state({triad}, coeff=1)",
                "source_module": "calc/xor_vector_spinor_phase_cycles.py",
                "support": nonzero_support(state),
                "support_bits": _support_bits_from_state(state),
                "support_size": len(nonzero_support(state)),
                "u1_charge_proxy": u1_charge(state),
                "period_left_e7": p_left,
                "period_right_e7": p_right,
                "stable_period4": p_left == 4 and p_right == 4,
                "state_sparse": state_sparse(state),
                "tags": ["vector", "fano_line", "stable_candidate"],
            }
        )

    # Named aliases used in task prompts/reports.
    aliases: list[tuple[str, tuple[int, int, int], list[str]]] = [
        ("vector_electron_favored", (1, 2, 3), ["vector", "electron_scaffold"]),
        ("vector_proton_proto_t124", (1, 2, 4), ["vector", "proton_proto_scaffold"]),
    ]
    for motif_id, triad, tags in aliases:
        state = vector_motif_state(triad, coeff=1)
        p_left, p_right = _periods_under_e7(state)
        rows.append(
            {
                "motif_id": motif_id,
                "representation": "vector",
                "family": "named_alias",
                "construction": f"vector_motif_state({triad}, coeff=1)",
                "source_module": "calc/xor_vector_spinor_phase_cycles.py",
                "support": nonzero_support(state),
                "support_bits": _support_bits_from_state(state),
                "support_size": len(nonzero_support(state)),
                "u1_charge_proxy": u1_charge(state),
                "period_left_e7": p_left,
                "period_right_e7": p_right,
                "stable_period4": p_left == 4 and p_right == 4,
                "state_sparse": state_sparse(state),
                "tags": tags,
            }
        )

    return rows


def _build_spinor_registry_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    su = ideal_su_basis_doubled()
    sd = ideal_sd_basis_doubled()

    motif_sets = [("Su", su), ("Sd", sd)]
    for family_name, motifs in motif_sets:
        for motif_id, state in motifs.items():
            p_left, p_right = _periods_under_e7(state)
            rows.append(
                {
                    "motif_id": motif_id,
                    "representation": "spinor",
                    "family": family_name,
                    "construction": f"{family_name} ideal basis element",
                    "source_module": "calc/xor_furey_ideals.py",
                    "support": nonzero_support(state),
                    "support_bits": _support_bits_from_state(state),
                    "support_size": len(nonzero_support(state)),
                    "u1_charge_proxy": u1_charge(state),
                    "period_left_e7": p_left,
                    "period_right_e7": p_right,
                    "stable_period4": p_left == 4 and p_right == 4,
                    "state_sparse": state_sparse(state),
                    "tags": ["spinor", "furey_ideal", family_name.lower()],
                }
            )

    # Explicit canonical aliases (same states, stable IDs for routing/workflows).
    alias_rows = [
        ("left_spinor_electron_ideal", furey_electron_doubled(), "Su"),
        ("right_spinor_electron_ideal", furey_dual_electron_doubled(), "Sd"),
    ]
    for motif_id, state, fam in alias_rows:
        p_left, p_right = _periods_under_e7(state)
        rows.append(
            {
                "motif_id": motif_id,
                "representation": "spinor",
                "family": "named_alias",
                "construction": f"{fam} electron ideal alias",
                "source_module": "calc/xor_furey_ideals.py",
                "support": nonzero_support(state),
                "support_bits": _support_bits_from_state(state),
                "support_size": len(nonzero_support(state)),
                "u1_charge_proxy": u1_charge(state),
                "period_left_e7": p_left,
                "period_right_e7": p_right,
                "stable_period4": p_left == 4 and p_right == 4,
                "state_sparse": state_sparse(state),
                "tags": ["spinor", "electron_alias", fam.lower()],
            }
        )

    return rows


def build_xor_motif_registry_dataset() -> dict[str, Any]:
    motifs = _build_vector_registry_rows() + _build_spinor_registry_rows()
    motifs = sorted(motifs, key=lambda m: m["motif_id"])

    representation_counts: dict[str, int] = {}
    for m in motifs:
        representation_counts[m["representation"]] = (
            representation_counts.get(m["representation"], 0) + 1
        )

    stable_count = sum(1 for m in motifs if m["stable_period4"])
    registry_sha256 = _registry_hash(motifs)

    csv_rows = [
        {
            "motif_id": m["motif_id"],
            "representation": m["representation"],
            "family": m["family"],
            "support": str(m["support"]),
            "support_bits": str(m["support_bits"]),
            "u1_charge_proxy": m["u1_charge_proxy"],
            "period_left_e7": m["period_left_e7"],
            "period_right_e7": m["period_right_e7"],
            "stable_period4": m["stable_period4"],
        }
        for m in motifs
    ]

    return {
        "schema_version": "xor_motif_registry_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "registry_sha256": registry_sha256,
        "motif_count": len(motifs),
        "stable_period4_count": stable_count,
        "representation_counts": representation_counts,
        "motifs": motifs,
        "csv_rows": csv_rows,
        "notes": [
            "Canonical registry for deterministic motif seeding in XOR simulations.",
            "u1_charge_proxy is an internal model observable (not direct SI calibration).",
        ],
    }


def write_xor_motif_registry_artifacts(
    dataset: dict[str, Any],
    json_paths: list[Path] | None = None,
    csv_paths: list[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_motif_registry.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_motif_registry.csv")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "motif_id",
        "representation",
        "family",
        "support",
        "support_bits",
        "u1_charge_proxy",
        "period_left_e7",
        "period_right_e7",
        "stable_period4",
    ]
    for path in csv_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in dataset["csv_rows"]:
                writer.writerow(row)


def main() -> int:
    dataset = build_xor_motif_registry_dataset()
    write_xor_motif_registry_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_motif_registry.json"),
            Path("website/data/xor_motif_registry.json"),
        ],
        csv_paths=[
            Path("calc/xor_motif_registry.csv"),
            Path("website/data/xor_motif_registry.csv"),
        ],
    )
    print("Wrote calc/xor_motif_registry.json")
    print("Wrote calc/xor_motif_registry.csv")
    print("Wrote website/data/xor_motif_registry.json")
    print("Wrote website/data/xor_motif_registry.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


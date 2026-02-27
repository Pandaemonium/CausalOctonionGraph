"""
calc/xor_furey_ideals.py

Furey minimal left-ideal motifs implemented in XOR notation.

Conventions:
  - Basis channels are e0..e7 (index 0..7).
  - Distinct imaginary multiplication channel uses XOR index + Fano sign
    from calc.xor_octonion_gate.mul_basis_fast.
  - Coefficients are Gaussian integers (re, im) in Z[i].
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from calc.xor_octonion_gate import mul_basis_fast

GI = tuple[int, int]  # (re, im)
StateGI = tuple[GI, GI, GI, GI, GI, GI, GI, GI]


def gi_zero() -> GI:
    return (0, 0)


def gi_add(a: GI, b: GI) -> GI:
    return (a[0] + b[0], a[1] + b[1])


def gi_neg(a: GI) -> GI:
    return (-a[0], -a[1])


def gi_mul(a: GI, b: GI) -> GI:
    ar, ai = a
    br, bi = b
    return (ar * br - ai * bi, ar * bi + ai * br)


def gi_scale(a: GI, n: int) -> GI:
    return (n * a[0], n * a[1])


def gi_is_zero(a: GI) -> bool:
    return a[0] == 0 and a[1] == 0


def state_zero() -> StateGI:
    return (gi_zero(), gi_zero(), gi_zero(), gi_zero(), gi_zero(), gi_zero(), gi_zero(), gi_zero())


def state_basis(idx: int, coeff: GI = (1, 0)) -> StateGI:
    if not (0 <= idx <= 7):
        raise ValueError(f"idx must be in [0,7], got {idx}")
    out = [gi_zero() for _ in range(8)]
    out[idx] = coeff
    return tuple(out)  # type: ignore[return-value]


def state_add(a: StateGI, b: StateGI) -> StateGI:
    return tuple(gi_add(a[i], b[i]) for i in range(8))  # type: ignore[return-value]


def state_eq(a: StateGI, b: StateGI) -> bool:
    return a == b


def oct_mul_xor(lhs: StateGI, rhs: StateGI) -> StateGI:
    """
    Full bilinear octonion multiplication in XOR notation over Z[i] coefficients.
    """
    out = [gi_zero() for _ in range(8)]
    for i in range(8):
        ci = lhs[i]
        if gi_is_zero(ci):
            continue
        for j in range(8):
            cj = rhs[j]
            if gi_is_zero(cj):
                continue
            core = mul_basis_fast(i, j)
            c = gi_mul(ci, cj)
            if core.sign == -1:
                c = gi_neg(c)
            out[core.out_idx] = gi_add(out[core.out_idx], c)
    return tuple(out)  # type: ignore[return-value]


def nonzero_support(state: StateGI) -> list[int]:
    return [i for i, c in enumerate(state) if not gi_is_zero(c)]


def state_sparse(state: StateGI) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for i, c in enumerate(state):
        if not gi_is_zero(c):
            out[f"e{i}"] = {"re": c[0], "im": c[1]}
    return out


def one_index_to_bits(idx: int) -> str:
    """
    e1..e7 -> 3-bit XOR channel notation.
    """
    if not (1 <= idx <= 7):
        raise ValueError(f"idx must be in [1,7], got {idx}")
    return format(idx, "03b")


# Witt pairs in one-indexed basis labels, matching rfc/CONVENTIONS.md.
WITT_PAIRS_ONE_INDEXED: tuple[tuple[int, int], tuple[int, int], tuple[int, int]] = (
    (6, 1),
    (2, 5),
    (3, 4),
)


def witt_raise_doubled(j: int) -> StateGI:
    """
    2*alpha_j^dagger = -e_a + i e_b.
    j is 1-based in {1,2,3}.
    """
    if j not in (1, 2, 3):
        raise ValueError("j must be in {1,2,3}")
    a, b = WITT_PAIRS_ONE_INDEXED[j - 1]
    return state_add(state_basis(a, (-1, 0)), state_basis(b, (0, 1)))


def witt_lower_doubled(j: int) -> StateGI:
    """
    2*alpha_j = e_a + i e_b.
    """
    if j not in (1, 2, 3):
        raise ValueError("j must be in {1,2,3}")
    a, b = WITT_PAIRS_ONE_INDEXED[j - 1]
    return state_add(state_basis(a, (1, 0)), state_basis(b, (0, 1)))


def vacuum_doubled() -> StateGI:
    """
    2*omega = e0 + i e7.
    """
    return state_add(state_basis(0, (1, 0)), state_basis(7, (0, 1)))


def vacuum_conj_doubled() -> StateGI:
    """
    2*omega^dagger = e0 - i e7.
    """
    return state_add(state_basis(0, (1, 0)), state_basis(7, (0, -1)))


def furey_electron_doubled() -> StateGI:
    """
    (2a1^dag)(2a2^dag)(2a3^dag)(2omega), right-associated.
    """
    s = oct_mul_xor(witt_raise_doubled(3), vacuum_doubled())
    s = oct_mul_xor(witt_raise_doubled(2), s)
    s = oct_mul_xor(witt_raise_doubled(1), s)
    return s


def furey_dual_electron_doubled() -> StateGI:
    """
    (2a1)(2a2)(2a3)(2omega^dagger), right-associated.
    """
    s = oct_mul_xor(witt_lower_doubled(3), vacuum_conj_doubled())
    s = oct_mul_xor(witt_lower_doubled(2), s)
    s = oct_mul_xor(witt_lower_doubled(1), s)
    return s


def ideal_su_basis_doubled() -> dict[str, StateGI]:
    """
    Basis-like motifs of S^u minimal left ideal generated from omega.
    """
    w = vacuum_doubled()
    a1 = witt_raise_doubled(1)
    a2 = witt_raise_doubled(2)
    a3 = witt_raise_doubled(3)
    return {
        "su_vacuum_omega": w,
        "su_single_1": oct_mul_xor(a1, w),
        "su_single_2": oct_mul_xor(a2, w),
        "su_single_3": oct_mul_xor(a3, w),
        "su_double_12": oct_mul_xor(a1, oct_mul_xor(a2, w)),
        "su_double_13": oct_mul_xor(a1, oct_mul_xor(a3, w)),
        "su_double_23": oct_mul_xor(a2, oct_mul_xor(a3, w)),
        "su_triple_electron": furey_electron_doubled(),
    }


def ideal_sd_basis_doubled() -> dict[str, StateGI]:
    """
    Basis-like motifs of dual minimal left ideal from omega^dagger.
    """
    wd = vacuum_conj_doubled()
    l1 = witt_lower_doubled(1)
    l2 = witt_lower_doubled(2)
    l3 = witt_lower_doubled(3)
    return {
        "sd_vacuum_omega_dag": wd,
        "sd_single_1": oct_mul_xor(l1, wd),
        "sd_single_2": oct_mul_xor(l2, wd),
        "sd_single_3": oct_mul_xor(l3, wd),
        "sd_double_12": oct_mul_xor(l1, oct_mul_xor(l2, wd)),
        "sd_double_13": oct_mul_xor(l1, oct_mul_xor(l3, wd)),
        "sd_double_23": oct_mul_xor(l2, oct_mul_xor(l3, wd)),
        "sd_triple_dual_electron": furey_dual_electron_doubled(),
    }


def e7_left(state: StateGI) -> StateGI:
    return oct_mul_xor(state_basis(7, (1, 0)), state)


def e7_right(state: StateGI) -> StateGI:
    return oct_mul_xor(state, state_basis(7, (1, 0)))


def detect_period(
    initial: StateGI,
    step_fn,
    max_steps: int = 64,
) -> int | None:
    cur = initial
    for n in range(1, max_steps + 1):
        cur = step_fn(cur)
        if state_eq(cur, initial):
            return n
    return None


@dataclass(frozen=True)
class FureyMotifRow:
    motif_id: str
    family: str
    support: tuple[int, ...]
    support_bits: tuple[str, ...]
    period_left_e7: int | None
    period_right_e7: int | None
    stable_period4: bool


def build_furey_ideal_cycle_dataset(max_steps: int = 64) -> dict[str, Any]:
    motifs = {}
    motifs.update(ideal_su_basis_doubled())
    motifs.update(ideal_sd_basis_doubled())

    rows: list[FureyMotifRow] = []
    payload: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []

    for motif_id, state in motifs.items():
        family = "Su" if motif_id.startswith("su_") else "Sd"
        support = tuple(nonzero_support(state))
        support_bits = tuple(one_index_to_bits(i) for i in support if i != 0)
        p_left = detect_period(state, e7_left, max_steps=max_steps)
        p_right = detect_period(state, e7_right, max_steps=max_steps)
        stable = p_left == 4 and p_right == 4

        rows.append(
            FureyMotifRow(
                motif_id=motif_id,
                family=family,
                support=support,
                support_bits=support_bits,
                period_left_e7=p_left,
                period_right_e7=p_right,
                stable_period4=stable,
            )
        )

        payload.append(
            {
                "motif_id": motif_id,
                "family": family,
                "support": list(support),
                "support_bits": list(support_bits),
                "state_sparse": state_sparse(state),
                "period_left_e7": p_left,
                "period_right_e7": p_right,
                "stable_period4": stable,
            }
        )

        csv_rows.append(
            {
                "motif_id": motif_id,
                "family": family,
                "support": str(list(support)),
                "support_bits": str(list(support_bits)),
                "period_left_e7": p_left,
                "period_right_e7": p_right,
                "stable_period4": stable,
            }
        )

    stable_count = sum(1 for r in rows if r.stable_period4)

    return {
        "schema_version": "xor_furey_ideal_cycles_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "notation": {
            "basis": "e0..e7",
            "imag_channels_bits": {str(i): one_index_to_bits(i) for i in range(1, 8)},
            "mul_rule": "e_i * e_j uses XOR index channel for distinct imaginaries, with Fano sign channel",
        },
        "witt_pairs_one_indexed": [list(p) for p in WITT_PAIRS_ONE_INDEXED],
        "motif_count": len(payload),
        "stable_period4_count": stable_count,
        "motifs": payload,
        "csv_rows": csv_rows,
    }


def write_furey_ideal_cycle_artifacts(
    dataset: dict[str, Any],
    json_paths: list[Path] | None = None,
    csv_paths: list[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_furey_ideal_cycles.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_furey_ideal_cycles.csv")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "motif_id",
        "family",
        "support",
        "support_bits",
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
    dataset = build_furey_ideal_cycle_dataset(max_steps=64)
    write_furey_ideal_cycle_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_furey_ideal_cycles.json"),
            Path("website/data/xor_furey_ideal_cycles.json"),
        ],
        csv_paths=[
            Path("calc/xor_furey_ideal_cycles.csv"),
            Path("website/data/xor_furey_ideal_cycles.csv"),
        ],
    )
    print("Wrote calc/xor_furey_ideal_cycles.json")
    print("Wrote calc/xor_furey_ideal_cycles.csv")
    print("Wrote website/data/xor_furey_ideal_cycles.json")
    print("Wrote website/data/xor_furey_ideal_cycles.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


"""
calc/xor_stable_motif_scan.py

Stable-motif scan utilities on top of the XOR octonion gate.

The core idea is support-closure under deterministic handed internal updates:
  - a motif is seeded as a sparse integer state over basis units e1..e7
  - one update round applies motif operators with fixed handed schedule
  - a motif is "support-stable" if evolved support never leaves motif U {e0}

This module is intentionally structural. It does not claim physical calibration.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable

from calc.conftest import FANO_CYCLES
from calc.xor_octonion_gate import Handedness, mul_basis_fast

StateVec = tuple[int, int, int, int, int, int, int, int]


@dataclass(frozen=True)
class MotifScanRow:
    triad: tuple[int, int, int]   # 1-indexed imaginary basis labels
    is_fano_line: bool
    support_stable: bool
    period: int | None


def zero_state() -> StateVec:
    return (0, 0, 0, 0, 0, 0, 0, 0)


def triad_seed_state(triad: tuple[int, int, int], coeff: int = 1) -> StateVec:
    """
    Seed state with equal weight on a 1-indexed triad over e1..e7.
    """
    if coeff == 0:
        raise ValueError("coeff must be non-zero")
    if len(set(triad)) != 3:
        raise ValueError(f"triad must contain 3 distinct labels, got {triad}")
    if any(not (1 <= x <= 7) for x in triad):
        raise ValueError(f"triad entries must be in [1,7], got {triad}")

    out = [0] * 8
    for x in triad:
        out[x] = coeff
    return tuple(out)  # type: ignore[return-value]


def support_indices(state: StateVec) -> set[int]:
    """
    Return basis indices with non-zero coefficient.
    """
    return {i for i, c in enumerate(state) if c != 0}


def apply_basis_handed(state: StateVec, op_idx: int, hand: Handedness) -> StateVec:
    """
    Apply basis operator e_op to a sparse integer state with handedness.
    """
    if not (1 <= op_idx <= 7):
        raise ValueError(f"op_idx must be in [1,7], got {op_idx}")

    out = [0] * 8
    for idx, coeff in enumerate(state):
        if coeff == 0:
            continue
        core = (
            mul_basis_fast(op_idx, idx)
            if hand is Handedness.LEFT
            else mul_basis_fast(idx, op_idx)
        )
        out[core.out_idx] += coeff * core.sign
    return tuple(out)  # type: ignore[return-value]


def motif_schedule(
    triad: tuple[int, int, int],
    mode: str = "alternating",
) -> tuple[tuple[int, Handedness], tuple[int, Handedness], tuple[int, Handedness]]:
    """
    Build one deterministic internal-update round for a triad.

    mode:
      - "alternating": LEFT, RIGHT, LEFT in triad order
      - "left_only":   LEFT for all
      - "right_only":  RIGHT for all
    """
    if mode not in {"alternating", "left_only", "right_only"}:
        raise ValueError(f"Unsupported mode: {mode}")

    a, b, c = triad
    if mode == "alternating":
        return (
            (a, Handedness.LEFT),
            (b, Handedness.RIGHT),
            (c, Handedness.LEFT),
        )
    if mode == "left_only":
        return (
            (a, Handedness.LEFT),
            (b, Handedness.LEFT),
            (c, Handedness.LEFT),
        )
    return (
        (a, Handedness.RIGHT),
        (b, Handedness.RIGHT),
        (c, Handedness.RIGHT),
    )


def run_round(state: StateVec, schedule: Iterable[tuple[int, Handedness]]) -> StateVec:
    cur = state
    for op_idx, hand in schedule:
        cur = apply_basis_handed(cur, op_idx, hand)
    return cur


def detect_period(
    initial: StateVec,
    schedule: Iterable[tuple[int, Handedness]],
    max_rounds: int = 64,
) -> int | None:
    """
    Return the smallest positive round period that returns to `initial`,
    or None if not detected within `max_rounds`.
    """
    cur = initial
    for n in range(1, max_rounds + 1):
        cur = run_round(cur, schedule)
        if cur == initial:
            return n
    return None


def support_stable_under_schedule(
    initial: StateVec,
    motif_support: set[int],
    schedule: Iterable[tuple[int, Handedness]],
    rounds: int = 16,
) -> bool:
    """
    Support-closure criterion:
      support(state_t) subset motif_support U {e0} for all t in scan horizon.
    """
    allowed = set(motif_support) | {0}
    cur = initial
    for _ in range(rounds):
        cur = run_round(cur, schedule)
        if not support_indices(cur).issubset(allowed):
            return False
    return True


def fano_lines_one_indexed() -> set[tuple[int, int, int]]:
    """
    Canonical one-indexed Fano lines (sorted tuple representation).
    """
    return {tuple(sorted((a + 1, b + 1, c + 1))) for (a, b, c) in FANO_CYCLES}


def scan_triad_stability(
    schedule_mode: str = "alternating",
    rounds: int = 16,
    period_horizon: int = 64,
) -> list[MotifScanRow]:
    """
    Scan all 35 triads of imaginary basis labels and report support stability.
    """
    lines = fano_lines_one_indexed()
    rows: list[MotifScanRow] = []

    for triad in combinations(range(1, 8), 3):
        triad_key = tuple(sorted(triad))
        schedule = motif_schedule(triad_key, mode=schedule_mode)
        seed = triad_seed_state(triad_key)
        stable = support_stable_under_schedule(
            seed,
            motif_support=set(triad_key),
            schedule=schedule,
            rounds=rounds,
        )
        period = detect_period(seed, schedule, max_rounds=period_horizon)
        rows.append(
            MotifScanRow(
                triad=triad_key,
                is_fano_line=triad_key in lines,
                support_stable=stable,
                period=period,
            )
        )
    return rows


def stable_rows(rows: Iterable[MotifScanRow]) -> list[MotifScanRow]:
    return [r for r in rows if r.support_stable]


def stable_motif_report(schedule_mode: str = "alternating") -> dict[str, object]:
    """
    Build a compact summary for downstream scripts/docs.
    """
    rows = scan_triad_stability(schedule_mode=schedule_mode)
    stable = stable_rows(rows)
    lines = [r for r in stable if r.is_fano_line]
    nonlines = [r for r in stable if not r.is_fano_line]
    return {
        "schedule_mode": schedule_mode,
        "triad_count": len(rows),
        "stable_count": len(stable),
        "stable_fano_line_count": len(lines),
        "stable_nonline_count": len(nonlines),
        "stable_triads": [r.triad for r in stable],
    }


def stable_vacuum_orbit_report(
    hand: Handedness = Handedness.LEFT,
    period_horizon: int = 64,
) -> dict[tuple[int, int, int], int | None]:
    """
    For each support-stable triad under alternating internal schedule, measure the
    period under repeated vacuum-axis hits (operator e7).
    """
    rows = scan_triad_stability(schedule_mode="alternating")
    out: dict[tuple[int, int, int], int | None] = {}
    for row in stable_rows(rows):
        seed = triad_seed_state(row.triad)
        out[row.triad] = detect_period(
            seed,
            schedule=[(7, hand)],
            max_rounds=period_horizon,
        )
    return out


if __name__ == "__main__":
    for mode in ("alternating", "left_only", "right_only"):
        report = stable_motif_report(schedule_mode=mode)
        print(f"\n=== XOR Stable Motif Scan ({mode}) ===")
        print(f"triads:   {report['triad_count']}")
        print(f"stable:   {report['stable_count']}")
        print(f"lines:    {report['stable_fano_line_count']}")
        print(f"nonlines: {report['stable_nonline_count']}")
        print("stable triads:")
        for triad in report["stable_triads"]:
            print(f"  {triad}")

    print("\n=== Vacuum-Drive Periods on Stable Triads (e7 LEFT) ===")
    vac = stable_vacuum_orbit_report(hand=Handedness.LEFT)
    for triad, period in vac.items():
        print(f"  {triad}: period={period}")

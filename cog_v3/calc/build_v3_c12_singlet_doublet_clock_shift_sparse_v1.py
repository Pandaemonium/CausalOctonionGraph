"""Build compact singlet+doublet clock-shift table for Q240 x C12.

State space:
  S = C12 x Q240, |S| = 12 * 240 = 2880

For each ordered pair (A, B) with fixed C = identity, compute

    F_{A,B,C}(x) = A * (B * (C * x))

and test, for every non-identity clock (cyclic subgroup in S), whether F acts
as a pure rotation on that same clock.

This script writes a compact per-pair table (one row per (A,B)):
  A,B,C,check_type,preserved_clock_count,advanced_clock_count,advanced_hits

Where:
- check_type = "singlet" if B==identity else "doublet"
- advanced_hits lists only nonzero-shift preserved clocks as "clock_id:shift|..."

The compact format avoids an impractically large wide matrix for C12.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]

DEFAULT_OUT_TABLE = (
    ROOT / "cog_v3" / "sources" / "v3_c12_singlet_doublet_clock_shift_sparse_v1.csv.gz"
)
DEFAULT_OUT_CLOCK_META = ROOT / "cog_v3" / "sources" / "v3_c12_clock_meta_v1.csv"
DEFAULT_OUT_ELEM_META = ROOT / "cog_v3" / "sources" / "v3_c12_element_meta_v1.csv"

PHASE_COUNT = 12
SENTINEL = -128


@dataclass(frozen=True)
class Clock:
    clock_id: int
    period: int
    rep_id: int
    canonical_cycle: Tuple[int, ...]  # canonicalized to start at identity


def phase_label(p: int) -> str:
    if p == 0:
        return "1"
    return f"zeta12^{p}"


def s_identity_id() -> int:
    # phase=0, q=identity
    return int(k.IDENTITY_ID)


def s_label(sid: int, qn: int) -> str:
    p = int(sid) // qn
    q = int(sid) % qn
    base = k.elem_label(int(q))
    return base if p == 0 else f"{phase_label(p)}*({base})"


def build_qmul_table() -> np.ndarray:
    qn = int(k.ALPHABET_SIZE)
    qmul = np.empty((qn, qn), dtype=np.uint16)
    for a in range(qn):
        for b in range(qn):
            qmul[a, b] = np.uint16(int(k.multiply_ids(int(a), int(b))))
    return qmul


def build_mul_table(phase_count: int, qmul: np.ndarray) -> np.ndarray:
    qn = int(qmul.shape[0])
    s_size = int(phase_count * qn)

    sid = np.arange(s_size, dtype=np.int32)
    phase_of = sid // qn
    q_of = sid % qn

    mul = np.empty((s_size, s_size), dtype=np.uint16)
    for a in range(s_size):
        ap = int(phase_of[a])
        aq = int(q_of[a])
        cp = (ap + phase_of) % phase_count
        cq = qmul[aq, q_of]
        mul[a, :] = (cp * qn + cq).astype(np.uint16)
    return mul


def element_order(seed: int, mul: np.ndarray, identity: int, max_order: int = 1024) -> int:
    cur = int(seed)
    order = 1
    while cur != int(identity):
        cur = int(mul[cur, seed])
        order += 1
        if order > int(max_order):
            raise RuntimeError(f"Order search exceeded bound for seed={seed}, bound={max_order}")
    return int(order)


def power_cycle(seed: int, mul: np.ndarray, identity: int) -> Tuple[int, Tuple[int, ...]]:
    order = int(element_order(int(seed), mul, int(identity)))
    out = [int(identity)]
    cur = int(identity)
    for _ in range(1, order):
        cur = int(mul[cur, seed])
        out.append(cur)
    return int(order), tuple(int(x) for x in out)


def build_clocks(mul: np.ndarray, identity: int) -> List[Clock]:
    s_size = int(mul.shape[0])
    subgroup_to_period: Dict[frozenset[int], int] = {}
    subgroup_to_rep: Dict[frozenset[int], int] = {}
    subgroup_to_cycle: Dict[frozenset[int], Tuple[int, ...]] = {}

    for sid in range(s_size):
        order, cyc = power_cycle(int(sid), mul, int(identity))
        if order <= 1:
            continue
        H = frozenset(int(x) for x in cyc)
        if H not in subgroup_to_period:
            subgroup_to_period[H] = int(order)
            subgroup_to_rep[H] = int(min(H))
            subgroup_to_cycle[H] = tuple(int(x) for x in cyc)
        else:
            prev = subgroup_to_cycle[H]
            if tuple(cyc) < tuple(prev):
                subgroup_to_cycle[H] = tuple(int(x) for x in cyc)

    clocks_unsorted: List[Clock] = []
    for H, period in subgroup_to_period.items():
        clocks_unsorted.append(
            Clock(
                clock_id=-1,
                period=int(period),
                rep_id=int(subgroup_to_rep[H]),
                canonical_cycle=tuple(int(x) for x in subgroup_to_cycle[H]),
            )
        )

    clocks_unsorted.sort(key=lambda c: (c.period, c.rep_id, c.canonical_cycle))
    clocks: List[Clock] = []
    for idx, c in enumerate(clocks_unsorted):
        clocks.append(
            Clock(
                clock_id=int(idx),
                period=int(c.period),
                rep_id=int(c.rep_id),
                canonical_cycle=tuple(int(x) for x in c.canonical_cycle),
            )
        )
    return clocks


def build_clock_arrays(clocks: Sequence[Clock], s_size: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n_clocks = int(len(clocks))
    max_p = int(max(c.period for c in clocks))
    clock_elems = np.zeros((n_clocks, max_p), dtype=np.int32)
    mask = np.zeros((n_clocks, max_p), dtype=bool)
    lengths = np.zeros((n_clocks,), dtype=np.int32)
    pos = np.full((n_clocks, s_size), -1, dtype=np.int16)

    for c in clocks:
        cid = int(c.clock_id)
        p = int(c.period)
        cyc = c.canonical_cycle
        lengths[cid] = p
        clock_elems[cid, :p] = np.asarray(cyc, dtype=np.int32)
        mask[cid, :p] = True
        for i, sid in enumerate(cyc):
            pos[cid, int(sid)] = np.int16(i)

    return clock_elems, mask, lengths, pos


def write_meta(
    *,
    out_elem_meta: Path,
    out_clock_meta: Path,
    qn: int,
    phase_count: int,
    identity: int,
    clocks: Sequence[Clock],
) -> None:
    out_elem_meta.parent.mkdir(parents=True, exist_ok=True)

    s_size = int(phase_count * qn)
    with out_elem_meta.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["s_id", "phase_idx", "q240_id", "label", "is_identity"])
        for sid in range(s_size):
            w.writerow(
                [
                    int(sid),
                    int(sid // qn),
                    int(sid % qn),
                    s_label(int(sid), int(qn)),
                    int(sid == int(identity)),
                ]
            )

    with out_clock_meta.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["clock_id", "period", "rep_id", "canonical_cycle"])
        for c in clocks:
            cyc = "|".join(str(int(x)) for x in c.canonical_cycle)
            w.writerow([int(c.clock_id), int(c.period), int(c.rep_id), cyc])


def open_writer(path: Path, gzip_output: bool) -> Tuple[object, csv.writer]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if gzip_output:
        fh = gzip.open(path, "wt", newline="", encoding="utf-8")
    else:
        fh = path.open("w", newline="", encoding="utf-8")
    return fh, csv.writer(fh)


def main() -> None:
    p = argparse.ArgumentParser(description="Build compact C12 singlet+doublet clock-shift table.")
    p.add_argument("--phase-count", type=int, default=int(PHASE_COUNT), help="Phase count (default: 12).")
    p.add_argument("--out-table", type=str, default=str(DEFAULT_OUT_TABLE), help="Output table CSV(.gz).")
    p.add_argument("--out-clock-meta", type=str, default=str(DEFAULT_OUT_CLOCK_META), help="Clock metadata CSV.")
    p.add_argument("--out-elem-meta", type=str, default=str(DEFAULT_OUT_ELEM_META), help="Element metadata CSV.")
    p.add_argument("--plain-csv", action="store_true", help="Write plain CSV (not gzip).")
    p.add_argument("--limit-pairs", type=int, default=0, help="0 means full |S|*|S|.")
    p.add_argument("--progress-every", type=int, default=200000, help="Progress print cadence.")
    p.add_argument("--b-chunk", type=int, default=192, help="Chunk size on B axis.")
    args = p.parse_args()

    phase_count = int(args.phase_count)
    if phase_count <= 0:
        raise ValueError("phase-count must be >= 1")

    out_table = Path(args.out_table).resolve()
    out_clock_meta = Path(args.out_clock_meta).resolve()
    out_elem_meta = Path(args.out_elem_meta).resolve()
    gzip_output = not bool(args.plain_csv)

    t0 = time.time()
    qmul = build_qmul_table()
    qn = int(qmul.shape[0])
    mul = build_mul_table(phase_count=phase_count, qmul=qmul)
    s_size = int(mul.shape[0])
    identity = int(s_identity_id())
    clocks = build_clocks(mul, identity=identity)

    clock_elems, mask, lengths, pos = build_clock_arrays(clocks, s_size=s_size)
    n_clocks = int(len(clocks))

    write_meta(
        out_elem_meta=out_elem_meta,
        out_clock_meta=out_clock_meta,
        qn=qn,
        phase_count=phase_count,
        identity=identity,
        clocks=clocks,
    )

    headers = [
        "A",
        "B",
        "C",
        "check_type",
        "preserved_clock_count",
        "advanced_clock_count",
        "advanced_hits",
    ]
    fh, w = open_writer(out_table, gzip_output=gzip_output)

    pair_target = int(s_size * s_size)
    if int(args.limit_pairs) > 0:
        pair_target = int(min(pair_target, int(args.limit_pairs)))

    idx = np.arange(clock_elems.shape[1], dtype=np.int16)[None, :]
    cix = np.arange(n_clocks, dtype=np.int32)[None, :, None]
    mask3 = mask[None, :, :]
    idx3 = idx[None, :, :]
    len3 = lengths[None, :, None]

    C_id = int(identity)
    done = 0
    b_chunk = max(1, int(args.b_chunk))

    try:
        w.writerow(headers)

        for A in range(s_size):
            if done >= pair_target:
                break
            for b0 in range(0, s_size, b_chunk):
                if done >= pair_target:
                    break
                b1 = min(s_size, b0 + b_chunk)
                B_idx = np.arange(b0, b1, dtype=np.int32)

                # Y[j, x] = A * (B_j * x), since C is identity.
                Y = mul[A, mul[B_idx, :]]

                selected = Y[:, clock_elems]
                psel = pos[cix, selected]
                valid = np.all((~mask3) | (psel >= 0), axis=2)
                deltas = (psel - idx3) % len3
                same = np.all((~mask3) | (deltas == deltas[:, :, [0]]), axis=2)
                rot = valid & same
                shifts = np.full((b1 - b0, n_clocks), SENTINEL, dtype=np.int16)
                shifts[rot] = deltas[:, :, 0][rot].astype(np.int16)

                remaining = pair_target - done
                rows_here = min(remaining, b1 - b0)
                for j in range(rows_here):
                    B = int(B_idx[j])
                    row_shifts = shifts[j]
                    row_rot = row_shifts != SENTINEL
                    row_adv = row_rot & (row_shifts != 0)

                    adv_ids = np.flatnonzero(row_adv)
                    if adv_ids.size > 0:
                        adv_hits = "|".join(f"{int(cid)}:{int(row_shifts[cid])}" for cid in adv_ids.tolist())
                    else:
                        adv_hits = ""

                    row = [
                        int(A),
                        int(B),
                        int(C_id),
                        "singlet" if int(B) == int(identity) else "doublet",
                        int(np.count_nonzero(row_rot)),
                        int(adv_ids.size),
                        adv_hits,
                    ]
                    w.writerow(row)
                    done += 1

                if done % int(args.progress_every) == 0:
                    dt = max(1e-9, time.time() - t0)
                    rate = done / dt
                    eta = (pair_target - done) / max(1e-9, rate)
                    print(
                        f"rows={done}/{pair_target} "
                        f"rate={rate:,.1f} rows/s "
                        f"eta={eta/60.0:,.1f} min"
                    )

            if done >= pair_target:
                break
    finally:
        fh.close()

    dt = max(1e-9, time.time() - t0)
    print(f"Wrote table: {out_table}")
    print(f"Wrote clock metadata: {out_clock_meta}")
    print(f"Wrote element metadata: {out_elem_meta}")
    print(f"rows={done}, elapsed={dt:.1f}s, rate={done/dt:,.1f} rows/s")
    print(
        f"state_size={s_size}, phase_count={phase_count}, "
        f"non_identity_clocks={n_clocks}, identity_id={identity}"
    )


if __name__ == "__main__":
    main()


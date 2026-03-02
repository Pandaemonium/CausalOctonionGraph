"""Build a brute-force doublet->clock advancement table for S960.

For each ordered pair (A, B) in S960 (and fixed C = identity), compute the
induced map

    F_{A,B,C}(x) = A * (B * (C * x))

and report, for each non-identity clock (cyclic subgroup) in S960, whether
F acts as a pure rotation on that same clock. If yes, record shift k
(0..period-1). If not, record SENTINEL.

Outputs:
1) Dense CSV(.gz) with ~|S|^2 rows and one column per clock.
2) Clock metadata CSV.
3) S960 element metadata CSV (id->label mapping).
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
OUT_DENSE = ROOT / "cog_v3" / "sources" / "v3_doublet_clock_shift_dense_v1.csv.gz"
OUT_CLOCKS = ROOT / "cog_v3" / "sources" / "v3_doublet_clock_meta_v1.csv"
OUT_ELEMS = ROOT / "cog_v3" / "sources" / "v3_s960_element_meta_v1.csv"

PHASE_LABELS = ("1", "i", "-1", "-i")
SENTINEL = -128


@dataclass(frozen=True)
class Clock:
    clock_id: int
    period: int
    rep_id: int
    canonical_cycle: Tuple[int, ...]  # starts at identity


def s960_identity_id() -> int:
    # phase=0 ("1"), q=identity
    return int(k.IDENTITY_ID)


def s960_label(sid: int) -> str:
    qn = int(k.ALPHABET_SIZE)
    p = int(sid) // qn
    q = int(sid) % qn
    base = k.elem_label(int(q))
    return base if p == 0 else f"{PHASE_LABELS[p]}*({base})"


def build_s960_mul_table() -> np.ndarray:
    qn = int(k.ALPHABET_SIZE)
    s = 4 * qn
    table = np.empty((s, s), dtype=np.uint16)
    for a in range(s):
        ap = a // qn
        aq = a % qn
        for b in range(s):
            bp = b // qn
            bq = b % qn
            cp = (ap + bp) % 4
            cq = int(k.multiply_ids(int(aq), int(bq)))
            table[a, b] = np.uint16(cp * qn + cq)
    return table


def power_cycle(seed: int, mul: np.ndarray, identity: int) -> Tuple[int, Tuple[int, ...]]:
    cur = int(seed)
    elems: List[int] = [cur]
    while cur != int(identity):
        cur = int(mul[cur, seed])
        elems.append(cur)
        if len(elems) > 4096:
            raise RuntimeError(f"Order search exceeded bound for seed={seed}")
    # elems currently starts at seed and ends at identity
    # reorder to canonical power cycle starting identity.
    # regenerate as identity, seed, seed^2, ... seed^(n-1)
    order = len(elems)
    out = [int(identity)]
    cur2 = int(identity)
    for _ in range(1, order):
        cur2 = int(mul[cur2, seed])
        out.append(cur2)
    return int(order), tuple(int(x) for x in out)


def element_order(seed: int, mul: np.ndarray, identity: int) -> int:
    cur = int(seed)
    order = 1
    while cur != int(identity):
        cur = int(mul[cur, seed])
        order += 1
        if order > 4096:
            raise RuntimeError(f"Order search exceeded bound for seed={seed}")
    return int(order)


def build_clocks(mul: np.ndarray, identity: int) -> List[Clock]:
    s = int(mul.shape[0])
    subgroup_to_period: Dict[frozenset[int], int] = {}
    subgroup_to_rep: Dict[frozenset[int], int] = {}
    subgroup_to_cycle: Dict[frozenset[int], Tuple[int, ...]] = {}

    for sid in range(s):
        order = element_order(int(sid), mul, int(identity))
        if order <= 1:
            continue  # exclude identity clock from table columns
        # subgroup set from canonical cycle of this generator
        _, cyc = power_cycle(int(sid), mul, int(identity))
        H = frozenset(int(x) for x in cyc)
        if H not in subgroup_to_period:
            subgroup_to_period[H] = int(order)
            subgroup_to_rep[H] = int(min(H))
            subgroup_to_cycle[H] = tuple(int(x) for x in cyc)
        else:
            # choose deterministic canonical cycle orientation:
            # lexicographically smallest cycle tuple among generators.
            prev = subgroup_to_cycle[H]
            if tuple(cyc) < tuple(prev):
                subgroup_to_cycle[H] = tuple(int(x) for x in cyc)

    clocks_unsorted: List[Clock] = []
    for H, period in subgroup_to_period.items():
        cyc = subgroup_to_cycle[H]
        rep = subgroup_to_rep[H]
        clocks_unsorted.append(
            Clock(
                clock_id=-1,
                period=int(period),
                rep_id=int(rep),
                canonical_cycle=tuple(int(x) for x in cyc),
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
        lengths[cid] = p
        cyc = c.canonical_cycle
        clock_elems[cid, :p] = np.asarray(cyc, dtype=np.int32)
        mask[cid, :p] = True
        for i, sid in enumerate(cyc):
            pos[cid, int(sid)] = np.int16(i)
    return clock_elems, mask, lengths, pos


def write_meta(clocks: Sequence[Clock], elem_out: Path, clock_out: Path, identity: int) -> None:
    elem_out.parent.mkdir(parents=True, exist_ok=True)
    qn = int(k.ALPHABET_SIZE)
    s = 4 * qn
    with elem_out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["s960_id", "phase_idx", "q240_id", "label", "is_identity"])
        for sid in range(s):
            w.writerow([sid, sid // qn, sid % qn, s960_label(int(sid)), int(sid == int(identity))])

    with clock_out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["clock_id", "period", "rep_id", "canonical_cycle"])
        for c in clocks:
            cyc = "|".join(str(int(x)) for x in c.canonical_cycle)
            w.writerow([int(c.clock_id), int(c.period), int(c.rep_id), cyc])


def open_dense_writer(path: Path, gzip_output: bool) -> Tuple[object, csv.writer]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if gzip_output:
        fh = gzip.open(path, "wt", newline="", encoding="utf-8")
    else:
        fh = path.open("w", newline="", encoding="utf-8")
    return fh, csv.writer(fh)


def main() -> None:
    p = argparse.ArgumentParser(description="Build brute-force S960 doublet->clock shift table.")
    p.add_argument("--out-csv", type=str, default=str(OUT_DENSE), help="Dense table output path.")
    p.add_argument("--out-clock-meta", type=str, default=str(OUT_CLOCKS), help="Clock metadata CSV.")
    p.add_argument("--out-elem-meta", type=str, default=str(OUT_ELEMS), help="S960 element metadata CSV.")
    p.add_argument("--plain-csv", action="store_true", help="Write plain CSV (not gzip).")
    p.add_argument("--limit-pairs", type=int, default=0, help="0 means full 960*960 pairs.")
    p.add_argument("--progress-every", type=int, default=5000, help="Progress print cadence.")
    p.add_argument("--b-chunk", type=int, default=120, help="Chunk size for B-axis vectorized evaluation.")
    args = p.parse_args()

    out_csv = Path(args.out_csv).resolve()
    out_clock = Path(args.out_clock_meta).resolve()
    out_elem = Path(args.out_elem_meta).resolve()
    gzip_output = not bool(args.plain_csv)

    t0 = time.time()
    mul = build_s960_mul_table()
    s_size = int(mul.shape[0])
    identity = s960_identity_id()
    clocks = build_clocks(mul, int(identity))
    if len(clocks) != 425:
        print(f"[warn] expected 425 non-identity clocks, got {len(clocks)}")

    clock_elems, mask, lengths, pos = build_clock_arrays(clocks, s_size=s_size)
    idx = np.arange(clock_elems.shape[1], dtype=np.int16)[None, :]
    clock_ids = np.arange(len(clocks), dtype=np.int32)[:, None]
    C_id = int(identity)

    write_meta(clocks, elem_out=out_elem, clock_out=out_clock, identity=int(identity))

    headers = ["A", "B", "C"]
    headers.extend(f"clock_{i:03d}" for i in range(len(clocks)))
    fh, w = open_dense_writer(out_csv, gzip_output=gzip_output)
    try:
        w.writerow(headers)

        pair_target = s_size * s_size
        if int(args.limit_pairs) > 0:
            pair_target = min(pair_target, int(args.limit_pairs))

        done = 0
        n_clocks = len(clocks)
        max_p = int(clock_elems.shape[1])
        mask3 = mask[None, :, :]  # (1,425,max_p)
        idx3 = idx[None, :, :]  # (1,425,max_p)
        len3 = lengths[None, :, None]  # (1,425,1)
        cix = np.arange(n_clocks, dtype=np.int32)[None, :, None]  # (1,425,1)
        b_chunk = max(1, int(args.b_chunk))

        for A in range(s_size):
            if done >= pair_target:
                break

            for b0 in range(0, s_size, b_chunk):
                if done >= pair_target:
                    break
                b1 = min(s_size, b0 + b_chunk)
                B_idx = np.arange(b0, b1, dtype=np.int32)
                # Y shape: (chunk, s_size), Y[j, x] = A * (B_j * x)
                Y = mul[A, mul[B_idx, :]]
                # gather clock elements for all B in chunk: (chunk, 425, max_p)
                selected = Y[:, clock_elems]
                # position lookup in each clock: (chunk, 425, max_p)
                psel = pos[cix, selected]

                valid = np.all((~mask3) | (psel >= 0), axis=2)
                deltas = (psel - idx3) % len3
                same = np.all((~mask3) | (deltas == deltas[:, :, [0]]), axis=2)
                rot = valid & same

                shifts = np.full((b1 - b0, n_clocks), SENTINEL, dtype=np.int16)
                shifts[rot] = deltas[:, :, 0][rot].astype(np.int16)

                # Respect global pair target.
                remaining = pair_target - done
                rows_here = min(remaining, b1 - b0)
                for j in range(rows_here):
                    B = int(B_idx[j])
                    row = [int(A), int(B), int(C_id)]
                    row.extend(int(x) for x in shifts[j].tolist())
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
    print(f"Wrote dense table: {out_csv}")
    print(f"Wrote clock metadata: {out_clock}")
    print(f"Wrote element metadata: {out_elem}")
    print(f"rows={done}, elapsed={dt:.1f}s, rate={done/dt:,.1f} rows/s")
    print(f"s960_size={s_size}, non_identity_clocks={len(clocks)}, identity_id={identity}")


if __name__ == "__main__":
    main()

"""S2880 light-cone Bayesian kernel (experimental motif-search lane).

Purpose:
- Keep the conservative pair update structure of the S2880 kernel.
- For each pair event, use the full past light-cone window (t-N..t-1)
  to choose the phase-transfer channel in a Bayesian way.

State encoding:
  sid = phase * 240 + q_id
  phase in Z12, q_id in Q240

Core guarantees preserved:
- Updates are computed from pre-round state only.
- One disjoint edge round is committed per tick.
- Per-pair triality is exactly conserved:
    (g_i' + g_j') mod 3 == (g_i + g_j) mod 3
  where g = phase mod 3.

Experimental additions:
- dg is selected by posterior score using the pair's past light-cone evidence.
- History can be initialized as repeated copies of the same image (t), with
  optional perturbations on older frames.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_s2880_pair_conservative_v1 as kpair


KERNEL_PROFILE = "cog_v3_s2880_lightcone_bayesian_v1"
PHASE_COUNT = 12


@dataclass(frozen=True)
class LightconeBayesConfig:
    """Hyperparameters for light-cone Bayesian dg selection."""

    depth: int = 3
    alpha: float = 1.0
    recency_decay: float = 0.85
    baseline_bias: float = 1.0
    include_spatial_cone: bool = True


class LightconeCache:
    """Cache exact graph-distance light-cone node sets.

    The graph is built from all edges in all disjoint rounds.
    nodes_within_hops(i, h) returns all nodes reachable from i in <= h hops.
    """

    def __init__(self, adjacency: Tuple[np.ndarray, ...]) -> None:
        self.adjacency = adjacency
        self.n_nodes = len(adjacency)
        self._within_cache: Dict[Tuple[int, int], np.ndarray] = {}

    @classmethod
    def from_pair_rounds(cls, pair_rounds: kpair.PairRounds) -> "LightconeCache":
        n_nodes = int(pair_rounds.nx) * int(pair_rounds.ny) * int(pair_rounds.nz)
        neigh_lists: List[List[int]] = [[] for _ in range(n_nodes)]
        for arr in pair_rounds.rounds:
            if arr.size == 0:
                continue
            for a, b in arr.tolist():
                ia = int(a)
                ib = int(b)
                neigh_lists[ia].append(ib)
                neigh_lists[ib].append(ia)
        adjacency = tuple(np.asarray(sorted(set(v)), dtype=np.int32) for v in neigh_lists)
        return cls(adjacency=adjacency)

    def nodes_within_hops(self, start: int, hops: int) -> np.ndarray:
        key = (int(start), int(hops))
        got = self._within_cache.get(key)
        if got is not None:
            return got

        s = int(start)
        h = int(hops)
        if h <= 0:
            arr0 = np.asarray([s], dtype=np.int32)
            self._within_cache[key] = arr0
            return arr0

        visited = {s}
        frontier = {s}
        for _ in range(h):
            nxt: set[int] = set()
            for node in frontier:
                for nb in self.adjacency[node].tolist():
                    if int(nb) not in visited:
                        nxt.add(int(nb))
            if not nxt:
                break
            visited.update(nxt)
            frontier = nxt
        arr = np.asarray(sorted(visited), dtype=np.int32)
        self._within_cache[key] = arr
        return arr


def default_qmul_table() -> np.ndarray:
    return c12.build_qmul_table()


def gamma_sum_mod3(world: np.ndarray, *, qn: int) -> int:
    sid = np.asarray(world, dtype=np.uint16).astype(np.int32)
    p = sid // int(qn)
    return int(np.sum(p % 3) % 3)


def initialize_history_from_world(
    world_now: np.ndarray,
    *,
    depth: int,
    qn: int = 240,
    phase_count: int = PHASE_COUNT,
    perturb_prob: float = 0.0,
    global_seed: int = 0,
) -> Tuple[np.ndarray, ...]:
    """Build history [t-depth, ..., t] from a single reference frame.

    Default behavior:
    - Every past frame starts as the same image as world_now.
    - Optional perturbations are applied to older frames only.
    """

    d = int(max(0, depth))
    base = np.asarray(world_now, dtype=np.uint16)
    out: List[np.ndarray] = []
    rr = np.random.default_rng(int(global_seed))

    for age in range(d, -1, -1):
        frame = base.copy()
        if float(perturb_prob) > 0.0 and age > 0:
            p_eff = min(1.0, float(perturb_prob) * (float(age) / float(max(1, d))))
            mask = rr.random(frame.shape[0]) < p_eff
            if np.any(mask):
                sid = frame.astype(np.int32)
                ph = sid // int(qn)
                q = sid % int(qn)
                # Small phase jitter to explore nearby local attractors.
                delta = rr.choice(np.asarray([-1, 1], dtype=np.int32), size=int(np.sum(mask)))
                ph[mask] = (ph[mask] + delta) % int(phase_count)
                frame = (ph * int(qn) + q).astype(np.uint16)
        out.append(frame)
    return tuple(out)


def _decode_sid(world: np.ndarray, qn: int) -> Tuple[np.ndarray, np.ndarray]:
    sid = np.asarray(world, dtype=np.uint16).astype(np.int32)
    return sid // int(qn), sid % int(qn)


def _choose_dg_from_lightcone(
    *,
    gl: int,
    gr: int,
    base_dg: int,
    left_counts: np.ndarray,
    right_counts: np.ndarray,
    alpha: float,
    baseline_bias: float,
) -> int:
    """Pick dg in {0,1,2} by posterior score.

    score[d] ~ prior[d] * P_left[(gl+d)%3] * P_right[(gr-d)%3]
    """

    prior = np.full((3,), float(alpha), dtype=np.float64)
    prior[int(base_dg) % 3] += float(baseline_bias)

    lp = left_counts.astype(np.float64)
    rp = right_counts.astype(np.float64)
    lp = lp / float(max(lp.sum(), 1e-12))
    rp = rp / float(max(rp.sum(), 1e-12))

    score = prior.copy()
    for d in range(3):
        score[d] *= lp[(int(gl) + d) % 3] * rp[(int(gr) - d) % 3]

    best = float(np.max(score))
    cand = np.where(score == best)[0].astype(np.int32)
    if int(base_dg) in cand.tolist():
        return int(base_dg)
    return int(cand[0])


def step_lightcone_bayesian(
    history: Sequence[np.ndarray],
    pair_rounds: kpair.PairRounds,
    *,
    qmul: np.ndarray,
    config: LightconeBayesConfig,
    cache: Optional[LightconeCache] = None,
    phase_count: int = PHASE_COUNT,
    tick: int = 0,
) -> np.ndarray:
    """One tick using full past light-cone evidence.

    history is ordered as [oldest, ..., current]. current = history[-1].
    """

    if len(history) <= 0:
        raise ValueError("history must include at least one frame")
    cur = np.asarray(history[-1], dtype=np.uint16).copy()
    if cur.ndim != 1:
        raise ValueError("history frames must be flat uint16 arrays")

    qn = int(qmul.shape[0])
    n_rounds = int(len(pair_rounds.rounds))
    if n_rounds <= 0:
        return cur
    ridx = int(tick) % n_rounds
    pairs = pair_rounds.rounds[ridx]
    if pairs.size == 0:
        return cur

    if cache is None:
        cache = LightconeCache.from_pair_rounds(pair_rounds)

    # Base snapshot for this tick's event computations.
    base = cur.astype(np.int32)
    out = cur.copy()

    li = pairs[:, 0].astype(np.int32)
    ri = pairs[:, 1].astype(np.int32)
    sl = base[li]
    sr = base[ri]
    pl = sl // qn
    pr = sr // qn
    ql = sl % qn
    qr = sr % qn

    # Q-channel remains the same non-commutative pair product.
    ql_new = qmul[ql, qr].astype(np.int32)
    qr_new = qmul[qr, ql].astype(np.int32)

    pl_new = pl.copy()
    pr_new = pr.copy()

    depth_use = min(int(config.depth), max(0, len(history) - 1))

    for idx in range(int(li.shape[0])):
        lnode = int(li[idx])
        rnode = int(ri[idx])
        gl = int(pl[idx] % 3)
        gr = int(pr[idx] % 3)
        base_dg = int((ql[idx] + 2 * qr[idx] + int(ridx)) % 3)

        left_counts = np.full((3,), float(config.alpha), dtype=np.float64)
        right_counts = np.full((3,), float(config.alpha), dtype=np.float64)

        for lag in range(1, depth_use + 1):
            frame = np.asarray(history[-1 - lag], dtype=np.uint16)
            w = float(config.recency_decay) ** float(lag - 1)

            if bool(config.include_spatial_cone):
                left_nodes = cache.nodes_within_hops(lnode, lag)
                right_nodes = cache.nodes_within_hops(rnode, lag)
            else:
                left_nodes = np.asarray([lnode], dtype=np.int32)
                right_nodes = np.asarray([rnode], dtype=np.int32)

            left_g = (frame[left_nodes].astype(np.int32) // qn) % 3
            right_g = (frame[right_nodes].astype(np.int32) // qn) % 3
            left_counts += w * np.bincount(left_g, minlength=3).astype(np.float64)
            right_counts += w * np.bincount(right_g, minlength=3).astype(np.float64)

        dg_sel = _choose_dg_from_lightcone(
            gl=gl,
            gr=gr,
            base_dg=base_dg,
            left_counts=left_counts,
            right_counts=right_counts,
            alpha=float(config.alpha),
            baseline_bias=float(config.baseline_bias),
        )

        # Exact per-pair triality conservation by construction (+dg / -dg).
        pl_new[idx] = (pl[idx] + int(dg_sel)) % int(phase_count)
        pr_new[idx] = (pr[idx] - int(dg_sel)) % int(phase_count)

    out[li] = (pl_new * qn + ql_new).astype(np.uint16)
    out[ri] = (pr_new * qn + qr_new).astype(np.uint16)
    return out


def run_ticks_lightcone_bayesian(
    history: Sequence[np.ndarray],
    pair_rounds: kpair.PairRounds,
    *,
    qmul: np.ndarray,
    ticks: int,
    config: LightconeBayesConfig,
    cache: Optional[LightconeCache] = None,
    phase_count: int = PHASE_COUNT,
    tick0: int = 0,
) -> Tuple[np.ndarray, Tuple[np.ndarray, ...]]:
    """Run ticks while maintaining a rolling history window."""

    if len(history) <= 0:
        raise ValueError("history must include at least one frame")
    hist = [np.asarray(w, dtype=np.uint16).copy() for w in history]
    if cache is None:
        cache = LightconeCache.from_pair_rounds(pair_rounds)

    keep = int(max(1, int(config.depth) + 1))
    for k in range(int(ticks)):
        nxt = step_lightcone_bayesian(
            hist,
            pair_rounds,
            qmul=qmul,
            config=config,
            cache=cache,
            phase_count=int(phase_count),
            tick=int(tick0) + int(k),
        )
        hist.append(nxt)
        if len(hist) > keep:
            hist = hist[-keep:]
    return hist[-1], tuple(hist)


def inspect_pair_lightcone(
    history: Sequence[np.ndarray],
    pair_rounds: kpair.PairRounds,
    *,
    cache: LightconeCache,
    tick: int,
    pair_row_index: int,
    depth: int,
    qn: int = 240,
) -> Dict[str, object]:
    """Return a human-readable view of one pair's full past light cone."""

    n_rounds = int(len(pair_rounds.rounds))
    if n_rounds <= 0:
        raise ValueError("pair_rounds has no rounds")
    ridx = int(tick) % n_rounds
    pairs = pair_rounds.rounds[ridx]
    if not (0 <= int(pair_row_index) < int(pairs.shape[0])):
        raise IndexError("pair_row_index out of bounds for selected round")
    left = int(pairs[int(pair_row_index), 0])
    right = int(pairs[int(pair_row_index), 1])

    depth_use = min(int(depth), max(0, len(history) - 1))
    lag_rows: List[Dict[str, object]] = []
    for lag in range(1, depth_use + 1):
        frame = np.asarray(history[-1 - lag], dtype=np.uint16)
        left_nodes = cache.nodes_within_hops(left, lag)
        right_nodes = cache.nodes_within_hops(right, lag)
        left_g = (frame[left_nodes].astype(np.int32) // int(qn)) % 3
        right_g = (frame[right_nodes].astype(np.int32) // int(qn)) % 3
        lag_rows.append(
            {
                "lag": int(lag),
                "left_nodes": left_nodes.tolist(),
                "right_nodes": right_nodes.tolist(),
                "left_g_hist": np.bincount(left_g, minlength=3).astype(int).tolist(),
                "right_g_hist": np.bincount(right_g, minlength=3).astype(int).tolist(),
            }
        )

    return {
        "tick": int(tick),
        "round_index": int(ridx),
        "pair_row_index": int(pair_row_index),
        "left_index": int(left),
        "right_index": int(right),
        "lags": lag_rows,
    }

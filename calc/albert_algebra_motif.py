"""
albert_algebra_motif.py  -- Attack Vector 2: Albert Algebra Embedder
Tests whether a 3-node COG motif (3 lepton generations) dynamically generates
eigenvalue statistics matching the J3(O_C) exceptional Jordan algebra prediction
delta^2 = 3/8 (Singh 2025, arXiv:2508.10131).

The 3x3 interaction matrix M_ij = <psi_i | psi_j> is built at each tick from
the COG Fano product of node states. Eigenvalues of M (real, since M is Hermitian)
give the mass-squared spectrum. The spread delta^2 = Var(sqrt(lambda)) / mean(sqrt(lambda))
is compared to the Singh target 3/8.

Run: pytest calc/test_albert_algebra_motif.py -v
"""

import numpy as np
from calc.conftest import FANO_CYCLES, FANO_SIGN, FANO_THIRD


def fano_mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Multiply two 8-vectors using the Furey octonion convention.
    a[0] = scalar part; a[1..7] = imaginary parts e1..e7.
    FANO_CYCLES uses 0-indexed imaginary units (0=e1..6=e7),
    so Fano index i maps to 8-vector index i+1.
    FANO_SIGN is keyed by (i,j) tuples.
    """
    result = np.zeros(8)
    # Scalar × scalar - imaginary.imaginary
    result[0] = a[0] * b[0] - np.dot(a[1:], b[1:])
    # Cross terms with scalar
    result[1:] = a[0] * b[1:] + b[0] * a[1:]
    # Fano imaginary products: iterate ALL 42 ordered pairs (FANO_SIGN covers cyclic+anti-cyclic)
    for (i, j), sgn in FANO_SIGN.items():
        k = FANO_THIRD[(i, j)]
        # 8-vector indices: Fano index p -> array index p+1
        result[k + 1] += sgn * a[i + 1] * b[j + 1]
    return result


def fano_inner(a: np.ndarray, b: np.ndarray) -> float:
    """Standard octonionic inner product (Euclidean dot product on R^8)."""
    return float(np.dot(a, b))


def build_interaction_matrix(states: list[np.ndarray]) -> np.ndarray:
    """
    Build the 3x3 Hermitian interaction matrix M_ij = <psi_i | psi_j>.
    States are real 8-vectors; M is real symmetric (= Hermitian over R).
    """
    n = len(states)
    M = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            M[i, j] = fano_inner(states[i], states[j])
    return M


def tick_states(states: list[np.ndarray]) -> list[np.ndarray]:
    """
    One COG tick for a 3-node lepton generation motif.
    Each node receives the Fano product of the OTHER two nodes' states,
    then is renormalised.
    The interaction is: psi_i' = fano_mul(psi_j, psi_k)  (cyclic)
    """
    n = len(states)
    new_states = []
    for i in range(n):
        j = (i + 1) % n
        k = (i + 2) % n
        raw = fano_mul(states[j], states[k])
        norm = np.linalg.norm(raw)
        new_states.append(raw / norm if norm > 1e-12 else states[i].copy())
    return new_states


def eigenvalue_spread(M: np.ndarray) -> float:
    """
    Compute delta^2 = Var(sqrt(lambda)) / mean(sqrt(lambda))^2
    where lambda are eigenvalues of M (negative eigenvalues set to 0).
    This is the Singh 2025 J3(O) diagnostic; target = 3/8.
    """
    evals = np.linalg.eigvalsh(M)
    evals_pos = np.clip(evals, 0, None)  # mass-squared >= 0
    sqrt_evals = np.sqrt(evals_pos)
    mu = np.mean(sqrt_evals)
    if mu < 1e-12:
        return float("nan")
    return float(np.var(sqrt_evals) / mu ** 2)


def run_motif(
    n_ticks: int = 500,
    seed: int = 42,
    verbose: bool = False,
) -> dict:
    """
    Run a 3-node lepton generation motif for n_ticks ticks.
    Returns dict with:
      - delta_sq_final:   delta^2 at last tick
      - delta_sq_mean:    mean delta^2 over last 100 ticks
      - delta_sq_target:  3/8 = 0.375 (Singh 2025)
      - deviation_pct:    |delta_sq_mean - 3/8| / (3/8) * 100
      - eigenvalues_final: M eigenvalues at last tick
    """
    rng = np.random.default_rng(seed)
    # Initialize 3 distinct states on the Fano imaginary sphere
    states = []
    for idx in range(3):
        raw = rng.standard_normal(8)
        raw[0] = 0.0  # project onto imaginary subspace (no scalar part)
        states.append(raw / np.linalg.norm(raw))

    target = 3.0 / 8.0
    history = []

    for tick in range(n_ticks):
        M = build_interaction_matrix(states)
        d2 = eigenvalue_spread(M)
        history.append(d2)
        states = tick_states(states)
        if verbose and tick % 100 == 0:
            print(f"  tick {tick:4d}: delta^2 = {d2:.6f}  (target 3/8 = 0.375)")

    M_final = build_interaction_matrix(states)
    d2_final = eigenvalue_spread(M_final)
    evals_final = np.linalg.eigvalsh(M_final)
    d2_mean = float(np.nanmean(history[-100:]))

    result = {
        "delta_sq_final":   round(d2_final, 8),
        "delta_sq_mean":    round(d2_mean, 8),
        "delta_sq_target":  target,
        "deviation_pct":    round(abs(d2_mean - target) / target * 100, 4),
        "eigenvalues_final": evals_final.tolist(),
        "sqrt_mass_ratios":  sorted(np.sqrt(np.clip(evals_final, 0, None)).tolist()),
    }

    if verbose:
        print(f"\n  Final delta^2 = {d2_final:.6f}")
        print(f"  Mean delta^2 (last 100 ticks) = {d2_mean:.6f}")
        print(f"  Target (J3(O) / Singh 2025) = {target:.6f} = 3/8")
        print(f"  Deviation: {result['deviation_pct']:.3f}%")
        ev = result["sqrt_mass_ratios"]
        if ev[0] > 1e-8:
            print(f"  sqrt(m) ratios: 1 : {ev[1]/ev[0]:.3f} : {ev[2]/ev[0]:.3f}")
        print(f"  Singh 2025 target ratios: 1 : 2 : 3")

    return result


def scan_seeds(n_seeds: int = 20, n_ticks: int = 500) -> dict:
    """
    Run motif across multiple random seeds; report mean delta^2 and fraction
    of runs within 5% of the 3/8 target.
    """
    target = 3.0 / 8.0
    deltas = []
    for seed in range(n_seeds):
        r = run_motif(n_ticks=n_ticks, seed=seed, verbose=False)
        if not np.isnan(r["delta_sq_mean"]):
            deltas.append(r["delta_sq_mean"])

    deltas = np.array(deltas)
    fraction_close = float(np.mean(np.abs(deltas - target) / target < 0.05))
    return {
        "n_seeds":       n_seeds,
        "mean_delta_sq": round(float(np.mean(deltas)), 6),
        "std_delta_sq":  round(float(np.std(deltas)), 6),
        "target":        target,
        "fraction_within_5pct": round(fraction_close, 3),
    }


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("=== Albert Algebra Motif: COG 3-generation lepton cone ===")
    print("    Testing whether COG dynamics generates delta^2 = 3/8 (Singh 2025)\n")
    result = run_motif(n_ticks=500, verbose=True)
    print()
    print("=== Seed scan (20 seeds) ===")
    scan = scan_seeds(n_seeds=20, n_ticks=500)
    print(f"  Mean delta^2 across seeds: {scan['mean_delta_sq']:.6f}")
    print(f"  Target:                    {scan['target']:.6f} = 3/8")
    print(f"  Std:                       {scan['std_delta_sq']:.6f}")
    print(f"  Fraction within 5% of target: {scan['fraction_within_5pct']:.1%}")
    dev = abs(scan['mean_delta_sq'] - scan['target']) / scan['target'] * 100
    print(f"  Overall deviation: {dev:.2f}%")

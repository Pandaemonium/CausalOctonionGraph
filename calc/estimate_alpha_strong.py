"""
calc/estimate_alpha_strong.py
RFC-026 §5.1: R(N) convergence to 1/7 — alpha_s leading-order estimate

Computes the trapped/total Fano-operation ratio R(N) for increasing
random-walk lengths N, showing convergence to 1/7 ≈ 0.14286.

Definitions (RFC-026 §4):
  "Trapped"  = Fano automorphism in Stab(e7) — the 24-element S4 subgroup.
  "Escaped"  = Fano automorphism NOT in Stab(e7) — remaining 144 elements.
  R(N)       = (trapped steps seen in N-step walk) / N

Theoretical limit: R(∞) = 24/168 = 1/7 by uniform measure on GL(3,2).
Physical comparison: alpha_s(M_Z) ≈ 0.1181 (~20% below; see RFC-026 §2).

TODO (delegate): add finite-density correction model per RFC-026 §5.1.
"""
from calc.gauge_check import (
    build_fano_auts,
    fixes_vacuum,
)
import numpy as np

ALPHA_S_PROXY = 1 / 7          # COG leading-order estimate
ALPHA_S_PHYSICAL = 0.1181      # PDG value at M_Z scale


def build_stabilizer_set(auts: list[list[int]], vacuum_axis: int = 6) -> set[int]:
    """Return indices of automorphisms that fix the vacuum axis."""
    return {i for i, sigma in enumerate(auts) if sigma[vacuum_axis] == vacuum_axis}


def estimate_R(n_steps: int, auts: list, stab_indices: set, rng) -> float:
    """Monte Carlo estimate of R(N): fraction of trapped steps in N-step walk."""
    choices = rng.integers(0, len(auts), size=n_steps)
    trapped = np.sum(np.isin(choices, list(stab_indices)))
    return trapped / n_steps


def run_convergence_scan(
    ns: list[int] = None,
    n_trials: int = 5,
    seed: int = 42,
) -> list[dict]:
    """Run R(N) for increasing N and report convergence to 1/7."""
    if ns is None:
        ns = [100, 500, 1_000, 5_000, 10_000, 50_000, 100_000]

    auts = build_fano_auts()
    stab = build_stabilizer_set(auts)
    rng = np.random.default_rng(seed)

    rows = []
    for n in ns:
        estimates = [estimate_R(n, auts, stab, rng) for _ in range(n_trials)]
        mean = float(np.mean(estimates))
        std = float(np.std(estimates))
        gap_from_proxy = mean - ALPHA_S_PROXY
        rows.append({
            "N": n,
            "R_mean": mean,
            "R_std": std,
            "proxy_1_7": ALPHA_S_PROXY,
            "gap_from_proxy": gap_from_proxy,
        })
    return rows


def print_report(rows: list[dict]) -> None:
    print(
        f"{'N':>10}  {'R(N)':>8}  {'±std':>7}  "
        f"{'1/7':>8}  {'gap':>8}"
    )
    print("-" * 55)
    for r in rows:
        print(
            f"{r['N']:>10,}  {r['R_mean']:>8.5f}  {r['R_std']:>7.5f}  "
            f"{r['proxy_1_7']:>8.5f}  {r['gap_from_proxy']:>+8.5f}"
        )
    print()
    print(f"  COG proxy (1/7):        {ALPHA_S_PROXY:.5f}")
    print(f"  Physical alpha_s(M_Z):  {ALPHA_S_PHYSICAL:.5f}")
    print(f"  Gap (proxy - physical): {ALPHA_S_PROXY - ALPHA_S_PHYSICAL:+.5f}  "
          f"({100*(ALPHA_S_PROXY - ALPHA_S_PHYSICAL)/ALPHA_S_PHYSICAL:+.1f}%)")
    print()
    print("  Note: ~20% overestimate attributed to trapped/escaped mixing")
    print("  correction at finite graph density (RFC-026 §5.1).")
    print("  TODO: implement finite-density correction model.")


if __name__ == "__main__":
    print("=== R(N) convergence to 1/7: alpha_s leading-order estimate ===\n")
    rows = run_convergence_scan()
    print_report(rows)

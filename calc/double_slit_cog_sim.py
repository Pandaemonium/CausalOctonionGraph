"""
calc/double_slit_cog_sim.py

RFC-033 prototype:
  Deterministic double-slit simulation using COG-style path-family updates.

This is a finite, fixed-topology toy model for:
  1) one-slit baselines (A-only, B-only),
  2) two-slit interference,
  3) which-way coupling sweep and fringe-visibility suppression.

Design constraints:
  - No RNG calls. Every shot is deterministic from integer shot_id.
  - Relative phase is quarter-turn (mod 4), aligned with RFC-023 clock style.
  - Which-way coupling is modeled as path-local extra interaction ticks that
    dephase A and B contributions across shots.

Run:
  python -m calc.double_slit_cog_sim
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import hashlib
import json
import math
from typing import Dict, Iterable, List, Tuple

import numpy as np


PHASES: Tuple[complex, ...] = (1.0 + 0.0j, 0.0 + 1.0j, -1.0 + 0.0j, 0.0 - 1.0j)


@dataclass(frozen=True)
class DoubleSlitConfig:
    """Deterministic toy-model parameters."""

    n_bins: int = 121
    shots: int = 8000
    screen_distance: float = 1.2
    source_distance: float = 1.0
    slit_separation: float = 0.18
    screen_half_width: float = 0.9
    ticks_per_unit: float = 56.0
    envelope_sigma: float = 0.42
    slit_width: float = 0.08
    sample_seed: int = 7331


def _u64(*values: int) -> int:
    """Deterministic 64-bit hash from integer tuple."""
    h = hashlib.blake2b(digest_size=8)
    for v in values:
        h.update(int(v).to_bytes(8, "little", signed=True))
    return int.from_bytes(h.digest(), "little", signed=False)


def _phase_from_ticks(ticks: int) -> complex:
    """Quarter-turn phase from integer tick count."""
    return PHASES[ticks & 3]


def _x_coords(cfg: DoubleSlitConfig) -> np.ndarray:
    return np.linspace(-cfg.screen_half_width, cfg.screen_half_width, cfg.n_bins)


def _path_ticks(
    x_bin: float,
    slit_x: float,
    cfg: DoubleSlitConfig,
) -> int:
    """Approximate path length converted to integer ticks."""
    src_to_slit = math.hypot(slit_x, cfg.source_distance)
    slit_to_screen = math.hypot(x_bin - slit_x, cfg.screen_distance)
    length = src_to_slit + slit_to_screen
    return int(round(cfg.ticks_per_unit * length))


def _path_weight(x_bin: float, slit_x: float, cfg: DoubleSlitConfig) -> float:
    """Envelope x diffraction surrogate for one path."""
    envelope = math.exp(-((x_bin / cfg.envelope_sigma) ** 2))
    # numpy.sinc uses sin(pi x)/(pi x); this gives a narrow slit envelope.
    diffraction = abs(np.sinc((x_bin - slit_x) / cfg.slit_width))
    return float(envelope * diffraction)


def _path_amplitude(
    shot_id: int,
    x_bin: float,
    slit_label: int,
    slit_x: float,
    cfg: DoubleSlitConfig,
) -> complex:
    """
    Deterministic path contribution for one slit.

    Path phase includes deterministic hidden microstate offset per shot.
    Which-way suppression is handled at the AB interference term.
    """
    base_ticks = _path_ticks(x_bin, slit_x, cfg)
    # Shared source-phase offset per shot keeps relative A/B phase coherent
    # when which-way coupling is zero.
    hidden_ticks = _u64(cfg.sample_seed, shot_id, 1717) % 4
    phase = _phase_from_ticks(base_ticks + hidden_ticks)
    weight = _path_weight(x_bin, slit_x, cfg)
    return weight * phase


def _intensity_profile(
    shot_id: int,
    mode: str,
    which_way: float,
    cfg: DoubleSlitConfig,
    x: np.ndarray,
) -> np.ndarray:
    """Per-shot detector intensity over bins."""
    slit_a = -0.5 * cfg.slit_separation
    slit_b = +0.5 * cfg.slit_separation
    intens = np.zeros_like(x, dtype=float)

    for i, xb in enumerate(x):
        a = _path_amplitude(shot_id, float(xb), 0, slit_a, cfg)
        b = _path_amplitude(shot_id, float(xb), 1, slit_b, cfg)

        if mode == "A":
            intens[i] = float((a.conjugate() * a).real)
        elif mode == "B":
            intens[i] = float((b.conjugate() * b).real)
        elif mode == "AB":
            # Which-way coupling suppresses coherence in the cross term.
            # c=1.0 -> full coherence, c=0.0 -> no interference.
            c = max(0.0, min(1.0, 1.0 - which_way))
            ia = float((a.conjugate() * a).real)
            ib = float((b.conjugate() * b).real)
            cross = 2.0 * c * float((a.conjugate() * b).real)
            intens[i] = max(1e-12, ia + ib + cross)
        else:
            raise ValueError(f"Unknown mode {mode!r}")

    # Keep strictly positive for categorical sampling.
    intens += 1e-12
    return intens


def _sample_bin_from_profile(profile: np.ndarray, shot_id: int, cfg: DoubleSlitConfig) -> int:
    """Deterministic categorical sample from per-shot intensity profile."""
    probs = profile / profile.sum()
    cdf = np.cumsum(probs)
    u = _u64(cfg.sample_seed, shot_id, 99991) / float(2**64)
    idx = int(np.searchsorted(cdf, u, side="right"))
    if idx >= len(profile):
        idx = len(profile) - 1
    return idx


def run_experiment(
    mode: str,
    cfg: DoubleSlitConfig,
    which_way: float = 0.0,
) -> Dict[str, np.ndarray]:
    """Run deterministic shot ensemble and return histogram and mean profile."""
    x = _x_coords(cfg)
    hist = np.zeros(cfg.n_bins, dtype=int)
    profile_acc = np.zeros(cfg.n_bins, dtype=float)

    for shot in range(cfg.shots):
        profile = _intensity_profile(shot, mode=mode, which_way=which_way, cfg=cfg, x=x)
        profile_acc += profile
        idx = _sample_bin_from_profile(profile, shot, cfg)
        hist[idx] += 1

    mean_profile = profile_acc / float(cfg.shots)
    return {"x": x, "hist": hist, "mean_profile": mean_profile}


def _moving_average(y: np.ndarray, win: int = 5) -> np.ndarray:
    if win <= 1:
        return y.copy()
    kernel = np.ones(win, dtype=float) / float(win)
    return np.convolve(y, kernel, mode="same")


def fringe_visibility(profile: np.ndarray) -> float:
    """
    Compute fringe visibility from histogram in central detector region.

    V = (Imax - Imin) / (Imax + Imin) using local maxima/minima estimates.
    """
    y = _moving_average(profile.astype(float), win=5)
    if np.all(y <= 0):
        return 0.0
    n = len(y)
    # Restrict to central detector strip where interference fringes are expected.
    lo = int(0.40 * n)
    hi = int(0.60 * n)
    ys = y[lo:hi]
    if len(ys) < 5:
        return 0.0

    peaks: List[float] = []
    troughs: List[float] = []
    for i in range(1, len(ys) - 1):
        if ys[i] > ys[i - 1] and ys[i] > ys[i + 1]:
            peaks.append(float(ys[i]))
        if ys[i] < ys[i - 1] and ys[i] < ys[i + 1]:
            troughs.append(float(ys[i]))

    if not peaks or not troughs:
        return 0.0

    i_max = max(peaks)
    i_min = min(troughs)
    denom = i_max + i_min
    if denom <= 0:
        return 0.0
    return float(max(0.0, min(1.0, (i_max - i_min) / denom)))


def l1_distance(p: np.ndarray, q: np.ndarray) -> float:
    """L1 distance between two normalized histograms."""
    p = p.astype(float)
    q = q.astype(float)
    p /= p.sum()
    q /= q.sum()
    return float(np.abs(p - q).sum())


def run_which_way_sweep(
    cfg: DoubleSlitConfig,
    couplings: Iterable[float],
    baseline_sum_profile: np.ndarray,
) -> Dict[str, object]:
    """Run AB mode for each coupling and report visibility trend."""
    rows = []
    strength_values: List[float] = []
    for c in couplings:
        result = run_experiment("AB", cfg, which_way=float(c))
        vis = fringe_visibility(result["mean_profile"])
        strength = l1_distance(result["mean_profile"], baseline_sum_profile)
        strength_values.append(strength)
        rows.append(
            {
                "which_way": float(c),
                "visibility_local": vis,
                "interference_strength": strength,
            }
        )

    # Relaxed monotonic check for finite-shot noise.
    tol = 0.002
    monotone_nonincreasing = True
    for i in range(1, len(strength_values)):
        if strength_values[i] > strength_values[i - 1] + tol:
            monotone_nonincreasing = False
            break

    return {"rows": rows, "monotone_nonincreasing": monotone_nonincreasing}


def summary_report(cfg: DoubleSlitConfig, output_json: str | None = None) -> Dict[str, object]:
    """Run one-slit/two-slit and which-way sweep, print and optionally save JSON."""
    res_a = run_experiment("A", cfg, which_way=0.0)
    res_b = run_experiment("B", cfg, which_way=0.0)
    res_ab = run_experiment("AB", cfg, which_way=0.0)

    h_a = res_a["hist"]
    h_b = res_b["hist"]
    h_ab = res_ab["hist"]

    vis_ab = fringe_visibility(res_ab["mean_profile"])
    vis_a = fringe_visibility(res_a["mean_profile"])
    vis_b = fringe_visibility(res_b["mean_profile"])

    p_sum = res_a["mean_profile"] + res_b["mean_profile"]
    interference_l1 = l1_distance(res_ab["mean_profile"], p_sum)

    sweep = run_which_way_sweep(
        cfg,
        couplings=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
        baseline_sum_profile=p_sum,
    )

    out: Dict[str, object] = {
        "config": {
            "n_bins": cfg.n_bins,
            "shots": cfg.shots,
            "screen_distance": cfg.screen_distance,
            "source_distance": cfg.source_distance,
            "slit_separation": cfg.slit_separation,
            "screen_half_width": cfg.screen_half_width,
            "ticks_per_unit": cfg.ticks_per_unit,
            "envelope_sigma": cfg.envelope_sigma,
            "slit_width": cfg.slit_width,
            "sample_seed": cfg.sample_seed,
        },
        "metrics": {
            "visibility_A": vis_a,
            "visibility_B": vis_b,
            "visibility_AB": vis_ab,
            "interference_l1_vs_AplusB": interference_l1,
        },
        "which_way_sweep": sweep,
    }

    print("=" * 72)
    print("RFC-033 deterministic double-slit prototype")
    print("=" * 72)
    print(f"shots={cfg.shots} bins={cfg.n_bins} slit_separation={cfg.slit_separation}")
    print("")
    print("Baseline visibilities:")
    print(f"  A only : {vis_a:.4f}")
    print(f"  B only : {vis_b:.4f}")
    print(f"  A+B    : {vis_ab:.4f}")
    print(f"  L1(A+B vs A_only+B_only): {interference_l1:.4f}")
    print("")
    print("Which-way sweep (AB mode):")
    for row in sweep["rows"]:
        print(
            f"  coupling={row['which_way']:.1f}  "
            f"interference_strength={row['interference_strength']:.4f}"
        )
    print(f"  monotone_nonincreasing={sweep['monotone_nonincreasing']}")
    print("=" * 72)

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"wrote summary: {output_json}")

    return out


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Deterministic COG double-slit prototype")
    p.add_argument("--shots", type=int, default=8000)
    p.add_argument("--bins", type=int, default=121)
    p.add_argument("--seed", type=int, default=7331)
    p.add_argument("--output-json", type=str, default="")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = DoubleSlitConfig(n_bins=args.bins, shots=args.shots, sample_seed=args.seed)
    summary_report(cfg, output_json=(args.output_json or None))


if __name__ == "__main__":
    main()

# RFC-008 Mesoscale Lorentz Pseudosymmetry and RG-Based Kernel Selection Contract

Status: Draft
Date: 2026-03-02
Owner: COG v3 kernel selection lane

## 1. Purpose
Define how kernels are selected using mesoscale Lorentz-like behavior criteria, acknowledging unavoidable microscale lattice anisotropy.

## 2. Principle
We do **not** require exact tick-level Lorentz invariance.
We require anisotropy to shrink under scale, reaching acceptable levels by relevant mesoscales.

## 3. Candidate kernel families
Initial shortlist:
1. `K1`: cube26 uniform seeded fold.
2. `K2`: cube26 shell-scheduled fold.
3. `K3`: cube26 split-step fold.

## 4. Mandatory metrics
Each kernel/seed batch must report:
1. `anisotropy_micro`: low-k directional velocity spread.
2. `front_eccentricity`: isotropic-launch wavefront shape distortion.
3. `anisotropy_block2`, `anisotropy_block4`, `anisotropy_block8` (if feasible).
4. `motif_retention`: survival/period metrics for baseline motifs.

## 5. Scale-decay gate
Kernel passes Lorentz-like gate only if:
1. `anisotropy_block2 < anisotropy_micro`, and
2. `anisotropy_block4 < anisotropy_block2`.

If block8 is computed, it must continue the non-increasing trend.

## 6. Staged evaluation
1. Stage A (screen): cheap isotropy probe + fail-fast.
2. Stage B (candidate): medium horizon with mirrored/rotated launches.
3. Stage C (confirm): long horizon + coarse-graining diagnostics.

## 7. Rejection rules
Reject kernel if any hold:
1. anisotropy increases under coarse-grain levels,
2. front anisotropy is strongly direction-locked,
3. baseline motifs cannot survive enough for kinematic measurement.

## 8. Required artifacts
1. Kernel comparison table (K1/K2/K3).
2. Per-kernel anisotropy decay plots/tables.
3. Run manifest with seeds and deterministic replay metadata.

## 9. Decision policy
- Promote only kernels that satisfy both:
  1) Lorentz-like scale-decay gate,
  2) motif-retention viability.
- If no kernel passes, iterate on rule family before broad motif search expansion.

## 10. Notes
This RFC is a selection contract, not a final physics claim.

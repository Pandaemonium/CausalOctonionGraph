# v3 Long-Horizon Research Backlog (v1)

Date started: 2026-03-02  
Owner: Codex  
Purpose: Track non-immediate research lanes that improve closure probability over weeks/months.

## 1. Priority Lanes

## 1.1 Bayesian/Active Search for Sparse Stable Motifs

Goal:

1. Improve hit-rate for stable loops under strict compute limits.

Planned outputs:

1. ranked seed proposal policy (explore/exploit balance),
2. uncertainty-aware candidate scorer,
3. benchmark against uniform random seed scans.

First experiments:

1. Thompson-style candidate sampling over motif families,
2. novelty-weighted UCB score for scan queue ordering.

## 1.2 Coarse-Graining and Renormalized Descriptors

Goal:

1. Build credible bridges from tractable boxes to larger emergent structures.

Planned outputs:

1. descriptor set (`period_class`, `drift_class`, `support_compactness`, `interaction_signature`),
2. stability-under-scale tests,
3. candidate coarse-grain map registry.

First experiments:

1. scale-up stress tests on top motifs (box and boundary changes),
2. descriptor invariance checks across seeds.
3. anisotropy audits under cube26 and channel-gating variants.

Isotropy note:

1. In multiplication-only kernels, treat "weights" as channel-activation schedules
   (deterministic masks or seeded stochastic gating) instead of additive coefficients.

## 1.3 Triplet-Scale Construction Strategy

Goal:

1. Develop practical route toward triplet-like large motifs without full brute-force at femtometer-equivalent volume.

Planned outputs:

1. hierarchical assembly protocol from smaller stable motifs,
2. interaction-attractor tests for triadic locking,
3. failure taxonomy (boundary-lock, transient mirage, anisotropy artifacts).

First experiments:

1. seeded triad placement with controlled phase offsets,
2. attractor basin scans around triad neighborhoods.

## 1.4 Chiral Kernel Architecture Program

Goal:

1. Identify chiral gate family that yields stable asymmetry without catastrophic instability.

Planned outputs:

1. kernel variant matrix,
2. asymmetry-vs-stability Pareto plots,
3. preregistered keep/drop criteria.

First experiments:

1. strict left-only gate vs soft suppression gate sweeps,
2. mirror/conjugation panel statistics with bootstrap confidence.

## 1.5 Surrogate Models and Fast Rejection

Goal:

1. Use cheap predictors to skip clearly bad candidates before full-kernel long runs.

Planned outputs:

1. surrogate classifier for early decay likelihood,
2. calibrated confidence thresholds for fail-fast.

First experiments:

1. train on archived run traces (`decay` vs `survive`),
2. evaluate false-reject rate on known good candidates.

## 2. Execution Rules

1. Every long-horizon lit cycle must update at least one lane with:
   - one concrete hypothesis,
   - one measurable next test.
2. Any lane that remains unchanged for 72 hours gets a review note:
   - `inactive: reason`.
3. Promote a lane to RFC when:
   - at least one tested hypothesis survives first falsification pass.

## 3. Current Next Actions

1. Add active-search scoring to overnight candidate queue (explore/exploit + novelty).
2. Define first descriptor schema for coarse-grained motif summaries.
3. Draft triplet-assembly pilot protocol using small-box triad seeds.
4. Implement a minimal kernel-variant registry for chiral gate sweeps.

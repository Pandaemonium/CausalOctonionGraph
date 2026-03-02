# RFC-007 Motif-First Chirality Emergence and Parity Test Contract
Status: Draft
Date: 2026-03-02
Owner: COG v3 kernel/motif program
## 1. Purpose
Define a rigorous test contract for the hypothesis that chirality emerges from particle motifs (state geometry + dynamical orbit), not primarily from an explicitly chiral kernel rule.
## 2. Scope
Applies to:
- S960 alphabet (C4 x Q240 shared-phase lane),
- multiplicative-only update semantics,
- cube26-focused kernel candidates.
## 3. Hypothesis
H1 (motif-first chirality):
- For parity-neutral kernels, there exist motifs M where M and its parity-transformed counterpart P(M) show reproducible asymmetric dynamics in designated interaction probes.
Null H0:
- Any apparent chirality is either transient or attributable only to explicit kernel asymmetry/event-order artifact.
## 4. Required observables
For each run, compute and log:
1. winding_sign: oriented phase winding around motif core.
2. 	riad_sign: orientation sign of local transport triad.
3. symmetry_score: response difference between M and P(M) under matched conditions.
4. survival_ticks, period_estimate, drift_vector.
## 5. Experimental protocol
1. Select motif seed M and construct parity transform P(M).
2. Use identical:
   - vacuum boundary condition,
   - kernel parameters,
   - deterministic event-order stream seed.
3. Run Stage A/B/C pipeline (short/medium/confirm horizons).
4. Record observables for both motifs.
## 6. Acceptance criteria (provisional)
A candidate chirality signal requires all:
1. Stability: both runs survive minimum horizon for meaningful comparison.
2. Reproducibility: asymmetry sign persists across at least 3 independent initial placements/orientations.
3. Nontriviality: observed asymmetry exceeds control motif baseline by configured margin.
4. Artifact guard: mirrored kernel-order variant does not fully erase the signal.
## 7. Falsification criteria
Any of the following rejects H1 for tested motif class:
1. Asymmetry collapses under placement/orientation re-sampling.
2. Signal disappears when event-order seed changes while controls remain stable.
3. Signal is fully explained by explicit directional kernel bias.
## 8. Deliverables
1. Chirality probe implementation in v3 runner.
2. Standardized run table with all required observables.
3. Candidate report with pass/fail evidence and raw artifacts.
## 9. Notes
- This RFC is intentionally operational, not interpretive.
- Physical interpretation (weak-channel analogs, parity violation narratives) must only follow successful operational evidence.

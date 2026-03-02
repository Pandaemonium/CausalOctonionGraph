# Round 12 Literature + Synthesis - Closure Memo and Next Actions

Date: 2026-03-02

## Synthesis across rounds
1. S960 has strong algebraic structure that can be turned into actionable priors (orders, families, conjugation tiers).
2. Interaction statistics in Q240 support focused, non-uniform search rather than blind brute force.
3. Chirality is plausible as motif-emergent; we now have explicit observables to test that claim.
4. Lorentz-like behavior should be selected by mesoscale metrics and coarse-grain anisotropy decay, not micro-level symmetry demands.

## Literature-backed constraints
1. Lattice no-go results imply chirality handling must be explicit (motif or structural asymmetry).
2. QCA literature supports low-k covariance as practical target.
3. Coarse-graining literature supports rejecting kernels that fail anisotropy decay.

## New contract-level outputs proposed
1. RFC-007: motif-first chirality emergence and parity test contract.
2. RFC-008: mesoscale Lorentz pseudosymmetry and RG-based kernel selection contract.

## Immediate next actions
1. Implement chirality probe harness and mirrored-control runner.
2. Implement anisotropy-at-scale diagnostic suite.
3. Run K1/K2 comparison with staged fail-fast pipeline.
4. Promote only candidates meeting both chirality and coarse-grain gates.

## Risk register (active)
1. Overfitting metrics to desired outcomes.
2. False positives from transient boundary effects.
3. Computational budget pressure if confirm stage is too broad.
4. Hidden convention-mixing bugs across kernels/conventions.

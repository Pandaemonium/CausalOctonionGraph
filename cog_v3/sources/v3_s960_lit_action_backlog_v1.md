# v3 S960 Literature Action Backlog (v1)

Date: 2026-03-02  
Owner: COG Core  
Status: Active triage

## 1. Purpose

Distill useful ideas from recent S960 literature review memos into:
1. test-ready items,
2. speculative items to track,
3. explicit non-claims.

Input review memos:
1. `sources/s960_particle_morphology_search.md`,
2. `sources/s960_ca_lorentz_lit_review.md`,
3. `sources/s960_cyclic_loops_rotation_lit_review.md`,
4. `sources/s960_chirality_emergence_lit_review.md`,
5. `sources/s960_complex_phase_octavian_lit_review.md`.

## 2. Classification Rule

Each idea is tagged as:
1. `validated_in_kernel`: measured and reproduced in current v3 runs,
2. `test_ready`: measurable now with existing code and artifacts,
3. `speculative`: useful intuition but not yet operational.

## 3. High-Value `test_ready` Items

## 3.1 Chirality diagnostics

1. Add left-vs-right evolution comparison panel for motif candidates.
2. Add associator-activity metric over trajectory windows.
3. Retain spatial asymmetry metric, but demote it to secondary chirality evidence.

Reason:
1. keeps chirality testing tied to nonassociative algebra structure,
2. avoids overinterpreting pure geometry of fronts.

## 3.2 Lorentz battery discipline

1. Run dispersion/isotropy tests on non-saturated distance sets only.
2. Report directional slope spread plus linear-fit residuals.
3. Require scale-persistence before promotion claims.

Reason:
1. protects against false positives from short-distance lattice artifacts.

## 3.3 Search-prior strategy

1. Seed stratification by order class (`1,2,3,4,6,12`),
2. seed stratification by conjugation tier,
3. seed stratification by family class (`A/B/C`) where available.

Reason:
1. reduces blind search and improves candidate diversity under fixed compute.

## 3.4 Lane separation

1. Keep transport occupancy and detector exclusivity as separate evaluation lanes.
2. Do not auto-reject candidate photons solely from two-front occupancy shape.

Reason:
1. occupancy geometry and detector outcomes are not equivalent observables.

## 3.5 Phase-resolution and symmetry-gap probes

1. Add an `effective C12` probe on order-12 sectors:
   - test whether key observables exhibit reproducible 12-step class structure.
2. Add exact geometric-vs-multiplication symmetry gap measurement:
   - compute multiplication-preserving relabeling group for current v3 convention,
   - compare against geometric panel groups used in motif testing.

Reason:
1. resolves the C4-vs-C12 ambiguity as a measurement problem,
2. prevents overclaiming geometric symmetry as kernel symmetry.

## 4. `speculative` Items to Track (Not Promotion Evidence)

1. Strong equivalence claims from E6/F4/McKay analogies.
2. "Guaranteed Lorentz emergence" from causal invariance analogies without direct confluence evidence.
3. Immediate mapping of one-node motifs to named SM particles.

Policy:
1. keep these as hypothesis generators,
2. require explicit tests before any RFC promotion language.

## 5. Immediate Backlog (Implementation Order)

1. Chirality panel upgrade:
   - add left-vs-right comparison output fields,
   - add associator-activity summary fields.
2. Lorentz panel hardening:
   - enforce non-saturated distance policy in runner configs,
   - persist directional fit and residual artifacts.
3. Seed bank upgrade:
   - emit seed strata manifest (`order`, `tier`, `family`) per batch.
4. Reporting:
   - add lane-separated leaderboards (`transport`, `detector`, `chirality`).

## 6. Non-Claims

This memo does not claim:
1. particle closure,
2. chirality closure,
3. Lorentz closure.

It defines only what is currently useful to test next.

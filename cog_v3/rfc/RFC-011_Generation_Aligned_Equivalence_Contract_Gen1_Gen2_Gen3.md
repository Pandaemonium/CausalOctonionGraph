# RFC-011: Generation-Aligned Equivalence Contract (Gen1/Gen2/Gen3)

Status: Draft
Date: 2026-03-03
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-004_Physics_Grounded_Kernel_Selection_Criteria.md`
- `cog_v3/rfc/RFC-009_S960_Phase_Fibered_E8_Symmetry_Model.md`
- `cog_v3/rfc/RFC-010_C12_Phase_Sector_Generation_and_Rare_Hop_Test_Contract.md`
- `sources/gen2_gen3_interactions_dm_de_lit_review_v2.md`

## 1. Purpose

Define a falsifiable contract for this hypothesis:
1. generation-aligned composites are dynamically equivalent in vacuum,
2. this equivalence holds until first interaction with a non-phase-synced external motif,
3. equivalence can be evaluated at `<1%` mismatch on registered observables.

This RFC is a test contract, not a closure claim.

## 2. Working generation map for this contract

Operational convention for current testing:
1. `C12` phase lane is primary.
2. Gen1 baseline phase label: `p`.
3. Gen2 label: `p+1 (mod 12)` (one tick advanced).
4. Gen3 label: `p+2 (mod 12)` (two ticks advanced).

Important caveat:
1. this RFC does not lock the microscopic operator class that implements `30/60` degree shifts.
2. operator-level mapping is deferred; dynamics-level predictions are tested first.

## 3. Primary comparison systems

## 3.1 Baseline pair (required)

1. System A: electron-like motif + `uud` triplet-like motif.
2. System B: muon-like motif + `ccs` triplet-like motif.

## 3.2 Offset-equivalence panels (required)

1. same-desync family examples (e.g., `tau + ccs` vs `mu + uud`) must also be tested.
2. equivalence claim applies whenever all interacting motifs are same-generation or equally desynced.

## 3.3 Scope boundary

1. claim is only for vacuum evolution and pre-mixing regime.
2. once a non-phase-synced interaction occurs, equivalence is no longer required by this contract.

## 4. Hypotheses

## H1 (vacuum equivalence)

For matched initialization and generation-aligned pairing:
1. registered dynamical observables for A and B agree within `<1%`.

## H2 (pre-mixing persistence)

Before first non-phase-synced interaction:
1. A/B equivalence remains within `<1%` over rolling windows.

## H3 (desync-transitivity)

If two systems are generation-aligned in relative offset:
1. dynamics are equivalent within `<1%` under matched conditions.

## 5. Null hypotheses

N1:
1. A/B observables differ by more than tolerance in vacuum.

N2:
1. apparent equivalence is seed- or boundary-fragile and collapses across reruns.

N3:
1. equivalence depends on absolute phase labels instead of relative generation alignment.

## 6. Registered observables (dimensionless-first)

For each system:
1. `T_cycle`: dominant recurrence period (ticks).
2. `R_hat`: normalized orbit radius (motif-core scaled).
3. `Omega_hat`: normalized angular advance per tick.
4. `S_stab`: stability score (post-transient recurrence fidelity).
5. `V_hat`: normalized centroid drift and variance in vacuum.
6. `H_phase`: phase-hop channel histogram summary (from RFC-010 metrics).

Pairwise mismatch for metric `m`:
1. `delta_m = |m_A - m_B| / max(|m_A|, |m_B|, epsilon)`.

Primary acceptance metric:
1. `Delta_max = max(delta_m over registered primary metrics)`.
2. Pass threshold: `Delta_max < 0.01`.

## 7. Test protocol

## 7.1 Initialization and replay

1. fixed seeded event order (deterministic replay).
2. matched vacuum background, box geometry, boundary condition, kernel profile.
3. matched transient ablation window before scoring.

## 7.2 Required panels

1. seed panel: at least 5 independent seeds.
2. geometry panel: at least 2 box scales.
3. boundary panel: fixed-vacuum baseline plus one robustness variant.
4. orientation panel: motif orientation permutations where applicable.

## 7.3 Pre-mixing window detector

1. define first non-phase-synced interaction event.
2. split scoring into:
   - `window_pre_mix`
   - `window_post_mix` (exploratory only)

Only `window_pre_mix` is contractual.

## 8. Promotion gates

## Gate 0 (integrity)

Must pass:
1. deterministic replay exactness.
2. metadata completeness.
3. no missing windows/metrics.

## Gate 1 (vacuum pair)

Pass if:
1. baseline pair (`e+uud` vs `mu+ccs`) has `Delta_max < 1%` in `window_pre_mix` across panel medians.

## Gate 2 (offset transitivity)

Pass if:
1. same-desync pairs satisfy `Delta_max < 1%` in `window_pre_mix`.

## Gate 3 (robustness)

Pass if:
1. equivalence survives required seed/scale/orientation panels.
2. no single panel dominates failure mode.

## 9. Falsifiers

The contract is rejected if any of the following persist:
1. baseline A/B mismatch exceeds `<1%` in pre-mixing windows.
2. equivalence fails under same-desync transitivity tests.
3. results are not reproducible across seed/scale panels.
4. equivalence requires fine-tuned absolute phase labels (instead of relative alignment).

## 10. What this RFC does not claim

1. It does not claim exact operator-level derivation for all `30/60` degree phase mechanisms.
2. It does not claim SM already predicts this equivalence.
3. It does not claim direct DM/DE resolution.

## 11. Relation to external physics (from literature)

From `sources/gen2_gen3_interactions_dm_de_lit_review_v2.md`:
1. SM does not assert generation-identical dynamics in physical units because masses/mixing differ.
2. Gen2/Gen3 sectors are precision constrained but not known as direct DM/DE explanation.
3. Therefore this RFC is a strong beyond-SM/discrete-dynamics test lane and should be judged by explicit falsification performance.

## 12. Artifact contract

Planned scripts:
1. `cog_v3/calc/build_v3_generation_aligned_equivalence_panel_v1.py`
2. `cog_v3/calc/test_v3_generation_aligned_equivalence_panel_v1.py`

Planned outputs:
1. `cog_v3/sources/v3_generation_aligned_equivalence_panel_v1.json`
2. `cog_v3/sources/v3_generation_aligned_equivalence_panel_v1.csv`
3. `cog_v3/sources/v3_generation_aligned_equivalence_panel_v1.md`

Required output fields:
1. `kernel_profile`
2. `convention_id`
3. `stencil_id`
4. `seed_id`
5. `system_id`
6. `generation_offset_signature`
7. `window_id`
8. `T_cycle`
9. `R_hat`
10. `Omega_hat`
11. `S_stab`
12. `V_hat`
13. `H_phase_summary`
14. `Delta_max_pair`
15. `pass_flag_lt_1pct`

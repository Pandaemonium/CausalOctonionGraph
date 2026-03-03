# RFC-010: C12 Phase-Sector Generation and Rare-Hop Mixing Contract

Status: Draft
Date: 2026-03-02
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-004_Physics_Grounded_Kernel_Selection_Criteria.md`
- `cog_v3/rfc/RFC-009_S960_Phase_Fibered_E8_Symmetry_Model.md`
- `sources/c12_phase_sector_generation_lit_review_v1.md`
- `cog_v3/sources/v3_c12_singlet_doublet_clock_shift_sparse_v1.csv.gz`
- `cog_v3/sources/v3_c12_clock_meta_v1.csv`

## 1. Purpose

Define a falsifiable test contract for the hypothesis:
1. In the `C12` phase lane, most physically relevant updates are `Delta p = +/-3` (90 degrees).
2. Rare updates `Delta p = +/-1, +/-2` are sector-mixing channels.
3. Three generation-like sectors may emerge as `g = p mod 3`.

This RFC is a test contract, not a claim of closure.

## 2. Why this is worth testing

Literature-aligned mechanism classes support this style of dynamics:
1. discrete flavor sectors with restricted mixing channels,
2. clock/anisotropy systems with dominant lock steps and rare slips,
3. hierarchical couplings from weak inter-step transfer channels.

See: `sources/c12_phase_sector_generation_lit_review_v1.md`.

## 3. Definitions

1. Phase index: `p in Z12`.
2. Phase hop for an event: `Delta p = p_next - p_prev (mod 12)`.
3. Generation-sector label: `g = p mod 3`.
4. Sector-preserving event: `Delta p mod 3 = 0`.
5. Sector-mixing event: `Delta p mod 3 != 0`.
6. Dominant channels (hypothesis): `Delta p in {+3, -3}`.
7. Rare channels (hypothesis): `Delta p in {+1,-1,+2,-2}`.

## 4. Hypotheses

## H1 (primary)

1. In stable or near-stable motif regimes, `P(Delta p in {+3,-3})` dominates over all other nonzero channels.
2. `g = p mod 3` is approximately conserved over long windows, broken primarily by rare channels.

## H2 (mixing structure)

1. Inter-sector transition matrix `T_ij` is sparse and generated mainly by `Delta p = +/-1, +/-2`.
2. Distinct motif classes can show distinct `T_ij` patterns (candidate analog for differing flavor sectors).

## H3 (chirality/CP proxy)

1. Asymmetry in signed rare hops (`+1` vs `-1`, `+2` vs `-2`) can be nonzero and stable under replay.

## 5. Null models

N0:
1. Hop channel usage is near-uniform after controlling for occupancy.

N1:
1. `g = p mod 3` shows no meaningful conservation in relevant windows.

N2:
1. Rare-hop asymmetries are consistent with noise under replay and panel tests.

## 6. Metrics

## 6.1 Channel dominance

1. `R3 = P(|Delta p| = 3) / P(|Delta p| in {1,2,4,5,6})`.
2. Track globally and by motif class.

## 6.2 Sector conservation

1. `C3 = P(Delta p mod 3 = 0)`.
2. `L3`: mean run length in same `g` sector before sector change.

## 6.3 Rare-hop transition matrix

1. Estimate `T_ij = P(g_t+1 = j | g_t = i, sector-mixing event)` for `i,j in {0,1,2}`.
2. Report confidence intervals (bootstrap).

## 6.4 Signed asymmetry

1. `A1 = (N_{+1} - N_{-1}) / (N_{+1} + N_{-1})`.
2. `A2 = (N_{+2} - N_{-2}) / (N_{+2} + N_{-2})`.

## 6.5 Robustness panel metrics

Repeat all above under:
1. orientation panels,
2. boundary panels,
3. seeded event-order panels.

## 7. Promotion gates

## Gate 0: Data integrity

Must pass:
1. deterministic replay,
2. complete metadata,
3. channel histogram consistency checks.

## Gate 1: Dominance evidence

Pass if:
1. `R3` exceeds threshold in at least two independent motif strata,
2. effect persists across panel reruns.

Initial threshold (exploratory):
1. `R3 >= 2.0` provisional,
2. `R3 >= 4.0` strong.

## Gate 2: Sector conservation evidence

Pass if:
1. `C3` significantly above shuffled null,
2. `L3` significantly above matched random baseline.

## Gate 3: Rare-hop mixing structure

Pass if:
1. `T_ij` is sparse/non-uniform with reproducible structure,
2. structure survives panel perturbations.

## Gate 4: Signed asymmetry stability

Pass if:
1. `A1` or `A2` nonzero beyond uncertainty and stable in sign,
2. not explained by boundary/orientation artifact.

## 8. Falsifiers

This hypothesis is rejected if any of the following hold persistently:
1. `R3` near 1 after occupancy controls,
2. `C3` indistinguishable from null across stable motif windows,
3. `T_ij` near uniform under rare-hop conditioning,
4. signed asymmetries collapse under replay/panel tests.

## 9. Key cautions

1. Absolute phase labels may be gauge-like; interpret results with relative/internal structure controls.
2. Sector findings are not automatically particle-generation findings.
3. Even if H1-H3 pass, anomaly-consistency and low-energy universality constraints remain required for physical promotion.

## 10. Implementation plan

## Phase A (fast)

1. Add event-level `Delta p` logging to motif runs.
2. Build channel histograms and compute `R3`, `C3`, `L3`.
3. Run null-shuffle controls.

## Phase B (mixing)

1. Estimate `T_ij` from rare-hop events.
2. Compute `A1`, `A2` and confidence intervals.
3. Run panel robustness battery.

## Phase C (integration)

1. Feed passing candidates into RFC-004 kernel selection lanes.
2. Tag candidates as:
   - `phase_sector_supported`,
   - `phase_sector_inconclusive`,
   - `phase_sector_rejected`.

## 11. Deliverables

1. `cog_v3/sources/v3_c12_phase_hop_histograms_v1.csv`
2. `cog_v3/sources/v3_c12_phase_sector_metrics_v1.json`
3. `cog_v3/sources/v3_c12_phase_sector_metrics_v1.md`
4. `cog_v3/sources/v3_c12_phase_sector_transition_matrix_v1.csv`
5. `cog_v3/sources/v3_c12_phase_sector_panel_report_v1.md`

## 12. References

Literature basis is documented in:
1. `sources/c12_phase_sector_generation_lit_review_v1.md`

Selected core references:
1. Ishimori et al. (2010), discrete symmetries in particle physics: https://doi.org/10.1143/PTPS.183.1
2. Altarelli and Feruglio (2010), discrete flavor review: https://doi.org/10.1103/RevModPhys.82.2701
3. King and Luhn (2013), neutrino/discrete symmetry review: https://doi.org/10.1088/0034-4885/76/5/056201
4. Jose et al. (1977), planar model + symmetry-breaking perturbations: https://doi.org/10.1103/PhysRevB.16.1217
5. Lapilli et al. (2006), six-state clock BKT transitions: https://doi.org/10.1088/0305-4470/39/12/006
6. Ueno et al. (2020), RG flows in 3D clock models: https://doi.org/10.1103/PhysRevLett.124.080602
7. Lou et al. (2021), U(1)-to-Z_q crossover: https://doi.org/10.1103/PhysRevB.103.054418
8. Krauss and Wilczek (1989), discrete gauge symmetry: https://doi.org/10.1103/PhysRevLett.62.1221
9. Banks and Dine (1991), discrete gauge anomalies: https://doi.org/10.1016/0370-2693(91)91614-2
10. Giudice and McCullough (2017), clockwork theory: https://doi.org/10.1007/JHEP02(2017)036

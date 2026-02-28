# RFC-004: Triplet Coherence and e000 Leakage Hypothesis (v1)

Status: Active  
Date: 2026-02-28  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-003_Theta_Continuum_Identification_Contract.md`

## 1. Purpose

Formalize a falsifiable hypothesis:

1. 3-cycle coherent motifs retain higher triplet coherence.
2. Off-cycle motifs leak more strongly into `e000`.
3. Off-cycle motifs reduce terminal non-`e000` mass proxy and transport proxy.

This RFC defines structure-first observables and test lanes only.
Leakage is explicitly modeled as a discrete distance-indexed ladder over graph depth.

## 2. Observables (normative IDs)

1. `C_t`: triplet coherence score  
   - mean triplet occupancy fraction over source/mediator/terminal nodes.
2. `M_t`: terminal non-`e000` mass proxy  
   - sum `abs2` over channels `1..7` at terminal node.
3. `E_t`: terminal `e000` share  
   - `abs2(e000) / (abs2(e000) + non_e000_power)`.
4. `L_t`: terminal leakage increment  
   - tick-wise increment of terminal `e000` power.
5. `T_t`: terminal transport proxy  
   - target power `(4..6)` divided by `(source(1..3) + target(4..6))`.
6. `D_t`: discrete graph-distance index  
   - integer tick depth from initial state (`D_t in N`).
7. `L_d`: distance-indexed leakage ladder  
   - leakage value at integer distance `d`.

## 3. Preregistered Probe Contract

Artifact builder:
- `cog_v2/calc/build_triplet_coherence_e000_leakage_v1.py`

Artifacts:
- `cog_v2/sources/triplet_coherence_e000_leakage_v1.json`
- `cog_v2/sources/triplet_coherence_e000_leakage_v1.md`
- `cog_v2/sources/triplet_coherence_e000_robustness_v1.json`
- `cog_v2/sources/triplet_coherence_e000_robustness_v1.md`

Scenarios:
1. `coherent_triplet_v1`
2. `broken_off_cycle_v1`

Ticks:
1. fixed at 120

Distance domain:
1. `d` is an integer axis (`0..119`) with contiguous bins.
2. No continuous interpolation is used for acceptance checks.

## 4. Directional Checks

Expected inequalities:

1. `mean_C_t(coherent) > mean_C_t(broken)`
2. `mean_E_t(broken) > mean_E_t(coherent)`
3. `positive_L_t_fraction(broken) > positive_L_t_fraction(coherent)`
4. `mean_M_t(broken) < mean_M_t(coherent)`
5. `mean_T_t(broken) < mean_T_t(coherent)`
6. distance axis is discrete and contiguous from zero.
7. broken-state tail-window mean absolute leakage is higher than coherent-state tail-window leakage.
8. distance-wise non-strict absolute-leakage dominance holds for broken state on a majority of bins.

## 5. Falsification Condition

Hypothesis is falsified if one or more directional checks fail under the
preregistered scenarios and canonical kernel profile.

Bridge implication:
1. This RFC supports bridge isolation by constraining leakage behavior on a discrete depth lattice.
2. It does not by itself select the continuum theta map shape.
3. Any continuum bridge policy should treat leakage corrections as depth-binned (`d in N`) quantities before any coarse-grain summary.

## 6. Non-Goals

This RFC does not:

1. claim continuum EFT closure,
2. claim full quark mass derivation,
3. replace THETA-001 bridge contracts.

## 7. Robustness Lane (v1)

Robustness sweep artifact:
1. `cog_v2/calc/build_triplet_coherence_e000_robustness_v1.py`
2. scenario family: 4 coherent/broken deterministic pairs
3. topology coverage: at least 2 parent-topology families

Acceptance semantics:
1. critical checks must pass for all pairs,
2. supporting checks must pass for a majority of pairs,
3. robustness envelope must retain:
   - coherent near-field first-order dominance,
   - coherent far-field higher-order growth over near-field,
   - `topology_family_count >= 2`,
   - `robustness_lane_ready = true`.

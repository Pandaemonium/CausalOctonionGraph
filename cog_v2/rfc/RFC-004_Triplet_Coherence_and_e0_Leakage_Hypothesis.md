# RFC-004: Triplet Coherence and e0 Leakage Hypothesis (v1)

Status: Active  
Date: 2026-02-28  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-003_Theta_Continuum_Identification_Contract.md`

## 1. Purpose

Formalize a falsifiable hypothesis:

1. 3-cycle coherent motifs retain higher triplet coherence.
2. Off-cycle motifs leak more strongly into `e0`.
3. Off-cycle motifs reduce terminal non-`e0` mass proxy and transport proxy.

This RFC defines structure-first observables and test lanes only.

## 2. Observables (normative IDs)

1. `C_t`: triplet coherence score  
   - mean triplet occupancy fraction over source/mediator/terminal nodes.
2. `M_t`: terminal non-`e0` mass proxy  
   - sum `abs2` over channels `1..7` at terminal node.
3. `E_t`: terminal `e0` share  
   - `abs2(e0) / (abs2(e0) + non_e0_power)`.
4. `L_t`: terminal leakage increment  
   - tick-wise increment of terminal `e0` power.
5. `T_t`: terminal transport proxy  
   - target power `(4..6)` divided by `(source(1..3) + target(4..6))`.

## 3. Preregistered Probe Contract

Artifact builder:
- `cog_v2/calc/build_triplet_coherence_e0_leakage_v1.py`

Artifacts:
- `cog_v2/sources/triplet_coherence_e0_leakage_v1.json`
- `cog_v2/sources/triplet_coherence_e0_leakage_v1.md`

Scenarios:
1. `coherent_triplet_v1`
2. `broken_off_cycle_v1`

Ticks:
1. fixed at 120

## 4. Directional Checks

Expected inequalities:

1. `mean_C_t(coherent) > mean_C_t(broken)`
2. `mean_E_t(broken) > mean_E_t(coherent)`
3. `positive_L_t_fraction(broken) > positive_L_t_fraction(coherent)`
4. `mean_M_t(broken) < mean_M_t(coherent)`
5. `mean_T_t(broken) < mean_T_t(coherent)`

## 5. Falsification Condition

Hypothesis is falsified if one or more directional checks fail under the
preregistered scenarios and canonical kernel profile.

## 6. Non-Goals

This RFC does not:

1. claim continuum EFT closure,
2. claim full quark mass derivation,
3. replace THETA-001 bridge contracts.

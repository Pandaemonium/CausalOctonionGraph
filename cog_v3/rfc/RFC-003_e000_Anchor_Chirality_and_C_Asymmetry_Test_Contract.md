# RFC-003: e000 Anchor, Chirality, and C-Asymmetry Test Contract

Status: Draft  
Date: 2026-03-02  
Owner: COG Core  
Depends on:
- `cog_v3/rfc/RFC-001_Ideal_Structure_and_Stable_Motif_Search_in_Octavian240_SharedPhase.md`
- `cog_v3/rfc/RFC-002_Seeded_Event_Order_FailFast_and_Photon_Chirality_Hypotheses.md`
- `cog_v3/python/kernel_octavian240_multiplicative_v1.py`

## 1. Purpose

Formalize and test the hypothesis that:

1. `e000` acts as a stability anchor in v3 dynamics,
2. chirality is parity-odd motif structure (not just axis polarity),
3. matter/antimatter differences, if present, appear as robustness-basin asymmetry
   under perturbations rather than intrinsic antimatter instability.

This RFC defines observables and falsification tests.

## 2. Non-Claims

This RFC does not claim:

1. antimatter is fundamentally unstable,
2. baryon asymmetry is already explained,
3. weak chirality is solved,
4. one-front photon wave occupancy is required.

It only defines what must be measured to support or reject these claims.

## 3. Algebraic Baseline Facts (v3)

Using current convention:

1. `e111 * e111 = -e000` (verified from kernel table),
2. repeated left multiplication by `e111` yields a 4-cycle on signs:
   `e000 -> e111 -> -e000 -> -e111 -> e000`.

Consequence:

1. `e111`-driven behavior is not a simple 2-state flip,
2. sign and phase structure must be tracked explicitly.

## 4. Refined Hypothesis

### 4.1 e000 Anchor

`e000` occupancy and return frequency are proxies for local stability/relaxation.

### 4.2 Chirality

Chirality is defined by parity-odd motif orientation or winding and must flip under
spatial mirror transform `P`.

### 4.3 C-Asymmetry

Any matter/antimatter preference should appear as:

1. different perturbation robustness basins for `M` versus `C(M)`,
2. not as immediate decay of all `C(M)` motifs.

## 5. Required Transform Definitions

### 5.1 Parity Transform `P`

`P` mirrors lattice geometry about a fixed axis/plane, preserving value alphabet.

### 5.2 Charge Conjugation Transform `C`

`C` maps each voxel value `(phase, q)` to conjugated value:

1. phase inversion (`i <-> -i`, equivalent to negating phase index mod 4),
2. octonion conjugation on `q` (sign inversion on imaginary components in basis form).

Implementation detail:

1. `C` must be deterministic and convention-id aware.

### 5.3 CP Transform

`CP(M) := C(P(M))`.

## 6. Observables

For each run and motif:

1. `f_e000(t)`:
   fraction of active support voxels whose `q` component is `e000`,
2. `R_e000`:
   return rate to `e000` over a fixed window,
3. `tau_survive`:
   survival horizon before fail-fast decay or run end,
4. `S_recur`:
   recurrence score (periodicity confidence),
5. `D_prop`:
   directional coherence score for propagating motifs,
6. `A_chi`:
   chirality asymmetry in matched interaction panels:
   `A_chi = (R(M) - R(P(M))) / (R(M) + R(P(M)))`,
7. `A_C`:
   conjugation robustness asymmetry:
   `A_C = (Q(M) - Q(C(M))) / (Q(M) + Q(C(M)))`,
   where `Q` is chosen quality metric (for example survival or recurrence),
8. `detector_exclusivity` (control metric):
   `1 - double_hit_rate` in twin-detector photon/control panels.

## 7. Test Matrix

### 7.1 Mirror Chirality Test

1. run matched panels for `M` and `P(M)`,
2. compute `A_chi`,
3. require sign consistency across reruns.

### 7.2 Conjugation Robustness Test

1. run matched panels for `M` and `C(M)`,
2. compute `A_C`,
3. distinguish small stochastic drift from persistent asymmetry.

### 7.3 CP Test

1. compare `M` and `CP(M)` statistics,
2. quantify any CP-odd residual.

### 7.4 Convention Invariance Test

1. rerun in at least one alternate valid convention mapping,
2. require qualitative conclusions to remain invariant.

### 7.5 Wave vs Detection Control

1. run chirality panels with explicit logging of wave-layer front class (`one_front_dominant` or `two_front_balanced`),
2. require chirality conclusions to be reported conditionally on detector exclusivity,
3. reject claims that depend only on front topology without detection-layer asymmetry support.

## 8. Provisional Decision Thresholds

Exploratory thresholds (can be tightened later):

1. effect floor:
   `|A_chi| >= 0.05` or `|A_C| >= 0.05`,
2. consistency:
   same effect sign across at least 3 independent reruns,
3. confidence:
   bootstrap 95 percent interval excludes zero.

Failure to meet these is "no evidence yet", not immediate disproof.

## 9. Falsification Conditions

This hypothesis lane is falsified if all hold:

1. `A_chi` remains statistically indistinguishable from zero across tested motifs,
2. `A_C` remains statistically indistinguishable from zero across tested motifs,
3. observed effects are not convention-invariant.

## 10. Artifact Contract

Planned scripts:

1. `cog_v3/calc/build_v3_chirality_conjugation_tests_v1.py`
2. `cog_v3/calc/test_v3_chirality_conjugation_tests_v1.py`

Planned outputs:

1. `cog_v3/sources/v3_chirality_conjugation_tests_v1.json`
2. `cog_v3/sources/v3_chirality_conjugation_tests_v1.md`

Required metadata:

1. `kernel_profile`
2. `convention_id`
3. `event_order_policy`
4. `seed_set_id`
5. `transform_definitions_hash`
6. `replay_hash`

## 11. Immediate Execution Steps

1. implement deterministic `P`, `C`, and `CP` transforms for voxel motifs,
2. run first panel on top candidates from RFC-002 search lane,
3. publish `A_chi`, `A_C`, and CP residual summaries,
4. decide whether to keep or drop the e000-anchor asymmetry hypothesis.

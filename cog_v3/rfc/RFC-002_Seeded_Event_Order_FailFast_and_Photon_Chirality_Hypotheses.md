# RFC-002: Seeded Event Order, Fail-Fast Search, and Photon/Chirality Hypothesis Lane

Status: Draft  
Date: 2026-03-02  
Owner: COG Core  
Depends on:
- `cog_v3/rfc/RFC-001_Ideal_Structure_and_Stable_Motif_Search_in_Octavian240_SharedPhase.md`
- `cog_v3/rfc/CONVENTION_IDS.md`
- `cog_v3/python/kernel_octavian240_multiplicative_v1.py`

## 1. Purpose

Lock an exploratory search policy for v3 that prioritizes throughput:

1. deterministic seeded-random event order (single timeline),
2. no multi-fold robustness ensemble during exploratory scans,
3. fail-fast execution for clearly decaying motifs,
4. explicit hypothesis lane for photon morphology and chirality emergence.

This RFC is an operational search policy, not a closure claim.

## 2. Policy Decisions

### 2.1 Event Order

Event order is not lexicographic. It is seeded-random and reproducible.

### 2.2 Timeline Mode

Use one fixed seed per run campaign (single-timeline lane).

### 2.3 Robustness Assumption (Exploratory)

Assume that motifs stable over long horizons are effectively fold-order robust.
Do not spend compute on fold-order ensembles during early search.

### 2.4 Fail-Fast

Abort runs early when decay is strongly indicated, while saving restartable state.

## 3. Deterministic Seeded-Random Event Order

For each tick:

1. derive `tick_seed = H(global_seed, scenario_id, tick_index)`,
2. instantiate PRNG from `tick_seed`,
3. run Fisher-Yates shuffle over node list to obtain `event_order_t`.

Requirements:

1. same inputs produce identical event orders,
2. no dependence on process scheduling or thread timing,
3. all seeds and hash methods are recorded in artifacts.

Required metadata:

1. `event_order_policy = seeded_random_per_tick_v1`,
2. `global_seed`,
3. `scenario_id`,
4. `hash_id`,
5. `prng_id`.

## 4. Single-Seed Exploratory Lane

### 4.1 Rationale

Compute budget is better spent on breadth of motifs and horizon length than
on immediate fold-order ensembles.

### 4.2 Override to RFC-001

For exploratory scans only, RFC-001 fold-order cross-check requirements are deferred.

### 4.3 Escalation Trigger

If a candidate reaches promotion threshold, then run a targeted robustness check
before any "supported" status:

1. one alternate `global_seed`,
2. one alternate box size.

This is the minimum escalation gate.

## 5. Fail-Fast Contract

### 5.1 Decay Signals

A run is considered decaying when all hold over configured windows:

1. non-vacuum support shrinks below `support_floor`,
2. recurrence score remains below `recurrence_floor`,
3. displacement coherence remains below `direction_floor`.

### 5.2 Early Abort

If decay signals persist for `W_abort` consecutive windows:

1. terminate run,
2. save full checkpoint,
3. emit abort reason and metrics.

### 5.3 Resume Support

Checkpoint must include:

1. lattice state snapshot,
2. tick index,
3. seed and event-order metadata,
4. motif descriptor and run params.

## 6. Stability Confirmation Policy

Two allowed run modes:

1. `fixed_horizon`: always run `T_max` ticks,
2. `adaptive_horizon`: stop after `N_confirm` repeated cycles with stable metrics.

Default for expensive scans: `fixed_horizon + fail_fast`.

## 7. Photon Hypothesis Lane

### 7.1 Working Hypothesis

Model split:

1. `subphoton`: minimal voxel-scale imaginary-phase rotator,
2. `superphoton`: coherent packet of many subphotons with net direction.

Vacuum may have seeded-random phase texture; packet shape can fluctuate locally but
retain coarse volume and directional coherence.

Important clarification:

1. two-front wave-layer propagation is allowed and is not, by itself, a rejection condition,
2. "single photon" behavior is evaluated at the detection layer (event outcomes), not by requiring one-front wave occupancy.

### 7.2 Direction/Orientation Hypothesis

Propagation direction is hypothesized to require an "orientator" component in `Q240`
coupled to phase rotation in `C4`.

Search object:

1. pairs `(rotator_phase, orientator_q)` or small packets built from them,
2. evaluated by directional coherence and packet persistence.

### 7.3 Photon Candidate Metrics

1. `v_group`: packet centroid speed,
2. `coh_dir`: directional coherence (unit-vector concentration),
3. `vol_stab`: variance of active support volume over time,
4. `scatter_rate`: disruption under seeded random vacuum phase,
5. `front_balance`: balance between opposite-going wavefront occupancy,
6. `double_hit_rate`: fraction of runs where opposite detectors both absorb in the same trial,
7. `detector_exclusivity`: `1 - double_hit_rate`.

Target profile:

1. high `v_group`,
2. high `coh_dir`,
3. bounded `vol_stab`,
4. low `scatter_rate`,
5. high `detector_exclusivity` in twin-detector panels.

### 7.4 Two-Front Interpretation Guardrails

Do not conflate wave occupancy with detection outcomes.

Required reporting for photon-like candidates:

1. wave-layer transport class:
   - `one_front_dominant`,
   - `two_front_balanced`,
   - `diffuse_nonpropagating`,
2. detection-layer exclusivity under absorbing opposite detectors,
3. whether directional claims depend on detector geometry or boundary choice.

Promotion implication:

1. `two_front_balanced` candidates may still be promoted if detection-layer exclusivity is high and propagation coherence remains robust.

## 8. Chirality and Left-Handed Interaction Hypothesis

### 8.1 Intuition

Chirality should appear as parity-odd response asymmetry between motif and mirror motif
in interaction outcomes, not as an arbitrary runtime flag.

### 8.2 Operational Test

For each motif `M` and mirrored motif `P(M)`:

1. run matched collision panels against identical target sets,
2. compare interaction rates and outcome classes.

Define:

`A_chi = (R(M) - R(P(M))) / (R(M) + R(P(M)))`

where `R` is a chosen interaction-response rate (for example absorption, conversion,
or scattering into non-vacuum support classes).

Weak-like left-handed behavior requires persistent nonzero `A_chi` with sign stability
across reruns.

## 9. Search Strategy (Executable)

1. run singleton `S960` census (already available),
2. build reduced seed alphabets by period classes,
3. run 3D seeded-random motif scans with fail-fast,
4. rank candidates by recurrence, propagation, and support stability,
5. evaluate photon lane metrics on top candidates,
6. run twin-detector exclusivity panels on photon finalists,
7. run chirality mirror tests on finalists.

## 10. Artifact Contract

Planned script lane:

1. `cog_v3/calc/build_v3_seeded_order_motif_scan_v1.py`
2. `cog_v3/calc/test_v3_seeded_order_motif_scan_v1.py`

Planned outputs:

1. `cog_v3/sources/v3_seeded_order_motif_scan_v1.json`
2. `cog_v3/sources/v3_seeded_order_motif_scan_v1.md`

Required fields:

1. `kernel_profile`
2. `convention_id`
3. `event_order_policy`
4. `global_seed`
5. `scenario_id`
6. `fail_fast_enabled`
7. `abort_reason` (if aborted)
8. `front_balance`
9. `double_hit_rate`
10. `detector_exclusivity`
11. `replay_hash`

## 11. Risks

1. single-seed assumption can hide fold-order-sensitive false positives,
2. fail-fast can prematurely abort motifs with long transients,
3. seeded random vacuum phases can introduce search bias if seed families are too narrow,
4. wave-layer two-front behavior can be misread as nonphysical if detection layer is not instrumented.

Mitigations:

1. mandatory escalation check on promoted candidates,
2. checkpoint-and-resume for any fail-fast abort,
3. periodic seed-rotation audits for top motif classes,
4. mandatory twin-detector panels before rejecting two-front candidates.

## 12. Falsification Conditions

This policy lane is considered inadequate if:

1. promoted candidates fail minimal escalation checks,
2. photon candidate metrics cannot be stabilized under seeded-random vacuum backgrounds,
3. chirality asymmetry disappears under small rerun perturbations.

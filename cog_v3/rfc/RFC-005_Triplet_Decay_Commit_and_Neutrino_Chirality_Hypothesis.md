# RFC-005: Triplet Decay Commit and Neutrino Chirality Hypothesis

Status: Draft  
Date: 2026-03-02  
Owner: COG Core  
Depends on:
- `cog_v3/rfc/RFC-001_Ideal_Structure_and_Stable_Motif_Search_in_Octavian240_SharedPhase.md`
- `cog_v3/rfc/RFC-003_e000_Anchor_Chirality_and_C_Asymmetry_Test_Contract.md`
- `cog_v3/rfc/RFC-004_Physics_Grounded_Kernel_Selection_Criteria.md`

## 1. Purpose

Capture and formalize the working intuition for beta-decay-like transitions in COG v3:

1. triplet motifs have internal oriented dynamics,
2. a decaying `d` leg enters a transient that can either roll back or convert,
3. a neutrino-like chiral branch may be the commit signal that forces `d -> u`,
4. weak-handedness may emerge from this commit geometry.

This RFC is a hypothesis/test contract, not a closure claim.

## 2. Intuition to Preserve

### 2.1 Core picture

For a neutron-like `udd` motif under perturbation:

1. one `d` leg is perturbed out of stable resonance,
2. that leg becomes a transient (`d*`) with two competing futures,
3. if conversion support arrives fast enough, `d*` commits to proto-`u`,
4. if not, surrounding `u,d` partners pull `d*` back into a stable `d`,
5. emitted lepton branch (`e^- + anti-nu_e`-like channel) is part of the same event family.

### 2.2 Handedness intuition

The neutrino-like branch is hypothesized to be directional/chiral:

1. it "kicks" commit in one oriented sense,
2. that orientation biases conversion success,
3. parity mirror should flip the success bias sign.

### 2.3 e000 anchor compatibility

The mechanism should remain compatible with the `e000` anchor concept:

1. conversion occurs in a stability landscape with an `e000`-coupled basin,
2. handed commit is local and event-resolved, not an ad hoc external term.

## 3. Known Constraints (to prevent overreach)

From Standard Model usage constraints:

1. the two `d` quarks in `udd` are identical and not classically labelable as
   "ahead of u" vs "behind u",
2. weak charged-current acts on the full quantum state, not a trackable tagged quark,
3. any site-selected decay claim is therefore beyond-SM and must be treated as a new prediction.

From current COG status constraints:

1. handedness is not yet locked in kernel closure,
2. neutrino motif is not yet established as a supported stable propagator,
3. no claim is allowed yet that only one fixed `d` site decays.

## 4. Operational Model (COG language)

Define decay as a two-timescale competition:

1. rollback timescale `tau_relock`: time for `d*` to re-enter original triplet lock,
2. commit timescale `tau_bridge`: time for conversion branch to stabilize proto-`u`.

Decision rule (hypothesis):

1. if `tau_bridge < tau_relock`, conversion branch wins (`d -> u` event),
2. if `tau_bridge >= tau_relock`, rollback wins (no decay completion).

Handedness extension (hypothesis):

1. `tau_bridge` is parity-sensitive,
2. mirror transform changes success probability and/or sign of chirality asymmetry.

## 5. Questions This RFC Answers

### 5.1 "Does this explain neutrino chirality?"

Potentially yes, but only if:

1. kernel contains an explicit parity-odd commit mechanism,
2. mirror panels show stable nonzero asymmetry,
3. asymmetry survives seed variation and moderate box scaling.

### 5.2 "Do all `uud` or `udd` triplets have one chirality?"

Not assumed.

1. same-type triplets can have opposite helicity/spin states,
2. enantiomer bias must be measured, not presumed,
3. parity-symmetric kernels should permit both; parity-biased kernels can favor one.

### 5.3 "Which `d` decays?"

In SM framing, this is not a labeled-particle question.
In COG motif framing, a local leg can appear selected, but that must be treated as a
new testable prediction, not imported SM fact.

## 6. Test Matrix

### 6.1 Commit-vs-Rollback panel

1. construct `udd`-like motif family with controlled perturbation amplitude,
2. estimate `tau_bridge`, `tau_relock` from event logs,
3. check conversion probability versus `tau_bridge - tau_relock`.

Expected support signature:

1. threshold-like crossover in conversion success.

### 6.2 Mirror chirality panel

1. run motif `M` and parity mirror `P(M)` under matched seeds and perturbations,
2. compute `A_commit = (p_commit(M)-p_commit(P(M))) / (p_commit(M)+p_commit(P(M)))`.

Expected support signature:

1. nonzero, sign-stable `A_commit`.

### 6.3 Conjugation panel

1. run `M` vs `C(M)` and evaluate conversion/rollback asymmetry.

Expected support signature:

1. measurable but bounded matter/antimatter robustness asymmetry,
2. no universal immediate instability of all conjugate motifs.

### 6.4 Site-selection panel (exploratory)

1. define internal leg labels in motif coordinates only for logging,
2. test whether one labeled leg has persistent higher commit probability.

Interpretation rule:

1. if observed, classify as COG-specific beyond-SM prediction candidate,
2. do not reinterpret as contradiction of identical-fermion SM statement without
   measurement bridge specification.

## 7. Falsification Criteria

This hypothesis lane is weakened or falsified if:

1. `tau_bridge` vs `tau_relock` has no predictive relation to outcomes,
2. mirror panel asymmetry collapses to zero within uncertainty across reruns,
3. any observed asymmetry flips randomly with seed and fails robustness tests,
4. effects vanish under minor scale or convention checks.

## 8. Non-Claims

This RFC does not claim:

1. full weak interaction closure is solved,
2. baryogenesis is solved,
3. all chirality phenomena are reduced to one mechanism,
4. SM has identifiable "front" and "back" quark decay labels.

## 9. Artifact Contract

Planned scripts:

1. `cog_v3/calc/build_v3_triplet_decay_commit_panel_v1.py`
2. `cog_v3/calc/test_v3_triplet_decay_commit_panel_v1.py`

Planned outputs:

1. `cog_v3/sources/v3_triplet_decay_commit_panel_v1.json`
2. `cog_v3/sources/v3_triplet_decay_commit_panel_v1.md`

Required fields:

1. `kernel_profile`
2. `convention_id`
3. `stencil_id`
4. `event_order_policy`
5. `seed_id`
6. `tau_bridge`
7. `tau_relock`
8. `commit_probability`
9. `A_commit`
10. `A_C`

## 10. Immediate Next Steps

1. implement operational estimators for `tau_bridge` and `tau_relock`,
2. run commit-vs-rollback threshold sweeps,
3. execute mirror/conjugation panels with confidence intervals,
4. decide whether to promote this lane into kernel-selection gating.

# RFC-023: Discrete Phase Clocks and Relative-Phase Interactions

**Status:** Active - Hypothesis and Research Design Draft (2026-02-26)  
**Module:** `COG.Core.PhaseClock`, `COG.Core.RelativePhase`  
**Depends on:** `rfc/CONVENTIONS.md`, `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`, `rfc/RFC-019_e7_Temporal_Axis_Vacuum_Photon_Duality.md`, `rfc/RFC-020_Kernel_Representation_Reconciliation.md`, `rfc/RFC-021_Entanglement_Interaction_and_Causal_Projection.md`, `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`  
**Literature basis:** `sources/discrete_phase_internal_clock_lit_review.md`

---

## 1. Executive Summary

This RFC formalizes a new COG hypothesis:

1. The proved period-4 e7 action induces a discrete local phase class (`Z4`) for each state trajectory under temporal commit.
2. Relative phase between interacting subsystems may modulate interaction channels and costs.
3. Lack of phase-reference information can create observer-level uncertainty even in a deterministic microstate evolution.
4. Composite subsystems may exhibit cycle lengths greater than 4, despite single-e7 period-4 structure.

This RFC explicitly rejects one over-claim:

- uncertainty/entropy about phase does not itself create physical energy.

---

## 2. Internal Evidence Already Established

From current Lean record:

1. `e7` left and right actions have exact period 4 for all nonzero states (`universal_Ce_period_four`, `universal_Ce_right_period_four` in `Spinors.lean`).
2. Vacuum orbit is explicit and phase-like under e7 action (`e7Left_on_omegaDoubled`, `e7Right_on_omegaDoubled`).
3. Vacuum orbit stays in `{e0,e7}` and avoids color sector in the proved photon-masslessness stack (`PhotonMasslessness.lean`).
4. Time architecture already separates topological and interaction clocks (`tau_topo`, `tau_int`) in RFC-018.

Therefore, adding a derived `Z4` phase observable is compatible with existing foundations.

---

## 3. Hypothesis Triage

### H1. Every subsystem has a discrete 4-phase under temporal commit.

**Verdict:** adopt as a COG hypothesis strongly motivated by current theorem stack.

### H2. Interaction outcomes depend on relative phase class.

**Verdict:** adopt as testable mechanism; currently unproved in COG.

### H3. Without shared phase reference, remote phase is effectively unpredictable.

**Verdict:** adopt in epistemic form (observer-limited), not as ontic randomness.

### H4. Unknown 4-phase gives 2 bits effective entropy.

**Verdict:** adopt as coarse-grained observer uncertainty measure only.

### H5. Entropy from unknown phase provides energy.

**Verdict:** reject.  
Energy must come from transition dynamics and conserved accounting, not from ignorance.

### H6. Composite dynamics can realize periods greater than 4.

**Verdict:** confirmed empirically (2026-02-26).

`cycle_spectrum_scan.py` (cross-coupled composite dynamics, Codex upgrade) measured:
- 2-node composites: periods observed in {3, 6, 8}
- Larger composites: periods observed in {8, 12}

All exceed the single-node period-4 bound. H6 is no longer merely plausible — the
period-extension mechanism is active in the current COG computational model.

Next step: characterise which graph topologies and colorLabel assignments produce which
periods. This is a prerequisite for the UPDATE-RULE-001 composite interaction tests.

---

## 4. Literature-Constrained Interpretation

What literature supports:

1. Internal clock/fast phase pictures are physically meaningful in multiple settings.
2. Relative phase can modulate interaction outcomes in coherent scattering/control settings.
3. Missing phase reference can operationally erase accessible coherence information.
4. Driven many-body systems can realize robust multi-period responses beyond simple 2-cycles.

What literature does not support:

1. a universal theorem that COG's exact e7/Z4 construction is the unique physical mechanism.
2. entropy-from-phase-ignorance as a direct energy source.

---

## 5. Formal COG Definitions (Proposed)

Let `T(x) := e7 * x` be temporal commit (RFC-019) on Kernel v2 state.

Define a derived phase class for node state `psi_t(v)`:

`phi4_t(v) in Z4`

such that successive `T` applications advance phase by +1 mod 4 on the tracked orbit class.

For interacting pair `(u,v)` at tick `t`, define relative phase:

`DeltaPhi4_t(u,v) := phi4_t(u) - phi4_t(v) mod 4`.

Define phase-conditioned transition statistics:

- `P(channel | DeltaPhi4 = d)` for `d in {0,1,2,3}`
- expected interaction-cost increment conditioned on `d`.

All definitions are derived from deterministic microstate evolution; no stochastic phase sampling is allowed in kernel logic.

---

## 6. Architectural Decisions (Locked in this RFC)

### D1. Phase is derived, not stored as authority

`phi4` is a deterministic derived observable from Kernel v2 state and update trace.

### D2. Entropy is epistemic

Any "2-bit phase entropy" is an observer model quantity:

`H_phase(observer) := H(phi4 | observer_information)`.

It is not kernel entropy creation and does not violate no-exogenous-information rules.

### D3. Energy accounting stays in transition semantics

Energy-like observables must be defined through transition costs/binding differences (RFC-015/RFC-018 style), not uncertainty measures.

### D4. Multi-period search is mandatory

COG must measure cycle spectrum for composite subsystems rather than assuming universal period-4 at all scales.

---

## 7. Falsifiable Predictions

### Test A: Relative-phase modulation

Holding all non-phase variables fixed as much as possible, observed channel/cost distributions vary with `DeltaPhi4`.

### Test B: No-reference degradation

When phase-reference information is removed from observer model, predictive accuracy for phase-sensitive channels drops.

### Test C: Energy non-equivalence

Changing observer phase uncertainty alone (without changing microstate dynamics) does not change conserved energy accounting.

### Test D: Cycle spectrum broadening

Composite subsystems exhibit periods in a set `S` that can include values larger than 4.

**Status:** passed empirically (2026-02-26). See H6 verdict above.
Observed periods: {3, 6, 8} (2-node); {8, 12} (larger). Formal Lean proof still open.

---

## 8. Lean and Python Implementation Targets

## 8.1 Lean targets

Add module(s):

- `CausalGraphTheory/PhaseClock.lean`
- optional: `CausalGraphTheory/RelativePhase.lean`

Definitions:

- `phi4 : Trace -> NodeId -> ZMod 4`
- `deltaPhi4 : Trace -> NodeId -> NodeId -> ZMod 4`
- `phaseEntropy : ObserverView -> Trace -> NodeId -> ENNReal` (or finite proxy)

Theorem targets:

1. `phi4_periodicity_on_temporal_commit` (derived from existing period-4 stack).
2. `phaseEntropy_epistemic` (depends on observer projection, not kernel mutation).
3. `phase_uncertainty_not_energy` (formal separation theorem skeleton).

## 8.2 Python targets

Add:

- `calc/phase_clock_probe.py`
- `calc/relative_phase_channel_stats.py`
- `calc/cycle_spectrum_scan.py`

Metrics to log:

- `phi4_histogram`
- `delta_phi4_by_interaction`
- channel outcomes by `DeltaPhi4`
- cycle spectrum for selected motifs/subgraphs

Required tests:

1. deterministic replay yields identical `phi4` traces
2. phase-conditioned stats are reproducible
3. cycle-spectrum detector recovers period-4 on single-e7 baseline and detects larger periods on composite cases when present

---

## 9. Governance Impact

1. Claims asserting phase-dependent interaction must include explicit `DeltaPhi4` evidence.
2. Claims asserting phase-derived energy are blocked unless they define an explicit dynamic energy map and pass Test C.
3. Any use of "phase entropy" must be labeled `epistemic_only: true` unless a physical entropy map is separately proved.

---

## 10. Open Questions

1. What is the cleanest invariant definition of `phi4` under general update composition, not just pure temporal commits?
2. Which interaction families show strongest `DeltaPhi4` dependence?
3. Does entanglement increase phase-reference accessibility in COG observables, and under what conditions?
4. What is the empirical distribution of cycle lengths in larger motifs?

---

## 11. Relationship to Existing RFCs

1. Extends RFC-019 by introducing explicit local/relative phase observables.
2. Complements RFC-018 by clarifying how phase variables relate to `tau_topo` and `tau_int`.
3. Constrains RFC-021 language: phase uncertainty is not equivalent to entanglement or physical entropy production.
4. Uses RFC-020 Kernel v2 as mandatory state layer.

---

## 12. References

See `sources/discrete_phase_internal_clock_lit_review.md` for full citations and links.


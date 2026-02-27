# RFC-028: Canonical Update Rule Closure

Status: Active - D1-D5 policy locked; D4 static-cone no-spawn lock applied (2026-02-27); D5 implementation/proof wiring in progress
Module:
- `COG.Core.UpdateRule`
- `COG.Core.Trace`
- `COG.Core.Lightcone`
- `COG.Core.D4D5Contracts`
Depends on:
- `rfc/CONVENTIONS.md`
- `rfc/RFC-002_Deterministic_Tick_Ordering.md`
- `rfc/RFC-020_Kernel_Representation_Reconciliation.md`
- `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
- `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`
Literature basis:
- `sources/update_rule_closure_lit_review.md`

---

## 1. Executive Summary

This RFC answers the current architecture question:

"Kernel state is `C x O`; does update depend on lightcone, trace, and superdetermined ordering?"

Answer:
1. Yes, lightcone-local boundary inputs are required.
2. Yes, deterministic ordering/parenthesization must be predeclared in the initial condition.
3. Trace is optional only if the kernel is strictly Markov; otherwise it must be explicit kernel state.
4. Fixed-topology update is now locked; D4 is now static-cone no-spawn; D5 projection closure remains.

This RFC defines what must be settled before promoting higher-level claims.

---

## 2. Problem Statement

COG has strong pieces already:
1. `C x O`-native node state (RFC-020),
2. deterministic ordering and parenthesization (RFC-002),
3. lightcone-local update framing (RFC-022),
4. phase clock semantics (RFC-023).
5. explicit contract layer for D4/D5 (`CausalGraphTheory/D4D5Contracts.lean`).

Legacy note:
1. V1 `State/Update` DAG modules are retained for historical invariants and migration only.
2. They are not the canonical kernel path for active physics claims.

But the full transition program is still incomplete:
1. D4 is locked to static-cone no-spawn and must be kept disabled in canonical runs,
2. D5 contracts are locked with minimal profile canonical, but extended profile activation criteria must be validated empirically,
3. invariants/replay/leak proofs are not all wired to the new contracts.

Without these, the model is not fully specified.

---

## 2b. Architectural Assumptions

These are locked design choices that are not under active re-evaluation. Each entry states
the locked choice, why it was made, what was explicitly rejected, and the concrete evidence
or failure that would prompt reopening it.

### A1. State space: ℂ⊗𝕆 over ℤ

**Locked choice:** Node state `ψ ∈ ℂ⊗𝕆` with integer coefficients (ℤ), not real or rational.

**Justification:** The project's prime directive forbids ℝ. ℂ⊗𝕆 is the minimal normed
division algebra structure that simultaneously contains U(1) phase (from ℂ) and the
octonion color-direction space (from 𝕆). Integer coefficients enforce the discrete-first
constraint and prevent continuous-limit approximations from silently entering Lean proofs.

**Alternatives not taken:** ℚ coefficients (preserve discreteness but add density and
complicate norm calculations); ℝ (violates prime directive); ℂ⊗ℍ⊗𝕆 full 64-dimensional
Clifford path (more expressive but requires explaining why three generations arise from a
single algebra rather than from three copies).

**Revision trigger:** A ratio prediction (e.g., proton-to-electron mass ratio) requires
intermediate values that are not ℤ-linear combinations of the eight octonionic basis
vectors, and no algebraic-integer representation exists within the current basis set.

---

### A2. Temporal commit operator: T(ψ) = e₇ · ψ

**Locked choice:** The temporal step is left-multiplication by the e₇ Fano basis element.

**Justification:** e₇ is the vacuum axis — the unique Fano-plane element stabilised by the
Witt-pair SU(3) action on the six color directions. Left-multiplication by e₇ generates a
cyclic action on the vacuum orbit (period 4, proved as `phi4_period4`), giving the Z₄ phase
clock. It is also the simplest generator consistent with the requirement that the vacuum
state maps to itself under repeated application.

**Alternatives not taken:** A Fano-triple product (e.g., e₁e₂) as time generator;
right-multiplication by e₇; a modular counter that does not use octonion algebra at all.

**Revision trigger:** `phi4_period4` fails to hold for physically relevant charged states
outside the vacuum orbit (i.e., e₇⁴ ≠ identity on an electron state); or a published
algebraic result establishes that a different element is the natural discrete-time
generator in ℂ⊗𝕆. This is one of the two assumptions most worth verifying with an external
algebraist (see project notes on Furey correspondence).

---

### A3. Left-multiplication convention

**Locked choice:** All edge operators and T apply as left-multiplications: `op * ψ`, not `ψ * op`.

**Justification:** Left-multiplication means the causally earliest message (lowest topoDepth)
is the innermost factor in the non-associative product. Causal ordering maps directly to
algebraic parenthesization depth: `((...(T(ψ) * m₁) * m₂) * ... * mₙ)`. The alternativity
theorem then makes the forced parenthesization meaningful: switching left to right would
reverse the causal ordering in the algebra.

**Alternatives not taken:** Right-multiplication throughout; mixed (left for T, right for
messages); symmetrised product that averages left and right results.

**Revision trigger:** Furey's number-operator charge construction is shown to require
right-module action to give correct charge eigenvalues on the electron state; or a
benchmark two-node interaction produces the correct U(1) charge sign only under
right-multiplication and the wrong sign under the current left-multiplication convention.

---

### A4. U(1) charge defined as Re(ψ₇)

**Locked choice:** `u1Charge(ψ) = Re(ψ.c₇)` — the real part of the e₇ component.

**Justification:** e₇ is the vacuum axis. In the Furey picture, charge is associated with
the complex phase of the vacuum-direction component. Re(ψ₇) is local (computable from a
single node), integer-valued on benchmark states (−½ for electron, +½ for positron-like,
0 for vacuum), and preserved by the Witt-pair symmetry in the six-direction color subspace.

**Alternatives not taken:** Furey's explicit number operator `J = ⅓(e₁₂₃ + e₁₄₆ + e₂₄₇ + ...)`
which recovers both hypercharge and EM charge from a single operator on a representation;
the e₀ (scalar/identity) component; the Euclidean norm of the full ψ vector.

**Revision trigger (highest priority):** Furey's number operator J applied to the electron
state yields a different eigenvalue than Re(ψ₇); hypercharge and EM charge must be
distinguished in a hydrogen binding energy calculation (requiring two independent charge
readouts, not one); or charge conservation fails in a multi-round simulation. This is the
assumption most urgently requiring external validation.

---

### A5. colorLabel is a static structural label

**Locked choice:** Each node's `colorLabel : FanoPoint` is set once at spawn and is never
modified by `nextStateV2` or any downstream update step. Proved: `nextStateV2_preserves_colorLabel`.

**Justification:** In Furey's algebraic picture, particle type (which Fano line a state
sits on) is a property of the irreducible representation, not something that changes during
free propagation. Color exchange in QCD is expected to be modelled by edge-operator
messages between nodes, not by mutation of the receiving node's own type label.

**Alternatives not taken:** Dynamic colorLabel updated by `nextStateV2` based on message
content; colorLabel derived deterministically from the live ψ state rather than stored as
a separate field.

**Revision trigger:** The proton bound-state model requires a quark node to change its
Fano-line assignment during evolution (e.g., color exchange cannot be expressed as
edge-operator messages between fixed-colorLabel nodes); or a spawn rule requires
initialising a new node with a non-vacuum colorLabel, which would require relaxing
`SpawnColorLabelLaw`.

---

### A6. Single tick per node per round (uniform step size)

**Locked choice:** Every node advances exactly one tick per scheduler round regardless of
how many incoming messages it receives.

**Justification:** Simplest closure. Uniform step size ensures `phi4` advances by exactly 1
for every node per round, maintaining global phase coherence. It is the discrete analog of
a uniform global coordinate time frame and avoids the need to specify a relative-time rule.

**Alternatives not taken:** Event-driven step (nodes tick only when they receive at least
one message); proper-time step (nodes with greater computational load tick more slowly);
multi-step (a single round advances some nodes by 2 or more ticks).

**Revision trigger:** A two-node simulation shows that a fast-propagating particle must
tick more than once per round to maintain causal ordering; or the scheduler-equivalence
invariant (event-driven vs fixed-step, §6 gate 4) is shown to fail, implying the two are
not interchangeable and one must be chosen on physical grounds.

---

### A7. Topology changes only between rounds

**Locked choice:** Spawn and edge-creation events can occur only at round boundaries, not
mid-round.

**Justification:** Prevents causal paradoxes where a mid-round spawn could influence nodes
that have already been updated in the same round. Between-round topology change is
consistent with the classical causal-set growth model (Rideout-Sorkin).

**Alternatives not taken:** Mid-round spawning (requires a causal ordering within a round,
which is currently under-specified); lazy spawn (node materialises only when first targeted
by a message from an existing node).

**Revision trigger:** The only natural model of virtual pair production requires a node to
appear mid-round and influence other nodes in the same round without causal ordering
violation; or lazy spawn is shown to satisfy `SpawnCompleteness` with simpler implementation
and no correctness gap.

---

### A8. Canonical message ordering: topoDepth ascending, nodeId as tiebreak

**Locked choice:** Multiple incoming boundary messages are folded in ascending source
`topoDepth` order, with `nodeId` as a deterministic tiebreak for same-depth messages.

**Justification:** topoDepth is the causal-depth index. Messages from causally earlier
nodes should apply first (innermost factor). NodeId is arbitrary but deterministic,
satisfying the superdetermination requirement without introducing physical content.

**Alternatives not taken:** Ordering by nodeId only (ignores causal structure); topoDepth
descending (most recent cause first — physically reversed); ordering by a global clock
(violates the no-exogenous-clock policy from §4).

**Revision trigger:** A Lorentz-invariance analog requires that no ordering can be preferred
among spacelike-separated boundary messages; or a benchmark shows that two same-depth
messages with different nodeId orderings produce different psi outcomes, meaning the
tiebreak is physically meaningful and must be derived, not merely declared.

---

## 3. Canonical Update Skeleton

Let `psi_t(v) : C x O` be node `v` at tick `t`.

Define:
1. `B_t(v)`: incoming boundary messages from the causal past cone boundary.
2. `O_t(v)`: canonical order on `B_t(v)` (topoDepth, then nodeId), with immutable parenthesization.
3. `H_t(v)`: local trace slice (possibly empty for Markov kernels).
4. `T(x) := e7 * x`: temporal commit operator.

Required transition form:

`psi_{t+1}(v) = U( T(psi_t(v)), O_t(v), H_t(v) )`

where `U` is deterministic and free of external entropy.

---

## 4. Superdetermined Initial Condition Contract

To prevent runtime ambiguity, initial microstate must include immutable:

1. initial graph topology and node states,
2. edge operator assignment policy,
3. tie-break key order,
4. parenthesization tree per multi-input interaction family,
5. trace window policy (Markov or finite-memory),
6. scheduler mode contract (fixed-step reference semantics).

No runtime rule may consult wall-clock time, RNG, or nondeterministic container order.

---

## 5. Mandatory Decisions to Close the Update Rule

## D1. Choose one `combine` family

Status: Locked.

**Decision:** multiplicative — `combine(base, interaction) = base * interaction`.

**Justification:** Octonion multiplication is the natural product in ℂ⊗𝕆. Multiplicative
combine is the unique choice consistent with the left-module action of the algebra on
itself. An additive combine `base + interaction` would not respect the algebraic structure
(states would exit any bounded norm ball) and has no obvious physical interpretation in
the Furey framework.

**Alternatives not taken:** Additive combine; weighted interpolation; projection-then-multiply.

**Lean artefacts:** `UpdateRule.combine`, closure theorem `UpdateRule.combine_closed_coz`.

**Revision trigger:** A numerical experiment shows that `base * interactionFold(msgs)` does
not preserve the vacuum orbit across full round sequences for a benchmark initial state,
while an alternative combine does; or charge conservation fails under multiplicative combine
in a multi-particle scattering simulation with known output.

---

## D2. Lock trace semantics

Status: Locked.

**Decision:** Markov — `H_t(v) = empty` (no trace memory).

**Justification:** Simplest closure that closes the update-rule specification. Markov is
sufficient for free-particle propagation and for interactions fully specified by current
boundary messages. Adding trace memory (m > 0) introduces a parameter with no evidence
that it is needed for any current benchmark. See also assumption A6 on uniform step size;
both reflect the same minimality principle.

**Alternatives not taken:** Finite trace window of depth m > 0; full history (infinite
memory); external context injection (breaks superdetermination constraint).

**Lean artefacts:** `UpdateRule.interactionFold` with empty list identity,
closure theorem `UpdateRule.interactionFold_empty_eq_one`.

**Revision trigger:** Any measured interaction outcome that requires the node's history
to predict correctly — specifically, if a two-node round produces different outcomes
depending on the ordered sequence of previous rounds, and this difference cannot be
expressed as a change in the current boundary messages alone.

---

## D3. Lock energy-exchange predicate

Status: Locked.

**Decision:** Energy exchange occurs iff `msgs ≠ []` AND `interactionFold(msgs) ≠ 1`.

**Justification:** The two conditions are the minimal criteria for a meaningful interaction.
An empty boundary means no incoming information (trivially no exchange). An identity fold
means the messages cancel algebraically — the boundary exists but carries no net action on
the state. Together they define the smallest set of interactions that can physically change
ψ. This predicate is computable from local transition data only, consistent with the cone-
locality requirement.

**Alternatives not taken:** Non-empty boundary alone (ignores algebraic cancellation);
change in ψ above a threshold (non-local in general, requires comparing pre- and post-state);
non-identity individual messages without requiring their fold to be non-identity.

**Lean artefacts:** `UpdateRule.isEnergyExchangeLocked`.

**Revision trigger:** A calculation shows `interactionFold(msgs) = 1` but the multi-step
trajectory of ψ differs from the trajectory without those messages — i.e., the identity
fold is a coincidence at the aggregate level but the individual messages do have physical
effect. This would require a finer-grained exchange predicate that tests individual
messages rather than their fold.

## D4. Lock topology policy (static cone, no spawn)

Status: Locked (2026-02-27).

**Decision summary:** Canonical runs use a preallocated full light-cone region at `t=0`
with vacuum initialization for inactive sites. **No spawning is allowed during evolution.**
Topology is fixed; nodes outside the active simulation cone are pruned/ignored by boundary
policy, not materialized dynamically.

Formally for canonical profile:
1. `shouldSpawn = false` for all inputs.
2. `applySpawn` is identity on microstate.
3. all causally relevant sites are present in the initial cone allocation.
4. out-of-cone sites are removed from active update scope by deterministic pruning.

**Justification:** This removes a major source of ambiguity and proof burden while preserving
the local update semantics. It is aligned with your declared simulation practice:
pre-build the cone, evolve deterministically, prune outside scope.

**Operational implications:**
1. D4 no longer blocks physical simulation campaigns that do not need dynamic node creation.
2. fixed-topology replay tests become simpler and stronger.
3. any result that needs pair-production or topology growth must declare a non-canonical
   dynamic-topology profile.

**Alternatives not taken in canonical mode:** active-input spawn, lazy spawn, mid-round spawn.
These remain research profiles only.

**Lean/runtime interpretation:** Existing spawn contracts remain in the codebase as an
experimental dynamic-topology profile. They are **not** canonical for current model-derived
claims.

**Revision triggers (to re-enable dynamic spawn in canonical mode):**
1. a required benchmark cannot be represented with preallocated cone + prune-only policy, or
2. a dynamic-topology claim is promoted with full determinism/locality/permutation proofs and
   clear superiority over static-cone profile.

**colorLabel vs phase-cycle clarification (unchanged):**
`colorLabel` is a static particle-type axis (Fano basis point), not a 4-phase tracker.
The discrete 4-phase is `phi4 = tickCount mod 4` (`PhaseClock.lean`). These are independent
fields. `nextStateV2_preserves_colorLabel` (proved in `UpdateRule.lean`) is the formal statement.

## D5. Lock projection contract

Status: Policy locked; **dual-track** observer policy.

**Decision summary:** Two observer profiles are implemented. `piObsCanonical := piObsMinimal`
is locked for base claims. `piObsWithSector` is available for proton and color-sector
analyses and must be declared explicitly in claim provenance.

**Interaction-observation identity (locked):** Any local interaction update is an
ontic observation event for the participating nodes. In other words, interaction
and observation are identical at kernel level. D5 does **not** decide whether an
interaction was observed; D5 only decides which subset of already-observed kernel
facts is exported to an external observer/reporting layer.

**Justification for dual-track (not single canonical):** A claim proved under a more
expressive observer is weaker — it depends on more projections being stable. Base claims
(hydrogen charge, phase counting, mass ratios) should not be silently coupled to
color-sector projection machinery that they do not require. The dual-track makes this
dependency explicit in each claim's provenance rather than hiding it in the canonical
choice.

**Justification for `piObsMinimal` as canonical:** Minimal is the strongest possible base:
it proves claims using the fewest observables. `piObsWithSector` is always available for
the analyses that need it; the canonical choice only governs what assumptions are implicit
in claims that do not specify their observer explicitly.

**Justification for `u1Sector = none` in minimal:** Color sector (`u1Sector`) is derived
from ψ via `CausalGraph.piObs`. Hiding it in the minimal profile is not an approximation —
the sector still exists in the microstate. It is simply not reported by the minimal
observer, preserving the claim-strength property described above.

**Alternatives not taken:** Single canonical set to `piObsWithSector` (all claims coupled
to color-sector stability, weaker governance); single canonical minimal with no extended
profile (blocks proton analyses); dynamic observer chosen per-round (non-deterministic,
violates superdetermination).

**Lean artefacts:** `piObsNodeMinimal`, `piObsNodeWithSector`, `piObsMinimal`,
`piObsWithSector`, `piObsCanonical`, `PiObsNonTrivial`, `PiObsPermutationInvariant`,
`PiObsNodeIdLaw`, `PiObsChargeLaw`, `PiObsPhaseLaw`.

Uncertainty/entropy claims must reference this contract, not informal "hidden information" language.

**Revision triggers for `piObsCanonical`:**
- **Promote to `piObsWithSector`:** (a) all locked base benchmarks are shown unaffected
  by the upgrade; (b) `PiObsPermutationInvariant` is proved for `piObsWithSector`; and
  (c) at least one proton-track claim requires it and cannot be expressed under `piObsMinimal`.
- **Add a new profile beyond `piObsWithSector`:** A proton simulation requires exposing
  ψ components beyond `u1Sector` (e.g., Witt-basis decomposition depth), and this cannot
  be captured by any combination of the current four minimal fields plus sector.
- **Collapse to single profile:** Evidence shows the dual-track adds documentation overhead
  without any case where the minimal and extended tracks give different proof outcomes on
  any benchmark attempted in the first 12 months.

---

## 6. Invariants and Gates

All must pass before promoting derived-constant claims:

1. Determinism: identical init state and plan gives identical trace hash.
2. No exogenous information: no randomness, no nondeterministic iteration dependence.
3. Cone locality: outside-past-cone perturbations do not change local update under strict-cone mode.
4. Scheduler equivalence: event-driven and fixed-step agree at interaction boundaries.
5. Clock consistency: `tau_topo` monotonic on causal edges, `tau_int` increments only on declared energy exchanges.
6. Trace policy consistency: if `m=0`, transition is provably history-independent.
7. Structural-label immutability: `nextStateV2` preserves `colorLabel` (`nextStateV2_preserves_colorLabel`).

---

## 7. Lean and Python Deliverables

## 7.1 Lean deliverables

Add module(s):
1. `CausalGraphTheory/UpdateRule.lean`
2. `CausalGraphTheory/TraceSemantics.lean`
3. `CausalGraphTheory/D4D5Contracts.lean`

Minimum theorem targets:
1. `incomingBoundary_deterministic`
2. `orderedBoundary_unique`
3. `update_deterministic`
4. `no_exogenous_information`
5. `outsideConeInvariant_strict`
6. `markov_if_m0`
7. `shouldSpawn_canonical_always_false` (canonical profile theorem)
8. `applySpawn_canonical_identity` (canonical profile theorem)
9. `pi_obs_permutation_invariant` (implementation-level theorem for canonical `Pi_obs`)
10. `nextStateV2_preserves_colorLabel` (static structural axis invariant; already proved in `UpdateRule.lean`)

## 7.2 Python deliverables

Add script(s):
1. `calc/update_rule_ablation.py`
2. `calc/no_cone_leak_tests.py`
3. `calc/fixed_vs_event_equivalence.py`

Required outputs:
1. trace hashes across replay runs,
2. leak score under outside-cone perturbations,
3. divergence report for scheduler comparison,
4. sensitivity table for `m` and `k_max` choices.

---

## 8. Literature-Constrained Policy

Adopted:
1. local bounded-speed update constraints,
2. explicit memory semantics for non-Markov dynamics,
3. operational no-signaling audits for correlation claims.

Not adopted as theorem:
1. blanket assumption that `k > 4` is negligible,
2. "superdeterminism implies no-signaling" (must still be tested),
3. dynamic spawning as canonical behavior (kept as non-canonical research profile).
4. any non-local or identity-triggered dynamic spawn predicate in canonical runs.

---

## 9. Claim Governance Impact

Until this RFC is closed:
1. no claim can be upgraded to "model-derived" if it implicitly assumes dynamic topology while using the canonical static-cone profile,
2. uncertainty/entropy claims remain provisional unless tied to canonical `piObsCanonical`,
3. scheduler-dependent results must be labeled unstable.

---

## 10. Recommended Execution Order

1. Implement concrete `applySpawn` and prove `SpawnCompleteness` + `SpawnThenUpdateLaw`.
2. Prove canonical D4 no-spawn theorems (`shouldSpawn=false`, `applySpawn=id`) and enforce profile tagging for any dynamic-topology experiment.
3. Keep `piObsCanonical := piObsMinimal` for baseline runs and prove implementation-level permutation invariance.
4. Run benchmark suite to decide whether extended `u1Sector` exposure is required by evidence.
5. Implement invariants and replay/leak/equivalence harnesses against the locked contracts.
6. Only then resume deeper constant-derivation pushes.

---

## 11. References

1. P. Arrighi, G. Dowek (2012), Causal graph dynamics, https://arxiv.org/abs/1202.1098
2. P. Arrighi, S. Martiel (2016), Quantum Causal Graph Dynamics, https://arxiv.org/abs/1607.06700
3. L. Maignan, A. Spicher (2024), Causal Graph Dynamics and Kan Extensions, https://arxiv.org/abs/2403.13393
4. D. P. Rideout, R. D. Sorkin (1999), Classical Sequential Growth Dynamics for Causal Sets, https://arxiv.org/abs/gr-qc/9904062
5. S. Surya (2019), The causal set approach to quantum gravity, https://arxiv.org/abs/1903.11544
6. F. A. Pollock et al. (2018), Operational Markov Condition for Quantum Processes, https://arxiv.org/abs/1801.09811
7. G. Chiribella, G. M. D'Ariano, P. Perinotti (2008), Quantum Circuit Architecture, https://arxiv.org/abs/0803.3231
8. M. J. W. Hall (2010), Relaxing measurement independence, https://arxiv.org/abs/1007.5518
9. A. S. Friedman et al. (2019), Measurement dependence in Bell tests, https://arxiv.org/abs/1901.04521
10. S. Hossenfelder, T. Palmer (2020), Rethinking Superdeterminism, https://arxiv.org/abs/1912.06462

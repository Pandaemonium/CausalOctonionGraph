# RFC-068: Generation Drag from Spinor-Frame Scalar Load

Status: Active Draft - Hypothesis with Phase A Instrumentation Implemented (2026-02-27)
Module:
- `COG.Generation.Drag`
- `COG.XOR.Lightcone`
Depends on:
- `rfc/CONVENTIONS.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-034_Electron_Mass_Mechanism.md`
- `rfc/RFC-063_XOR_Octonion_Gate_and_Signed_Handed_Dynamics.md`
- `rfc/RFC-065_XOR_Vector_Spinor_Operator_and_Ideal_Stabilization.md`

---

## 1. Executive Summary

This RFC captures and formalizes a new mass-hierarchy hypothesis:
1. electron-like vector motifs evolve with lower effective drag,
2. spinor motifs (and heavier generations) incur higher deterministic update overhead,
3. the overhead appears as increased scalar-channel accumulation and ideal-stabilization work under the same XOR kernel.

Key correction:
1. `e0` is the octonion identity basis element, not a non-interacting "dead direction."
2. therefore the hypothesis is reframed as scalar-channel load and stabilization load, not "e0 does not interact."

This is a hypothesis RFC with explicit falsification gates.

---

## 2. Problem Statement

The project needs a concrete, testable mechanism for why muon and tau effective mass exceeds electron mass without introducing free continuous parameters.

Existing pieces already in scope:
1. deterministic XOR gate over `C x O` basis (RFC-063),
2. full-lightcone deterministic update policy (RFC-028 canonical profile),
3. shared vector/spinor operator with spinor stabilization stage (RFC-065),
4. prior mass-overhead framing (RFC-034).

Missing piece:
1. a single measurable drag model that compares electron, muon, and tau motifs under the same update semantics.

---

## 3. Hypothesis

### H1. Scalar-channel load
Under repeated lightcone interactions, motifs accumulate varying load in the scalar basis channel (`e0` coefficient magnitude and turnover). This load acts as computational inertia in the update loop.

### H2. Spinor-frame penalty
Spinor motifs require precondition and stabilization (RFC-065) to remain in a canonical ideal class. That deterministic extra work increases effective drag relative to vector motifs.

### H3. Generation ordering
If heavier generations correspond to motifs that require greater long-run stabilization and higher non-associative exposure, then:
1. `drag_electron < drag_muon < drag_tau`,
2. with no fitted attenuation constant added to the core XOR rule.

---

## 4. Formal Quantities (Discrete, No New Reals)

Let `psi_t` be node state at tick `t`, with Gaussian-integer coefficients on `e0..e7`.

Define per-tick observables:
1. `S_t` (scalar load): `L1(coeff_e0(psi_t))`.
2. `V_t` (vacuum-channel load): `L1(coeff_e7(psi_t))`.
3. `M_t` (ideal misalignment load): count of components outside declared ideal after raw XOR update, before stabilization.
4. `C_t` (stabilization work): integer count of stabilization operations applied that tick.
5. `A_t` (associator exposure): integer count of non-associative triple contexts encountered under the fixed parenthesization path.

Define deterministic drag proxy:
1. `D_t := S_t + M_t + C_t + A_t`.

Define motif drag score over horizon `T`:
1. `DragScore(T) := (1/T) * sum_{t=1..T} D_t`.

Define relative mass proxy to electron baseline:
1. `MuEff(motif, T) := DragScore_motif(T) / DragScore_electron(T)`.

This RFC keeps `mu_eff` normalization baseline at 1 for electron unless a strict algebraic reason is later proved.

---

## 5. Interpretation of the Original "Mass Trap" Intuition

The original intuition is preserved in corrected form:
1. "trap" means persistent scalar/stabilization load in discrete update dynamics,
2. "escape" means low misalignment and low repair burden under vacuum-driven evolution,
3. heavier generations correspond to motifs whose frame relation to the vacuum/ideal basis causes more persistent load.

This reframing avoids the incorrect statement that `e0` does not interact.

---

## 6. Predictions

If H1-H3 are correct, deterministic simulations should show:
1. vector-electron motifs have the smallest long-run `DragScore`,
2. spinor motifs with heavier-generation embeddings have higher `M_t` and `C_t` frequencies,
3. handedness policies (left-only vs right-only vs mixed) shift drag numerically but preserve ordering,
4. ordering remains stable across full-lightcone initial conditions once measured over a fixed plateau window.

---

## 7. Falsification Gates

Reject this RFC direction if any of the following occur:
1. `DragScore` ordering does not separate electron/muon/tau motifs under identical schedules,
2. spinor stabilization counters are near-zero and do not differ materially from vector runs,
3. ordering flips unpredictably under deterministic replay with same initial microstate,
4. results require adding fitted continuous attenuation factors to maintain ordering,
5. alternative simple discrete proxy (without scalar/stabilization terms) explains ordering better.

---

## 8. Implementation Plan

### Phase A: Instrumentation

Add:
1. `calc/xor_generation_drag_metrics.py`
2. `calc/test_xor_generation_drag_metrics.py`

Required outputs per run:
1. per-tick `S_t, V_t, M_t, C_t, A_t, D_t`,
2. replay hash,
3. motif id, handedness policy, initial-condition id.

### Phase B: Motif suite

Run on:
1. electron baseline motif (Furey-aligned representation already used in project),
2. candidate muon/tau motifs defined in a predeclared mapping file,
3. same full-lightcone update rule and horizon policy.

### Phase C: Report and gate

Produce:
1. `sources/generation_drag_report.md`,
2. `sources/generation_drag_metrics.json`,
3. claim update draft for `MU-*` with gate status.

---

## 9. Governance Constraints

1. No retrofitting:
   - motif mapping and schedule policy must be declared before reading outcomes.
2. No hidden continuous fitting:
   - drag proxy remains integer/discrete from kernel observables.
3. Full replayability:
   - every reported table row must include deterministic replay hash.
4. Canonical update lock:
   - use RFC-028 canonical full-lightcone contributor semantics only.

---

## 10. Decisions Requested

To operationalize this RFC, lock:
1. the candidate muon/tau motif mapping source file,
2. the plateau-window rule for reporting `DragScore`,
3. the exact associator-exposure counting rule (`A_t`) for benchmark comparability.

---

## 11. Acceptance Criteria

RFC-068 is `partial` when:
1. instrumentation exists and tests pass,
2. drag metrics are generated for at least one electron and one heavier-generation candidate motif,
3. replay hashes validate deterministic reproducibility.

RFC-068 is `supported` when:
1. ordering evidence is stable across multiple predeclared initial conditions,
2. falsification gates remain untriggered,
3. claim metadata is updated with explicit artifact links and method disclosure.

---

## 12. Notes

This RFC does not claim the mass hierarchy is solved. It defines a rigorous path to test whether generation-dependent drag can be derived from existing `C x O` XOR and spinor-stabilization machinery without adding ad hoc continuous parameters.

---

## 13. Phase A Status

Implemented artifacts:
1. `calc/generation_drag_motif_mapping.json`
2. `calc/xor_generation_drag_metrics.py`
3. `calc/test_xor_generation_drag_metrics.py`
4. `calc/xor_generation_drag_metrics.json`
5. `calc/xor_generation_drag_metrics.csv`
6. `sources/generation_drag_report.md`

Current result:
1. deterministic instrumentation is closed,
2. strong generation separation is not yet observed under the current candidate mapping and proxy,
3. Phase B is required for measured (not estimated) stabilization-work accounting.

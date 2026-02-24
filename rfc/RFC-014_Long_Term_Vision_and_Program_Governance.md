# RFC-014: Long-Term Vision and Program Governance

**Status:** Active — Revision 2 (2026-02-23)
**Supersedes:** RFC-014 Draft (Revision 1, Codex-generated)
**Type:** Program Charter
**Depends on:** `rfc/CONVENTIONS.md`, `rfc/RFC-001_Canonical_State_and_Rules.md`, `ORIENTATION.md`
**Related claims:** `FANO-001`, `ALG-001`, `GAUGE-001`, `KOIDE-001`, `LEPTON-001`, `MU-001`, `CFS-001`, `GEN-001`, `GEN-002`

---

## 1. Mission

COG tests one strict hypothesis:

> **Physical law is a deterministic computation on a discrete causal graph whose node states live in C ⊗ O (complex octonions). All observables — particle masses, coupling constants, generation count — emerge from the locked algebraic structure of the Fano plane with no free parameters.**

The program is falsifiable by construction. Every numerical claim is either machine-checked in Lean 4, computationally verified in Python, or explicitly recorded as blocked or falsified. Falsification evidence is never deleted.

**Algebra clarification:** Node states live in `C ⊗ O` — the 8-dimensional complex-octonionic algebra. This is *not* the 64-dimensional Dixon algebra `R ⊗ C ⊗ H ⊗ O`. The `H` (quaternion) factor does not appear as an independent layer; the quaternionic subalgebra `H_L ⊂ O` is accessed via the Fano line structure.

---

## 2. What Has Been Proved (as of 2026-02-23)

Formal record is in `PROGRESS.md`. Summary:

| Result | Method | Key file |
|--------|--------|---------|
| `|Aut(Fano)| = 168 ≅ GL(3,2)` | `decide` (Lean 4) | `GaugeGroup.lean` |
| `|Stab(e7)| = 24 ≅ SL(2,3)` — derived, not postulated | `decide` (Lean 4) | `GaugeGroup.lean` |
| Koide Q = 2/3 ⟺ B² = 2, proved over ℚ | `linear_combination` + `linarith` | `Koide.lean` |
| Race condition / confluence for simultaneous edges | structural proof | `RaceCondition.lean` |
| Triality circuit depth N_tau = 14 = dim(G₂) | greedy CSE | `triality_map.py` |
| Schur's Lemma: no 8×8 intertwiner T for V ↔ S+ reps | eigenvalue argument | `muon_mass.yml` |
| **Universal C_e = 4 theorem:** L_{e7}^4 = id for ALL non-zero states | left-alternative law | `furey_electron_orbit.py` |
| vertex_cost_ratio V_mu/V_e = 15 — confirmed lower bound on m_mu/m_e | simulation | `emu_dag_sim.py` |
| Finster orbit action S(n) = 2(1 - 1/n); simple L-ratio bounded by ~2 | analytic + tests | `cfs_action.py` |
| Full Furey electron state psi_e = -i * omega_dag, orbit period 4 | algebraic derivation | `furey_electron_orbit.py` |

---

## 3. What Has Been Ruled Out

These are proved negative results. They constrain what mechanisms are still viable.

| Ruled out | Why | Evidence |
|-----------|-----|---------|
| m_mu/m_e from state-orbit period alone | Universal C_e = 4: ALL states have period 4 under L_{e7} | `furey_electron_orbit.py`, 26 tests |
| Simple CFS L-ratio as mass mechanism | S(n_mu)/S(n_e) < 2 for any positive n; 100x below 206.768 | `cfs_action.py`, 29 tests |
| COG-QC-01: m_mu/m_e = 1 + N_tau | 1 + 14 = 15 ≠ 207 | `triality_map.py` |
| 8x8 SO(8) intertwiner T: V-rep ↔ S+-rep | Schur's Lemma; eigenvalue spectra differ | `muon_mass.yml` |
| S3 automorphism in Aut(O) | S3 ⊄ Aut(O); lives at sedenion level | Gresnigt 2306.13098 |
| proton motif C_e=3, C_p=8, mu=2.667 | asymmetric exchange, frozen quark | RFC-001 Phase II simulation |
| proton motif C_e=3, C_p=11, mu=3.667 | 500x below target | RFC-001 Phase III simulation |

---

## 4. The Three Central Open Problems

These are the quantitative predictions COG must make to be a viable physical theory. They are listed by how much progress has been made, from most to least.

### 4.1 Muon-to-Electron Mass Ratio (LEPTON-001)

**Target:** m_mu/m_e = 206.7682830 ± 0.0000046 (CODATA 2022)

**Proved lower bound:** V_mu/V_e = 15 (vertex cost ratio)
**Closest COG model:** N_TAU × V_mu = 14 × 15 = 210 (1.56% above; no derivation yet)
**Gap to close:** factor of ~13.78 above the vertex-cost lower bound

The Universal C_e theorem has ruled out orbit-period mechanisms. The remaining viable classes are:

1. **Spacetime density:** mass ∝ S_action = total CFS action over all node pairs in the particle's worldline. The Finster S ~ m^2 scaling (arXiv:2201.06382) gives m_mu/m_e ≈ V_mu/V_e = 15 (not 206), but a careful treatment of spin degeneracy (n=8 in the Lagrangian) has not been done.

2. **Geometric mean model:** Is N_TAU × V_mu = dim(G₂) × (dim(G₂)+1) a coincidence or derivable? The product dim(G₂) × (dim(G₂)+1) = 14 × 15 = 210 is structurally natural (it is the dimension of the full rank-2 symmetric space of G₂) but lacks a causal derivation.

3. **Fano path-length difference:** The electron cycles within an associative subalgebra (L1 quaternion line); the muon traverses a non-associative Fano path. If the muon's effective path length is longer per absorption (not longer period, but more evaluations per hop), this could multiply V_mu beyond 15. This has not been simulated.

**Next task for LEPTON-001:** See T3 and T4 in §5.

### 4.2 Proton-to-Electron Mass Ratio (MU-001)

**Target:** m_p/m_e = 1836.15267343 ± 0.00000011 (CODATA 2022)

**Current simulation:** mu_COG = 3.667 (Phase III), ~500× below target
**Root cause of gap:** The proton motif is a 3-quark color-singlet cycle. The current simulation uses minimum-first-recurrence; the physical proton likely requires the gate-density thermodynamic limit, not a finite recurrence count.

The RFC-001 branching model (non-associative steps spawn two branches, cost = 2 each) has not been combined with the gate-density measurement. The 250-branch explosion after 100 steps (Phase III) shows that the full branching tree is intractable. The correct measurement is the ratio of gate densities in the thermodynamic limit, not the ratio of first-recurrence cycle counts.

**Critical architectural decision still open:** For mass, do we measure
- (a) the ratio of first-recurrence tick counts C_p/C_e, or
- (b) the ratio of gate densities in the infinite-time limit, or
- (c) the ratio of minimum-cost path lengths from root to color-singlet recurrence?

Option (c) is the most defensible (lowest-action path = physical classical trajectory). Options (a) and (b) both have problems. This decision must be made before MU-001 can be simulated correctly.

**Next task for MU-001:** See T5 in §5.

### 4.3 Three Fermion Generations (GEN-001, GEN-002)

**Status:** Blocked at the C ⊗ O level.

The algebraic fact is: S3 ⊄ Aut(O). The Gresnigt mechanism (arXiv:2306.13098) generates three generations from the S3 automorphism of the sedenions S, which contains O as a subalgebra. COG operates at the C ⊗ O level and cannot directly access this mechanism.

Two distinct questions remain open and should not be conflated:

**Question A (algebraic):** Can the three Witt pairs (e6,e1), (e2,e5), (e3,e4) — which are the three SU(3) color planes in C ⊗ O — be permuted by an S3 action that, while not an automorphism of the Fano multiplication table, is still a symmetry of the DAG edge topology?

If yes: three generations may emerge as topological orbits within COG, not requiring sedenion extension.
If no: COG at C ⊗ O cannot generate three generations algebraically.

**Question B (representation):** Does the Furey projector construction (s·S*, s*·S* sectors of C ⊗ O) give distinct orbit topologies for electron (generation 1) vs muon (generation 2)? If the two sectors have different DAG path lengths, that is the generation discriminant.

**Next task for GEN:** See T2 in §5.

---

## 5. Prioritized Work Queue

Tasks are ordered by: (tractability × centrality). Tier 1 tasks have clear yes/no answers and bounded scope. Tier 2 tasks are the core unsolved problems. Tier 3 tasks are prerequisite research with no current clear path.

### Tier 1 — Bounded, Tractable, High-Value

**T1: Lean 4 — Universal C_e = 4 theorem**
The Python proof is complete (26 tests). Formal verification requires:
- `e7 * e7 = -e0` (from the Fano table, already in the codebase)
- Left-alternative law: `e7 * (e7 * x) = (e7 * e7) * x = -x` for all x in C ⊗ O
- Therefore L_{e7}^4 = id, period 4 for all non-zero states

Input: existing `Oct` type and multiplication table in `CausalGraphTheory/`. Output: `theorem universal_Ce_period` in a new `Lean` file, 0 sorries.

**T2: Python — Witt-pair S3 permutation check**
Define the cyclic permutation sigma: (e6,e1) -> (e2,e5) -> (e3,e4) -> (e6,e1) and test whether it preserves the Fano multiplication table (i.e., is sigma in Aut(Fano)?). ~30 lines using `FANO_CYCLES` from `conftest.py`. This is a clean yes/no answer to GEN-002 open question 2. If sigma is NOT in Aut(Fano), then S3 acting on Witt pairs is still not a Fano automorphism — three generations remain blocked at C ⊗ O. If sigma IS in Aut(Fano), then GEN-002's blocked status should be revisited.

**T3: Python — Investigate N_TAU × V_mu derivation**
Is there a spacetime-density argument that naturally gives 14 × 15 = 210 ≈ 206.768? Specific candidates to test:
- dim(G₂) × (dim(G₂)+1) = 14 × 15: the "triangular number" of G₂ — is this the dimension of the symmetric space G₂/SO(4)? (Answer: no, but check.)
- The spin-degeneracy correction: Finster's Lagrangian L = |c|^2 - |c|^4/n with n=8 (spin dimension) and the orbit action S(n=8) = 7/4. Does the n-dependence give a correction factor of 14/15 that shifts 225 down to 210? (S(8)/S(8+epsilon) ~= 1, so probably no. But check the CFS action with n=15 for the muon, n=1 for the electron — treating vertex cost as effective spin dimension.)
- If no derivation found within one session: record as unresolved in `claims/muon_mass.yml` and move on.

**T4: YAML — Update CFS-001 status**
`claims/causal_action_discrete.yml` is still `status: stub`. Update to `status: partial` with the §4g orbit action formula S(n) = 2(1-1/n), the simple L-ratio ruled-out result, and the new Finster literature entries (arXiv:2201.06382, arXiv:2503.00526).

### Tier 2 — Core Unsolved Problems

**T5: Python — Proton minimum-cost-path simulation**
Implement the RFC-001 §3.3 branching protocol with minimum-cost-path selection: at each step, follow the branch with the lower tick count. This gives a classical trajectory through the non-associative tree. Run until color-singlet recurrence and compute C_p. Compare C_p/C_e to 1836. The prediction of RFC-001 is that this ratio should approach 1836 — that is the claim MU-001 is testing. If the result is still << 1836, it is a new falsification datum. Do not adjust the motif or rules to match; record the result and what it implies.

Architecture constraint: Use minimum-cost branch (§5.2 of RFC-001), not full branching. The physical proton is a single classical object, not a superposition.

**T6: Python — Muon Fano path-length simulation**
The electron lives in sector s·S* and absorbs photons via L_{e7}. The muon lives in sector s*·S* (different projector). Does the muon's Fano path — the sequence of states it traverses when absorbing a photon — differ in EFFECTIVE LENGTH (not period) from the electron's?

Specifically: in the e-mu DAG simulation, the muon takes V_mu = 15 ticks per absorption. Where do those 15 ticks go? Are they 14 non-associative evaluations + 1 associative one? Or some other decomposition? If V_mu = 1 + 14 (one native absorption + 14 triality-translation steps), can the 14 triality steps be decomposed into a sequence of Fano-path hops that are computationally distinct from the electron's? This would give a structural derivation of V_mu = 15 from the Fano path geometry.

**T7: RFC amendment — Resolve the branching architecture decision for MU-001**
The RFC-001 branching model (cost = 2 per non-associative step, both branches retained) leads to exponential blowup. But the mass ratio MU-001 requires a single number. Before T5 can produce a definitive result, the selection rule must be formally stated. Draft a one-page addendum to RFC-001 §3.3 specifying: "The classical path is the minimum-cost branch at each non-associative step. The mass ratio is computed on this path." This decision must be recorded and justified before the simulation result can be reported as evidence.

### Tier 3 — Long-Range or Prerequisite Research

**T8: Coupling constants — ground the stub claims**
`claims/alpha_fine_structure.yml`, `claims/weinberg_angle.yml`, `claims/alpha_strong.yml` are stubs. Before attempting derivations, document precisely what COG predicts for each:
- alpha: is the claim that 1/alpha = |GL(3,2)|/|SL(2,3)| × (something)? That gives 168/24 = 7, not 137. What is the proposed mechanism?
- sin^2(theta_W): the 1:3:6 argument in RFC-007 §6.2 gives a ratio of 1/(1+3) = 1/4 = 0.25; the measured value is 0.231. What correction is needed?
Until there is a proposed mechanism (not just a goal), these claims cannot be moved from stub.

**T9: Lean 4 — Witt basis formal properties**
The Witt basis identities (alpha_j · omega = 0, alpha_j^dag idempotent, etc.) are verified in Python (26 tests in `furey_electron_orbit.py`). A Lean proof would upgrade these from numerically verified to formally proved. Medium effort; uses existing `Oct` type.

**T10: RFC-005 — Continuum limit strategy**
RFC-005 (`RFC-005_Continuum_Limit_Strategy.md`) is a stub. The central question: does COG's discrete causal graph reproduce Lorentz symmetry, Maxwell's equations, or the Dirac equation in any large-graph limit? Without a continuum limit, COG is a self-consistent algebraic structure but not a theory of spacetime. This is a long-range theoretical question but must be formally addressed before the program can claim to be a physical theory.

---

## 6. Non-Negotiable Constraints

These constrain every artifact in the repository. They are not negotiable without explicit human approval.

1. **`rfc/CONVENTIONS.md` is canonical.** All Fano triples, sign tables, Witt basis pairings, and vacuum axis assignments are locked. No code may redefine them.

2. **No continuum primitives in core derivations.** Real analysis, differential equations, and probability measures are forbidden in the core algebra. The Lean gate (`CLAUDE.md §3`) enforces this via forbidden Mathlib imports.

3. **Deterministic replay.** From an identical initial microstate, the simulation must produce bit-identical output. No stochastic paths.

4. **Free parameters are disallowed.** If a numeric constant is tuned to match a target, it is not a derivation. Record what the COG-native value is and the discrepancy. Do not post-hoc adjust.

5. **Falsification evidence is retained.** Failed simulations, falsified sub-hypotheses, and retracted claims are documented in their YAML files with dates. They are never deleted.

6. **Claim pointers must exist and run.** A claim with `status: proved` must have a lean_file/lean_theorem or python_test that passes. Broken pointers are integrity violations.

---

## 7. Program Failure Conditions

The core hypothesis is falsified if any of the following is established:

1. **Deterministic closure fails:** The update rule requires a free choice (not derivable from the Fano table or initial microstate) to proceed.

2. **Observable mismatch is structural:** After a good-faith best-effort derivation, the COG-native prediction differs from the experimental value by more than can be attributed to known approximations (finite graph size, missing generation structure, etc.), with no remaining viable mechanism.

3. **The locked conventions are inconsistent:** A contradiction is derived from the Fano triples and octonion alternativity axioms alone.

4. **Reproducibility fails:** Different platforms or implementations, given the same initial microstate, produce different results for the same claim.

None of these conditions has been triggered as of 2026-02-23. The three mass ratio gaps (factor ~13.78 for muon, factor ~500 for proton) are large but have viable remaining mechanisms. The program continues.

---

## 8. Architecture State

This section records architectural decisions that have been made, for reference when reading simulation code.

### 8.1 Node State Representation

Current: nodes carry an 8-component complex numpy array representing a state in C ⊗ O. The OctIdx label from RFC-001 §2.1 is superseded by the full C ⊗ O vector for lepton simulations; the 3-quark baryon simulation still uses OctIdx + sign.

### 8.2 Two Simulation Regimes

**Lepton/photon regime (QED):** The photon absorption operator is L_{e7} (left-multiplication by e7). This is a 2-body product: e7 * state. There is NO branching. The orbit period is provably 4 for all non-zero states (Universal C_e theorem). Files: `qed_ee_sim.py`, `emu_dag_sim.py`, `furey_electron_orbit.py`.

**Baryon/gluon regime (QCD):** Gluon exchange is a 3-body product: (source_state · gluon) · dest_state vs source_state · (gluon · dest_state). This MAY branch (if the triple is non-Fano). Files: `mass_drag.py`. Status: partial (see MU-001).

These two regimes are physically distinct. The lepton mass ratio (m_mu/m_e) is in the QED regime. The proton mass ratio (m_p/m_e) is in the QCD regime. Do not conflate them.

### 8.3 The CFS Action Layer

The Finster causal action L(x,y) = |c|^2 - |c|^4/n has been implemented and tested (§4g of PROGRESS.md, `cfs_action.py`). Key finding: the per-orbit action ratio S(n_mu)/S(n_e) is bounded above by ~2 and cannot explain the 206.768 ratio. The effective m^2 model gives (V_mu/V_e)^2 = 225 (8.8% above). The CFS action layer is currently a diagnostic tool, not a complete mass mechanism.

---

## 9. Evidence Integrity Rules

These govern how claims advance through the status vocabulary (`stub → in_progress → partial → proved / blocked / falsified`).

1. `stub → partial` requires an implementation artifact (Python test or Lean file) that makes partial progress. The artifact must be pointed to in the claim.
2. `partial → proved` requires a complete derivation with no open sub-steps. All pointers must pass.
3. Any status → `blocked` requires an explicit `blocked_reason` describing what external result, unresolved design decision, or mathematical obstruction prevents progress.
4. Any status → `falsified` requires a `simulation_record` with: input microstate, rule version, output value, discrepancy metric, and rerun command. The record is permanent.
5. Claims with stale or non-existent pointers must be downgraded. They cannot remain `proved`.

---

## 10. Completion Criterion

The COG program has answered its central question when:

1. **Three quantitative predictions are derived** (not fitted): m_mu/m_e, m_p/m_e, and the Koide formula, each from the locked Fano/C ⊗ O conventions with no free parameters.
2. **Two qualitative predictions are derived:** three fermion generations and the SU(3) × U(1) unbroken symmetry, from the same conventions.
3. **All derivations are reproducible** from a clean checkout with documented commands.
4. **The falsification record is complete:** every ruled-out mechanism is documented with why it was ruled out.

The program has *not* answered its central question simply because the formal verification record is clean. Lean proofs of algebraic identities are necessary but not sufficient. The physics must also be checked.

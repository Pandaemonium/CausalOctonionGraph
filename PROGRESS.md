# PROGRESS.md — COG: Proved Results

**Updated:** 2026-02-24 | **Lean:** 0 sorries | **Python:** 648 tests passing | **Build:** 1824 jobs

Novel results first. Previously-known results verified in the COG framework are in §5.

---

## 1. Vacuum Stabilizer Derived from Fano Geometry  *(Lean 4 — novel)*

**File:** [CausalGraphTheory/GaugeGroup.lean](CausalGraphTheory/GaugeGroup.lean)

The order-24 vacuum stabilizer is **derived**, not postulated (isomorphism label under review):

| Theorem | What it proves | Method |
|---------|---------------|--------|
| `fano_aut_count` | \|Aut(Fano)\| = 168 ≅ GL(3,2) | `decide` |
| `vacuum_stabilizer_count` | \|Stab(e7)\| = 24 | `decide` |
| `vacuum_lines_count` | Exactly 3 Fano lines through e₇ | `decide` |
| `orbit_stabilizer_check` | 168 = 7 × 24 | `decide` |

Orbit-stabilizer gives the 24-element vacuum stabilizer directly from the Fano action on the vacuum axis e7. The exact isomorphism label is tracked separately and currently under review in light of the newly formalized order-profile checks.

---

## 2. Race Condition Theorem  *(Lean 4 — novel)*

**File:** [CausalGraphTheory/RaceCondition.lean](CausalGraphTheory/RaceCondition.lean)

`confluence`: Two causal graphs that differ only in the ordering of simultaneous edges produce **identical tick counts**. First machine-checked proof that COG causal ordering is insensitive to edge-processing order — a necessary condition for Lorentz-like invariance at the algebraic level. Proved structurally with no sorry.

---

## 3. Koide Q = 2/3 over ℚ  *(Lean 4 + Python — novel)*

**Files:** [CausalGraphTheory/Koide.lean](CausalGraphTheory/Koide.lean), [calc/koide_sl23.py](calc/koide_sl23.py)

| Result | Method |
|--------|--------|
| `brannen_b_squared`: Brannen ansatz + Q=2/3 forces B²=2, proved over ℚ | `linear_combination` + `linarith` (no reals) |
| SL(2,3) → Z3 → Brannen → Koide chain end-to-end | 54 Python tests (`calc/test_koide_sl23.py`) |
| **Positivity band:** physical phase φ ≈ 2/9 keeps all f_k > 0 by a margin of 0.028 | `TestPositivityBand` |

The ring identity Q = 2/3 ⟺ B² = 2 is proved with **no reals, no analysis, no irrational numbers** — over ℚ alone, by `linear_combination` (4 steps) + `linarith`. Axioms: {propext, Classical.choice, Quot.sound} only.

**Positivity band (corrects an earlier error):** B = A√2 does NOT universally force a negative amplitude. All three f_k = A + A√2·cos(φ + 2πk/3) are positive iff min cosine > −1/√2 ≈ −0.7071. The physical charged-lepton phase φ ≈ 2/9 gives min cosine ≈ −0.6795 (margin 0.028). The empirical Koide formula holds with **all-positive** square roots. The algebraic identity Q = 2/3 also holds outside the band (where one f_k < 0) as a pure ring identity.

---

## 4. Triality Circuit Depth = dim(G₂)  *(Python — novel)*

**Files:** [calc/triality_map.py](calc/triality_map.py), [calc/qed_scatter.py](calc/qed_scatter.py)

`count_circuit_depth_greedy(H) = 14 = dim(G₂)` for McRae's exact 4×4 Euclidean triality quartet matrix (arXiv:2502.14016, eq. 8). The Boolean circuit cost of one triality evaluation equals the dimension of the symmetry group it stabilizes. Verified: H³ = I₄, HᵀH = I₄, greedy CSE = 4 shifts + 2 intermediates + 8 sums = 14.

**Schur's Lemma block:** The 8×8 SO(8) intertwiner T satisfying T·V_ij·T⁻¹ = L_{H(ij)} does not exist — V-rep eigenvalues ±i, S+-rep eigenvalues ±i/2 are different, ruling out any intertwiner. The COG photon operator (e₇) is translated via the 4×4 H matrix, not an 8D state vector.

**QED vertex cost ratio:** e⁻+e⁻ → 1 tick (native XOR), e⁻+μ⁻ → 15 ticks (14 triality + 1 XOR). Ratio 15 is a lower bound on m_μ/m_e. Full e-mu timing simulation: see §4f below.

**Falsified:** COG-QC-01 (m_μ/m_e = 1 + N_τ). N_τ = 14 gives 15 ≠ 207; O(N log N) bound rules out naive scaling without an arbitrary multiplier.

**⚠ Literature note (2026-02-23):** McRae's own Section 5 flags "one obstruction to making this [triality → three generations] work in the obvious way: finding outer automorphisms which act at the level of the representation, and not merely on the algebra." The N_τ = 14 = dim(G₂) result stands as proved; the generation-identification step remains an open COG-original claim.

---

## 4b. L1 Electron Calibration — C_e = 4  *(Python — novel)*

**Files:** [calc/qed_calibration.py](calc/qed_calibration.py), [calc/test_qed_calibration.py](calc/test_qed_calibration.py)

**Kick mechanism** (right-mult by e₇, verified against locked Fano convention):

| Step | Op | State | In L1? |
|------|----|-------|--------|
| 0 | — | +e₁ | yes |
| 1 | ×e₇ | +e₆ | no |
| 2 | ×e₇ | −e₁ | yes |
| 3 | ×e₇ | −e₆ | no |
| 4 | ×e₇ | +e₁ | yes ✓ |

**Results (50 tests, all passing):**
- C_e_exact = **4** symmetric exchange cycles (exact signed return)
- C_e_L1 = **2** (L1 membership return)
- Both **vacuum-independent** (n_vacuum cancels in exchange count)
- Witt pair interconversion: e₇ maps e₁↔e₆, e₂↔e₅, e₃↔e₄

**✓ Gap resolved (2026-02-24):** The full Furey state C_e = 4 is now formally proved in Lean 4 (see §4e). The C_e = 4 result holds universally for all non-zero states, including the full composite state α₁†α₂†α₃†ω. The `gap_1_electron_state` caveat in claims/muon_mass.yml is closed.

---

## 4c. E-E Dynamic Graph Simulation — Goal C Phase 1  *(Python — novel)*

**Files:** [calc/qed_ee_sim.py](calc/qed_ee_sim.py), [calc/test_qed_ee_sim.py](calc/test_qed_ee_sim.py)

Implements RFC-013 (Algebraic Vacuum, ℂ⊗O State, Dynamic Causal Spawning) for a 1D
electron-electron scattering chain.  Two electrons separated by D vacuum nodes;
both emit simultaneously; photons relay at 1 tick/hop.

**Three locked architecture decisions verified (RFC-013):**

| Decision | Implementation | Verified |
|----------|---------------|---------|
| Full ℂ⊗O state | 8-component complex numpy array | `oct_mul_full` unit tests |
| Left-multiplication | `state_next = oct_mul_full(E7, state)` | 61 tests passing |
| Vacuum relay | `e7·ω = −iω` (RFC-013 §5.1) | `test_vacuum_relay_identity` |

**Key results (61 tests, all passing):**

- **C_e = 4 with left-multiplication:** Verified for D = 0, 1, 2, 3, 4, 8 vacuum nodes.
  Consistent with Goal A (right-multiplication).  Convention-invariant as proved in RFC-013 §4.3.
- **Vacuum phase accumulation:** After cycle 1 (D=1), V[0] = −ω (2 photon hits).
  Vacuum returns to ω at cycle 2 (4 hits total).  Period = 2 exchange cycles.
- **System return period = 4:** Electrons (period 4) and vacuum lattice (period 2) have LCM = 4.
  Full system returns to initial state at Ce_exact = 4.
- **Tick formula:** total_ticks = C_e × (D+1) = 4(D+1).  Vacuum-independent orbit count.
- **Axiom of Identity:** `state_is_vacuum_orbit(state)` performs algebraic check only
  (no metadata); all 4 orbit elements {ω, −iω, −ω, +iω} correctly detected.

**COG-original observations:**
- Vacuum period (2 cycles) divides electron period (4 cycles): LCM determines return time.
- Vacuum accumulates phase (−i)^n per n photon hits, then resets every 4 hits.
- Both period-4 results (electron orbit and vacuum orbit) follow from L_{e₇}⁴ = id
  acting on all of ℂ⊗O.

---

## 4d. E-E Dynamic Graph Simulation — Goal C Phase 2 / Architecture A  *(Python — novel)*

**Files:** [calc/qed_dag_sim.py](calc/qed_dag_sim.py), [calc/test_qed_dag_sim.py](calc/test_qed_dag_sim.py)

Implements RFC-013 Architecture A (locked decision §8.1): **fully immutable-node causal DAG**.
Each photon-absorption event creates a new `Node`; no in-place mutation; full audit trail retained.
Vacuum nodes are instantiated on-demand via the SPAWN protocol (RFC-013 §6).

**Architecture A invariants verified (78 tests, all passing):**

| Invariant | D=0 | D=1 | D=2 | General |
|-----------|-----|-----|-----|---------|
| Ce_exact | 4 | 4 | 4 | 4 (all D) |
| total_ticks | 4 | 8 | 12 | 4(D+1) |
| node_count | 10 | 14 | 26 | — |
| edge_count | 8 | 16 | 24 | 8(D+1) = 2·total_ticks |
| spawn_count | 0 | 1 | 2 | D |

**SPAWN protocol confirmed:** `spawn_count == D` for all D = 0..4.
Each vacuum position fires SPAWN exactly once (first photon arrival).  Subsequent nodes at
that position are created by absorption, not SPAWN.

**Vacuum trajectory (D=1, pos=1):**
- Tick 1 (SPAWN, 2 simultaneous hits): state = −ω,  proper_time = 2
- Tick 3 (2 hits): state = +ω,  proper_time = 4   ← first return to OMEGA (vacuum_period_tick = 4)
- Tick 5 (2 hits): state = −ω,  proper_time = 6
- Tick 7 (2 hits): state = +ω,  proper_time = 8

**Electron trajectory (D=0, pos=0) — full immutable audit trail:**
- Tick 0 (root): +e₁, pt=0
- Tick 1: −e₆, pt=1
- Tick 2: −e₁, pt=2
- Tick 3: +e₆, pt=3
- Tick 4: +e₁, pt=4  ← exact return → Ce_exact = 4

**Simultaneous-arrival grouping confirmed:** When n photons arrive at the same position in the
same tick, ONE new node is created with L_{e₇} applied n times (by octonion alternativity,
sequential order irrelevant for e₇·e₇ = −1).

**Invariant:** `edge_count == 2 × total_ticks` holds for all D tested (0..3): exactly 2 photons
in flight at all times (one from each electron, relayed end-to-end).

---

## 4f. E-Mu DAG Timing Simulation — Goal B  *(Python — novel)*

**Files:** [calc/emu_dag_sim.py](calc/emu_dag_sim.py), [calc/test_emu_dag_sim.py](calc/test_emu_dag_sim.py)

Implements RFC-012 Goal B: electron-muon causal exchange in a 1D DAG with asymmetric vertex costs.

**Model (queued-photon):**
- Electron (V rep): V_e = 1 tick per vertex — native L_{e₇} application.
- Muon (S+ rep): V_mu = 15 ticks per vertex — 1 tick absorption + 14 ticks triality overhead.
- Photons that arrive while a particle is processing are queued and absorbed at the next free tick.

**Key results for D=0 (30 tests, all passing):**

| Metric | Value |
|--------|-------|
| E absorption ticks | [1, 17, 32, 47] |
| Mu absorption ticks | [1, 16, 31, 46] |
| E orbit time | 47 ticks |
| Mu orbit time | 46 ticks |
| e-e baseline | 4 ticks |
| timing_ratio_max | 11.75 |
| vertex_cost_ratio | 15.0 |
| gap_to_experimental | ~13.78× |

**For D=1:** E ticks [2, 19, 34, 49], Mu ticks [2, 17, 32, 47]. Both return to initial.

**Algebraic closure confirmed:** Both particles return to initial state after exactly 4 absorptions
(Universal C_e = 4 theorem), for any non-zero initial state including the full Furey states.

**Gap quantified:** vertex_cost_ratio = 15 is a **confirmed lower bound** on m_μ/m_e.
The remaining gap factor ≈ 13.78× to the experimental value 206.768 requires DAG topology
beyond single-vertex timing. The timing ratio decreases as D increases (→ 1 as D→∞),
ruling out the pure vertex-cost mechanism as a complete explanation.

---

## 4e. Full Furey Electron State and Universal C_e = 4 Theorem  *(Lean 4 + Python — novel)*

**Files:** [CausalGraphTheory/Spinors.lean](CausalGraphTheory/Spinors.lean), [calc/furey_electron_orbit.py](calc/furey_electron_orbit.py), [calc/test_furey_electron_orbit.py](calc/test_furey_electron_orbit.py)

Resolves `gap_1_electron_state` (claims/muon_mass.yml): whether C_e = 4 is specific to the
e₁ basis component or holds for the full Furey charged-lepton state.

**UNIVERSAL C_e THEOREM (formally proved in Lean 4, verified in Python):**

By the **left-alternative law** of C(×)O, for all x:
$$L_{e_7}^2(x) = e_7 \cdot (e_7 \cdot x) = (e_7 \cdot e_7) \cdot x = -x$$
Therefore L_{e₇}⁴ = id. Period 1 and 2 would require x = 0. Hence **every non-zero state has orbit period exactly 4** under L_{e₇}.

**Lean 4 proof stack** (`CausalGraphTheory/Spinors.lean`, axioms: {propext, Classical.choice, Quot.sound}):

| Theorem | Statement |
|---------|-----------|
| `e7LeftOp_square_eq_neg_one` | e7 * e7 = -1 in CO |
| `e7_left_twice_neg` | e7 * (e7 * x) = -x for all x |
| `e7_left_four_id` | e7^4(x) = x for all x |
| `e7_left_period_two_impossible` | e7^2(x) ≠ x for x ≠ 0 |
| `e7_left_period_one_impossible` | e7(x) ≠ x for x ≠ 0 |
| **`universal_Ce_period_four`** | **Period is exactly 4 for all x ≠ 0 (left)** |
| **`universal_Ce_right_period_four`** | **Period is exactly 4 for all x ≠ 0 (right)** |
| `fureyElectronStateDoubled_closed_form` | α₁†·(α₂†·(α₃†·ω)) = −8i·(2ω†) at 16× scale |
| `fureyDualElectronStateDoubled_closed_form` | α₁·(α₂·(α₃·ω†)) = −8i·(2ω) at 16× scale |
| `gen2State_proportional_idempotent` | ψ_μ² = −4ψ_μ (muon is anti-idempotent) |
| `gen2StateQuadruple_ne_zero` + period corollaries | Muon state inherits exact period 4 |

**Witt basis properties verified (26 tests, all passing):**

| Property | Result |
|----------|--------|
| αⱼ · ω = 0 for j = 1,2,3 | lowering operators annihilate vacuum ✓ |
| αⱼ† · ω = αⱼ† | raising operators are elements of S = C(×)O · ω ✓ |
| ω² = ω, (ω†)² = ω† | both vacua are idempotent ✓ |
| α₁ · (α₁† · ω) = ω | raise-then-lower returns vacuum ✓ |

**Full Furey electron state computed (CONVENTIONS.md §6):**

$$\psi_e = \alpha_1^\dagger \cdot (\alpha_2^\dagger \cdot (\alpha_3^\dagger \cdot \omega)) = -i\,\omega^\dagger$$

Derivation chain (all machine-checked):
- α₃† · ω = α₃†  (ω acts as right identity on the ideal S)
- α₂† · α₃† = ½(e₁ − ie₆)  (Fano product, verified)
- α₁† · ½(e₁ − ie₆) = −i·ω†  (final product)

**Orbit:** {−iω†, ω†, +iω†, −ω†}, period 4.  **Consistent with C_e = 4.**

**Consequence for muon mass ratio:**
C_e(e₁ component) = C_e(full Furey state) = **4 universally**. The mass ratio m_μ/m_e
cannot arise from state-orbit period alone — triality overhead or DAG topology is required.
This closes `gap_1_electron_state` and sharpens the Phase 3 problem.

---

## 4g. Finster Discrete Causal Action — CFS Lagrangian Test  *(Python — novel)*

**Files:** [calc/cfs_action.py](calc/cfs_action.py), [calc/test_cfs_action.py](calc/test_cfs_action.py)

Implements the Finster CFS Lagrangian (arXiv:2201.06382, 2403.00360) for the COG e-mu system.
For rank-1 projectors x = |ψ_x⟩⟨ψ_x|, y = |ψ_y⟩⟨ψ_y| on ℂ⁸ with n-dimensional spin space:

$$\mathcal{L}(x,y) = |c|^2 - \frac{|c|^4}{n}, \quad c = \langle\psi_x|\psi_y\rangle$$

**Orbit structure (4 steps of L_{e₇} from e₁):**

| Pair | Overlap |c| | L(n=8) |
|------|---------|---------|--------|
| (0,1) | 0 | 0 |
| (0,2) | 1 (antiparallel) | 7/8 |
| (0,3) | 0 | 0 |
| (1,2) | 0 | 0 |
| (1,3) | 1 (antiparallel) | 7/8 |
| (2,3) | 0 | 0 |

Only antipodal pairs (0,2) and (1,3) contribute. Total orbit action:

$$S(n) = 2\left(1 - \frac{1}{n}\right)$$

**Key results (29 tests, all passing):**

| Model | Prediction | vs. 206.768 |
|-------|-----------|-------------|
| Simple L-ratio S(n_μ)/S(n_e) | **bounded above by ~2** | ruled out (100× too small) |
| Effective m² model: (V_μ/V_e)² = (15/1)² | 225 | 8.8% above |
| N_TAU² = 14² | 196 | 5.2% below |
| **N_TAU × V_μ = 14 × 15** | **210** | **1.56% above** |

**Main findings:**

1. **Simple L-ratio ruled out:** The ratio S(n_μ)/S(n_e) is bounded above by 1/(1−1/n_e). For any n_e ≥ 2 this is ≤ 2, far below 206.768. The CFS Lagrangian alone (varying only spin dimension) cannot produce the muon mass ratio.

2. **Effective m² model:** If each vertex tick corresponds to one spacetime event and S ~ m² (Finster discrete Dirac sphere scaling), then m_μ/m_e ≈ √(S_μ/S_e) = V_μ/V_e = 15. To match 206.768 requires (m_μ/m_e)² = 225 = V_μ². This is 8.8% above the experimental value.

3. **Closest COG integer model:** N_TAU × V_μ = 14 × 15 = 210 sits 1.56% above 206.768. This is the product of the two COG-derived constants (triality circuit depth × muon vertex cost) but lacks a derivation from first principles.

**Literature basis:**
- arXiv:2201.06382 (Finster 2022): Discrete Dirac spheres; S ~ m² for m equally-spaced minimizers.
- arXiv:2503.00526 (Finster 2025): Action-driven flows; non-convexity, natural cycles consistent with COG 4-cycle.
- arXiv:2403.00360 (Finster et al. 2024): CFS + octonion bridge paper; octonionic vacuum symmetry + CFS causal action.

---

## 4h. Photon Eigenvalue Structure and Witt Operator Algebra  *(Lean 4 — novel)*

**File:** [CausalGraphTheory/Spinors.lean](CausalGraphTheory/Spinors.lean), [CausalGraphTheory/WittBasis.lean](CausalGraphTheory/WittBasis.lean)

**Claims:** [claims/vacuum_symmetry_from_octonions.yml](claims/vacuum_symmetry_from_octonions.yml) (CFS-003), [claims/subalgebra_detection.yml](claims/subalgebra_detection.yml) (ALG-002)

### Photon operator eigenvalues

The vacuum projectors ω and ω† are **eigenstates** of the photon operator e7:

| Theorem | Statement | Eigenvalue |
|---------|-----------|-----------|
| `e7Left_on_omegaDoubled` | e7 · ω = −i · ω | −i |
| `e7Right_on_omegaDoubled` | ω · e7 = −i · ω | −i |
| `e7Left_on_leftVacConjDoubled` | e7 · ω† = +i · ω† | +i |
| `e7Right_on_leftVacConjDoubled` | ω† · e7 = +i · ω† | +i |

Left and right action agree for both projectors. This is a nontrivial algebraic fact: ω and ω† are in an especially symmetric position relative to e7 in the Fano structure. The ±i eigenvalue split is the algebraic origin of particle/antiparticle charge distinction — the vacuum sector (ω) carries charge −i, the conjugate vacuum (ω†) carries +i.

**Corollaries (period-4 on projectors):** `vacuum_orbit_exact_period_four`, `leftVacConjDoubled_left/right_orbit_exact_period_four` — the projectors themselves have exact period 4 under both left and right e7 action, consistent with the universal theorem.

**Scaled idempotence:** `leftVacConjDoubled_idempotent_scaled` — (2ω†)² = 2·(2ω†), confirming ω† is a projector at the scale used in the Lean definitions.

### Witt operator nilpotency (Grassmann structure)

| Theorem | Statement | Physical meaning |
|---------|-----------|-----------------|
| `wittLower_nilpotent` | (2αⱼ)² = 0 for j = 0,1,2 | Cannot annihilate same color-charge twice |
| `wittRaise_nilpotent` | (2αⱼ†)² = 0 for j = 0,1,2 | Cannot create same color-charge twice |
| `wittRaise_right_identity_scaled` | (2αⱼ†)·(2ω) = 2·(2αⱼ†) | Raising operator is idempotent on ω |

These are the Grassmann/Pauli-exclusion identities at the algebraic level. All proved by `fin_cases k` + `norm_num` over ℤ (component-by-component).

---

## 4i. Witt-Pair Gate Theorems and Generation Separation  *(Lean 4 - novel)*

**Files:** [CausalGraphTheory/WittPairSymmetry.lean](CausalGraphTheory/WittPairSymmetry.lean), [CausalGraphTheory/GenerationSeparation.lean](CausalGraphTheory/GenerationSeparation.lean)

This batch adds finite gate checks and state-separation lemmas in standalone modules.

| Theorem | Result |
|---------|--------|
| `wittPair_cyclic_perm_is_fano_aut` | The orientation-preserving cyclic map of Witt pairs is a Fano automorphism (`true`). |
| `wittPair_cyclic_perm_flip_not_fano_aut` | A closely-related cycle with one internal pair flip is not a Fano automorphism (`false`). |
| `wittPair0_supporting_line` | Pair `(e6,e1)` sits on line 2. |
| `wittPair1_supporting_line` | Pair `(e2,e5)` sits on line 4. |
| `wittPair2_supporting_line` | Pair `(e3,e4)` sits on line 5. |
| `wittPairs_on_distinct_lines` | Distinct Witt pairs are supported on distinct Fano lines. |
| `gen1_ne_gen2` | Full generation-1 (Furey electron) state is not generation-2 (muon) state. |
| `gen1dual_ne_gen2` | Dual generation-1 state is not generation-2 state. |
| `gen1_ne_gen1dual` | Primal and dual generation-1 states are distinct. |

Interpretation:
- The "is it in Aut(Fano)?" question is now split cleanly by map choice: one natural pair-cycle is allowed, a nearby flipped variant is forbidden.
- The generation-sector states are now formally separated as distinct microstates in Lean.

---

## 4j. Stepwise Furey Chain Proofs and Scalar Bridges  *(Lean 4 - novel)*

**File:** [CausalGraphTheory/FureyChain.lean](CausalGraphTheory/FureyChain.lean)

This batch factors the three-operator Furey constructions into explicit intermediate-state theorems.

| Theorem | Statement |
|---------|-----------|
| `alpha3Dag_mul_omega_step` | `(2α₃†)·(2ω)` explicit intermediate state |
| `alpha2Dag_mul_step1` | `(2α₂†)·(step1)` explicit intermediate state |
| `alpha1Dag_mul_step2` | `(2α₁†)·(step2) = -8i·(2ω†)` |
| `fureyElectronStateDoubled_chain` | full primal chain assembled to closed form |
| `alpha3_mul_omegaDag_step` | `(2α₃)·(2ω†)` explicit intermediate state |
| `alpha2_mul_dual_step1` | `(2α₂)·(dual step1)` explicit intermediate state |
| `alpha1_mul_dual_step2` | `(2α₁)·(dual step2) = -8i·(2ω)` |
| `fureyDualElectronStateDoubled_chain` | full dual chain assembled to closed form |

Two scalar-bridge lemmas were added so the `-8i·(2ω†)` and `-8i·(2ω)` forms are now proved as actual scalar actions, not only by identical component definitions:
- `negEightIOmegaDagDoubled_scalar_bridge`
- `negEightIOmegaDoubled_scalar_bridge`

---

## 4k. Vacuum-Stabilizer Action on Witt-Pair Labels  *(Lean 4 - novel)*

**File:** [CausalGraphTheory/VacuumStabilizerAction.lean](CausalGraphTheory/VacuumStabilizerAction.lean)

This batch formalizes the induced action of the 24-element vacuum stabilizer on the
three Witt-pair color labels.

| Theorem | Result |
|---------|--------|
| `vacuumStabilizerList_count` | Reconstructed stabilizer list has size 24. |
| `wittPair_cyclic_in_vacuumStabilizerList` | The Witt-pair cycle element is explicitly in the stabilizer. |
| `wittPair_cyclic_inducedColorPerm` | That element induces `[0,1,2] -> [1,2,0]` on color labels. |
| `inducedColorPerms_count` | Distinct induced color permutations count is 6. |
| `inducedColorPermFiberSizes_eq` | Uniform fibers: each of the 6 permutations has 4 preimages in the 24-element stabilizer. |
| `inducedColorPerms_perm_S3` | Induced action equals all permutations of three labels (S3), up to list order. |
| `color_perm_realized_by_vacuum_stabilizer` | Every S3 label permutation has a stabilizer preimage. |

Interpretation:
- The previously-open "is Z3 present in the vacuum stabilizer explicitly?" question is now closed.
- More strongly, the stabilizer induces full S3 on unordered Witt-pair labels.
- This does not conflict with `wittPair_cyclic_perm_flip_not_fano_aut`: a specific pointwise flip candidate can fail even while full label-level S3 is realized by other stabilizer elements.

---

## 4l. Vacuum-Stabilizer Quotient Checks and Transposition Witness  *(Lean 4 - novel)*

**File:** [CausalGraphTheory/VacuumStabilizerQuotient.lean](CausalGraphTheory/VacuumStabilizerQuotient.lean)

This batch upgrades the stabilizer-action story from raw counts to finite structural checks.

| Theorem | Result |
|---------|--------|
| `vacuumStabilizer_closed_comp_bool` | Stabilizer is closed under composition (exhaustive check). |
| `idPermList_in_vacuumStabilizer` | Identity permutation is in the stabilizer. |
| `inverseInVacuumStabilizer_spec_bool` | Two-sided inverse witness exists in stabilizer (finite search). |
| `inducedColorPerm_hom_on_vacuumStabilizer_bool` | Induced color action passes homomorphism check. |
| `stabilizerKernelList_count` | Kernel of induced action has size 4. |
| `stabilizerKernel_normal_bool` | Kernel is normal under conjugation (finite check). |
| `stabilizer_kernel_index_six` | Quotient cardinality is 6. |
| `wittPair_swap01_in_vacuumStabilizer` | Explicit transposition witness is in the stabilizer. |
| `wittPair_swap01_inducedColorPerm` | Witness induces `[0,1,2] -> [1,0,2]`. |

Interpretation:
- The stabilizer-to-color map is now backed by finite closure/inverse/hom/normality checks.
- A transposition is explicitly realized, not just inferred from cardinality.

---

## 4m. Koide Group-Bridge Lemmas  *(Lean 4 - novel)*

**File:** [CausalGraphTheory/KoideGroupBridge.lean](CausalGraphTheory/KoideGroupBridge.lean)

This batch adds reusable algebraic bridge lemmas for KOIDE-001:

| Theorem | Result |
|---------|--------|
| `wittPair_cyclic_color_powers` | Explicit Z3 cycle powers on color labels. |
| `z3_sumprod_implies_sumsq` | From Z3 constraints: `c0^2 + c1^2 + c2^2 = 3/2`. |
| `brannen_sos_from_z3_and_b2` | Z3 + `B^2=2` implies Koide SOS condition. |
| `brannen_koide_from_z3_and_b2` | Pipeline corollary to Koide `Q=2/3` equation. |

Interpretation:
- The Koide bridge now has explicit reusable lemmas rather than one monolithic argument.
- Remaining blocker is still deriving the Z3 ansatz from COG dynamics, not algebraic closure once ansatz is supplied.

---

## 4n. Vacuum-Stabilizer S4 Identification via Non-Vacuum Lines  *(Lean 4 - novel)*

**File:** [CausalGraphTheory/VacuumStabilizerS4.lean](CausalGraphTheory/VacuumStabilizerS4.lean)

This batch identifies the stabilizer type through its action on the four Fano lines not incident to e7.

| Theorem | Result |
|---------|--------|
| `nonVacuumLines_eq_canonical` | Non-vacuum lines are exactly `[0,1,3,6]`. |
| `inducedNonVacLinePerms_count` | 24 distinct induced permutations on that 4-line set. |
| `inducedNonVacLinePerms_perm_S4` | Induced action equals all permutations of 4 labels (S4). |
| `inducedNonVacLinePerm_hom_on_vacuumStabilizer_bool` | Homomorphism check passes for line-action map. |
| `inducedNonVacLinePerm_faithful_bool` | Action is faithful (only identity acts trivially). |
| `liftFromS4Perm_right_inv_bool` | Explicit lift S4 -> stabilizer is right-inverse to induced action. |
| `liftFromS4Perm_left_inv_bool` | Lift is also left-inverse on stabilizer list (explicit witness). |
| `vacuumStabilizer_action_on_nonVacLines_S4` | Combined S4-surjective + faithful action summary theorem. |
| `vacuumStabilizer_explicit_iso_S4_bool` | Combined explicit isomorphism witness summary (two-sided inverse checks). |

Interpretation:
- In this encoding, the most direct machine-checked identification is: the 24-element vacuum stabilizer acts faithfully as S4 on non-vacuum lines.
- This explains the order histogram `(1:1, 2:9, 3:8, 4:6)` and the involution count `9`.
- An explicit lift map from S4 permutations back to stabilizer elements is now formalized and validated by two-sided inverse checks.
- The prior SL(2,3) label remains under review pending an explicit isomorphism proof in this formalization.

---

## 5. Previously Known Results, Verified in COG Framework

*These confirm internal consistency of the algebraic machinery but are not novel claims.*

| Result | Standard reference | Method in COG |
|--------|--------------------|---------------|
| Fano plane: 7 lines, 3 pts/line, 2-point uniqueness | Combinatorics | `decide` |
| Octonion alternativity (left, right, flexible) over any comm. ring | Schafer 1966 | `ring` |
| 7/35 associative imaginary triples | Known | `decide` |
| Witt basis vacuum idempotent ω² = ω | Furey 2019 | `decide` (integer arith.) |
| Muon sector anti-idempotent ψ_μ² = −ψ_μ | Furey 2019, Eq. 21 | `rfl` after `fin_cases` on Fin 8 |
| Witt operators nilpotent: αⱼ² = (αⱼ†)² = 0 | Furey 2019 / Grassmann algebra | `fin_cases` + `norm_num` over ℤ |
| Vacuum projectors ω, ω† are ±i eigenstates of e7 | COG-original formal proof | `fin_cases` + `norm_num` over ℤ |
| Z3 character table orthogonality | Representation theory | NumPy (1e-10) |
| Vacuum stabilizer order profile (24 elements): `(1:1, 2:9, 3:8, 4:6)` | Finite group diagnostics | `native_decide` |
| Koide Q=2/3 ⟺ sum-of-squares identity over any ring | Koide 1982 | `ring` + `linarith` |
| Mass monotonicity: more ticks → more mass | COG axiom | Lean structural |

---

## 6. Open / Blocked

| Claim | Status | Note |
|-------|--------|------|
| Koide: COG update rules force Z3 ansatz | **Blocked** | Need COG graph symmetry derivation -> sum c_k = 0, sum c_j*c_k = -3/4 (algebraic bridge lemmas now proved once ansatz is given) |
| m_μ/m_e from DAG orbit length | **Partial** | vertex_cost_ratio=15 confirmed lower bound; timing_ratio_max=11.75 (D=0); gap ~13.78× to 206.768; full mechanism open |
| C_e for the full Furey electron state α₁α₂α₃ω†ω | **Resolved** | Universal C_e = 4 theorem: L_{e₇}² = −id by left-alternative law; ALL non-zero states have period 4 (see §4e, muon_mass.yml gap_1_electron_state) |
| e₇ right-mult = photon absorption | **COG-original** | Algebraically consistent; no direct Furey or arXiv precedent found (search 2026-02-23) |
| McRae triality → three generations | **Open (obstacles noted)** | McRae §5 explicitly flags representation-level obstruction; N_τ = 14 operator-translation result unaffected |
| Dixon X-product orbit periods ≈ 206 | **Unverified** | Full text of hep-th/9410202 not read; abstract makes no mass-ratio claims; connection unsupported |
| Three generations in COG (GEN-002) | **Partial** | Label-level action is stronger now: the vacuum stabilizer induces full S3 on the 3 Witt-pair labels (`inducedColorPerms_perm_S3`) and contains an explicit transposition witness (`wittPair_swap01_inducedColorPerm`). Remaining open issue is a state-level generation operator, not label-level S3 existence. |
| Vacuum stabilizer isomorphism label | **Under review** | Finite proof shows order profile `(1:1, 2:9, 3:8, 4:6)` and involution count `9` (`vacuumStabilizer_involution_count`). The historical `SL(2,3)` label is not yet machine-verified in this encoding, and `SL(2,3)/Q8 ~= Z3` is therefore not currently formalized. |
| CFS Lagrangian → m_μ/m_e | **Partial** | Simple L-ratio bounded by ~2 (ruled out); N_TAU×V_μ=210 is 1.56% above 206.768 (closest integer model, no derivation yet); full spacetime-density mechanism open |

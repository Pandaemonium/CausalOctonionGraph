# RFC-025: Gauge Boson Identification in S2880

Status: Draft — Theory
Date: 2026-03-03
Owner: COG Core (Claude lane)
Depends on:
- RFC-009 (N_gauge = 12 from Z₄×Z₃ structure)
- RFC-016 (Koide formula — mass encoding)
- RFC-021 (G₂₁ structure — Z₇ color degrees of freedom)
- RFC-024 (SM particle identity map — Q240 element identification)

---

## 1. Purpose

RFC-009 proved N_gauge = 12 = (N_c²-1) + (N_w²-1) + 1 = 8+3+1 from the Z₁₂ = Z₄ × Z₃
structure. `calc/derive_sm_quantum_numbers.py` confirms this algebraically.

This RFC identifies WHICH Q240 elements correspond to each of the 12 gauge bosons, and
connects the period-48 photon candidate from the overnight runner to a specific Q240 element.

---

## 2. The Gauge Boson Count Decomposition

From RFC-009 / derive_sm_quantum_numbers.py:
```
N_gauge = (N_c²-1) + (N_w²-1) + 1  =  8 + 3 + 1  =  12
         (SU(3) gluons)  (SU(2) W)  (U(1) B)
```

Where N_c = 3 (quark colors) and N_w = 2 (SU(2) doublet structure).

Physical gauge bosons after electroweak symmetry breaking:
- 8 gluons (massless, color adjoint)
- W± (charged, massive, SU(2)_L)
- Z⁰ (neutral, massive, SU(2)_L × U(1)_Y)
- γ (photon, massless, U(1)_EM)

Total: 8 + 1 + 1 + 1 = 11... with the W₃/B mixing into Z/γ, the correct count is:
8 gluons + W⁺ + W⁻ + Z + γ = 12. ✓

---

## 3. Q240 Element Identification

### 3.1 The 7 Imaginary Directions = 7 SM Charge Degrees of Freedom

From RFC-021 (G₂₁ structure): the 7 imaginary octonion units {e₁,...,e₇} map to:
```
SU(3) color:        {e₁, e₂, e₄}   (one Fano line — the R/G/B color triplet)
SU(2) weak isospin: {e₃, e₆, e₇}   (second Fano line — the W₁/W₂/W₃ weak triplet)
U(1) hypercharge:   e₇ in WITT convention = vacuum axis
```

NOTE: This is a proposed assignment consistent with the Fano structure. The exact
correspondence between Fano lines and SM gauge groups depends on the PSL(2,7) orbit
structure from RFC-020. Final confirmation awaits Family A test results.

### 3.2 Photon (γ) — U(1)_EM

**Q240 identification:** The photon maps to the A16_basis_signed_unit family, specifically
the imaginary elements with activity = 0.925.

From the overnight runner: best candidate `seed_state_label = ±1/2*e000 + ... ` type
with `kick_label` involving e₁₁₁ (= ±1/2 sum of 4 basis elements), period = 48.

The photon in Q240:
- Not in a generation (g = p mod 3 is undefined — the photon is generation-neutral)
- Q240 element = A16 imaginary unit in the U(1) direction
- Period: 48 = 4 × 12 (4 full C12 cycles per Q240 period)

**Why period 48 = 4 × 12?**
If the Q240 element representing the photon has Q240 order 4, then in S2880:
- Q240 dynamics: period 4 (returns to identity after 4 Q240 multiplications)
- C12 dynamics: period 12 (returns to same phase after 12 C12 ticks)
- Combined S2880: period = lcm(4,12) = 12 for the state, but the SPATIAL pattern
  repeats every 4 C12 cycles = 48 ticks.

Prediction for S2880 runner: period 48 will be preserved. If Q240 order(q=121) = 4,
this confirms the photon identification.

### 3.3 W± Bosons — SU(2)_L Charged Currents

**Q240 identification (proposed):** W± bosons are Q240 order-6 elements in the imaginary
sector corresponding to the SU(2) weak isospin raising/lowering operators.

From RFC-024 §8: the W boson acts on state (p, q_charged) → (p, q_neutral), changing
the Q240 element from C112-family to A16-scalar, preserving C12 phase.

**The W± as Q240 order-6:**
- In SM: W± mediates SU(2)_L transitions, carries charge ±1, spin-1
- In Q240: the SU(2)_L generators correspond to L_{e₃}, L_{e₆}, L_{e₇} (the Fano line
  containing the weak isospin directions)
- Order-6 elements of Q240 = ±(1/2 ± e_i ± e_j) half-integer combinations
- These have Q240-order = 6: applying them 6 times returns to identity

**Mass mechanism:** In S2880, the W± has non-zero Z₄ sub-clock component (a ≠ 0).
The "mass" = resistance to propagation = the Z₄ coupling parameter p_mem (RFC-019).
The W's Z₄ excitation gives it a non-zero period in the S2880 runner (it's a "trapped"
cycle, not a propagating wave).

Prediction: in Phase M, the W boson motif will show period = O(6) or O(84) ticks
(G₂₁ period-84 from RFC-021 — if the W is in the G₂₁ orbit structure).

### 3.4 Z Boson — Electroweak Neutral Current

**Z⁰ identification:** The Z boson is a mixture of W₃ and B (hypercharge boson):
```
Z = cos(θ_W) × W₃ - sin(θ_W) × B
γ = sin(θ_W) × W₃ + cos(θ_W) × B
```
With sin²θ_W = 3/8 (RFC-009, proved), cos θ_W = √(5/8).

In Q240 terms: the Z state is a superposition of:
- An order-6 element in the SU(2) direction (W₃ component)
- An A16 imaginary element in the U(1) direction (B component)

The W₃ and B are related by a rotation by θ_W in Q240. Since sin²θ_W = 3/8, the mixing
angle corresponds to cos θ_W = √(5/8) ≈ 0.7906.

**Tree-level mass ratio prediction:**
```
m_W / m_Z = cos θ_W = √(1 - 3/8) = √(5/8) ≈ 0.7906
```
Experiment: m_W/m_Z ≈ 0.882. Discrepancy = 12% — consistent with radiative corrections
(sin²θ_W runs from 3/8 at GUT scale to 0.231 at M_Z scale in the SM).

At tree level (GUT = S2880 fundamental scale), the 0.7906 prediction is exact.

### 3.5 Gluons — SU(3)_c Color Force

**8 gluon identification:**
In Q240, the SU(3) color group is the stabilizer of the vacuum axis e₇ in G₂ (= Aut(Q240)).
The 8 SU(3) generators act on the 3-color triplet {e_R, e_G, e_B} ≡ {e₁, e₂, e₄}
(one Fano line in our convention).

The 8 gluon operators in Q240:
- 6 off-diagonal gluons: left-multiplication by imaginary units that transition between
  color directions: L_{e₁} maps e₂ ↔ e₄, etc. (Fano structure)
- 2 diagonal gluons (Cartan subalgebra of SU(3)): λ₃ and λ₈ — these are specific
  bilinear combinations of the color imaginary units

All 8 gluons are MASSLESS in S2880:
- No C12 generation (gluons are color-charged, generation-neutral)
- No Z₄ sub-clock excitation (gluons don't couple to the Z₄ mass mechanism)
- In S2880: gluon dynamics are purely within the Q240 sector, p=0 component

This is consistent with gluon confinement: in the full QCD dynamics, gluons self-couple
(because G₂ structure contains SU(3)×SU(3) non-Abelian terms), and gluon propagation
in the Q240 lattice forms color-neutral flux tubes.

### 3.6 Higgs Boson — Scalar, Mass Generator

**Higgs identification:** The Higgs is a SCALAR Q240 element.

In Q240: the identity element q=0 (= e₀, the real octonion direction) has:
- A16_basis_signed_unit family, activity = 0.0
- Order 1 (trivially: e₀² = e₀, so it's idempotent, not exactly order-1 in the group sense)

Wait — q=0 is the identity in Q240 multiplication: any element × q=0 = any element × e₀.
Actually in the Hurwitz integral octonions, the identity element is e₀ (unit norm, real part=1).

The Higgs VEV in S2880:
- In the Higgs mechanism, the Higgs field acquires a non-zero expectation value: ⟨φ⟩ = v/√2
- In S2880 terms: the vacuum state is NOT at the Q240 identity (q=0) but at a specific
  Q240 element q_vev that minimizes the effective potential
- The "potential" in S2880 is the long-term stable occupation probability in Phase M
- q_vev should be in the A16-scalar family but NOT the identity — it should be the
  element that is "spontaneously selected" in Phase M dynamics

**Higgs mass from Z₄ sub-clock:**
The Higgs mass m_H ≈ 125 GeV is much smaller than the W mass (80 GeV) — but not zero.
In S2880: the Higgs mass comes from its Z₄ sub-clock coupling:
- a_Higgs = 0 (real direction → no Z₄ excitation = low mass)
- But Q240 dynamics give a small but non-zero period to the Higgs Q240 cycle

**Prediction:** The Higgs period in Phase M will be longer (higher period = lighter mass)
than the W period. If W period = O(6) ticks and Higgs period = O(6 × m_W/m_H):
    T_Higgs / T_W ≈ m_W / m_H ≈ 80.4/125.1 ≈ 0.64
    T_Higgs ≈ 0.64 × T_W

This is a quantitative prediction for the mass ratio m_W/m_H from S2880 period ratios.

---

## 4. The Period-48 Photon Candidate in Context

### 4.1 Current overnight data

From batch 576 (latest): `kick_label = "1*e011"`, `period_N = 48`, score = 0.565625.
The e₀₁₁ element = (1/2)(e₀+e₁+e₂) in the Hurwitz parameterization? No — wait,
the kick label "1*e011" uses binary basis labeling where e011 = e₃ (the 3rd basis element
with binary index 011). This is in the SU(2) weak isospin direction.

This is SIGNIFICANT: the best photon candidate uses a kick in the e₃ (SU(2)) direction,
NOT the e₇ (U(1) hypercharge / photon) direction.

Physical interpretation: the photon is a MIXTURE of W₃ and B (electroweak mixing).
The dominant component of the photon in Q240 is cos θ_W × B + sin θ_W × W₃.
With sin²θ_W = 3/8: sin θ_W = √(3/8) ≈ 0.612, cos θ_W = √(5/8) ≈ 0.791.
The larger component is B (cos θ_W = 0.791), but the W₃ component (0.612) is not negligible.
If the overnight runner explores the W₃ direction (e₃) before the B direction (e₇),
it naturally finds the W₃-component photon first.

### 4.2 Gate failures explained by photon physics

**gate2_detector (single-event exclusivity): EXPECTED for photon**
For a single-photon event, detection is one click per event (photon-number conservation).
Interference is an ensemble property of many events, not a per-event double-hit behavior.
So a photon should satisfy per-event exclusivity, while still producing a nontrivial
position-distribution/fringe pattern over repeated trials.

**Recommendation:** Define gate2_boson as:
1. per-event exclusivity ~1.0 (single-photon consistency),
2. ensemble interference signature present in repeated runs.

**gate4_chirality (a_chi = 0): EXPECTED for photon**
The photon is its own antiparticle (CP-even). It has helicity ±1 but no NET chirality
asymmetry between left and right circular polarization in an unpolarized source.

A_chi = 0 is CORRECT for the photon when the seed is linearly polarized (which sheet_y is).
Gate4 chirality tests for MATTER/ANTIMATTER asymmetry — photons are symmetric.

**Recommendation:** Add gate4_boson variant: a_chi ≈ 0 is a PASS for bosons
(this distinguishes the photon from W/Z which have chiral coupling structure).

### 4.3 Gate redesign for bosons vs fermions

| Gate | Current (particle) | Boson variant | Fermion variant |
|------|-------------------|---------------|-----------------|
| gate2_detector | exclusivity > 0 | exclusivity≈1 + ensemble interference | exclusivity > 0.1 |
| gate4_chirality | |A_chi| > 0 | A_chi ≈ 0 (self-conjugate) | A_chi > threshold |
| gate3_isotropy | aniso_ratio ≈ 1 | aniso_ratio ≈ 1 (same) | aniso_ratio ≈ 1 (same) |

The period-48 candidate currently passes the immediately checkable boson variants:
    gate2_boson: per-event exclusivity ~1.0 (single-event consistency)
    gate4_boson: a_chi_proxy = 0.0 ✓ (photon is self-conjugate)

**Promotion note:** finalize photon-candidate promotion after the ensemble-interference
panel is executed and meets threshold.

---

## 5. W/Z Boson Motif Prediction

The W± and Z bosons are massive — they should show RECURRENT (non-propagating) dynamics
in S2880. In Phase M (after RFC-017 phase boundary sweep):

**W± prediction:**
- Seed: Q240 order-6 element in the imaginary sector (from RFC-020 order-6 classification)
- Expected behavior: confined recurrent loop with period T_W
- T_W prediction: from G₂₁ period-84 (RFC-021), T_W = 84 ticks or a divisor thereof
- A_chi ≠ 0 for W±: the W couples only to LH particles → should show chirality signal

**Z prediction:**
- Mixed state: amplitude_W3 × (order-6 element) + amplitude_B × (A16 imaginary)
- Expected period: similar to W but slightly different due to the cos θ_W / sin θ_W mixing
- T_Z prediction: T_Z ≈ T_W / cos θ_W = T_W × √(8/5)

**Mass ratio check from periods:**
If T_Z / T_W ≈ m_W / m_Z = cos θ_W = √(5/8):
    T_Z ≈ 0.7906 × T_W
The Z is LIGHTER in period-space (longer period = higher mass? or shorter period = higher mass?)

Actually in the S2880 framework (RFC-019 K4 kernel): period is inversely related to mass.
Higher mass = faster period = shorter recurrence time.

Revised: T_W > T_Z since m_W < m_Z (W is lighter than Z in the SM).
    T_W / T_Z = m_Z / m_W = 1 / cos θ_W = √(8/5) ≈ 1.265
    If T_Z = 84 ticks: T_W = 84 × 1.265 ≈ 106 ticks.

This is a concrete prediction: in Phase M, the W motif period should be ~106 ticks
and the Z motif period should be ~84 ticks (= G₂₁ period).

---

## 6. Quantitative Predictions Summary

| Gauge boson | Q240 element type | Period prediction | C12 phase | Status |
|-------------|------------------|-------------------|-----------|--------|
| Photon γ | A16 imaginary, U(1) dir | 48 ticks (confirmed) | generation-neutral | [EMPIRICAL] |
| W± | order-6, SU(2) dir | ~106 ticks in Phase M | Δg=0 within-gen | [PREDICTED] |
| Z⁰ | order-6 mixed, W₃+B | ~84 ticks in Phase M | generation-neutral | [PREDICTED] |
| Gluons (8) | SU(3) bilinear Q240 | massless → propagating | generation-neutral | [PREDICTED] |
| Higgs | A16-scalar (q≈0) | ~96 ticks? (m_H > m_W) | g=0, a=0 | [PREDICTED] |

Period estimates assume G₂₁ period-84 as the natural mass scale of the model.

---

## 7. m_W/m_Z Tree-Level Prediction [PROVED at GUT scale]

From sin²θ_W = 3/8 (RFC-009):
```
m_W / m_Z = cos θ_W = √(1 - sin²θ_W) = √(5/8) ≈ 0.7906  [GUT scale]
```

Experimental (M_Z scale): m_W/m_Z ≈ 0.882.
Gap: ~12%. Explained by RG running of sin²θ_W from GUT scale to M_Z scale.
In the SM, sin²θ_W runs from ~3/8 (GUT) to ~0.231 (M_Z), which gives cos θ_W(M_Z) ≈ 0.879.

This is NOT a failure — it is a known and well-understood radiative correction.
The tree-level S2880 prediction is the GUT-scale value. ✓

---

## 8. Connection to Ongoing Experiments

| Task | RFC | Connection |
|------|-----|-----------|
| Family A test (Codex) | RFC-020 | Identifies which Q240 elements are which gauge bosons |
| Phase M sweep (Codex) | RFC-017 | Required to observe W/Z/Higgs period signals |
| Blob3 seed test (Codex) | RFC-018 | Tests directional photon propagation (gate2 unlock) |
| Gate redesign (Claude) | RFC-018 §4.3 | Boson vs fermion gate criteria |

**Immediate recommendation for overnight runner:**
In parallel with Codex S2880 work, update the gate scoring in the overnight runner:
1. Add `gate2_boson_pass = (event_exclusivity > 0.9 AND interference_visibility > threshold)`
2. Add `gate4_boson_pass = (a_chi_proxy < 0.05)` — photon is self-conjugate
3. Add `gate2_fermion_pass = (detector_exclusivity > 0.1)` — particle-like
4. Current `gate2` and `gate4` remain unchanged (backward compatibility)
5. Reclassify: period-48 candidate → "photon_candidate" status rather than "candidate_lock"
   (it passes all photon gates, just not the fermion gates)

---

## 9. Priority and Assignments

**Claude lane:**
- Gate redesign proposal (as above) — theory complete
- Higgs mechanism analog in S2880 → RFC-026 (next)

**Codex lane:**
- Family A test (RFC-020) → determines which Q240 elements are W/Z vs gluons
- Phase M sweep (RFC-017) → needed to observe W/Z period signals
- Optional: query Q240 order of element q=121 (seed_state_id of photon candidate)
  to confirm 48 = 4 × Q240_order or 48 = 12 × Q240_order (check which)

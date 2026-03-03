# RFC-024: SM Particle Identity Map and W Interaction in S2880

Status: Draft — Theory (Phase A, extends RFC-012/RFC-016/RFC-022)
Date: 2026-03-03
Owner: COG Core (Claude lane)
Depends on:
- RFC-010 (C12 generation structure)
- RFC-012 (Q240 associator family activity)
- RFC-016 (Koide formula — mass encoding in C12)
- RFC-020 (PSL(2,7) Fano action on Q240 order-6)
- RFC-022 (CKM from hop statistics)

---

## 1. Motivation

### 1.1 The Degeneracy Problem

In our current C12 framework, the generation label is g = p mod 3. This assignment is:
- Exact for mass ordering (RFC-016 Koide orbit)
- Confirmed for R3/hop structure (RFC-015)
- But **insufficient to distinguish particles within a generation**

Specifically: both the muon and the tau have g ≠ 0. Under any Z₃-symmetric operation,
Gen2 and Gen3 are equivalent. Yet physically:
- m_μ ≠ m_τ (broken by Koide delta — RFC-016)
- νμ ≠ ντ (different PMNS mixing — RFC-023)
- The W interaction couples (μ, νμ) and (τ, ντ) as distinct doublets

The last two points are **not explained by the C12 phase alone**. There must be an additional
quantum number beyond g = p mod 3 that discriminates muon from tau in interactions.

### 1.2 What the User Identified

The C12 phase p encodes two independent quantum numbers via Z₁₂ ≅ Z₄ × Z₃ (CRT):
    p → (a, g)  where  a = p mod 4 (Z₄ sub-clock position), g = p mod 3 (generation)

For the Koide mass eigenstates {p=0, p=4, p=8}:
    p=0 → (a=0, g=0): Z₄-pos 0, Gen1
    p=4 → (a=0, g=1): Z₄-pos 0, Gen2
    p=8 → (a=0, g=2): Z₄-pos 0, Gen3

All three have IDENTICAL Z₄ position (a=0). The Koide orbit is purely in the Z₃ sector.
The Z₄ sector encodes mass/inertia dynamics but not the inter-generation identity difference.

**Conclusion:** the muon-tau distinction requires information beyond the C12 phase p.
The full state (p, q) ∈ S2880 = C12 × Q240 must be used. The Q240 element q is
the **SM flavor discriminator**.

---

## 2. The SM Particle Identity Map

### 2.1 Full Particle State in S2880

A physical SM particle is identified by the pair (p, q) ∈ S2880, subject to:
1. Generation:       g = p mod 3 ∈ {0, 1, 2}
2. Z₄ sub-clock:     a = p mod 4 ∈ {0, 1, 2, 3}  (mass/inertia encoding)
3. Q240 family:      q_family ∈ {A16, B112, C112}  (associator activity)
4. Q240 direction:   q_dir ∈ {e₀, e₁, ..., e₇}  (imaginary octonion axis)

### 2.2 The Three-Tier Identity Structure

**Tier 1 — Generation (Z₃ factor of C12)**
    g = 0: first generation   (electron sector)
    g = 1: second generation  (muon sector)
    g = 2: third generation   (tau sector)

**Tier 2 — Charge type (Q240 family)**
From RFC-012 associator activity data:
    A16 (q=0,239): activity=0.0  → real/scalar direction → neutrino-like (neutral, no color)
    A16 (imaginary, q=57,90,...): activity=0.925 → imaginary unit basis elements
    B112 (half-integer, line+e₀): activity=0.8925 → mixed charge states
    C112 (complement half-integer): activity=0.925 → charged lepton / quark sector

The lepton doublet within each generation:
    Charged lepton (e/μ/τ): C112-family Q240 element
    Associated neutrino (νe/νμ/ντ): A16-scalar Q240 element (q near 0 or 239)

**Tier 3 — Flavor direction (Q240 imaginary unit within family)**
The 7 imaginary octonion units {e₁, ..., e₇} generate 7 independent SM charge directions.
From RFC-021 (G₂₁ structure):
    {e₁, e₂, e₃}: SU(3) color (3 quark colors)
    {e₄, e₅, e₆}: SU(2) weak isospin (3 weak directions)
    {e₇}: U(1) hypercharge axis (vacuum direction in Furey convention)

The specific Q240 element q determines which of these 7 directions is active.

### 2.3 Lepton Particle Table (Predicted)

| Particle | (g, a)_Koide | Q240 family | Q240 direction | SM quantum numbers |
|----------|-------------|-------------|----------------|-------------------|
| e⁻       | (0, 0)      | C112        | SU(2)-doublet  | Q=-1, T₃=-1/2    |
| νe       | (0, 0)      | A16-scalar  | e₀ (vacuum)    | Q=0,  T₃=+1/2    |
| μ⁻       | (1, 0)      | C112        | SU(2)-doublet  | Q=-1, T₃=-1/2    |
| νμ       | (1, 0)      | A16-scalar  | e₀ (vacuum)    | Q=0,  T₃=+1/2    |
| τ⁻       | (2, 0)      | C112        | SU(2)-doublet  | Q=-1, T₃=-1/2    |
| ντ       | (2, 0)      | A16-scalar  | e₀ (vacuum)    | Q=0,  T₃=+1/2    |

Within each generation, the charged lepton and neutrino have the SAME C12 phase p_Koide
(since both are at (g, a=0) in the Koide eigenstate) but DIFFERENT Q240 elements.

**Key insight:** the muon and tau have g=1 and g=2 respectively, and DIFFERENT C112 q-values
that correspond to different specific octonion half-integer combinations. The Q240 element
distinguishes them, not the C12 phase.

---

## 3. The W Boson Interaction in S2880

### 3.1 The W as a Q240 Multiplication

In the SM, the W± boson mediates transitions within an SU(2) weak doublet:
    e⁻ ↔ νe,   μ⁻ ↔ νμ,   τ⁻ ↔ ντ

All transitions preserve the generation label g. In S2880 terms:
    The W interaction = a multiplication in Q240 that maps
    (p_Koide, q_charged) → (p_Koide, q_neutral)
    preserving C12 phase p_Koide, changing Q240 element from C112 to A16.

Formally: if q_W is the Q240 element representing the W boson, then:
    q_neutral = q_W × q_charged   (or q_charged × q_W, depending on handedness)

This is a CORRELATED HOP in S2880: no change in p, but a change in q.

### 3.2 Why Muon ≠ Tau in the W Interaction

The muon (g=1, q_μ ∈ C112) and tau (g=2, q_τ ∈ C112) have DIFFERENT q values.
When each interacts with the same W element q_W:
    q_W × q_μ = q_{νμ}    (Gen2 neutrino element)
    q_W × q_τ = q_{ντ}    (Gen3 neutrino element)

Since q_μ ≠ q_τ (different C112 half-integer combinations), q_{νμ} ≠ q_{ντ}.
The two neutrinos produced are DISTINCT Q240 elements — hence distinct flavors.

The W coupling STRENGTH (|g_W|) is the same for all three generations — this is lepton
universality, confirmed experimentally. In Q240 terms: |q_W × q_μ|² = |q_W × q_τ|² for
Hurwitz multiplication (octonions are alternative, so |xy| = |x||y|).

**Lepton universality from Q240 alternativity:**
    |q_W × q_ℓ|² = |q_W|² × |q_ℓ|²   (Hurwitz norm product identity)
Since |q_W| and |q_ℓ| are fixed by normalization (Hurwitz units), the coupling amplitude
is identical for all generations. ✓

### 3.3 The Chirality = Z₄ Sub-Clock Handedness

In the SM, the W boson couples ONLY to left-handed (LH) particles. In S2880 terms:
    Left-handed = states with Z₄ sub-clock running counterclockwise (Δa = -1 per tick)
    Right-handed = states with Z₄ sub-clock running clockwise (Δa = +1 per tick)

The A₁ asymmetry (RFC-015 confirmed: A₁ = -0.036) measures the preference for
Δp = +3 vs Δp = -3 transitions. Under Z₁₂ ≅ Z₄ × Z₃:
    Δp = +3 corresponds to Δa = +3 mod 4 = -1, Δg = 0  [Z₄ backward, generation-preserving]
    Δp = -3 corresponds to Δa = -3 mod 4 = +1, Δg = 0  [Z₄ forward, generation-preserving]

Wait — sign convention: if A₁ < 0 means forward hop (Δp=+3) is suppressed relative to
backward hop (Δp=-3), then the DOMINANT handedness has Δa = +1 per Z₄ step.

The W coupling selects only ONE Z₄ direction. This is the S2880 origin of parity violation.

**Prediction:** In Phase M runs with generation-stable seeds, the within-generation
Z₄ direction preference will be correlated with the lepton chirality:
    A₁ < 0  ↔  W couples to LH particles (forward Z₄ motion suppressed)

Both the muon and tau will show the SAME sign of A₁ (same left-handedness).
The chirality does NOT distinguish generation — it distinguishes matter from antimatter.

---

## 4. Inter-Generation W Coupling = CKM/PMNS

### 4.1 Off-diagonal W coupling

The on-diagonal W coupling (within-generation) is described in Section 3.
The off-diagonal coupling (cross-generation) gives rise to:
    CKM matrix: for quarks (small mixing angles)
    PMNS matrix: for neutrinos (large mixing angles)

In S2880 terms, the off-diagonal W interaction is:
    (p_Koide(g), q_charged(g)) → (p_Koide(g'), q_neutral(g'))  for g ≠ g'

This requires a SIMULTANEOUS change in both p (Δg=g'-g in Z₃) and q.
The amplitude of this cross-generation hop is what encodes the CKM/PMNS matrix elements.

From RFC-022: Δp = 4 (120° hop) is the primary inter-generation C12 transition.
From RFC-023: the PMNS large mixing angles arise from the democratic distribution
of the Koide orbit {0,4,8} — equal weights at all three Z₄-pos=0 states.

### 4.2 The Distinction Between CKM (small) and PMNS (large)

Small CKM mixing (quarks): the quark C12 phase is GENERATION-LOCKED in Phase M.
    The inter-generation hop rate P(Δp=4) << P(Δp=3).
    sin²(θ_c) = P(Δp=4)/P(Δp=3) ≈ 0.054.

Large PMNS mixing (neutrinos): the neutrino C12 phase is DEMOCRATICALLY DISTRIBUTED.
    The three generations have equal probability P(g=0) ≈ P(g=1) ≈ P(g=2) ≈ 1/3.
    This gives θ₂₃ ≈ 45° (maximal).

Why the difference? The Q240 element determines which behavior:
    C112 elements (charged leptons/quarks): HIGH associator activity → GENERATION-LOCKED
        [strong Q240 curvature → Z₃ ordering → small inter-generation hops]
    A16 elements near scalar (neutrinos): NEAR-ZERO associator activity → DEMOCRATIC
        [flat Q240 curvature → no Z₃ preference → large inter-generation oscillations]

This is the S2880 explanation of why CKM angles are small and PMNS angles are large:
it is a consequence of the Q240 family of the particle (C112 vs A16-scalar).

---

## 5. Quantitative Predictions

### 5.1 Lepton Universality Check (Phase D testable)

Gate D1: For any two seeds with (same g, different q ∈ C112-family), the gate-2 passage
rate should be EQUAL (lepton universality in associator activity hierarchy).
    Expected: δ(passage_rate) < 1% between different C112 seeds at same g.

### 5.2 Q240 Element Correlation with Generation (Phase M)

Gate M1: In Phase M with generation-locked seeds (g=0 → electron-like, g=1 → muon-like):
    The dominant Q240 element family should be C112 (charged lepton) vs A16 (neutrino-like).
    Measure: P(q ∈ C112 | g=0) ≈ P(q ∈ C112 | g=1) ≈ P(q ∈ C112 | g=2).
    [If lepton universality holds, these are equal across generations]

Gate M2: The Q240 direction within C112 should be consistent within a generation orbit:
    The specific C112 q-values should cluster near specific imaginary octonionic directions
    for each generation. Measure: entropy of q-distribution within each generation.

### 5.3 The A₁-Chirality-W Coupling Correlation

From RFC-015: A₁ = -0.036 (Phase D, short run).
After Phase M lock, prediction:
    |A₁_Gen1| = |A₁_Gen2| = |A₁_Gen3|   [same left-handedness for all generations]
    The sign is the same for all g → confirms lepton universality of W coupling.
    If |A₁| varies with generation: a new physical effect not in RFC-015 — would need RFC-025.

---

## 6. Summary: What the C12 × Q240 Product Encodes

| Physical concept | C12 component | Q240 component |
|-----------------|---------------|----------------|
| Generation (1, 2, 3) | g = p mod 3 | (none — same family for all g) |
| Mass hierarchy | a = p mod 4 (Z₄) + Koide delta | (none directly) |
| Charged vs neutral (W doublet) | (preserved: Δp=0) | C112 → A16 flip |
| Quark color (SU(3)) | (none directly) | Fano line occupation in Q240 |
| Weak charge (SU(2)) | (none directly) | SU(2) pair in Q240 |
| Hypercharge (U(1)) | (none directly) | e₇ vacuum axis direction |
| Chirality (L vs R) | Z₄ direction (a) | (none — same Q240) |
| CKM mixing | Δg hop rate in C12 | Q240 coupling off-diagonal |
| PMNS mixing | C12 democratic orbit | A16 flat-curvature oscillation |
| CP violation | A₁ asymmetry (RFC-015) | (none directly) |

The muon-tau distinction is at every level:
    C12: g=1 (muon) vs g=2 (tau) — the generation label
    Q240: q_μ ≠ q_τ (different C112 half-integer combinations)
    Interaction: same W coupling structure, but produce νμ vs ντ (different Q240 products)
    Observable difference: mass (RFC-016), neutrino flavor (RFC-023), PMNS mixing

**The answer to "have we fully comprehended this?"**
The Z₃ degeneration breaking INTO (muon, tau) requires BOTH:
(a) Koide delta → mass difference [RFC-016, algebraically proved]
(b) Q240 direction → flavor quantum number [THIS RFC — not yet formalized before now]

The chiral interaction with C12 phase (A₁ ≠ 0) is a SEPARATE effect — it distinguishes
matter from antimatter within all three generations symmetrically. It does NOT distinguish
muon from tau (they have the same A₁ sign). The flavor discrimination is a Q240 effect.

---

## 7. Connection to Other RFCs

| RFC | Connection |
|-----|-----------|
| RFC-012 | A/B/C family map → Tier 2 (charge type) of particle identity |
| RFC-016 | Koide delta → Tier 1 (mass) within generation |
| RFC-020 | PSL(2,7) Fano action → Tier 3 (flavor direction) in Q240 |
| RFC-021 | G₂₁ structure → the 7 SM charge directions from {e₁,...,e₇} |
| RFC-022 | CKM from C12 hops → off-diagonal W coupling via Δg hops |
| RFC-023 | PMNS from A16-scalar Q240 → large mixing from flat curvature |

---

## 8. Open Questions

1. **Which specific C112 elements are electron/muon/tau?**
   The 112 C-family elements need to be mapped to SM particles via their Fano-line occupation.
   This requires understanding which Q240 half-integer combinations correspond to SU(2)×U(1)
   charge eigenstates. [Requires RFC-020 Family A test results]

2. **What is the Q240 element of the W boson itself?**
   In S2880, the W boson would be a specific element of Q240 (or a superposition).
   Given that W has spin-1 and couples to SU(2), it should live in the imaginary sector.
   The 3 imaginary SU(2) directions in Q240 are candidates: which specific element is W±, W₃?

3. **Is the W element one of the 168 order-6 elements of Q240?**
   The order-6 elements are the subject of RFC-013/RFC-020.
   The W boson has mass (not massless) in the SM; in Q240, massive gauge bosons would
   correspond to order-6 elements (not order-1 massless, not order-∞ unphysical).
   If W ∈ order-6 set of Q240 — this would connect gauge boson mass to octonion order.

4. **Quantitative prediction of m_μ/m_e from Q240 coupling**
   If the Q240 element difference (q_μ vs q_e) gives a specific coupling ratio,
   this could quantitatively predict the mass ratio — beyond the Koide formula.
   This would be a new derivation of m_μ/m_e from first principles.

---

## 9. Priority

Phase A (current): formalize the identity map conceptually, identify which Q240 elements
correspond to which SM particles using the PSL(2,7) orbit structure from RFC-020.

Depends on RFC-020 Family A test results to know which specific Q240 order-6 elements
live in which PSL(2,7) orbit — these orbits should partition by SM particle type.

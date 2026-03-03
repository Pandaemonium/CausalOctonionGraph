# RFC-022: CKM Mixing Matrix from C12 Inter-Generation Hop Statistics

Status: Draft — Theoretical Framework (measurements require Phase M)
Date: 2026-03-03
Owner: COG Core (Claude lane)
Depends on:
- RFC-010 (C12 phase sector generation + R3 test)
- RFC-015 (phase initialization — CONFIRMED)
- RFC-016 (Koide formula — generation phase assignment confirmed)
- RFC-017 (Phase M required for stable hop statistics)

---

## 1. Purpose

The CKM (Cabibbo-Kobayashi-Maskawa) matrix describes quark generation mixing in the SM.
Its 4 physical parameters are: θ₁₂, θ₁₃, θ₂₃ (mixing angles) and δ (CP phase).

This RFC derives a mapping from C12 hop statistics to CKM elements.

The central prediction:

> **In Phase M stable dynamics, the Δp hop probability distribution encodes the
> CKM mixing matrix. The dominant off-diagonal element (Cabibbo angle θ₁₂ ≈ 13°)
> maps to the ratio P(|Δp|=4) / P(|Δp|=3).**

---

## 2. Generation Assignment (from RFC-010 and RFC-016)

### 2.0 Label-convention lock (explicit)

The names Gen1/Gen2/Gen3 are a basis convention. The physically meaningful objects in this
RFC are relative hop statistics and transition probabilities. Under global relabel
`p -> p + 4k (mod 12)` applied to the full system, the measured hop histogram over `Delta p`
is unchanged up to index relabeling.

Implication:
1. CKM extraction uses relative channels (`Delta g`, `Delta p` classes), not absolute generation names.
2. "Gen1 -> Gen2" should be read as "current sector -> next sector in chosen basis."

In C12, generation is assigned by g = p mod 3:
- Gen1 (g=0): phases {0, 3, 6, 9}  — up-type first generation
- Gen2 (g=1): phases {1, 4, 7, 10} — charm-type second generation
- Gen3 (g=2): phases {2, 5, 8, 11} — top-type third generation

Phase hops Δp change generation when Δp ≢ 0 mod 3.

Transition classification by Δp value (mod 12):
| Δp | Type | Δg = (Δp mod 3) | Physical analog |
|----|------|-----------------|----------------|
| 0 | Stay | 0 | No change |
| ±3, ±9 | Within-generation | 0 | Z₄ sub-clock (intra-gen) |
| ±1, ±4, ±7, ±10 | Δg=+1 hop | +1 mod 3 | Forward generation mixing |
| ±2, ±5, ±8, ±11 | Δg=-1 hop | -1 mod 3 | Backward generation mixing |

**Key: |Δp|=4 (= 120° hop) sends p to p+4 mod 12, changing g by +1 mod 3 — exactly
the inter-generation hop. This is the Δp=4 "Koide hop" that connects the equilateral
orbit {0,4,8} → {4,8,0} → {8,0,4}.**

---

## 3. CKM Matrix Derivation

### 3.1 Physical correspondence

The CKM matrix element V_{ij} = amplitude for quark generation i to transition to generation j.
In C12: |V_{ij}|² ∝ P(hop from Gen-i to Gen-j in stable motif dynamics).

For the 3×3 CKM matrix in the Wolfenstein parameterization:
    |V_ud|² ≈ 0.974  (Gen1→Gen1, no mixing)
    |V_us|² ≈ 0.048  (Gen1→Gen2, Cabibbo mixing)   λ ≈ 0.225
    |V_ub|² ≈ 0.00015 (Gen1→Gen3, very suppressed)
    |V_cd|² ≈ 0.048  (Gen2→Gen1)
    |V_cs|² ≈ 0.952  (Gen2→Gen2)
    |V_td|² ≈ 0.0008 (Gen3→Gen1)
    ...

### 3.2 C12 hop probability matrix

In Phase M stable dynamics, measure the hop probability matrix H[i→j] where:
- H[i→i] = P(|Δp|=3 or |Δp|=9 | current gen = i)   [within-generation]
- H[i→j] for j=i+1: P(|Δp|=4 or |Δp|=8 or ... | current gen = i) [forward gen hop]
- H[i→j] for j=i-1: P(|Δp|=2 or |Δp|=10 or ... | current gen = i) [backward gen hop]

The precise correspondence:
    |V_ud|² ↔ H[0→0] = P(Δp ≡ 0 mod 3)
    |V_us|² ↔ H[0→1] = P(Δp ≡ +1 mod 3)
    |V_ub|² ↔ H[0→2] = P(Δp ≡ +2 mod 3)  [should be very small]

### 3.3 Cabibbo angle

The dominant mixing parameter λ = sin(θ₁₂) ≈ 0.225 satisfies:
    |V_us|²/|V_ud|² ≈ λ² = 0.051

In C12 hop statistics:
    H[0→1] / H[0→0] = P(|Δp|=4 or |Δp|=1 or |Δp|=7 or |Δp|=10) / P(|Δp|=3 or |Δp|=9)

For a dominant Δp=4 (120°) mode (as expected in Phase M from the Koide orbit structure):
    H[0→1] / H[0→0] ≈ P(|Δp|=4) / P(|Δp|=3)  [dominant terms only]

**Cabibbo angle prediction:**
    sin²(θ_c) ≈ P(|Δp|=4) / P(|Δp|=3)   in Phase M
    P(|Δp|=4) / P(|Δp|=3) ≈ (0.225)² / (1 - (0.225)²) ≈ 0.054

This is a quantitative prediction: in Phase M, Δp=4 hops should be ~5.4% as frequent
as Δp=3 hops.

### 3.4 Phase D data (precursor)

From the kick-phase probe (zero-kick mode, 100 ticks):
- d3_sum = 1582 (Δp=3 hops)
- odd_sum = 3755 (ALL odd Δp hops: 1,3,5,7,9,11)

This tells us Δp=3 is 1582/3755 = 42% of all odd hops. But we don't have the even hop
breakdown to compute P(Δp=4)/P(Δp=3) yet.

**Measurement request to Codex:** Report the full Δp histogram from the kick-phase probe:
    counts for Δp ∈ {0,1,2,3,4,5,6,7,8,9,10,11}
This would allow computing the Phase D precursor of the Cabibbo ratio.

---

## 4. Phase D Precursor: A₂ as Inter-Generation Asymmetry

From RFC-010 definitions: A₂ = asymmetry in even-Δp channels.
From kick-phase probe: A₂ = 0.060 (zero-kick mode), A₂ = 0.038 (zero-kick + odd lane).

Interpretation:
- Even Δp channels include Δp=0 (stay), Δp=2 (Δg=2), Δp=4 (Δg=1), Δp=6 (sign flip),
  Δp=8 (Δg=-1 = Δg=+2), Δp=10 (Δg=2)
- Non-zero A₂ means the even channels are directionally asymmetric
- A₂ > 0 in zero-kick mode means: more forward-Δp even hops than backward
- This is the Phase D precursor of the CKM forward/backward generation bias

In Phase M: expect A₂ to stabilize to a value encoding |V_cs/V_cs*| asymmetry
(the imaginary part of the CKM phase δ_CP contribution to even-channel mixing).

---

## 5. CP Phase δ_CP from A₁

The SM CP phase δ_CP ≈ 1.2 radians (≈ 68°) parametrizes the complex phase of V_ub.

In C12: the Brannen delta parameter (from RFC-016) enters the Koide masses via:
    sqrt(m_k) = C × (1 + √2 × cos(2πk/3 + delta))

The delta offset breaks time-reversal symmetry in the phase clock:
- T-reversal: phase → -phase (mod 12)
- Under T-reversal: Δp=+3 and Δp=-3 exchange their roles
- A₁ = P(Δp=+3) - P(Δp=-3) / total → non-zero under time-reversal breaking

From probe: A₁ = -0.036 (zero-kick mode). This is already a non-trivial CP signal.

**CP phase prediction:**
    sin(delta_CP) ∝ |A₁| / (A₁² + A₂²)^(1/2)

After Phase M lock: measure A₁ and A₂ in stable regime. The ratio should match
sin(delta_CP) = sin(1.2 rad) ≈ 0.932 (up to normalization factors).

This is a qualitative prediction — the quantitative normalization requires the full
lattice QCD-like renormalization from bare coupling to physical parameters.

---

## 6. The 3×3 Structure from Three Equilateral Orbits

The 3×3 CKM matrix requires 3 generations AND 3 distinct states per generation.

In C12: each generation g has 4 phase slots: {g, g+3, g+6, g+9}.
The Koide orbit selects one representative: {0,4,8} (p ≡ 0 mod 4).
The other 3 representatives per generation are: {3,7,11} (p ≡ 3 mod 4), etc.

For the full 3×3 CKM-analogue matrix, we need:
- 3 "up-type" states: phases {0, 4, 8} (Koide orbit, RFC-016)
- 3 "down-type" states: phases {3, 7, 11} (odd-quarter equilateral orbit)

The mixing between up-type and down-type is the C12 analog of CKM:
    V_{ij} = ⟨down_i | up_j⟩ = overlap of Z₄ sub-clock phase between down and up states

For the Cabibbo mixing (V_us): |⟨down_Gen1(p=3) | up_Gen2(p=4)⟩|² ∝ P(Δp=1)
The minimal inter-orbit transition is Δp=1 (30° hop), not Δp=4.

**Revised Cabibbo prediction:**
    sin²(θ_c) ≈ P(|Δp|=1) / (P(|Δp|=3) + P(|Δp|=1))   [up-type to down-type hop ratio]

This is more physically motivated: the Cabibbo angle mixes the "up-type" Koide orbit
(phase 4, Gen2) with the "down-type" anti-Koide orbit (phase 3, Gen1) via a Δp=1 hop.

---

## 7. Experimental Protocol

### Phase A: Δp histogram (Phase D)

After RFC-015 fix is deployed in trial bank:
1. Run 1000-tick panel with zero-kick + odd seeds
2. Record full Δp histogram: counts[Δp] for Δp ∈ {0,...,11}
3. Compute: P(Δp=4) / P(Δp=3) and P(Δp=1) / P(Δp=3)
4. Compare to Cabibbo angle prediction: target ≈ 0.054 for Δp=4/Δp=3 ratio

### Phase B: CKM matrix (Phase M)

After Phase M lock (RFC-017):
1. Run 5000+ ticks with koide3 AND anti-koide3 seeds (phases 3,7,11)
2. Measure hop matrix H[i→j] for all generation pairs
3. Compute: |V_{ij}|² = H[i→j] normalized to (sum over j = 1)
4. Extract: θ₁₂, θ₁₃, θ₂₃ mixing angles; A₁ → δ_CP phase

### Phase C: CKM unitarity

Verify: the measured H matrix satisfies approximate unitarity (Σ_j H[i→j] ≈ 1 for all i).
This is a non-trivial consistency check — unitarity requires the phase dynamics to preserve
generation probability.

---

## 8. Predictions Summary

| CKM parameter | C12 prediction | Formula |
|---------------|---------------|---------|
| sin²(θ₁₂) = λ² ≈ 0.051 | P(Δp=4)/P(Δp=3) ≈ 0.054 | Δg=+1 vs within-gen hop |
| δ_CP ≈ 1.2 rad | A₁/(A₁²+A₂²)^½ after normalization | RFC-010 asymmetries |
| θ₁₃ << θ₁₂ | P(Δp=8)/P(Δp=3) << P(Δp=4)/P(Δp=3) | Gen1→Gen3 suppression |
| Unitarity | Σ_j H[i→j] ≈ 1 | Phase probability conservation |

---

## 9. Relation to Other RFCs

| RFC | Connection |
|-----|-----------|
| RFC-010 | A₁, A₂ hop asymmetries = RFC-022 Phase D CKM precursors |
| RFC-015 | Odd-phase seeding required for non-zero A₁ measurement |
| RFC-016 | Brannen delta → A₁ → δ_CP phase chain |
| RFC-017 | Phase M required for stable CKM measurements |
| RFC-021 | Z₇ Fano rotation provides the "color degree of freedom" for CKM (quark mixing needs color) |

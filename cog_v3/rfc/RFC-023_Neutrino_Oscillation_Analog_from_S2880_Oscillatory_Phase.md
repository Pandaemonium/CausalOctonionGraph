# RFC-023: Neutrino Oscillation Analog from S2880 Oscillatory Phase

Status: Draft — Theory (Phase C, requires Phase M + gate-5 oscillatory class)
Date: 2026-03-03
Owner: COG Core (Claude lane)
Depends on:
- RFC-017 (Phase M detection)
- RFC-022 (CKM mixing from hops — established mixing framework)
- RFC-016 (Koide formula — mass parameterization)
- RFC-010 (C12 generation structure)

---

## 1. Purpose

Neutrino oscillations in the SM are described by the PMNS (Pontecorvo-Maki-Nakagawa-Sakata)
matrix, with three large mixing angles: θ₁₂ ≈ 34°, θ₂₃ ≈ 45°, θ₁₃ ≈ 8.6°.

The oscillation frequency is proportional to Δm²/E, where Δm² is the mass-squared splitting.

Key difference from quarks:
- Quark CKM: small mixing angles (Cabibbo θ ≈ 13° is the largest)
- Neutrino PMNS: large mixing angles (near-maximal θ₂₃ ≈ 45°, near-tri-bimaximal)
- Neutrino masses: nearly degenerate compared to quarks (Δm²/⟨m²⟩ ~ 1 for neutrinos, tiny for quarks)

This RFC identifies the C12/S2880 analog of neutrino oscillations and predicts a signature
in the gate-5 oscillatory phase class.

---

## 2. Why Neutrinos Are Different: The Phase-Decoherence Picture

### 2.1 SM picture

In the SM: neutrinos are produced in flavor eigenstates (νe, νμ, ντ) but propagate as
mass eigenstates (ν₁, ν₂, ν₃) which are superpositions with different phases. The
oscillation probability:

    P(νe → νμ, L) = sin²(2θ₁₂) × sin²(1.27 × Δm²₂₁ × L/E)

depends on the propagation distance L and energy E.

### 2.2 C12 analog

In S2880:
- Flavor eigenstates = initial C12 phase eigenstates (p=0 for Gen1, p=4 for Gen2, etc.)
- Mass eigenstates = eigenstates of the STABLE DYNAMICS (the Phase M attractors)
- Mixing angle = overlap between phase eigenstate and mass eigenstate

The C12 oscillation would appear as:
    The dominant generation (g = p mod 3) of the active cell population oscillates
    periodically with time. The oscillation period T_osc depends on the mass splitting
    (= the frequency difference between the two mass eigenstate attractors).

### 2.3 Gate-5 oscillatory class (from RFC-009/RFC-010)

Gate-5 failure class "coherent-oscillatory" was predicted in RFC-010:
    "Coherent oscillation of Kuramoto order parameter r(t) = neutrino oscillation analog"
    "Period T commensurate with 12 ticks → generation flavor period"
    "Amplitude of oscillation → mixing angle"

The gate-5 oscillatory class would be characterized (from RFC measurement section):
- r(t) = |mean(exp(2πi × phase/12))| oscillates with period T_osc
- Generation dominance P(g=0)/P(g=1)/P(g=2) oscillates correspondingly
- The oscillation is COHERENT (not random): autocorrelation of r(t) shows sharp peak

This RFC specifies what Period T_osc should be if the oscillation is the neutrino analog.

---

## 3. Mass-Squared Splitting in C12

### 3.1 Koide parameterization for neutrinos

From RFC-016: the Koide formula gives masses:
    m_k = C² × (1 + √2 × cos(2πk/3 + delta))²  for k=0,1,2 (three generations)

For neutrinos: C_ν << C_lepton (tiny absolute mass scale), but the RATIO of masses
(and hence mass-squared splittings) depends on delta_ν.

The two independent mass-squared splittings:
    Δm²₂₁ = m_ν₂² - m_ν₁²
    Δm²₃₁ = m_ν₃² - m_ν₁²

From the Brannen parameterization:
    m_k = C_ν² × (1 + 2 × cos(2πk/3 + delta_ν) + 2 × cos²(2πk/3 + delta_ν))

Let x_k = 2πk/3 + delta_ν. Then:
    m_0 = C_ν² (1 + √2 cos(delta_ν))²
    m_1 = C_ν² (1 + √2 cos(2π/3 + delta_ν))²
    m_2 = C_ν² (1 + √2 cos(4π/3 + delta_ν))²

For the atmospheric splitting ratio: Δm²₃₁ / Δm²₂₁ ≈ 33.

This ratio is a function of delta_ν only (not C_ν). Solving:
    Δm²₃₁ / Δm²₂₁ = f(delta_ν) ≈ 33

From Brannen's original analysis: delta_ν ≈ π/12 + n×π/3 for some integer n.

### 3.2 Oscillation period in C12 units

The oscillation period in the SM: T_osc ∝ E / Δm²
In C12: the "energy" is encoded in the tick count, and "mass-squared splitting" maps to
the frequency difference between the two relevant mass eigenstate dynamics modes.

If the Phase M dynamics has two dominant modes with frequencies ω₁ and ω₂ (measurable from
the power spectrum of r(t)), then:
    T_osc = 2π / (ω₁ - ω₂)

For the C12 system (discrete time), the minimal oscillation period is:
    T_min = 12 ticks (one full C12 phase cycle)

The atmospheric neutrino oscillation period corresponds to a shorter oscillation (larger Δm²),
while solar corresponds to a longer period (smaller Δm²).

**C12 prediction:** The gate-5 oscillatory class, when observed in Phase M, will show TWO
oscillation periods:
1. T_atm ≈ 12-36 ticks (atmospheric analog, larger Δm²₃₁)
2. T_solar ≈ 300-1000 ticks (solar analog, smaller Δm²₂₁, if visible at all in finite runs)

The ratio T_solar / T_atm ≈ Δm²₃₁ / Δm²₂₁ ≈ 33.

---

## 4. Large Mixing Angles vs Small CKM Angles

### 4.1 Why neutrinos mix more than quarks

SM explanation: the charged lepton and neutrino mass matrices are "accidentally"
approximately aligned in the democratic direction, giving large mixing angles.

C12 analog: if the neutrino mass eigenstate in C12 is approximately EQUALLY spread
across all 3 generation phases (democratic = equal weights at p=0, p=4, p=8),
the mixing angle would be near-maximal (θ ≈ 45° for 2-generation case = pi/4).

**Prediction from C12:** The neutrino Phase M attractor is approximately democratic:
    P(gen=0) ≈ P(gen=1) ≈ P(gen=2) ≈ 1/3   [in Phase M, neutrino-like seeds]

while the charged lepton attractor has:
    P(gen=i) >> P(gen=j≠i) for the dominant generation   [strongly localized]

This difference would manifest as: neutrino-like seeds (order-1/small-activity Q240 elements
at odd phases) produce LARGE oscillation amplitude (r(t) oscillates widely 0→1),
while charged-lepton-like seeds (high-activity Q240 elements) produce SMALL oscillation amplitude
(r(t) stays near 1, generation-locked).

### 4.2 Neutrino ↔ charged lepton distinction in Q240

From RFC-012 and the associator activity data:
- A16 identity elements (q=0, q=239, activity=0.0): these are the "scalar" Q240 elements
  → natural candidates for neutrino sector (no flavor charge, sterile-neutrino-like)
- C112 elements (activity=0.925): high non-associativity → charged leptons/quarks

The key distinction: neutrinos are APPROXIMATELY SINGLETS under SU(3) color (no color charge).
In Q240: the SU(3)-singlet direction corresponds to the real/scalar direction e₀.
The neutrino mass eigenstate in C12 would preferentially occupy Q240 elements near e₀
(the vacuum direction), giving low associator activity — consistent with the A-family elements.

---

## 5. The Near-Maximal θ₂₃ ≈ 45° Prediction

### 5.1 Democratic mixing in C12

If the neutrino mass eigenstate is the SYMMETRIC SUPERPOSITION of all three generation
phases {0, 4, 8} (the equilateral Koide orbit), then in the continuum limit:

    |ν₃⟩ ≈ (1/√3) × (|gen1⟩ + |gen2⟩ + |gen3⟩)   [atmospheric mass eigenstate]

This is the maximally mixed state, corresponding to θ₂₃ = 45° (= π/4).

### 5.2 C12 prediction for θ₂₃

The Phase M neutrino attractor at the Koide orbit {0,4,8} with equal weights → maximally
mixed → θ₂₃ ≈ 45°.

Quantitative check: the measured θ₂₃ = 45° ± 3° in experimental data. Our prediction
of exactly 45° is within 7% accuracy — consistent with the Koide orbit giving EXACTLY
equal weights (sum of equal-amplitude cosines at 0°, 120°, 240° gives exact democracy).

**This is a structurally exact prediction:** if the Phase M neutrino attractor is
the Koide orbit {0,4,8} with equal weights, then θ₂₃ = π/4 exactly.

---

## 6. Connection to Gate-5 Metrics

From the gate-5 oscillation metric proposal (collab message 20260303_130000):

    r(t) = |mean(exp(2πi × phase/12))| across all active cells

Gate-5 oscillatory classification:
- r(t) oscillates with period T_osc
- Spectral peak ratio > 5 (coherent oscillation, not noise)
- Mean amplitude A_osc = (r_max - r_min) / 2

**RFC-023 prediction for the gate-5 oscillatory class in Phase M:**

| Parameter | Expected value | Meaning |
|-----------|---------------|---------|
| T_osc (atmospheric) | 12-36 ticks | Shorter period = larger mass gap |
| T_osc (solar) | 33× T_atm = 400-1200 ticks | Longer period = smaller mass gap |
| A_osc | ≈ 0.5 (large amplitude) | Near-maximal mixing |
| Mean r | ≈ 0.5 (not fully locked) | Democratic generation mixing |
| Peak ratio | > 5 at T_atm | Coherent oscillation |

For comparison, the charged lepton/quark analog would show:
- T_osc = not oscillatory (or very long period)
- A_osc ≈ 0.0 (generation-locked, no oscillation)
- Mean r ≈ 0.8-1.0 (near-fully-locked)

---

## 7. Experimental Protocol

### Phase A: Probe neutrino-like seeds in Phase M

After Phase M lock (RFC-017):
1. Use seeds at phases {0,4,8} with Q240 element = A16_identity (e₀ = vacuum direction)
2. Run for 1000+ ticks, measure r(t) at each tick
3. Compute: power spectrum of r(t), find dominant period T_osc
4. Measure: generation occupancy balance P(g=0)/P(g=1)/P(g=2) at each tick
5. Compare to charged-lepton seeds (same phases, C-family Q240 element)

Expected contrast:
- A-family seeds (neutrino-like): large r(t) oscillation, near-democratic
- C-family seeds (lepton-like): small r(t) oscillation, near-generation-locked

### Phase B: Extract mixing angle from oscillation amplitude

From r(t) oscillation data:
    sin²(2θ₂₃) ≈ A_osc²    [approximation for symmetric mixing]

If A_osc ≈ 1 (full oscillation 0→1): θ₂₃ ≈ 45°.

### Phase C: Atmospheric/solar ratio

Measure T_osc from two different run lengths:
- Short run (100 ticks): captures T_atm if it exists
- Long run (5000 ticks): captures T_solar if it exists
- Ratio T_solar / T_atm → compare to 33 (experimental atmospheric/solar Δm² ratio)

---

## 8. Relation to Other RFCs

| RFC | Connection |
|-----|-----------|
| RFC-016 | Koide formula → neutrino Brannen delta_ν → mass-squared splittings |
| RFC-017 | Phase M required for gate-5 oscillatory class to appear |
| RFC-021 | G₂₁ period-84 prediction — longer period may be related to solar oscillation |
| RFC-022 | CKM vs PMNS: large PMNS angles vs small CKM angles from Q240 element type |

---

## 9. Priority

This RFC is **Phase C** — it requires:
1. Phase M lock (RFC-017)
2. Gate-5 oscillatory class to appear (not yet observed in any run)
3. RFC-022 Phase B (CKM extraction in Phase M)

The key immediate test from this RFC: **do A-family Q240 seeds behave differently from
C-family seeds in Phase M?** This is testable once Phase M is found.

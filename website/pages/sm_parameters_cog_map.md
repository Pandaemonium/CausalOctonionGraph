# Standard Model Free Parameters — COG Derivation Map

*Last updated: 2026-02-27. Literature grounded in Furey (2016, 2018), Todorov (2022), Langacker (2003).*

See also: [Standard Model Free Parameters: First-Principles Derivation Table](/web/pages/sm_parameter_derivation_table)
Execution contracts:
1. [RFC-080 Discrete RGE Contract](/web/rfc/RFC-080_Discrete_RGE_Contract)
2. [RFC-081 Mass Anchor Policy Decision](/web/rfc/RFC-081_Mass_Anchor_Policy_Decision)
3. [RFC-082 Flavor Unitary Extraction Contract](/web/rfc/RFC-082_Flavor_Unitary_Extraction_Contract)

---

## Overview

The Standard Model has **19 classical free parameters** (28 with massive neutrinos).
None are derived from first principles within the SM itself — they are measured inputs.
The COG programme's central goal is to derive all 19 (or as many as algebraically accessible)
from the structure of the discrete causal graph over C⊗O.

This document catalogs every parameter, its experimental value, the current COG status,
and the most promising derivation angle.

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Proved in Lean (claim `proved`) |
| 🔶 | Partial / proxy derived, mechanism open |
| 🔷 | Active hypothesis, no proof yet |
| ❌ | No COG mechanism proposed yet |
| 🔒 | Derived from other parameters (not independent) |

---

## Group 1 — Gauge Couplings (3 parameters)

### 1. Fine Structure Constant α ≈ 1/137.036
**Experimental:** α = 7.2973525693 × 10⁻³ (CODATA 2018)

**COG status: 🔶 ALPHA-001 (`proved` upper bound only)**

The Fano plane has 7 lines and 7 points. The proxy `1/(7×7) = 1/49 ≈ 0.0204` is proved as
an upper bound in `CausalGraphTheory/AlphaFano.lean` (no sorry). Three candidate proxies
were tested; none match the physical value — all are bounds or rough order-of-magnitude
estimates.

**Open mechanism:** The exact value 1/137.036 is not derived. The challenge is that α
is an IR coupling that runs logarithmically from a UV boundary condition. Two candidate
approaches:
- **Combinatorial:** α ∝ (volume of U(1)_EM orbit in PG(2,2)) / (total Fano volume).
  The exclusive U(1) ratio gives 1/49; we need ~3× reduction to 1/137.
- **Functional approach:** Wyler (1969) computed `α ≈ (9/8π⁴)(π/4)⁵/5! ≈ 1/137.036`
  from the volume of a compact symmetric space. Baez (2002) partially explained this
  geometrically. If PG(2,2) volumes map to the same compact spaces, this could close.

**Priority: HIGH.** The most celebrated SM constant. A COG derivation would be a
landmark result.

---

### 2. Strong Coupling Constant α_s(M_Z) ≈ 0.1179
**Experimental:** α_s(M_Z) = 0.1179 ± 0.0010 (PDG 2022)

**COG status: 🔶 STRONG-001 (`proved` proxy, mechanism open)**

Proxy: `|Stab(e₇)| / |Aut(PG(2,2))| = 24/168 = 1/7 ≈ 0.143`.
This overestimates the physical value by ~20%, documented per RFC-026 honesty requirement.
Proved in `CausalGraphTheory/StrongCoupling.lean`.

**Open mechanism:** The 20% gap likely reflects:
1. Scale running: α_s(M_Z) = 0.118 but at the Planck or GUT scale α_s ≈ 1/7. Need
   COG RGE-analog (discrete running from Fano to IR).
2. The stabilizer Stab(e₇) ≅ S₄ (order 24) vs the full SU(3) generators. The correct
   identification may require projecting onto color-charged lines only.

**Priority: MEDIUM.** The proxy is physically motivated; the running is the gap.

---

### 3. Weak Mixing Angle sin²θ_W ≈ 0.23122
**Experimental:** sin²θ_W(M_Z) = 0.23122 ± 0.00003 (Z-pole, PDG 2022)

**COG status: 🔶 WEINBERG-001 (`partial` — UV fixed point proved, IR running open)**

UV structural observable: `sin²θ_W^(UV) = 1/4 = 0.25` from the exclusive U(1) ratio
`(|U1 mask| - |U1∩Weak|) / |EW mask| = 1/4`. Proved in multiple Lean theorems
in `CausalGraphTheory/WeakMixingObservable.lean`. The Z-pole target 0.23122 is NOT
yet derived — the scale-running bridge from UV 1/4 to IR 0.23122 is open (RFC-029).

**Open mechanism:** The gap (1/4 - 0.23122 = 0.01878) must come from radiative
corrections. In COG, this could be:
- Discrete RGE: The Fano geometry at the electroweak scale adds corrections via
  the non-vacuum Fano lines that "dress" the U(1) projector.
- Connes-NCG route: Todorov (2022, arXiv:2206.06912) derives `m_H/m_W` from
  `cos(θ_W^theory)` in Clifford algebra. The same algebra (Cl₆ ⊂ Cl₁₀) underlies
  COG's C⊗O structure. This is the most promising bridge.

**Priority: HIGH.** The UV 1/4 is a genuine algebraic result. Closing the IR gap
would immediately validate the Weinberg angle prediction.

---

## Group 2 — Charged Lepton Masses (3 parameters)

*General COG mechanism:* Mass = computational drag = tick frequency = gate density.
The three lepton generations map to the three orbits of the Stab(0) action on Fano
lines (LEPTON-001, proved): sizes {1, 3, 3}.

### 4. Electron Mass m_e = 0.51099895 MeV
**COG status: 🔷 Reference mass — absolute scale open**

The electron is the H⊂O state — lives in the associative quaternion subalgebra.
Gate density V_electron = 0 (no non-associative cost for H states). The electron
is massless at the pure COG level — its mass requires an absolute energy scale
(electroweak VEV or COG tick unit). The tick unit is the open "cosmological"
problem of COG.

---

### 5. Muon Mass m_μ = 105.6584 MeV → ratio m_μ/m_e ≈ 206.768
**COG status: 🔷 muon_mass.yml (active hypothesis)**

The muon is the second-generation lepton — orbit-A of Stab(0) (size-3, lines not
through 0). The ratio m_μ/m_e ≈ 206.768 must equal the tick-overhead ratio between
orbit-A and the H⊂O electron state. The factor ~206.8 = 2 × 103.4 does not obviously
map to a simple Fano combinatorial ratio, but note:
- |GL(3,2)| / |H| = 168/8 = 21 (too small)
- |GL(3,2)| / 2 = 84 (closer but wrong)
- 168 × 6 / (4+1) = 201.6 (near miss)
- No proved formula yet.

**Best angle:** KOIDE-001's Diophantine search may find a circulant matrix whose
eigenvalue ratio reproduces the lepton mass hierarchy including m_μ/m_e.

---

### 6. Tauon Mass m_τ = 1776.86 MeV → ratio m_τ/m_e ≈ 3477.5
**COG status: 🔷 Constrained by KOIDE-001**

The tauon is orbit-B of Stab(0) (size-3, lines through 0). The Koide formula
links all three: `(m_e + m_μ + m_τ) = (2/3)(√m_e + √m_μ + √m_τ)²`.
KOIDE-001 targets a Diophantine representation of the Koide factor Q ≈ 2/3 from
discrete COG algebra — specifically a circulant matrix with rational eigenvalue
ratio √B/A = √2. If proved, this fixes m_τ given m_e and m_μ, reducing three
free parameters to one absolute scale plus the Koide constraint.

---

## Group 3 — Quark Masses (6 parameters)

*General note:* Quark masses are not directly observable (confinement); they are
MS-bar renormalized masses. The COG mechanism for quark mass would be: higher
gate density for color-charged states (SU(3) non-associative overhead per Fano cycle).

### 7–9. Light Quarks: u ≈ 2.2 MeV, d ≈ 4.7 MeV, s ≈ 93 MeV
**COG status: ❌ No claims filed**

The light-quark mass ratios (m_u : m_d : m_s ≈ 1 : 2 : 42) must come from different
color-orbit configurations in PG(2,2). The fact that m_d > m_u despite down-quark
smaller charge is a challenge for any algebraic model.

**Best angle:** The 7 Fano points correspond to 7 octonion basis elements e₁–e₇.
Quarks come in (r,g,b) triples — 3-point non-collinear Fano triples (PROTON-001:
28 such triples proved). The three light quarks u,d,s form a flavor SU(3) triplet.
Their masses might map to the three eigenvalues of the color-permutation operator
on the 3-cycle Fano lines. **Claim idea: QUARK-001.**

### 10–12. Heavy Quarks: c ≈ 1.27 GeV, b ≈ 4.18 GeV, t ≈ 172.76 GeV
**COG status: ❌ No claims filed**

The top quark at 172.76 GeV is special — it's the only fermion with a Yukawa
coupling of order 1, suggesting it is the "natural" mass scale set by the
electroweak VEV. In COG, this means the top quark tick overhead ≈ electroweak
tick unit.

**Critical ratio:** m_t/m_W ≈ 2.15. If the W mass comes from the Higgs mechanism
(m_W = gv/2) and v is the COG energy scale, then m_t ≈ 2v/√2 × Y_t where Y_t ≈ 1.
**Claim idea: QUARK-002** (top quark as COG scale anchor).

---

## Group 4 — CKM Quark Mixing Matrix (4 parameters)

### 13–16. CKM angles θ₁₂ ≈ 13.04°, θ₁₃ ≈ 0.20°, θ₂₃ ≈ 2.38°, δ_CP ≈ 69°
**COG status: ❌ No claims filed**

The CKM matrix describes quark generation mixing. The Cabibbo angle θ₁₂ ≈ 13.04° is
the dominant parameter.

**Best angle (Cabibbo):** Duret & Machet (2006, arXiv:hep-ph/0607193) show
`tan(2θ_c) = ±1/2` from universality of weak neutral currents — giving cos θ_c ≈ 0.9732
(within 0.07% of experiment). In COG: the Cabibbo angle could be the geometric angle
between two Fano projective lines sharing a point. In PG(2,2), two distinct lines through
a common point define a "pencil" — the angle between them in the projective metric
might yield exactly `tan(2θ) = 1/2`. **Claim idea: CKM-001.**

**CP violation δ_CP:** In COG, CP violation would come from the complex phase of the
octonion product — the associator `[e_i, e_j, e_k]` is antisymmetric and can carry
a phase. Whether this matches δ_CP ≈ 69° requires computing the phase of the relevant
Fano automorphism. Open.

---

## Group 5 — Higgs Sector (2 parameters)

### 17. Electroweak VEV v ≈ 246 GeV
**COG status: ❌ Open — absolute energy scale problem**

The VEV v = (√2 G_F)^(-1/2) = 246.22 GeV sets the absolute energy scale of the
electroweak theory. In COG, this is the open "cosmological" or "calibration" problem:
what is the energy corresponding to one COG tick?

**Best angle:** The COG tick rate might be set by the mass of the lightest massive
particle (the electron at 0.511 MeV) or by the electroweak scale itself. If the
tick unit = ℏ/v, then v defines the frequency of forced evaluation. This is circular
without an independent determination. One approach: demand that the COG update rule
has a unique fixed point mass scale from the non-associativity of O — this could give
v in terms of G_Newton and ℏ via dimensional analysis in a Planck unit framework.
**Fundamental open problem.**

### 18. Higgs Mass m_H ≈ 125.25 GeV
**COG status: ❌ Open — but close approach exists**

**Best angle:** Todorov (2022, arXiv:2206.06912) derives `m_H/m_W = 2cos(θ_W^theory)`
from the Clifford algebra Cl₆ ⊂ Cl₁₀ structure. With the COG UV Weinberg angle
sin²θ_W = 1/4 → cos(θ_W) = √3/2 → `m_H/m_W = 2×(√3/2) = √3 ≈ 1.732`.
This predicts m_H ≈ √3 × 80.377 ≈ 139.2 GeV — about 11% above the measured 125.25 GeV.

If the IR Weinberg angle correction (0.25 → 0.231) is applied: cos(θ_W^IR) ≈ 0.8773 →
`m_H/m_W = 2 × 0.8773 ≈ 1.755 → m_H ≈ 141 GeV`. Still ~13% off.

The residual gap might close with radiative corrections in the COG framework.
**Claim idea: HIGGS-001** (bounds m_H from Fano + Weinberg angle; leaves correction open).

---

## Group 6 — QCD Theta Term (1 parameter)

### 19. θ_QCD < 10⁻¹⁰ (experimentally consistent with zero)
**COG status: 🔷 No formal claim — but compelling COG argument exists**

The "strong CP problem": why is θ_QCD so small? The SM provides no explanation.

**COG argument:** The discrete automorphism group GL(3,2) = Aut(PG(2,2)) preserves
the orientation of the Fano plane. The CP transformation corresponds to reversing
the orientation of all directed Fano triples. If the COG update rule is invariant
under this orientation reversal (Fano plane orientation reversal = complex conjugation
in C⊗O), then θ_QCD = 0 is forced geometrically — no axion required.

Formally: the Fano multiplication table is antisymmetric under sign reversal of
the structure constants (e_i × e_j → e_j × e_i = −e_i × e_j for i≠j), which is
equivalent to parity × time-reversal = CP. If the COG Lagrangian (action functional)
is invariant under this reversal by construction, θ_QCD = 0 follows.

**Priority: HIGH.** This would solve one of the major open problems of the SM.
**Claim idea: THETA-001.**

---

## Group 7 — Neutrino Sector (7–9 parameters with neutrino masses)

### 20–22. Neutrino Masses m_ν₁, m_ν₂, m_ν₃ < 0.1 eV each
**COG status: 🔷 Partially addressed via GEN-001**

GEN-001 proved that the vacuum-orbit state (neutrino index) has U(1) charge zero.
But the absolute mass scale is open.

**COG mechanism:** Neutrinos are the "vacuum orbit" states — orbit of size 1 under
Stab(0) (LEPTON-001). Their gate density is minimal (they don't excite the non-vacuum
Fano structure). This gives m_ν << m_e qualitatively. The seesaw scale Λ would come
from the ratio |GL(3,2)| / min(orbit) = 168/1 = 168, giving m_ν ≈ m_e / 168 ≈ 3 keV —
too large by a factor of ~30M compared to the experimental upper bound ~0.1 eV.
A double seesaw (Λ₁ × Λ₂) through two Fano structures might give the right scale.
Open.

### 23–26. PMNS Mixing: θ₁₂ ≈ 33.6°, θ₁₃ ≈ 8.5°, θ₂₃ ≈ 47.7°, δ_CP (unknown)
**COG status: ❌ No claims filed**

Note: PMNS angles are surprisingly large (quasi-democratic mixing) compared to CKM
(hierarchical mixing). In COG, this could reflect the difference between quark
(color-triplet) and lepton (color-singlet) orbit structures in PG(2,2).

**Best angle:** The "tribimaximal mixing" approximation gives sin²θ₁₂=1/3, sin²θ₂₃=1/2,
θ₁₃=0. These are strikingly simple fractions. In COG: the ratio 1/3 maps to
1/(orbit-A size) = 1/3 and 1/2 maps to the cardinality ratio of the vacuum line.
**Claim idea: PMNS-001** (tribimaximal mixing from Fano orbit ratios).

### 27–28. Majorana Phases φ₁, φ₂ (unknown experimentally)
**COG status: ❌ Not addressed**

Majorana phases only exist if neutrinos are their own antiparticles. In C⊗O, the
complex conjugation symmetry that relates particles to antiparticles could naturally
identify ν with ν̄ for the vacuum-orbit state. **Claim idea: MAJORANA-001.**

---

## Summary Table

| # | Parameter | Value | COG Claim | Status |
|---|-----------|-------|-----------|--------|
| 1 | α (EM coupling) | 1/137.036 | ALPHA-001 | 🔶 Upper bound 1/49 proved |
| 2 | α_s (strong) | 0.1179 | STRONG-001 | 🔶 Proxy 1/7 proved (+20%) |
| 3 | sin²θ_W | 0.23122 | WEINBERG-001 | 🔶 UV value 1/4 proved |
| 4 | m_e | 0.511 MeV | — | 🔷 Absolute scale open |
| 5 | m_μ | 105.66 MeV | muon_mass.yml | 🔷 Ratio 206.8 not derived |
| 6 | m_τ | 1776.86 MeV | KOIDE-001 | 🔷 Koide constraint near-proved |
| 7 | m_u | 2.2 MeV | — | ❌ No mechanism |
| 8 | m_d | 4.7 MeV | — | ❌ No mechanism |
| 9 | m_s | 93 MeV | — | ❌ No mechanism |
| 10 | m_c | 1.27 GeV | — | ❌ No mechanism |
| 11 | m_b | 4.18 GeV | — | ❌ No mechanism |
| 12 | m_t | 172.76 GeV | — | ❌ Scale anchor candidate |
| 13 | θ₁₂^CKM | 13.04° | — | ❌ Cabibbo = Fano projective angle? |
| 14 | θ₁₃^CKM | 0.20° | — | ❌ |
| 15 | θ₂₃^CKM | 2.38° | — | ❌ |
| 16 | δ_CP^CKM | ~69° | — | ❌ Associator phase candidate |
| 17 | v (EW VEV) | 246 GeV | — | ❌ Absolute scale — fundamental gap |
| 18 | m_H | 125.25 GeV | — | ❌ √3 m_W proxy: ~11% off |
| 19 | θ_QCD | ≈ 0 | — | 🔷 GL(3,2) CP symmetry argument |
| 20 | m_ν₁ | < 0.1 eV | — | 🔷 Vacuum orbit → suppressed |
| 21 | m_ν₂ | < 0.1 eV | — | 🔷 |
| 22 | m_ν₃ | < 0.1 eV | — | 🔷 |
| 23 | θ₁₂^PMNS | 33.6° | — | ❌ Tribimaximal 1/3 candidate |
| 24 | θ₁₃^PMNS | 8.5° | — | ❌ |
| 25 | θ₂₃^PMNS | 47.7° | — | ❌ Tribimaximal 1/2 candidate |
| 26 | δ_CP^PMNS | unknown | — | ❌ |
| 27 | φ₁ (Majorana) | unknown | — | ❌ |
| 28 | φ₂ (Majorana) | unknown | — | ❌ |

---

## Priority Ranking for New Claims

### Tier 1 — High impact, algebraically accessible

| Claim idea | Why now |
|-----------|---------|
| **THETA-001** θ_QCD = 0 | GL(3,2) CP symmetry forces it; provable with existing Fano tools |
| **WEINBERG-002** IR running | Gap from 1/4 to 0.231 via discrete Fano correction factors |
| **HIGGS-001** m_H bounds | Todorov Cl₆ route + COG UV angle give testable bound ~√3 m_W |
| **CKM-001** Cabibbo angle | Duret-Machet tan(2θ_c)=1/2 translates to Fano projective angle |
| **PMNS-001** Tribimaximal | sin²θ₁₂=1/3 from orbit-A size; sin²θ₂₃=1/2 from vacuum line ratio |

### Tier 2 — Harder, foundational

| Claim idea | Why it's harder |
|-----------|----------------|
| **QUARK-001** Light quark masses | Need flavor SU(3) structure in PG(2,2); no obvious mapping yet |
| **SCALE-001** Absolute energy scale | Requires connecting COG tick to ℏc/v; needs a mass anchor |
| **SEESAW-001** Neutrino mass scale | Double seesaw with two Fano geometries — speculative |
| **KOIDE-002** Quark Koide triplets | Experimental evidence for quark Koide triplets is weak |

### Tier 3 — Essentially open

| Claim idea | Blocker |
|-----------|---------|
| **QUARK-003** Heavy quark hierarchy | No discrete algebraic mechanism for the c–b–t mass ladder |
| **CKM-002** CP phase δ_CKM | Needs full complex phase of C⊗O associator; very hard |
| **MAJORANA-001** Neutrino mass type | Experiments inconclusive; COG prediction would be bold |

---

## Key Literature Anchors

| Reference | Relevance to COG |
|-----------|-----------------|
| Furey (2016), arXiv:1603.04078 | Charge quantization from number operator N/3 in C⊗O |
| Furey (2018), arXiv:1910.08395 | Three generations from (C⊗O)²; SU(3)×U(1) unbroken |
| Furey (2025), arXiv:2505.07923 | Z₂⁵-graded algebra = Jordan algebra H₁₆(C); gauge bosons + 3 generations |
| Todorov (2022), arXiv:2206.06912 | m_H/m_W from Cl₆ ⊂ Cl₁₀ + Weinberg angle; closest to COG |
| Langacker (2003), arXiv:hep-ph/0304186 | Standard reference for SM Lagrangian and free parameters |
| Koide (2005), arXiv:hep-ph/0506247 | Koide formula mechanism via Z₄×S₃ vacuum; maps to Fano |
| Duret & Machet (2006), arXiv:hep-ph/0607193 | Cabibbo angle from universality: tan(2θ_c)=1/2 |
| Baez (2002), arXiv:math/0105155 | Octonions in physics; compact symmetric spaces and α |

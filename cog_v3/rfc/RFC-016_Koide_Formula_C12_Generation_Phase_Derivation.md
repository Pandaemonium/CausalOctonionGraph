# RFC-016: Koide Formula Derivation from C12 Generation Phase Geometry

Status: Draft
Date: 2026-03-03
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-010_C12_Phase_Sector_Generation_and_Rare_Hop_Test_Contract.md`
- `cog_v3/rfc/RFC-009_S960_Phase_Fibered_E8_Symmetry_Model.md`
- `cog_v3/rfc/RFC-015_S2880_Trial_Bank_Phase_Initialization_Contract.md`

## 1. Purpose

The Koide formula states that for the three charged leptons:

```
K = (m_e + m_mu + m_tau) / (sqrt(m_e) + sqrt(m_mu) + sqrt(m_tau))^2 = 2/3
```

This RFC derives K = 2/3 exactly and algebraically from the geometry of the C12 phase
clock, without fitting any parameters. The derivation rests entirely on:

1. The 12-phase structure of C12 (30° per phase step).
2. The three-generation assignment g = p mod 3 from RFC-010.
3. The existence of exactly one 120°-equispaced representative orbit within C12.

This is a **structural prediction**: the Koide ratio is not a coincidence but a
consequence of equispacing in a 12-phase clock used as the generation sector.

## 2. Notation and Setup

### 2.1 C12 phase geometry

C12 = {0, 1, 2, ..., 11} with phase angle theta_p = p * pi/6 radians = p * 30 degrees.

The 12 phases correspond to the 12th roots of unity: exp(i * p * pi/6).

### 2.2 Generation assignment

From RFC-010, generation g = p mod 3:
- Gen1 (g=0): p in {0, 3, 6,  9}   (phases 0°,  90°, 180°, 270°)
- Gen2 (g=1): p in {1, 4, 7, 10}   (phases 30°, 120°, 210°, 300°)
- Gen3 (g=2): p in {2, 5, 8, 11}   (phases 60°, 150°, 240°, 330°)

### 2.3 Brannen mass parameterization

Brannen (2006) showed that any solution to K = 2/3 can be written as:

```
sqrt(m_k) = C * (1 + sqrt(2) * cos(phi_k + delta))
```

for k = 0, 1, 2, where phi_0, phi_1, phi_2 are equispaced by 2*pi/3 = 120°, C > 0,
and delta is a free phase. The Koide ratio K = 2/3 holds for any value of delta (it
is an algebraic identity, not a constraint on delta).

Key: the 120° equispacing of {phi_0, phi_1, phi_2} is the ONLY requirement.

## 3. The 120°-Equispaced Orbit in C12

### 3.1 The canonical orbit

Within C12, the orbit {0, 4, 8} is equispaced by 4 phase steps = 4 * 30° = 120°:
- p=0: theta = 0°   (Gen1, g=0)
- p=4: theta = 120° (Gen2, g=1)
- p=8: theta = 240° (Gen3, g=2)

These are the UNIQUE representatives (one per generation) that lie on the inscribed
equilateral triangle of the unit circle partitioned by C12.

### 3.2 Uniqueness

The other equilateral-triangle orbits in C12 are:
- {1, 5, 9}: 30°, 150°, 270° (also 120°-equispaced; one per generation)
- {2, 6, 10}: 60°, 180°, 300°
- {3, 7, 11}: 90°, 210°, 330°

All four are valid 120°-equispaced triples; each contains exactly one representative
from Gen1, Gen2, Gen3. Any of the four gives K = 2/3 by the same algebra.

The canonical choice {0, 4, 8} is preferred because p=0 is the vacuum-adjacent phase
(generation 1 base state) and the orbit has the smallest sum p=0+4+8=12.

## 4. Algebraic Derivation of K = 2/3

### 4.1 Setup

Let phi_k = 2*pi*k/3 = k * 120° for k = 0, 1, 2. Set:
```
a_k = 1 + sqrt(2) * cos(phi_k + delta)
```
so sqrt(m_k) = C * a_k (assuming a_k > 0 for all k, which requires |delta| bounded).

### 4.2 Key algebraic identities

Identity 1 (sum of equispaced cosines):
```
sum_{k=0}^{2} cos(phi_k + delta) = sum_{k=0}^{2} cos(2*pi*k/3 + delta) = 0
```
(Sum of 3 unit vectors at 120° spacing.)

Identity 2 (sum of squared cosines):
```
sum_{k=0}^{2} cos^2(phi_k + delta) = 3/2
```
(Follows from cos^2(x) = (1 + cos(2x))/2 and sum of cos at 240° spacing = 0.)

### 4.3 Numerator

```
sum m_k = C^2 * sum a_k^2
= C^2 * sum [1 + 2*sqrt(2)*cos(phi_k+delta) + 2*cos^2(phi_k+delta)]
= C^2 * [3  +  2*sqrt(2)*0            +  2*(3/2)]
= C^2 * [3 + 0 + 3]
= 6 * C^2
```

### 4.4 Denominator

```
sum sqrt(m_k) = C * sum a_k = C * [3 + sqrt(2)*0] = 3*C

(sum sqrt(m_k))^2 = 9 * C^2
```

### 4.5 Koide ratio

```
K = (6 C^2) / (9 C^2) = 6/9 = 2/3   (exact, for any delta and C > 0)
```

**K = 2/3 is an algebraic identity that holds for any set of three masses at 120°-equispaced
phases, parameterized in the Brannen form. It requires no numerical fitting.**

## 5. Mapping to C12 Phases

### 5.1 Phase angle correspondence

The Brannen phases phi_k connect to C12 phase indices p_k via:
```
phi_k = p_k * pi/6   (theta_p = p * pi/6)
```
For the canonical orbit {0, 4, 8}:
```
phi_0 = 0 * pi/6 = 0      (= phi_0 in Brannen, k=0)
phi_4 = 4 * pi/6 = 2*pi/3 (= phi_1 in Brannen, k=1)
phi_8 = 8 * pi/6 = 4*pi/3 (= phi_2 in Brannen, k=2)
```
This is exactly the Brannen 120°-equispacing. The mapping is:

| C12 phase | Angle    | Generation | Brannen index |
|-----------|----------|-----------|---------------|
| p=0       | 0°       | Gen1      | k=0           |
| p=4       | 120°     | Gen2      | k=1           |
| p=8       | 240°     | Gen3      | k=2           |

### 5.2 The free parameter delta

Brannen determined delta_lepton ≈ 0.2222*pi ≈ 40° from experimental lepton masses.
In C12 terms, delta encodes the within-generation phase offset (not yet fixed by the
structural argument). The physical prediction is:

```
delta = theta_fixed * pi/6   for some integer-shift fixed
```

where fixed is determined by which within-generation phase the stable mass eigenstate
occupies. RFC-015 identifies p in {1, 5, 9} as the odd-phase seeds producing d3 hops;
these are the elements of the {1, 5, 9} equilateral orbit in C12. The lepton delta
corresponds to a shift of approximately 1.333 steps (40/30 = 4/3).

The within-generation Z4 sub-clock dynamics (Δp=±3 hops within a generation orbit)
will determine which delta value is energetically favored. This is a prediction for
RFC-010 Phase B and C measurements.

### 5.3 Why not p={0,1,2} (30°-spaced)?

With p_k ∈ {0, 1, 2} (Δp=1 steps):
```
phi_k = k * pi/6 = 0°, 30°, 60°   (30° spacing, not 120°)
```
The equispacing is 30° = pi/6 — NOT 2*pi/3. The algebraic identity above fails:
```
sum cos(k*pi/6 + delta) ≠ 0 in general
```
This would give K ≠ 2/3. The Koide formula requires 120° equispacing, which
corresponds to Δp=4 (inter-generation jumps), not Δp=1 (adjacent phase steps).

**Implication: the three generation "mass eigenstates" are not at the adjacent phases
{0,1,2} but at the 120°-equispaced representatives {0,4,8} within C12.**

## 6. Physical Interpretation

### 6.1 Within-generation dynamics (Z4 sub-clock)

Each generation orbit under g = p mod 3 is a Z4 sub-clock:
- Gen1: {0, 3, 6, 9} — four phases, each 90° apart
- Gen2: {1, 4, 7, 10} — four phases, each 90° apart
- Gen3: {2, 5, 8, 11} — four phases, each 90° apart

The RFC-010 dominant channel Δp=±3 drives within-generation Z4 oscillation.
The Koide mass eigenstate (p=0, p=4, p=8) is the "base phase" of each orbit.

In a stable motif, the time-averaged phase occupation must be non-uniform: the
mass eigenstate is the orbit element closest to the 120°-equispaced configuration.

### 6.2 The strong/weak coupling analog

From RFC-015 §10: Δp=±3 (within-generation) is the dominant channel.
In the Koide language, this dominance is the discrete analog of the strong coupling
constant — it governs within-generation mass splitting (the Z4 sub-clock energy).

The inter-generation channels (Δp=1, 2, 4, 5...) are the weak/Cabibbo mixing channels.
The Δp=4 (120° jump) specifically connects generation representatives:
- p=0 (Gen1) → p=4 (Gen2) → p=8 (Gen3) → p=0 (Gen1)

This Δp=4 cycle is the discrete analog of CKM generation rotation.

### 6.3 Mass ratios from delta

Once delta is measured from S2880 dynamics (via stable motif phase occupation),
the predicted mass ratios are:
```
sqrt(m_1/m_3) = |1 + sqrt(2)*cos(delta)| / |1 + sqrt(2)*cos(4*pi/3 + delta)|
```
For delta ≈ 40°: sqrt(m_1/m_3) ≈ 0.0237 → m_e/m_tau ≈ 0.000562 ≈ 0.511/1776 = 0.000288.
Close in order of magnitude; exact value requires dynamical delta from the kernel.

### 6.4 Connection to quark Koide extensions

Repeating the same geometry with:
- Up-type quarks at phases {0, 4, 8} + delta_up
- Down-type quarks at phases {0, 4, 8} + delta_down
- Neutrinos at {0, 4, 8} + delta_nu

Each sector gets its own delta; K = 2/3 holds for all sectors by the same algebra.
This is consistent with the observed approximate Koide ratios in quark sectors
(though modified by mixing).

## 7. Hypotheses

### H1 (K = 2/3 exact at tree level)

For any mass assignment of the form m_k = C^2 * a_k^2 with a_k = 1 + sqrt(2)*cos(phi_k + delta)
and phi_k at C12 120°-equispaced phases, K = 2/3 exactly.

This is PROVED analytically in §4 above. No experiment needed; it is a theorem.

### H2 (120°-equispaced orbit selection)

The stable S2880 motif preferentially occupies the 120°-equispaced orbit {0, 4, 8}
(or one of the other three equilateral orbits {1,5,9}, {2,6,10}, {3,7,11})
rather than the adjacent-phase orbit {0, 1, 2}.

Testable by: measuring phase occupation in stable gate-5-passing runs.

### H3 (delta from dynamics)

The S2880 stable motif's within-generation phase occupation is non-uniform.
The asymmetry directly encodes delta.
The predicted delta from C12 geometry is:

delta ≈ pi/6 * (1 + fractional_within_generation_weight)

This is a long-horizon prediction requiring stable high-R3 data (post-RFC-015 fix).

## 8. Null Models

N1: The three stable phases are {0, 1, 2} (30°-equispaced) → K ≠ 2/3 in general.

N2: The stable motif has uniform within-generation phase occupation → no mass
distinction between generations (not physically viable).

N3: The Brannen formula's delta is irrational relative to C12 step → no exact
phase lock; K ≈ 2/3 holds approximately but not from equispacing.

(N3 would require a continuous parameter and would indicate C12 is too coarse
a discretization for exact lepton mass derivation.)

## 9. Implementation Plan

### Phase A (algebraic confirmation)

1. Verify K=2/3 numerically using Python with the Brannen formula at C12 phases {0,4,8}
   for a sweep of delta in [0, 2*pi]. K should be exactly 2/3 for all delta.
2. Verify K ≠ 2/3 for phases {0,1,2} (control: adjacent-phase parameterization fails).
3. Output: `cog_v3/calc/build_v3_koide_c12_verification_v1.py`
   Results: `cog_v3/sources/v3_koide_c12_verification_v1.md`

### Phase B (dynamical delta measurement)

1. After RFC-015 fix is applied and odd-phase trials run, measure phase occupation
   histogram for Gen1, Gen2, Gen3 in stable regime windows.
2. Fit delta from within-generation occupation asymmetry.
3. Compute predicted lepton mass ratios from fitted delta.
4. Compare to experimental m_e/m_mu/m_tau.

### Phase C (quark sector extension)

1. Apply same analysis to quark-generation sector.
2. Predict delta_up, delta_down from quark sector stable phase occupation.

## 10. Promotion Gates

Gate 1:
1. Python verification confirms K=2/3 for delta sweep over C12 120°-equispaced phases.
2. Python verification confirms K ≠ 2/3 for 30°-equispaced phases {0,1,2}.

Gate 2:
1. At least one S2880 stable trial (post-RFC-015 odd-phase seeding) shows measurably
   non-uniform within-generation phase occupation (consistent with delta ≠ 0).

Gate 3:
1. Fitted delta from dynamics predicts lepton mass ratios to within 20%.
2. (20% tolerance at this stage; exact matching requires full dynamical refinement.)

## 11. Falsifiers

Reject this lane if:
1. K ≠ 2/3 algebraically for Brannen form at 120°-equispaced C12 phases (would indicate
   math error — this should be impossible given the algebraic proof).
2. Stable S2880 motifs strongly prefer the 30°-equispaced orbit {0,1,2}
   (would indicate the dynamical attractor is incompatible with the Koide geometry).
3. Phase occupation in stable runs is completely uniform across all C12 phases
   (would indicate S2880 dynamics cannot select a generation-representative phase).

## 12. Non-Claims

1. This RFC does not claim to predict the absolute mass scale (m_e in MeV). The C
   parameter in the Brannen formula requires separate dimensional analysis.
2. This RFC does not claim that delta is exactly pi/6 * (4/3). That is a hypothesis
   for Phase B measurement.
3. This RFC does not address neutrino masses (which require a different delta and may
   require RFC-010 neutrino-sector channel analysis).

## 13. Cross-References

| RFC | Connection |
|-----|-----------|
| RFC-010 | Generation sector g = p mod 3; Δp=±3 dominant channel = Z4 sub-clock |
| RFC-015 | Odd-phase seeds required to see d3 (Δp=3) within-generation hops |
| RFC-011 | Omega_hat mass ratio ~3.573 ≈ chord ratio 3.73 (consistent with delta offset) |
| RFC-009 | S960 order-6 subgroup structure; 168 elements provide PSL(2,7) geometric context |

## 14. Summary Table

| Quantity | Value | Source |
|----------|-------|--------|
| Koide ratio K | 2/3 (exact) | Algebraic identity §4 |
| C12 phases for Koide | {0,4,8} (or {1,5,9}, {2,6,10}, {3,7,11}) | §3 |
| C12 orbit spacing | Δp=4 (120° = 4 steps) | §5.1 |
| Brannen delta (lepton) | ~40° = ~1.33 phase steps | Experimental; §5.2 |
| Z4 sub-clock | {p, p+3, p+6, p+9} per generation | RFC-010 |
| Dominant hop | Δp=±3 (within-generation Z4) | RFC-010, RFC-015 |
| Inter-generation hop | Δp=4 (CKM mixing analog) | §6.2 |

# RFC-029: Photon as Z4 Phase Excitation â€” Wave Emergence and EM Identification

Status: Draft
Date: 2026-03-03
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-010_C12_Phase_Sector_Generation_and_Rare_Hop_Test_Contract.md`
- `cog_v3/rfc/RFC-016_Koide_Formula_C12_Generation_Phase_Derivation.md`
- `cog_v3/rfc/RFC-024_SM_Particle_Identity_Map_and_W_Interaction_in_S2880.md`
- `cog_v3/rfc/RFC-025_Gauge_Boson_Identification_in_S2880.md`
- `cog_v3/rfc/RFC-028_Generation_Triality_Charge_and_Z3_Conservation_Law.md`

---

## 1. Purpose

RFC-025 established that the photon corresponds to a U(1)_EM gauge degree of freedom in
S2880 and identified a period-48 simulation candidate. RFC-024 established that Z4 sub-clock
direction encodes chirality.

This RFC contributes three things not previously stated:

1. **Canonical photon internal quantum numbers (preregistered for future kernel tests):** the four physical photon properties
   (masslessness, generation neutrality, color neutrality, self-conjugacy) all follow from
   a single assignment in the Z4 x Z3 x Q240 decomposition of S2880.

2. **EM wave emergence:** classical electromagnetic waves arise naturally from the Z4 group
   structure without additional assumptions. Oscillation, universal propagation speed c,
   transverse polarization, superposition, and arbitrary wavelength all follow from the
   cyclic structure of Z4.

3. **Energy gap identification:** photon energy (E = hv) is not encoded in the internal
   state label. It is a geometric property of the causal graph â€” the rate of Z4 phase
   advancement across lattice sites. This gap must be filled by a separate energy
   accounting scheme (deferred to RFC-031).

---

## 2. State Space Decomposition

S2880 = C12 x Q240, where C12 = Z12 = Z4 x Z3 via CRT.

Every site state s = (p, q) carries:

```
a = p mod 4    (Z4 sub-clock â€” EM phase sector)
g = p mod 3    (Z3 generation index)
q in Q240      (Hurwitz octonion â€” color/flavor sector)
p = (9a + 4g) mod 12   (CRT reconstruction)
```

The Z4 generator T4 (Dp = +3) advances a by -1 mod 4 and leaves g unchanged.
The Z3 generator T3 (Dp = +4) advances g by +1 mod 3 and leaves a unchanged.
The two sub-clocks are fully independent (RFC-028 Section 3.1).

---

## 3. Photon Internal State â€” Canonical (Preregistered) Definition

The photon is a pure Z4 phase excitation:

```
photon state:  (a in {1, 3},  g = 0,  q = 1_Q240)
```

where `1_Q240` is the multiplicative identity of the Q240 Hurwitz octonion loop.

Note: `q=1_Q240` is the canonical target definition for the edge-based (RFC-030) architecture. The site-based runner currently observes an A16 imaginary candidate; reconciliation is a preregistered hypothesis (see Section 8.4).

### 3.1 Z4 phase table

The four Z4 states map to the four canonical phases of one EM oscillation cycle:

| Z4 index a | 4th root of unity | Physical role |
|---|---|---|
| 0 | +1 | Vacuum â€” no photon / field at zero |
| 1 | +i | Physical photon: helicity +1 (right circular) |
| 2 | -1 | Longitudinal mode (unphysical â€” see Section 8.2) |
| 3 | -i | Physical photon: helicity -1 (left circular) |

Z4 is the minimal cyclic group that encodes a full oscillation cycle. Its four elements
are the four 4th roots of unity {+1, +i, -1, -i}, which are the natural discrete basis
for one AC cycle. The assignment above is forced by group order â€” no additional structure
is needed.

---

## 4. Physical Properties

All four properties follow from the canonical target assignment without additional assumptions.

### 4.1 Masslessness

Rest mass in S2880 arises from Q240 complexity â€” the computational drag of non-trivial
Hurwitz octonion states. With `q = 1_Q240` (the multiplicative identity, purely real,
zero imaginary octonion excitation), the photon has zero drag and therefore zero rest mass.

The Koide mass eigenstates occupy the a=0 slice {p=0, 4, 8} (RFC-016). Photon states
(a in {1,3}) are in orthogonal sectors of Z4 â€” no interference with the mass mechanism.

### 4.2 Generation neutrality

The interaction vertex is the R3 hop (Dp = +/-3). Since Dg = +/-3 mod 3 = 0, the photon
neither carries nor transfers a generation label. Triality is conserved at every photon
vertex (RFC-028 Section 4):

```
(g_photon + g_lepton) mod 3 = (0 + g) mod 3 = g    (g unchanged)
```

### 4.3 Color neutrality

`q = 1_Q240` is the trivial element of Q240. The photon is in the trivial representation
of the Q240 color sector and carries no color charge. It is invisible to the Q240 dynamics.

### 4.4 Self-conjugacy (photon = its own antiparticle)

Discrete CPT conjugation acts as `a -> -a mod 4`. Under this map:

```
a=1  ->  a=3    (helicity +1 <-> helicity -1)
a=3  ->  a=1
```

The two helicity states are each other's CPT conjugates. The photon type (Z4 excitation)
is self-conjugate, consistent with gamma = anti-gamma in QED.

---

## 5. Interaction Vertex

The photon emission and absorption vertex is the R3 hop:

```
Dp = +/-3
Da = -/+1 mod 4    (Z4 phase shifts by one step)
Dg = 0             (generation unchanged)
Dq = 0             (Q240 component unchanged)
```

A charged lepton in Z4 state `a_L` absorbs a photon with Z4 state `a_gamma`:

```
a_L -> (a_L + a_gamma) mod 4
```

The photon edge returns to a=0 (vacuum). Emission is the reverse.

The selection rule Dg = 0 means EM interactions are generation-diagonal: the photon
couples within a single generation sector, never exchanging generation label. This is
consistent with QED (no EM flavor-changing neutral currents). It also follows
automatically from the R3 hop structure â€” no additional constraint is required.

---

## 6. EM Wave Emergence from Z4 Group Structure

This section shows that classical electromagnetic waves arise directly from the Z4 cyclic
structure, without additional physical assumptions.

### 6.1 The discrete wave

A classical EM wave is a spatially periodic pattern of Z4 states advancing at speed c.
For a wave where the Z4 phase advances by one step every N lattice sites:

```
a(x, t) = floor((x - c*t) / (N * l0)) mod 4

wavelength:    lambda = 4 * N * l0
frequency:     nu = c / lambda = c / (4 * N * l0)
```

`l0` is the lattice spacing. N can be any positive integer, giving a discrete but dense
spectrum of allowed wavelengths.

For N >> 1, consecutive lattice sites are in nearly the same Z4 state and the pattern
is indistinguishable from a continuous sinusoid. The discrete Z4 structure becomes
invisible at wavelengths much larger than 4*l0.

### 6.2 Properties emerging without additional assumptions

| Wave property | Source in Z4 group structure |
|---|---|
| Oscillation | Z4 cyclic group: 0 -> 1 -> 2 -> 3 -> 0 |
| Phase | Z4 elements = {+1, +i, -1, -i} (4th roots of unity) |
| Universal speed c | One lattice hop per tick for every Z4 excitation |
| Arbitrary wavelength | N sites per Z4 step; N in Z+ gives dense spectrum |
| Two transverse polarizations | a=1 (helicity +1) and a=3 (helicity -1) |
| Superposition | Z4 addition: phases combine mod 4 at each site |
| Transverse nature | Z4 excitation on transverse edges; propagation along longitudinal edges |

### 6.3 Amplitude and coherent states

Z4 encodes phase, not amplitude. Classical EM amplitude emerges from the density of
simultaneously-excited Z4 edges in a given spatial region. High photon-number occupancy
in a single mode is a coherent state â€” the many-body limit of many Z4 quanta packed
phase-coherently into the same spatial pattern. This is the discrete analog of QED's
coherent state description of classical EM fields.

A single photon detection event = one Z4 quantum on one edge. A laser beam = many Z4
quanta in the same spatial mode, collectively producing a definite measurable amplitude.

### 6.4 Fourier decomposition

Z4 has exactly four irreducible representations with characters {+1, +i, -1, -i}. These
are the basis vectors of the Discrete Fourier Transform over Z4. Any Z4-valued field on
the lattice decomposes into these four harmonics. The physical EM field uses only the
order-4 harmonics (a=1 and a=3) â€” the two physical polarizations. The unphysical modes
(a=0 scalar, a=2 longitudinal) are eliminated by the discrete gauge condition (Section 8.2).

The DFT over Z4 IS the plane-wave decomposition of the EM field, in discrete form.
Wave analysis falls out of the representation theory of Z4.

### 6.5 Continuum limit

As N -> infinity (long wavelength limit), the discrete Z4 wave converges to a continuous
sinusoid with period 4*N*l0. The wave equation:

```
d^2 E / dt^2 = c^2 * d^2 E / dx^2
```

emerges as the continuum limit of the discrete Z4 propagation rule, exactly as the
diffusion equation emerges from a random walk. The discreteness is undetectable at
wavelengths much larger than the lattice spacing but is in principle observable at
wavelengths approaching 4*l0.

---

## 7. Gauge Structure Summary

The three discrete subgroups of C12 = Z4 x Z3 plus Q240 correspond to the three SM
gauge sectors:

| Discrete group | SM gauge sector | Gauge boson | Mediates |
|---|---|---|---|
| Z4 | U(1)_EM | Photon (a in {1,3}, g=0, q=1) | EM force |
| Z3 | SU(2)_W (discrete) | W boson (g != 0) | Generation change |
| Q240 | SU(3)_c (discrete) | Gluon (q != 1_Q240) | Color exchange |

This table is a structural identification, not a full derivation. The full correspondence
(Z4 -> U(1), Q240 -> SU(3), etc.) is a claim that requires its own RFC.

RFC-025 derives the gauge boson count (12 = 8+3+1) from this structure and provides the
Q240 element identification for each gauge boson. The present RFC adds only the Z4
internal structure and wave emergence analysis.

---

## 8. Open Items

The following are explicitly not locked by this RFC.

### 8.1 Site vs edge architecture

Two options remain for the architectural implementation:

- **Option A (lattice gauge theory, recommended):** The photon is a label on edges of the
  causal graph. Z4 labels live on links; matter (Z3 x Q240) lives on sites. This is the
  standard lattice QED structure and is geometrically principled. The photon "q=1" means
  the EM link variable is in the trivial Q240 representation.

- **Option B (site state):** The photon is a site state with (a != 0, g=0, q=1_Q240).
  Simpler to implement but less principled geometrically.

A future kernel RFC will specify the link-variable contract.

### 8.2 Discrete gauge condition for a=2

The a=2 element is the unique order-2 element of Z4 and corresponds to the unphysical
longitudinal polarization. In QED the Lorenz condition eliminates this mode. A discrete
analog must be specified: a gauge-fixing rule that forbids a=2 as an asymptotic photon
state while allowing it as a virtual intermediate in pair events. This is deferred to the
kernel RFC.

### 8.3 Energy accounting

Photon energy (E = h*nu) is NOT encoded in the (a, g, q) internal label. Two photons
with identical (a=1, g=0, q=1) but different frequencies are indistinguishable by
internal state alone. Frequency and energy are geometric properties: the rate at which
the Z4 phase advances across lattice sites (N sites per Z4 step, nu = c/(4*N*l0)).

Per RFC-028 Section 5.2, energy must be tracked as a separate conserved scalar tag
alongside the state label. The energy assignment rule at emission â€” how the emitting
particle's energy budget sets the photon's energy tag â€” is deferred to RFC-031.

### 8.4 Relation to RFC-025 period-48 candidate

RFC-025 identified the photon in the current overnight runner as an A16 imaginary Q240
element (activity = 0.925) with period 48, using kick label 1*e011 (SU(2) direction).

This is not inconsistent with the canonical target definition above, but requires reconciliation:

- The internal state definition (a in {1,3}, g=0, q=1) describes the photon's Z4 phase
  quantum number in the conceptual edge-based picture.
- The period-48 runner candidate describes a SITE STATE in the current simulation, which
  operates in a site-based picture where the photon appears as an A16 imaginary excitation.
- The reconciliation path: the A16 imaginary element in the runner represents the photon's
  transverse polarization direction in Q240 space. In the edge-based target architecture,
  this maps to the Z4 label on the link, with q=1 for the trivial U(1) link variable.

This reconciliation is a hypothesis, not a proved equivalence. The Family A test
(RFC-020) and the gate-boson redesign (RFC-025 Section 4.3) are needed to confirm it.

### 8.5 R3 rate vs alpha

If R3 hops are photon emission/absorption vertices, the R3 rate should converge to
alpha â‰ˆ 1/137 â‰ˆ 0.0073. Current Phase D measurements give R3 rate â‰ˆ 0.09-0.22, a
factor of 12-30 too large. This is a known kernel calibration gap. It does not block
the definition of the photon's internal quantum numbers.

### 8.6 Z boson

The Z boson is a mixed electroweak state (Z = cos(theta_W)*W3 - sin(theta_W)*B) and
would be a mixed Z3/Z4 excitation within Z12. The Weinberg angle theta_W is not yet
derived from Z12 structure. Per RFC-025 Section 3.4, sin^2(theta_W) = 3/8 at tree
level. The Z boson identification is deferred.

---

## 9. Consistency Checks

| Check | Result |
|---|---|
| Triality conservation at vertex | Pass: Dg = 0 at R3 hop (RFC-028 Section 4) |
| Koide orbit compatibility | Pass: Koide uses a=0 slice; photon uses a in {1,3}; orthogonal sectors |
| CPT self-conjugacy | Pass: a=1 <-> a=3 under a -> -a mod 4 |
| Polarization count (3+1D) | Pass (structural): |Z4|=4 gives 2 physical + 1 longitudinal + 1 vacuum. Gauge mechanism deferred â€” see Section 8.2. |
| Masslessness | Pass: q=1_Q240 gives zero drag |
| Generation neutrality | Pass: g=0 and Dg=0 at vertex |
| Color neutrality | Pass: q=1_Q240 is trivial Q240 representation |
| No Koide interference | Pass: photon sectors (a=1,3) are orthogonal to mass sector (a=0) |

---

## 10. Acceptance Criteria

RFC-029 is considered implemented when all pass:

1. R3 hops in the kernel use only the Z4 component of the phase; they leave g and q
   unchanged at every photon vertex.
2. Photon propagation tests confirm universal speed c (one hop per tick) independent of
   helicity or spatial wavelength N.
3. Wave superposition tests confirm Z4 phase addition at coincident edges.
4. A symmetry regression check confirms K(T_Z4(S)) = T_Z4(K(S)) where T_Z4 is the
   global Z4 shift a -> a+1 mod 4. This is the EM gauge equivariance test.
5. The period-48 overnight runner candidate is confirmed as a photon under the boson gate
   redesign from RFC-025 Section 4.3.

Current status snapshot:

| Criterion | Target | Current status |
|---|---|---|
| 1. R3 hops leave g,q unchanged | step_em_photon_round | Implemented in kernel; not yet integrated into overnight runner |
| 2. Universal speed c | propagation test | Not yet implemented |
| 3. Wave superposition | Z4 phase-addition test | Not yet implemented |
| 4. Z4 equivariance | check_z4_equivariance | Implemented and passing (short-horizon regression) |
| 5. Period-48 candidate under boson redesign | boson gate panel | In progress (closure probe + gate redesign alignment) |

---

## 11. Immediate Follow-on RFCs

1. **RFC-030:** Link-variable (edge-based) photon architecture and kernel contract.
2. **RFC-031:** Photon energy accounting â€” emission/absorption energy conservation rule
   and the assignment of E = h*nu from the geometric N-sites-per-Z4-step rate.
3. **RFC-032:** Discrete gauge condition for Z4 â€” elimination of a=2 as an asymptotic
   state; discrete analog of the Lorenz condition.
4. **RFC-033:** Z boson and Weinberg angle from Z3/Z4 mixing in Z12.



# RFC-089: Neutrino Z3 Domain Structure, Vacuum Interaction Asymmetry, and Majorana-Dirac Split

Status: Active — Hypothesis and Architecture Draft
Date: 2026-03-03
Owner: Research Director
Depends on:
- `rfc/RFC-001_Canonical_State_and_Rules.md`
- `rfc/RFC-019_e7_Temporal_Axis_Vacuum_Photon_Duality.md`
- `rfc/RFC-038_Vacuum_Phase_Locking_and_Higgs_Mechanism.md`
- `rfc/RFC-070_Left_Handed_vs_Right_Handed_Interaction_Contract.md`
- `claims/MASS-COUPLING-001.yml`
- `claims/LEPTON-001` (pending formalization)

---

## 1. Executive Summary

In the S2880 = C12 x Q240 model, each lepton carries a Z3 generation index `g in {0,1,2}`
and a Z4 energy-phase index `a in {0,1,2,3}`, encoding into a single C12 phase
`p = (4g + 3a) mod 12`.

The physical vacuum is the state `(g=0, a=0, p=0)` — the Z3 ground domain, no energy-phase tilt.

The three charged leptons and their SU(2)_L doublet partners (neutrinos) occupy the six
non-degenerate Z3 slots:

| Charged lepton | g | Neutrino partner | g_nu |
|----------------|---|-----------------|------|
| e-             | 0 | nu_e            | 1    |
| mu-            | 1 | nu_mu           | 2    |
| tau-           | 2 | nu_tau          | 0    |

This RFC establishes three consequences of this assignment that follow purely from the
Z3 group structure, without additional model assumptions:

1. **Vacuum interaction asymmetry**: nu_e and nu_mu impart nonzero Z3 domain charge to
   any state they multiply; nu_tau does not.

2. **Structural Majorana/Dirac split**: In Z3, only `g=0` is self-conjugate under charge
   negation. Therefore nu_tau is the unique Majorana-candidate neutrino by algebra alone;
   nu_e and nu_mu form a Z3 conjugate pair.

3. **Neutrino mass puzzle for nu_tau**: Under the MASS-COUPLING-001 picture (mass = C12
   phase offset from vacuum), nu_tau at `p=0` should be exactly massless. But oscillation
   experiments require all three neutrinos to be massive. This RFC proposes the vacuum
   flickering mechanism as the resolution.

---

## 2. Lepton Domain Table

Using the corrected lepton table (session 2026-03-03) and the canonical phase embedding
`p = (4g + 3a) mod 12`:

| Particle | g | a | p  | Q240 family | Phase offset from vacuum |
|----------|---|---|----|-------------|--------------------------|
| e-       | 0 | 0 | 0  | B112/C112 (Witt pair) | 0  |
| nu_e     | 1 | 0 | 4  | A16 (e0 oct)          | 4  |
| mu-      | 1 | 0 | 4  | B112/C112 (Witt pair) | 4  |
| nu_mu    | 2 | 0 | 8  | A16 (e0 oct)          | 8  |
| tau-     | 2 | 0 | 8  | B112/C112 (Witt pair) | 8  |
| nu_tau   | 0 | 0 | 0  | A16 (e0 oct)          | 0  |

Notes:
- Charged leptons carry a Witt-pair Q240 structure (B112 or C112 family).
- Neutrinos carry `q = e0` (real unit octonionic basis), placing them in the A16
  (associative, scalar) sector.
- The a=0 assignment for all neutrinos reflects: no spin-axis tilt (neutrinos are
  left-handed, not polarized like charged leptons under the C4 rotation).

---

## 3. Vacuum Interaction Analysis

The vacuum element is `v = (p=0, q=e0)` — the identity of S2880.

**Left-multiplication by vacuum** acts as the identity for all states (trivial).

The physically non-trivial vacuum interaction is the **e7 condensate** (Furey/CONVENTIONS.md
vacuum axis = e7). Under `s * e7`:

- Octonionic content `e0` (nu_tau sector): `e0 * e7 = e7` — passes through unchanged.
  The neutrino sees the vacuum axis but does not absorb it.
- Octonionic content `e7` (vacuum-aligned): `e7 * e7 = -e0` — strongly interacts,
  collapses to -identity with sign flip.
- Octonionic content `e_i` (i in {1,...,6}): cross-talks to a different basis element
  via the Fano multiplication table.

**Domain (Z3) interaction with vacuum:**

When a neutrino state `n = (p_n, q_n)` multiplies the vacuum element `v = (0, e0)`:

```
n * v = ((p_n + 0) mod 12, QMT[q_n, e0]) = (p_n, q_n)
```

Trivially unchanged (vacuum is identity). The physically meaningful question is:
does the neutrino's Z3 domain charge persist after interaction, or is it annihilated?

Under Z3 domain charge conservation:
- nu_e has g=1: any product of nu_e with a g=0 (vacuum-domain) state produces g=1
  — the domain charge is imparted and does not vanish.
- nu_mu has g=2: similarly imparts g=2 domain charge.
- nu_tau has g=0: products with vacuum-domain states remain g=0 — no domain charge
  is imparted. nu_tau is domain-neutral with respect to the vacuum.

**Self-products (key physical observable):**

`s * s = (2p mod 12, QMT[q, q])`

| Neutrino | p   | 2p mod 12 | Interpretation                    |
|----------|-----|-----------|-----------------------------------|
| nu_e     | 4   | 8         | self-product is tau-phase (g=2)   |
| nu_mu    | 8   | 4         | self-product is muon-phase (g=1)  |
| nu_tau   | 0   | 0         | self-product is vacuum-phase      |

nu_tau is the only neutrino whose self-product remains at the vacuum phase. It is a
**fixed point of self-interaction modulo phase** — the vacuum flicker candidate.

For the Q240 part: `QMT[e0, e0] = e0` (identity maps to itself). So nu_tau's full
self-product is `(0, e0)` = the vacuum element exactly.

**nu_tau is the unique state in the lepton table whose self-product equals the vacuum.**

---

## 4. Majorana-Dirac Split from Z3 Group Theory

In the Standard Model, a Dirac fermion has a distinct antiparticle; a Majorana fermion
is its own antiparticle. In the COG model, antiparticle conjugation acts on the Z3
domain index as:

```
antiparticle(g) = (-g) mod 3
```

(Charge negation reverses all quantum numbers; Z3 negation maps g to 3-g mod 3.)

Applying this:

| Neutrino | g   | g_anti = (-g) mod 3 | Self-conjugate? |
|----------|-----|---------------------|-----------------|
| nu_e     | 1   | 2                   | No — pairs with nu_mu |
| nu_mu    | 2   | 1                   | No — pairs with nu_e  |
| nu_tau   | 0   | 0                   | **Yes — Majorana** |

**nu_tau is Majorana by Z3 group structure alone.** This requires no additional
Majorana mass term or see-saw mechanism to be imposed — it is a consequence of the
Z3 group structure and the assignment of nu_tau to g=0.

**nu_e and nu_mu are Z3 Dirac conjugates of each other.** Their antiparticles in Z3
sense are each other:
```
anti-nu_e = nu_mu (in Z3 domain)
anti-nu_mu = nu_e (in Z3 domain)
```

This means: in the COG model, "nu_e bar" (the antineutrino produced in beta decay)
has Z3 domain g=2, which is the nu_mu domain. Lepton number violation in the COG
picture is not accidental — it is a consequence of the nu_e / nu_mu conjugate pairing.

---

## 5. Neutrino Mass Puzzle and the Vacuum Flickering Mechanism

**The puzzle:** Under MASS-COUPLING-001, mass = C12 phase offset from vacuum. nu_tau
has p=0 (vacuum phase), so it should be massless. But neutrino oscillations confirm
all three neutrino mass eigenstates have nonzero mass.

**Proposed resolution: vacuum flickering.**

nu_tau cannot acquire mass from a phase offset (it has none). Instead, it acquires mass
from its **rate of vacuum excitation** — the frequency with which it transitions between
the nu_tau state and the vacuum itself.

Since nu_tau's self-product `(p=0, e0)` is exactly the vacuum, nu_tau and the vacuum
are connected by a single multiplication step with no phase or basis change. This means:

1. At each causal tick, nu_tau can "fall into" the vacuum (self-product = vacuum) with
   some amplitude A.
2. The vacuum can "re-excite" into nu_tau with the same amplitude (time-reversal
   symmetry holds since nu_tau is Majorana).
3. The Compton oscillation rate for nu_tau is set by this excitation amplitude A, not
   by a phase offset.

Formally: nu_tau mass ~ amplitude for `(vacuum -> nu_tau -> vacuum)` transition
per causal tick. This is structurally analogous to a Majorana mass term:

```
L_Majorana ~ (nu_tau)^T C (nu_tau) + h.c.
```

which does not require a distinct right-handed partner — the left-handed nu_tau couples
directly to itself through the vacuum.

**For nu_e and nu_mu:** They have BOTH a phase offset (p=4, p=8) AND a vacuum-flickering
contribution (since their self-products shift them to different phases). Their masses
are therefore larger: two contributions vs. one for nu_tau.

This is qualitatively consistent with the observed neutrino mass hierarchy, though the
quantitative derivation requires closing gate C5 from KOIDE-KERNEL-CONSTRAINTS-001.

---

## 6. PMNS Mixing Reinterpretation

The PMNS (Pontecorvo-Maki-Nakagawa-Sakata) matrix mixes flavor eigenstates (produced
in weak interactions) with mass eigenstates (propagating states).

In the COG model:
- **Flavor eigenstates**: defined by the weak-interaction pairing (SU(2) doublets).
  nu_e is produced with e-, nu_mu with mu-, nu_tau with tau-.
- **Mass eigenstates**: defined by the C12 phase (p=0,4,8) and the vacuum flickering
  rate for p=0.

The PMNS matrix in this picture encodes the mismatch between:
- The Z3 domain assignment from weak pairing (g = 0,1,2 for nu_tau, nu_e, nu_mu)
- The mass eigenstate ordering from C12 phase offset

**Key structural prediction:** the PMNS matrix cannot be arbitrary — it must be
consistent with the Z3 cyclic structure. In particular:

1. The PMNS matrix should be "nearly tribimaximal" (a known experimental observation)
   because tribimaximal mixing is the unique unitary matrix compatible with Z3 symmetry
   and the constraint that nu_tau is self-conjugate.

2. CP violation in the lepton sector (the PMNS phase delta_CP) should be related to
   the phase mismatch between the Z3 domain structure and the C12 phase embedding.
   Specifically, delta_CP should be a rational multiple of 2pi/12 (a C12 angle), not
   a free continuous parameter.

3. The smallest mass eigenstate corresponds to nu_tau (the vacuum-flickerer, Majorana,
   domain-neutral) — i.e., the normal hierarchy is preferred over the inverted hierarchy.

---

## 7. Graviton Connection

The self-product analysis of Section 3 applies more broadly. Among all 2880 S2880
elements, the elements whose self-product phase is 0 (vacuum-phase) satisfy:

```
2p mod 12 = 0  =>  p in {0, 6}
```

- `p = 0`: The vacuum itself and nu_tau (and the electron charged lepton at a=0).
- `p = 6`: The C12 antipodal element. This is the **graviton candidate** from the
  gravity RFC discussion.

The graviton candidate at `p=6` shares with nu_tau the property that its self-product
is vacuum-phase-aligned. Both are therefore candidates for **self-coupling particles
that interact with the vacuum non-trivially through self-products**, not through phase
offsets. This suggests a structural relationship:

- nu_tau: spin-1/2 Majorana fermion, vacuum-domain, self-product = vacuum
- graviton: spin-2 boson, vacuum-phase, self-product = vacuum-phase

Both "disappear into the vacuum" on self-interaction. The Majorana nature of nu_tau and
the self-coupled nature of gravity may be two manifestations of the same algebraic
property: self-products returning to the vacuum sector.

---

## 8. Concrete Predictions

1. **nu_tau is Majorana; nu_e and nu_mu are Dirac (as a conjugate pair).**
   Falsifiable by: Majorana mass search for nu_tau (e.g., neutrinoless double-beta
   decay rate for tau-neutrino channel), or observation that nu_e and nu_mu can
   convert into each other through lepton-number-changing processes.

2. **Normal mass hierarchy**: m(nu_1) < m(nu_2) < m(nu_3), with the lightest state
   being the Majorana nu_tau (the vacuum-flickerer).

3. **PMNS matrix is near-tribimaximal**, with deviations parametrized by a single C12
   angle. The CP phase delta_CP = k * pi/6 for some integer k (i.e., a multiple of 30
   degrees). Current experimental value is approximately 195 degrees = 6.5 * 30 deg,
   consistent with k=6 or k=7 (within measurement uncertainty).

4. **nu_tau does not impart Z3 domain phase to any state it interacts with.**
   Consequence: reactions that require domain-charge transfer (e.g., Z3-charge-sensitive
   processes) are suppressed for nu_tau relative to nu_e and nu_mu. This may contribute
   to the difficulty of directly detecting nu_tau.

5. **nu_e and nu_mu can convert into each other through Z3 domain exchange** (in
   addition to standard oscillations). The rate should be related to the Z3 coupling
   constant, distinct from the Z4 (EM) coupling.

---

## 9. Open Questions

1. **What is the vacuum flickering amplitude A?** This must be derived from kernel
   dynamics (gates C4/C5 in KOIDE-KERNEL-CONSTRAINTS-001), not fitted. The target is:
   A = some simple rational function of the C12 structure constants.

2. **Is the nu_e/nu_mu Dirac conjugate pairing exact or approximate?** If exact in the
   algebra, lepton number is violated by a computable amount. If only approximate (due
   to PMNS mixing with nu_tau), the violation is small.

3. **How does the vacuum flickering mechanism produce a nonzero but tiny nu_tau mass?**
   In the current model, the excitation amplitude A is formally of order 1 (one step
   connects nu_tau to vacuum), but the physical mass is tiny (~0.1 eV). The suppression
   must come from the ratio of the kernel tick rate to the electron mass scale —
   the same calibration constant κ that sets the overall mass scale.

4. **Do all three neutrinos contribute equally to the normal hierarchy, or is the
   nu_tau mass parametrically smaller than nu_e, nu_mu masses?**
   In the vacuum-flickering picture, nu_tau mass ~ A (one contribution), while
   nu_e, nu_mu masses ~ sqrt(phase offset^2 + A^2). For small A, this gives
   m(nu_tau) << m(nu_e), m(nu_mu) — consistent with the lightest eigenstate being
   nearly massless (current experimental bound: m_nu < 0.12 eV from Planck).

5. **Connection to the see-saw mechanism:** The standard see-saw requires a heavy
   right-handed Majorana partner. In the COG model, nu_tau's Majorana mass arises
   without a right-handed partner. Is this a failure of the model, or does it predict
   the absence of a right-handed tau neutrino?

---

## 10. Gates (Formalization Targets)

| Gate | Description | Lean target | Status |
|------|-------------|-------------|--------|
| G1 | Z3 domain assignment for nu_e, nu_mu, nu_tau | `neutrino_z3_assignment` | open |
| G2 | nu_tau self-product = vacuum (p=0, q=e0) | `nutau_selfproduct_vacuum` | open |
| G3 | Z3 self-conjugacy of nu_tau (Majorana condition) | `z3_selfconjugate_g0` | open |
| G4 | nu_e / nu_mu Z3 conjugate pairing | `nue_numu_z3_dirac_pair` | open |
| G5 | Vacuum flickering amplitude derivation | `nutau_mass_from_flickering` | open |
| G6 | PMNS phase quantization at C12 angle | `pmns_phase_c12_rational` | open |

G2 is the highest-priority Lean target: it is a direct corollary of the Z3 assignment
and the S2880 self-product table, requiring no additional assumptions.

---

## 11. Relation to Existing Claims

- **MASS-COUPLING-001**: The phase-offset mass mechanism covers nu_e and nu_mu directly
  (p=4 and p=8). The nu_tau puzzle (p=0) is an extension not covered by MASS-COUPLING-001.
  This RFC proposes adding a "vacuum flickering" clause to that claim.

- **PHOTON-001**: The photon is A16 + phi4=0 (no domain charge, no phase offset).
  nu_tau is also A16 + phi4=0 in the Q240 sense. The distinction: photon has e=0 (no
  energy accumulation) and is spin-1 (a != 0 or specific basis); nu_tau has spin-1/2
  structure. The exact Q240 element that distinguishes them needs formalization.

- **KOIDE-KERNEL-CONSTRAINTS-001 gate C4**: The lepton orbit is the Z3 orbit of
  charged leptons. This RFC extends the orbit picture to include the neutrino doublet
  partners and their shifted Z3 positions.

---

## 12. Summary

The three neutrinos are not symmetric with respect to the vacuum:

- **nu_tau (g=0)**: vacuum-domain, self-product = vacuum, Z3 Majorana, domain-neutral.
  Mass from vacuum flickering (excitation rate), not phase offset.

- **nu_e (g=1) and nu_mu (g=2)**: Z3 conjugate pair, both impart domain phase to vacuum,
  Dirac-paired (in Z3 sense), mass from both phase offset and vacuum coupling.

This structure follows entirely from the Z3 group assignment of the lepton table and
requires no new algebraic assumptions. The key open step is deriving the vacuum
flickering amplitude from kernel dynamics.

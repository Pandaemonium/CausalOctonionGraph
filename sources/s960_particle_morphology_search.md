# S960 Particle Morphology: A Search Framework and Literature Survey

**Status:** Working Draft (2026-03-02)
**Depends on:**
- `rfc/RFC-001_Canonical_State_and_Rules.md`
- `rfc/RFC-004_Particle_Motifs.md`
- `rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md`
- `rfc/RFC-043_Motif_Catalog_v1.md`
- `rfc/CONVENTIONS.md`
- `sources/octavian_ideals_lit_review.md`

---

## 1. Introduction and Organizing Principle

The COG framework models physical reality as a directed acyclic causal graph.
Each node carries a discrete state in `OctIdx = {1,...,7}` (the seven imaginary
octonion basis elements).  The full state space from which seeds are drawn is
**S960**:

```
S960 = M_240 x Z_4 = { zeta * v : v in M_240, zeta in {1, i, -1, -i} }
```

where M_240 is the set of 240 Coxeter integral octonion units (the "octavians"
or "Cayley integers" on the unit sphere).  The Z_4 factor accounts for the four
complex phases.

This document asks: *what do elementary particles look like as stable repeating
motifs (orbits) in S960, and how would one search for them?*

### The Organizing Principle: Lightspeed Tractability

The single most powerful organizing idea for this search is:

> **A particle traveling at or near the speed of light cannot interact with its
> own causal past.**  Therefore its stability does NOT require a large
> self-generated supporting structure.  Its motif can be minimal.

Conversely, a massive, slow particle *does* interact with its own causal past,
so its stability may require a large surrounding cloud of self-generated
structure — potentially extending to the particle's physical size (femtometers).

This creates a tractability gradient:

| Particle | Speed | Self-interaction | Motif complexity | Tractable? |
|----------|-------|-----------------|-----------------|------------|
| Photon | c (exact) | None | Minimal (1 node) | Yes |
| Neutrino | ~c (tiny mass) | Negligible | Near-minimal (1-2 nodes) | Yes |
| Electron | v << c | Moderate | Small motif (1-4 nodes) | Likely yes |
| Muon | v < c | Moderate | Same topology, heavier drag | Likely yes |
| Pion | v << c | Strong | Small composite (2-3 nodes) | Possibly |
| Proton | v << c | Strong, confinement | Triplet + cloud | Uncertain |
| Nucleus | v << c | Very strong | Many-body | No |

The photon and neutrino are the natural first computational targets.  The
electron is a strong second.  The proton requires additional analysis of whether
its physical size (femtometer) maps to a topologically compact motif or an
intractably large one.

---

## 2. The S960 State Space (Recap)

### 2.1 Nodes, Edges, and Ticks

From RFC-001, a node is:

```
N : { id: Nat, state: OctIdx, tickCount: Nat }
```

The state `k` represents the imaginary octonion basis element e_k.  The seven
states map to physical roles:

- e_1, e_2, e_3: color-raising Witt half-pairs (Colors 1, 2, 3)
- e_4, e_5, e_6: color-lowering Witt half-pairs (Colors 3, 2, 1)
- e_7: vacuum axis / symmetry-breaking direction

### 2.2 The Interaction Rule and Branching

A three-body interaction event `(a, g, b)` computes:

```
s_L = (e_a * e_g) * e_b     (left-bracketed)
s_R = e_a * (e_g * e_b)     (right-bracketed)
```

If `{a, g, b}` is a Fano triple (one of 7 associative triples): `s_L = s_R`,
cost = 1 tick.

If `{a, g, b}` is a non-Fano triple (28 of 35 possible): `s_L = -s_R`, the
DAG *branches* into two causal futures, cost = 2 ticks.

The tick count accumulates as a measure of computational drag, identified with
inertial mass.

### 2.3 The 4/5 Branching Fraction

For a random triple, the probability of a branch is 28/35 = 4/5.  This is the
fundamental non-associativity fraction of the octonions.  Any stable motif must
have well-defined *expected* branching behavior.

A motif with zero branching (all interactions are Fano triples) is purely
associative and costs 1 tick per step — the minimum possible drag.  This is the
natural profile of a **massless particle**.

---

## 3. Photon Morphology

### 3.1 The Lightcone Argument

A photon propagates on the causal lightcone by definition.  In a DAG causal
graph, this means each photon node has exactly *one causal parent* — itself at
the previous tick — and no interaction with other nodes in the same "spatial"
slice.

Formally: the photon motif is a **singleton traveling node** with no incoming
edges from other non-photon nodes.  Its only "interaction" is with itself via
the temporal operator e_7 (the vacuum axis, which implements the Z_4 phase
clock under RFC-023).

### 3.2 The Weyl Equation from Discrete Causal Structure

The key result from Farrelly and Short (arXiv:1312.2852, 2014) is:

> *Any massless particle with a 2-dimensional internal degree of freedom
> whose dynamics are (i) discrete, (ii) causal (DAG structure), and (iii)
> unitary, necessarily satisfies the Weyl equation in the continuum limit.*

This is a uniqueness theorem: given the structural constraints of the COG
framework (discrete DAG, local update rule), a massless degree of freedom with
2 internal states **must** behave as a Weyl fermion (or, for its antiparticle
combination, a massless Dirac fermion or photon).

This directly constrains the photon motif.  A photon in S960 must have:
- 2 internal degrees of freedom (left- and right-circular polarization),
- mass zero (no branching, pure Fano-associative update path),
- causal propagation (one parent per step, no spacelike edges).

### 3.3 Candidate Photon Motif in S960

**Hypothesis (hypothesis-level):** The photon is a 1-node motif with state
cycling under the e_7 operator:

```
psi_photon(t) = (e_7)^t * omega_vac
```

where `omega_vac = (1/2)(1 + i*e_7)` is the vacuum idempotent (RFC-001 §4).

The Z_4 complex phase `zeta in {1, i, -1, -i}` provides exactly 2 real degrees
of freedom — matching the Farrelly-Short requirement.

The two polarization states correspond to `+i*e_7` and `-i*e_7` rotations
(left-hand vs right-hand helicity).

**Critical property:** Since this is a 1-node motif with no color-charge
excitation (state stays near e_7), there are no inter-node Fano products and
therefore **zero branching**.  Every step costs exactly 1 tick.  Mass = 0.
This is consistent.

### 3.4 Photon as Colorless: Witt Pair Selection Rule

In the Furey construction (RFC-040 §M2, §C1), states in the minimal left ideal
`J_1 = Cl(6) * f_1` are color singlets.  The vacuum idempotent `f_1` and the
e_7 axis are exactly the colorless directions.

A photon carrying no color charge lives entirely in the e_7 / vacuum sector,
confirming the single-node e_7-cycling motif hypothesis.

---

## 4. Neutrino Morphology

### 4.1 Why the Neutrino is the Best First Target

The neutrino is:
- Electrically neutral (no U(1) charge),
- Very light mass (sub-eV, compared to 511 keV electron),
- Traveling at nearly c (its deviation from c is ~10^-18 by current bounds),
- Uncharged under color (no SU(3) interactions).

In the S960 model, all of these constraints push the neutrino toward the
*simplest possible non-trivial motif* — barely distinguishable from the photon,
but with a tiny deviation from pure e_7 cycling.

### 4.2 Furey's Identification: Sterile Neutrino = Vacuum

In Furey's Cl(6) construction (arXiv:1405.4601, 1611.09182), the sterile
right-handed neutrino `nu_R` is identified with the vacuum state `omega_vac`
itself.  It is *not* a separate particle — it is the ground state of the
algebra.

If this identification holds in the S960 context, then the sterile neutrino
IS the vacuum motif M1 from RFC-040.  It requires no search — it is the
zero point.

### 4.3 Active Neutrino as a Perturbed Vacuum

The active (left-handed) neutrino `nu_L` is a small perturbation away from the
vacuum.  It is the lowest-lying excitation that:
- Carries SU(2)_L charge (weak isospin),
- Carries no color,
- Has tiny mass.

In S960 terms, this is a 1-node motif with a small but non-zero deviation from
the pure e_7 cycle.  The mass corresponds to a small non-zero branching
probability — perhaps 1 or 2 non-Fano interactions over a large period.

**Tractability argument:** Because the neutrino mass is ~10^-12 of the electron
mass, and mass = tick drag = branching frequency, the neutrino's branching rate
is roughly 1 non-Fano event per 10^12 ticks.  The orbital period is enormous
but the *core structure* (the minimal seed) should be 1-2 nodes.

**Recommended first search:** Enumerate all 1-node seeds `s in S960` and run
the RFC-001 update for 10^4 ticks.  Identify seeds that produce period-4 or
period-8 orbits with zero or near-zero branching.  These are neutrino candidates.

### 4.4 Three Generations

The three neutrino generations in the Furey framework correspond to three
copies of the minimal left ideal under a `C^3` Witt decomposition (Furey
arXiv:1611.09182, §5).

In the S960 search, three-generation structure would appear as three distinct
but topologically equivalent orbit families, distinguished by which Witt pair
is excited (Color 1, 2, or 3 direction).

---

## 5. Electron Morphology

### 5.1 The Furey S_minus Seed

From RFC-040 (§M2) and RFC-004 (§2.2), the electron motif seed is:

```
fureyElectronStateDoubled
```

which represents the algebraic state `Psi_e = alpha_1^dag * alpha_2^dag * alpha_3^dag * omega`
in Furey's creation operator notation.  This is a *fully anti-symmetrized*
combination that saturates all three color creation operators on the vacuum.

The key properties established in `FureyChain.lean` and `Spinors.lean`:
- nonzero state,
- exact period-4 under the e_7 stack (4-cycle orbit),
- U(1) charge sign: negative (-1, identifying it as the electron).

### 5.2 Period-4 Orbit and Mass

The electron's mass is finite, which in the COG framework means non-zero tick
drag from non-Fano branching events.  The period-4 orbit under e_7 matches the
Z_4 complex phase structure of S960 — the electron's orbital period is locked
to the vacuum's phase clock.

The ratio of electron mass to photon mass (0 vs 511 keV) corresponds to the
difference in branching rates: photon = 0 branches per orbit, electron = some
fixed non-zero number.

The current measured ratio `mu_COG = 8/3 ≈ 2.667` vs `mu_exp = 1836.15` shows
the proton-to-electron mass ratio is not yet correctly captured, but the
*electron itself* is well-grounded algebraically.

### 5.3 Electron as Minimal Color-Saturated Motif

The electron is the *minimally massive particle* that saturates all three color
Witt pairs.  By saturating all three, it becomes color-neutral (the three color
charges cancel to a singlet), consistent with the electron being uncharged under
SU(3)_c.

This is a fundamental structural insight: the electron cannot be reduced to a
smaller motif without losing one of the three anti-symmetrization operators.
A hypothetical 2-operator state would carry residual color charge and would be
a quark, not an electron.

### 5.4 Comparison to Photon

| Property | Photon | Electron |
|----------|--------|---------|
| Seed state | omega_vac (e_7 sector) | S_minus (fully antisymmetric) |
| Color charge | 0 | 0 (but internally 3-colored) |
| U(1) charge | 0 | -1 |
| Period | Continuous (lightlike) | 4 (under e_7 action) |
| Branching rate | 0 | Non-zero |
| Motif size | 1 node | 1 node (algebraically) |

Both are 1-node motifs algebraically.  The electron's additional complexity
lives in the internal algebraic structure, not in the number of nodes.

---

## 6. Quark and Proton Morphology

### 6.1 The Color Triplet Constraint

A quark cannot exist in isolation.  This is QCD confinement, and in the S960
model it has an algebraic correlate: a state carrying a single Witt-pair
excitation (one color direction) cannot form a stable closed orbit under the
update rule — it will always radiate or absorb color from the vacuum.

The *minimal stable color-neutral* composite from quarks is three quarks in a
color singlet, i.e., a baryon.  The three Witt pairs `(e_6, e_1)`, `(e_2, e_5)`,
`(e_3, e_4)` each contribute one quark, and their combination in an
antisymmetric tensor product gives the color-neutral (baryon number = 1) state.

RFC-004 §3.1 formalizes this as:
```
PROTON_INIT = (e_5, e_1, e_3)    -- one element from each Witt pair
Gluon exchange schedule: Color1<->2 -> Color1<->3 -> Color2<->3
```

### 6.2 The 3-Body Problem and Chaos

A proton motif involves three nodes in mutual interaction.  The 3-body problem
in classical mechanics is non-integrable (Poincaré's theorem), and while the
S960 system is discrete and deterministic, analogous quasi-periodic behavior
is expected.

**The proton triplet may not be strictly periodic.**  Instead, it may be:
- Quasi-periodic: the three nodes cycle through color states in a pattern that
  recurs approximately but not exactly.
- Asymptotically periodic: it converges to a periodic orbit after a long
  transient.
- Chaotic-but-confined: it explores a large but bounded region of state space.

Physical intuition suggests the third option is closest to correct.  The
proton *is* stable (it does not decay in the SM), but its internal color-field
structure is chaotic — this is precisely what lattice QCD models.

In S960 terms, the proton motif is a **confined strange attractor** rather than
a periodic orbit.  Its defining property is not a period but a basin of
attraction: many initial 3-node configurations flow under the update rule toward
the same chaotic attractor.

### 6.3 The Scale Problem

A proton has physical size ~1 fm = 10^-15 m.  The Planck length is ~1.6 × 10^-35 m.
Therefore:

```
Number of Planck voxels across one proton diameter ≈ (10^-15)/(1.6 × 10^-35)
    = 6.25 × 10^19 ≈ 10^20
```

If the proton's stability requires a *spatially extended* structure at the
Planck scale, the simulation is intractable.  A 10^20-node motif is not
computationally accessible by any foreseeable means.

However, the topological braid model (Section 8 below) offers a resolution:
the proton's *essential topological data* may be encodable in a compact 3-node
core, with the surrounding 10^20 Planck voxels constituting a dynamically
generated "vacuum foam" that is irrelevant to identity.

### 6.4 The Basin-of-Attraction Hypothesis

**If the proton motif has a large basin of attraction**, then:
1. Many initial 3-node configurations quickly flow toward the same attractor.
2. The proton is "robust" — it does not require fine-tuned initial conditions.
3. The surrounding Planck-scale structure is mostly vacuum modes that do not
   change the topological class of the motif.
4. The "effective proton" can be captured by a 3-node description.

This is exactly what we observe physically: protons form spontaneously from
quark-gluon plasma as it cools.  The basin of attraction is enormous.

This hypothesis is falsifiable: enumerate 3-node initial conditions from S960
and check what fraction flow to a stable triplet orbit.  If the fraction is
large (say, >1%), the basin-of-attraction hypothesis is confirmed and the
proton motif is tractable.

---

## 7. Braid and Topological Classification

### 7.1 The Bilson-Thompson Helon Model

Sundance Bilson-Thompson (2005, arXiv:hep-ph/0503213) proposed that all first-
generation SM particles can be represented as **framed braids on three strands**
("helons").  Each helon carries a charge ±1/3 or 0, implemented as a left- or
right-twist of the ribbon.

Key SM particles in this encoding:

| Particle | Braid word | Twist pattern |
|---------|-----------|--------------|
| Photon | Trivial (identity) | (0, 0, 0) |
| Electron | Full left twist | (-1/3, -1/3, -1/3) |
| u quark | Partial twists | (+2/3, 0, 0) [permuted] |
| d quark | Partial twists | (-1/3, -1/3, +2/3) [permuted] |
| W+ boson | sigma_1 sigma_2^-1 | crossing + twist |
| Z boson | Symmetric crossing | neutral braid |

The three strands map naturally to the three Witt color pairs in S960, and the
twist direction maps to the Z_4 complex phase.

Chester, Arsiwalla, and Kauffman (arXiv:2501.03260, 2025) have recently extended
this to include the SU(3) × U(1) sector and higher generations using "helon
diagrams," a graphical calculus for the braid group with color structure.

### 7.2 Embedding Braids in S960

In S960, a "braid" corresponds to a sequence of color-exchange operations (gluon
exchanges) between the three Witt pairs.  The topology of the braid word encodes
which pairs interact in which order.

The six gluon operators `{e_1, e_2, e_3, e_4, e_5, e_6}` form the generators
of SU(3) in the Witt pair basis (RFC-001 §2.2).  A braid word over these
generators defines a trajectory in the group algebra, and a **periodic braid
word** defines a closed orbit — a stable motif.

The Bilson-Thompson classification suggests:
- Leptons: braid words that are *pure braids* (no permutation of strands).
- Quarks: braid words that include a strand permutation.
- Gauge bosons: braid words with trivial permutation but non-trivial crossing.

This gives a concrete search strategy for S960: enumerate short braid words
over `{e_1,...,e_6, e_7}` and check which close (form periodic orbits).

### 7.3 Vaid's LQG Embedding

Vaid (arXiv:1002.1462, 2010) embedded the Bilson-Thompson model in a loop
quantum gravity framework by representing particles as "emergent" excitations of
the gravitational spin network.  In his construction:
- The spin network vacuum plays the role of M_240.
- Excitations above the vacuum are topological defects (braids).
- The SM particle spectrum emerges from the classification of stable braids.

This provides a conceptual bridge: the S960 vacuum (omega_vac) is the spin
network ground state, and particles are the stable braid excitations above it.

---

## 8. Search Methodology

### 8.1 Glider Search (Cellular Automaton Methodology)

The search for stable propagating structures in cellular automata (CAs) provides
the most mature methodology directly applicable to S960.

Martinez, Adamatzky, and colleagues (arXiv:1105.4332, 2011) demonstrated
systematic "supercollider" searches: they enumerate CA rules and initial
conditions, record all glider (propagating soliton) collisions, and catalog the
outcomes.  Gomez Soto and Wuensche (arXiv:1709.02655, 2017) found the minimal
glider gun (just 4 cells) in a 2D CA.

**Adapted for S960:**

1. **Enumeration phase:** For k = 1, 2, 3, ... nodes, enumerate all seeds in
   S960^k (k nodes, all states from OctIdx × Z_4).

2. **Propagation phase:** Run each seed under the RFC-001 update rule for
   N = 10^4 ticks.

3. **Periodic orbit detection:** Check if the sequence of states is (a) exactly
   periodic, (b) quasi-periodic within epsilon, or (c) chaotic/divergent.

4. **Classification:** For periodic orbits, extract the braid word, the period
   T, the total tick cost C_T (sum of ticks over one period), and the branching
   count B.

5. **Signature matching:** Compare (T, C_T, B, charge_sign) against the
   expected signature from the motif catalog (RFC-043).

For k=1: enumeration is over 7 × 4 = 28 seeds (7 OctIdx values × 4 Z_4
phases).  This is trivially exhaustive.

For k=2: enumeration over (28)^2 = 784 seed pairs.  Trivially exhaustive.

For k=3: enumeration over (28)^3 ≈ 22,000 seed triples.  A few minutes of
Python.

For k=4: ~600,000 seeds.  Still feasible in a day.

This exhaustive search of small-k motifs should be the immediate next
computational step.

### 8.2 Basin-of-Attraction Analysis

Given a candidate stable orbit O*, define its **basin of attraction** as:

```
B(O*) = { seeds s in S960^k : update_rule^N(s) converges to O* }
```

Measure |B(O*)| / |S960^k| as the basin fraction.  A large basin fraction means:
1. The motif is physically natural (many initial conditions lead to it).
2. The motif is robust to perturbations.
3. The surrounding Planck-scale structure is irrelevant (it flows to the same attractor).

This is the key metric distinguishing a "real particle" from an artifact.

### 8.3 Replay Hash Stability (RFC-043 §7)

Per RFC-043 §7, motif promotion requires "deterministic replay hash stability."
This means: given a motif seed and a fixed rule profile, running the simulation
twice always produces the same sequence of states.

For the S960 update rule this is automatic (the rule is deterministic), but the
branching protocol introduces non-determinism: when `s_L = -s_R`, both branches
are spawned.  The branching tree must be pinned by a fixed traversal order for
replay stability.

**Recommended:** always traverse branches in lexicographic order of the
resulting state index (smaller OctIdx first).  This gives a canonical "left-
preferred" execution that is reproducible.

### 8.4 Topological Invariant Search (Braid Classification)

Rather than enumerating individual seeds, enumerate braid words:

1. Generate all braid words of length L over generators `{e_1, e_2, e_3, e_4, e_5, e_6}`
   (the color-exchange operators).

2. For each braid word `w = g_1 g_2 ... g_L`, compute the S960 orbit of the
   vacuum under sequential application of `w`.

3. Check if the orbit is closed (returns to vacuum) or open (drifts to a new
   stable state).

4. Closed orbits under a color-exchange braid word = color singlet composite motif.
5. Open orbits (drifting to a non-vacuum state) = particle creation event.

This is more algebraically principled and directly connects to the Bilson-
Thompson classification.

### 8.5 Near-Vacuum Perturbation Search

A targeted approach for lepton candidates:

1. Start from `omega_vac` (the vacuum seed).
2. Apply a single gluon perturbation: `psi_1 = e_k * omega_vac` for each k in {1,...,7}.
3. Run for N = 10^3 ticks and observe: does the system return to vacuum, orbit
   stably, or diverge?

This directly tests which single-operator excitations above the vacuum are
stable.  The electron corresponds to a 3-operator excitation (all three color
operators applied).  The photon is the e_7 perturbation.  A single-color
excitation is a quark (which will be unstable in isolation, by confinement).

---

## 9. Tractability Assessment and Recommendations

### 9.1 Summary Table

| Target | Motif size | Expected period | Search cost | Verdict |
|--------|-----------|----------------|-------------|---------|
| Photon | 1 node | Continuous/lightlike | Trivial | Tractable now |
| Sterile neutrino (nu_R) | 0-1 nodes | = vacuum period | None (it IS the vacuum) | Done |
| Active neutrino (nu_L) | 1 node | Very long (mass ~ 0) | Small k=1 exhaustive | Tractable now |
| Electron | 1 node (algebraic) | 4 | k=1 exhaustive | Tractable now |
| Positron | 1 node (algebraic) | 4 | k=1 exhaustive | Tractable now |
| Muon | 1 node (diff. sector) | 4 (different drag) | k=1 exhaustive | Tractable now |
| Pion | 2 nodes | Small | k=2 exhaustive | Tractable |
| Kaon | 2 nodes | Longer | k=2 exhaustive | Tractable |
| Proton | 3-node core | Quasi-periodic | k=3 exhaustive | Likely tractable |
| Neutron | 3-node core (metastable) | Quasi-periodic | k=3 exhaustive | Likely tractable |
| Nucleus | > 10 nodes | Complex | k > 5 | Intractable |

### 9.2 The Femtometer Scale Problem (Proton)

The proton's physical size (1 fm) requires ~10^20 Planck voxels if the proton's
stability depends on its full spatial extent.  However, three lines of argument
suggest the topological core is only ~3 nodes:

1. **Bilson-Thompson:** All SM particles including proton are describable by
   3-strand braid words.  The 3 strands map to 3 quarks.  The surrounding
   gluon field is the "vacuum foam" generated by color exchange.

2. **Basin of attraction:** If the proton basin is large (> 1% of k=3 state
   space), the 10^20 surrounding voxels all flow to the same attractor
   regardless of their initial state.  The proton "core" is the attractor,
   not the cloud.

3. **Confinement as automatic stability:** In QCD, confinement means any
   color-charged excitation is automatically attracted back to the color-singlet
   ground state.  This acts as an automatic stability mechanism: the proton
   motif does not need a specific surrounding cloud; *any* surrounding
   configuration will eventually shed its color charges and contribute to the
   vacuum foam.

**Recommended test:** Run k=3 basin-of-attraction analysis and measure the
fraction of initial conditions that converge to a stable triplet.  If > 1%,
the femtometer scale problem is resolved and the proton is tractable.

### 9.3 Recommended Research Order

1. **Immediate:** Run exhaustive k=1 search over S960.  Identify all
   period-1, period-2, period-4 orbits.  Match against known particle
   signatures (vacuum, neutrino, electron, photon).

2. **Short-term:** Run k=2 search.  Find all 2-node stable orbits.
   Match against meson candidates (pion, kaon, photon pair).

3. **Medium-term:** Run k=3 search + basin analysis.  Find triplet attractor.
   Test basin fraction.  This either confirms the proton is tractable or
   falsifies the minimal-core hypothesis.

4. **Parallel theory:** Enumerate braid words of length 1-6 and classify
   closed vs open orbits.  Cross-reference with SM spectrum.

---

## 10. Literature Summary

### Most Relevant Papers

| arXiv ID | Authors | Year | Relevance |
|----------|---------|------|-----------|
| 1312.2852 | Farrelly, Short | 2014 | **KEY:** Massless particle w/ 2D internal DoF in any discrete causal dynamics -> Weyl equation. Uniqueness theorem for photon morphology. |
| hep-ph/0503213 | Bilson-Thompson | 2005 | **KEY:** SM particles as framed 3-strand braids. Direct motif classification scheme. |
| 0903.1376 | Bilson-Thompson, Hackett, Kauffman | 2009 | Extension to all three generations; framed Artin braid group. |
| 2501.03260 | Chester, Arsiwalla, Kauffman | 2025 | Modern helon revision with SU(3) x U(1) sector. |
| 1002.1462 | Vaid | 2010 | Embedding B-T in LQG via geometric condensate of tetrads. |
| 0806.3083 | Johnston | 2008 | Particle propagators on causal sets via discrete path integral. |
| 1105.4332 | Martinez et al. | 2011 | Cellular automaton supercolliders: glider collision catalog methodology. |
| 1709.02655 | Gomez Soto, Wuensche | 2017 | Minimal glider-gun in 2D CA: 4-cell minimal seed. |
| 1405.4601 | Furey | 2014 | Cl(6) construction; nu_R = vacuum; electron as 3-operator excitation. |
| 1611.09182 | Furey | 2016 | One generation from Cl(6), three generations from C^3 Witt decomposition. |
| 2209.13016 | Furey | 2022 | Unification of three generations in H16(C). |

### Supporting Papers

| arXiv ID | Authors | Year | Relevance |
|----------|---------|------|-----------|
| gr-qc/9704066 | Montesinos et al. | 1997 | Fermion mass gap in loop representation. |
| 1210.1485 | Girelli et al. | 2012 | LQG phenomenology: discrete Planck-scale effects. |
| 2403.00360 | Finster et al. | 2024 | Causal fermion systems: wave equation emergence. |

---

## 11. Key Open Questions

1. **Does the photon motif `psi(t) = (e_7)^t * omega_vac` satisfy the RFC-040
   orbit closure predicate (OrbitPredicate)?**  This requires defining what
   "orbit" means for a lightlike trajectory in the DAG, since the photon never
   returns to a previously visited node.

2. **What is the correct minimal motif for the active neutrino?**  It should be
   distinguishable from the vacuum but should have near-zero branching rate.
   Does such a motif exist in S960 at k=1?

3. **Does the k=3 exhaustive search over S960 find a triplet attractor with a
   large basin of attraction?**  This is the primary empirical test of the
   proton tractability hypothesis.

4. **Do the three neutrino generations correspond to three distinct k=1 orbits,
   and are they identifiable in the k=1 exhaustive search?**

5. **What is the S960 analog of the braid group crossing?**  The Bilson-
   Thompson model uses ribbon crossings; in S960 these might correspond to
   specific sequences of Fano-triple vs non-Fano-triple interactions.

---

## 12. Conclusion

The COG/S960 framework provides a well-defined computational substrate for
searching for elementary particle motifs.  The lightspeed tractability argument
identifies the photon, neutrino, and electron as the natural first targets —
all are plausibly 1-node motifs whose stability can be tested by exhaustive
enumeration.

The Farrelly-Short theorem provides theoretical grounding for the photon
morphology: any massless 2D-internal-DoF particle in a discrete causal graph
*must* satisfy the Weyl equation.  The e_7-cycling vacuum perturbation is the
natural photon candidate.

The proton presents the deepest challenge.  Its stability may require either
a large surrounding structure (10^20 nodes, intractable) or a compact topological
core (3 nodes, tractable).  The basin-of-attraction analysis is the decisive test.

The Bilson-Thompson braid classification provides a rich framework for
enumerating and classifying motif candidates without full enumeration of the
state space.  It is directly compatible with the S960 Witt pair structure and
should be formalized as part of the RFC-043 motif catalog.

**Immediate deliverables:**
1. Python script: exhaustive k=1 S960 orbit search (`calc/s960_orbit_search_k1.py`).
2. Python script: k=3 basin-of-attraction analysis (`calc/s960_basin_k3.py`).
3. Braid word closure test (`calc/s960_braid_closure.py`).

---

*Evidence level: `hypothesis` (literature-supported analysis; no Lean proofs
or Python verification yet for the specific claims here).*
*Rule profile: RFC-028 canonical update rule (Fano multiplication, Z_4 phase).*
*Spin mode: not yet declared (pending RFC-056 alignment).*

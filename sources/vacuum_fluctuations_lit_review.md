# Vacuum Fluctuations in Discrete and Algebraic Spacetime Models
## A Critical Literature Review for the COG Project

**Date:** 2026-02-23
**Status:** Reference document — informs RFC architecture decisions, no code changes.
**Related:** `rfc/RFC-013_Algebraic_Vacuum_and_Causal_Spawning.md`

---

## 1. Purpose and Scope

This review surveys the literature on vacuum states and vacuum fluctuations across four
discrete/algebraic approaches to spacetime: causal set theory, causal dynamical triangulations
(CDT), loop quantum gravity (LQG), non-commutative geometry (NCG), and the division-algebra
Standard Model programme (Furey, Dixon, Todorov). A fifth section covers the question of
whether virtual particles and the Casimir effect genuinely require a "boiling vacuum."

The goal is to answer, critically and with arXiv citations, the question: **how should the
COG framework handle vacuum fluctuations?**

---

## 2. The Standard-QFT Picture: What COG Is Replacing

In perturbative quantum field theory (QFT), the vacuum |0⟩ is the Fock-space state with
no on-shell particles, but it is not "empty." It has nonzero energy from the zero-point
contributions of every mode, and Green's functions evaluated in |0⟩ receive corrections from
virtual-particle loop diagrams. The "boiling vacuum" picture is real within that formalism.

**Two things must be distinguished immediately:**

1. **The vacuum STATE** — a well-defined algebraic object (a density matrix or wave function
   over field configurations).
2. **Virtual particles** — Feynman-diagram internal lines; perturbation-theory artifacts that
   do not correspond to any gauge-invariant, on-shell observable.

Point 2 is not controversial: in the modern operator-algebraic formulation of QFT (the
Haag-Kastler axioms), there is no reference to virtual particles at all. As pointed out by
Cortes and Smolin (arXiv:1308.2206), the virtual-particle ontology is not fundamental — it is
an artefact of expanding around a particular background state in perturbation theory.

The question for COG is how to construct a **vacuum STATE** on a discrete causal graph that
does not require virtual particles or background continuous fields.

---

## 3. Causal Set Theory: The Sorkin-Johnston Vacuum

### 3.1 Defining the Vacuum Without Time-Slicing

The dominant formal programme for QFT on discrete causal structures is Sorkin's causal set
theory. The central challenge is that the standard vacuum definition — the state annihilated
by all positive-frequency operators — requires a Cauchy surface, a global time function, and
a Fourier decomposition. None of these exist on a generic causal set (or a causal DAG).

Sorkin (arXiv:1107.0698, "Scalar Field Theory on a Causal Set in Histories Form") shows this
explicitly: "the great majority of causal links will 'pass through' a maximal antichain without
meeting it at all; information can pass through without registering on it — the impossibility
of which is precisely what characterizes a Cauchy surface in the continuum."

The solution, developed by Sorkin and Johnston (Johnston PhD thesis, arXiv:1010.5514; Sorkin
arXiv:1703.00610), replaces the mode-decomposition vacuum with the **Sorkin-Johnston (SJ)
state**:

```
W = Pos(iΔ)  =  (iΔ + √(−Δ²)) / 2
```

where:
- Δ(x,y) = G_ret(x,y) − G_adv(x,y) is the **Pauli-Jordan (commutator) function** built
  from the retarded Green function G_ret of the discrete d'Alembertian.
- Pos(·) extracts the **positive spectral part** of the self-adjoint operator iΔ.
- W(x,y) = ⟨φ(x)φ(y)⟩ is the resulting Wightman two-point function.

This construction has four key properties for COG:

| Property | Consequence for COG |
|----------|---------------------|
| Built from G_ret alone | The vacuum is determined entirely by causal order — no background metric, no Killing vector, no time-slicing. |
| Uniquely determined by Δ | Given a fixed causal set, there is exactly one SJ vacuum (no gauge freedom, no Bogoliubov ambiguity). |
| Reduces to Minkowski vacuum | In flat Minkowski spacetime the SJ state converges to the standard Poincaré-invariant vacuum. |
| Non-Hadamard at boundaries | The SJ state is NOT Hadamard at the boundaries of causal diamonds (arXiv:2212.10592, Zhu-Yazdi 2022). This means the standard QFT renormalization machinery does not apply. |

The SJ construction is the strongest existing existence proof that a **deterministic,
non-perturbative vacuum** can be extracted from a discrete causal structure. For COG,
the analog of G_ret is precisely the causal adjacency structure of the DAG: G_ret(x,y) = 1
iff there is a directed path from y to x in the DAG.

### 3.2 Stochasticity in Causal Sets: Growth Dynamics vs. Vacuum

A critical distinction that Gemini's analysis conflates: in causal set theory there are **two
distinct levels** at which stochasticity can enter.

**Level 1 — The growth dynamics** (Rideout-Sorkin, arXiv:gr-qc/9904062): How does the causal
set grow? The "classical sequential growth" model is explicitly stochastic — a Markov process
with transition probabilities satisfying causality and general covariance. The universe is a
random causal set drawn from this Markov process.

**Level 2 — The vacuum on a fixed causal set**: Given a fixed causal set C, the SJ vacuum is
uniquely and deterministically determined by the causal order. No stochasticity enters at this
level.

**COG implication:** The COG project's deterministic Prime Directive is fully compatible with
Level 2 — the vacuum on a fixed DAG is deterministic. The question of Level 1 (whether the
DAG itself grows stochastically or deterministically) remains open in COG and should not be
conflated with the vacuum structure.

### 3.3 The Cosmological Constant as a Discreteness Effect

Sorkin (arXiv:0710.1675) made a successful pre-observation prediction: the cosmological
constant in a discrete spacetime is not the Planck density but fluctuates with value

```
Λ ~ 1 / √N   (in Planck units)
```

where N is the number of causal set elements in the current Hubble volume. This prediction,
made before the 1998 supernova observations confirmed accelerating expansion, is widely
regarded as one of the strongest qualitative successes of causal set theory.

The mechanism: in a discrete spacetime, vacuum-energy contributions do **not** coherently add
to Planck density. Fluctuations partially cancel, leaving only a 1/√N residual. The
cosmological constant problem — the 120-order-of-magnitude discrepancy between the QFT
prediction and observation — is an artefact of continuous spacetime forcing all UV modes to
contribute additively.

**COG implication:** The SPAWN protocol's "lazy" vacuum creation (vacuum nodes only exist where
photons create them) is structurally compatible with this picture. The total number of active
causal nodes in the COG graph is finite and determined by the matter content, not by an
infinite pre-existing background. The cosmological constant problem does not arise.

### 3.4 Interacting Fields: pAQFT, Not Loop Diagrams

Dable-Heath, Fewster, Rejzner, Woods (arXiv:1908.01973) constructed the first interacting
scalar QFT on a fixed causal set background using **perturbative algebraic QFT (pAQFT)**.
The key point for COG: the interactions are added via **algebraic deformation maps** on the
observable algebra, not by summing Feynman loop diagrams with virtual particles.

The "vacuum polarization" diagram (photon → e⁺e⁻ loop → photon) corresponds in this
framework to a **correction to the two-point function** computed via the relative Cauchy
evolution — an algebraic map measuring how the algebra of observables changes when the causal
structure is perturbed. No virtual particles are created; no particle ontology is needed.

---

## 4. Causal Dynamical Triangulations: Vacuum as Emergent de Sitter Geometry

CDT (Ambjorn, Gorlich, Jurkiewicz, Loll) produces a macroscopic 4D de Sitter geometry from
a path integral over discrete Lorentzian triangulations with a strict causal layer structure.

Key result (arXiv:0807.4481, "The Nonperturbative Quantum de Sitter Universe"): without any
a priori continuum input, the dominant saddle-point geometry in the CDT path integral at
large scales is 4D de Sitter space. The quantum fluctuations around de Sitter are small and
well described by a minisuperspace action.

From arXiv:1007.2560: the de Sitter emergence is **entropic** — it is the entropy maximum
of the space of causal triangulations consistent with the prescribed total spacetime volume.
It is not due to fine-tuning.

**COG implication:** This is the most direct existence proof that a 4D semiclassical universe
with a definite vacuum geometry can emerge purely from Planck-scale discrete causal rules.
The "vacuum" in CDT is the typical triangulation, not a state in a Hilbert space. The parallel
in COG would be the typical large-D limit of the e-e DAG simulation — the emergent macroscopic
geometry of photon exchanges.

**Important caveat:** CDT is Lorentzian but still uses Monte Carlo (computational) sampling
of a Euclidean-Wick-rotated action. The CDT vacuum "fluctuations" are Monte Carlo fluctuations
used to sample the path integral, NOT physical fluctuations happening in real time. This
distinction is often obscured in popular presentations.

---

## 5. Loop Quantum Gravity: The Vacuum Is an Open Problem

LQG (Rovelli, Ashtekar, Lewandowski, Thiemann) is the discrete-geometry approach with the
most extensive mathematical machinery, but it has a fundamental unsolved problem: there is no
agreed-upon physical vacuum.

The kinematical Ashtekar-Lewandowski (AL) vacuum is the state of "no geometry" (zero area on
all surfaces). It is the algebraic ground state of the discrete quantum geometry algebra but
is not the physical vacuum (which would require solving the Hamiltonian constraint — the
central unsolved problem of LQG).

Several constructions have been proposed:
- **Conrady free vacuum** (arXiv:gr-qc/0409036): Linearize gravity around a flat torus; map
  the Fock vacuum into LQG kinematic Hilbert space as a Gaussian over spin networks.
- **Dittrich-Geiller BF vacuum** (arXiv:1401.6441): A vacuum dual to the AL vacuum, based
  on BF theory, closer to the semiclassical limit. Now the basis of the "spin foam" program.

**Warning for COG:** The distinction between kinematical vacuum (no geometry) and physical
vacuum (satisfies all constraints) is a potential pitfall. The COG project must distinguish
between the "initial graph state" (analogous to the AL vacuum: no vacuum nodes spawned yet)
and the "physical vacuum" (the long-time attractor of the DAG simulation). These are
not the same thing.

---

## 6. Non-Commutative Geometry: Vacuum Fluctuations as Inner Automorphisms

Connes' NCG approach constructs the Standard Model from a spectral triple (A, H, D).
The central result (Connes arXiv:hep-th/9603053): **the gauge bosons of the SM are inner
fluctuations of the Dirac operator D**:

```
D  →  D + A + JAJ⁻¹
```

where A is a self-adjoint element of the algebra A (a "connection" in the algebraic sense).
The inner fluctuations encode the gauge fields. The vacuum is the minimum of the spectral
action Tr[f(D/Λ)].

**This is the structurally closest existing framework to COG:** the gauge interactions are
algebraic operators (inner automorphisms of A), not path-integral fluctuations. The Higgs
field and all gauge bosons emerge from the internal geometry of the spectral triple, not
from a quantized background field.

Boyle and Farnsworth (arXiv:1401.5083) show that extending NCG from non-commutative to
**non-associative geometry** eliminates 7 unwanted action terms that previously had to be
removed by hand. This is a significant result: non-associativity is a feature, not a bug,
in the algebraic description of the SM.

**COG implication:** The COG framework's e₇ operator acting on states corresponds to an
inner automorphism in the NCG sense — an algebraic map on the state space rather than a
particle trajectory. The vacuum (ω = 0.5·e₀ + 0.5i·e₇) is the fixed point of this map
up to phase, just as the NCG vacuum is the minimum of Tr[f(D/Λ)]. The parallel is precise.

---

## 7. Division Algebra Approaches: The Vacuum as a Primitive Idempotent

In the Furey/Dixon/Todorov programme for the SM from C⊗O (or T = R⊗C⊗H⊗O), the vacuum
is a **primitive idempotent** in the Witt basis:

```
ω = α†α  (in Furey's Witt-basis notation)
```

where α†, α are creation/annihilation operators built from the complex octonion generators.
Key facts:

- ω² = ω (idempotent)
- All lowering operators annihilate ω (Fock vacuum condition)
- Particle states = (C⊗O)·ω (minimal left ideal generated by ω)
- SM gauge group = stabilizer of ω in Aut(C⊗O)

Furey (arXiv:1611.09182): one generation of quarks and leptons under su(3)_c ⊕ u(1)_em
sits in this minimal left ideal.

Todorov (arXiv:2206.06912) sharpens this: **the SM gauge group G_SM is the subgroup of the
Pati-Salam group G_PS = Spin(4)×Spin(6)/Z₂ that preserves the vacuum idempotent** (the
sterile neutrino direction). This is an exact algebraic statement: G_SM = Stab(ω).

Finster et al. (arXiv:2403.00360, "Causal Fermion Systems and Octonions"): "Octonions and
tensor products of division algebras come up naturally to describe the **symmetries of the
vacuum configuration** of a causal fermion system." Causal fermion systems provide octonionic
theories with spacetime structures and dynamical equations via a **causal action principle**.

**On vacuum fluctuations:** None of Furey, Dixon, or Todorov discuss vacuum fluctuations.
The vacuum in this framework is a structurally inert algebraic element. It does not fluctuate;
it does not generate virtual particles; it simply defines which states are "particles" by
specifying the minimal left ideal. **This is the correct COG treatment of the vacuum.**

### The Furey Vacuum in COG

The COG vacuum state ω = 0.5·e₀ + 0.5i·e₇ is **exactly Furey's primitive idempotent**:

- In Witt-basis notation: ω = ½(e₀ + i·e₇) with e₇ = VACUUM_AXIS.
- ω² = ω (verified: see `calc/test_qed_ee_sim.py::TestAxiomOfIdentity`).
- L_{e₇}·ω = −i·ω (phase shift, RFC-013 §5.1): the e₇ operator rotates ω in the orbit
  {ω, −iω, −ω, +iω}, but it does not destroy ω. The orbit is closed and periodic.
- Electron state e₁ is NOT in this orbit (it is in the minimal left ideal generated by ω).

The SPAWN mechanism in RFC-013 is the causal-DAG analog of Furey's idempotent selection:
when a photon (e₇ operator) first arrives at an unoccupied position, it instantiates the
vacuum as ω at that position. This is not "creating something from nothing" — it is the
algebraic statement that wherever a U(1)_EM operator acts, it finds a vacuum idempotent on
which to act.

---

## 8. 't Hooft's Cellular Automaton Interpretation

't Hooft (arXiv:quant-ph/0212095, "Determinism beneath Quantum Mechanics") is the most
important paper for understanding the difficulty of COG's programme:

> "What is difficult however is to obtain a Hamiltonian that is bounded from below, and whose
> **ground state is a vacuum that exhibits complicated vacuum fluctuations, as in the real
> world**. Beneath Quantum Mechanics, there may be a deterministic theory with (local)
> information loss. This may lead to a sufficiently complex vacuum state."

This is the honest statement of the hard problem. 't Hooft's own solution relies on
**information loss** at the Planck scale — when ontological (deterministic) states undergo
irreversible information loss, the coarse-grained effective description requires a quantum
Hilbert space with nontrivial vacuum statistics.

Blasone, Jizba, Scardigli (arXiv:0901.3907) show that Born's rule emerges naturally from
't Hooft's programme without being postulated — the vacuum statistics follow from the
coarse-graining of the deterministic substrate.

**COG implication:** 't Hooft explicitly warns that generating a vacuum with the right
complexity is the hard, unsolved problem of deterministic QM. The COG project's computational
drag / mass-as-frequency interpretation is structurally analogous to 't Hooft's information
loss mechanism — both treat the effective quantum statistics as emerging from a deterministic
substrate's inability to be tracked exactly at the sub-Planck level. But this analogy must
be developed rigorously, not assumed.

---

## 9. Virtual Particles and the Casimir Effect: Are They Real?

The Casimir effect is the most common argument for the "physical reality" of vacuum
fluctuations. The literature shows this argument is much weaker than usually presented.

**Nikolic (arXiv:1702.03291):** "Zero-point energy is generally unphysical as an absolute
quantity... Casimir force is best viewed as a manifestation of van der Waals forces." The
Casimir force is a retarded van der Waals force between the plates' constituent charges; it
does not require a literal photon sea between the plates.

This is the **Jaffe thesis** (Jaffe, Phys. Rev. D 72, 2005 — not on arXiv as a standalone
paper, but widely cited): "The Casimir effect gives no more evidence for the reality of
vacuum energy than the van der Waals force does."

Suppes, Sant'Anna, de Barros (arXiv:quant-ph/9510010): the Casimir force can be derived using
a **finite, discrete set of real photons** — no infinite vacuum energy required.

Hsiang and Hu (arXiv:1910.11527): the partition between "vacuum fluctuations" and "radiation
reaction" contributions to atom-field interactions is **not gauge-invariant** — it changes
under different operator orderings. This confirms that "vacuum fluctuations" are a formalism-
dependent description, not an observable.

Cortes-Smolin (arXiv:1308.2206, "Energetic Causal Sets"): "fundamentally there are no
commutation relations, no uncertainty principle and, indeed, no ℏ. All that remains of quantum
theory is the relationship between the absolute value squared of complex amplitudes and
probabilities." If ℏ is emergent, virtual particles — defined via ΔE·Δt ~ ℏ — cannot be
fundamental.

**COG implication:** The Casimir effect does not require virtual particles. In the COG
framework, the analog of the Casimir force would be a modification of the photon propagator
spectrum (the set of allowed periodic orbits in the causal DAG) when boundary conditions are
imposed by a conductor. This is purely kinematic — a change in the set of allowed causal paths,
not a change in vacuum particle content.

---

## 10. Critical Evaluation of the Gemini Analysis

The Gemini suggestions contain several correct observations and several claims that require
qualification.

### Correct

- "The vacuum is strictly the causal shadow of matter interactions" — consistent with SPAWN
  and with the SJ vacuum being constructed from G_ret (the retarded propagator of the matter
  field). ✓

- "You do not need to write a simulate_vacuum_fluctuations() function" — correct, and
  consistent with all the literature surveyed here. ✓

- "Do not introduce random number generators, probabilities, or spontaneous node generation" —
  correct in the sense that the vacuum on a FIXED DAG is deterministic (SJ vacuum, Furey
  idempotent). ✓

- "Virtual particles... must be a deterministic, algebraic necessity forced by the graph's
  conflict resolver" — the correct spirit, though the mechanism is better described as
  algebraic deformation (pAQFT) rather than edge-splitting. ✓

### Requires Qualification

- **"e₇ → e₁ × −e₁ → e₇" as a vacuum fluctuation** — this is speculative and not grounded
  in existing literature. The Furey programme does not describe the vacuum as temporarily
  "unzipping" into fermions. The minimal left ideal structure is static: e₁ and ω are in
  different algebraic sectors (matter vs. vacuum), and their interconversion requires a
  specific coupling term in the algebra. This mechanism should NOT be added to the simulation
  without a formal derivation from first principles. The correct framework for interacting
  theories on the COG DAG is pAQFT (§3.4), not ad hoc edge-splitting rules.

- **"Uncertainty is a macroscopic illusion"** — 't Hooft (quant-ph/0212095) explicitly warns
  that generating a vacuum with the right complexity to reproduce quantum statistics is the
  UNSOLVED problem of his programme. Asserting that ℏ is an illusion does not automatically
  produce the correct physics; it must be derived, not assumed.

- **"A vacuum fluctuation is just a closed algebraic loop in the DAG"** — this is an
  interesting conjecture but has no direct support in the literature as stated. Closed loops
  in causal DAGs (causal cycles) are typically FORBIDDEN by the acyclicity constraint of a
  DAG. If vacuum fluctuations correspond to closed loops, they would violate the DAG
  structure. The correct statement, following Sorkin, is that interacting corrections to the
  vacuum are algebraic maps on the observable algebra, not additional causal edges.

### Missing from Gemini's Analysis

- The SJ vacuum construction (§3.1) — the most relevant existing formalism.
- The non-Hadamard property of the SJ state (§3.1) — critical for understanding UV structure.
- The cosmological constant prediction from discreteness (§3.3) — strongest quantitative
  support for the COG approach.
- 't Hooft's honest warning about the hardness of getting a non-trivial vacuum (§8).
- The Casimir/van der Waals equivalence (§9) — eliminates the strongest empirical argument
  for physical vacuum fluctuations.

---

## 11. Recommended Architecture for COG Vacuum Handling

Based on this review, the following decisions are recommended:

### What the vacuum IS in COG

The vacuum at position p is the primitive idempotent ω = 0.5·e₀ + 0.5i·e₇ in the
C⊗O algebra. It is instantiated at p when the first causal edge (photon) reaches p (SPAWN).
It evolves deterministically under left-multiplication by e₇:

```
L_{e₇} : ω ↦ −iω ↦ −ω ↦ +iω ↦ ω   (period 4)
```

This is already implemented in RFC-013 / calc/qed_dag_sim.py. No changes needed here.

### What vacuum fluctuations ARE NOT in COG

- NOT stochastic noise added to ω.
- NOT spontaneous node generation without a causal trigger.
- NOT virtual particle-antiparticle pairs "popping in and out."
- NOT e₇ → e₁ × (−e₁) edge-splitting (not yet derived from first principles).

### What vacuum "fluctuations" MIGHT BE in COG (open problems)

These are conjectures that require formal derivation before implementation:

1. **Second-order corrections to the two-point function** — following the pAQFT approach
   of Dable-Heath et al. (arXiv:1908.01973), the first interaction correction to the
   vacuum propagator would be an algebraic deformation of the SJ state on the COG DAG.
   This is the COG analog of vacuum polarization.

2. **Loop corrections as closed causal paths** — in a general graph (not a strict DAG),
   closed causal paths could contribute to the vacuum energy. In the strict DAG architecture
   of RFC-013, such paths are forbidden. If vacuum corrections are needed, they would
   require a relaxation of the strict DAG constraint (a RESEARCH QUESTION, not a coding task).

3. **SJ vacuum on the COG DAG** — implementing the full SJ construction
   (W = Pos(iΔ) where Δ = G_ret − G_adv) on the COG DAG would give the first rigorous
   quantum vacuum state for the COG theory. This is a substantial research project.
   Johnston's PhD thesis (arXiv:1010.5514) is the primary reference.

### Prime Directive Update for the Codebase

Supplement the existing Prime Directive with:

> **Vacuum Handling (mandatory):**
> 1. Vacuum nodes are ONLY created via the SPAWN protocol (RFC-013 §6.1): first photon
>    arrival at an unoccupied position. No spontaneous vacuum node generation.
> 2. Vacuum node states evolve deterministically under left-multiplication by E7. No random
>    perturbations to vacuum states.
> 3. The COG vacuum is the Furey primitive idempotent ω; it is algebraically inert except
>    for the deterministic phase rotation under L_{e₇}. It does not "fluctuate."
> 4. Interactions (beyond photon relay) are NOT yet implemented. When they are, use the
>    pAQFT framework (algebraic deformation of the SJ state), not ad hoc edge-splitting.
> 5. The Casimir effect and vacuum energy are NOT modeled by virtual particles. They are
>    boundary-condition effects on the discrete propagator spectrum.

---

## 12. Key Papers at a Glance

| arXiv ID | Authors | Relevance to COG |
|----------|---------|-----------------|
| 1107.0698 | Sorkin | SJ vacuum construction from G_ret alone; no Cauchy surface needed. |
| 1703.00610 | Sorkin | From Green function to quantum field; unique vacuum proof. |
| 1010.5514 | Johnston | Causal set Feynman propagator; non-perturbative S-matrix. |
| 1908.01973 | Dable-Heath et al. | pAQFT on causal sets: interactions without virtual particles. |
| 2306.04800 | Nomaan X | QFT on causal sets: comprehensive review of SJ formalism. |
| gr-qc/9904062 | Rideout-Sorkin | Classical sequential growth dynamics; stochastic at growth level, not vacuum level. |
| 0710.1675 | Sorkin | Cosmological constant from causal set discreteness: Λ ~ 1/√N. |
| 2212.10592 | Zhu-Yazdi | SJ state is non-Hadamard: UV structure differs from continuum QFT. |
| 0807.4481 | Ambjorn et al. | CDT: 4D de Sitter emerges from discrete Lorentzian triangulations. |
| 1007.2560 | Ambjorn et al. | CDT vacuum is entropic (entropy maximum of causal triangulations). |
| 1401.6441 | Dittrich-Geiller | New LQG vacuum from BF theory; kinematical vs. physical vacuum distinction. |
| hep-th/9603053 | Connes | NCG: SM gauge bosons = inner fluctuations of Dirac operator. |
| 1401.5083 | Boyle-Farnsworth | Non-associative NCG eliminates unwanted action terms. |
| 1611.09182 | Furey | C⊗O vacuum = primitive idempotent; SM generation in minimal left ideal. |
| 2403.00360 | Finster et al. | Causal fermion systems + octonions: vacuum symmetries from division algebras. |
| 2206.06912 | Todorov | G_SM = stabilizer of vacuum idempotent (sterile neutrino direction). |
| quant-ph/0212095 | 't Hooft | Deterministic QM: getting a complex vacuum is the HARD problem. |
| 1308.2206 | Cortes-Smolin | Energetic causal sets: no ℏ at fundamental level; virtual particles dissolve. |
| 1702.03291 | Nikolic | Zero-point energy is unphysical; Casimir = van der Waals force. |
| 1910.11527 | Hsiang-Hu | "Vacuum fluctuations" are operator-ordering artifacts, not observables. |

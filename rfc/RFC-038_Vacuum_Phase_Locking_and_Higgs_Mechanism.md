# RFC-038: Vacuum Phase-Locking, Spontaneous Symmetry Breaking, and the COG Higgs Mechanism

Status: Active — Hypothesis and Architecture Draft (2026-02-26)
Depends on:
- `rfc/RFC-019_e7_Temporal_Axis_Vacuum_Photon_Duality.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-029_Weinberg_Angle_Gap_Closure.md`
- `rfc/RFC-037_Weinberg_Derivation_Avenues_and_Gates.md`
- `CausalGraphTheory/VacuumStabilizerAction.lean`
- `CausalGraphTheory/WeakMixingObservable.lean`

---

## 1. Executive Summary

The temporal commit `T(psi) = e7 * psi` has exact period 4 for all nonzero states (proved in
`Spinors.lean`). The vacuum state `omega = 1/2 (e0 + i*e7)` visits a four-element orbit
`{omega, -i*omega, -omega, i*omega}` under iterated application of `T` (RFC-019).

This RFC proposes that these facts, taken together with the superdetermined initial conditions of
the COG causal graph, yield a complete first-principles mechanism for:

1. **Vacuum variation** — the vacuum is a source of four distinct interaction types, not a
   static background. This variation is apparent from the perspective of a matter node but
   fully determined by the initial causal graph topology (superdeterminist resolution).

2. **Spontaneous symmetry breaking** — the Higgs mechanism corresponds to the vacuum phase
   crystallizing at a specific point in its four-element orbit. Before locking the vacuum
   cycles freely (symmetric phase). After locking it freezes to a single state (broken phase).

3. **Mass generation** — fields that couple to the EW sector experience a fixed-phase locked
   vacuum. Any field whose dynamics do not commute with the locked phase acquires a COG
   mass penalty (analogous to the SM statement that fields acquiring mass are those that
   do not preserve the Higgs VEV direction).

4. **The massless photon** — the photon is the unique linear combination of the U(1)_Y and
   SU(2)_L sector operators that is invariant under the locked vacuum phase. This
   combination is fixed by the Fano algebra, yielding `sin^2(theta_W) = 1/4` at the
   UV lattice scale (already Lean-proved in `WeakMixingObservable.lean`).

5. **Running from differential associator load** — the gap from 1/4 to the measured 0.231
   at M_Z is produced by the differential associator load on the SU(2) channel vs. the
   U(1) channel as amplitude propagates through the full C x O algebra (Avenue 13,
   RFC-037). This is a parameter-free computation from the Fano structure constants.

6. **Canonical parenthesization from superdetermined initial conditions** — the
   non-associativity of C x O requires a bracket ordering for compound operations. In COG
   this ordering is not a free choice: it is a topological invariant of the initial causal
   graph, fixed by the initial conditions. The `interactionFold` of RFC-028 encodes this
   canonical ordering.

---

## 2. Literature Synthesis

### 2.1 External derivations of sin^2(theta_W) = 1/4 as a UV boundary condition

The value 1/4 appears as an independent UV prediction in two bodies of work unrelated to
the Fano plane:

- **Ellis, Hung, Mavromatos (2020)** [arXiv:2008.00464]: Derives `sin^2(theta_W) = 1/4`
  at the electroweak monopole mass scale as a direct consequence of Dirac quantization
  applied to an SU(2) electroweak monopole. Standard Model RG running from the monopole
  mass down to M_Z then yields the measured 0.231. This is the most directly parallel
  external result: a UV algebraic constraint forces 1/4, and RG running closes the gap.
  COG's Fano vacuum structure plays the role of the monopole's topological constraint.

- **Hasegawa, Lim, Maru (2015)** [arXiv:1509.04818]: In 6-dimensional gauge-Higgs
  unification (GHU), the triplet/sextet representations of SU(3) force `sin^2(theta_W) = 1/4`
  at the GHU compactification scale, together with the prediction M_H = 2M_W at leading
  order. The 6-dimensional internal space in GHU is structurally analogous to the 7-point
  Fano plane plus vacuum axis in COG (both are compact discrete-to-continuous limits of
  the same symmetry structure).

These two independent derivations provide external convergent evidence that 1/4 is a
physically well-motivated UV boundary. They do not validate the COG mechanism, but they
remove the concern that 1/4 is an arbitrary coincidence.

### 2.2 Algebraic spontaneous symmetry breaking

- **Furey and Hughes (2022)** [arXiv:2210.10126]: Demonstrates that a complete SSB
  cascade Spin(10) -> Pati-Salam -> Left-Right -> SM+B-L is driven purely by a sequence
  of complex structures derived from the octonions, then quaternions, then complex numbers
  in the R x C x H x O tower. The Higgs doublet emerges algebraically from the
  quaternionic triality structure tri(H). This is the closest existing mechanism to RFC-038's
  claim that the Higgs VEV direction is selected by the algebraic structure of C x O rather
  than by a scalar potential. The Furey-Hughes cascade does not fix sin^2(theta_W), but it
  establishes that the same algebraic tower can drive SSB without an external potential.

- **Volovik (2024)** [arXiv:2406.00718]: In a quantum gravity scenario where the
  gravitational tetrad emerges as the VEV of a fermion bilinear, the system carries a
  discrete Z4 symmetry `e^a_mu -> i * e^a_mu`. Spontaneous breaking of this Z4 to Z2
  (corresponding to the EM residual symmetry) produces domain walls and contributes to
  baryon asymmetry. The structural identity with COG is near-complete: the octonion
  vacuum state `omega = 1/2(e0 + i*e7)` plays the role of the gravitational tetrad VEV,
  and its Z4 orbit `{omega, -i*omega, -omega, i*omega}` maps to Volovik's discrete Z4
  phase. Breaking Z4 -> Z1 in COG corresponds to the vacuum phase-locking to `omega`.

### 2.3 Non-associative algebra and differential RG running

- **Flodgren and Sundborg (2023)** [arXiv:2303.13884, arXiv:2311.05993]: Proves that the
  one-loop RG flow of adjoint multi-scalar gauge theories is governed by a non-associative
  algebra of marginal couplings. Idempotents and Peirce numbers of this algebra characterize
  RG fixed points. The gauge coupling beta function vanishes at specific matter content
  (M = 22 adjoints). Sectors residing in associative sub-algebras of the coupling algebra
  have qualitatively different beta functions from sectors in the non-associative complement.
  This is external proof of concept for Avenue 13: in COG, the EW sector sits in the
  quaternionic (associative) sub-algebra of C x O, while the color sector sits in the
  non-associative complement, producing exactly the differential beta function structure
  that drives Weinberg angle running.

- **Flodgren and Sundborg (2023)** [arXiv:2312.04954]: Extends the above, showing that
  RG fixed-point structure and Kowalevski exponents can be read off directly from the
  algebraic (idempotent) structure of the non-associative coupling algebra. For COG, this
  means the IR fixed point of sin^2(theta_W) — the value toward which the curve runs —
  is in principle computable from the idempotent structure of the Fano algebra alone,
  without iterating the curve.

### 2.4 Associator as obstruction in octonionic gauge theories

- **Waldron and Joshi (1992)** [arXiv:hep-th/9211123]: The canonical result showing that
  non-associativity forces extra terms in the gauge-covariant derivative when gauging the
  octonion algebra. The associator `[A,A,A]` appears explicitly in the kinetic Lagrangian
  and field transformation laws. In COG, these extra terms are the "Fano penalty" — the
  computational cost per alternation step that is non-zero only for the non-associative
  (color-sector-coupled) interactions.

- **Ootsuka, Tanaka, Loginov (2005)** [arXiv:hep-th/0512349]: Constructs a gauge theory
  based on the Moufang loop (unit octonions S^7) rather than a Lie group. The associator
  `[A,A,A]` appears as an obstruction in the Bianchi identity — directly analogous to
  COG's Fano triple producing a non-zero associator load when two of the three elements
  are from different sectors (EW and color).

### 2.5 Superdeterminism and causal ordering

- **Hossenfelder and Palmer (2019)** [arXiv:1912.06462]; **Hossenfelder (2020)**
  [arXiv:2010.01324]: The standard reference pair for superdeterminism as a consistent
  local deterministic description of quantum correlations. Relevant here for Section 7:
  the canonical parenthesization of C x O operations in COG is precisely the type of
  "hidden variable correlated with initial conditions" that the superdeterminist program
  studies. The key requirement from Hossenfelder — a measure on initial data that is
  not product-separable across the causal past — is automatically satisfied in COG by the
  non-associativity: the result of a sequence of octonionic operations depends on the full
  causal history, not on a product of independent local decisions.

### 2.6 What the literature does not yet provide

No existing paper:
- Derives sin^2(theta_W) = 1/4 from the Fano plane geometry or the octonion vacuum axis
  specifically.
- Connects the associator load of Fano triples (Section 6.2) to Weinberg angle running.
- Proves that Z4 vacuum phase-locking of the form proposed here produces the correct photon
  as the invariant combination.

The Furey program (1806.00612, 2209.13016, 1910.08395) establishes the SM gauge group
structure from C x O but does not fix coupling constant ratios. This RFC proposes the
mechanism that would complete the coupling constant prediction within the Furey framework.

---

## 3. The Vacuum Four-Cycle

### 2.1 Established facts (already proved)

From `Spinors.lean`:
- `universal_Ce_period_four`: left-multiplication by `e7` has period exactly 4 for
  all nonzero states.
- `universal_Ce_right_period_four`: same for right-multiplication.

The vacuum orbit under `T = L_e7` is:

```
T^0(omega) = omega               = 1/2 (e0 + i*e7)
T^1(omega) = -i*omega            = 1/2 (e7 - i*e0)
T^2(omega) = -omega              = 1/2 (-e0 - i*e7)
T^3(omega) = i*omega             = 1/2 (-e7 + i*e0)
T^4(omega) = omega               (period-4 return)
```

The four states are distinct and form a Z4 orbit.

### 2.2 Vacuum interactions come in four varieties

A matter node at causal depth `n` that receives a vacuum message receives the vacuum state
at phase `T^n(omega)`. The effective content of this message depends on `n mod 4`. From the
matter node's perspective, without knowledge of the global causal depth, these four variants
are indistinguishable prior to interaction — they constitute an apparent Z4 entropy source.

**Superdeterminist resolution:** In COG, the causal graph is fully deterministic and the
initial conditions are superdetermined. The vacuum phase at any causal depth was fixed at
initialization. There is no actual randomness: the apparent four-variety entropy is an
artifact of incomplete knowledge of the global initial state. An observer with full knowledge
of the causal graph topology would know, in advance, which vacuum phase every interaction
encounters.

This is consistent with the COG prime directive (deterministic causal graph) and with
RFC-019 (e7 as temporal axis with dual role: state and operator).

---

## 4. Spontaneous Symmetry Breaking as Vacuum Phase-Locking

### 3.1 The symmetric phase

In the symmetric phase, the vacuum cycles freely through its Z4 orbit. Every interaction
type `{omega, -i*omega, -omega, i*omega}` is equally represented. The system has full Z4
symmetry.

Computationally: in the symmetric phase, the average vacuum state seen by a matter node over
four consecutive steps is zero (the Z4 orbit sums to zero in the C x O algebra). This
corresponds to a vanishing vacuum expectation value.

### 3.2 The broken phase (phase-locking)

Spontaneous symmetry breaking corresponds to the vacuum `freezing` to a specific state in
its orbit — say `omega` — and remaining there rather than cycling. After locking:

- Every vacuum interaction delivers the same state `omega = 1/2(e0 + i*e7)`.
- The average vacuum state is `omega != 0`.
- The Z4 symmetry is broken to the trivial group.

The locked state `omega` singles out the `e0 + i*e7` direction in C x O as the `vacuum
expectation value` direction. This is the COG analog of the Higgs VEV.

### 3.3 What breaks the symmetry

The phase-locking is not imposed by an external potential: it is a consequence of the
superdetermined initial conditions of the causal graph. The initial state of the vacuum nodes
encodes a specific phase, and the dynamics preserve it. The symmetry `appears` to be broken
because the initial conditions selected one point in the orbit. From outside the theory,
this looks spontaneous; from within the superdeterminist framework, it was always going to
be this phase.

**Structural parallel:** Volovik (2024, arXiv:2406.00718) identifies a near-identical
mechanism in quantum gravity: the gravitational tetrad emerges as the VEV of a fermion
bilinear carrying Z4 symmetry `e^a_mu -> i*e^a_mu`. Spontaneous Z4 breaking produces
domain walls and contributes to baryon asymmetry. The COG vacuum orbit Z4 is the same
algebraic object, with `omega` playing the role of the tetrad VEV and the Fano-forced
initial conditions playing the role of the fermion bilinear ground state. The COG
mechanism predicts no domain walls (there is only one causal graph, not a network of
domains) but is otherwise structurally identical. This paper should be cited as
independent evidence for discrete Z4 vacuum selection as a physically viable mechanism.

---

## 5. Mass Generation from Phase Mismatch

### 4.1 The mechanism

A field operator `F` propagating through the causal graph accumulates phase at each
interaction with the locked vacuum. If `F` commutes with the locked vacuum state `omega`
in the C x O sense (i.e., `omega * F * omega^{-1} = F`), then `F` is invariant under the
locking and propagates freely — it is massless.

If `F` does not commute with `omega`, each vacuum interaction introduces a phase mismatch.
Over multiple interactions, this mismatch accumulates as a computational cost — a drag on
free propagation. In COG, computational drag is mass (RFC-018, RFC-034). Therefore:

- **Massless fields:** operators that commute with `omega` in C x O (invariant under the
  locked vacuum phase).
- **Massive fields:** operators that do not commute with `omega` — they acquire mass
  proportional to the phase mismatch per interaction.

### 4.2 The EW sector decomposition

The locked vacuum state `omega = 1/2(e0 + i*e7)` lives in the EW subspace
`{e0, e7, ea, eb}`. This subspace is quaternionic: it is an associative subalgebra of C x O
(the octonion associator vanishes identically within it).

Within the EW subspace, the fields that do not commute with `omega` are those that involve
the `ea` and `eb` weak-pair directions: these are the W boson components. The combination
that `does` commute with `omega` — the one that is invariant under e0-phase rotations — is
the linear combination of the `e7` and `(ea, eb)` sector operators that constitutes the
photon.

The W and Z bosons couple to the EW sector through the weak pair and fail to commute with
the locked vacuum direction. They acquire mass. The photon combination commutes and is
massless.

---

## 6. The Weinberg Angle from Phase-Locking

### 5.1 UV value: sin^2(theta_W) = 1/4

The Weinberg angle is determined by which linear combination of the U(1)_Y sector (`e7`)
and the SU(2)_L sector (`ea, eb`) is invariant under the locked vacuum phase `omega`.

The Lean-proved result in `WeakMixingObservable.lean`:
- `sin2ThetaWObs_exclusive_u1_eq_one_four`: the exclusive-U1 observable equals exactly `1/4`.
- `sin2ThetaWObs_exclusive_u1_stabilizer_invariant`: this value is invariant under all 24
  elements of the vacuum stabilizer (S4 of order 24 = PSL(2,7) stabilizer of e7).

Interpretation in the phase-locking framework:
- The locked vacuum selects `e0` (the scalar/exclusive-U1 direction) as the VEV direction.
- The Weinberg angle = (exclusive U1 support) / (full EW support) = 1 / 4.
- This is the UV lattice-scale value: the tree-level prediction of COG at the COG lattice
  scale, analogous to the SU(5) prediction of 3/8 at the GUT scale.
- **External convergence:** Ellis, Hung and Mavromatos (2020) independently obtain 1/4
  at the electroweak monopole mass scale from Dirac quantization. Hasegawa et al. (2015)
  obtain 1/4 from 6D gauge-Higgs unification constraints. The same boundary value arising
  from three independent mechanisms (Fano vacuum structure, monopole topology, GHU
  compactification) is a non-trivial structural coincidence warranting explanation.

### 5.2 Running: associator-load differential (Avenue 13)

The gap from 1/4 (UV) to 0.231 (M_Z measured value) is produced by the differential
associator load on the two channels as causal depth increases.

Key structural facts that drive the running:

1. The EW subspace `{e0, e7, ea, eb}` is quaternionic and associative. Within it, the
   associator `A(a,b,c) = (a*b)*c - a*(b*c) = 0` identically. There is therefore no
   differential running between U(1) and SU(2) from purely EW interactions alone. The
   Weinberg angle does not run in a theory with only EW fields.

2. The SU(2)_L directions `ea` and `eb` participate in non-EW Fano triples (the 4
   non-vacuum triples that connect the weak pair to the color sector). Each such
   interaction produces a nonzero associator.

3. The U(1)_Y exclusive direction `e0` (the scalar) has zero Fano coupling. It does not
   appear in any Fano triple. Its associator load is identically zero.

4. Therefore: per causal step involving a color-sector element, the SU(2) channel
   accumulates associator load while the U(1) channel does not. This differential
   accumulation is the COG beta function for the Weinberg angle.

The running is:

```
Delta(sin^2(theta_W)) per color-sector step
  = (mixing rate of ea, eb into color) - (mixing rate of e0 into color)
  = (nonzero, from Fano color triples) - 0
  < 0
```

So sin^2(theta_W) monotonically decreases from 1/4 as causal depth increases. The IR
fixed point is reached when the differential associator load is exhausted — this should
correspond to the physical scale M_Z.

**This derivation has no free parameters.** The mixing rates are determined entirely by
the Fano multiplication table (locked in `rfc/CONVENTIONS.md`) and the matter content
forced by the C x O structure (3 Witt pairs = 3 quark colors, 1 vacuum axis = lepton).

**Literature support for the mechanism:** Flodgren and Sundborg (2023) prove that
one-loop RG flows of gauge theories are governed by a non-associative algebra of marginal
couplings, and that sectors in associative sub-algebras of that algebra have qualitatively
different beta functions from sectors in the non-associative complement. In COG, the EW
sector is the quaternionic (associative) sub-algebra and the color sector is the
non-associative complement — the differential beta function structure is therefore
algebraically forced by the same mechanism Flodgren-Sundborg identify, applied to the
Fano algebra specifically. Their framework also implies the IR fixed point of the running
curve is in principle readable from the idempotent structure of the Fano algebra
(arXiv:2312.04954), potentially yielding the target value without iterating the full
depth scan.

### 5.3 Connecting causal depth to physical scale

The number of color-sector causal steps separating the COG UV scale from M_Z is:

```
N_RG = log(M_COG / M_Z) / log(k_gate_step_size)
```

where `M_COG` is the COG lattice scale (derived from RFC-034 electron mass mechanism)
and `k_gate_step_size` is the per-step energy resolution set by the electron's gate
density. If the resulting sin^2(theta_W)(N_RG) matches 0.231, the derivation closes.

---

## 7. Canonical Parenthesization from Superdetermined Initial Conditions

The update rule `psi_{t+1} = T(psi_t) * I_Y(msgs) * I_2(msgs)` involves a compound
C x O product. Because C x O is non-associative, the bracket ordering matters:

```
(A * B) * C  !=  A * (B * C)   in general
```

This is not an ambiguity in COG. The bracket structure is a topological invariant of the
causal graph. The initial causal graph encodes, for every pair of incoming messages at every
node, which message is the causal predecessor of the other. This ordering is the canonical
bracket structure.

**Concretely:** the `interactionFold` defined in RFC-028 gives the canonical left-fold over
incoming messages ordered by causal precedence:

```
fold_left (*) msgs = (...((m_1 * m_2) * m_3) * ... * m_k)
```

where `m_1, m_2, ..., m_k` are ordered by causal depth (earliest first). This ordering was
fixed at the creation of the causal graph — it is an initial condition, not a choice.

The non-associativity of C x O is therefore not a source of ambiguity but a source of
physical content: the precise bracket structure determined by the causal order produces
the specific associator at each step that drives the Weinberg angle running. Different
causal orderings (different initial conditions) would produce different running — and
therefore different physics. The fact that COG has specific physics is a consequence of
having specific initial conditions.

---

## 8. Falsification Gates

**Gate F1: Monotone decrease of sin^2(theta_W)**
Run the alternation-depth scan (see Section 8.1). Starting from the UV state with
sin^2(theta_W) = 1/4, iteratively apply the Fano right-multiplication matrices weighted
by the 3:1 quark/lepton ratio forced by C x O topology. The curve sin^2(theta_W)(N) must
be monotonically non-increasing. If it increases or oscillates without settling, reject
Avenue 13.

**Gate F2: Zero associator load on e0**
Verify computationally that the associator `A(e0, x, y) = 0` for all `x, y` in the C x O
basis. This must hold by the scalar identity `e0 * x = x` — the scalar is the unit element
and cannot contribute nonzero associator. Failure would invalidate the differential running
mechanism.

**Gate F3: Nonzero associator load on ea, eb from color triples**
Verify that `A(ea, ec, ed) != 0` for at least one color-sector pair `(ec, ed)` connected to
`ea` by a non-vacuum Fano triple. Same for `eb`. If these are zero, the SU(2) channel has
no differential load and the Weinberg angle cannot run.

**Gate F4: IR value consistent with 0.231**
At the alternation depth `N_RG` derived from RFC-034 electron mass / COG lattice scale, the
computed sin^2(theta_W)(N_RG) must agree with 0.231 within ±0.005 (2% tolerance). If the
curve does not pass through the target at the correct scale, the mechanism is falsified for
this matter-content assumption.

**Gate F5: Stabilizer invariance of running**
The running curve must be the same regardless of which Witt pair is chosen as the weak pair.
The vacuum stabilizer (S4) acts transitively on the three Witt pairs, so any two choices
must give the same running. Already proved structurally for the UV value; must be
verified dynamically for the running.

**Gate F6: No free parameters**
The entire derivation — from UV value 1/4 to the running curve to the IR value — must use
only:
  - The Fano multiplication table from `rfc/CONVENTIONS.md`
  - The electron gate density from RFC-034
  - The locked `interactionFold` ordering from RFC-028
No attenuation parameters, no steps-and-attenuation bridge policies, no fitted coefficients.
If a parameter is introduced, it must be derived from the above, not fit to 0.231.

---

## 9. Implementation Targets

### 8.1 Python: Alternation depth scan (priority)

File: `calc/weinberg_associator_running.py`

1. Implement the 8x8 right-multiplication matrices `M_sigma` for each of the 7 Fano
   generators, using the locked Fano cycles from `calc/conftest.py`.
2. Starting from UV state: `psi_0 = e0` (exclusive-U1 direction, sin^2(theta_W) = 1/4).
3. At each step, apply a weighted mixture of generators:
   - EW generators (3 vacuum triples involving e7): weight proportional to lepton content (1)
   - Color generators (4 non-vacuum triples): weight proportional to quark content (3)
4. Compute `sin^2(theta_W)(N)` after each step.
5. Output: curve from N=0 (value = 1/4) to N=N_max.
6. Mark the depth `N_0231` where the curve first crosses 0.231.
7. Report whether `N_0231` is consistent with `log(M_COG / M_Z)` from RFC-034.

Required tests:
- `test_sin2_starts_at_one_quarter`: verify N=0 gives 1/4 exactly.
- `test_sin2_monotone_decreasing`: verify no upswings.
- `test_gate_F2_e0_associator_zero`: verify e0 associator identically zero.
- `test_gate_F3_ea_color_associator_nonzero`: verify ea color-triple associator nonzero.

### 8.2 Lean: Associator load theorems

File: `CausalGraphTheory/AssociatorLoad.lean`

Target theorems:
- `e0_associator_zero (x y : OctonionInt) : assoc e0 x y = 0` (from scalar unit property)
- `ea_color_assoc_nonzero : ∃ (x y : OctonionInt), assoc ea x y ≠ 0` (from Fano color triple)
- `u1_exclusive_zero_color_coupling`: the exclusive-U1 direction has no Fano triple
  involving color-sector elements (purely structural counting theorem).

These three theorems prove the asymmetry that drives differential running. They do not
prove the full running curve, but they prove the mechanism is non-trivial.

---

## 10. Relation to Existing Work

| Existing result | Status | Role in this RFC |
|---|---|---|
| `sin2ThetaWRaw = 1/2` | Lean-proved | The symmetric (no-locking) UV baseline |
| `sin2ThetaWObs_exclusive_u1 = 1/4` | Lean-proved | The locked-vacuum UV prediction |
| Stabilizer invariance of 1/4 | Lean-proved | Confirms locking is canonical, not arbitrary |
| RFC-028 `interactionFold` | Locked | Supplies the canonical parenthesization |
| RFC-019 vacuum orbit `{omega, -i*omega, ...}` | Active hypothesis | Supplies the four-variety mechanism |
| RFC-034 electron mass / k_gate | Complete simulation | Supplies `M_COG` for scale calibration |
| RFC-037 Avenue 13 | Listed, not implemented | This RFC is the implementation plan for it |
| Ellis, Hung, Mavromatos 2020 | External literature | Independent derivation of 1/4 as UV boundary via monopole Dirac quantization + SM RG running to 0.231 |
| Furey, Hughes 2022 | External literature | SSB cascade from algebraic complex structures in R x C x H x O (no potential required) |
| Flodgren, Sundborg 2023 | External literature | Non-associative coupling algebras drive differential RG; EW/color split matches COG sector structure |
| Volovik 2024 | External literature | Z4 vacuum phase-locking from fermion bilinear VEV — near-identical mechanism in quantum gravity |

The H1 discrete bridge policies (`calc/weinberg_h1_bridge_policies.json`) are superseded
by this RFC as the mechanism for gap closure. They are retained as archived baselines but
should not be extended or tuned.

---

## 11. Non-Goals

This RFC does not claim:

1. A derivation of the Higgs boson mass.
2. A derivation of the Higgs quartic self-coupling.
3. Proof that the vacuum `must` phase-lock (this requires a stability argument beyond
   the current framework).
4. That 0.231 will be derived exactly (the gate is ±0.005 = 2% tolerance).
5. A full connection to the continuum SM electroweak Lagrangian.

---

## 12. Validation Checklist

- [ ] `calc/weinberg_associator_running.py` produces a curve starting at 1/4 (Gate F1).
- [ ] `test_gate_F2_e0_associator_zero` passes.
- [ ] `test_gate_F3_ea_color_associator_nonzero` passes.
- [ ] Curve crosses 0.231 at a depth consistent with RFC-034 scale (Gate F4).
- [ ] Witt-pair independence of running curve verified (Gate F5).
- [ ] No free parameters introduced (Gate F6).
- [ ] `AssociatorLoad.lean` theorems compile without `sorry`.
- [ ] `claims/weinberg_angle.yml` updated to reference this RFC as the running mechanism.

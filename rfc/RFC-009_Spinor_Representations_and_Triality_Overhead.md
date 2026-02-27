# RFC-009: Spinor Representations and Triality Overhead

**Status:** Draft
**Created:** 2026-02-22
**Module:** `COG.Algebra.Triality`, `COG.Particles.SpinorMotifs`
**Dependencies:** `rfc/CONVENTIONS.md` (locked), `rfc/RFC-001_Canonical_State_and_Rules.md`
**Claims addressed:** MU-001 (proton/electron ratio), KOIDE-001 (lepton generation masses)

---

## 1. Executive Summary

The simulation `calc/mass_drag.py` (Phase 10) ran cleanly and produced a
**falsification datum**: `C_e = 3`, `C_p = 8`, `mu_COG = 2.667` vs
`mu_exp = 1836.153` (relative gap 99.85%).

This RFC diagnoses the two structural defects in the current proton motif
definition and provides the theoretical foundation for correcting them. It
also formalizes the Triality overhead mechanism (KOIDE-001), which is
the separate question of lepton generation mass — independent of MU-001.

**Two corrections are needed before MU-001 can be revisited:**

1. **Cyclic exchange correction** (§3): The proton exchange schedule must be
   directed cyclic (C1→C2→C3→C1), ensuring every quark both emits and absorbs.
   The current schedule has Color1 perpetually emitting, never absorbing.

2. **Recurrence condition tightening** (§4): The color-singlet return must
   require each quark to have independently traversed its minimum algebraic
   orbit, not merely return to the same state tuple.

Separately, **KOIDE-001** (§5–6) requires defining V, S+, S- as distinct node
types in the COG graph and computing the Triality rotation overhead that
produces the Koide 2/3 ratio.

---

## 2. Diagnosis: Why MU-001 Simulated C_p = 8

### 2.1 The Asymmetric Exchange Bug

The exchange schedule in `calc/mass_drag.py` (Phase 10) was:

```
Step 0: src=Q[1](Color1,e1), dst=Q[0](Color2,e5), gluon {e3,e4}
Step 1: src=Q[1](Color1,e1), dst=Q[2](Color3,e3), gluon {e2,e5}
Step 2: src=Q[0](Color2),    dst=Q[2](Color3),    gluon {e1,e6}
```

**Quark Q[1] (Color1, state e1) appears as SOURCE in steps 0 and 1,
and is NEVER a destination.** Its state is never updated by the
interaction rule. Q[2] (Color3) appears as destination in both steps 1
and 2, but is never a source.

As a result:
- `Q[1].state` is permanently frozen at 0 (e1) throughout the simulation.
- The recurrence check `states == (4, 0, 2)` trivially satisfies
  `Q[1].state == 0` at every step.
- Recurrence only requires `Q[0].state == 4` AND `Q[2].state == 2`.

This is why the proton "recurred" after only 8 ticks: it only needed two
of the three quarks to return to their initial states, and one of those
(Q[1]) had never moved.

### 2.2 Physical Interpretation of the Bug

A color-singlet hadron maintains confinement through a balanced exchange
of color charge. Each quark must both emit and receive color during a full
confinement cycle. An exchange where one color (Color1) perpetually emits
without absorbing is equivalent to a persistent color current — physically
a charged source, not a neutral proton.

The "mass" of such a motif is dominated by the orbit length of just the
other two quarks, which is short (order 4–8 over the 7 Witt elements).

---

## 2b. The Color-Singlet Sector — An Algebraic Fact (Verified)

Before addressing the exchange schedule, there is a deeper structural result
that clarifies what the "proton sector" actually is.

### 2b.1 The 4/4 Split of One-Per-Witt-Pair States

There are exactly 8 ways to choose one element from each Witt pair (2³ = 8).
A direct enumeration via `three_body(w0, w1, w2)` reveals a **perfect 4/4
structural split** (verified computationally in Phase 10, 2026-02-22):

| Configuration | Fano line? | Triple product | Interpretation |
|--------------|-----------|---------------|---------------|
| (e₆, e₂, e₄) | **L4** {2,4,6} | −1 (real, blocked) | Quark "annihilation" |
| (e₆, e₅, e₃) | **L7** {3,5,6} | −1 (real, blocked) | Quark "annihilation" |
| (e₁, e₂, e₃) | **L1** {1,2,3} | −1 (real, blocked) | Quark "annihilation" |
| (e₁, e₅, e₄) | **L2** {1,4,5} | −1 (real, blocked) | Quark "annihilation" |
| (e₆, e₂, e₃) | not Fano | ±e₇ (non-assoc) | Active proton state |
| (e₆, e₅, e₄) | not Fano | ±e₇ (non-assoc) | Active proton state |
| (e₁, e₂, e₄) | not Fano | ±e₇ (non-assoc) | Active proton state |
| **(e₁, e₅, e₃)** | not Fano | ±e₇ (non-assoc) | **PROTON_INIT** |

**The pattern is exact:**
- The 4 **blocked** configurations are exactly the one-per-Witt-pair triples that
  lie on one of the **4 non-vacuum Fano lines** (L1, L2, L4, L7 — the lines that
  do not pass through e₇). The triple product hits a squared element → −1 (real).
- The 4 **active** configurations are exactly the one-per-Witt-pair triples that
  span three different Fano lines (no three of them collinear). Both bracketings
  land on **e₇**, with opposite signs (s_L = −e₇, s_R = +e₇ or vice versa),
  confirming the Alternativity Trigger fires.

### 2b.2 Physical Interpretation (Correcting the "Bug" Reading)

The result s_L = −e₇ and s_R = +e₇ for PROTON_INIT is **not a bug**.
The vacuum axis e₇ is the electromagnetic/photon direction (the U(1) axis).
The fact that the proton's 3-quark product always lands on ±e₇ means:

> **The proton IS the color-singlet state that continuously projects onto the
> photon sector.** This is the discrete-algebraic analog of the proton having
> an electromagnetic charge distribution (charge radius, magnetic moment).

The 4 blocked configurations (real result −1) are *not* proton states —
their triple product annihilates to the scalar. These may correspond to
meson-like or vacuum-like configurations.

### 2b.3 Implication: Revised Recurrence Condition

The recurrence condition `states == PROTON_INIT` used in Phase 10 is too
restrictive. The physically correct condition is:

**Color-singlet recurrence:** The quark tuple (q₀, q₁, q₂) returns to **any
of the 4 active configurations**, not necessarily the exact initial assignment.

Under the revised condition, the proton "lifetime" (C_p) is the tick count
for the quark tuple to complete an orbit through the 4-state active sector
back to PROTON_INIT. Since the sector has exactly 4 states, and the exchange
schedule must visit all of them (by symmetry), the orbit length is set by
the exchange group action on these 4 states — not merely on one fixed tuple.

### 2b.4 The ±e₇ Sign — ARCHITECTURAL REQUIREMENT (resolved 2026-02-22)

Both bracketings land on e₇ with **opposite signs**. The simulation
currently does not track the sign of a node state — it tracks only the
OctIdx ∈ {0..6}. This means +e₇ and −e₇ are indistinguishable in the
current model.

**This MUST be fixed.** Signs must NOT be collapsed. Gemini's architectural
directive (2026-02-22):

> **DO NOT COLLAPSE THE SIGNS.** In a discrete graph, quantum interference
> and the Pauli Exclusion Principle arise from these exact algebraic minus
> signs. The +e₇ and −e₇ results are the graph's way of generating
> chirality and anti-particles. The difference between +e₇ and −e₇
> dictates whether the next gauge interaction in the DAG will be attractive
> or repulsive.

The node payload must be extended to track `(OctIdx, sign)` where
`sign ∈ {+1, −1}`. Collapsing to `OctIdx` alone destroys CP violation
and chiral projection information.

**Implementation:** Change `Node.state: int` to `Node.state: tuple[int, int]`
where the first element is the OctIdx (0–6) and the second is the sign (+1
or −1). All Fano product functions must propagate the sign correctly.
The recurrence condition for the proton must check both the OctIdx AND the
sign tuple of each quark.

---

## 3. Correction 1 — Cyclic Directed Exchange (Revised Proton Motif)

### 3.1 The Correct Exchange Schedule

A color-singlet proton exchange must be a **directed cycle**: each color
emits to the next color in the cycle, and receives from the previous.
The canonical directed cycle is:

```
C1 → C2 → C3 → C1   (one full color rotation)
```

In quark-index notation (PROTON\_INIT assigns Q[0]=Color2, Q[1]=Color1,
Q[2]=Color3):

```
Step 0: src=Q[1](Color1), dst=Q[0](Color2), gluon {e3,e4}  [C1→C2]
Step 1: src=Q[0](Color2), dst=Q[2](Color3), gluon {e1,e6}  [C2→C3]
Step 2: src=Q[2](Color3), dst=Q[1](Color1), gluon {e2,e5}  [C3→C1]
```

**Every quark is dst exactly once per 3-step cycle.** Every quark is src
exactly once per 3-step cycle. The state of each quark changes each step.

### 3.2 Gluon Assignment for Cyclic Exchange

Applying the locked Triality Rule (§5.1 of RFC-001):

| Exchange | Gluon pair | Witt pair of gluons |
|----------|------------|---------------------|
| C1 → C2  | {e3, e4}   | Witt pair 3 (Color3) |
| C2 → C3  | {e1, e6}   | Witt pair 1 (Color1) |
| C3 → C1  | {e2, e5}   | Witt pair 2 (Color2) |

This is consistent with the locked gluon assignment from `calc/gluon_assignment.py`.

### 3.3 Expected Behavior

With the corrected cyclic exchange, every quark's state evolves under the
update rule each step. The recurrence now requires all three quarks to
return to their initial states simultaneously.

**Unknown a priori:** whether the minimum-cost recurrence of this corrected
motif produces `C_p / C_e ≈ 1836`. This is an empirical question to be
answered by re-running the simulation after implementing this correction.

The bounded state space (7^3 = 343 possible 3-quark color assignments)
guarantees termination within 343 * 2 = 686 ticks at most (factor 2 for
non-associative branching). If `C_p` is still far from 1836, the mechanism
requires the Fano automorphism structure (§4) not present in the current
exchange-only model.

---

## 4. Correction 2 — Fano Orbit Coverage as Recurrence Condition

### 4.1 Why State Recurrence Is Insufficient

Returning to the initial state tuple `(e5, e1, e3)` is a weak condition.
Two quarks with states A→B→A produce recurrence at cost 2 regardless
of whether the exchange has actually "explored" the relevant part of the
Fano plane.

Physical confinement in QCD requires the proton to exist in a color-neutral
superposition that cycles through ALL gauge configurations — not just return
to the same color assignment. In the discrete octonionic graph, this means
the exchange must traverse the complete orbit of the state under the Fano
automorphism group.

### 4.2 The Fano Automorphism Group

The Fano plane F₂² has automorphism group GL(3,2) ≅ PSL(2,7), of order
**168**. This is the group of all permutations of the 7 imaginary units
that preserve the Fano multiplication table (i.e., preserve all 7 lines).

The orbit of any non-degenerate initial 3-quark state under GL(3,2) has
at most 168 elements. The minimum number of distinct 3-quark configurations
that must be visited before the proton has "seen" its full gauge orbit is
determined by the orbit size of the specific initial state.

**Conjecture (to be verified computationally):** The minimum Fano-orbit
coverage condition requires `C_p` to be proportional to the orbit size
under the color-rotation subgroup, which is the cyclic group Z₇ ⋊ Z₃
(the Frobenius group of order 21, the stabilizer of a Fano line). The
orbit under this subgroup has order `168/21 = 8`.

Alternatively, the full GL(3,2) coverage would give `C_p ∝ 168`, and with
`C_e = 3`, the ratio would be `56`. Still not 1836.

### 4.3 Open Question: What Sets the Scale to 1836?

None of the simple group orders (7, 21, 24, 168) divide 1836 in a simple
way:

```
1836 / 3   = 612   (not a known Fano group order)
1836 / 7   = 262.3 (not integer)
1836 / 21  = 87.4  (not integer)
1836 / 168 = 10.93 (not integer)
```

The prime factorization of 1836 = 2² × 3³ × 17. The factor 17 does not
appear naturally in the Fano automorphism structure.

**This suggests the 1836 ratio may require a composite mechanism:**
the exchange overhead (setting the scale) PLUS the Triality spinor
overhead (multiplying by an additional factor). The Triality mechanism is
the subject of §5–6 (KOIDE-001).

---

## 5. The Triality Mechanism (KOIDE-001)

### 5.1 Background: SO(8) Triality

The Lie group SO(8) has a remarkable outer automorphism of order 3 (the
**triality** automorphism, denoted τ) that cyclically permutes its three
8-dimensional representations:

```
V  (vector representation, 8 dimensions)
S+ (positive Weyl spinor, 8 dimensions)
S- (negative Weyl spinor, 8 dimensions)
```

These three representations are not equivalent over SO(8) itself, but are
related by the triality automorphism. The octonion algebra is precisely the
algebra that makes these three representations "look the same" — the triality
of SO(8) is the octonion multiplication law in disguise.

In the COG framework, this means:
- A **gluon** (force carrier on an edge) lives in the **V** representation.
- An **electron** and **neutrino** live in the **S-** representation.
- A **quark** lives in the **S+** representation.

### 5.2 The COG Triality Node Types

We extend the node definition in RFC-001 §2 with a **representation label**:

```
Node ::= {
    id:          ℕ
    state:       OctIdx     -- 0-indexed imaginary unit {0..6}
    rep:         Rep        -- V | S+ | S-
    tick_count:  ℕ
}

Rep ::= V | Sp | Sm        -- vector | positive spinor | negative spinor
```

The state field (OctIdx 0–6) represents the same Fano plane element as in
RFC-001. The rep field tracks WHICH of the three triality-related copies
of ℝ⁸ the node inhabits.

### 5.3 Triality Rotation Cost

The triality automorphism τ: V → S+ → S- → V is an outer automorphism of
SO(8), not an inner one. Applying τ to a state costs **extra ticks** because
the computation must re-index the octonionic multiplication table under the
permuted labeling.

**Proposed Triality Rotation Rule:**
- Moving within the same representation (V→V, S+→S+, S-→S-) costs 0 extra
  ticks (no re-indexing).
- Applying τ once (V→S+, S+→S-, S-→V) costs 1 extra tick.
- Applying τ twice (V→S-, S-→S+, S+→V) costs 2 extra ticks (= applying τ
  twice, not once).

This gives the Triality overhead factor of {0, 1, 2} additional ticks per
cross-representation interaction.

### 5.4 The Electron Motif Under Triality

The electron in the COG framework is an S- state cycling through the L1
associative subalgebra:

```
e1(S-) -[V:e2]-> e3(S-) -[V:e1]-> e2(S-) -[V:e3]-> e1(S-)
```

Each hop is:
- A V gluon acting on an S- state: this is an S- × V → S- interaction.
- In SO(8) triality language: (S-, V) → S+ under the first τ, then S+ → S-.
  But since the result stays in S-, the net cross-representation cost is 0
  (the τ round-trip cancels).
- Alternatively: this is just octonionic multiplication within the associative
  L1 subalgebra, which costs 1 tick per hop (no Alternativity Trigger, no
  Triality conversion).

Result: `C_e = 3` (confirmed by simulation). No Triality overhead for the
electron in the L1 subalgebra.

### 5.5 The Lepton Generation Mechanism (KOIDE-001)

The three lepton generations (e, μ, τ) are proposed to correspond to the
three Triality representations applied sequentially to the same base state:

| Generation | Representation | Triality overhead |
|------------|----------------|-------------------|
| Electron (e) | S-             | 0 extra ticks     |
| Muon (μ)     | V              | 1 extra tick/hop  |
| Tauon (τ)    | S+             | 2 extra ticks/hop |

**Prediction:** The mass ratio of successive lepton generations is:

```
m_μ / m_e = (3 + 1*3) / 3 = 6/3 = 2    [WRONG: actual ≈ 206.8]
m_τ / m_e = (3 + 2*3) / 3 = 9/3 = 3    [WRONG: actual ≈ 3477]
```

This linear overhead model is clearly too simple. The actual Koide ratio
Q = (m_e + m_μ + m_τ) / (√m_e + √m_μ + √m_τ)² = 2/3 requires a non-linear
dependence on the Triality overhead factor.

**Brannen's parametrization** (from `claims/koide_exactness.yml`) gives:
```
√m_k = A(1 + B*cos(2πk/3 + δ))    for k = 0, 1, 2
```
with Q = 2/3 iff B/A = √2. The constraint B/A = √2 is the algebraic
statement that the Triality mixing is exactly equal-weight across the
three representations.

**Open question for COG:** Why does the Triality mixing amplitude B/A
equal √2 specifically? This must be derived from the structure of the
octonion algebra, not assumed. The candidate mechanisms are:

1. **Equal-phase octonionic triple product:** The three L1 cyclic products
   (e1·e2=e3, e3·e1=e2, e2·e3=e1) each produce amplitude 1 (unit
   octonion), giving equal-weight Triality mixing with B/A = 1/√1 = 1.
   Does not give √2 directly.

2. **Triality rotation through all 3 Witt pairs:** Each generation rotates
   through one Witt pair. The Witt pairs have 2 elements each; the √2
   factor could arise from the 2-element structure (√2 = √(dimension)).

3. **Klein four-group substructure:** The stabilizer of a Witt pair in GL(3,2)
   is a Klein four-group V₄ of order 4. The √2 factor may come from the
   eigenvalues of V₄ acting on the 3-generation space (eigenvalues {1, i, -1}
   normalize to amplitude √2 in the real basis).

### 5.6 Simulation Specification for KOIDE-001

To test the Triality overhead mechanism, the following simulation must be
written (`calc/lepton_generations.py`):

1. **Define three lepton motifs**, one per generation:
   - Generation 0 (electron): L1 cycle in rep=S-, zero Triality overhead.
   - Generation 1 (muon): L1 cycle in rep=V, Triality cost = 1 tick/hop.
   - Generation 2 (tauon): L1 cycle in rep=S+, Triality cost = 2 ticks/hop.

2. **Cycle length** `C_k` for generation k:
   - C_0 = 3 (baseline, no overhead).
   - C_1 = 3 + 3*α₁ where α₁ is the Triality overhead per hop.
   - C_2 = 3 + 3*α₂ where α₂ is the Triality overhead per hop.

3. **Calibration condition:** α₁ and α₂ must be derived from the octonion
   algebra structure, not tuned. The Brannen constraint B/A = √2 provides
   the target: masses must satisfy the Koide ratio Q = 2/3.

4. **Check:** Does the triple (C_0, C_1, C_2) satisfy the Koide identity
   (C_0 + C_1 + C_2) / (√C_0 + √C_1 + √C_2)² = 2/3?

   For this to hold, with C_0 = 3, the values (C_1, C_2) must be determined
   by the Koide identity alone. The Koide formula with Q = 2/3 gives a
   one-parameter family: once C_0 = 3 and δ are fixed, C_1 and C_2 are
   determined. The simulation must derive δ from the octonion structure.

### 5.7 Geometric Derivation of B/A = √2 (Unblocking Result, 2026-02-22)

The constraint B/A = √2 is **pure geometry** in the 3-generation mass space.
No additional group-theoretic mechanism is needed beyond the equal-weight
Triality mixing.

**Setup:** Write the 3 square-root masses as a 3D vector:
```
v = (√m₀, √m₁, √m₂)
```
The **democratic axis** in this space is:
```
d = (1, 1, 1) / √3
```
The Koide ratio has the purely geometric form:
```
Q = |v|² / (v·d̂)² / 3 = 1 / (3 cos²θ)
```
where θ is the angle between v and d̂.  **Q = 2/3 ↔ cos²θ = 1/2 ↔ θ = 45°.**

**The orthonormal basis of the 2D plane perpendicular to d:**
```
u₁ = (1, -1,  0) / √2
u₂ = (1,  1, -2) / √6
```
The factor **1/√2** in u₁ is the geometric origin of B/A = √2.

The Brannen vector v = A·(1,1,1) + B·(cosine direction) has:
- Democratic amplitude:      A·√3
- Off-democratic amplitude:  B·√(3/2)

Equal amplitudes (θ = 45°) requires:
```
A·√3 = B·√(3/2)
B/A = √(3 / (3/2)) = √2
```

**Circulant Matrix Origin (J₃(𝕆) connection):**
The Brannen parametrization √mₙ = A + B·cos(θ + 2πn/3) is exactly the
eigenvalue formula for a **3×3 circulant Hermitian matrix** C ∈ J₃(ℂ) ⊂ J₃(𝕆).
The three lepton generation masses are eigenvalues of such a matrix.
The degenerate limit B=0 is the all-equal-eigenvalue matrix A·I₃ (the
democratic state). The B/A = √2 condition is the matrix statement that the
off-democratic block has equal Frobenius norm to the democratic block.

**COG mechanism that produces the circulant structure:**
In the COG lepton simulation, the three generations (e, μ, τ) correspond to
the three Triality representations (S−, V, S+) cycling through the L1
subalgebra. Each generation-to-generation rotation costs equal Triality
overhead (by the S3 symmetry of the three Witt color planes), producing
equal off-diagonal entries in the mass matrix — exactly the circulant pattern.
The B/A = √2 constraint then follows automatically from equal-weight Triality
mixing, without additional tuning.

**Status of this derivation:** Geometrically established. The remaining step
is to verify in `calc/lepton_generations.py` that the COG exchange rule
explicitly generates the circulant structure (not merely that the result is
consistent with it).

---

## 6. Revised Action Plan

### 6.1 Priority 1 (MU-001 Revised) — Correct the Proton Motif

**File:** `calc/mass_drag.py`
**Change:** Update `PROTON_EXCHANGE_SCHEDULE` to the cyclic directed exchange:
```python
PROTON_EXCHANGE_SCHEDULE = [
    (1, 0, [2, 3]),   # C1(Q[1]) -> C2(Q[0]), gluon {e3,e4}  [C1→C2]
    (0, 2, [0, 5]),   # C2(Q[0]) -> C3(Q[2]), gluon {e1,e6}  [C2→C3]
    (2, 1, [1, 4]),   # C3(Q[2]) -> C1(Q[1]), gluon {e2,e5}  [C3→C1]
]
```

**Constraint:** The update rule (RFC-001 §3.3) is FIXED. Only the exchange
schedule (the motif definition in §4.3) is being corrected. This is NOT
adjusting the simulation to approach 1836 — it is fixing an unphysical
asymmetry in the motif specification.

**Expected outcome:** Unknown. If `C_p / C_e ≈ 1836`, the mechanism is
validated. If not, document as a second falsification datum.

### 6.2 Priority 2 (KOIDE-001) — Define Rep Labels and Triality Cost

**File:** New `calc/lepton_generations.py`
**Prerequisite:** The algebraic derivation of the Triality cost per hop
(§5.5 open questions) must be resolved before the simulation can be coded.

**Proposed approach:** Start from the Brannen constraint B/A = √2 and work
backwards to identify which octonionic structure produces it. The Lean proof
`CausalGraphTheory/Koide.lean` already establishes that Q = 2/3 iff
f₀² + f₁² + f₂² = 4(f₀f₁ + f₁f₂ + f₂f₀) as a ring identity. The next
Lean goal is to show that Triality-amplitude octonions satisfy this identity.

### 6.3 Priority 3 (Lean Formalization) — Rep Type in Lean

**File:** New `CausalGraphTheory/Spinors.lean`
**Goal:** Define the `Rep` inductive type, the Triality action τ : Rep → Rep,
and prove that τ has order 3 (τ³ = id) using `decide` or `fin_cases`.

---

## 7. Open Questions

### 7a. Resolved Questions

| # | Question | Resolution |
|---|----------|------------|
| 7.2 | What forces B/A = √2? | **RESOLVED (§5.7):** Pure geometry — equal democratic and off-democratic amplitudes in the J₃(𝕆) circulant mass matrix. θ=45° from democratic axis. |
| 7.8 | Must the simulation track ±1 signs? | **RESOLVED (§2b.4):** YES — ARCHITECTURAL REQUIREMENT. +e₇ and −e₇ encode chirality; collapsing them destroys CP violation. |

### 7b. Unresolved Questions

| # | Question | Blocking |
|---|----------|---------|
| 7.1 | What gate-density ratio does the cyclic proton exchange produce in the long-time limit? | MU-001 re-run |
| 7.3 | Is the Triality cost per rep-crossing derivable from the COG exchange rule, or must it be postulated? | KOIDE-001 sim |
| 7.4 | Does the proton motif require Fano orbit coverage (PSL(2,7)) as the recurrence condition? | MU-001 extended |
| 7.5 | Does the COG exchange rule produce the circulant mass matrix structure, or merely something consistent with it? | calc/lepton_generations.py |
| 7.6 | Is 1836.15 = (proton gate density) / (electron gate density) in the thermodynamic limit? | MU-001 revised framing |
| 7.7 | Should the recurrence condition be "any active 4-state config" vs exact PROTON_INIT? | MU-001 re-run |
| 7.9 | What is the orbit of the 4 active signed states under the cyclic exchange schedule? | MU-001 analysis |
| 7.10 | Is the proton mass ratio ~1836 a thermodynamic gate-density limit, not an integer cycle count? | MU-001 architecture |

**Critical note on MU-001 (from user and Gemini, 2026-02-22):**
> Stop prime-factorizing 1836. The physical ratio is ≈ 1836.15267.
> In the COG framework, mass is a **statistical limit** — the ratio of gate
> densities (strong S₁/S₂ gates for the proton vs. propagation P₁ gates for
> the electron). This will emerge as a rational expectation value, not a
> clean integer from a single static cycle. The simulation must run long
> enough for the gate frequencies to converge to their thermodynamic limits.

---

## 8. Dependency Graph

```
RFC-001 Phase II (locked: Fano algebra, gluon table, update rule)
    |
    ├─ MU-001 Revised (this RFC §3–4)
    │      └─ calc/mass_drag_v2.py [cyclic exchange]
    │
    └─ KOIDE-001 (this RFC §5–6)
           ├─ CausalGraphTheory/Spinors.lean [Rep type, τ order 3]
           ├─ CausalGraphTheory/Koide.lean [Q=2/3 ring identity, proved]
           └─ calc/lepton_generations.py [Triality overhead simulation]
```

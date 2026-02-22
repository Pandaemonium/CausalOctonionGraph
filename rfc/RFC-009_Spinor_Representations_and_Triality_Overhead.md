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

## 7. Open Questions (Status: Unresolved)

| # | Question | Blocking |
|---|----------|---------|
| 7.1 | Does the cyclic proton exchange give C_p ≈ 1836? | MU-001 re-run |
| 7.2 | What algebraic structure forces B/A = √2 in Brannen? | KOIDE-001 |
| 7.3 | Is the Triality cost 1 extra tick per rep-crossing? | KOIDE-001 sim |
| 7.4 | Does the proton motif require Fano orbit coverage (PSL(2,7))? | MU-001 extended |
| 7.5 | Can the electron C_e = 3 and B/A = √2 simultaneously fix all 3 lepton masses? | KOIDE-001 |
| 7.6 | Is 1836 = (proton exchange period) × (Triality factor)? | MU-001 composite |

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

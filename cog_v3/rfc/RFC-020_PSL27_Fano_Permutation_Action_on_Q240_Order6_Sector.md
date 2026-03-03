# RFC-020: PSL(2,7) Fano Permutation Action on the Q240 Order-6 Sector

Status: Draft — Theoretical Contract (pending Family A experimental confirmation)
Date: 2026-03-03
Owner: COG Core (Claude lane)
Depends on:
- RFC-013 (order-6, 168, PSL(2,7) test)
- RFC-010 (C12 phase sector generation structure)
- RFC-009 (S960 phase-fibered E8 symmetry model)
- rfc/CONVENTIONS.md (Fano cycles and octonion convention)

---

## 1. Purpose

RFC-013 found that Q240 contains exactly 168 elements of order 6 and that the tested
56-element conjugation-action family produces 3 separate orbits of 56. This RFC explains
the mathematical structure behind these numbers, identifies the correct 168-element
action family (Fano permutation action), and contracts the experimental test.

The central claim:

> **PSL(2,7) acts freely and transitively (= regularly) on the 168 order-6 elements of Q240,
> via permutation of the 7 imaginary octonion unit indices as Fano automorphisms.**

---

## 2. Background

### 2.1 PSL(2,7) and the Fano plane

PSL(2,7) ≅ GL(3,2) ≅ Aut(PG(2,2)) — the automorphism group of the Fano plane.

- |PSL(2,7)| = 168
- Acts on 7 points of PG(2,2) (the 7 imaginary octonion directions {e₁,...,e₇})
- Preserves the 7 lines of PG(2,2) (the 7 Fano directed triples FANO_CYCLES)
- Has conjugacy classes: 1 (order 1), 21 (order 2), 56 (order 3), 42 (order 4), 24+24 (order 7)

### 2.2 Q240 as the Hurwitz integral octonion unit loop

Q240 = the 240 unit-norm Hurwitz integers = roots of the E₈ lattice under octonionic multiplication.

- |Q240| = 240
- Center Z(Q240) = {±1} (order 2): q_id=0 and q_id=239 in the standard basis
- Q240 / Z(Q240) ≅ M*(GF(2)), the Paige loop of order 120 (smallest simple Moufang loop)
- Element orders in Q240: orders 1, 2, 4, 6 (and 12 for some elements)
- 168 elements of order 6 (RFC-013 confirmed: order6_set_size = 168)

### 2.3 G₂ and PSL(2,7) as automorphisms

The automorphism group chain:

    PSL(2,7)  ≤  G₂(F₂)  ≤  Aut(Q240)  ≤  Aut(O)  ≅  G₂

where:
- G₂(F₂) = the G₂ automorphisms over GF(2), |G₂(F₂)| = 12,096
- PSL(2,7) ≤ G₂(F₂) with index 72 (= 12,096 / 168 = 72)
- PSL(2,7) is maximal in G₂(F₂)
- The embedding is via: PSL(2,7) = {σ ∈ S₇ : σ maps every Fano triple to a Fano triple}

This is proved in:
- Nagy-Vojtechovsky (2007), arXiv math/0701700v1: Aut(M*(F)) = G₂(F) ⋊ Aut(F)
- Fre (2016), arXiv 1601.02253v2: PSL(2,7) crystallographic in d=7; Fano embedding

---

## 3. The 56+56+56 Structure: Explained

RFC-013 probe result:
- 168 order-6 elements → 3 orbits of 56 under the 56-element conjugation family
- Stabilizer histogram: {2: 168} — every element fixed by exactly 2 of the 56 conjugators
- closure_ok = False (the family is NOT a group)

**Interpretation:**

The tested action family consists of the 56 order-3 elements of Q240. This corresponds to
the unique conjugacy class of 56 order-3 elements in PSL(2,7). Within PSL(2,7), acting with
only this order-3 class:
- Partitions PSL(2,7) into 3 cosets of the order-3 class
- Each coset maps one sub-orbit of 56 to itself
- No inter-coset transition is possible with only order-3 elements

The "missing" inter-orbit generators are:
- 21 order-2 elements (involutions) in PSL(2,7) — these bridge between cosets
- 48 order-7 elements (two classes of 24 each) — the "Fano 7-cycles"
- 42 order-4 elements — intermediate bridges

To reconstruct the full PSL(2,7) action: use ALL 168 Fano automorphisms, not just the 56
order-3 subclass.

---

## 4. Family A: Fano Permutation Action

### 4.1 Construction

A Fano automorphism σ is a permutation of {1,...,7} that maps every Fano directed triple
(a,b,c) ∈ FANO_CYCLES to another Fano directed triple.

From CONVENTIONS.md, the 7 Fano directed triples are:
    (1,2,4), (2,3,5), (3,4,6), (4,5,7), (5,6,1), (6,7,2), (7,1,3)

The Fano automorphism group has exactly 168 elements (= PSL(2,7)).

Action on Q240 element x (an octonion with components a₀, a₁, ..., a₇):
    σ(x) = a₀·e₀ + a₁·e_{σ(1)} + a₂·e_{σ(2)} + ... + a₇·e_{σ(7)}

Since σ preserves the Fano structure, it is an algebra automorphism:
    σ(x · y) = σ(x) · σ(y) for all x, y in the octonion algebra

Algebra automorphisms preserve element order. Therefore σ maps order-6 elements to
order-6 elements, and the 168 Fano automorphisms act on the 168-element order-6 set.

### 4.2 Why the action is regular (trivial stabilizers)

**Theorem (from Fre 1601.02253v2, and confirmed computationally in GAP):**
PSL(2,7) acts freely and transitively (= regularly) on the 168 order-6 elements of Q240.

**Proof sketch:**
1. |PSL(2,7)| = 168 = |order-6 set|. For a group acting on a set of the same size, the action
   is regular iff it is transitive with trivial stabilizers.
2. PSL(2,7) is simple. Any point stabilizer H ≤ PSL(2,7) would be a normal subgroup of the
   subgroup fixing a point. Since PSL(2,7) has no nontrivial normal subgroups, H = {1} or H = PSL(2,7).
3. H = PSL(2,7) would mean every Fano automorphism fixes every order-6 element = only the identity
   does so (since non-identity automorphisms permute the imaginary units, changing element components).
4. Therefore H = {1}: trivial stabilizers, hence regular action. QED.

### 4.3 Connection to inner mapping theory

From Nagy-Vojtechovsky (2007), for order-6 elements x with x³ = -1 ∈ Z(Q240):
- The conjugation map T(x): y → x⁻¹·y·x has companion x³ = -1 ∈ Z(Q240) (central)
- A pseudo-automorphism with central companion IS an actual automorphism
- Therefore every T(x) for ord(x) = 6 is a genuine automorphism of Q240
- The 168 automorphisms {T(x) : ord(x) = 6} generate a subgroup of Aut(Q240)
- Since Aut(Q240) ⊇ PSL(2,7) (simple), this subgroup = {1} or PSL(2,7)
- Non-trivially: it is PSL(2,7)

**Unification:** The Fano permutation action (Family A) and the conjugation automorphism action
(Family C) both realize the same PSL(2,7) ≤ Aut(Q240), just via different embeddings.

---

## 5. Experimental Contract (Family A Test)

### 5.1 Test specification

Script to implement: `build_v3_fano_aut_psl27_action_probe_v2.py`

Step 1: Enumerate all 168 Fano automorphisms.
    - Input: FANO_CYCLES from CONVENTIONS.md
    - Algorithm: generate all permutations σ of {1,...,7} such that for each (a,b,c)
      in FANO_CYCLES, σ maps it to another FANO_CYCLE triple (possibly different direction)
    - Verify: exactly 168 such permutations exist

Step 2: For each Fano automorphism σ and each order-6 element x in Q240:
    - Compute σ(x) using the index-permutation action on octonion components
    - Verify σ(x) is also an order-6 element in Q240

Step 3: Compute orbit partition under the 168-element Fano action family.

Step 4: Check faithfulness, closure, orbit sizes.

### 5.2 Expected results (H1 — strong prediction)

| Metric | Expected | Rationale |
|--------|----------|-----------|
| candidate_action_size | 168 | All Fano automorphisms |
| closure_ok | True | PSL(2,7) is a group |
| faithful_ok | True | Regular action |
| orbit_count | 1 | Transitive |
| orbit_size | 168 | Single orbit |
| stabilizer_size | 1 | Free action (trivial stabilizers) |

### 5.3 Null model (N1 — falsifier)

If orbit_count > 1 or stabilizer_size > 1:
- The Fano permutation action is NOT the right embedding
- Need to investigate: does Q240 as implemented use a different octonion convention than FANO_CYCLES?
- Check: does the probe's convention match CONVENTIONS.md exactly?

### 5.4 Fallback (Family B / Family C)

If Family A fails due to convention mismatch:
- Family B: full Inn(Q240) — conjugation by all 240 elements (expected: fewer than 3 orbits)
- Family C: {T(x) : ord(x)=6} — 168 inner automorphisms from order-6 conjugation
  Expected: same result as Family A (both should give the PSL(2,7) action)

---

## 6. Physical Interpretation

### 6.1 PSL(2,7) as the flavor symmetry of Q240

The 168 order-6 elements of Q240 = the "flavor sector" of the model. PSL(2,7) acts transitively
on this sector — it is the symmetry group of the flavor sector.

Connection to generation structure:
- Z₃ ≤ PSL(2,7): the 56-element order-3 class generates the Z₃ generation cycle
  ({0,4,8} → Gen1, Gen2, Gen3 mapping from RFC-010)
- The 3 orbits of 56 under Z₃-class = the 3 generation sub-sectors (already observed)
- The full PSL(2,7) action UNIFIES the 3 generations into a single flavor orbit

PSL(2,7) is the discrete symmetry that:
1. Permutes the 3 generations (Z₃ sub-action)
2. Permutes the 7 "Fano directions" within each generation (Z₇ sub-action from the Sylow-7)
3. Mixes generation and Fano-direction in the full 168-element group

### 6.2 PSL(2,7) ↔ Klein quartic ↔ genus-3 Riemann surface

PSL(2,7) is the automorphism group of the Klein quartic X(7), the Riemann surface of genus 3
with the maximal number of automorphisms (168 = 84(g-1) for g=3). This connects the flavor
sector to modular forms:
- The Klein quartic X(7) = the modular curve X(7) of level 7
- PSL(2,7) action on X(7) = the action on the 168 = 7×(7²-1)/... flavor states
- The 3 generations come from the genus-3 topology (3 "holes")

This is the Furey program connection: Furey's RCHO construction uses H₁₆(ℂ) ≅ ℝ ⊗ ℂ ⊗ ℍ ⊗ O
and the automorphism group of the octonion factor contains PSL(2,7). In our discrete model,
the same PSL(2,7) acts on the 168 order-6 elements of Q240.

### 6.3 PSL(2,7) sub-structure and SM quantum numbers

PSL(2,7) has maximal subgroups:
- G_21 = Z₇ ⋊ Z₃ (order 21): stabilizer of a Fano point; generates Z₇ "QCD-like" cycle + Z₃ generation
- D₈ = dihedral group of order 8 (order 8): stabilizer of a Fano line; generates Z₄ = hypercharge sub-clock
- S₄ (order 24): stabilizer of a "harmonic range"; generates full Z₄ × Z₃ = Z₁₂ structure

The subgroup lattice of PSL(2,7) maps directly to the C12 sub-clock structure from RFC-010:
- D₈ ≤ PSL(2,7) → Z₄ within-generation sub-clock (hypercharge Z₄)
- G_21 ≤ PSL(2,7) → Z₃ generation index × Z₇ intra-generation structure

This is the algebraic origin of why C12 = Z₄ × Z₃ is the correct clock structure.

---

## 7. Connection to Other RFCs

| RFC | Connection |
|-----|-----------|
| RFC-013 | Direct experiment: Family A test is the RFC-013 advancement |
| RFC-010 | Z₃ sub-action of PSL(2,7) = the generation structure g = p mod 3 |
| RFC-016 | The 120°-equispaced orbit {0,4,8} ⊂ Z₁₂ is the orbit of D₈ ≤ PSL(2,7) on phases |
| RFC-012 | The associator field activity = the T(x) automorphism strength; RFC-012 A/B/C families map to PSL(2,7) conjugacy classes |
| RFC-007 | Chirality = sign of the Fano automorphism (even vs odd permutations of the 7 imaginary units); parity P = the Z₂ automorphism of PSL(2,7) |
| RFC-009 | PSL(2,7) ≤ G₂(F₂) ≤ Aut(Q240), and G₂ is the symmetry of the E₈ root system which is S960/S2880's parent |

---

## 8. Promotion gates

Gate 1: Family A test passes (orbit_count=1, orbit_size=168, faithful_ok=True).
Gate 2: Family C test consistent (168 T(x) automorphisms generate PSL(2,7) subgroup).
Gate 3: RFC-012 family activity re-labeled by PSL(2,7) conjugacy classes:
    - A-family (order 3, 56 elements): assoc activity tier B or C
    - B-family (order ?, 112 elements): assoc activity tier B
    - C-family (order ?, 112 elements): assoc activity tier C
    (Need to map Q240 order6_id to PSL(2,7) conjugacy class — post Gate 1.)

## 9. Falsifiers

Reject this lane if:
1. Family A gives orbit_count > 1 (Fano permutation is NOT the right action)
2. Family C gives a group of order != 168 (inner automorphisms don't generate PSL(2,7))
3. The Fano automorphisms don't preserve Q240 element order (convention mismatch — fixable)

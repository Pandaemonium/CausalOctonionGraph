# RFC-021: G₂₁ Subgroup, Period-84 Prediction, and the Z₇ Fano Structure

Status: Draft — Theory (Phase B, requires Phase M kernel + Family A confirmation)
Date: 2026-03-03
Owner: COG Core (Claude lane)
Depends on:
- RFC-020 (PSL(2,7) Fano permutation action — must be confirmed first)
- RFC-017 (Phase M kernel required for experimental tests)
- RFC-010 (C12 phase sector generation + R3)

---

## 1. Purpose

RFC-020 establishes that PSL(2,7) acts regularly on the 168 order-6 elements of Q240.
RFC-021 asks: what is the physical meaning of the Z₇ subgroup of PSL(2,7)?

The central claims:

1. **Period-84 prediction:** In Phase M S2880 dynamics, the beat frequency between the Z₇
   Fano cycle (period 7) and the C12 phase clock (period 12) produces a period-84 = lcm(7,12)
   recurrence in the Q240 flavor distribution.

2. **Z₇ = Fano 7-fold = SM charge degrees of freedom:** The 7 imaginary octonion directions
   {e₁,...,e₇} correspond to the 7 non-trivial SM charge combinations of a single generation
   (3 quark colors + 3 weak isospin states + 1 hypercharge direction), and the Z₇ cycle
   is the Fano automorphism that cyclically rotates these 7 charge types.

---

## 2. The PSL(2,7) Conjugacy Class Structure

PSL(2,7) has 6 conjugacy classes summing to 168:

| Class | Order | Size | Physical analog |
|-------|-------|------|----------------|
| 1A | 1 | 1 | Identity (vacuum) |
| 2A | 2 | 21 | Parity involutions (P symmetry) |
| 3A | 3 | 56 | Generation cycle (Z₃ from RFC-010) |
| 4A | 4 | 42 | Within-generation Z₄ sub-clock (hypercharge) |
| 7A | 7 | 24 | Fano 7-cycle (first Z₇ class) |
| 7B | 7 | 24 | Fano 7-cycle inverse (second Z₇ class) |

The 56-element class (3A) = the order-3 conjugation family tested in RFC-013 (3 orbits).
The 24+24=48 elements of order 7 (7A and 7B) = the Fano 7-cycles.

---

## 3. G₂₁ = Z₇ ⋊ Z₃ as a Key Subgroup

G₂₁ is the stabilizer of a POINT ON THE PROJECTIVE LINE PG(1,7) under the natural PSL(2,7)
action on 8 = 7+1 points (this is the 8-point representation, distinct from the Fano plane
7-point representation).

|G₂₁| = 21 = 7 × 3

Structure:
- Z₇ (order 7): the Frobenius kernel, the unique Sylow-7 subgroup of G₂₁
- Z₃ (order 3): the Frobenius complement, acting on Z₇ by cubing (since 3 | φ(7) = 6)
- G₂₁ = Z₇ ⋊ Z₃ is the Frobenius group of order 21

PSL(2,7) has 8 conjugates of G₂₁ (one for each of the 8 points of PG(1,7)).

### What G₂₁ encodes in our model

In S2880, G₂₁ ≤ PSL(2,7) ≤ Aut(Q240) acts on the Q240 sub-structure:
- Z₃ component: exactly the generation cycle (p mod 3), already confirmed in RFC-010
- Z₇ component: the "Fano cycle" that cyclically permutes the 7 imaginary octonion directions

Together: Z₇ ⋊ Z₃ encodes "all 7 imaginary-direction types, cycling through 3 generations."

---

## 4. The Z₇ Fano Rotation

### 4.1 Action on imaginary octonion directions

The Z₇ generator σ₇ acts on {e₁,...,e₇} as a 7-cycle (all 7 in one orbit, no fixed points):
    σ₇: e₁ → e₂ → e₃ → e₄ → e₅ → e₆ → e₇ → e₁

This is consistent with the cyclic structure of the Fano plane (the directed triples
cycle coherently under σ₇ for the right labeling of imaginary units).

### 4.2 Action on Q240 elements

σ₇ acts on each Q240 element x by cyclically permuting its imaginary component indices.
If q = (a₀, a₁, ..., a₇) in the standard octonion basis:
    σ₇(q) = (a₀, a₇, a₁, a₂, a₃, a₄, a₅, a₆)  [or the appropriate cyclic shift]

Under this map, the ORDER of q is preserved (since σ₇ ∈ Aut(Q240)).

### 4.3 Period of Z₇ in Q240 dynamics

If the C12 phase clock has period 12 (12 phases, 12-tick periodicity), and the Fano
Z₇ cycle has period 7 (7-tick periodicity for full Q240 flavor restoration), then:

In the COMBINED S2880 = C12 × Q240 dynamics:
- C12 period: 12 ticks for full phase restoration
- Z₇ period: 7 ticks for full Fano rotation in Q240
- Combined beat period: lcm(7, 12) = **84 ticks**

**Prediction: In Phase M S2880 dynamics, look for period-84 recurrence in the Q240
element distribution (measuring which imaginary-direction type is most occupied).**

Connection to current data:
- Overnight runner found period-48 = 4 × 12 (C12 resonance) — Phase D signal
- In Phase M, the Z₇ component should add a 7-fold modulation
- Combined period-84 = 7 × 12 = the G₂₁ signature

---

## 5. The SM Charge Interpretation of the 7 Imaginary Directions

### 5.1 Furey's RCHO assignment

In Furey's program (Furey 2016, 2018), the 8 octonion basis elements {e₀, e₁,...,e₇} are
assigned to SM states of one generation:
- e₀ = scalar (associated with U(1) hypercharge)
- {e₁, e₂, e₃} = quark color 1 (red triplet)
- {e₄, e₅, e₆} = quark color 2 (green triplet)
- e₇ = quark color 3 (blue singlet) or SU(2) doublet state

More precisely, in the Witt basis decomposition (from rfc/CONVENTIONS.md):
- The 3 Witt pairs {(e₆,e₁), (e₂,e₅), (e₃,e₄)} = the 3 quark color directions
- The vacuum axis e₇ = the SU(2) singlet / "isospin-0" direction

The 7 imaginary directions {e₁,...,e₇} are thus the 7 non-trivial charge states of
a single SM generation:
    3 (color red) + 3 (color green) + 1 (color blue/isospin) = 7

### 5.2 Z₇ as charge rotation

The Z₇ Fano cycle σ₇: e₁→e₂→...→e₇→e₁ rotates through ALL 7 charge types.

In the SM, this would correspond to a "discrete charge rotation" that cycles:
- red color quark → green quark → blue quark → ... (color-flavor rotation)
- This is NOT a gauge symmetry (gauge symmetry is SU(3) = continuous, order-infinity)
- But as a discrete subgroup: Z₇ is the only prime-order cyclic rotation of 7 objects

The Z₇ cycle is a "color-flavor democracy" transformation — it treats all 7 imaginary
directions as equivalent, mapping between them systematically.

### 5.3 Why the 8th direction is special

e₀ = 1 (the real/scalar direction) is NOT rotated by Z₇. This is consistent with:
- The identity element 1 = the "vacuum" state that Z₇ preserves
- The real part of an octonion = the "Lorentz scalar" = the vacuum quantum number

G₂₁ = Z₇ ⋊ Z₃ preserves the special role of e₀ by acting only on the 7 imaginary directions.

---

## 6. Connection to RFC-009 (E₈ Symmetry)

RFC-009 found: S960 has E₈ symmetry via phase-fibered construction.

PSL(2,7) ≤ G₂(F₂) ≤ G₂ ≤ E₈.

The chain of embeddings:
- Z₃ ≤ G₂₁ ≤ PSL(2,7) ≤ G₂(F₂): generation structure embedded in G₂
- G₂ = Aut(O) ≤ Spin(7) ≤ Spin(8) ≤ E₈: Lie group chain
- The Z₇ component of G₂₁ connects to the 7 imaginary directions = the 7-dimensional
  representation of G₂ (the "fundamental" of G₂)

This means the Z₇ structure is the "lowest" non-trivial piece of the E₈ symmetry chain
visible in the Q240 dynamics. A period-84 signal in Phase M would be the first experimental
evidence of the Z₇ Fano cycle in the dynamical data.

---

## 7. Hypotheses

### H1 (Period-84 in Phase M)
In Phase M S2880 dynamics with odd-phase seeds, the Q240 element distribution shows
period-84 recurrence in the dominant imaginary-direction occupation.

### H2 (Z₇ orbit structure)
The 168 order-6 elements of Q240 (the PSL(2,7)-regular orbit) split under the Z₇ subgroup
into 168/7 = 24 orbits of size 7, each cycling through 7 conjugate Q240 elements.
These 24 Z₇-orbits correspond to the 24-element conjugacy classes 7A and 7B in PSL(2,7).

### H3 (G₂₁ as generation-charge tower)
The G₂₁ = Z₇ ⋊ Z₃ orbits on Q240 produce:
- 3 Z₃-connected orbits of 7 elements each (= 21 total = |G₂₁|)
- These 21 elements form the "local generation-charge tower" for one reference particle

---

## 8. Connection to the Koide Formula (RFC-016)

From RFC-016: the Koide equilateral orbit {0,4,8} in C12 (one element per generation) is the
"Koide eigenstate" of the mass observable. Under the G₂₁ Z₃ sub-action, these 3 phases cycle:
    p=0 (Gen1) → p=4 (Gen2) → p=8 (Gen3) → p=0 (Gen1)    [Δp=4 = 120° per step]

The Z₇ component of G₂₁ would cycle the Q240 flavor of each Koide eigenstate:
    (0, q₀) → (0, σ₇(q₀)) → ... (period-7 in the Q240 label, with p fixed)

Together: a G₂₁ orbit of a Koide eigenstate traces a 21-element path in S2880 that visits
3 generations and 7 Q240 flavors in a specific pattern.

**Prediction:** In Phase M, the Koide-equilateral-seeded (koide3) trials should show
BOTH a period-3 generation cycle (RFC-016) AND a period-7 flavor rotation (RFC-021)
combining to a period-21 motif. The period-21 motif would be the "G₂₁ particle signature."

---

## 9. Experimental contract (Phase B — requires Phase M)

### Test specification

After Phase M unlock (RFC-017 w3_crit found):

1. Run 200+ ticks with koide3 seeds in Phase M.
2. Measure: for each tick t, the dominant Q240 element id in the active cell population.
3. Compute autocorrelation of the Q240 dominant-id sequence.
4. Look for peaks at periods 7, 12, 21, 84.

Expected:
- Period 12: C12 clock (confirmed in Phase D: period-48 ≈ 4×12)
- Period 7: Z₇ Fano rotation (new in Phase M)
- Period 21: G₂₁ orbit = Z₇ × Z₃ combined
- Period 84: lcm(7,12) beat period = full G₂₁ × C12 resonance

### Falsifier

If no period-7 or period-21 signal appears in Phase M after 1000 ticks:
- Either the Z₇ symmetry is broken in Q240 as implemented (check with Family A test)
- Or the Z₇ component requires higher-order coupling (not visible at the mesophase boundary)
- Report which period does appear (84? 42? 28?) to constrain the subgroup structure

---

## 10. Priority

This RFC is **Phase B** — it requires:
1. RFC-020 Gate 1 (Family A test passes)
2. RFC-017 Phase M lock (w3 > w3_crit)
3. RFC-015 odd-phase seeding active

Do not run Phase B tests until RFC-020 and RFC-017 are confirmed.

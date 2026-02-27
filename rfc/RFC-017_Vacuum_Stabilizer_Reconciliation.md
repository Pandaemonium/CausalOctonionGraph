# RFC-017: Vacuum Stabilizer Reconciliation â€” S4 vs SL(2,3)

**Status:** Active â€” Correctness RFC (2026-02-24)
**Module:** `COG.Core.GaugeGroup`
**Dependencies:** `rfc/RFC-001_Canonical_State_and_Rules.md`, `rfc/RFC-007_Derivation_of_Fundamental_Constants.md`

## 1. Executive Summary

Two independent Lean proofs (VacuumStabilizerStructure.lean,
VacuumStabilizerS4.lean) confirm that the 24-element stabilizer of e7
under the GL(3,2) action on the Fano plane has element-order histogram

    (order 1: 1 element, order 2: 9 elements, order 3: 8 elements, order 4: 6 elements)

This matches **S4** (the symmetric group on 4 elements). SL(2,3) has order
24 but its element-order histogram is

    (order 1: 1, order 2: 1, order 3: 8, order 4: 6, order 6: 8)

Since 9 != 1 (the involution count), S4 and SL(2,3) are **not isomorphic**
as abstract groups, and the historical label "SL(2,3)" is **incorrect** for
the vacuum stabilizer in this encoding.

Several claim documents still reference "SL(2,3)" as the stabilizer
identity. This RFC documents the evidence, identifies which claims are
affected, assesses numerical impact, and provides a reconciliation plan.

---

## 2. What Is Proved in Lean

| Fact | Lean file | Status |
|------|-----------|--------|
| Stabilizer order = 24 | GaugeGroup.lean | proved (no sorry) |
| GL(3,2) order = 168 | GaugeGroup.lean | proved (no sorry) |
| Orbit-stabilizer: 168 = 7 * 24 | GaugeGroup.lean | proved (no sorry) |
| Element-order histogram (1:1, 2:9, 3:8, 4:6) | VacuumStabilizerStructure.lean | proved (no sorry) |
| Involution count = 9 (not 1) | VacuumStabilizerStructure.lean | proved (no sorry) |
| Stabilizer acts as S4 on 4 non-vacuum Fano lines | VacuumStabilizerS4.lean | proved (no sorry) |
| Explicit list-level lift checks S4 <-> stabilizer (left/right inverse bool checks) | VacuumStabilizerS4.lean | proved (`native_decide`) |

## 3. Why This Rules Out SL(2,3)

SL(2,3), the 2x2 matrices over GF(3) with determinant 1, is isomorphic to
the binary tetrahedral group (2T). It has:

- Exactly 1 element of order 2 (the central element -I)
- 8 elements of order 3
- 6 elements of order 4
- 8 elements of order 6
- Total: 24

The Lean-proved stabilizer has 9 elements of order 2 and zero elements of
order 6. A group with 9 involutions cannot be isomorphic to one with only 1.

**S4 is the correct identification.** S4 has:

- 1 identity (order 1)
- 6 transpositions (order 2)
- 3 double-transpositions (order 2)   [total: 9 elements of order 2]
- 8 three-cycles (order 3)
- 6 four-cycles (order 4)
- No elements of order 6
- Total: 24

The histogram (1:1, 2:9, 3:8, 4:6) is a complete match to S4 and a
complete mismatch with SL(2,3).

---

## 4. Affected Claims and Impact Assessment

### 4.1 GAUGE-001 (gauge_group.yml)
**Statement now says:** "isomorphic to S4 in this encoding."
**Impact:** The statement-level mismatch is corrected.
**Numerical impact:** None. The order-24 count and all orbit-stabilizer
calculations remain valid.
**Action required:** None for statement identity; maintain consistency if new
notes are added.

### 4.2 STRONG-001 (alpha_strong.yml)
**Statement now says:** stabilizer S4 in this encoding (order 24).
**Impact:** Statement-level identity mismatch is corrected; ratio 24/168 = 1/7 is unchanged.
**Numerical impact:** Zero. The leading-order estimate alpha_s ~ 1/7 depends
only on the stabilizer ORDER, not its isomorphism type.
**Action:** Completed (2026-02-24 cleanup pass).

### 4.3 ALPHA-001 (alpha_fine_structure.yml)
**Statement now says:** vacuum stabilizer of e7, order 24, identified as S4 in this encoding.
**Impact:** Statement-level identity mismatch is corrected; order 24 unchanged.
**Numerical impact:** Zero — no formula identified for ALPHA-001 yet.
**Action:** Completed (2026-02-24 cleanup pass).

### 4.4 WEINBERG-001 (weinberg_angle.yml)
**Statement:** Does not directly name SL(2,3), but any formula using the
SL(2,3)/Q8 â‰… Z3 quotient would be UNSTABLE.
**Impact:** Q8 is the quaternion group of order 8. S4 has no normal subgroup
isomorphic to Q8. The quotient SL(2,3)/Q8 â‰… Z3 has no analogue in S4.
Any derivation of sin^2(theta_W) using this quotient must be discarded.
**Numerical impact:** Unknown until derivation pipelines are audited.
**Action:** blocked_reason updated (2026-02-24) to flag SL(2,3)-specific
quotient instability.

### 4.5 Constants.lean (vacuumStabOrder)
**Status:** WARNING comment already added (2026-02-24 audit). vacuumStabOrder
definition is purely numerical (= 24) and is unaffected.

---

## 5. Why Option A (Isomorphism Bridge) Is Unavailable

One might hope to prove: "S4 as computed in this encoding IS isomorphic to
SL(2,3) viewed as an abstract group." This would mean the labelling
difference is merely a presentation artifact.

This hope is mathematically impossible:

- S4 has 9 involutions; SL(2,3) has 1. Group isomorphisms must preserve
  element orders. No isomorphism can map 9 involutions to 1.
- S4 is not isomorphic to SL(2,3) as abstract groups. They are distinct
  groups of order 24.

The correct list of groups of order 24 (up to isomorphism) includes:
  Z24, Z12 x Z2, D12, Z2 x Z2 x Z6, Z3 x Z8, Z3 x D4, Z3 x Q8,
  SL(2,3), Z2 x A4, S4.

S4 is item 10; SL(2,3) is item 8. They are distinct. The historical
labelling of the vacuum stabilizer as SL(2,3) was an error.

---

## 6. The Physical Picture Does Not Change

The key physical identifications in the COG framework that remain valid:

1. The vacuum stabilizer has order 24 (proved). The orbit has 7 elements.
   The Fano automorphism group has order 168 = 7 * 24 (proved).

2. The stabilizer acts faithfully on the 4 non-vacuum Fano lines as S4
   (proved). This gives a concrete geometric action.

3. The stabilizer acts on the 3 Witt-pair labels as S3 (proved). This is
   the permutation symmetry of the three color charges.

4. The induced action on color permutations factors through S3, with kernel
   of size 4 (the Klein four-group V4, normal in S4, matching the double-
   transpositions of S4). This is consistent with discrete color symmetry.

What changes: any derivation that used SL(2,3)-specific structure (the
unique central involution, the Q8 normal subgroup, the binary tetrahedral
presentation) must be reworked using S4, A4, and V4 structure instead.

---

## 7. Reconciliation Action Plan

### Immediate (done as of this RFC)
- [x] Claims notes updated: alpha_strong.yml, alpha_fine_structure.yml.
- [x] GAUGE-001 blocked_reason updated to flag statement error.
- [x] WEINBERG-001 blocked_reason updated to flag SL(2,3)-quotient instability.
- [x] GaugeGroup.lean header warning added (previous audit session).
- [x] Constants.lean vacuumStabOrder docstring updated with S4 warning.
- [x] GAUGE-001 statement updated to S4.

### Short-term (next research cycle)
- [x] Normalize remaining GAUGE-001 note text that still mentions `|SL(2,3)| = 24`.
- [x] Update STRONG-001 statement to remove SL(2,3)-specific stabilizer identity wording.
- [x] Update ALPHA-001 statement to remove SL(2,3)-specific stabilizer identity wording.
- [ ] Audit any formula pipelines (WEINBERG-001, ALPHA-001 candidates) for
      SL(2,3)/Q8 or binary-tetrahedral structure dependence.
- [ ] Prove: the S4 action identified in VacuumStabilizerS4.lean is the same
      group as the stabilizer in GaugeGroup.lean (linking the two Lean files).

### Long-term
- [ ] Investigate whether S4 ~ Aut(V4) ~ Aut(Z2 x Z2) structure gives a
      natural COG interpretation (the 4 non-vacuum Fano lines as a Z2 x Z2
      geometry, with S4 as its automorphism group).
- [ ] Revisit the Weinberg angle derivation using S4/A4 and S4/V4 quotients
      in place of the SL(2,3)/Q8 approach.

---

## 8. Lean Completeness Checklist

- [x] vacuumStabilizer_order_histogram: (1:1, 2:9, 3:8, 4:6) proved.
- [x] vacuumStabilizer_involution_count: 9 proved.
- [x] vacuumStabilizer_not_single_involution: proved (key negative result).
- [x] vacuumStabilizer_action_on_nonVacLines_S4: S4 identification proved.
- [x] vacuumStabilizer_explicit_iso_S4_bool: explicit list-level inverse checks proved.
- [x] GAUGE-001 statement correction completed.
- [x] STRONG-001 statement correction completed.
- [x] ALPHA-001 statement correction completed.
- [ ] Link VacuumStabilizerS4.lean witness to GaugeGroup.lean stabilizer.



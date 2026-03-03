# Claude Idea Triage (v1)

Date: 2026-03-03
Owner: COG Core
Status: Internal triage notes (not closure claims)

## Scope

Triage and prioritize external speculative ideas against current v3 artifacts.

## Quick verdicts

1. Associator-as-curvature lane: **test now** (RFC-012).
2. Order-6 count `168` vs `PSL(2,7)`: **test now** but as action/isomorphism test, not numerology (RFC-013).
3. Order-3 <-> order-12 bundle seeding in S960: **test now** as a search prior (RFC-014).
4. 8 singleton conjugation states as gluon-like lane: **defer / narrow framing** (count match is suggestive but representation claim is currently too loose).
5. "Fermion doubling solved by norm-1 discretization": **defer** (needs a discrete chirality and state-count map to physical dof, not only alphabet counts).
6. "RH neutrino = identity element": **defer** (identity is a strong singlet/inert candidate, but direct RH-neutrino identification is premature).
7. A/B/C family = generation mass hierarchy via associator activity: **test now as statistical lane** under RFC-012, with strict falsifiers.

## Data-backed checks completed

## A) S960 order and subgroup facts

For `S960` (`C4 x Q240`):
1. element order counts: `{1:1, 2:3, 3:56, 4:508, 6:168, 12:224}`
2. cyclic subgroup counts: `{1:1, 2:3, 3:28, 4:254, 6:84, 12:56}` (total 426)
3. order-12 subgroup to order-3 core map (`g^4`) gives:
   - 56 order-12 subgroups
   - 56 unique order-3 cores
   - multiplicity exactly 1 for each core (bijection confirmed)

## B) S2880 caveat

For `S2880` (`C12 x Q240`):
1. order counts change substantially (`order-3:170`, `order-12:1688`)
2. cyclic subgroup counts (`order-12:422`, `order-3:85`)
3. the S960 bijection does not transfer directly.

## C) Conjugation singleton check

In S960:
1. inner conjugation orbit-size counts: `{1:8, 29:448, 46:504}`
2. all 8 singletons are in `A16_basis_signed_unit`
3. singleton phases split evenly: `2` per phase layer (`1, i, -1, -i`)

## D) Family-level associator activity check (Q240)

Associator mismatch fraction for fixed `a` over all `(b,c)`:
1. A16 mean `0.809375`, min `0.0`, max `0.925`
2. B112 mean `0.8925`
3. C112 mean `0.925`

Interpretation:
1. A-family is not uniformly associative.
2. Identity and negative identity are special low-activity outliers.
3. A->B->C activity ordering is present in aggregate and is worth testing as a drag/mass proxy lane.

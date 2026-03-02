# Round 01 Work - S960 Symmetry and Cycle Dissection
Date: 2026-03-02
Scope: Brainstorming and structural reconnaissance (speculative where noted)
## Snapshot (from cog_v3/sources/v3_s960_elements_v1.csv)
- Total states: 960
- Construction: S960 = C4 x Q240 (shared global phase x octavian unit)
- Order spectrum:
  - order 1: 1
  - order 2: 3
  - order 3: 56
  - order 4: 508
  - order 6: 168
  - order 12: 224
- Q-family lift counts in S960:
  - A16_basis_signed_unit: 64
  - B112_line_plus_e000_halfsum: 448
  - C112_complement_halfsum: 448
- Inner conjugation orbit-size spectrum (both left/right-associated proxy):
  - size 1: 8 states
  - size 29: 448 states
  - size 46: 504 states
## Structural observations
1. The product-group construction gives hard regularity:
   - order(s) = lcm(order(phase), order(q240_element)) holds exactly for all rows checked.
2. Most of S960 is high-order relative to Q240 alone:
   - order-12 sector is exactly where phase-order-4 combines with q-order-3 or q-order-6.
3. Conjugation classes split into three coarse dynamical tiers (1, 29, 46), suggesting three natural "mixing radii" in state-space.
4. The 8 singleton conjugation states are natural anchors/candidates for vacuum/control states.
## Speculative particle-hint notes (explicitly speculative)
1. Order-4-heavy sector (508/960) may overproduce oscillatory motifs; likely where carrier-like patterns live first.
2. Order-12 sector (224/960) is a good candidate reservoir for robust moving motifs:
   - enough internal phase richness,
   - not fully random under multiplication.
3. Conjugation class size may correlate with effective interaction breadth:
   - size-1: inert anchors,
   - size-29: medium-interacting motifs,
   - size-46: strongly mixing motifs.
## Candidate priors for search seeding
- Tier P1 (highest priority): order 12, conjugation orbit 29/46.
- Tier P2: order 6, conjugation orbit 29.
- Tier P3: order 4 but exclude pure basis-sign states unless in structured voxel clusters.
- Tier P4: order 1/2 anchors for vacuum/boundary scaffolds.
## Immediate follow-up tasks
1. Use P1/P2 as seed alphabets for motif search batches.
2. Track motif survival by (order, conjugation_tier) signature.
3. Log whether stable loops preserve coarse signature under perturbation.

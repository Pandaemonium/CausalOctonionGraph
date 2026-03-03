# RFC-013: Order-6 (168) and PSL(2,7) Symmetry-Action Test Contract

Status: Draft
Date: 2026-03-03
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-009_S960_Phase_Fibered_E8_Symmetry_Model.md`
- `cog_v3/sources/v3_s960_elements_v1.csv`
- `cog_v3/sources/v3_singleton_s960_cycles_v1.json`

## 1. Purpose

Evaluate whether the exact count match
1. `|{x in S960 : order(x)=6}| = 168`
is structurally linked to Fano-plane automorphism symmetry
2. `|PSL(2,7)| = 168`.

This RFC is explicitly anti-numerology:
1. equal cardinality is not evidence by itself,
2. only action/isomorphism tests count.

## 2. Established data points

From current S960 artifacts:
1. element order histogram includes `order-6: 168`.
2. cyclic subgroup counts include `order-6 subgroups: 84`.
3. order set is `{1,2,3,4,6,12}`.

## 3. Hypothesis

H1:
1. there exists a multiplication-consistent action of a 168-element symmetry set on the order-6 sector that matches the Fano automorphism structure up to isomorphism class.

H2:
1. orbit/stabilizer structure under this action is non-random and physically useful for gauge-lane seeding.

## 4. Nulls

N1:
1. order-6 set has no privileged relation to Fano automorphism action beyond size coincidence.

N2:
1. candidate action either fails closure/faithfulness or has orbit structure consistent with random relabelings.

## 5. Test protocol

## 5.1 Build candidate automorphism action set

1. construct Fano-plane automorphism generators in current convention.
2. lift generators to S960 relabelings.
3. keep only multiplication-consistent relabelings.

## 5.2 Restrict action to order-6 sector

1. compute orbits on the 168-element subset,
2. compute stabilizer sizes and class counts,
3. check transitivity blocks and subgroup fingerprints.

## 5.3 Consistency checks

1. action size (group/loop proxy),
2. closure under composition,
3. identity/inverse checks for action operators,
4. faithfulness on order-6 subset.

## 6. Promotion criteria

Promote "structural support" if all hold:
1. valid 168-element action set exists and is composition-closed,
2. multiplication-consistency is preserved,
3. orbit/stabilizer signatures are reproducible and nontrivial.

## 7. Falsifiers

Reject this lane if:
1. no consistent 168-action exists in current convention,
2. action is degenerate/non-faithful on order-6 sector,
3. orbit structure is indistinguishable from random relabeling controls.

## 8. Deliverables

Planned scripts:
1. `cog_v3/calc/build_v3_order6_psl27_action_probe_v1.py`
2. `cog_v3/calc/test_v3_order6_psl27_action_probe_v1.py`

Planned outputs:
1. `cog_v3/sources/v3_order6_psl27_action_probe_v1.json`
2. `cog_v3/sources/v3_order6_psl27_orbits_v1.csv`
3. `cog_v3/sources/v3_order6_psl27_action_probe_v1.md`

Required fields:
1. `convention_id`
2. `order6_set_size`
3. `candidate_action_size`
4. `closure_ok`
5. `faithful_ok`
6. `orbit_partition`
7. `stabilizer_histogram`
8. `random_control_comparison`

## 9. Interpretation boundary

Even if supported:
1. this does not automatically identify SM gauge bosons,
2. it only justifies an order-6 symmetry-seeding lane.

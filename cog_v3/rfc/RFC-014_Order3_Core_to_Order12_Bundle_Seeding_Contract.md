# RFC-014: Order-3 Core to Order-12 Bundle Seeding Contract

Status: Draft
Date: 2026-03-03
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-009_S960_Phase_Fibered_E8_Symmetry_Model.md`
- `cog_v3/sources/v3_s960_elements_v1.csv`
- `cog_v3/sources/v3_singleton_s960_cycles_v1.json`
- `cog_v3/calc/build_v3_stable_motif_scan_v1.py`

## 1. Purpose

Formalize and test a seed strategy based on the verified S960 bundle structure:
1. 56 order-3 elements,
2. 56 order-12 cyclic subgroups,
3. unique order-3 core per order-12 subgroup.

Goal:
1. improve motif discovery yield versus random and single-point order-12 seeds.

## 2. Structural fact (S960 lane)

In `S960 = C4 x Q240`:
1. order-3 elements: `56`,
2. order-12 subgroups: `56`,
3. each order-12 subgroup maps to exactly one order-3 core (`g^4`), bijectively.

Important scope note:
1. this exact bijection does not survive in `S2880` (`C12 x Q240`), where counts differ.

## 3. Hypothesis

H1:
1. seeding by order-3 core plus associated order-12 bundle points outperforms baseline single-point seeding for stable motif yield.

H2:
1. 4-point bundle seeds (phase-spaced picks from one order-12 subgroup) outperform naive 4-point random seeds at equal budget.

## 4. Nulls

N1:
1. bundle seeds show no yield gain over random seeds.

N2:
1. any observed gain disappears under seed/boundary/orientation controls.

## 5. Seeding construction

For each order-12 subgroup `H`:
1. choose generator `g`,
2. compute order-3 core `c = g^4`,
3. define candidate 4-point bundle seed:
   - `{g^1, g^4, g^7, g^10}` (mod 12 step spacing),
4. place the 4 states in compact local geometry templates.

Control seeds:
1. single-point order-12 only,
2. single-point order-3 only,
3. random 4-point seeds with matched support size.

## 6. Metrics

Primary:
1. candidate-lock yield per 1k seeds,
2. propagating-candidate yield per 1k seeds,
3. median best score of top decile.

Secondary:
1. recurrence period diversity,
2. motion-class diversity,
3. post-perturbation survival rate.

## 7. Promotion gates

Gate 1:
1. bundle seeds beat random controls on candidate-lock yield with reproducible margin.

Gate 2:
1. bundle seeds maintain advantage on propagating-candidate yield or robustness metrics.

Gate 3:
1. gains survive boundary/orientation panels.

## 8. Falsifiers

Reject this lane if:
1. no reproducible yield advantage over controls,
2. gains are explained by trivial support-size effects,
3. gains collapse under panel controls.

## 9. Implementation plan

Planned scripts:
1. `cog_v3/calc/build_v3_order3_order12_bundle_seed_bank_v1.py`
2. `cog_v3/calc/build_v3_bundle_seed_vs_random_ablation_v1.py`
3. `cog_v3/calc/test_v3_bundle_seed_vs_random_ablation_v1.py`

Planned outputs:
1. `cog_v3/sources/v3_order3_order12_bundle_seed_bank_v1.csv`
2. `cog_v3/sources/v3_bundle_seed_vs_random_ablation_v1.json`
3. `cog_v3/sources/v3_bundle_seed_vs_random_ablation_v1.md`

Required fields:
1. `seed_strategy_id`
2. `seed_count`
3. `candidate_lock_yield`
4. `propagating_yield`
5. `score_distribution`
6. `panel_id`
7. `effect_size_vs_control`
8. `gate_results`

## 10. Interpretation boundary

If this lane passes:
1. it is a search-efficiency result, not a direct particle identification proof.

## 11. First-pass artifact snapshot (2026-03-03)

From `cog_v3/sources/v3_order3_order12_bundle_seed_bank_v1.json`:
1. `order12_subgroup_count = 56`
2. `unique_order3_core_count = 56`
3. `bijection_ok = true`

Status:
1. structural seed-bank construction is now implemented and validated on S960,
2. heavy ablation (`seed-budget=5000`) is running to test yield advantages against random controls.

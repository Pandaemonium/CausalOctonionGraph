# e7 Muon Ablation Prep Report

Date: 2026-02-27  
Scope: "Get ready to model e7 muon interaction and look for enhanced ablation projected along e7."

## 1. What was prepared

1. Predeclared run conditions:
   - `calc/e7_muon_ablation_conditions.json`
2. Deterministic scan runner:
   - `calc/xor_e7_muon_ablation_scan.py`
3. Test suite:
   - `calc/test_xor_e7_muon_ablation_scan.py`
4. Generated artifacts:
   - `calc/xor_e7_muon_ablation_scan.json`
   - `calc/xor_e7_muon_ablation_scan.csv`
   - `website/data/xor_e7_muon_ablation_scan.json`
   - `website/data/xor_e7_muon_ablation_scan.csv`

## 2. Metrics in this prep pass

Per depth:
1. `e7_projection_load`: sum over nodes of L1 coefficient magnitude on `e7`.
2. `e0_scalar_load`: sum over nodes of L1 coefficient magnitude on `e0`.
3. `projected_ablation_vs_baseline`: `max(0, baseline_e7_projection_load - case_e7_projection_load)`.

Baseline case:
1. `electron_electron` (used for projection subtraction).

Candidate interaction cases:
1. `muon_candidate_electron` (`su_double_12` vs `furey_electron_doubled`)
2. `tau_candidate_electron` (`su_single_1` vs `furey_electron_doubled`)

## 3. First readout

At current settings (`depth_horizon=12`, `initial_edge_distance=5`):
1. baseline `electron_electron` has e7 load 20 at depth 0, then 8 at depth 1, then 0.
2. both candidate muon/tau interactions have e7 load 12 at depth 0, then 8 at depth 1, then 0.
3. projected ablation at depth 0 is 8 for both candidate cases relative to baseline.

Interpretation:
1. the pipeline now detects and quantifies an e7-projection deficit relative to electron baseline.
2. separation between muon and tau candidates is not yet visible with this candidate mapping and horizon.

## 4. How to run

```powershell
python -m calc.xor_e7_muon_ablation_scan
pytest calc/test_xor_e7_muon_ablation_scan.py -q
```

## 5. Next tightening targets

1. lock physically motivated muon/tau motifs (replace placeholders).
2. add hand-specific scans (`left` vs `right`) for e7 projection asymmetry.
3. extend horizon and distance sweep to test whether the early-depth ablation signal persists.
4. add control-subtraction variants (vacuum-only and identity-only controls).

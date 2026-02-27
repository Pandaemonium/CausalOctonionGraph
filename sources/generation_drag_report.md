# Generation Drag Report (RFC-068 Phase A)

Date: 2026-02-27  
Artifacts:
- `calc/xor_generation_drag_metrics.json`
- `calc/xor_generation_drag_metrics.csv`
- `website/data/xor_generation_drag_metrics.json`
- `website/data/xor_generation_drag_metrics.csv`

## 1. What Was Formalized

Phase A instrumentation was implemented against the canonical full-lightcone engine:
1. deterministic full-cone update (`simulate_full_lightcone`),
2. predeclared motif mapping (`calc/generation_drag_motif_mapping.json`),
3. per-depth drag observables:
   - `S_t`: scalar load,
   - `V_t`: vacuum-channel load,
   - `M_t`: ideal misalignment load,
   - `C_t`: stabilization-work estimate,
   - `A_t`: associator exposure estimate,
   - `D_t = S_t + M_t + C_t + A_t`.

## 2. Current Outcome

With current mapping and metric definition:
1. baseline electron `MuEff = 1.0` by construction,
2. `muon_candidate` and `tau_candidate` are near baseline (~0.997),
3. per-case drag is dominated by `A_t` (associator exposure from contributor counts),
4. `M_t` and `C_t` are near zero in this run family.

Interpretation:
1. the instrumentation is valid and deterministic,
2. this first proxy does not yet produce a strong generation hierarchy signal.

## 3. Why Separation Is Weak Right Now

1. `A_t` depends mostly on cone geometry and contributor count, which is shared across cases.
2. Current stabilization metric is an estimate (`C_t := M_t`) rather than measured repair operations.
3. Candidate muon/tau mappings are placeholders, not a locked generation-motif basis.

## 4. Next Tightening Pass (Phase B+)

1. Replace estimated stabilization work with measured operation counts from an explicit stabilizer pass.
2. Split associator exposure into:
   - geometry-only exposure,
   - state-dependent non-associative activation.
3. Lock candidate generation mappings in RFC/governance before reruns.
4. Add horizon windows that de-emphasize early-depth transients.

## 5. Determinism

The suite is replay-stable:
1. fixed mapping + fixed horizon + fixed distance yields identical suite replay hash,
2. each case carries simulation replay hash for audit.

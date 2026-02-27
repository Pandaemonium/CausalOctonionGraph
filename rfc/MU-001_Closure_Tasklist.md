# MU-001 Closure Tasklist

Status: Active  
Claim: `MU-001`  
Current matrix status: `active_hypothesis`

## 1. Scope

Close MU-001 from `active_hypothesis` -> `partial` by producing a deterministic, sign-aware many-step overhead estimate with explicit uncertainty and motif contract.

This tasklist does NOT target full `supported` status.

## 2. Entry Conditions

1. Canonical claim file exists: `claims/proton_electron_ratio.yml`.
2. Matrix row exists for `MU-001`.
3. Baseline scripts/tests run:
   - `calc/mass_drag_v2.py`
   - `calc/test_mass_drag_v2.py`.

## 3. Required Deliverables

### 3.1 Motif and State Contract

1. Freeze motif definitions:
   - electron motif
   - proton motif
2. Explicitly preserve sign in state tracking (`+/-`).
3. Publish contract doc:
   - `sources/mu_motif_contract.md`.

### 3.2 Deterministic Estimator

1. Add/upgrade estimator:
   - `calc/estimate_mu_overhead.py`
2. Required outputs:
   - per-motif overhead metrics
   - ratio estimate
   - replay hash
   - horizon metadata
3. Add tests:
   - `calc/test_estimate_mu_overhead.py`
   - deterministic replay + sanity bounds.

### 3.3 Convergence and Uncertainty Report

1. Add:
   - `sources/mu_overhead_results.md`
2. Include:
   - horizon ladder (short/medium/long)
   - variance/deviation across fixed initial-condition families
   - what is and is not concluded.

## 4. Promotion Gates (`active_hypothesis` -> `partial`)

All gates must pass:

1. Determinism: identical replay hash under fixed policy.
2. Sign-sensitive behavior is explicitly tested.
3. Estimator has declared horizon and uncertainty summary.
4. Claim notes reference produced artifacts and remove placeholder-only framing.

## 5. Non-Promotion Guardrails

Do NOT move to `supported` unless all hold:

1. scale calibration is closed (`calibration_mode=calibrated`),
2. reduction/extraction policy is locked for many-body contexts,
3. uncertainty artifact is non-empty for promoted scope.

## 6. Matrix Wiring

After gate closure:

1. Update matrix row owner:
   - `owner_rfc: rfc/MU-001_Closure_Tasklist.md`
2. Ensure `battery_artifacts` includes:
   - estimator test selector
   - estimator script
   - results report.

# ALPHA-001 Closure Tasklist

Status: Active  
Claim: `ALPHA-001`  
Current matrix status: `active_hypothesis`

## 1. Scope

Close ALPHA-001 from `active_hypothesis` -> `partial` by replacing placeholder framing with a frozen, testable candidate family and explicit falsification gates.

This tasklist does NOT target full `supported` status.

## 2. Entry Conditions

1. `claims/alpha_fine_structure.yml` exists with canonical `id: ALPHA-001`.
2. Matrix row exists in `claims/CLAIM_STATUS_MATRIX.yml`.
3. Baseline constants tests pass in `calc/test_constants.py`.

## 3. Required Deliverables

### 3.1 Frozen Candidate Contract

1. Add one policy file:
   - `calc/alpha_policies.json`
2. Each candidate must include:
   - `policy_id`
   - formula definition
   - allowed inputs (discrete-only)
   - no fitted attenuation parameters
3. Candidate set must be declared before running numeric comparison.

### 3.2 Reproducible Estimator

1. Add script:
   - `calc/estimate_alpha_from_policy.py`
2. Required outputs:
   - candidate value
   - absolute/relative gap vs CODATA target
   - policy checksum
   - replay hash
3. Add tests:
   - `calc/test_alpha_policy_governance.py`
   - ensures unknown policy fails and frozen IDs are enforced.

### 3.3 Claim Artifact Bundle

1. Add source report:
   - `sources/alpha_policy_results.md`
2. Minimum contents:
   - all policy rows
   - target comparison
   - explicit "no fit" declaration
   - pass/fail summary for each row.

## 4. Promotion Gates (`active_hypothesis` -> `partial`)

All gates must pass:

1. At least one frozen policy has deterministic replay (hash-stable).
2. Governance tests pass for frozen policy IDs.
3. Report artifact exists and is referenced in claim notes.
4. Claim no longer says "no candidate formula yet identified."

## 5. Non-Promotion Guardrails

Do NOT move to `supported` unless all hold:

1. physical-units calibration mode is `calibrated`,
2. scale profile is defined (`scale_profile_id` non-empty),
3. cross-scale behavior is mechanistically derived (not numeric fit).

## 6. Matrix Wiring

After gate closure:

1. Update matrix row owner:
   - `owner_rfc: rfc/ALPHA-001_Closure_Tasklist.md`
2. Ensure `battery_artifacts` includes:
   - governance test selector
   - estimator script
   - results report.

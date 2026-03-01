# Autonomous Lab Hardening Protocol

## Purpose
Increase rigorous throughput on Standard Model parameter derivations while preserving lab culture and creativity.

## Core Policy
Every constant-derivation task must follow this order:
1. Create explicit microstate(s) where the phenomenon is relevant.
2. Apply canonical COG update rules.
3. Extract an exact UV observable from replayable traces.
4. Construct a combinatoric bridge per `cog_v2/rfc/RFC-006_Bridge_Construction_from_CxO_Combinatorics.md`.
5. Formalize in Lean and verify with replayable tests.

## Runtime Enforcement
- Duplicate task hardening: only one actionable task per `(claim_id, gate_id)` at a time; duplicates become `superseded`.
- Stale-task retirement: abandoned `active` tasks are automatically returned to `pending` for reassignment.
- Deterministic productivity precheck: weak or underspecified tasks are deferred before expensive worker cycles.
- Rigor scoring in dispatch: task ordering now favors concrete, executable closure work.
- Human-approve gate hardening: approval is blocked if pre-registration contract fields are missing.
- Run contract hardening: a run fails if required claim-declared artifacts were not actually written.
- Analysis cap: status cannot be promoted beyond the evidence quality produced by run + claim contract.
- Skeptic contract hardening: skeptic output must include decision, defects/limits, salvage, and substantive notes.
- Free-time persistence guard: if a worker does not explicitly save, the orchestrator autosaves a transcript artifact.

## Additional Contract Strictness
- Pre-registration now requires: `pre_registered_prediction`, `bridge_theorem`, valid `derivation_status`, falsification condition, and declared Lean/Python deliverables.
- Claim status promotion is capped by evidence quality; prose cannot override missing artifacts or failed runs.

## Lane Balancing
Dispatch lanes:
- `closure`: derivation and gate closure work.
- `reliability`: validators, falsification, replay robustness, regression checks.
- `culture`: educational/public artifacts, narrative quality, creative output.

Target mix per round:
- `closure`: 65%
- `reliability`: 25%
- `culture`: 10%

Free-time lane remains active to preserve culture, but closure/reliability now have explicit runtime balancing.

## Model Routing Integrity
Worker nodes must respect assigned `worker_tier` and `worker_model` from dispatch. No hidden hardcoded fallback to a single tier.

## Promotion Integrity
- `supported_bridge` requires preregistered prediction + replayable simulation + combinatoric bridge + Lean formalization.
- `proved_core` remains blocked until bridge assumptions are discharged.
- No convention laundering.

## Expected Outcome
Fewer invalid loops, fewer duplicate efforts, better gate discipline, clearer artifact quality, and a stable balance between scientific rigor and lab culture.

# RFC-007: UV Exact Closure and Bridge Applicability Boundary

Status: Active Draft  
Date: 2026-02-28  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-003_Theta_Continuum_Identification_Contract.md`
- `cog_v2/rfc/RFC-006_Bridge_Construction_from_CxO_Combinatorics.md`

## 1. Purpose

Define a strict two-regime policy:

1. **UV short-time regime**: claim evidence must be exact, tick-by-tick, non-bridged.
2. **High-time/low-frequency regime**: bridge maps are allowed only after UV exact primitives are locked.

This RFC is about epistemic discipline, not any single constant result.

## 2. Core Thesis

Under canonical v2 axioms (DAG + `C x O` unity states + projective lightcone update):

1. In finite short-time UV windows, state/event evolution is directly computable and auditable.
2. In deep-time horizons, observables become aggregate/coarse-grained and exact full-history combinatorics become non-closed in practice.
3. Therefore:
   - UV claims must be **non-bridged**.
   - bridges are a controlled inference layer for high-time observables only.

## 3. Definitions

1. `event_state_identity`: events and states are the same object at each tick (node-local state transition).
2. `uv_exact_window`:
   - fixed initial microstate,
   - fixed event order policy,
   - finite depth `D_uv`,
   - full per-tick event/state trace recorded.
3. `uv_exact_observable`: an observable computed directly from complete UV traces without map fitting.
4. `high_time_observable`: an observable requiring depth-window aggregation, asymptotic estimation, or coarse-grained identification.
5. `bridge`: preregistered map from locked discrete primitives to a target high-time observable.

## 4. UV Exact Protocol (Non-Bridged, Normative)

For any claim that is stated as UV-range:

1. Lock `init_profile_id`, `policy_id`, `kernel_profile_id`, and `event_order`.
2. Run exact tick update for each event through depth `D_uv`.
3. Emit full trace artifacts:
   - per-tick node states,
   - per-event projector output,
   - per-tick derived primitive summaries,
   - replay hash.
4. Compute UV observables directly from trace (no bridge map).
5. Replay on independent environment with identical checksum outputs.

UV claim evidence is invalid if any post-hoc map/fit is introduced.

## 5. Boundary: When Bridge Layer Becomes Admissible

Bridge use is admissible only when all hold:

1. UV primitives are already locked by exact runs.
2. Target observable is explicitly high-time/low-frequency.
3. Required statistic is not a single-tick or finite-closed UV identity.
4. A preregistered intractability statement exists, including:
   - required depth/horizon,
   - required ensemble/windowing,
   - reason exact end-to-end expression is not directly closed under current theorem/script set.

No bridge is admissible for claims that can be evaluated exactly in the declared UV window.

## 6. Bridge Constraints After Boundary Crossing

When bridge is admissible:

1. Bridge origin must be `cxo_combinatoric`.
2. Bridge may consume only UV-locked primitives and preregistered depth-binned summaries.
3. `structure_match` and `value_match` must be reported separately.
4. Bridge assumptions must be explicit and falsifiable.
5. Any map-family change resets holdout status and promotion lane.

## 7. Promotion Semantics

1. UV-labeled claims:
   - `supported_bridge` is not required for closure if exact UV derivation is complete.
   - non-bridged exact closure is the primary evidence class.
2. High-time claims:
   - may use `supported_bridge` if bridge gates pass.
   - remain blocked from `proved_core` until bridge assumptions are discharged.

## 8. Required Artifacts for UV-Exact Claims

Minimum artifact set:

1. `*_uv_exact_trace.json` (tick/event complete trace),
2. `*_uv_exact_observables.json` (direct non-bridged outputs),
3. `*_uv_exact_replay.json` (cross-run checksum equivalence),
4. `*_uv_exact_limits.md` (declared UV window and non-goals).

## 9. Immediate Implementation Tasks

1. Add `regime_label` to claim/artifact schema:
   - `uv_exact_non_bridged`,
   - `high_time_bridge`.
2. Add validator rule:
   - if `regime_label=uv_exact_non_bridged`, reject any bridge-map fields.
3. Add validator rule:
   - if `regime_label=high_time_bridge`, require intractability statement fields.
4. Add runner option to always emit per-tick per-event trace pack in UV mode.

## 10. Non-Goals

This RFC does not:

1. force all high-time claims to remain bridge-based forever,
2. claim that current bridge families are physically complete,
3. replace existing THETA-specific bridge contracts.

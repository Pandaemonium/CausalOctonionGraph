# RFC-006: Bridge Construction from CxO Combinatorics

Status: Active Draft  
Date: 2026-02-28  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-002_Event_Resolution_Modes_and_Interpretation_Layer.md`
- `cog_v2/rfc/Simulation_Selection_Guide_for_Combinatoric_Bridge_Refinement.md`
- `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
- `rfc/RFC-080_Discrete_RGE_Contract.md`

## 1. Purpose

Lock a modeling principle for v2 constant-derivation work:

1. Bridge functions should be derived from discrete combinatorics of `C x O` event dynamics.
2. Bridge claims must be auditable as combinatoric constructions, not output-fitted formulas.

This RFC does not claim any specific constant is closed. It defines bridge discipline.

## 2. Thesis

Given canonical v2 axioms (DAG + unity-state `C x O` + projective lightcone update),
the physically meaningful bridges are expected to emerge from:

1. finite event combinatorics,
2. algebraic invariants of the XOR/Fano multiplication structure,
3. deterministic aggregate statistics over preregistered runs.

## 3. Definitions

1. `combinatoric_bridge`:
   a map from preregistered event traces to a target observable using only declared
   discrete primitives and fixed aggregation rules.

2. `primitive`:
   one atomic measurable object from canonical runs, e.g.:
   - channel occupancy counts,
   - sign-balance counts,
   - orbit/stabilizer cardinalities,
   - cycle periods,
   - incidence/adjacency counts,
   - finite-depth histogram moments,
   - deterministic replay-invariant summary statistics.

3. `fit_bridge`:
   any bridge where free continuous parameters are chosen after seeing target-matching output.

## 4. Normative Policy

For promotion-grade bridge artifacts, all of the following are required:

1. `bridge_origin` must be `cxo_combinatoric`.
2. `primitive_set` must be explicitly listed.
3. `map_family_id` must be fixed before execution.
4. `free_parameter_count` must be declared and justified.
5. `posthoc_parameter_update` must be false.
6. `replay_hash` must be present and reproducible.

### 4.1 Allowed Operations

1. Integer/rational arithmetic on declared primitives.
2. Fixed finite-window deterministic statistics (mean, median, MAD, counts, ratios).
3. Predeclared linear/nonlinear maps with frozen coefficients.
4. Predeclared depth-binned coarse-graining.

### 4.2 Disallowed Operations (for claim-grade promotion)

1. Choosing map coefficients after target inspection.
2. Changing policy bundle (`policy_id`, seeds, depth schedule, bounds) based on output.
3. Mixing incompatible kernel profiles in one bridge closure.
4. Claiming bridge closure from one hand-picked seed without declared robustness lane.

## 5. Bridge Construction Workflow

1. Lock canonical runner profile and event-order policy.
2. Lock initial microstate/seed contract and horizon schedule.
3. Define primitive set and extraction code.
4. Freeze map family and acceptance tests.
5. Run deterministic campaign and emit replayable artifacts.
6. Run independent rerun + skeptic review.
7. Report `structure_match` and `value_match` separately.

## 6. Falsification Conditions

A bridge lane is falsified (or downgraded) if any hold:

1. target agreement requires post-hoc parameter retuning,
2. result fails independent rerun replay,
3. result collapses under small admissible profile perturbations,
4. primitive definitions are changed without resetting claim state.

## 7. Promotion Gates (Bridge Layer)

`partial -> supported_bridge` requires:

1. combinatoric provenance fields complete,
2. deterministic replay check pass,
3. holdout or independent rerun check pass,
4. skeptic report confirms no hidden fitting,
5. bridge assumptions/falsification condition are explicit in claim YAML.

`supported_bridge -> proved_core` additionally requires:

1. all bridge assumptions discharged or proven unnecessary,
2. theorem-level identification of map to target observable,
3. no unresolved policy-waiver blocks.

## 8. Parameter-Lane Guidance

1. `THETA-001`:
   keep CP/sign combinatoric lane primary; continuum identification remains explicit bridge work.
2. `WEINBERG-001`:
   enforce one discrete-RGE policy bundle; no policy-shopping across seeds/horizons.
3. `STRONG-001`:
   treat scale-running bridge as separate combinatoric map closure task.
4. Mass lanes:
   freeze mass observable and anchor policy before absolute claims.

## 9. Immediate Implementation Tasks

1. Add bridge provenance fields to claim/artifact validators.
2. Fail promotion when `posthoc_parameter_update=true`.
3. Require map-family checksum in bridge artifacts.
4. Add explicit `structure_match` / `value_match` outputs in campaign reports.

## 10. Non-Goals

This RFC does not:

1. force all future successful bridges to be linear,
2. decide any specific scale calibration convention,
3. guarantee any constant will close under the first map family attempted.

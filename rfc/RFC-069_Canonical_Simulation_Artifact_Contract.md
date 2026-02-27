# RFC-069: Canonical Simulation Artifact Contract (Full Light Cone + Update Rule + User-Defined Observables)

Status: Active Draft - Policy Lock Candidate (2026-02-27)
Module:
- `COG.Sim.ArtifactContract`
- `COG.Sim.ObservableInterface`
Depends on:
- `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-035_Distance_as_Next_Interaction_Node_Gap.md`
- `rfc/RFC-063_XOR_Octonion_Gate_and_Signed_Handed_Dynamics.md`
- `rfc/RFC-064_Superdeterminism_and_Lightcone_Information_Volume.md`

---

## 1. Executive Summary

This RFC locks the public simulation contract for the COG program.

Every simulation artifact has exactly two core ingredients:
1. a fully specified superdetermined `C x O` lightcone microstate,
2. a deterministic update rule.

Everything else is an observable layer.

A user can define any observable they want, but it must be declared as an explicit macro-measurement rule over microstates. This keeps physics claims reproducible and separable from interpretation.

Project deliverables are executable Python and formal Lean code so any external user can run, audit, or challenge results.

---

## 2. Policy Lock

### 2.1 Canonical simulation form (mandatory)

A conforming simulation MUST provide:
1. `initial_lightcone_state` (full predetermined microstate in canonical schema),
2. `update_rule` (deterministic transition definition),
3. `observable_spec` (declared measurement mapping).

No simulation may omit (1) or (2).

### 2.2 No hidden dynamics

A conforming artifact MUST NOT use hidden randomness, hidden wall-clock input, or undocumented exogenous state.

### 2.3 Public executability

A conforming artifact MUST ship:
1. Python runner(s),
2. Lean spec/theorem links (and proof status),
3. machine-readable config files.

---

## 3. Canonical Data Contract

### 3.1 `initial_lightcone_state`

Required fields:
1. `schema_version`
2. `microstate_id`
3. `topology` (nodes, edges, depths)
4. `node_states` (`C x O` coefficients in canonical basis)
5. `boundary_conditions` (explicitly declared and deterministic)
6. `time_zero_depth`
7. `provenance` (generator script, commit hash, date)

Interpretation:
1. This is the full superdetermined lightcone snapshot for the run.
2. It is not a partial seed that relies on later random completion.

### 3.2 `update_rule`

Required fields:
1. `rule_id`
2. `python_impl_path`
3. `lean_spec_path`
4. `determinism_contract` (named laws)
5. `canonical_ordering` (message/order semantics)
6. `hash` (content hash of the rule bundle)

Interpretation:
1. Same input state + same rule + same horizon MUST replay identically.

### 3.3 `observable_spec`

Required fields:
1. `observable_id`
2. `macrostate_name`
3. `event_predicate` (microstate -> Bool, or equivalent explicit rule)
4. `aggregation_rule` (how event-level data becomes reported value)
5. `units_in_graph_terms` (edge count, depth count, phase class, etc.)
6. `controls` (if subtraction/baseline controls are applied)

Interpretation:
1. Physically, an "observation" is a user-declared macrostate event rule over microstates.
2. Different observables can be run on the same simulation without changing dynamics.

---

## 4. Observable Semantics (Locked)

This RFC adopts the following semantics:
1. Microphysics is the deterministic evolution of the full lightcone state under the update rule.
2. Observable physics is a projection/selection rule on that evolution.
3. A macro-claim is valid only when its observable rule is declared and replayable.

Equivalent statement:
1. "What was measured" is part of the claim contract, not an afterthought.

---

## 5. Constant-Derivation Packaging Standard

Any claim to derive a physical constant MUST ship a package with:
1. canonical `initial_lightcone_state`,
2. canonical `update_rule`,
3. one or more `observable_spec` files,
4. runnable Python command(s),
5. Lean reference(s) for the underlying rule semantics,
6. reproducibility report (input hashes, output hashes, runtime metadata).

Recommended package layout:
1. `simulations/<constant_id>/initial_lightcone_state.json`
2. `simulations/<constant_id>/update_rule.json`
3. `simulations/<constant_id>/observable_*.json`
4. `simulations/<constant_id>/run.py`
5. `simulations/<constant_id>/README.md`
6. `simulations/<constant_id>/repro_report.json`

---

## 6. Computational Reality and Public Communication

The project explicitly acknowledges:
1. physically faithful large-scale runs may require extreme compute because Planck-scale discretization is far below human scales,
2. this does not alter the contract,
3. downscaled demonstrations are allowed only when clearly labeled as scale-limited validation runs.

Public-facing requirement:
1. every published result MUST state whether it is a full-scale run, reduced-scale run, or extrapolated estimate.

---

## 7. Verification Gates

A simulation artifact passes this RFC only if all gates pass:
1. **Schema gate**: all required fields present and valid.
2. **Determinism gate**: replay hash stable across repeated runs.
3. **Transparency gate**: no hidden inputs outside declared files.
4. **Observable gate**: macro claim references explicit observable spec.
5. **Portability gate**: independent user can run Python artifacts from docs.
6. **Formal linkage gate**: Lean rule/spec references resolve to existing files/theorems.

---

## 8. Immediate Implementation Tasks

1. Add a simulation artifact schema validator (`calc/validate_sim_artifact.py`).
2. Add canonical template files under `simulations/templates/`.
3. Add CI checks for determinism replay hash and observable-spec presence.
4. Require new constant claims to include a simulation package matching Section 5.
5. Add a short public explainer page: "Same universe, different observables."

---

## 9. Non-Goals

This RFC does not:
1. choose one privileged observable for all physics,
2. assert specific numerical values for constants,
3. replace existing physics RFCs for individual mechanisms.

It only standardizes the simulation contract so those mechanism RFCs can be tested consistently.

---

## 10. Decision Record

Locked by this RFC:
1. all COG simulations use the same base form: full superdetermined lightcone + deterministic update rule,
2. observables are explicitly user-defined macrostate event rules over microstates,
3. deliverables are Python + Lean artifacts intended for independent execution and audit.

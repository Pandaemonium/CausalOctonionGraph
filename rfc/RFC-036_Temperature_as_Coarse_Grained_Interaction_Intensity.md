# RFC-036: Temperature as Coarse-Grained Interaction Intensity

**Status:** Active - Draft (2026-02-26)  
**Module:** `COG.Theory.Temperature`  
**Depends on:** `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`, `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`, `rfc/RFC-028_Canonical_Update_Rule_Closure.md`, `rfc/RFC-035_Distance_as_Next_Interaction_Node_Gap.md`

---

## 1. Executive Summary

This RFC defines temperature in COG as an observer-level, coarse-grained quantity derived from interaction activity, not as a primitive microstate field.

Core statement:

1. Microstate evolution remains deterministic and zero-entropy from the omniscient viewpoint.
2. Temperature is an observable over regions and time windows.
3. The primary temperature proxy is normalized energy-exchange event density.

Primary observable:

`T_proxy(R, W) = (1 / (|R| * |W|)) * sum_{t in W} sum_{v in R} I_energy(v, t)`

where `I_energy(v,t) = 1` iff `isEnergyExchangeLocked(msgs_v(t)) = true`, else `0`.

---

## 2. Motivation

COG already defines:

1. deterministic local update,
2. energy-exchange predicate (`isEnergyExchangeLocked`),
3. topological and interaction clocks (`tau_topo`, `tau_int`).

What is missing is a thermodynamic bridge: a reproducible mapping from micro-dynamics to "hot/cold" behavior in simulations and claims.

---

## 3. Definition Layer

Let:

1. `R` be a finite set of node IDs (region),
2. `W = {t0, ..., t0+Delta-1}` be a finite tick window.

Define local indicator:

`I_energy(v, t) in {0,1}`.

Define regional activity density:

`A(R, W) = (1 / (|R| * Delta)) * sum I_energy(v, t)`.

Define canonical temperature proxy:

`T_proxy(R, W) := A(R, W)`.

Interpretation:

1. `T_proxy = 0` means no active exchange events in the window.
2. Larger `T_proxy` means denser interaction processing in that region.

Units:

1. Dimensionless in this draft.
2. Physical calibration to Kelvin is explicitly out of scope for this RFC.

---

## 4. Relation to Energy and Entropy

This RFC keeps a strict separation:

1. **Kernel level:** deterministic, no exogenous randomness.
2. **Observer level:** coarse-grained temperature and entropy-like summaries.

Temperature here is not defined as a fundamental field attached to each node.  
It is a statistic over update events.

Optional extension (not locked in this RFC):

1. effective energy `E_eff(R,W)` from weighted interaction counts,
2. observational entropy `S_obs` from projection fibers (`Pi_obs`),
3. thermodynamic-style parameter `beta_eff = dS_obs / dE_eff`.

These remain future work to avoid premature overfitting.

---

## 5. Connection to Distance and Dynamics

Using RFC-035 distance-gap semantics:

1. high `T_proxy` regions are expected to show larger short-window fluctuations in `d_next`,
2. low `T_proxy` regions should preserve smoother pair-gap evolution.

This is a testable prediction, not yet a theorem.

---

## 6. Invariants and Requirements

Any conforming implementation must satisfy:

1. `0 <= T_proxy(R,W) <= 1`.
2. Determinism under replay: identical initial microstate and scheduler produce identical `T_proxy` traces.
3. No dependence on wall-clock or RNG.
4. Region/window explicitness: every reported temperature value must specify `(R, W)`.

---

## 7. Open Decisions

### TEMP-1. Event weighting policy

Do all energy-exchange events contribute equally, or do we weight by interaction payload class?

Draft default:

1. uniform weight = 1 for each `I_energy = 1`.

### TEMP-2. Region policy

How regions are selected:

1. fixed node-ID sets,
2. causal subgraph neighborhoods,
3. moving windows tied to particle motifs.

### TEMP-3. Window policy

Whether `W` is:

1. fixed-length sliding window, or
2. event-count window (next N interactions).

---

## 8. Implementation Plan

### 8.1 Python

Add:

1. `calc/temperature_proxy_scan.py`
2. `calc/test_temperature_proxy_scan.py`

Minimum outputs:

1. `T_proxy` time series for selected regions,
2. replay-determinism hash checks,
3. comparison plots/tables of `T_proxy` against `d_next` volatility (RFC-035 toy mode).

### 8.2 Lean scaffold

Add:

1. `CausalGraphTheory/TemperatureProxy.lean`

Initial targets:

1. definition of `I_energy` and `T_proxy` over finite lists,
2. boundedness theorem (`0 <= T_proxy <= 1` in rational form),
3. determinism theorem inherited from deterministic update assumptions.

---

## 9. Claim Governance Impact

Until this RFC is implemented:

1. "temperature" language in claims remains interpretive,
2. any thermal statement must be labeled as proxy-level, not fundamental,
3. no Kelvin calibration claims are allowed.

---

## 10. Acceptance Criteria

This RFC is considered closed when:

1. Python `T_proxy` module and tests pass in CI,
2. replay determinism for `T_proxy` is demonstrated on at least two benchmark motifs,
3. Lean scaffold definitions and boundedness theorem are merged,
4. one claim file references `T_proxy` with explicit `(R,W)` provenance.


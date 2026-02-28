# RFC-008: Layered Causality and Defect Falsification Contract

Status: Active  
Date: 2026-02-28  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-002_Event_Resolution_Modes_and_Interpretation_Layer.md`

## 1. Purpose

Lock strict layered causality as the canonical v2 default and define a
falsification lane for possible topological-defect alternatives.

This RFC separates:

1. canonical production geometry (strict layered DAG),
2. controlled defect experiments (non-canonical lane).

## 2. Canonical Layered Causality Decision

For canonical v2 runs, the DAG is **strictly layered**:

1. each node has integer depth `d in N`,
2. each edge must satisfy `depth(dst) = depth(src) + 1`,
3. no transitive shortcut edges are included in primitive update graphs.

Consequence:

1. for any comparable pair `(A,B)`, causal edge count is unique,
2. all directed `A -> B` paths have the same length `depth(B) - depth(A)`.

## 3. Defect Definitions

Let `(A,B)` be a reachable ordered pair.

1. `Lmin(A,B)`: shortest directed path length,
2. `Lmax(A,B)`: longest directed path length,
3. `Delta(A,B) := Lmax(A,B) - Lmin(A,B)`.

Interpretation:

1. `Delta = 0`: no path-length spread,
2. `Delta > 0`: multi-length causal chain (defect candidate).

Defect candidate classes:

1. **shortcut defect**: edge violates strict layer step,
2. **delay defect**: alternate longer route coexists with shorter route,
3. **mixed-lane defect**: topology merges data from incompatible layer rules.

## 4. Canonical Acceptance Rule

Canonical run acceptance requires:

1. acyclic graph (`is_dag = true`),
2. zero layer violations,
3. `max_delta = 0` on sampled/covered reachable pairs.

If any fail, run must be labeled non-canonical.

## 5. Falsification Lane (non-canonical by design)

Defect exploration is allowed only in explicit defect runs:

1. inject controlled violations (`skip edge`, `delay edge`, or both),
2. report defect metrics (`Delta`, defect density, affected pair set),
3. compare against canonical run on same initialization and observables.

Required labeling:

1. `causality_mode = layered_strict_v1` for canonical,
2. `causality_mode = layered_defect_probe_v1` for defect lane.

## 6. Physical Manifestation Hypotheses

If real defects are needed physically, expected signatures include:

1. causal-delay sidebands (same endpoint pair reached with `n` and `n+1` ticks),
2. motif clock splitting/beat patterns from mixed transport lengths,
3. persistent phase-slip pockets tied to positive `Delta` regions.

These are hypotheses only and must be preregistered per claim.

## 7. Tooling and Proof Requirements

### 7.1 Python validator

Script:

1. `cog_v2/scripts/validate_layered_causality_v1.py`

Minimum outputs:

1. DAG check,
2. layer-violation list/count,
3. sampled pair-count, defect pair-count, `max_delta`,
4. canonical verdict (`pass` / `fail`),
5. optional defect-case examples.

### 7.2 Lean theorem lane

Module:

1. `cog_v2/lean/CausalGraphV2/LayeredCausality.lean`

Required theorem shape:

1. under layered-edge axiom, any two directed paths between same endpoints have equal length.

## 8. Non-Goals

This RFC does not:

1. claim defects are physically required,
2. replace canonical strict layering,
3. assert continuum phenomenology from defect probes without separate bridge contracts.


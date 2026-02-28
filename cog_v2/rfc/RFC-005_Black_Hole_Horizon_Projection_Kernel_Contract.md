# RFC-005: Black-Hole and Horizon Contract under Projective Unity Kernel

Status: Active  
Date: 2026-02-28  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-002_Event_Resolution_Modes_and_Interpretation_Layer.md`

## 1. Purpose

Define black-hole and horizon semantics directly in the v2 canonical model:

1. DAG state graph,
2. `C x O` over unity (`{0, +/-1, +/-i}`),
3. projective lightcone update rule.

This RFC is structure-first: it defines graph-theoretic objects and deterministic falsification tests under the canonical projection kernel.

## 2. Definitions (normative)

Given directed graph `G = (V, E)` with edge direction `u -> v`:

1. `B subset V` is a black-hole candidate region.
2. `B` is a black-hole region iff:
   - for every edge `(u -> v)` in `E`, if `u in B` then `v in B`.
   - equivalently: there are no outgoing edges from `B` to `V \ B`.
3. Horizon `H(B)` is:
   - `H(B) = { v in B | exists u in V \ B such that (u -> v) in E }`.
4. Exterior is `X = V \ B`.

Interpretation:
1. Black-hole region is a one-way causal sink.
2. Horizon is the ingress boundary where exterior influence enters interior.

## 3. Kernel-Consistent Dynamic Semantics

Under `cog_v2/python/kernel_projective_unity.py`:

1. State update at each node uses parent messages only.
2. Therefore, if no interior node is parent of any exterior node, interior states cannot influence exterior states.
3. Because projection is idempotent and unity-closing, all states remain bounded in unity alphabet for all ticks.

## 4. Falsification Tests (required)

Artifact builder:
- `cog_v2/calc/build_blackhole_projection_contract_v1.py`

Artifacts:
- `cog_v2/sources/blackhole_projection_contract_v1.json`
- `cog_v2/sources/blackhole_projection_contract_v1.md`

### T1. Topological One-Way Isolation

Condition:
1. Outgoing-crossing edge count from `B` to exterior equals `0`.

Falsify if:
1. any edge `(u -> v)` exists with `u in B` and `v in X`.

### T2. Horizon Ingress Non-Emptiness

Condition:
1. `H(B)` is non-empty.
2. each `h in H(B)` has at least one parent in exterior.

Falsify if:
1. `H(B)` is empty or malformed relative to parent map.

### T3. Exterior Independence from Interior Initialization

Condition:
1. Run two worlds with identical exterior initial states, different interior initial states.
2. For all ticks in a preregistered window, exterior trajectories are exactly equal.

Falsify if:
1. any exterior node differs at any tick.

### T4. Exterior-to-Interior Influence Exists

Condition:
1. Run two worlds with identical interior initial states, different exterior initial states.
2. At least one interior node differs at some tick.

Falsify if:
1. interior never responds; this indicates no causal ingress path from exterior.

### T5. Boundedness under Dense Interior

Condition:
1. Run finite horizon over dense interior connectivity.
2. Every coefficient at every node/tick remains in unity alphabet.

Falsify if:
1. any coefficient escapes unity alphabet.

## 5. Acceptance Contract

`blackhole_contract_pass = T1 and T2 and T3 and T4 and T5`.

This acceptance is structure-first only. It does not claim:
1. GR-equivalent metric reconstruction,
2. Hawking spectrum derivation,
3. astrophysical black-hole phenomenology closure.

## 6. Non-Goals

This RFC does not:
1. define spawn/topology-growth cosmology,
2. derive continuum Einstein dynamics,
3. resolve full strong-gravity EFT matching.

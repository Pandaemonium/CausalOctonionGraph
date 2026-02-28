# RFC-001: Canonical Axiom Profile for COG v2

Status: Active  
Date: 2026-02-28  
Owner: COG Core

Interpretation/Resolution Extension:
- `cog_v2/rfc/RFC-002_Event_Resolution_Modes_and_Interpretation_Layer.md`
- `cog_v2/rfc/RFC-003_Theta_Continuum_Identification_Contract.md`
- `cog_v2/rfc/RFC-004_Triplet_Coherence_and_e000_Leakage_Hypothesis.md`
- `cog_v2/rfc/RFC-005_Black_Hole_Horizon_Projection_Kernel_Contract.md`
- `cog_v2/rfc/RFC-006_Bridge_Construction_from_CxO_Combinatorics.md`
- `cog_v2/rfc/RFC-007_UV_Exact_Closure_and_Bridge_Applicability_Boundary.md`
- `cog_v2/rfc/RFC-008_Layered_Causality_and_Defect_Falsification_Contract.md`
- `cog_v2/rfc/RFC-009_F2^3_Index_Geometry_and_Unique_Causal_Length.md`
- `cog_v2/rfc/RFC-010_Octonion_Cube_Phase_Fiber_and_Fano_Orientation.md`
- `cog_v2/rfc/Targeted_Branching_Policy_for_Computational_Efficiency_and_Statistical_Integrity.md`

## 1. Decision

COG v2 adopts a single canonical model:

1. Spacetime is a directed acyclic graph (DAG).
2. Each node carries a `C x O` state over a unity alphabet.
3. Node evolution is a deterministic projection update over the incoming light cone.
4. Canonical geometry is strictly layered (`depth(dst) = depth(src) + 1` for every edge).

This RFC is the source-of-truth profile for all new work under `cog_v2/`.

## 2. Canonical State Contract

Each node state is an 8-slot `C x O` tuple with Gaussian-integer coefficients.

Canonical basis labels (index-locked):

1. `e000` (scalar/identity channel)
2. `e001`
3. `e010`
4. `e011`
5. `e100`
6. `e101`
7. `e110`
8. `e111` (vacuum-sign channel in current THETA probes)

Alias policy:

1. v2 documentation and code use binary labels (`e000..e111`) as canonical names.
2. legacy `e0..e7` aliases are not normative in `cog_v2/`.

Allowed canonical coefficients:

- `0`
- `+1`
- `-1`
- `+i`
- `-i`

Input policy:

- Default: strict (`reject` non-unity coefficients).
- Compatibility mode: allow non-unity input only by deterministic projection into unity alphabet.

## 3. Canonical Update Rule

For node `n` with current state `s_n` and parent states `P_n`:

1. `payload_raw = fold(parent_states)` using fixed Fano multiplication.
   - Runtime index channel is XOR for distinct imaginary basis pairs:
     `k = i xor j` with orientation-sign table.
2. `payload = Pi(payload_raw)` where `Pi` is deterministic unity projection.
3. `s'_n = Pi(payload * s_n)`.

`Pi` must be idempotent (`Pi(Pi(x)) = Pi(x)`) and replay-deterministic.

## 4. Event Ordering Contract

Update execution order must be deterministic and pre-registered when provided:

- If `event_order` exists in input, use it exactly.
- Else use canonical fallback `sorted(node_ids)`.

This isolates order effects and preserves reproducibility.

Note:
- RFC-001 defines the deterministic baseline required for claim-grade replay.
- RFC-002 adds optional interpretation-layer resolution modes (stochastic and branching)
  without changing the base dynamics defined here.

## 5. Validation Requirements

Any canonical kernel must pass:

1. projector idempotence checks,
2. closure under unity alphabet after every update,
3. deterministic replay equivalence,
4. strict-input rejection behavior,
5. explicit kernel metadata (`kernel_profile`, `projector_id`) in outputs.

## 6. Migration Rule

No existing legacy path is deleted by this RFC.
Migration is lane-based:

1. copy minimal artifact into `cog_v2`,
2. enforce canonical profile requirements,
3. re-run tests/proofs under v2,
4. register migration state in `migration/migration_manifest.yaml`.

## 7. Non-Goals (for this RFC)

This RFC does not claim:

- continuum EFT closure,
- complete physical interpretation of mass/gravity,
- full Standard Model parameter derivations.

Those remain separate claims gated by v2 contracts.

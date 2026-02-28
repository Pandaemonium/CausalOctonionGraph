# RFC-001: Canonical Axiom Profile for COG v2

Status: Active  
Date: 2026-02-28  
Owner: COG Core

Interpretation/Resolution Extension:
- `cog_v2/rfc/RFC-002_Event_Resolution_Modes_and_Interpretation_Layer.md`
- `cog_v2/rfc/RFC-003_Theta_Continuum_Identification_Contract.md`
- `cog_v2/rfc/RFC-004_Triplet_Coherence_and_e0_Leakage_Hypothesis.md`
- `cog_v2/rfc/Targeted_Branching_Policy_for_Computational_Efficiency_and_Statistical_Integrity.md`

## 1. Decision

COG v2 adopts a single canonical model:

1. Spacetime is a directed acyclic graph (DAG).
2. Each node carries a `C x O` state over a unity alphabet.
3. Node evolution is a deterministic projection update over the incoming light cone.

This RFC is the source-of-truth profile for all new work under `cog_v2/`.

## 2. Canonical State Contract

Each node state is an 8-slot `C x O` tuple with Gaussian-integer coefficients.

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

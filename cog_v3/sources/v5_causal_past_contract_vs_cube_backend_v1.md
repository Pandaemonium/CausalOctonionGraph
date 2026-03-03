# v5 Causal Past Contract vs Cube Backend (v1)

Date: 2026-03-03

## Why this split exists

We separate:

1. **Kernel contract** (foundational):  
   "Given complete causal past, deterministic fold+multiply gives the target state."

2. **Retrieval mechanism** (supplementary):  
   "How do we obtain that complete causal past in practice?"

This prevents over-committing to a specific geometry too early.

## Kernel contract (geometry-agnostic)

Required for correctness:
- complete causal contributors are included,
- fold order is deterministic,
- multiplication law is fixed,
- coherence/path-independence check is applied.

Not required:
- any specific chart such as `(x,y,z)` coordinates,
- any specific neighbor graph.

## Current bundled backend

`F2^3` cube backend:
- 8 nodes,
- XOR one-bit edges,
- path enumeration + parity/distance reachability filters.

Module:
- `cog_v3/python/causal_past_contract_v1.py`
  - `CausalPastProvider` (interface)
  - `F2CubePastProvider` (current implementation)

## Research implication

Koide and symmetry claims should be tied to kernel invariants and extraction
maps, not to cube-specific artifacts unless explicitly stated as backend-dependent.

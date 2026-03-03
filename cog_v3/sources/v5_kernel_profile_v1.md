# v5 Kernel Profile (v1)

Profile id: `cog_v5_coherent_lightcone_fold_v1`

## Purpose

Freeze a clean, reproducible kernel lane for external communication and proof linking.

## Core semantics

1. Coherent lightcone (non-Markov)
- A configuration is physical iff path products to each lightcone point agree.

2. Algebra
- Site state channels: `Z3` (domain), `Z4` (energy phase), octonionic `(sign,basis)`, and integer `E >= 0`.

3. Geometry
- Lattice: `F2^3` (8 sites), causal edges by XOR one-bit flips.

4. Update
- Ordered path-product fold along causal paths.

## Contract vs backend separation

Core contract (axiomatic):
- Kernel consumes the **complete causal past** of each target and applies a
  deterministic fold+multiply rule.
- Physicality is path-independence/coherence.

Supplementary implementation (current):
- Causal-past retrieval backend is `F2^3` cube/XOR geometry.
- This is one backend, not a foundational axiom of the kernel contract.

Backend contract module:
- `cog_v3/python/causal_past_contract_v1.py`
- Provides a backend-agnostic interface plus:
  - `F2CubePastProvider` (dense baseline),
  - `SparseCausalBackend` (vacuum-identity sparse path backend).

## Runtime files

- Kernel API: `cog_v3/python/kernel_cog_v5_coherence.py`
- Canonical engine: `cog_v3/python/engine_canonical_v5.py`
- Smoke builder: `cog_v3/calc/build_v5_canonical_engine_smoke_v1.py`
- Smoke artifact: `cog_v3/sources/v5_canonical_engine_smoke_v1.md`

## Formal linkage

- Lightcone locality/determinism lemmas: `CausalGraphTheory/KernelV4Lightcone.lean`
- Koide conditional bridge package: `CausalGraphTheory/KoideFromKernelV5.lean`

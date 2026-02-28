# Lean Port Status (v2)

## Scope

Initial v2 proof lane ports only:

- `CausalGraphV2/Fano.lean`
- `CausalGraphV2/FanoMul.lean`
- `CausalGraphV2/ThetaQCD.lean`
- `CausalGraphV2/ThetaEFTBridge.lean`
- `CausalGraphV2/TripletDecayExact.lean`

## Current State

- Package scaffold created (`lakefile.toml`, `lean-toolchain`, root imports).
- Minimal algebra and THETA witness modules copied and namespace-adjusted.
- Continuum bridge theorem lane added (`ThetaEFTBridge`) with:
  - `discreteCpResidual_zero`
  - `theta_zero_if_direct_bridge`
  - `theta_zero_if_linear_bridge`
  - `theta_zero_if_affine_bridge`
- Additional generic bridge theorem added:
  - `theta_zero_if_zero_anchored_bridge`
- Exact dynamic witness lane added (`TripletDecayExact`) with:
  - exact integer predicate formalization for
    - `offMotif`
    - `vacuumCoupled`
    - `daughterChannelsPresent`
    - `decayActive`
  - explicit theorem-level replay witnesses from
    `triplet_decay_exact_simulation_v1.json`
  - contract theorem `tripletDecayExactWitnessContract_v1`
- Full theorem parity with legacy tree is not yet complete.
- Lean v2 build is now green in this environment:
  - `cd cog_v2/lean && lake build` (14 jobs succeeded)
- THETA v2 claim lane status:
  - gate_1: done (Lean lane compiled),
  - gate_2: done (Python witness/tests),
  - gate_3: done with `PASS_WITH_LIMITS` skeptic artifact.

## Next Ports

1. `KernelV2`-compatible update rule formalization under canonical unity projector assumptions.
2. Move THETA-001 from structure-first bridge support toward full EFT value closure.
3. Optional: add theorem lane for periodic-angle bridge map if promoted from stub.

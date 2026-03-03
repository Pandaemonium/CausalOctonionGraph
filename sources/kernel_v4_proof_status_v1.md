# Kernel v4 Proof Status (v1)

Date: 2026-03-03

## What is now formally proved

File: `CausalGraphTheory/KernelV4Lightcone.lean`

1. `projectedCone_is_past`
- Every contributor used by `projectedCone` is strictly in the past (`ts.1 < t`).
- This is the formal causal-locality guarantee from the kernel spec.

2. `statesOnCone_ext`
- If two histories agree on all timed sites in a cone, the extracted cone state lists are equal.

3. `updateAt_history_ext_on_projectedCone`
- `updateAt` is fully determined by history values on the projected cone only.
- No off-cone data can change the result.

4. `updateAt_history_ext_on_all_past`
- Stronger locality form: agreement on all strictly-past sites implies equal updates.

5. `backProjectedSupport_congr`
- Back-projected support is deterministic under equal measurement input `(t, observed)`.

Build check:
- `lake build CausalGraphTheory.KernelV4Lightcone` passes.

## Runtime check (engine lane)

File: `cog_v3/sources/v3_canonical_engine_smoke_v1.md`

- Engine profile: `cog_v4_coherent_lightcone_fold_v1`
- Result: `physical=True`, `violation=None` (smoke horizon 2).

## What is still not proved

1. Real-world correctness
- Lean proofs above are internal model theorems (determinism/causality/locality), not experimental validation.

2. Path-independence universality over broad seed classes
- Current runtime smoke is a narrow instance; broader exhaustive/contract sweeps still needed.

3. Kernel-to-phenomenology bridge
- Claims linking this kernel to full particle spectrum, exact masses, and full SM observables remain hypothesis+test programs.

## Bottom line

We now have a real proof artifact for the kernel's formal structure:
- causal past-only dependency,
- update locality,
- deterministic back-projection semantics.

This upgrades the kernel from "idea" to "formally constrained object."

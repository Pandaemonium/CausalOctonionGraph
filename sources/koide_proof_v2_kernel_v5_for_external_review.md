# Koide Proof Package (v2, Kernel v5)

Date: 2026-03-03  
Audience: external technical review

## Executive Summary

This repository now contains a formally checked Koide proof package with a clean separation between:

1. **pure algebraic theorems** (fully proved in Lean), and  
2. **kernel-to-physics bridge assumptions** (explicitly stated, no hidden fitting).

The result is logically bulletproof in this form:

- **If** the v5 kernel yields the listed Z3/Brannen constraints,  
- **then** the Koide equation follows exactly.

No numerical fitting constants are inserted in the proof chain.

## Kernel v5 used

Profile: `cog_v5_coherent_lightcone_fold_v1`  
Code: `cog_v3/python/kernel_cog_v5_coherence.py`

Semantics:

- state algebra per site: `Z3 x Z4 x O x Z_{>=0}` channels implemented as `(g, a, basis, sign, e)`,
- causal-input contract: kernel assumes complete causal past is provided for each target,
- supplementary backend (current): `F2^3` with XOR-adjacent paths,
- update law: ordered path-product fold,
- physicality criterion: path independence on the lightcone.

Smoke artifact:

- `cog_v3/sources/v5_canonical_engine_smoke_v1.md`

## Formal theorem chain (Lean)

### A) Algebraic Koide equivalence

File: `CausalGraphTheory/Koide.lean`  
Theorem: `koide_algebraic_iff`

\[
3(f_0^2+f_1^2+f_2^2)=2(f_0+f_1+f_2)^2
\iff
f_0^2+f_1^2+f_2^2=4(f_0f_1+f_1f_2+f_2f_0).
\]

This is exact algebra, independent of model details.

### B) Z3/Brannen bridge

Files:

- `CausalGraphTheory/Koide.lean` (`brannen_b_squared`)
- `CausalGraphTheory/KoideGroupBridge.lean` (`brannen_sos_from_z3_and_b2`, `brannen_koide_from_z3_and_b2`)

Given Brannen-form frequencies and Z3 identities plus \(B^2=2\), Koide follows exactly.

### C) Kernel-v5 packaged theorem

File: `CausalGraphTheory/KoideFromKernelV5.lean`

New theorem package:

- `KernelV5KoideAxioms` (explicit assumptions),
- `sos_from_kernel_v5_axioms`,
- `koide_equation_from_kernel_v5_axioms`.

Main statement:

If `KernelV5KoideAxioms` hold, then

\[
3(f_0^2+f_1^2+f_2^2)=2(f_0+f_1+f_2)^2.
\]

This theorem compiles with:

```bash
lake build CausalGraphTheory.KoideFromKernelV5
```

## Exact assumptions (explicit boundary)

The v5 bridge theorem assumes:

1. Z3 sum identity: \(c_0+c_1+c_2=0\),
2. Z3 pair-product identity: \(c_0c_1+c_1c_2+c_2c_0=-3/4\),
3. amplitude condition: \(B^2=2\),
4. Brannen-form frequencies:
   \[
   f_k = A(1 + B c_k), \quad k\in\{0,1,2\}.
   \]

These are transparent assumptions, not hidden constants.

## What is proved vs not yet proved

### Proved now

- The full algebraic Koide implication chain in Lean.
- A clean theorem that maps explicit kernel assumptions to Koide exactly.

### Not yet proved from dynamics

- That v5 kernel dynamics *force* all four assumptions above for physical charged-lepton motifs.

This is an open derivation task, not a logical gap in the proven chain.

## Why this is robust

- Every implication in the theorem chain is machine-checked.
- Assumptions are enumerated and auditable.
- The proof avoids real-analysis approximations and avoids numerical fitting.

## Minimal external claim (safe wording)

"We have a machine-checked theorem chain showing that if the v5 coherent-lightcone kernel produces the explicit Z3/Brannen constraints, then Koide follows exactly. The remaining work is to derive those constraints directly from motif dynamics in the kernel."

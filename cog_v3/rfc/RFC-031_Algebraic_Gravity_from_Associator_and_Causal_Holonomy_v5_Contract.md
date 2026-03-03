# RFC-031: Algebraic Gravity from Associator and Causal Holonomy (v5 Contract)

Status: Draft  
Date: 2026-03-03  
Owner: COG Core  
Depends on:
- `cog_v3/sources/v5_kernel_profile_v1.md`
- `cog_v3/sources/v5_causal_past_contract_vs_cube_backend_v1.md`
- `cog_v3/rfc/RFC-012_Associator_Field_Curvature_and_Family_Activity_Test_Contract.md`
- `cog_v3/python/kernel_cog_v5_coherence.py`

## 1) Purpose

Formalize a strict "no added gravity field" lane:

1. gravity-like behavior must arise from algebraic observables already present in the kernel,  
2. causal structure is updated by the existing kernel contract (complete causal past + deterministic fold),  
3. curvature proxies are extracted from nonassociativity and loop transport, not inserted externally.

## 2) Core stance

We do **not** add a separate gravitational field variable.

All gravity candidates must be derived from:

1. state algebra (`Z3 x Z4 x O x Z>=0`),  
2. causal-past transport/fold,  
3. invariants of nonassociative composition.

## 3) Definitions

Let `*` be the v5 state multiplication.

1. Associator indicator
   - `Assoc(a,b,c) = 1` iff `(a*b)*c != a*(b*c)`, else `0`.

2. Local associator density
   - `A_local(x,t)` = average `Assoc` over selected local contributor triples at site `x`, tick `t`.

3. Associator shell profile
   - `A_shell(r,t)` = average of `A_local(x,t)` over sites at graph-radius `r` from motif center.

4. Causal-loop transport spread (holonomy proxy)
   - For target `(x,t)`, collect all causal paths from origin under backend.
   - Compute path products.
   - `H_spread(x,t) = (# distinct path products) - 1`.

Interpretation:

1. `A_local` captures nonassociative activity concentration.  
2. `A_shell` captures spatial curvature-like profile around motif.  
3. `H_spread` captures transport nonclosure before coherence filtering.

## 4) Hypotheses

H1 (vacuum flatness proxy):
1. vacuum control has near-minimal `A_local` and flat `A_shell`.

H2 (motif curvature proxy):
1. stable or quasi-stable motifs show elevated `A_local` near core relative to vacuum baseline.

H3 (radial structure):
1. motif `A_shell(r)` shows reproducible radial decay or structured non-flat profile.

H4 (coherent transport closure):
1. promoted physical motifs must have `H_spread = 0` on evaluated cone points.
2. nonphysical seeds can show `H_spread > 0`.

## 5) Falsifiers

Reject this lane if:

1. motif `A_local` is indistinguishable from vacuum under repeated controls,  
2. shell profile has no reproducible structure above control noise,  
3. coherent candidate motifs require persistent nonzero `H_spread`.

## 6) Promotion gates

Gate G1 (baseline separation):
1. `DeltaA = mean(A_local_motif) - mean(A_local_vacuum) > epsilon_A`.

Gate G2 (radial structure):
1. non-flat `A_shell(r)` reproducible across seeds in same motif family.

Gate G3 (coherence consistency):
1. motif candidates marked physical in v5 must satisfy `H_spread = 0`.

## 7) Implementation contract

Script:
1. `cog_v3/calc/build_v5_associator_holonomy_probe_v1.py`

Artifacts:
1. `cog_v3/sources/v5_associator_holonomy_probe_v1.json`
2. `cog_v3/sources/v5_associator_holonomy_probe_v1.md`

Required fields:
1. `kernel_profile`
2. `causal_backend`
3. `horizon`
4. `A_bg_mean`
5. `A_motif_mean`
6. `DeltaA_mean`
7. `A_shell_bg`
8. `A_shell_motif`
9. `H_spread_bg_summary`
10. `H_spread_motif_summary`
11. `gate_results`

## 8) Scope boundary

This RFC does not claim Einstein equations or inverse-square law yet.

It only establishes a strict, testable route where:
1. curvature-like observables are algebra-native,
2. transport closure/coherence is kernel-native,
3. no external gravity field is introduced.

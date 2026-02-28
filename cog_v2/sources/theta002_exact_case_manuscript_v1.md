# Manuscript: THETA-002 Exact Finite-Case Dynamics (v1)

Status: Draft  
Date: 2026-02-28  
Primary claim lane: `THETA-002` (exploratory, structure-first)  
Companion claim lane: `THETA-001` (supported_bridge)

## 1. Core Physical Model

This manuscript models a quark-like object as a **triplet resonance motif** inside a discrete octonionic time crystal:

1. spacetime is a DAG (events are nodes),
2. each event carries an 8-channel state (`e000..e111`),
3. update is deterministic projection over the local lightcone,
4. imaginary-channel routing is XOR-closed, and orientation/sign is set by directed Fano triples.

In this language, a "particle" is a stable repeating event-pattern under the same update map. There is no separate decay law added later.

## 2. Bit-Flip Structure of the Triplet Motif

For distinct imaginary channels, index closure is:

1. `k = i XOR j`

Sign is supplied by the oriented Fano rule, so the multiplication channel and orientation channel are separated.

Operationally, triplet motifs are stable because repeated updates keep returning occupancy/phase structure to a bounded orbit rather than dispersing into arbitrary channels. This is the time-crystal notion in this lane: repeated event updates that remain on a recurring motif class.

## 3. Stability Then Perturbation: Decay as Off-Resonance Dynamics

The central modeling sequence is:

1. start from a stable triplet motif,
2. apply perturbation (weak kick and/or CKM-like transport pulse),
3. motif is pushed outside its stable resonance class,
4. during this off-resonance interval, event-level states show altered orientation flow,
5. system relaxes toward vacuum-coupled and daughter-pattern structure.

In this manuscript, that temporally unstable off-motif interval is exactly what we interpret as decay dynamics.

## 4. Why Theta-Like Behavior Appears Without Extra Terms

No additional theta-specific interaction term is inserted into the kernel.

The same update algebra already defines:

1. control channel: squared strong residual,
2. sign-sensitive channel: oriented Fano-cubic CP-odd residual.

A theta-like moderated interaction then appears as a consequence of initial conditions and perturbation regime:

1. strong control stays zero,
2. sign-sensitive oriented residual can become nonzero with definite sign,
3. sign class depends on the perturbation regime and exact microstate path.

So this is not "new physics added by hand". It is the same update map evaluated in high-perturbation off-resonance trajectories.

## 5. Scope and Boundary

Exact in this manuscript:

1. finite-trace deterministic predictions for four representative nonzero domains,
2. exact integer outputs and full per-tick microstates,
3. exact replay hash and script hashes.

Not claimed here:

1. exhaustive closure over all microstates/depths,
2. full continuum EFT value closure,
3. automatic migration of THETA-002 semantics into THETA-001 semantics.

## 6. Lean Structural Foundation (Proved)

Source: `CausalGraphTheory/ThetaQCD.lean`

1. `cpMap_involution`
2. `orientationFlip_preserves_incidence`
3. `fano_sign_pos_count_eq_21`
4. `fano_sign_neg_count_eq_21`
5. `fanoSignOrderedSum_zero`
6. `theta_qcd_forced_zero_if_cp_invariant`

Bridge-form implications:

Source: `CausalGraphTheory/ThetaEFTBridge.lean`

1. `discreteCpResidual_zero`
2. `theta_zero_if_direct_bridge`
3. `theta_zero_if_linear_bridge`
4. `theta_zero_if_affine_bridge`

Interpretation: Lean proves the structural CP/sign-balance core and conditional bridge forms. The nonzero finite-domain dynamics are currently delivered by deterministic Python witnesses.

## 7. Python Formalism for Exact Event Traces

Primary dynamics module:

1. `cog_v2/calc/theta001_cp_invariant_v2.py`

State/update ingredients:

1. `State8 = Tuple[int,int,int,int,int,int,int,int]`
2. CP map flips imaginary channels and keeps `e000`
3. basis updates are left multiplications using Fano sign table
4. strong control observable uses `STRONG_SECTOR_WEIGHTS`
5. oriented CP-odd observable uses directed Fano-cubic sum

Sign-sensitive observable:

Source: `cog_v2/calc/build_theta001_nonzero_candidate_probe_v1.py`

```text
Q(state) = sum_(a,b,c in FANO_CYCLES) state[a+1] * state[b+1] * state[c+1]
```

Exact finite-case builder:

1. `cog_v2/calc/build_theta002_exact_microstate_domains_v1.py`

Artifact:

1. `cog_v2/sources/theta002_exact_microstate_domains_v1.json`
2. replay hash: `90214a539e5be2ba85619940dab7b1f9018015e8cc6854dc0bc2921c842fb2e8`

## 8. Exact Finite-Case Result

Define per scenario:

1. `R_sq`: squared strong residual total,
2. `R_cub`: oriented cubic residual total,
3. `R_cub_ex_t0`: oriented cubic residual excluding tick 0.

Finite witness statement:

1. for all four selected domains, `R_sq = 0`,
2. for all four selected domains, `R_cub_ex_t0 != 0`,
3. sign of `R_cub_ex_t0` matches the domain label (positive/negative).

### Exact numerical predictions

| Domain | Lane | sample_id | weak_kick | ckm_phase | period | `R_sq` | `R_cub` | `R_cub_ex_t0` |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| weak_positive | weak | 166 | 11 | 3 | 3 | 0 | 4164 | 4164 |
| weak_negative | weak | 298 | 11 | 1 | 2 | 0 | -3516 | -3386 |
| ckm_positive | ckm | 340 | 9 | -1 | 5 | 0 | 2844 | 3624 |
| ckm_negative | ckm | 206 | 11 | 1 | 2 | 0 | -2784 | -2730 |

Summary checks:

1. `all_squared_totals_zero = true`
2. `domain_signs_satisfied = true`
3. `scenario_count = 4`

## 9. What the Tick-Level Data Contains

For each scenario, every tick includes:

1. `orig_state_vector` and `dual_state_vector` (`e000..e111` exact integers),
2. `sq_delta`, `sq_cumulative`,
3. `oriented_cubic_delta`, `oriented_cubic_cumulative`,
4. CP relation flags (`cp_map_matches_dual`, `cp_map_matches_neg_dual`).

This is an event-resolved trajectory, not only endpoint fitting.

## 10. Physical Reading of the Four Domains

In this model:

1. `weak_positive` and `weak_negative` are perturbative weak-kick off-resonance decay classes with opposite orientation accumulation sign,
2. `ckm_positive` and `ckm_negative` are transport-pulsed off-resonance classes with opposite orientation sign,
3. all four keep squared strong control at zero while sign-sensitive orientation channel is nonzero.

That is the explicit mathematical form of "theta-moderated interaction" in this lane: orientation-sensitive decay dynamics emerging from the base kernel, not from an added term.

## 11. Reproducibility

Build exact-case artifact:

```bash
python -m cog_v2.calc.build_theta002_exact_microstate_domains_v1 --write-sources
```

Run test:

```bash
pytest -q cog_v2/calc/test_theta002_exact_microstate_domains_v1.py
```

Validate claims:

```bash
python cog_v2/scripts/validate_claim_contracts_v2.py --root . --claims-dir cog_v2/claims
```

## 12. Next Formal Steps

1. lift oriented-cubic bounded-depth dynamics into Lean theorems,
2. prove Lean/Python parity on selected exact traces,
3. extend domain coverage with preregistered selection policy,
4. decide observable migration policy across THETA-001 and THETA-002 contracts.

## 13. References

1. `cog_v2/sources/theta002_exact_microstate_domains_v1.json`
2. `cog_v2/sources/theta002_exact_microstate_domains_v1.md`
3. `cog_v2/sources/theta001_nonzero_search_v1.json`
4. `cog_v2/sources/theta001_nonzero_robust_casebook_v1.json`
5. `cog_v2/claims/THETA-002.yml`
6. `CausalGraphTheory/ThetaQCD.lean`
7. `CausalGraphTheory/ThetaEFTBridge.lean`

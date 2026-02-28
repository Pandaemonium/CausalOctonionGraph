# Promotion Memo: First Statistical Constant Candidate (THETA-001 v2)

Status: Draft for approval  
Date: 2026-02-28  
Claim: `THETA-001`  
Scope: `structure_first`  
Promotion target: `supported_bridge` (not `proved_core`)

## 1. Decision Requested

Approve `THETA-001` as the first statistical constant candidate at
`supported_bridge` under the v2 canonical axioms:

1. spacetime is a DAG,
2. node states are `CxO` over unity,
3. update rule is projective lightcone update.

Constant candidate interpretation in this lane:
1. strong-sector CP-odd residual is structurally zero,
2. locked linear bridge map (`linear_scale_1_v1`) identifies continuum theta proxy as zero in the declared contract scope.

## 2. Evidence Snapshot

Source packet:
1. `cog_v2/sources/theta001_supported_bridge_closure_packet_v2.json`
2. replay hash:
   `4e89cff9953b859dee839f91ae202348f8e5327e679b4037b19102fddd00b831`

Gate status:
1. Gate 1 (Lean structural witnesses): pass
2. Gate 2 (Python deterministic witness + replay): pass
3. Gate 3 (independent skeptic, model-family-diverse): pass

Primary quantitative checks (all pass in current package):
1. Fano sign balance: `positive_count=21`, `negative_count=21`, `signed_sum=0`
2. Weak leakage suite: `all_zero=true`, `rows=324`, `max_abs_residual=0`
3. CKM-like weak leakage suite: `all_zero=true`, `rows=1440`, `max_abs_residual=0`
4. Continuum bridge diagnostics:
   - `finite_size_residual_stable_zero=true`
   - `normalized_residual_stable_zero=true`
   - zero plateau depth starts at `d=12`
5. Correction envelopes:
   - base correction lane ready: `true`
   - robustness correction lane ready: `true`
6. Topology-diverse robustness:
   - `pair_count=4`
   - `topology_family_count=2`
   - topologies: `baseline_v1`, `alt_branch_v1`
7. Map policy lock:
   - policy: `theta_map_identification_linear_unit_v1`
   - selected map: `linear_scale_1_v1`
   - selected unique: `true`

## 3. What This Promotion Means

Approved claims at `supported_bridge`:
1. Structural CP-odd residual suppression is reproducible and currently unfalsified in the declared stress lanes.
2. Under the locked v2 linear identification contract, theta proxy remains zero across the current deterministic sweep package.
3. The package is validator-clean and replay-stable for the declared scope.

## 4. What This Promotion Does Not Mean

Not approved in this memo:
1. No `proved_core` promotion.
2. No full continuum EFT derivation of physical `theta_QCD`.
3. No claim that all physically realistic cross-sector leakage classes are exhausted.

## 5. Explicit Proved-Core Blockers

1. Continuum EFT identification remains hypothesis-level (`structure_first` contract).
2. Weak-leakage realism boundary remains open beyond current synthetic stress families.
3. Claim scope is policy-locked to `structure_first`; scope migration is required before `proved_core`.

## 6. Required Next Actions Before Proved-Core Attempt

1. Discharge continuum-identification theorem chain from discrete residual to continuum operator coefficient.
2. Add and pass a preregistered realism-expanded weak leakage suite acceptable to independent skeptic review.
3. Submit scope-transition packet (`structure_first -> full_value_closure`) and rerun full gate stack.

## 7. Recommendation

1. Promote/retain `THETA-001` at `supported_bridge` now.
2. Keep `proved_core` blocked until the three blockers above are discharged.

## 8. Skeptic Note (High-School First, Then Technical)

### 8.1 High-School Version

Think of the universe here as:
1. a giant directed graph,
2. where each dot (node) is an event,
3. and arrows only point forward (cause -> effect).

That means no time loops. "Time" is just how many layers deep you are in this graph.

Each node stores an 8-slot state (`e000` to `e111`), and each slot has a tiny phase-like value from:
1. `0`
2. `+1`
3. `-1`
4. `+i`
5. `-i`

At each tick, a node looks backward at its parent nodes (its local past light cone), combines those messages, and then projects back to the allowed alphabet above. So the system stays discrete and deterministic.

The THETA result in this lane is:
1. the strong-sector CP-odd residual keeps coming out exactly zero in the tested families,
2. this zero survives weak-side perturbation stress lanes in our current package,
3. and therefore the current bridge contract keeps the theta proxy at zero (for `supported_bridge` scope).

### 8.2 Time Cone in This Kernel

For each node `n`, the kernel uses only `parents[n]` to update it. Operationally:

```text
for node in canonical_order:
    msgs = states_of(sorted(parents[node]))
    payload = project_to_unity(fold_octonion_mul(msgs))
    new_state[node] = project_to_unity(payload * old_state[node])
```

So:
1. causality is local and directed,
2. update is deterministic under fixed graph + initial state + ordering,
3. "cone" means the backward-reachable causal neighborhood feeding the node.

### 8.3 Bitwise/XOR Structure of the Basis

The v2 runtime basis is named in binary:
1. `e000` (index 0)
2. `e001` (1)
3. `e010` (2)
4. `e011` (3)
5. `e100` (4)
6. `e101` (5)
7. `e110` (6)
8. `e111` (7)

For imaginary basis multiplication (indices 1..7), channel closure is:
1. `k = i XOR j`

Sign is not from XOR alone. Sign comes from the oriented Fano triples (antisymmetry).

Concrete examples:
1. `e001 * e010 = +e011` because `1 XOR 2 = 3` and orientation is positive on that order.
2. `e010 * e001 = -e011` (reversing order flips sign).
3. `e001 * e001 = -e000` (same imaginary basis squares to `-1`).
4. `e000 * exxx = exxx` (identity action).

This is why binary naming is useful: channel destination is visibly bitwise, while sign is handled by orientation.

### 8.4 What a Particle Motif Means Here

In this lane, a motif is a stable/repeating occupancy-phase pattern across selected basis channels under repeated updates.

The triplet-coherence probes use:
1. coherent lane: concentrated, phase-structured occupancy on a 3-cycle-compatible triplet support,
2. broken lane: off-cycle occupancy including stronger coupling into `e000`/`e111` directions.

Measured proxies then compare coherent vs broken behavior over depth:
1. triplet coherence (`C_t`),
2. `e000` share (`E_t`),
3. leakage increment (`L_t`),
4. non-`e000` mass proxy (`M_t`),
5. transport proxy (`T_t`).

### 8.5 What Happens Off-Motif

Off-motif does not break physics; it changes local phase-routing under the same rules.

Mechanically:
1. off-cycle interactions produce different raw coefficients in local channels,
2. projector snaps each coefficient back to `{0, +-1, +-i}` by dominant-axis rule,
3. this changes the local phase pattern and often increases `e000` share in broken families.

In the current artifact package, broken families are expected (and observed in acceptance checks) to trend toward:
1. higher `e000` share,
2. lower non-`e000` proxy load,
3. reduced transport proxy relative to coherent controls.

### 8.6 Why This Is a Statistical Constant Candidate and Not Final Theory

Why candidate:
1. multiple deterministic sweeps are replay-stable,
2. CP-odd strong residual remains zero across declared stress grids,
3. map-identification policy is locked and validator-enforced.

Why not final:
1. bridge to full continuum EFT is still assumption-bound (`structure_first`),
2. realism expansion for leakage families is incomplete,
3. scope is intentionally blocked from `proved_core` until those are discharged.

### 8.7 Bottom Line for a Skeptic

What is genuinely strong right now:
1. algebraic closure and deterministic reproducibility,
2. explicit falsification lanes with zero residual outcomes in current package,
3. strict promotion gating with clear blockers, not hand-waving.

What is still open:
1. first-principles continuum identification closure,
2. broader realism closure on cross-sector leakage.

That is exactly why this is promoted at `supported_bridge`, not `proved_core`.

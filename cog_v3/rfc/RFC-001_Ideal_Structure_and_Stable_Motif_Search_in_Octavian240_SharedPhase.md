# RFC-001: Stable Multiplicative Loop Search in Octavian240 Shared-Phase Lane

Status: Draft  
Date: 2026-03-02  
Owner: COG Core  
Depends on:
- `cog_v3/README.md`
- `cog_v3/rfc/CONVENTION_IDS.md`
- `cog_v3/python/kernel_octavian240_multiplicative_v1.py`

## 1. Purpose

Define the v3 particle-search object as multiplicative stable loops, not additive ideals.

Core target:

1. discover cyclic motifs in a 3D voxel world over `S960`,
2. classify stationary loops and propagating loops,
3. produce replay-deterministic artifacts for each candidate class.

This RFC is the operational contract for loop discovery.

## 2. Scope Clarification

1. We are using multiplication-only dynamics in runtime.
2. Additive closure and ring-theoretic ideals are out of scope for this RFC.
3. The word "ideal" in previous notes was an overloaded term; the correct runtime object
   is a stable multiplicative loop/orbit.

## 3. Algebra and State Space

### 3.1 Element Alphabet

Define shared-phase alphabet:

1. `Q240`: closed Octavian-240 multiplicative set,
2. `C4 = {1, i, -1, -i}`,
3. `S960 = C4 x Q240`, with product:
   `(p1, q1) * (p2, q2) = (p1 p2, q1 * q2)`.

`S960` is finite and closed under multiplication.

### 3.2 Vacuum

Default vacuum voxel value:

1. `v_vac = (1, e000)`.

Boundary default:

1. fixed vacuum boundary, unless explicitly overridden by scenario contract.

## 4. Loop Definitions

### 4.1 Singleton Vacuum-Driven Orbit

For `a in S960`, define:

1. `x0 = v_vac`,
2. `x_{t+1} = a * x_t`.

Because `S960` is finite, this orbit is eventually periodic. Since left multiplication by
a fixed loop element is bijective, this is a pure cycle on finite set states.

`a` is a singleton loop seed with period `P` if `x_{t+P} = x_t` for all `t`.

### 4.2 3D Motif Loop

Let lattice `L = [0..Nx-1] x [0..Ny-1] x [0..Nz-1]`.

1. A motif initialization `M` assigns each voxel one value in `S960`.
2. Outside motif support, voxels are `v_vac`.
3. One tick is the canonical v3 kernel update over the full lattice.

A motif is:

1. `stationary-loop` with period `P` if `T^P(M) = M`,
2. `propagating-loop` with period `P` and displacement `d` if
   `T^P(M) = Shift_d(M)` with nonzero `d`.

This is the CA-style object analogous to oscillators/spaceships.

## 5. Why Singleton Is Not Enough

Singleton scans are useful but insufficient for particle modeling:

1. they characterize local multiplicative orders,
2. they do not encode multi-voxel stabilizing geometry,
3. physically relevant motifs may require surrounding support voxels and phase texture.

Therefore the search pipeline must include explicit 3D motif construction.

## 6. Tractable Search Strategy

Brute force over all 3D assignments is intractable. Use staged constrained search.

### 6.1 Stage A: Singleton Census (Complete)

1. Enumerate all `a in S960`.
2. Compute singleton period/order statistics.
3. Keep seeds with short or structured periods as motif-building primitives.

### 6.2 Stage B: Small-Support Exhaustive Search (Symmetry-Reduced)

For support size `k` in small range (for example `k <= 4`):

1. enumerate connected voxel polycubes,
2. assign values from a restricted seed alphabet from Stage A,
3. quotient candidates by translation/rotation/reflection symmetries,
4. run bounded-horizon evolution and detect periodic return.

### 6.3 Stage C: Guided Growth

Grow only promising motifs:

1. start from Stage B survivors,
2. add one shell voxel at a time,
3. keep mutations that improve loop score (periodic stability, bounded support,
   reproducible displacement).

### 6.4 Stage D: Robustness Validation

For each candidate:

1. rerun at larger boxes,
2. rerun with admissible fold-order variants,
3. verify period and displacement stability within declared tolerance.

## 7. Canonicalization and Pruning Rules

To prevent combinatorial explosion:

1. canonicalize motifs under lattice symmetries and translation,
2. canonicalize by global phase rotation equivalence when physically admissible,
3. reject trajectories whose occupied support exceeds configured max bound,
4. reject trajectories without recurrence evidence by horizon cutoff.

Required invariants to store per candidate:

1. support size over time,
2. phase histogram over support,
3. period estimate and confidence,
4. displacement vector estimate,
5. replay hash.

## 8. Candidate Classes and Labels

Use operational classes:

1. `singleton_cycle`,
2. `stationary_loop_candidate`,
3. `propagating_loop_candidate`,
4. `unstable/transient`.

Promotion to `supported_loop_candidate` requires reproducible replay across:

1. at least two box sizes,
2. at least two admissible event-order variants,
3. identical convention id.

## 9. Artifact Contract

Planned scripts:

1. `cog_v3/calc/build_v3_singleton_s960_cycles_v1.py`
2. `cog_v3/calc/build_v3_voxel_loop_search_v1.py`
3. `cog_v3/calc/test_v3_singleton_s960_cycles_v1.py`
4. `cog_v3/calc/test_v3_voxel_loop_search_v1.py`

Planned outputs:

1. `cog_v3/sources/v3_singleton_s960_cycles_v1.json`
2. `cog_v3/sources/v3_singleton_s960_cycles_v1.md`
3. `cog_v3/sources/v3_voxel_loop_search_v1.json`
4. `cog_v3/sources/v3_voxel_loop_search_v1.md`

Required metadata fields:

1. `kernel_profile`
2. `convention_id`
3. `alphabet_id` (`s960_shared_phase_v1`)
4. `box_shape`
5. `boundary_condition`
6. `event_order_policy`
7. `replay_hash`

## 10. Falsification Conditions

This loop-search thesis is falsified if:

1. no nontrivial stationary or propagating loops survive robustness checks, or
2. discovered loops are not replay-stable under fixed contract settings, or
3. candidate loops disappear systematically under modest box scaling.

## 11. Immediate Execution Plan

1. Implement singleton census first and freeze seed shortlist.
2. Implement symmetry-reduced small-support 3D search.
3. Promote first reproducible stationary loop and first reproducible propagating loop.
4. Then expand support size and horizon.

## 12. References

1. C. Furey, "Division Algebras, Ladders, and Particle Physics," arXiv:1611.09182  
   https://arxiv.org/abs/1611.09182
2. A. Kleinschmidt, H. Nicolai, "E10 and SO(9,9) invariant supergravity," arXiv:1010.2212  
   https://arxiv.org/abs/1010.2212
3. R. Basak, "Integral octonions, octonion XY-product, and the Leech lattice," arXiv:1702.05705  
   https://arxiv.org/abs/1702.05705
4. G. P. Nagy, P. Vojtechovsky, et al., finite simple Moufang loop constructions, arXiv:0908.2797  
   https://arxiv.org/abs/0908.2797

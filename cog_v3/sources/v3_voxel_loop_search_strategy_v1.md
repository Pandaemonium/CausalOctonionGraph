# v3 Voxel Loop Search Strategy (v1)

Date: 2026-03-02  
Lane: `cog_v3_octavian240_multiplicative_v1`  
Convention: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`  
Alphabet: `S960 = C4 x Q240` (shared phase + octavian state)

## Objective

Find reproducible 3D motifs that evolve as:

1. stationary loops: `T^P(M) = M`
2. propagating loops: `T^P(M) = Shift_d(M)` with nonzero `d`

under fixed-vacuum boundaries and multiplication-only update.

## Why this strategy

Full brute force is intractable. We therefore:

1. constrain seeds with singleton cycle structure,
2. exhaustively scan only tiny connected supports,
3. grow only candidates that already show recurrence,
4. promote only replay-stable classes.

## Stage 0: Singleton Census (Complete, exact)

Use:

- `cog_v3/calc/build_v3_singleton_s960_cycles_v1.py`
- output: `cog_v3/sources/v3_singleton_s960_cycles_v1.json`

Actions:

1. compute periods for all 960 singleton seeds,
2. rank period classes and representatives,
3. build reduced seed alphabets for voxel search.

Default reduced alphabets:

1. `A_short`: representatives from low periods (`P <= 8`)
2. `A_mid`: representatives from medium periods (`9 <= P <= 32`)
3. `A_long`: representatives from top 5 to top 10 longest periods

## Stage 1: Small-support exhaustive scan (symmetry-reduced)

Search domain:

1. support size `k = 1..4`
2. connected supports only
3. canonicalize by translation + cube symmetries
4. assign voxel values from `A_short U A_mid` (not full `S960`)

Runtime defaults:

1. geometry: `Nx x Ny x Nz = 21 x 9 x 9`
2. stencil: `axial6` (default tractable baseline)
3. ticks: `96`
4. warmup: `20`
5. period window: `2..24`

Keep candidate if:

1. recurrence evidence appears in horizon,
2. support remains bounded (no global blow-up),
3. replay hash is stable.

## Stage 2: Guided growth

For each Stage-1 survivor:

1. add one shell voxel mutation at a time,
2. test values from `A_mid U A_long`,
3. accept mutation only if score improves.

Score (example):

1. recurrence confidence (weight 0.45)
2. support compactness (weight 0.20)
3. period consistency across reruns (weight 0.20)
4. directional displacement consistency (weight 0.15)

## Stage 3: Robustness gates

Every promoted candidate must pass:

1. box scaling gate:
   - `21x9x9` and `31x11x11` both pass recurrence
2. event-order gate:
   - at least 2 admissible event-order variants agree on class and period window
3. stencil cross-check:
   - `axial6` primary and `cube26` secondary do not contradict class

Pass states:

1. `supported_stationary_loop_candidate`
2. `supported_propagating_loop_candidate`

## Stage 4: Particle-lane handoff

For each supported loop candidate:

1. freeze initialization recipe,
2. freeze measurement contract (`P`, displacement, support trace),
3. run perturbation-response panel (kicks, background phases),
4. map to phenomenology lane only after reproducibility lock.

## Artifacts to produce per search batch

Required:

1. JSON summary with `replay_hash`, `kernel_profile`, `convention_id`
2. markdown report with top candidates and failure reasons
3. compact trace slices for candidate motifs

Optional:

1. voxel snapshots for one period
2. gif/mp4 render of support evolution

## Failure modes and mitigations

1. Failure: combinatorial blow-up.
   Mitigation: enforce support-size cap and symmetry canonicalization.
2. Failure: boundary-induced false recurrences.
   Mitigation: box scaling gate + fixed-vacuum boundary lock.
3. Failure: one-off lucky candidates.
   Mitigation: multiple reruns and event-order variants.
4. Failure: overfitting to one stencil.
   Mitigation: axial6 primary with mandatory cube26 cross-check.

## Immediate next run plan

1. Run singleton census and freeze `A_short`, `A_mid`, `A_long`.
2. Execute Stage-1 exhaustive scan for `k <= 3`.
3. Promote first reproducible stationary candidate.
4. Promote first reproducible propagating candidate.

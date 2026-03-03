# RFC-001: Global Lightcone Coherence Kernel Contract (v4)

Status: Draft  
Date: 2026-03-03  
Owner: COG Core

## 1. Purpose

Define v4 kernel semantics under the axiom:

1. The full lightcone is coherent.
2. Future states are uniquely determined by causal past lightcone data.
3. No stochastic update is allowed in the production rule.

This RFC establishes the minimal deterministic simulator lane for small-system coherent behavior.

## 2. State Space

Per-cell state:

`sid = phase * 240 + q_id`, where:

1. `phase in Z12`,
2. `q_id in Q240`.

Equivalent factorization:

`Z12 ~ Z3 x Z4`, with:

1. triality/domain channel `g = phase mod 3`,
2. energy channel `a = phase mod 4`.

## 3. Measurement-to-Start Construction

Given:

1. world shape,
2. measurement volume `V_meas`,
3. decoherence horizon `D` ticks,

the start volume is computed by backward lightcone projection:

`V_start = BackProject(V_meas, D)`.

Operationally in code:

1. create mask for `V_meas`,
2. apply `D` one-hop graph dilations on chosen stencil.

This guarantees `V_start` contains all possible contributors to `V_meas` at speed `c=1`.

## 4. Seeding Rule

Input seed tuple:

1. `domain_g in Z3`,
2. `energy_a in Z4`,
3. `q_id in Q240`.

Phase reconstruction:

`phase = (9*a + 4*g) mod 12`.

Seed state:

`seed_sid = phase * 240 + q_id`.

Initialization:

1. cells in `V_start` receive `seed_sid` (or deterministic seed_rule),
2. outside cells receive `vacuum_sid`,
3. history stack `[t-N..t0]` is initialized as repeated `t0` frame.

## 5. Deterministic Full-Lightcone Update

Per tick:

1. select one disjoint pair round (deterministic index `tick mod n_rounds`),
2. read all pair inputs from shared pre-round frame,
3. update Q channel non-commutatively:
   - `qL' = mul(qL, qR)`,
   - `qR' = mul(qR, qL)`,
4. choose `dg in {0,1,2}` from full lightcone evidence only,
5. update phase pair-conservatively:
   - `pL' = pL + dg`,
   - `pR' = pR - dg`  (mod 12).

No RNG, no learned fit constants in update rule.

## 6. Hard Invariants

### 6.1 Triality conservation (exact)

Per event:

`(gL' + gR') mod 3 = (gL + gR) mod 3`.

### 6.2 Causal determinism

Given identical:

1. history frames,
2. stencil,
3. boundary mode,
4. pair-round graph,

the next frame is exactly identical bit-for-bit.

## 7. Reference Implementation

Kernel:

`cog_v4/python/kernel_s2880_lightcone_coherent_v1.py`

Builder:

`cog_v4/calc/build_v4_small_system_coherent_sim_v1.py`

Test:

`cog_v4/calc/test_v4_small_system_coherent_sim_v1.py`

## 8. Promotion Gates

Gate 1:

1. deterministic replay exact match for fixed inputs,
2. exact triality conservation over all tested ticks.

Gate 2:

1. `|V_start| >= |V_meas|` always for finite `D`,
2. backward projection geometry matches stencil semantics.

Gate 3:

1. stable cyclic motifs appear in small volumes under deterministic coherent updates,
2. motif classes reproducible across run repeats and machine restarts.

## 9. Non-Claims

1. This RFC does not claim Lorentz closure at mesoscale.
2. This RFC does not claim calibrated physical units (mass/time/length mapping).
3. This RFC does not claim particle identification closure (photon/neutrino/electron).

## 10. Immediate Next Steps

1. Add a motif-search panel that consumes this kernel directly.
2. Add observables panel for mass-like, momentum-like, and angular-momentum-like proxies.
3. Add strict equivariance audit (`Z3`, `Z4`, lattice symmetry subgroup).


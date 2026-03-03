# RFC-002: Integer Z Energy from C4 Spin Transfer

Status: Draft  
Date: 2026-03-03  
Owner: COG Core

## 1. Purpose

Add an explicit integer energy register `Z` to v4 coherent simulations:

1. `Z` is integer-valued per cell,
2. `Z` is never negative,
3. C4 spin steps transfer integer quanta between pair partners.

This directly encodes the project hypothesis:
`C4 spin increments/decrements integer Z` with hard floor at zero.

## 2. Rule

For each active pair event:

1. choose triality channel `dg in {0,1,2}`,
2. map to signed C4 spin step `s`:
   - `dg=0 -> s=0`,
   - `dg=1 -> s=+1`,
   - `dg=2 -> s=-1`.

Energy transfer:

1. if `s=+1`, transfer one quantum `right -> left`,
2. if `s=-1`, transfer one quantum `left -> right`,
3. if requested emitter has `Z=0` and nonnegativity is enforced:
   - flip direction if opposite side can emit,
   - else set `s=0`.

Phase updates use `s` (unit step) rather than raw `dg`.

## 3. Hard Invariants

1. Triality remains exact per event: pair sum modulo 3 conserved.
2. Global `Z` is exactly conserved (pure transfer, no source/sink).
3. Per-cell `Z >= 0` always.
4. Non-negativity is not optional in v4; negative seeds or runtime negatives raise errors.

## 4. Reference Implementation

Kernel functions:

1. `step_coherent_full_lightcone_with_integer_energy`
2. `run_coherent_reconstruction_with_integer_energy`

File:

`cog_v4/python/kernel_s2880_lightcone_coherent_v1.py`

Builder:

`cog_v4/calc/build_v4_small_system_coherent_sim_with_integer_energy_v1.py`

Test:

`cog_v4/calc/test_v4_small_system_coherent_sim_v1.py`

## 5. Current Validation Snapshot

From `cog_v4/sources/v4_small_system_coherent_sim_with_integer_energy_v1.md`:

1. `triality conserved: True`,
2. `total Z conserved: True`,
3. `nonnegative: True`.

## 6. Non-Claims

1. This RFC does not claim physical unit calibration of `Z`.
2. This RFC does not claim mass closure for identified particles.
3. This RFC does not claim final Lorentz-emergence closure.

# COG v3 Bootstrap

This directory starts a new canonical lane with:

1. Closed Octavian-240 alphabet as the state basis.
2. Multiplication-only update rule.
3. Explicit convention metadata (`convention_id`) to prevent mixing with v2.
4. Active default runtime profile for new work.

## Default profile

The active repository-level default is defined in:

- `cog_runtime_default_v1.json`

and resolves to:

- module: `cog_v3.python.kernel_default`
- kernel profile: `cog_v3_octavian240_multiplicative_v1`
- convention id: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`

## Convention note

Requested triplets were:

- `(110,111,011)` positive
- `(100,111,011)` positive
- `(010,111,101)` positive

The first line is algebraically inconsistent with octonion unit multiplication
when combined with the others (right multiplication by a unit is bijective on
basis units). v3 therefore uses the nearest consistent target:

- `(110,111,001)` positive
- `(100,111,011)` positive
- `(010,111,101)` positive

This is verified by `cog_v3/calc/build_v3_bootstrap_probe_v1.py`.

## Acceleration lane

v3 now includes an optional accelerated step backend:

- module: `cog_v3/python/kernel_octavian240_accel_v1.py`
- benchmark: `cog_v3/calc/benchmark_v3_kernel_accel_v1.py`

Backends:

- `python` (reference)
- `numba_cpu` (JIT CPU, available by default in this repo env)
- `numba_cuda` (GPU path, enabled only when Numba CUDA toolchain is complete)

Run benchmark:

```powershell
python -m cog_v3.calc.benchmark_v3_kernel_accel_v1 --reps 5 --warmup-reps 2
```

Artifacts:

- `cog_v3/sources/v3_kernel_accel_benchmark_v1.json`
- `cog_v3/sources/v3_kernel_accel_benchmark_v1.md`

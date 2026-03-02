# V3 Kernel Acceleration Benchmark (v1)

## Backend Availability

- `python`: available=`True` (reference)
- `numba_cpu`: available=`True` (available)
- `numba_cuda`: available=`False` (CUDA device found but NVVM unavailable: libNVVM cannot be found. Do `conda install cudatoolkit`:
Could not find module 'nvvm.dll' (or one of its dependencies). Try using the full path with constructor syntax.)

## Cases

| case_id | size | ticks | backend | ok | best_sec | best_ticks/s | best_cells/s | hash_ok |
|---|---|---:|---|---|---:|---:|---:|---|
| `small_15x7x7` | `15x7x7` | 48 | `python` | `True` | 0.074038 | 648.319 | 476514.8 | `True` |
| `small_15x7x7` | `15x7x7` | 48 | `numba_cpu` | `True` | 0.000501 | 95873.529 | 70467044.1 | `True` |
| `mid_39x11x11` | `39x11x11` | 24 | `python` | `True` | 0.239689 | 100.130 | 472512.4 | `True` |
| `mid_39x11x11` | `39x11x11` | 24 | `numba_cpu` | `True` | 0.000329 | 73033.589 | 344645508.0 | `True` |
| `wide_79x21x21` | `79x21x21` | 8 | `numba_cpu` | `True` | 0.000377 | 21230.135 | 739636672.4 | `True` |

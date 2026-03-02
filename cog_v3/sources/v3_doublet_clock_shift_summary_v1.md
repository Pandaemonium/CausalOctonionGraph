# v3 Doublet Clock Shift Table Summary (v1)

Date: 2026-03-02

## Outputs

1. Dense table: `cog_v3/sources/v3_doublet_clock_shift_dense_v1.csv.gz`
2. Clock metadata: `cog_v3/sources/v3_doublet_clock_meta_v1.csv`
3. S960 element metadata: `cog_v3/sources/v3_s960_element_meta_v1.csv`
4. Generator script: `cog_v3/calc/build_v3_doublet_clock_shift_table_v1.py`

## Table schema

1. Columns `A`, `B`, `C`
2. Columns `clock_000` .. `clock_424` (425 non-identity clocks)
3. `C` is fixed to S960 identity id `239`
4. Cell value semantics:
5. `-128` means the map does not act as a pure rotation on that same clock
6. `0..period-1` means pure rotation by that many ticks on that clock

## Build/run notes

1. Evaluated all ordered pairs `(A,B)` in S960: `960 x 960 = 921600` rows
2. Compressed dense output size: `9169774` bytes
3. Header columns: `428` total (`3 + 425`)

## Aggregate behavior (full brute-force)

1. Rows with exactly 1 rotating/preserved clock: `806400`
2. Rows with 3 rotating/preserved clocks: `53760`
3. Rows with 6 rotating/preserved clocks: `53760`
4. Rows with 29 rotating/preserved clocks: `3840`
5. Rows with 87 rotating/preserved clocks: `960`
6. Rows with 155 rotating/preserved clocks: `1920`
7. Rows with all 425 clocks rotating/preserved: `960`

## Specific check requested ("one clock advances, all others static")

1. Rows where all 425 clocks are preserved and exactly one clock has nonzero shift: `0`

## Guidance

1. Your dense CSV approach is feasible and is now generated.
2. For analysis speed, join with `v3_doublet_clock_meta_v1.csv` and treat `-128` as "not a same-clock rotation".
3. If you want triplets next, keep this dense format but consider adding a sparse companion file for queries.

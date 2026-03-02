# COG v3 Singleton S960 Cycle Census (v1)

## Scope

- Alphabet: `S960 = C4 x Q240`
- Rule: `x_{t+1} = a * x_t`, `x0 = vacuum`
- All seeds scanned exactly once

## Params

- phase_count: `4`
- q_alphabet_size: `240`
- s960_size: `960`
- max_period_bound: `960`

## Summary

- seed_count: `960`
- min_period: `1`
- max_period: `12`
- distinct_period_count: `6`
- no_scan_errors: `True`

## Longest Representative Seeds

| period | sid | phase | q_id |
|---:|---:|---|---:|
| 12 | 241 | `i` | 1 |
| 6 | 183 | `1` | 183 |
| 4 | 57 | `1` | 57 |
| 3 | 1 | `1` | 1 |
| 2 | 0 | `1` | 0 |
| 1 | 239 | `1` | 239 |

## Checks

- seed_count_ok: `True`
- all_periods_positive: `True`
- all_periods_within_bound: `True`
- no_scan_errors: `True`

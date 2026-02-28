# THETA-001 Nonzero Candidate Case Development (v1)

- Claim: `THETA-001`
- Replay hash: `b27d3cd0c28fb3e5715bf441968154b60147519df6d3ae00648aa3f1105e369d`
- Developed cases: `12`

## Aggregate
- all_sq_totals_zero: `True`
- all_cubic_totals_nonzero: `True`
- cases_with_nonzero_cubic_total_excluding_t0: `6`
- weak_cases_with_nonzero_cubic_total_excluding_t0: `0`
- ckm_cases_with_nonzero_cubic_total_excluding_t0: `6`
- max_abs_cubic_total: `88338`
- max_abs_cubic_case: `alt_lane_b_v2`
- max_abs_cubic_lane: `ckm`

## Developed Cases (summary)

| lane | case_id | weak_kick | ckm_phase | period | sq_total | cubic_total | cubic_total_ex_t0 | first_nonzero_tick | first_nonzero_tick_ex_t0 | peak_tick | peak_abs_cubic |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| weak | alt_lane_b_v2 | 11 |  |  | 0 | -15830 | 0 | 0 | 2 | 0 | 15830 |
| weak | alt_lane_b_v2 | 9 |  |  | 0 | -14770 | 0 | 0 | 2 | 0 | 14770 |
| weak | alt_lane_b_v2 | 7 |  |  | 0 | -13710 | 0 | 0 | 2 | 0 | 13710 |
| weak | alt_lane_b_v2 | 5 |  |  | 0 | -12650 | 0 | 0 | 2 | 0 | 12650 |
| weak | alt_lane_b_v2 | 3 |  |  | 0 | -11590 | 0 | 0 | 2 | 0 | 11590 |
| weak | alt_lane_b_v2 | 1 |  |  | 0 | -10530 | 0 | 0 | 2 | 0 | 10530 |
| ckm | alt_lane_b_v2 | 11 | -5 | 5 | 0 | -88338 | -72508 | 0 | 2 | 0 | 15830 |
| ckm | alt_lane_b_v2 | 9 | -5 | 5 | 0 | -83218 | -68448 | 0 | 2 | 0 | 14770 |
| ckm | alt_lane_b_v2 | 7 | -5 | 5 | 0 | -78098 | -64388 | 0 | 2 | 0 | 13710 |
| ckm | alt_lane_b_v2 | 5 | -5 | 5 | 0 | -72978 | -60328 | 0 | 2 | 0 | 12650 |
| ckm | alt_lane_b_v2 | 11 | -7 | 2 | 0 | -69242 | -53412 | 0 | 2 | 0 | 15830 |
| ckm | alt_lane_b_v2 | 11 | -3 | 2 | 0 | -69242 | -53412 | 0 | 2 | 0 | 15830 |

## Limits
- Exploratory diagnostic artifact for case development.
- Does not alter THETA-001 supported_bridge status.
- Promotion impact requires preregistered observable migration and skeptic review.

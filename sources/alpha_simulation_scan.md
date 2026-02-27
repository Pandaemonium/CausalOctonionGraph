# ALPHA-001 Deterministic Full-Cone Simulation Scan

Target alpha: 0.0072973525693 (CODATA-2022, Q->0)

| Condition | Cone depth | Cone sites | Ce_ticks_exact | Best proxy | Best value | Rel gap | Replay hash |
|---|---:|---:|---:|---|---:|---:|---|
| cone_d4 | 4 | 25 | 20 | alpha_proxy_hybrid_sites_plus_ticks | 0.022222222222 | 204.52% | `7a64bf5f4d71831d` |
| cone_d7 | 7 | 64 | 32 | alpha_proxy_hybrid_sites_plus_ticks | 0.010416666667 | 42.75% | `50576b4906eb865c` |
| cone_d11 | 11 | 144 | 48 | alpha_proxy_cone_sites | 0.006944444444 | 4.84% | `af5c0e13440c2a38` |
| cone_d15 | 15 | 256 | 64 | alpha_proxy_cone_sites | 0.003906250000 | 46.47% | `46ad121df217c318` |
| cone_d23 | 23 | 576 | 96 | alpha_proxy_cycle_ticks | 0.010416666667 | 42.75% | `b29e85158bf9eee2` |
| cone_d31 | 31 | 1024 | 128 | alpha_proxy_cycle_ticks | 0.007812500000 | 7.06% | `77f8c462c6c70600` |

## Governance
- All conditions are predeclared in `calc/alpha_simulation_conditions.json`.
- Full-cone preconditioning is enforced by condition schema (`cone_depth`, full-cone site count).
- No fitted attenuation parameters are used.

## Best Row
- `cone_d11` (alpha_proxy_cone_sites = 0.006944444444, relative gap 4.84%)

## Note
These are simulation-backed proxy observables, not a closed first-principles derivation.

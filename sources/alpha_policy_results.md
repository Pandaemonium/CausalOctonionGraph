# ALPHA-001 Policy Results

Target: CODATA-2022 alpha at Q->0

| Policy ID | Candidate | Relative gap | Gate (<=15%) | Policy checksum | Replay hash |
|---|---:|---:|---|---|---|
| alpha_proxy_v1_area | 0.020408163265 | 179.67% | FAIL | `7b2eb8c65ac68a84` | `16195987c5cfb137` |
| alpha_proxy_v2_stabilizer_gap | 0.006535947712 | 10.43% | PASS | `7dca4966c2f7a9d5` | `324c3b887daaa214` |
| alpha_proxy_v3_cubic_fano | 0.006896551724 | 5.49% | PASS | `de6379b9b31cd77b` | `f431b6fed55eda28` |

## Governance
- Policies are loaded from `calc/alpha_policies.json`.
- Policies are predeclared and evaluated in file order (no output-driven selection).
- No fitted attenuation parameters are allowed in the bundle.
- Replay hashes are deterministic for identical policy + target inputs.

## No-Fit Declaration
This artifact is a frozen policy comparison only. It is not a parameter fit.

## Pass/Fail Summary
- Passing rows (relative gap <= 15%): 2/3
- Best row: `alpha_proxy_v3_cubic_fano` (candidate=0.006896551724, relative gap=5.49%)

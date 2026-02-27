# ALPHA Lightcone Extraction Report

- Simulation replay hash: `3f11bec53af6263c...`
- Extraction replay hash: `127ad14bb2c47674...`
- Conditions checksum: `507fc25cce6e69df...`
- Mass normalization (mu_eff): 1.0
- Target alpha: 0.0072973525693

## Per-Channel Summary

| Channel | Samples | alpha_hat median | MAD | Relative gap |
|---|---:|---:|---:|---:|
| electron_electron | 8 | 6793.000000000000 | 6728.000000000000 | 93088454.18% |
| electron_positron | 3 | 49.000000000000 | 24.000000000000 | 671376.40% |

## Pooled Signal Summary
- Samples: 11
- alpha_hat median: 81.0
- MAD: 56.0
- Relative gap to target: 11098.91592577936

## Governance
- Full predetermined lightcone policy enforced by frozen condition file.
- Channel/phase/distance grid is predeclared; no output-driven selection.
- Control subtraction is mandatory (matched by phase_id + initial_edge_distance).
- No fitted attenuation parameter is used in extraction.

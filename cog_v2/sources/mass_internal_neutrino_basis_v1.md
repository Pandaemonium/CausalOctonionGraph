# Mass Internal Neutrino Basis (v1)

## Basis Policy

- basis_motif_id: `su_vacuum_omega`
- basis_mass_unit: `1.0`
- scope: internal normalization only (no physical-unit calibration in this artifact)

## Params

- ticks: `64`
- warmup_ticks: `32`
- width: `96`
- lambda_vacuum_drag: `1.0`
- source_op_cycle: `[7, 7, 7, 7]`

## Derived Values

- m_eff_neutrino_basis_raw: `1.393299621941782`
- m_eff_electron_raw: `1.3962758124179724`
- m_electron_in_neutrino_units: `1.0021360735546907`

## Checks

- m_eff_neutrino_positive: `True`
- m_eff_electron_positive: `True`
- electron_heavier_than_neutrino_internal: `True`
- rows_match_ticks: `True`

## Notes

- This artifact is a structure-first internal-basis lane.
- External mass calibration and SM closure require a separate anchor contract.

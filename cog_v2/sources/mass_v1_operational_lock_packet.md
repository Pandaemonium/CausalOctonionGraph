# Mass v1 Operational Lock Packet

Status: locked (domain-qualified)  
Date: 2026-03-01  
RFC: `cog_v2/rfc/RFC-016_Operational_Mass_Definition_v1.md`

## Locked definition

1. `I_h` = exact init impulse hamming distance
2. `delta_v_impulse` = mean impulse-window velocity response difference
3. `m_est = I_h / |delta_v_impulse|` for `|delta_v_impulse| > eps`

Implementation:

1. `cog_v2/calc/build_operational_mass_targeted_lock_v1.py`

## Supporting artifacts

1. `cog_v2/sources/operational_kinematics_mass_energy_v1.json`
2. `cog_v2/sources/operational_mass_targeted_lock_v1.json`

## Accepted lock scope

Current lock-ready lanes:

1. `left_spinor_muon_motif` + `E2_center_plus_shell1`
2. `left_spinor_tau_motif` + `E2_center_plus_shell1`

Primary profile policy:

1. large off-axis 3D profile (`size_y >= 11`, `size_z >= 11`) is lock-authoritative,
2. 1D lanes are retained as diagnostics.

## Remaining scope

Not yet locked universally for all motifs/energies.
Use extension registry:

1. `cog_v2/sources/operational_kinematics_extension_registry_v1.md`

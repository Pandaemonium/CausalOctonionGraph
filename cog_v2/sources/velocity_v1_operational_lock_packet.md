# Velocity v1 Operational Lock Packet

Status: locked (domain-qualified)  
Date: 2026-03-01  
RFC: `cog_v2/rfc/RFC-015_Operational_Velocity_Definition_v1.md`

## Locked definition

1. `rho_nonvac(x,t) := sum_{k=1..7} |psi_k(x,t)|^2`
2. `X_mod(t)` from weighted circular centroid on periodic x
3. `X_unwrap(t)` from nearest-lift continuity
4. `v_x(t) := X_unwrap(t+1) - X_unwrap(t)`
5. `v_mean` on preregistered measurement window

Implementation:

1. `cog_v2/calc/build_operational_kinematics_mass_energy_v1.py`

## Supporting artifacts

1. `cog_v2/sources/operational_kinematics_mass_energy_v1.json`
2. `cog_v2/sources/operational_kinematics_targeted_lock_v1.json`

## Accepted lock scope

Current lock-ready lanes:

1. `left_spinor_muon_motif` + `E2_center_plus_shell1`
2. `left_spinor_tau_motif` + `E2_center_plus_shell1`

## Remaining scope

Not yet locked universally for all motif/energy lanes.
Use extension registry:

1. `cog_v2/sources/operational_kinematics_extension_registry_v1.md`

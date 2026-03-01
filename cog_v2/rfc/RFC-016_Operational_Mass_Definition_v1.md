# RFC-016: Operational Mass Definition v1

Status: Active (Domain-Qualified)  
Date: 2026-03-01  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-014_Operational_Kinematics_Mass_and_Kinetic_Energy_Contract.md`
- `cog_v2/rfc/RFC-015_Operational_Velocity_Definition_v1.md`

## 1. Decision

Lock operational mass definition `mass_v1` for canonical v2 measurement lanes.

This lock is domain-qualified and currently tied to the large off-axis 3D profile
lane used in targeted mass lock artifacts.

## 2. Locked Definition

For fixed particle/profile/energy lane:

1. `I_h` = exact hamming impulse count between initialized case and matched control.
2. `delta_v_impulse` = window mean of per-tick velocity response difference:
   `mean(v_case(t) - v_control(t))` on preregistered early impulse window.
3. `m_est := I_h / |delta_v_impulse|` when `|delta_v_impulse| > eps`.

Normative implementation:

- `cog_v2/calc/build_operational_mass_targeted_lock_v1.py`

## 3. Lock Scope

The lock is accepted for lanes satisfying:

1. all-run impulse-response validity (`|delta_v_impulse| > eps`),
2. fold mass-span gate pass on primary large off-axis 3D profile(s),
3. profile-gap gate pass when multiple primary profiles exist.

Current primary-profile policy:

1. prefer profiles with `size_y >= 11` and `size_z >= 11`,
2. if no such profile exists, fallback to available profile set.

## 4. Evidence

Primary artifacts:

1. `cog_v2/sources/operational_kinematics_mass_energy_v1.json`
2. `cog_v2/sources/operational_mass_targeted_lock_v1.json`

Current mass-lock-ready lanes:

1. `left_spinor_muon_motif` + `E2_center_plus_shell1`
2. `left_spinor_tau_motif` + `E2_center_plus_shell1`

## 5. Explicit Non-Claims

This RFC does not claim:

1. universal lock across all motif/energy lanes,
2. SI-unit mass calibration,
3. final kinetic-energy closure.

Kinetic remains under RFC-014 draft lane.

## 6. Falsification

Mass lock is falsified for a lane if any occurs:

1. replay mismatch under fixed prereg inputs,
2. impulse-response undefined (`|delta_v_impulse| <= eps`) in required runs,
3. fold mass-span failure on primary profile set,
4. profile-gap failure where applicable.

## 7. Promotion Path

Promotion from domain-qualified to broader lock requires:

1. extension campaigns in
   `cog_v2/sources/operational_kinematics_extension_registry_v1.md`,
2. independent external replay replication with hash-consistent artifacts.

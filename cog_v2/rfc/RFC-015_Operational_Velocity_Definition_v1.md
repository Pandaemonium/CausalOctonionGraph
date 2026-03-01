# RFC-015: Operational Velocity Definition v1

Status: Active (Domain-Qualified)  
Date: 2026-03-01  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-014_Operational_Kinematics_Mass_and_Kinetic_Energy_Contract.md`

## 1. Decision

Lock operational velocity definition `velocity_v1` for canonical v2 measurement lanes.

This lock is domain-qualified, not universal across all motifs/energies.

## 2. Locked Definition

For a replay trace on periodic lattice:

1. `rho_nonvac(x,t) := sum_{k=1..7} |psi_k(x,t)|^2`
2. `X_mod(t)` = x-centroid from weighted circular mean of `rho_nonvac`
3. `X_unwrap(t)` = nearest-lift unwrapped series of `X_mod(t)`
4. `v_x(t) := X_unwrap(t+1) - X_unwrap(t)`
5. `v_mean := mean(v_x(t))` on preregistered window `[t_burn, t_burn + T_meas)`

Normative implementation:

- `cog_v2/calc/build_operational_kinematics_mass_energy_v1.py`

## 3. Lock Scope

The lock is accepted for lanes that satisfy all three:

1. fold-order robustness gate pass,
2. cross-shape robustness gate pass,
3. targeted long-horizon lock pass (transient ablation + multi-cycle stability).

## 4. Evidence

Primary artifacts:

1. `cog_v2/sources/operational_kinematics_mass_energy_v1.json`
2. `cog_v2/sources/operational_kinematics_targeted_lock_v1.json`

Current lock-ready lanes:

1. `left_spinor_muon_motif` + `E2_center_plus_shell1`
2. `left_spinor_tau_motif` + `E2_center_plus_shell1`

## 5. Explicit Non-Claims

This RFC does not claim:

1. universal velocity closure for all motifs/energies,
2. absolute physical-unit calibration,
3. mass or kinetic definitions are locked.

Mass and kinetic remain under RFC-014 draft process.

## 6. Falsification

This lock is falsified for a lane if any occurs:

1. deterministic replay mismatch under identical preregistered inputs,
2. fold-order robustness failure,
3. cross-shape robustness failure,
4. targeted long-horizon lock failure.

## 7. Promotion Path

Promotion from domain-qualified to universal requires:

1. successful extension campaigns listed in
   `cog_v2/sources/operational_kinematics_extension_registry_v1.md`,
2. replicated external reruns with hash-consistent outputs.

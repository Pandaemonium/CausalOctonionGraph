# Operational Kinematics Extension Registry (v1)

Date: 2026-03-01  
Base artifacts:
- `cog_v2/sources/operational_kinematics_mass_energy_v1.json`
- `cog_v2/sources/operational_kinematics_targeted_lock_v1.json`

## Locked in current lane

1. `left_spinor_muon_motif` + `E2_center_plus_shell1`
2. `left_spinor_tau_motif` + `E2_center_plus_shell1`

Both passed targeted long-horizon lock criteria across:

1. two profiles (`41x1x1`, `41x11x11`),
2. four fold-order variants,
3. transient ablation + multi-cycle stability gates.

## Registered extension campaigns

### EXT-KME-001: Electron E2/E3 shape-robustness recovery

Goal:
1. recover shape-robust lock in electron lanes by increasing x-length and stabilization windows.

Required pass:
1. fold-order robust,
2. cross-shape robust (`delta_v`, `m_est`),
3. targeted lock ready.

Compute class: medium.

### EXT-KME-002: Proton-like motif targeted stabilization

Goal:
1. test whether proton-like lanes need larger y/z or longer transients to stabilize under current estimators.

Required pass:
1. same as EXT-KME-001.

Compute class: medium-high.

### EXT-KME-003: Third-profile confirmation lane

Goal:
1. add third large profile (`61x11x11` or `81x11x11`) to reduce two-profile ambiguity.

Required pass:
1. target remains lock-ready after adding profile-3.

Compute class: medium-high.

### EXT-KME-004: External replication packet

Goal:
1. publish fixed parameter pack and replay hashes for external group reruns.

Required pass:
1. bitwise replay hash agreement on at least one independent hardware stack.

Compute class: low (engineering), then external run costs vary.

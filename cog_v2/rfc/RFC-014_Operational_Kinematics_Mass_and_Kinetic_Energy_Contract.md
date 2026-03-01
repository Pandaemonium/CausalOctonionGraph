# RFC-014: Operational Kinematics, Mass, and Kinetic Energy Contract

Status: Draft  
Date: 2026-03-01  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-006_Bridge_Construction_from_CxO_Combinatorics.md`
- `cog_v2/rfc/RFC-013_Mass_Rephasing_Latency_and_Vacuum_Drag_Contract.md`

## 1. Purpose

Define lockable, replay-deterministic statistics for:

1. velocity (`v`),
2. mass estimator (`m`),
3. kinetic estimator (`K`),

under canonical v2 axioms, using elongated lattices and fold-order robustness gates.

This RFC is a measurement contract. It does not yet claim SM mass closure.

Note:
Operational velocity is locked in domain-qualified form by
`cog_v2/rfc/RFC-015_Operational_Velocity_Definition_v1.md`.
Operational mass is locked in domain-qualified form by
`cog_v2/rfc/RFC-016_Operational_Mass_Definition_v1.md`.
This RFC remains the active draft lane for kinetic estimator closure and scope extension.

## 2. Core Definitions (Operational)

All quantities are defined from simulation traces only.

1. `rho_nonvac(x,t)`  
   non-vacuum occupancy power at lattice coordinate `x` and tick `t`:  
   `rho_nonvac := sum_{k=1..7} |psi_k|^2`.

2. `X_mod(t)`  
   x-centroid on periodic torus from weighted circular mean of `rho_nonvac`.

3. `X_unwrap(t)`  
   unwrapped x-centroid from nearest-lift continuity of `X_mod`.

4. `v_x(t)`  
   per-tick velocity trace:  
   `v_x(t) := X_unwrap(t+1) - X_unwrap(t)`.

5. `v_mean`  
   mean velocity over fixed window `[t_burn, t_burn + T_meas)`.

6. `I_h` (impulse hamming)  
   exact hamming count of coefficient differences between:
   - unperturbed initialization (`E0_control`),
   - perturbed initialization (`E1/E2/E3`),  
   at fixed particle/profile.

7. `delta_v`  
   `v_mean(perturbed) - v_mean(control)` for matched fold/profile/particle.

8. `m_est`  
   candidate inertial estimator:  
   `m_est := I_h / |delta_v|` when `|delta_v| > eps`, else undefined.

9. `K_est`  
   candidate kinetic estimator:  
   `K_est := 0.5 * m_est * max(0, v_perturbed^2 - v_control^2)`.

## 3. Geometry Requirement

To limit short-box artifacts, required profile set must satisfy:

1. include at least one strongly elongated profile with `size_x / max(size_y,size_z) >= 10`,
2. include at least one large off-axis 3D profile (`size_y >= 11` and `size_z >= 11`).

Canonical first-pass profiles:

1. `elongated_1d_x41`: `(41,1,1)`,
2. `elongated_3d_offaxis_x41_y11_z11`: `(41,11,11)`.

## 4. Perturbation Protocol

Energy bands are fixed and preregistered:

1. `E0_control`: no explicit kick, no shell seeding.
2. `E1_center_kick`: center basis kick.
3. `E2_center_plus_shell1`: center kick + coherent shell-1 vacuum seed (+x).
4. `E3_center_plus_shell2`: center kick + coherent shell-1 and shell-2 seeds (+x).

Operator index (`op_idx`) is selected by preregistered ranking:

1. evaluate candidate `op_idx` set across fold variants,
2. score by median `|delta_v|`,
3. select highest score (tie-break: smallest `op_idx`).

## 5. Robustness Gates

### 5.1 Fold-order gate

For each particle/profile/energy:

1. velocity span across fold variants <= `velocity_span_tol`,
2. delta-velocity span across fold variants <= `delta_velocity_span_tol`,
3. nonzero `delta_v` sign consistent across folds.

If these fail, the case is not promotable.

### 5.2 Cross-shape gate

For matched particle/energy across at least two elongated profiles:

1. relative gap in median `delta_v` <= 0.35,
2. relative gap in median `m_est` <= 0.50.

These thresholds are first-pass; tightening requires prereg update.

## 6. Artifact Contract

Required artifacts:

1. script: `cog_v2/calc/build_operational_kinematics_mass_energy_v1.py`
2. tests: `cog_v2/calc/test_operational_kinematics_mass_energy_v1.py`
3. json: `cog_v2/sources/operational_kinematics_mass_energy_v1.json`
4. markdown: `cog_v2/sources/operational_kinematics_mass_energy_v1.md`

Schema id:

`operational_kinematics_mass_energy_v1`

## 7. Lean Scope (next)

Lean formalization target for this RFC:

1. well-definedness of centroid unwrap map under finite lattice traces,
2. determinism of measurement map under fixed kernel/profile/order,
3. positivity properties of `I_h`, and domain condition for `m_est`.

Numerical robustness thresholds remain simulation-level checks.

## 8. Non-goals

This RFC does not:

1. claim absolute mass calibration to SI units,
2. claim relativistic energy closure,
3. resolve gravitational coupling,
4. prove uniqueness of the chosen estimator forms.

## 9. Promotion Criteria

Promote draft to active when all are present:

1. replay-stable artifact with required schema fields,
2. fold-order gate outcomes explicitly reported for every case,
3. cross-shape comparisons reported for every particle/energy lane,
4. at least one independent skeptic pass confirming no post-hoc retuning.

## 10. Targeted Lock Strategy (Tractable-First)

Execution order for lock attempts:

1. run broad first-pass suite to identify shape-robust lanes,
2. select only shape-robust lanes for long-horizon reruns,
3. ablate transients by stabilization detector on velocity and e000-share windows,
4. require post-transient multiple-cycle stability before lock recommendation.

Reference targeted artifact contract:

1. script: `cog_v2/calc/build_operational_kinematics_targeted_lock_v1.py`
2. tests: `cog_v2/calc/test_operational_kinematics_targeted_lock_v1.py`
3. source JSON: `cog_v2/sources/operational_kinematics_targeted_lock_v1.json`
4. source markdown: `cog_v2/sources/operational_kinematics_targeted_lock_v1.md`

This lane is the canonical way to obtain tractable lock evidence before external
large-compute replication campaigns.

## 11. Targeted Mass Lock Lane

Mass lock uses impulse-response windows (not post-transient zero-mean tails):

1. compute `delta_v_impulse` on fixed early window after perturbation,
2. compute `m_est := I_h / |delta_v_impulse|`,
3. enforce fold-span and cross-shape mass robustness gates.

Reference artifact contract:

1. script: `cog_v2/calc/build_operational_mass_targeted_lock_v1.py`
2. tests: `cog_v2/calc/test_operational_mass_targeted_lock_v1.py`
3. source JSON: `cog_v2/sources/operational_mass_targeted_lock_v1.json`
4. source markdown: `cog_v2/sources/operational_mass_targeted_lock_v1.md`

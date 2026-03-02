# v3 Lorentz Emergence Literature Synthesis (v1)

Date: 2026-03-02  
Owner: COG Core  
Scope: Practical constraints for choosing a v3 kernel that can yield Lorentz-like behavior at mesoscale.

## 1. Executive Summary

Main takeaway:

1. Discrete micro-updates do not need to be Lorentz-invariant at one-tick scale.
2. The kernel should be judged by whether Lorentz-like behavior emerges under coarse-graining.
3. In prior discrete-physics literature, the strongest successes come from explicit enforcement of:
   - locality,
   - homogeneity,
   - isotropy,
   - stable propagation bands,
   - scale-aware validation.

For v3 this means:

1. stop using tick-1 arrival saturation as evidence of isotropy,
2. require a mesoscale Lorentz battery with multi-distance and multi-direction probes,
3. promote kernels by mesoscale closure quality, not by short-run score alone.

## 2. What the Literature Supports

## 2.1 QCA / quantum-walk line

Recurring pattern:

1. discrete rules recover Weyl/Dirac/Maxwell only after strong structural constraints,
2. Lorentz-like behavior appears in low-momentum or long-wavelength limits,
3. lattice choice and symmetry are decisive.

Implication for v3:

1. emergent closure should be tested in a regime where multiple lattice steps are traversed,
2. directional slope equality and linear travel-time scaling are first-pass proxies.

## 2.2 Causal-set line

Recurring pattern:

1. random discretization can avoid preferred-frame artifacts statistically,
2. fixed regular grids can imprint directional bias unless carefully controlled.

Implication for v3:

1. if fixed-grid kernels plateau on directional artifacts, introduce controlled stochastic channel policies
   or schedule mixing and measure whether anisotropy drops at scale.

## 2.3 Lattice-gas / hydrodynamic CA line

Recurring pattern:

1. isotropy is engineered, not assumed,
2. velocity-set geometry and moment constraints determine continuum closure quality.

Implication for v3:

1. `cube26` is a stronger base than `axial6`,
2. channel-class schedules should be evaluated as multiplicative analogs of geometric weighting,
3. promotion should require scale-stable isotropy, not single-scale isotropy.

## 3. Specific Risks in Current v3 Runner

Observed issues:

1. many runs saturate first-arrival at tick 1, collapsing useful speed discrimination,
2. isotropy metric reports `1.0` even when transport class is still two-front-balanced with poor detector behavior,
3. scoring can overvalue stationary or quasi-stationary locks that do not help Lorentz closure.

Risk statement:

1. current gate pass on isotropy is necessary but not sufficient; it can be a false pass under saturated probes.

## 4. Mesoscale Lorentz Closure Criteria for v3

Define mesoscale:

1. distances large enough that `t(d)` spans multiple ticks and avoids immediate-arrival saturation.

Required measurements:

1. multi-distance travel-time linearity:
   - measure first-arrival or centroid-arrival over `d in {6, 10, 14, 18, 22, ...}`,
   - fit `t(d) = a + b d`,
   - track residuals.
2. multi-direction slope consistency:
   - axis, face-diagonal, body-diagonal, and sampled off-axis directions,
   - compare fitted `b` values and confidence intervals.
3. wavefront shape isotropy:
   - second-moment tensor eigenvalue spread of support envelope at matched times.
4. scale persistence:
   - repeat on at least two box sizes and two detector margins.

Pass concept:

1. kernel is Lorentz-like-ready only if these metrics remain bounded and improve or hold under scale increase.

## 5. Kernel-Selection Implications

Immediate policy:

1. reweight ranking toward mesoscale transport closure,
2. penalize detector-failed two-front classes in Lorentz lane,
3. demote stationary locks for Lorentz scoring.

Candidate-family expectations:

1. `K0` uniform `cube26` is baseline.
2. `K1` deterministic channel schedule may reduce directional bias if cadence is balanced.
3. `K2` seeded stochastic gating may mimic isotropic averaging at mesoscale.
4. `K3+` are justified only if `K0-K2` fail mesoscale closure.

## 6. Recommended Lorentz Battery Artifact

Planned script:

1. `cog_v3/calc/build_v3_lorentz_closure_battery_v1.py`

Planned outputs:

1. `cog_v3/sources/v3_lorentz_closure_battery_v1.json`
2. `cog_v3/sources/v3_lorentz_closure_battery_v1.md`

Required fields:

1. `kernel_candidate_id`
2. `stencil_id`
3. `channel_policy_id`
4. `direction_set_id`
5. `distance_set`
6. `fit_slope_by_direction`
7. `fit_residual_summary`
8. `front_tensor_eigen_spread`
9. `scale_comparison_summary`
10. `lorentz_closure_score`

## 7. Decision Rule

1. Do not promote weak/chirality interpretation lanes until a kernel clears mesoscale Lorentz battery.
2. If no candidate clears battery after bounded search budget, pivot kernel architecture before deeper particle claims.

## 8. Reference Set (used for synthesis)

1. Meyer, D. A. (1996), QCA and lattice gas viewpoint: `arXiv:quant-ph/9604003`
2. Bialynicki-Birula, I. (1994), Weyl/Dirac/Maxwell on lattice automata: `PhysRevD.49.6920`
3. Bisio et al. (2016), Weyl/Dirac/Maxwell from QCA principles: `arXiv:1601.04832`
4. Arrighi et al. (2014), discrete Lorentz covariance constructions: `arXiv:1404.4499`
5. Bibeau-Delisle et al. (2013), deformed relativity in QCA context: `arXiv:1310.6760`
6. Bombelli, Henson, Sorkin (2006), discreteness and Lorentz compatibility: `arXiv:gr-qc/0605006`
7. Dowker, Henson, Sorkin (2003), Lorentz invariance and discreteness: `arXiv:gr-qc/0311055`
8. Surya (2019), causal set review: `arXiv:1903.11544`
9. Frisch, Hasslacher, Pomeau (1986), isotropic lattice-gas methods: `PhysRevLett.56.1505`

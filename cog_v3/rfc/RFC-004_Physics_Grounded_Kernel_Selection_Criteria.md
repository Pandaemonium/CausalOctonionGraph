# RFC-004: Physics-Grounded Kernel Selection Criteria

Status: Draft  
Date: 2026-03-02  
Owner: COG Core  
Depends on:
- `cog_v3/rfc/RFC-001_Ideal_Structure_and_Stable_Motif_Search_in_Octavian240_SharedPhase.md`
- `cog_v3/rfc/RFC-002_Seeded_Event_Order_FailFast_and_Photon_Chirality_Hypotheses.md`
- `cog_v3/rfc/RFC-003_e000_Anchor_Chirality_and_C_Asymmetry_Test_Contract.md`
- `cog_v3/python/kernel_octavian240_multiplicative_v1.py`

## 1. Purpose

Define how v3 selects the "proper" kernel from competing kernel variants using:

1. physics-first hard constraints,
2. measurable empirical gates,
3. reproducible promotion/rejection rules.

This RFC is a kernel-selection contract, not a closure claim on any particle.

## 2. Problem

Current search results show persistent failure modes:

1. photon lane remains `two_front_balanced` with low detector exclusivity,
2. anisotropy remains high across orientation probes,
3. chirality proxies remain near zero.

We need a disciplined way to decide which kernel modifications are physically credible
and worth compute.

## 3. Kernel Candidate Definition

A kernel candidate is identified by:

1. neighborhood geometry and stencil (`axial6`, `cube26`, etc.),
2. channel inclusion policy (uniform, deterministic masks, stochastic masks),
3. event order policy,
4. local update structure (single-pass vs staged),
5. optional local auxiliary state (orientation/memory/chiral selectors),
6. measurement model used for detector-level claims.

Each candidate gets a unique `kernel_candidate_id`.

## 4. Physics Principles to Preserve

## 4.1 Causality

Requirements:

1. update at tick `t+1` may depend only on permitted data at tick `t`,
2. no acausal lookahead.

Proxy checks:

1. dependency graph audit,
2. replay determinism under fixed seed.

## 4.2 Algebraic Consistency

Requirements:

1. state alphabet remains closed under kernel multiplication rules,
2. update remains multiplication-only for this lane.

Proxy checks:

1. closure scans over required operation set,
2. explicit contract tests in CI.

## 4.3 Finite Propagation

Requirements:

1. information front speed is finite and bounded by kernel locality.

Proxy checks:

1. detector arrival-time envelopes from localized seeds.

## 4.4 Isotropy as Lorentz-Proxy Prerequisite

Requirement:

1. no severe preferred-axis artifacts in long-wavelength transport.

Proxy checks:

1. orientation-matched speed proxies (`axis`, `face-diagonal`, `body-diagonal`),
2. anisotropy ratio `v_max / v_min`.

Note:

1. Lorentz symmetry is not claimed directly here; isotropy and linear arrival behavior
   are treated as required prerequisites.

## 4.5 Chirality Discipline

Requirement:

1. parity-odd effects, if present, must arise from explicit kernel structure and be measurable.

Proxy checks:

1. mirror panels (`M` vs `P(M)`),
2. conjugation panels (`M` vs `C(M)`),
3. effect sign stability.

## 4.6 Measurement-Layer Consistency

Requirement:

1. wave-layer occupancy and detector-layer events must be distinguished explicitly.

Proxy checks:

1. twin-detector exclusivity metrics,
2. front-class labeling (`one_front_dominant`, `two_front_balanced`, `diffuse_nonpropagating`).

## 4.7 Mesoscale Lorentz-Closure Principle

Requirement:

1. Lorentz-like behavior is not required at one-tick microscale,
2. Lorentz-like behavior must emerge by mesoscale under coarse-grained observables.

Definitions:

1. microscale: single/few-tick local update behavior,
2. mesoscale: multi-distance propagation regime where arrival times span multiple ticks and
   avoid immediate-arrival saturation.

Proxy checks (mandatory for Lorentz lane):

1. multi-distance linearity:
   - fit `t(d) = a + b d` over `d` sets that avoid tick-1 saturation,
2. multi-direction slope consistency:
   - compare `b` across axis/face/body and off-axis direction samples,
3. wavefront isotropy tensor:
   - bounded eigenvalue spread for support-envelope second moments,
4. scale persistence:
   - qualitative stability of above metrics across at least two box scales.

Decision implication:

1. passing microscale isotropy alone is insufficient for kernel promotion.

## 4.8 Exploratory Scale-Envelope for Lorentz Violation (Investigation Line, Non-Binding)

Status:

1. This subsection is an investigation line, not a hard gate contract.
2. It is intended to guide search strategy and reporting while evidence accumulates.

Motivation:

1. v3 microscale updates are allowed to be anisotropic,
2. anisotropy should decay with coarse-graining if Lorentz-like behavior is emergent.

Define exploratory LV proxy:

1. `epsilon_LV(ell) = max(directional_slope_spread, normalized_t(d)_nonlinearity, front_tensor_anisotropy)`.

Exploratory decay model:

1. `epsilon_LV(ell) <= epsilon_0 * (ell / ell_0)^(-alpha)`,
2. initial reference values for investigation:
   - `ell_0 = 10^2 * l_P`,
   - `epsilon_0 = 1e-1`,
   - target trend `alpha > 0`.

Exploratory milestone ladder (subject to revision):

1. `10^2-10^6 l_P`: `epsilon_LV <= 1e-2`,
2. `10^6-10^10 l_P`: `epsilon_LV <= 1e-4`,
3. `10^10-10^14 l_P`: `epsilon_LV <= 1e-6`,
4. `10^14-10^18 l_P`: `epsilon_LV <= 1e-8`,
5. `10^18-10^20 l_P` (proton-neighborhood extrapolation lane): `epsilon_LV <= 1e-10` (minimum exploratory target), preferred `1e-12` class if supported.

Usage rule:

1. do not treat this ladder as validated truth until repeated fits show stable `alpha`,
2. report confidence intervals on fitted `alpha` and extrapolated `epsilon_LV` values.

## 5. Selection Gates

Kernel candidates are evaluated in ordered gates. Failing an earlier gate blocks later promotion.

## 5.1 Gate 0: Contract Integrity (Hard)

Must pass:

1. deterministic replay with fixed seed,
2. convention-id and metadata integrity,
3. closure/causality checks.

Fail action:

1. reject candidate immediately.

## 5.2 Gate 1: Transport Viability

Must show:

1. nontrivial propagation or stable recurrence above vacuum baseline,
2. no immediate universal collapse into noise.

Fail action:

1. demote to archive unless candidate has a unique theoretical reason to retain.

## 5.3 Gate 2: Detector-Layer Photon Viability

Must show:

1. stable wave transport class and measurable detector behavior,
2. detector exclusivity above baseline noise floor in targeted panels.

Pass conditions:

1. `one_front_dominant` with high exclusivity, or
2. `two_front_balanced` with high exclusivity and robust coherence.

Fail action:

1. keep as transport-only candidate; do not label photon-like.

## 5.4 Gate 3: Isotropy Threshold

Must show:

1. anisotropy ratio improves versus baseline,
2. no worsening under modest box scaling.

Exploratory threshold:

1. `v_max / v_min <= 2.0` for provisional keep,
2. tighter thresholds are required for later promotion.

Fail action:

1. route to isotropy-focused kernel redesign lane.

Additional Lorentz-lane clause:

1. Gate 3 pass is provisional until mesoscale Lorentz battery metrics pass:
   - non-saturated distance set,
   - directional slope consistency,
   - acceptable linear-fit residuals.
2. kernels failing mesoscale closure remain non-promotable even if `v_max / v_min` is favorable.

## 5.5 Gate 4: Chirality Signal

Must show:

1. stable nonzero `A_chi` under mirrored panels,
2. sign consistency across reruns.

Fail action:

1. keep candidate for non-chiral lanes only.

## 6. Kernel Scoring Matrix

For candidates that pass Gate 0, compute a comparison score:

1. transport quality (20 percent),
2. detector exclusivity quality (20 percent),
3. isotropy quality (25 percent),
4. chirality quality (15 percent),
5. robustness under seed/scale perturbation (10 percent),
6. compute efficiency (10 percent).

Notes:

1. score is ranking-only, not a substitute for hard-gate checks,
2. any hard-gate failure overrides score.

## 7. Candidate Families to Test

Priority order:

1. `K0`: uniform `cube26` baseline,
2. `K1`: deterministic channel-class schedules (axis/face/corner cadence),
3. `K2`: seeded stochastic channel gating (reproducible probabilities),
4. `K3`: orientation-tag local state with multiplicative gating,
5. `K4`: two-stage update (transport then local interaction),
6. `K5`: one-step local memory augmentation.

Rationale:

1. `K1/K2` are closest multiplicative analogs of geometric weighting without addition,
2. `K3-K5` are added only if `K1/K2` cannot reduce anisotropy or improve exclusivity.

## 8. Rejection and Promotion Rules

Reject if either holds:

1. fails Gate 0 integrity checks,
2. repeatedly degrades isotropy/exclusivity versus baseline without compensating gains.

Provisional promotion (`supported_kernel_candidate`) requires:

1. passing Gates 0-3,
2. clear improvement over current default in at least one primary lane,
3. no major regression in other primary lanes.

Default promotion (`default_kernel`) requires:

1. passing Gates 0-4 with replicated results,
2. stable artifact package and test reproducibility.

## 9. Artifact Contract

Planned scripts:

1. `cog_v3/calc/build_v3_kernel_selection_matrix_v1.py`
2. `cog_v3/calc/test_v3_kernel_selection_matrix_v1.py`

Planned outputs:

1. `cog_v3/sources/v3_kernel_selection_matrix_v1.json`
2. `cog_v3/sources/v3_kernel_selection_matrix_v1.md`

Required fields:

1. `kernel_candidate_id`
2. `kernel_profile`
3. `convention_id`
4. `event_order_policy`
5. `stencil_id`
6. `channel_policy_id`
7. `front_balance`
8. `detector_exclusivity`
9. `anisotropy_metrics`
10. `A_chi`
11. `A_C`
12. `gate_results`
13. `replay_hash`
14. `lorentz_distance_set`
15. `lorentz_fit_slope_by_direction`
16. `lorentz_fit_residual_summary`
17. `lorentz_front_tensor_eigen_spread`
18. `lorentz_scale_comparison`

## 10. Immediate Execution Plan

1. freeze current baseline candidate as `K0_cube26_uniform_v1`,
2. implement `K1` deterministic channel-class schedules with 2-3 cadence variants,
3. implement `K2` seeded stochastic gating with fixed probability grid,
4. run mesoscale Lorentz battery on `K0-K2` using non-saturated distance sets,
5. run kernel selection matrix and publish gate outcomes with Lorentz battery fields,
6. select top surviving kernel family for deeper particle search.

Execution ordering note:

1. weak/chirality interpretation lanes are secondary until at least one kernel
   clears provisional mesoscale Lorentz closure.

## 11. Non-Claims

This RFC does not claim:

1. we already have Lorentz symmetry,
2. we already have physical photons/neutrinos/electrons,
3. any single metric is sufficient for kernel truth.

It only defines a physics-grounded decision protocol for kernel selection.

## 12. Literature-Grounded Constraints

This section records the external math/physics constraints that shaped this RFC.
It exists to prevent drift toward purely ad hoc kernel tuning.

## 12.1 Nonassociative Gauge Leads (Majid and related)

Findings:

1. Nonassociative gauge structures can be formulated systematically via cochain/associator data
   rather than hand-written exceptions.
2. Moufang-loop-based gauge constructions show octonion-like multiplicative structure can support
   field-like dynamics and nontrivial solution classes.

Kernel implication:

1. If heuristic channel policies (`K0-K2`) plateau, prioritize one structured kernel branch whose
   update constraints are derived from explicit associator/cocycle rules.
2. Keep this branch in the same gate framework (do not bypass Gate 0-4).

## 12.2 Emergent Relativity in Discrete Dynamics (QCA/QW line)

Findings:

1. Lorentz-like closure appears in constrained discrete models when locality, homogeneity,
   and isotropy are enforced jointly.
2. Closure is generally a long-wavelength/mesoscale property, not a one-tick property.
3. Lattice/graph geometry strongly controls directional artifacts.

Kernel implication:

1. Maintain `cube26` as primary isotropy lane.
2. Require multi-distance and multi-direction mesoscale tests before claiming Lorentz-like behavior.
3. Treat tick-1-saturated probe outcomes as non-diagnostic.

## 12.3 Discreteness and Lorentz Compatibility (causal-set guidance)

Findings:

1. Discreteness does not force Lorentz breaking in principle.
2. Fixed finite-valency structures can still embed preferred-direction artifacts if uncorrected.

Kernel implication:

1. Favor kernels that reduce anisotropy with scale rather than those that only look isotropic at one box size.
2. Use scale-persistence as a hard promotion condition.

## 12.4 Classical Isotropy Engineering (lattice-gas guidance)

Findings:

1. Continuum-like symmetry in lattice methods is engineered by moment-balance constraints.

Kernel implication:

1. Use channel-class schedules/gating as multiplicative analogs of geometric weighting.
2. During kernel synthesis, explicitly target:
   - zero net drift (first-moment balance),
   - isotropic second-moment behavior,
   - bounded higher-moment anisotropy proxies.

## 12.5 v3 Decision Synthesis

1. Lorentz-like closure is a mesoscale gate, not a cosmetic metric.
2. Weak/chirality interpretation lanes remain secondary until mesoscale Lorentz battery passes.
3. Kernel promotion requires both:
   - empirical gate success,
   - literature-consistent structural justification.

## 13. Primary Source Set

1. Majid (2005), nonassociative gauge on octonionic spaces: `https://arxiv.org/abs/math/0506453`
2. Ootsuka, Tanaka, Loginov (2005), nonassociative/Moufang gauge: `https://arxiv.org/abs/hep-th/0512349`
3. Meyer (1996), QCA/lattice gas: `https://arxiv.org/abs/quant-ph/9604003`
4. Bialynicki-Birula (1994), Weyl/Dirac/Maxwell lattice automata: `https://doi.org/10.1103/PhysRevD.49.6920`
5. D'Ariano, Perinotti et al. (2016), QCA free-field derivations: `https://arxiv.org/abs/1608.02004`
6. Arrighi, Facchini, Forets (2014), discrete Lorentz covariance in QW/QCA: `https://doi.org/10.1088/1367-2630/16/9/093007`
7. Dowker, Henson, Sorkin (2003), discreteness and Lorentz phenomenology: `https://arxiv.org/abs/gr-qc/0311055`
8. Bombelli, Henson, Sorkin (2006), discreteness without symmetry breaking: `https://arxiv.org/abs/gr-qc/0605006`
9. Frisch, Hasslacher, Pomeau (1986), isotropy engineering in lattice-gas CA: `https://doi.org/10.1103/PhysRevLett.56.1505`
10. Furey (2016, 2019), algebraic SM/chirality structure: `https://arxiv.org/abs/1611.09182`, `https://arxiv.org/abs/1910.08395`

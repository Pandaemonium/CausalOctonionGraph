# RFC-004: Physics-Grounded Kernel Selection Criteria

Status: Draft  
Date: 2026-03-02  
Owner: COG Core  
Depends on:
- `cog_v3/rfc/RFC-001_Ideal_Structure_and_Stable_Motif_Search_in_Octavian240_SharedPhase.md`
- `cog_v3/rfc/RFC-002_Seeded_Event_Order_FailFast_and_Photon_Chirality_Hypotheses.md`
- `cog_v3/rfc/RFC-003_e000_Anchor_Chirality_and_C_Asymmetry_Test_Contract.md`
- `cog_v3/rfc/RFC-009_S960_Phase_Fibered_E8_Symmetry_Model.md`
- `cog_v3/sources/v3_comprehensive_symmetry_kernel_lit_review_v2.md`
- `cog_v3/sources/v3_s960_lit_action_backlog_v1.md`
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

## 2.1 Symmetry Interpretation Layer (from RFC-009)

For v3 kernel selection, adopt the `RFC-009` interpretation:

1. `S960` has a useful point-set symmetry model (phase-fibered octavian shell),
2. point-set symmetry and multiplication symmetry are not the same thing,
3. geometric symmetry is used to generate candidates and panel tests,
4. kernel claims must be validated by multiplication-respecting dynamics.

Practical implication:

1. passing a geometric mirror/rotation panel is supportive evidence,
2. but promotion still requires Gate 0-5 performance in this RFC.

## 2.2 Multi-Lane Objective Separation

Problem:
1. a single aggregate score can hide incompatible objectives (e.g., two-front photon transport vs one-front detector exclusivity).

Policy:
1. score and monitor at least three lanes separately:
   - transport lane (`wave_transport_class`, isotropy, recurrence),
   - detector lane (exclusivity, arrival asymmetry),
   - chirality lane (mirror-panel asymmetry stability).
2. do not promote a kernel on one lane by silently failing another lane's contract.

Plain-English:
One number is not enough. Different physics questions need different scoreboards.

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

## 4.9 Clock-Aware Structural Viability (from RFC-009)

Purpose:
1. Use S960 cycle-class structure as an additional physics-grounded selection signal.

Definitions:
1. order classes: `1,2,3,4,6,12`,
2. `clock_signature(t)`: normalized occupancy histogram over order classes at tick `t`,
3. `clock_signature_drift`: windowed distance between post-transient signatures.

Kernel relevance:
1. good kernels should preserve nontrivial high-order lanes (`12/6`) long enough to support motif formation,
2. avoid immediate sink collapse into one dominant class,
3. avoid unstructured diffusion across all classes.

Plain-English:
If the kernel instantly kills all rich clocks, stable motifs are unlikely. If it keeps too much random clock chaos, motifs are also unlikely. We want a middle regime where clock structure stabilizes.

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

## 5.6 Gate 5: Clock-Structure Gate

Must show (post-transient windows):
1. bounded `clock_signature_drift`,
2. no immediate single-class collapse,
3. no persistent full-class noise plateau,
4. at least one viable candidate with stable recurrence trend under this kernel.

Fail action:
1. demote kernel from motif-discovery priority even if earlier gates look acceptable.

## 6. Kernel Scoring Matrix

For candidates that pass Gate 0, compute a comparison score:

1. transport quality (20 percent),
2. detector exclusivity quality (20 percent),
3. isotropy quality (25 percent),
4. chirality quality (15 percent),
5. clock-structure quality (10 percent),
6. robustness under seed/scale perturbation (10 percent),
7. compute efficiency (10 percent).

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

1. passing Gates 0-3 and Gate 5,
2. clear improvement over current default in at least one primary lane,
3. no major regression in other primary lanes.

Default promotion (`default_kernel`) requires:

1. passing Gates 0-5 with replicated results,
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
19. `clock_signature_series`
20. `clock_signature_drift`
21. `clock_collapse_flag`
22. `clock_noise_plateau_flag`

## 10. Immediate Execution Plan

1. freeze current baseline candidate as `K0_cube26_uniform_v1`,
2. implement `K1` deterministic channel-class schedules with 2-3 cadence variants,
3. implement `K2` seeded stochastic gating with fixed probability grid,
4. run mesoscale Lorentz battery on `K0-K2` using non-saturated distance sets,
5. run lane-separated scoring (transport/detector/chirality) and publish all three leaderboards,
6. run kernel selection matrix and publish gate outcomes with Lorentz + clock fields,
7. select top surviving kernel family for deeper particle search.

Execution ordering note:

1. weak/chirality interpretation lanes are secondary until at least one kernel
   clears provisional mesoscale Lorentz closure.

## 10.1 Distilled Backlog from Recent S960 Literature Reviews

Scope:
1. This subsection converts external review notes into testable kernel work.
2. Only items with concrete measurement hooks are included.

Sources:
1. `sources/s960_particle_morphology_search.md`,
2. `sources/s960_ca_lorentz_lit_review.md`,
3. `sources/s960_chirality_emergence_lit_review.md`,
4. `sources/s960_cyclic_loops_rotation_lit_review.md`,
5. `sources/s960_complex_phase_octavian_lit_review.md`.

### A. Promote immediately (high utility, low ambiguity)

1. Replace chirality-only spatial proxy with algebra-aware panel metrics:
   - add left-vs-right evolution comparison panel,
   - add associator-activity summary over trajectory windows,
   - keep existing spatial asymmetry metric as secondary.
2. Keep lane separation hard:
   - transport lane may show two-front occupancy,
   - detector lane must still test exclusivity directly,
   - no automatic photon rejection from occupancy shape alone.
3. Prioritize seed-bank stratification by measured structure:
   - order class,
   - conjugation tier,
   - family class.
4. Run Lorentz battery only on non-saturated distance sets and report fit residuals.
5. Add `effective C12` probe on order-12 motifs:
   - test whether measured observables exhibit stable 12-step phase class structure.
6. Add explicit automorphism-gap measurement:
   - compute multiplication-preserving relabeling set for current convention,
   - compare against geometric panel groups.

### B. Keep as exploratory hypotheses (require explicit falsification tests)

1. Causal-invariance-based Lorentz claims:
   - treat as hypothesis until confluence-like macro tests pass repeatedly.
2. Direct map from E6/F4/McKay interpretations to kernel truth:
   - keep as symmetry prior, not as promotion evidence.
3. Specific particle-identification claims from one-node motifs:
   - keep as candidate labels only until replay and panel gates pass.
4. Non-split phase-extension kernels:
   - keep as exploratory branch only after baseline split-model diagnostics are mature.

### C. Operational acceptance rule for literature-derived ideas

An idea from literature is promotable to this RFC only if all hold:
1. it defines a measurable observable,
2. it can be computed with current artifacts,
3. pass/fail criteria can be stated before running,
4. it does not bypass Gate 0-5.

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

## 12.6 Chirality No-Go Constraint (Practical)

From Nielsen-Ninomiya/Ginsparg-Wilson/domain-wall/overlap literature:
1. lattice chirality claims require explicit anti-artifact controls,
2. mirror-pair and doubling checks are mandatory before labeling a lane as genuinely chiral.

Kernel implication:
1. treat chirality as an operationally fragile claim until replayed across controls.

## 12.7 Coarse-Graining Constraint (Practical)

From QCA/CA coarse-graining literature:
1. mesoscale closure requires anisotropy to decay under block scale, not just look acceptable at one scale.

Kernel implication:
1. reject candidates where block-scale anisotropy does not improve monotonically in the tested range.

## 12.8 Review-Hygiene Constraint (Practical)

From recent internal review synthesis:
1. use literature to generate testable priors, not closure claims,
2. separate "mathematical analogy" from "validated kernel behavior",
3. mark each imported idea as:
   - `validated_in_kernel`,
   - `test_ready`,
   - `speculative`.

Kernel implication:
1. promotion decisions may use only `validated_in_kernel` evidence.

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

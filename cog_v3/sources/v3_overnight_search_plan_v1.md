# v3 Overnight Search Plan (v1)

Date: 2026-03-02  
Owner: Codex (autonomous overnight run)  
Kernel lane: `cog_v3_octavian240_multiplicative_v1`  
Convention: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`
Default stencil: `cube26` (isotropy-first lane)

## 1. Mission

Primary objective for this overnight run:

1. find a strong photon-candidate motif class,
2. test one or more chiral kernel variants for neutrino-candidate discovery,
3. if neutrino candidate quality is sufficient, start electron-candidate search.

Photon interpretation policy for this run:

1. two-front wave-layer propagation is allowed,
2. "single photon" behavior is tested at detection layer using twin-detector exclusivity metrics.

Secondary objective:

1. improve search methodology with targeted literature checks and strategy revisions.

## 2. Success Criteria

Night is successful if at least one of the following is achieved:

1. `supported_propagating_loop_candidate` in photon lane with robust directional coherence,
2. `supported_two_front_photon_candidate` with high detector exclusivity in twin-detector panels,
3. nonzero repeatable chirality asymmetry (`A_chi`) in neutrino lane under a tested chiral kernel,
4. at least one `stationary_or_slow_propagating` higher-drag candidate worth promotion review for electron lane.

## 3. Run Architecture

Use repeated batches. Each batch has four phases:

1. think/choose next experiment,
2. run code,
3. score outputs and update shortlist,
4. decide next batch.

No blind long run without intermediate scoring.

Operational corrections now applied:

1. detector panels use one-shot absorbing logic with deterministic tie handling,
2. isotropy probes run on cubic boxes (equal axis distances),
3. event-order label is explicit (`synchronous_parallel_v1`) for current accelerated lane,
4. kernel selection is matrix-driven (`K0`, `K1`, `K2`) instead of single-policy looping,
5. stall auto-pivot triggers every 40 non-improving batches (seed-basin rotation).

## 4. Batch Order

### Batch A: Photon-first baseline and front taxonomy

1. run seeded-order motif scans with fail-fast on photon-oriented seeds,
2. default to `cube26` stencil for isotropy-first search,
3. keep periodic `axial6` audits only as control checks (not primary),
4. evaluate:
   - `v_group`,
   - `coh_dir`,
   - `vol_stab`,
   - `front_balance`,
   - `double_hit_rate`,
   - `detector_exclusivity`,
   - directional isotropy score (`axis` vs `face-diagonal` vs `body-diagonal`),
   - recurrence confidence.
5. keep top candidates by composite score.

Promotion gate from Batch A:

1. at least one candidate with:
   - high directional coherence and bounded support variance, or
   - two-front-balanced transport with high detector exclusivity,
2. and acceptable directional isotropy (no severe axis-locking).

### Batch B: Photon stress tests

1. rerun top photon candidates on:
   - one larger box,
   - one alternate seeded random stream,
   - one explicit twin-detector absorbing setup.
2. drop candidates that collapse under small perturbation.

### Batch C: Neutrino lane with chiral kernels

Test at least two chiral variants against same seed sets:

1. `chiral_gate_v1`: strict left-only weak gate (`epsilon=0`),
2. `chiral_gate_v2`: soft suppression (`epsilon>0` small).

For each variant:

1. run mirror panels (`M` vs `P(M)`),
2. compute `A_chi`,
3. run conjugation panels (`M` vs `C(M)`), compute `A_C`,
4. retain only sign-stable asymmetries across reruns.

Promotion gate from Batch C:

1. repeatable nonzero asymmetry with survival/recurrence not collapsing.

### Batch D: Electron lane (conditional)

Only if Batch C passes:

1. expand support and drag-targeted seeds,
2. search for higher-latency, stable recurring motifs,
3. prioritize candidates with:
   - longer recurrence period,
   - stronger e000-coupled stabilization behavior,
   - retained coherence under mild perturbation.

## 5. Fail-Fast and Compute Discipline

Fail-fast is enabled for broad scans:

1. abort when decay metrics stay below thresholds for sustained windows,
2. always save checkpoint + abort reason.

No fail-fast on top-10 candidates in confirmation reruns.

Fixed horizon for broad scans, adaptive horizon only for top candidates.

## 6. Literature Interleave Plan

Every 2-3 compute batches:

1. run a focused literature query on one immediate blocker and one long-horizon topic,
2. summarize one actionable change,
3. apply or reject with reason.

Topic priority:

1. discrete chirality implementations in lattice/automata,
2. finite-size scaling and coarse-graining for intractable scales,
3. coherent propagating packet stability criteria,
4. discrete isotropy and emergent Lorentz-like behavior on cubic stencils.

Long-horizon priority lanes (always active):

1. Bayesian priors and active-search policies for sparse motif discovery,
2. coarse-graining/renormalization strategies for triplet-scale structures,
3. surrogate modeling (cheap predictors) to reduce expensive full-kernel runs,
4. symmetry-aware seed generation and equivalence-class pruning,
5. uncertainty quantification and preregistration-friendly reporting patterns.
6. multiplicative analogs of geometric weighting for face/edge/corner channels.

Cadence split:

1. 50 percent of lit cycles: immediate blockers for current run decisions,
2. 50 percent of lit cycles: long-horizon capabilities and roadmap enablers.

Documentation requirement per lit cycle:

1. append short findings to `cog_v3/sources/v3_lit_review_log_v1.md`,
2. if a finding changes medium/long-term strategy, update
   `cog_v3/sources/v3_long_horizon_research_backlog_v1.md`,
3. if a finding implies immediate implementation work, add to next batch notes.

## 6.1 Lorentz-Like Recovery Program (cube26)

Goal:

1. maximize emergent isotropy so long-wavelength dynamics can approach Lorentz-like behavior.

Core diagnostics:

1. directional speed anisotropy:
   - launch matched motifs along axis, face diagonal, body diagonal,
   - compute `v_axis`, `v_face`, `v_body`,
   - track anisotropy ratios `v_face/v_axis`, `v_body/v_axis`,
2. wavefront sphericality proxy:
   - compare second-moment tensor eigenvalues of active support,
3. arrival-time linearity:
   - detector panels at multiple distances, fit `t(d)` and residuals,
4. dispersion consistency:
   - compare group-velocity proxies across orientations for same seed family.

Discrimination rules:

1. reject hard axis-locked candidates even if recurrence is high,
2. prioritize candidates with stable detector exclusivity and low directional anisotropy,
3. treat anisotropy regressions as blockers requiring kernel/search adjustment.

Multiplicative-weight analog options (no addition allowed):

1. multiplicity scheduling:
   - include face/edge/corner messages at different tick frequencies over a cycle,
2. stochastic channel gating:
   - probabilistically include edge/corner channels with fixed seed (reproducible),
3. phase-gated masks:
   - deterministic phase cycle that controls which channel classes are active.

Selection policy:

1. start with uniform cube26 inclusion,
2. only introduce gating schedules if isotropy diagnostics stall.

## 7. Output Artifacts (Per Batch)

1. machine-readable result JSON in `cog_v3/sources`,
2. markdown summary with:
   - tested params,
   - top candidates,
   - rejected reasons,
   - next-step decision.

Required fields in every output:

1. `kernel_profile`,
2. `convention_id`,
3. `event_order_policy`,
4. `global_seed`,
5. `replay_hash`,
6. `stencil_id`,
7. `anisotropy_metrics`.

## 8. Decision Rules

1. If photon lane repeatedly fails either detector exclusivity or isotropy checks, pause and inspect kernel assumptions before scaling search.
2. If chiral variants produce asymmetry but kill stability, tune chirality gate strength before widening search.
3. If no neutrino-like candidate emerges, continue photon and singleton-informed morphology search and defer electron lane.
4. If strong neutrino candidate appears, allocate remaining compute to electron lane immediately.

## 9. Morning Deliverable Package

1. ranked candidate table (photon, neutrino, electron lanes),
2. strongest candidate traces with key metrics,
3. photon front-taxonomy summary (`one_front_dominant` vs `two_front_balanced`) with detector exclusivity,
4. isotropy panel outcomes (`v_axis`, `v_face`, `v_body`, anisotropy ratios),
5. chirality panel outcomes (`A_chi`, `A_C`),
6. what changed in kernel/search settings and why,
7. recommendation for next day:
   - continue,
   - pivot,
   - or tighten falsification.

## 10. Intuition Map (What I Will Actually Follow Overnight)

This section is the explicit reasoning prior behind the search. It is a working
prior, not a closure claim.

### 10.1 Global intuition

1. The useful motifs will be rare but structured, not random.
2. Multiplication-only dynamics imply exact finite-state determinism, so "chaos"
   at this scale usually means long transients plus long eventual cycles.
3. Most random seeds should decay into vacuum-like behavior quickly; this is signal,
   not failure, because it sharpens the contrast for true coherent motifs.
4. If a candidate survives long horizons only under one narrow setup, it is likely
   an artifact and not a particle-class motif.

### 10.2 Photon intuition

1. A photon-like class should be propagation-first:
   - high directional coherence,
   - minimal or low-support core,
   - low drag signatures,
   - weak directional anisotropy across equivalent launch orientations.
2. I will treat "packet coherence despite local fluctuations" as more important than
   perfect voxel-by-voxel shape preservation.
3. Symmetric two-front emissions are not automatic failures. I will classify them as
   potentially physical if detection-layer exclusivity remains high under stress tests.
4. I will search for an orientator effect:
   - specific `Q240` content coupled to phase state that stabilizes directional drift.
5. If no robust directed class appears, but two-front classes remain detector-exclusive,
   I will treat that as a viable photon lane and not force one-front assumptions.
6. If neither one-front nor two-front-exclusive classes survive stress, I will treat
   this as evidence that the kernel may be missing a chirality/selection ingredient.
7. If exclusivity survives but anisotropy remains high, I will treat that as an
   isotropy problem (not a photon-null result) and prioritize cube26 gating studies.

### 10.3 Neutrino intuition

1. Neutrino-like motifs should be "nearly transparent":
   - small support,
   - long survival,
   - weak interaction response except under the weak/chiral gate.
2. I expect neutrino candidates to look closer to photon candidates than to electron
   candidates in pure kinematics, but differ in chiral interaction asymmetry.
3. I will prioritize motifs that remain coherent at high propagation speeds while
   showing stable `A_chi` asymmetry in mirror tests under chiral kernels.
4. If asymmetry appears only when stability collapses, I will interpret that as an
   over-aggressive chiral gate and tune gate strength before broadening search.

### 10.4 Electron intuition

1. Electron-like motifs should show higher drag and stronger self-anchoring than
   photon/neutrino lanes.
2. I expect:
   - slower propagation (or stationary recurrence with transport under kick),
   - stronger coupling to e000-anchor observables,
   - more complex recurrence structure than simple short cycles.
3. I will not begin broad electron search unless neutrino lane yields at least one
   stable chiral candidate, because that validates the interaction gate architecture.
4. I will reject candidates that only appear in tiny boxes and vanish immediately under
   one-step scale-up.

### 10.5 Artifact intuition (what will likely fool us)

1. Boundary-locking:
   motifs that look periodic only because boundaries feed them.
2. Event-order aliasing:
   motifs that "work" for one seed but collapse under minimal seed perturbation.
3. Stencil overfitting:
   motifs that exist only in one stencil class and fail cross-stencil checks.
4. Early transient mirage:
   motifs that seem coherent for short windows then wash out.

These will be tracked explicitly as rejection reasons.

### 10.6 Coarse-graining intuition (for larger structures)

1. Direct Planck-to-femtometer simulation is intractable, so I will treat robust
   mesoscopic motif classes as coarse-grained primitives.
2. If small motifs exhibit stable renormalized descriptors under box scaling
   (period class, drift class, support compactness), that is actionable evidence for
   scale bridging.
3. I will periodically test whether candidate descriptors are stable under controlled
   coarse-grain maps instead of requiring exact microstate identity.

### 10.7 How this intuition changes during the night

This is a living document. I will revise priors based on evidence:

1. If photon candidates repeatedly fail directionality, I will elevate kernel-structure
   concerns and reduce brute-force expansion.
2. If chiral asymmetry stabilizes, I will shift more compute to neutrino and then electron.
3. If no lane gives robust candidates, I will spend more cycles on targeted literature
   checks and model revision proposals rather than raw search volume.

### 10.8 Logging rule for intuition updates

For each overnight revision, I will append:

1. `prior_before`,
2. `evidence_observed`,
3. `decision_change`,
4. `expected_impact`,
5. `next falsification check`.

This keeps interpretation auditable and prevents drift into ad hoc tuning.

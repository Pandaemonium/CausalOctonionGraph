# Stable Motif Search Campaigns Across Domains: Literature Review and Practical Guide (v2)

Date: 2026-03-02
Owner: COG Core
Status: Draft (`test_ready` campaign guide; no closure claims)

## 1) Goal

Build a search campaign that can discover, verify, and rank stable (or metastable) motifs in a very large deterministic discrete system where:
- exact brute force is infeasible at full scale,
- truly interesting motifs are rare,
- many candidates die quickly,
- verification cost is high.

This guide focuses on algorithmic tactics from adjacent fields (Boolean network attractors, cellular automata discovery, rare-event simulation, quality-diversity optimization, and adaptive scheduler design), then maps them into a concrete search architecture for your motif program.

## 2) Literature Findings (What Transfers Cleanly)

## 2.1 Exact + symbolic attractor methods are the calibration backbone

What literature shows:
- SAT-based attractor finding scales much farther than naive state graph expansion in Boolean network settings.
- Trap-space / most-permissive abstractions can reduce complexity while preserving key attractor logic.

Why this matters for your search:
- You need a guaranteed-correct micro-regime to calibrate every heuristic.
- If your candidate pipeline cannot recover known exact micro attractors, downstream search quality is untrustworthy.

Operational takeaway:
- Keep a permanent exact lane (small boxes, short horizons) to generate "truth sets".
- Use that lane to evaluate false positive/negative rates of all fast filters.

Key sources:
- Dubrova & Teslenko (2009), SAT attractors: https://arxiv.org/abs/0901.4448
- Skodawessely & Klemm (2010), asynchronous attractors: https://arxiv.org/abs/1008.3851
- Chatain et al. (2018), most-permissive semantics: https://arxiv.org/abs/1808.10240
- Moon et al. (2022), minimal trap-space complexity: https://arxiv.org/abs/2212.12756
- Zanudo & Albert (2015), control via network dynamics: https://doi.org/10.1371/journal.pcbi.1004193

## 2.2 CA object discovery succeeds via campaign engineering, not one optimizer

What literature shows:
- High-impact CA discoveries (e.g., spaceships) relied on constrained state-graph/de Bruijn style search plus heavy pruning and canonicalization.
- Evolutionary search can find collision structures/gliders, but only with strong representation and evaluation pipelines.

Why this matters:
- Stable motifs in your system are analogous to CA moving objects/oscillators in terms of rarity and deceptive local neighborhoods.

Operational takeaway:
- Build a dedicated motif canonicalizer early.
- Separate discovery from verification lanes.

Key sources:
- Eppstein (2000/2002), de Bruijn style spaceship search: https://arxiv.org/abs/cs/0004003
- Sapin & Bull (2008), evolutionary CA logic gates: https://doi.org/10.25088/ComplexSystems.17.4.321
- Alfonseca & Soler Gil (2011), GA for Life-like initial conditions: https://doi.org/10.25088/ComplexSystems.21.1.57

## 2.3 Quality-Diversity is better than single-objective search for unknown motif classes

What literature shows:
- MAP-Elites and descendants outperform pure objective optimization when the objective is deceptive or underspecified.
- Heterogeneous emitters and archive-based search improve coverage and robustness.

Why this matters:
- You do not yet know a single scalar "motif quality" that captures physical relevance.
- You need broad discovery across behavior classes, not just one score peak.

Operational takeaway:
- Use a descriptor archive (period, drift vector, recurrence profile, anisotropy, chirality proxies, etc.).
- Optimize for both quality and coverage.

Key sources:
- Mouret & Clune (2015), MAP-Elites: https://arxiv.org/abs/1504.04909
- Cully (2020), ME-MAP-Elites: https://arxiv.org/abs/2007.05352
- Fontaine & Nikolaidis (2022), CMA-MAE: https://arxiv.org/abs/2205.10752
- Cully & Demiris (2017), modular QD framework: https://arxiv.org/abs/1708.09251

## 2.4 Rare-event methods are critical when target motifs are very low probability

What literature shows:
- Weighted Ensemble (WE), Forward Flux Sampling (FFS), and Adaptive Multilevel Splitting (AMS) reduce variance and cost for rare transitions vs naive Monte Carlo.
- The central design variable is the progress coordinate/interface schedule.

Why this matters:
- Stable motif formation likely has narrow funnels in seed space.
- Uniform random seeding wastes budget.

Operational takeaway:
- Define staged interfaces for "motif-likeness".
- Clone/resample candidates that cross interfaces; terminate low-probability lines early.

Key sources:
- Huber & Kim (1996), weighted ensemble: https://doi.org/10.1016/S0006-3495(96)79552-8
- Allen, Frenkel, ten Wolde (2006), FFS efficiency analysis: https://doi.org/10.1063/1.2198827
- Cerou, Guyader, Rousset (2019), AMS overview: https://doi.org/10.1063/1.5082247
- Brehier et al. (2015), AMS unbiasedness: https://arxiv.org/abs/1505.02674

## 2.5 Adaptive compute schedulers dominate static budgets in expensive search

What literature shows:
- Early stopping + adaptive allocation (Successive Halving/Hyperband style) provides large speedups.
- Bandit/Bayesian schedulers outperform fixed splits when arm quality is unknown.

Why this matters:
- Most motif candidates decay quickly.
- Long rollouts should be reserved for the top tail.

Operational takeaway:
- Use staged budgets: very cheap probe -> medium validation -> expensive confirmation.
- Apply Thompson/UCB style arm scheduling across strata.

Key sources:
- Hyperband (Li et al., 2018): https://www.jmlr.org/beta/papers/v18/16-558.html
- BOHB (Falkner et al., 2018): https://proceedings.mlr.press/v80/falkner18a.html
- Thompson sampling (Agrawal & Goyal, 2013): https://proceedings.mlr.press/v28/agrawal13.html
- Practical BO (Snoek et al., 2012): https://proceedings.neurips.cc/paper/2012/hash/05311655a15b75fab86956663e1819cd-Abstract.html
- Multi-fidelity BO (Kandasamy et al., 2016): https://arxiv.org/abs/1603.06288

## 2.6 Basin metrics are the right language for robustness

What literature shows:
- Basin volume estimation complements local linear stability and is useful for multistable systems.
- Finite-time basin metrics provide practical robustness indicators under finite budgets.

Why this matters:
- A motif that survives one trajectory is weak evidence.
- You need basin size estimates over perturbation shells and seed neighborhoods.

Operational takeaway:
- Track both asymptotic and finite-horizon basin estimates.
- Promote candidates based on basin robustness tiers, not just survival count.

Key sources:
- Menck et al. (2013), basin stability: https://doi.org/10.1038/nphys2516
- Schultz et al. (2017), finite-time basin stability: https://arxiv.org/abs/1711.03857

## 3) Recommended Search Architecture

Use a 5-lane campaign that runs continuously and shares one artifact schema.

### Lane A: Exact Micro-Truth Lane

Purpose:
- Exhaustive/symbolic attractor census in tractable regimes.

Methods:
- Full state enumeration where feasible.
- SCC/terminal component extraction.
- SAT-based cycle search for larger-but-still-tractable instances.

Outputs:
- Exact attractor ledger.
- Verified basin fractions in micro boxes.

### Lane B: Fast Probe Lane (Fail-fast)

Purpose:
- Kill obviously bad candidates cheaply.

Methods:
- Short rollouts, decay detectors, recurrence proxies, entropy/dispersion checks.
- Cheap anisotropy and drift checks.

Outputs:
- Candidate scorecards with reasons for rejection.

### Lane C: QD Discovery Lane

Purpose:
- Discover diverse motif families rather than one local optimum.

Methods:
- MAP-Elites style archive.
- Descriptor bins (period class, drift class, chirality proxy, clock-shift sparsity, localization width).
- Multi-emitter mutations/crossover templates.

Outputs:
- Elite motif archive and coverage map.

### Lane D: Rare-Event Funnel Lane

Purpose:
- Increase hit rate for very rare motifs.

Methods:
- Interface schedule over motif-likeness score.
- Splitting/resampling across interfaces (WE/FFS/AMS-inspired).
- Restart from successful interface states.

Outputs:
- Transition-path ensembles.
- Empirical probability estimates for reaching high-stability regimes.

### Lane E: Robustness and Promotion Lane

Purpose:
- Convert candidates into testable claims.

Methods:
- Perturbation-shell sweeps (state noise, boundary variants, seed changes).
- Finite-time and long-horizon basin estimates.
- Replicated runs with logged reproducibility metadata.

Outputs:
- Promotion packet with confidence tier.

## 4) Scheduler (How to Spend Compute)

Use hierarchical adaptive allocation:
1. Strata as bandit arms (seed families, orbit classes, motif templates, perturbation classes).
2. Thompson/UCB for arm selection based on observed yield.
3. Hyperband-style early stopping inside each arm.
4. Multi-fidelity rollout depths (cheap -> medium -> expensive).

Practical policy:
- 70% exploit top-yield arms,
- 20% explore under-sampled arms,
- 10% adversarial novelty (explicitly anti-prior).

## 5) Candidate Metrics (Minimal Set)

Record these for every run:
- recurrence_time_estimate,
- survival_ticks,
- drift_vector and drift_speed,
- localization_radius over time,
- anisotropy_index,
- chirality_proxy,
- clock_shift_signature sparsity,
- finite_time_basin_estimate,
- perturbation_robustness_score.

Promotion gate suggestion:
- Passes threshold on both recurrence and robustness,
- Demonstrates basin support above a minimum floor,
- Reproduces under at least one independent seed family.

## 6) Immediate Execution Plan (first week)

1. Lock the artifact schema and deterministic replay metadata.
2. Stand up Lane A truth sets for the smallest 2-3 tractable regimes.
3. Run Lane B + Lane C jointly to fill an initial descriptor archive.
4. Add Lane D splitting interfaces once enough failed/near-miss data exists.
5. Start Lane E only for top 1-5% candidates to control cost.
6. Weekly ablation: remove one tactic at a time and measure yield drop.

## 7) Risks and Mitigations

Risk: Archive gaming (high score but physically irrelevant motifs).
Mitigation: Require physics-facing constraints in promotion gate.

Risk: Overfitting to one kernel or boundary condition.
Mitigation: Multi-panel validation and condition-perturbation tests.

Risk: Scheduler lock-in to early lucky strata.
Mitigation: enforce exploration floor and periodic arm resets.

Risk: False stability from short horizons.
Mitigation: finite-time basin + long-horizon confirmation tiers.

## 8) Notes on Transfer Validity

Inference (explicit):
- Most cited methods were developed in other domains (biology networks, molecular simulation, RL, CA).
- Transfer is algorithmic (search/control/estimation mechanics), not a claim that those systems are mechanistically identical to COG.

## 9) Core References (Primary)

- Dubrova E, Teslenko M. SAT attractor computation. https://arxiv.org/abs/0901.4448
- Skodawessely T, Klemm K. Asynchronous Boolean attractors. https://arxiv.org/abs/1008.3851
- Zanudo JGT, Albert R. Cell fate reprogramming via network control. https://doi.org/10.1371/journal.pcbi.1004193
- Chatain T et al. Most permissive semantics. https://arxiv.org/abs/1808.10240
- Moon K, Lee K, Pauleve L. Minimal trap-space complexity. https://arxiv.org/abs/2212.12756
- Eppstein D. Searching for spaceships. https://arxiv.org/abs/cs/0004003
- Sapin E, Bull L. Evolutionary CA logic gates. https://doi.org/10.25088/ComplexSystems.17.4.321
- Alfonseca M, Soler Gil FJ. Evolving interesting CA initial conditions. https://doi.org/10.25088/ComplexSystems.21.1.57
- Mouret JB, Clune J. MAP-Elites. https://arxiv.org/abs/1504.04909
- Cully A. ME-MAP-Elites. https://arxiv.org/abs/2007.05352
- Fontaine MC, Nikolaidis S. CMA-MAE. https://arxiv.org/abs/2205.10752
- Cully A, Demiris Y. Modular QD framework. https://arxiv.org/abs/1708.09251
- Li L et al. Hyperband. https://www.jmlr.org/beta/papers/v18/16-558.html
- Falkner S et al. BOHB. https://proceedings.mlr.press/v80/falkner18a.html
- Agrawal S, Goyal N. Thompson sampling (linear contextual bandits). https://proceedings.mlr.press/v28/agrawal13.html
- Snoek J, Larochelle H, Adams RP. Practical BO. https://proceedings.neurips.cc/paper/2012/hash/05311655a15b75fab86956663e1819cd-Abstract.html
- Kandasamy K et al. MF-GP-UCB. https://arxiv.org/abs/1603.06288
- Huber GA, Kim S. Weighted-ensemble dynamics. https://doi.org/10.1016/S0006-3495(96)79552-8
- Allen RJ, Frenkel D, ten Wolde PR. FFS efficiency analysis. https://doi.org/10.1063/1.2198827
- Cerou F, Guyader A, Rousset M. AMS perspective/recent results. https://doi.org/10.1063/1.5082247
- Brehier CE et al. AMS unbiasedness. https://arxiv.org/abs/1505.02674
- Menck PJ et al. Basin stability. https://doi.org/10.1038/nphys2516
- Schultz P et al. Finite-time basin stability. https://arxiv.org/abs/1711.03857


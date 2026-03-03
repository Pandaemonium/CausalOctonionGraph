# Stable Motif Search Campaigns: Literature-Grounded Strategy Guide (v1)

Date: 2026-03-02  
Owner: COG Core  
Status: Draft (`test_ready` strategy guide; not a closure claim)

## 1. Purpose

This document summarizes algorithmic tactics from adjacent domains for searching stable motifs / attractors in very large deterministic state spaces, then converts them into an actionable campaign plan for COG-style motif discovery.

Scope:
1. algorithmic strategy, not particle-identity claims,
2. search campaign design, not one-off experiments,
3. methods from any domain if transfer is technically sound.

## 2. Executive Summary

Best strategy is a hybrid, not one method:
1. exact enumeration where tractable,
2. symbolic/satisfiability methods for medium scales,
3. quality-diversity (QD) search for open-ended motif discovery,
4. Bayesian/bandit resource allocation across search strata,
5. basin estimation via stratified Monte Carlo and local perturbation shells,
6. robust replay and symmetry panels before promotion.

This combination is consistently supported across:
1. Boolean network attractor studies (SAT/decomposition/trap-space),
2. cellular automata object search campaigns (de Bruijn + stochastic/evolutionary search),
3. QD optimization literature (MAP-Elites family),
4. rare-event simulation (splitting/WE/FFS line),
5. adaptive resource-allocation methods (bandits/Hyperband/Thompson).

## 3. What Prior Search Campaigns Teach

## 3.1 Exact and Symbolic Attractor Discovery (Boolean network line)

Key message:
1. do exact search at small scales to establish ground truth,
2. use SAT / decomposition / symbolic abstractions to delay state-space explosion.

Useful tactics:
1. SAT-based cycle/attractor finding with bounded-unfolding and loop constraints.
2. SCC/decomposition methods to split large transition systems into smaller subproblems.
3. Trap spaces / stable motifs / most-permissive semantics for attractor localization without full graph expansion.

Transfer to COG:
1. keep small-box exact census as calibration lane,
2. formalize motif predicates as satisfiability constraints where possible,
3. use trap-space-like partial invariants to prune non-viable regions early.

## 3.2 CA Pattern Search Campaigns (spaceships/glider guns)

Key message:
1. massive novelty discovery came from campaign engineering, not one clever heuristic.

Useful tactics:
1. de Bruijn/state-graph inspired constrained search (spaceship search),
2. stochastic/evolutionary sweeps for rare emergent objects (glider gun campaigns),
3. canonicalization/classification layers to deduplicate discoveries and track families.

Transfer to COG:
1. invest in canonical motif signatures and dedup first,
2. maintain separate “discovery” and “verification” lanes,
3. run many cheap candidate probes with fail-fast filters before expensive confirmation.

## 3.3 Quality-Diversity (QD) Search

Key message:
1. when objective is unknown or deceptive, QD often outperforms pure objective optimization.

Useful tactics:
1. MAP-Elites archive over behavior descriptors,
2. CMA-ME / ME-MAP-Elites emitters to mix exploration modes,
3. noisy-domain variants (adaptive sampling) for robust archive updates.

Transfer to COG:
1. build an archive over motif behavior descriptors (period, transport class, chirality proxy, clock signature),
2. maintain elites per descriptor bin,
3. use heterogeneous emitters/operators instead of one mutation policy.

## 3.4 Rare-Event and Path Sampling

Key message:
1. when targets are extremely rare, unbiased brute-force sampling is wasteful.

Useful tactics:
1. splitting / adaptive multilevel splitting for rare pathway discovery,
2. weighted-ensemble / forward-flux style interface progression,
3. cross-entropy style adaptive proposal distributions.

Transfer to COG:
1. define interface levels to target motifs (e.g., recurrence score, panel-stability score),
2. split/resample trajectories crossing higher interfaces,
3. estimate “reachability” of rare motif classes with uncertainty bounds.

## 3.5 Adaptive Resource Allocation

Key message:
1. budget allocation is as important as search operators.

Useful tactics:
1. Thompson sampling/UCB over strata to balance exploration/exploitation,
2. Hyperband-like early stopping for expensive candidates,
3. model-based proposal (Bayesian optimization/QD surrogates) when evaluations are costly.

Transfer to COG:
1. treat seed strata as arms,
2. update posterior success rates online,
3. aggressively stop decaying candidates and reallocate to productive strata.

## 4. Recommended COG Campaign Architecture

## 4.1 Phase A: Ground-Truth Layer (exact where feasible)

Goals:
1. exact attractor/basin results in tractable micro-regimes,
2. validate signatures and metrics before scaling.

Outputs:
1. canonical attractor signature function,
2. exact basin tables for calibration testbeds,
3. mismatch report between exact and heuristic estimators.

## 4.2 Phase B: Descriptor + Archive Layer (QD core)

Define behavior descriptors (example):
1. period class,
2. transport class,
3. detector exclusivity score,
4. chirality metrics (spatial + algebra-aware),
5. clock-signature stability.

Archive policy:
1. keep best candidate per descriptor bin,
2. log novelty distance and survival metadata,
3. track lineage (stepping-stone analysis).

## 4.3 Phase C: Bayesian Stratum Scheduler

Strata examples:
1. seed order-class mix,
2. conjugation tier,
3. phase coherence class,
4. geometry class.

Controller:
1. maintain Beta/Bernoulli or bounded-reward posteriors per stratum,
2. allocate via Thompson sampling,
3. enforce exploration floor to avoid premature lock-in.

## 4.4 Phase D: Basin Estimation Layer

Per attractor candidate:
1. local basin estimate from perturbation shells,
2. global estimate from stratified sampling with importance weights,
3. report credible intervals, not just point estimates.

Use two labels:
1. `local_basin_mass`,
2. `global_weighted_basin_mass`.

## 4.5 Phase E: Promotion and Robustness

Before promotion:
1. deterministic replay hash checks,
2. symmetry panels (rotate/mirror/conjugate),
3. kernel/order robustness spot checks,
4. scale-up drift checks.

Promotion gate:
1. candidate must survive both discovery-lane and verification-lane criteria.

## 5. Campaign Metrics (Minimum Set)

Discovery metrics:
1. new motif families per compute-hour,
2. archive coverage growth,
3. top-k quality improvement rate.

Reliability metrics:
1. replay pass rate,
2. symmetry-panel survival rate,
3. false-positive rate from verification lane.

Basin metrics:
1. local basin mass,
2. global weighted basin mass,
3. interval width (uncertainty).

Allocation metrics:
1. stratum posterior evolution,
2. exploration fraction over time,
3. regret proxy versus uniform allocation baseline.

## 6. Practical Implementation Notes

1. Keep compact row formats for large campaigns (avoid ultra-wide CSV unless required).
2. Canonicalize signatures early (prevents duplicate compute waste).
3. Use fail-fast criteria based on measurable decay/noise indicators.
4. Separate lane logic in code:
   - candidate generation,
   - cheap screening,
   - expensive verification.
5. Store enough metadata for retrospective analysis:
   - RNG seed,
   - convention id,
   - kernel id,
   - panel transform id,
   - termination reason.

## 7. Risks and Mitigations

Risk:
1. overfitting to one descriptor set.
Mitigation:
1. rotate descriptor sets in ablation runs.

Risk:
1. Bayesian scheduler locks in too early.
Mitigation:
1. enforce minimum exploration quota and periodic forced exploration.

Risk:
1. false motif inflation from weak signatures.
Mitigation:
1. canonical signature plus verification lane and replay checks.

Risk:
1. conflating geometric symmetry with multiplication symmetry.
Mitigation:
1. explicit automorphism-gap measurement.

## 8. Immediate `test_ready` Experiments

1. Build a pilot archive with 5-10 descriptor bins and measure discovery throughput vs random search.
2. Run Thompson-allocated vs uniform stratum allocation and compare top-k verified motif yield.
3. Add local perturbation-shell basin estimates for top 20 candidates.
4. Run symmetry-gap benchmark:
   - geometric panel transforms vs multiplication-preserving transforms.
5. Run `effective C12` diagnostics on order-12 sectors as separate hypothesis lane.

## 9. Suggested Deliverables

1. `cog_v3/calc/build_v3_motif_signature_catalog_v1.py`
2. `cog_v3/calc/run_v3_qd_archive_search_v1.py`
3. `cog_v3/calc/run_v3_bayes_strata_scheduler_v1.py`
4. `cog_v3/calc/build_v3_basin_estimates_v1.py`
5. `cog_v3/sources/v3_motif_campaign_dashboard_v1.json`
6. `cog_v3/sources/v3_motif_campaign_dashboard_v1.md`

## 10. Primary Sources

Quality-diversity / search strategy:
1. Mouret & Clune (MAP-Elites, 2015): https://arxiv.org/abs/1504.04909
2. Cully (ME-MAP-Elites, 2020): https://quality-diversity.github.io/papers.html
3. Kent & Branke (BOP-Elites, 2020): https://arxiv.org/abs/2005.04320
4. Sfikas et al. (Monte Carlo Elites, 2021): https://arxiv.org/abs/2104.08781

Novelty search:
1. Lehman & Stanley (2011): DOI 10.1007/978-1-4614-1770-5_3

Boolean network attractors / stable motifs / trap spaces:
1. Dubrova & Teslenko (SAT attractors, 2009/2011): https://arxiv.org/abs/0901.4448
2. SCC decomposition attractor detection (2019): https://doi.org/10.1016/j.scico.2019.05.001
3. Random sampling vs exact enumeration (2009): https://arxiv.org/abs/0904.3948
4. Cell fate reprogramming / stable motif control (2015): https://pmc.ncbi.nlm.nih.gov/articles/PMC4388852/
5. Most permissive semantics (2018): https://arxiv.org/abs/1808.10240

CA pattern search campaigns:
1. Eppstein, spaceship search (2000/2002): https://arxiv.org/abs/cs/0004003
2. Adamatzky et al., stochastic glider-gun search (2010): https://doi.org/10.1007/s11047-009-9109-0

Basin and rare-event methods:
1. Datseris & Wagemakers, basin estimation (2021/2022): https://arxiv.org/abs/2110.04358
2. Menck et al., basin stability (2013): https://www.nature.com/articles/nphys2516
3. Dean & Dupuis, splitting for rare events (2007): https://arxiv.org/abs/0711.2037
4. Cérou & Guyader, adaptive multilevel splitting (2014): https://arxiv.org/abs/1408.6366
5. Cérou et al., AMS asymptotic normality (2018): https://arxiv.org/abs/1804.08494
6. Huber & Kim weighted ensemble (1996): https://pubmed.ncbi.nlm.nih.gov/8770190/

Adaptive budget allocation:
1. Hyperband (2016): https://arxiv.org/abs/1603.06560
2. Thompson sampling tutorial (2017): https://arxiv.org/abs/1707.02038

## 11. What This Document Does Not Claim

1. No claim that these methods prove COG particle identities.
2. No claim that any one method is sufficient.
3. No claim that literature analogies automatically transfer without verification.

This is a strategy map for building a rigorous, data-efficient search campaign.


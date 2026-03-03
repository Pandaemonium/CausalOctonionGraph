# Stable Motif Search: Full Execution Checklist (v1)

Date: 2026-03-02
Owner: COG Core
Status: Active working checklist (`test_ready`)

Use this as the operational checklist for launching and running a stable motif search campaign end-to-end.

## 0) Scope Lock

- [ ] Confirm search objective for this campaign window:
  - [ ] stable stationary motifs
  - [ ] stable propagating motifs
  - [ ] metastable motifs (minimum lifetime threshold)
- [ ] Lock kernel variant(s) under test (e.g., `axial6`, `cube26`, other candidates).
- [ ] Lock state alphabet (e.g., `S960`, `Q240 x C12`) and convention ID.
- [ ] Lock boundary conditions (fixed vacuum default; periodic only for specific tests).
- [ ] Lock event-order policy (seeded deterministic randomized order if selected).
- [ ] Write campaign ID and assumptions into a manifest file.

## 1) Reproducibility + Governance

- [ ] Define canonical run manifest schema:
  - [ ] kernel ID/version
  - [ ] convention ID
  - [ ] alphabet version
  - [ ] geometry and boundary condition
  - [ ] event-order seed
  - [ ] perturbation recipe
  - [ ] stop condition and horizon
- [ ] Ensure each run writes immutable metadata first (before simulation loop).
- [ ] Ensure deterministic replay command exists and is documented.
- [ ] Add artifact naming convention (`campaign/date/lane/batch/candidate`).
- [ ] Add data provenance tags: `generated_by`, `code_sha`, `config_sha`, `timestamp_utc`.

## 2) Artifact Schema (must lock before large runs)

- [ ] Candidate-level row schema is finalized and versioned.
- [ ] Required fields present:
  - [ ] `candidate_id`
  - [ ] `parent_ids` (for evolved candidates)
  - [ ] `lane`
  - [ ] `stratum`
  - [ ] `seed`
  - [ ] `survival_ticks`
  - [ ] `recurrence_estimate`
  - [ ] `drift_vector`
  - [ ] `localization_radius_trace`
  - [ ] `anisotropy_index`
  - [ ] `chirality_proxy`
  - [ ] `clock_shift_signature`
  - [ ] `termination_reason`
- [ ] Compression + chunking format selected (e.g., `csv.gz`, parquet if adopted).
- [ ] Dedup/canonicalization fields finalized (hash of canonical motif representation).

## 3) Baseline Calibration (Lane A: exact micro-truth)

- [ ] Choose 2-3 tractable micro-regimes for exhaustive truth sets.
- [ ] Run exact attractor/loop census in each micro-regime.
- [ ] Compute exact basin fractions for the micro-regimes.
- [ ] Save truth ledgers and test fixtures for pipeline validation.
- [ ] Validate fast filters against truth sets:
  - [ ] false positive rate
  - [ ] false negative rate
  - [ ] ranking correlation with exact outcomes

## 4) Fast Probe Pipeline (Lane B)

- [ ] Implement fail-fast checks:
  - [ ] rapid decay detector
  - [ ] immediate dispersion threshold
  - [ ] recurrence pre-signal threshold
  - [ ] anisotropy sanity bound
- [ ] Implement early-stop reasons with explicit enum values.
- [ ] Verify probe lane throughput benchmark meets target.
- [ ] Ensure probe outputs include rejection diagnostics (not just pass/fail).

## 5) Discovery Archive (Lane C, QD)

- [ ] Finalize descriptor bins for MAP-Elites-style archive:
  - [ ] period class
  - [ ] transport class
  - [ ] chirality proxy class
  - [ ] localization class
  - [ ] clock-signature sparsity class
- [ ] Implement archive update policy (replace by quality + confidence).
- [ ] Add heterogeneous emitters/operators:
  - [ ] local mutation
  - [ ] crossover/template splice
  - [ ] adversarial novelty operator
- [ ] Add novelty metric and archive coverage tracking.

## 6) Rare-Event Funnel (Lane D)

- [ ] Define motif-likeness progress coordinate.
- [ ] Define interface levels (L0 -> Lk).
- [ ] Implement splitting/resampling only at interface crossings.
- [ ] Log lineage graph of split candidates.
- [ ] Validate no bias introduced by implementation bug (sanity tests).

## 7) Robustness + Promotion (Lane E)

- [ ] Define promotion tiers (`candidate`, `provisional`, `robust`, `benchmark`).
- [ ] Define perturbation-shell protocol:
  - [ ] state perturbations
  - [ ] boundary perturbations
  - [ ] seed perturbations
  - [ ] event-order perturbations (if policy requires)
- [ ] Define finite-time basin estimation protocol and confidence intervals.
- [ ] Define long-horizon replay protocol for promoted candidates.
- [ ] Promotion packet template finalized.

## 8) Scheduler + Budgeting

- [ ] Define search strata (arms):
  - [ ] orbit families
  - [ ] seed template families
  - [ ] perturbation families
  - [ ] kernel variant
- [ ] Implement adaptive arm allocation (Thompson/UCB/other chosen policy).
- [ ] Implement staged fidelity budget (short -> medium -> long rollouts).
- [ ] Implement early stopping policy (Hyperband-style rung thresholds).
- [ ] Set exploration floor to avoid lock-in.

## 9) Basin-of-Stability Estimation

- [ ] Define local perturbation neighborhoods for each candidate.
- [ ] Define sampling plan per neighborhood (N and stratification).
- [ ] Estimate:
  - [ ] finite-time basin size
  - [ ] long-horizon survival fraction
  - [ ] sensitivity map by perturbation type
- [ ] Store basin estimates with uncertainty bounds.

## 10) Symmetry + Physics Panels

- [ ] Define symmetry panel tests (rotation/reflection/permutation panels as applicable).
- [ ] Define mesoscale Lorentz-like anisotropy panel:
  - [ ] directional transport comparison
  - [ ] dispersion relation fit residuals
  - [ ] scale-dependent anisotropy trend
- [ ] Define chirality panel:
  - [ ] motif-intrinsic chirality metrics
  - [ ] interaction chirality selection checks
- [ ] Define channel-specific interaction tests (if enabled).

## 11) Search Seeding Strategy

- [ ] Build seed pools by strata:
  - [ ] pure orbit seeds
  - [ ] mixed-orbit seeds
  - [ ] known-interest template seeds (photon-like/neutrino-like/electron-like hypotheses)
  - [ ] adversarial random seeds
- [ ] Assign priors (uniform initially unless evidence supports weighted priors).
- [ ] Version the seed generator and record generator parameters.

## 12) Monitoring + Alerting

- [ ] Real-time progress metrics dashboard:
  - [ ] runs/sec
  - [ ] pass rates by lane
  - [ ] archive coverage growth
  - [ ] promotion rate
  - [ ] compute utilization
- [ ] Add alerts:
  - [ ] stuck scheduler (no novelty growth)
  - [ ] storage pressure
  - [ ] repeated failures by same termination reason
  - [ ] suspiciously perfect repetition (possible bug)

## 13) Data Management

- [ ] Storage budget projection completed for planned run volume.
- [ ] Chunking/rotation policy enabled for long campaigns.
- [ ] Daily compaction job for raw logs -> summarized ledgers.
- [ ] Retention policy for raw vs derived artifacts.
- [ ] Backup or mirror policy for critical promotion packets.

## 14) Verification and QA

- [ ] Unit tests for kernel invariants and replay determinism.
- [ ] Regression tests for metric calculations.
- [ ] Canary runs before large batch launch.
- [ ] Cross-check sample candidates with independent evaluator script.
- [ ] Spot-audit lineage and metadata integrity weekly.

## 15) Operational Cadence

- [ ] Daily:
  - [ ] review throughput and novelty metrics
  - [ ] inspect top new candidates
  - [ ] rebalance scheduler if needed
- [ ] Weekly:
  - [ ] ablation test (remove one tactic, measure delta)
  - [ ] refresh priors using last-week evidence
  - [ ] archive and summarize validated findings
- [ ] Biweekly:
  - [ ] literature refresh focused on current blockers
  - [ ] update campaign strategy document

## 16) Deliverables Checklist (minimum)

- [ ] `campaign_manifest_v1.json`
- [ ] `artifact_schema_v1.md`
- [ ] `exact_micro_truth_ledger_v1.*`
- [ ] `probe_lane_rejection_stats_v1.*`
- [ ] `qd_archive_snapshot_v1.*`
- [ ] `rare_event_lineages_v1.*`
- [ ] `promotion_packets_v1/`
- [ ] `weekly_ablation_report_v1.md`
- [ ] `search_campaign_status_dashboard_export_v1.*`

## 17) Exit Criteria for this Campaign Window

- [ ] At least one candidate reaches `robust` tier under defined promotion gate.
- [ ] Basin estimate reported with uncertainty for top candidates.
- [ ] Mesoscale anisotropy panel executed for promoted candidates.
- [ ] Reproducible replay confirmed from stored manifests.
- [ ] Final campaign summary written with failures + next actions.

## 18) Common Failure Modes (watchlist)

- [ ] "Single-run illusion" (candidate looks stable once but fails under replay).
- [ ] "Archive gaming" (high score, physically irrelevant behavior).
- [ ] "Scheduler lock-in" (early lucky arm monopolizes budget).
- [ ] "Metric drift" (descriptor definitions changed mid-campaign).
- [ ] "Serialization bottleneck" (compute idle, I/O saturated).

## 19) First 48-Hour Boot Sequence

- [ ] Lock schema + manifest.
- [ ] Run micro-truth lane and validate filters.
- [ ] Start probe + QD lanes with conservative budget.
- [ ] Enable scheduler with exploration floor.
- [ ] Start robustness lane only for top 1-5% candidates.
- [ ] Ship first daily status report with blockers and course corrections.


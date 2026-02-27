# MASTER IMPLEMENTATION PLAN V2

Status: Active Draft  
Date: 2026-02-26  
Supersedes: `rfc/MASTER_IMPLEMENTATION_PLAN.md` (historical baseline)

---

## 1. Executive Summary

COG is no longer in the "define basic algebra" phase. The core algebra and kernel contract exist. The current bottleneck is closure quality:
1. turning locked policy into fully proved implementation contracts,
2. enforcing claim governance in CI,
3. separating exploratory physics narratives from promotion-grade evidence.

V2 shifts the project from "build components" to "run a governed proof-and-falsification program."

---

## 2. Holistic Model Snapshot (Current)

## 2.1 Kernel and dynamics (mostly locked)

1. Node state is `NodeStateV2` with `psi : ComplexOctonion Z`, `tickCount`, `topoDepth`, `colorLabel`.
2. Update semantics are locked at policy level in RFC-028:
   - temporal commit `T(psi) = e7 * psi`,
   - multiplicative combine,
   - Markov fold,
   - energy exchange predicate locked.
3. D4/D5 contract language exists, but implementation-level proof wiring is still incomplete in places.

## 2.2 Observer/governance stack (defined, not fully enforced)

1. Projection governance: RFC-044.
2. Equivalence governance: RFC-054.
3. Confinement claim gates: RFC-047.
4. Spin governance and corrected `H subset O` framing: RFC-056.
5. Battery and matrix governance: RFC-049 and RFC-050.

## 2.3 Claim portfolio (mixed maturity)

Observed pattern:
1. foundation claims (Fano/octonion/tick/order) are largely `proved`,
2. high-impact physics claims (Weinberg, strong, Koide closure tracks, generation lift) remain `partial`/`stub`,
3. status hygiene is inconsistent (inline comment-tainted status strings in claim YAMLs),
4. canonical matrix artifact (`claims/CLAIM_STATUS_MATRIX.yml`) is not yet present.

---

## 3. Strategic Assessment

## 3.1 What is strong

1. Discrete-first algebraic core is real and nontrivial.
2. Kernel semantics are materially more concrete than before.
3. Governance direction is now sound (anti-retrofit, profile awareness, reproducibility gates).

## 3.2 What is weak

1. Governance docs are ahead of enforcement scripts/CI.
2. Promotion semantics can still drift without a live matrix + validators.
3. Some RFC and claims artifacts are still treated as narrative instead of gate-driven outputs.
4. Autonomous lab reliability is improved but still not fully normalized to deterministic failure taxonomy and hard acceptance gates.

## 3.3 Highest-risk failure mode

The primary risk is not "wrong algebra."  
It is "status inflation": claims sounding derived before battery/matrix gates are complete.

---

## 4. V2 Program Structure

V2 is split into six workstreams with strict sequencing and explicit handoffs.

## WS-A: Kernel Closure and Contract Proof Wiring

Scope:
1. finalize D4 implementation proofs (`SpawnCompleteness`, `SpawnThenUpdateLaw`) over concrete `applySpawn`,
2. complete D5 implementation-level invariants for canonical observer path,
3. verify no hidden dependence on deprecated v1 state/update paths.

Deliverables:
1. Lean theorem set for D4/D5 implementation closure,
2. deterministic replay fixture for update paths,
3. explicit migration note for any remaining v1 references.

Gate:
1. no new `sorry`,
2. `lake build` clean,
3. one reproducible transition trace hash in Python aligned to Lean contracts.

## WS-B: Claim Governance Enforcement (Matrix + Validators)

Scope:
1. create `claims/CLAIM_STATUS_MATRIX.yml`,
2. implement semantic validator from RFC-050 fields,
3. synchronize matrix rows with current active claims.

Deliverables:
1. matrix file in repo,
2. `scripts/validate_claim_status_matrix.py`,
3. CI fail-on-missing-row and fail-on-missing-required-field.

Gate:
1. every non-archived claim has a matrix row,
2. `supported` status cannot appear without mandatory artifacts.

## WS-C: Battery v2 Implementation

Scope:
1. implement battery runner and schema validator (`RFC-049`),
2. integrate B7 (confinement) and B8 (spin-mode),
3. connect outputs to matrix updater.

Deliverables:
1. `battery_v2_summary.json`,
2. `battery_v2_report.md`,
3. run fingerprint and gate map.

Gate:
1. at least 3 high-value claims re-run through v2,
2. promotion blocked when required families are missing.

## WS-D: Physics Priority Tracks (Evidence-Producing)

Priority order:
1. `WEINBERG-001`: lock and test policy-defined routes only, no post-hoc fit.
2. `STRONG-001`: execute closure tasklist with RFC-047 gating.
3. `KOIDE-001`: treat as constrained search/falsification, not narrative closure.
4. hydrogen/electron-electron toy bridge: only after spin mode + observer declarations are explicit.

Deliverables:
1. per-claim evidence bundles with theorem refs + run artifacts,
2. status updates tied to matrix and battery outputs.

Gate:
1. no claim promotion from prose alone,
2. all high-impact claim updates include artifacts.

## WS-E: Spin Track (RFC-056)

Scope:
1. implement spin-mode governance fields (`spin_mode`, `spin_artifact`, `spin_sensitivity`) in claims and matrix,
2. add operational `label` mode harness,
3. reserve `algebraic` mode for promotion-grade spin claims.

Deliverables:
1. mode-aware spin test harness (`calc/spin_observable.py`, tests),
2. at least one claim explicitly reclassified by `spin_mode`.

Gate:
1. no precision spin claim can be `supported` without `spin_mode: algebraic`.

## WS-F: Autonomous Lab Reliability and Throughput

Scope:
1. complete graph-first orchestrator flow (`manager -> worker -> debugger`),
2. enforce deterministic failure taxonomy and remediation map,
3. enforce safe mode and budget routing policies.

Deliverables:
1. normalized runtime event schema,
2. retry/escalation metrics,
3. nightly artifact bundle for debugging and governance traceability.

Gate:
1. 10 consecutive autonomous rounds without silent task loss,
2. each failed round has classified failure + remediation outcome.

---

## 5. Sequencing and Milestones

## Milestone M0 (2-3 days): Baseline Hygiene Freeze

1. establish claim status normalization (remove inline-comment status variants),
2. create matrix skeleton rows,
3. lock "no status promotion without matrix row" policy.

## Milestone M1 (1-2 weeks): Governance Runtime-Active

1. matrix validator + battery validator wired into CI,
2. B7/B8 implemented and tested on at least one claim each,
3. D4/D5 implementation-level proofs materially advanced.

## Milestone M2 (1-2 weeks): Strong/Weinberg Evidence Sprint

1. run declared policy bundles for WEINBERG and STRONG tracks,
2. publish pass/fail artifacts and uncertainty envelopes,
3. update statuses only through validator-passing changesets.

## Milestone M3 (1 week): Spin + Bound-State Readiness

1. spin label-mode harness complete and reproducible,
2. two-node to bound-state bridge claims explicitly tagged with `spin_mode` and projection profile,
3. go/no-go decision on first hydrogen-bound-state simulation campaign.

---

## 6. Hard Rules (V2 Governance)

1. No claim promotion without matrix row + battery artifact.
2. No post-hoc policy mutation for constant-derivation runs.
3. Projection profile and spin mode must both be declared for spin-sensitive claims.
4. Confinement language requires RFC-047 gate compliance.
5. Canonical kernel remains `C x O` unless a formal replacement RFC is accepted.
6. Any "major architecture change" must include:
   - migration plan,
   - compatibility window,
   - deprecation path,
   - rollback procedure.

---

## 7. Decision Register (Current Recommendations)

1. Keep `C x O` kernel canonical in near term.
   - Rationale: closure and governance debt is larger than representational debt.
2. Continue dual-profile observer policy (`minimal` canonical, `with_sector` explicit).
   - Rationale: stronger baseline claims and cleaner dependency disclosure.
3. Treat spin as governance/observable-layer closure first, algebraic spin second.
   - Rationale: progress without premature kernel churn.
4. Freeze ad hoc running bridges for constants unless policy-locked and mechanism-grounded.
   - Rationale: anti-retrofit discipline.
5. Prioritize enforcement infrastructure over new speculative RFC branches.
   - Rationale: prevents compounding unverifiable claims.

---

## 8. Deliverable Map (Concrete Files)

Core governance:
1. `claims/CLAIM_STATUS_MATRIX.yml` (new)
2. `scripts/validate_claim_status_matrix.py` (new)
3. `scripts/run_battery_v2.py` (new)
4. `scripts/validate_battery_v2.py` (new)

Kernel closure:
1. `CausalGraphTheory/D4D5Contracts.lean` updates
2. `CausalGraphTheory/UpdateRule.lean` updates
3. targeted Lean theorem additions for D4/D5 implementation closure

Spin track:
1. `calc/spin_observable.py` (new)
2. `calc/test_spin_observable.py` (new)

Confinement/strong track:
1. artifacts listed in `rfc/STRONG-001_Closure_Tasklist.md`

---

## 9. Exit Criteria for V2

V2 is considered complete when all hold:
1. matrix exists, validates, and is used as single status source,
2. battery v2 is CI-enforced with B7 and B8 active,
3. D4/D5 implementation-level closure items are no longer policy-only,
4. at least two high-impact claims have status changes backed by full artifact bundles,
5. autonomous lab produces reproducible per-round diagnostics with deterministic failure handling.

---

## 10. Anti-Goals (What V2 Explicitly Does Not Do)

1. does not attempt to finish every open physics RFC immediately,
2. does not replace `C x O` kernel with `C x H x O` in this cycle,
3. does not treat exploratory numeric proximity as derivation,
4. does not allow claim status changes based on dashboard narrative alone.

---

## 11. Immediate Next Actions (This Week)

1. Create `claims/CLAIM_STATUS_MATRIX.yml` and populate rows for all active claims.
2. Implement matrix validator and run it in CI.
3. Implement battery v2 runner skeleton with B7/B8 hooks.
4. Close one D4 implementation theorem pair on concrete `applySpawn`.
5. Backfill `spin_mode` metadata for spin-sensitive claims.


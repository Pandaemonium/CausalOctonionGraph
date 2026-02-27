# RFC-062: Fano Task-Class Scheduler and Role Decoupling for Autonomous Lab

Status: Draft Planning Document  
Date: 2026-02-27  
Owner: Lab Manager + Research Director  
Scope: Orchestrator scheduling policy (task class selection, role assignment, model routing integration)

---

## 1. Executive Summary

The autonomous lab is currently over-assigning tasks to `Lean_Theorems_Expert`, reducing throughput diversity and causing repeated queue patterns.

This RFC proposes a two-stage scheduler:
1. select a **task class** on a 7-node Fano graph,
2. select **role/model** probabilistically within that class.

The design explicitly prevents collapse into a single role while preserving scientific priority and claim-closure pressure.

---

## 2. Problem Statement

Current behavior shows:
1. role collapse (most assignments to Lean workers),
2. duplicate active tasks in the same claim area,
3. weak coupling between task type and manager intent,
4. limited scheduling response to failure modes (no-text outputs, stale tasks, repeated retries).

This produces avoidable delay, higher spend, and lower cross-domain progress.

---

## 3. Design Goals

1. Increase task-type diversity without losing claim closure discipline.
2. Prevent repeated assignment loops.
3. Separate **task type** from **worker role/model**.
4. Preserve governance rigor (`not_claimed`, evidence, validation).
5. Keep scheduling decisions observable and auditable.

---

## 4. Non-Goals

1. This RFC does not redefine scientific claim criteria.
2. This RFC does not replace probabilistic model routing.
3. This RFC does not force one-to-one class-role mappings.

---

## 4.1 Primitive-Closure Overlay (Default Research Mode)

The default mode for frontier research is **primitive closure** over one shared object:

`H7 = {e1..e7 with locked Fano incidence + orientation/sign convention; e0 identity outside H7}`.

Primitive tasks must close exactly one gate:
1. XOR index channel (`i xor j`) for distinct imaginaries.
2. Sign channel from locked orientation table.
3. Left/right handedness sign relation.
4. Deterministic cycle extraction.
5. Support-closure stability predicate.
6. Deterministic artifact replay (`json/csv`).

Each assignment should specify:
1. one primitive ID,
2. one executable verifier command,
3. one artifact path.
4. the dossier fields in `rfc/PRIMITIVE_CLOSURE_TASK_TEMPLATE.md`.

Meta/status tasks are allowed only on cadence (every ~8-12 rounds) or after repeated failures.

---

## 5. Fano Task-Class Graph

Define seven task classes (nodes), mapped to `Fin 7`:

1. `N0`: Lean Formalization
2. `N1`: Physics Simulation / Numerical Experiments
3. `N2`: Pedagogy / Public Explanation
4. `N3`: Long-Term Theory / Architecture
5. `N4`: Lab Self-Improvement (orchestrator + infra)
6. `N5`: Self-Checking / Audits / Verification
7. `N6`: Claim Closure / Integration / Release Readiness

Use canonical Fano lines from `rfc/CONVENTIONS.md` (0-indexed):
1. `(0,1,2)`
2. `(0,3,4)`
3. `(0,6,5)`
4. `(1,3,5)`
5. `(1,4,6)`
6. `(2,3,6)`
7. `(2,5,4)`

Interpretation:
1. classes on a shared line are natural adjacent transitions,
2. line-local transitions get a positive adjacency bonus,
3. non-adjacent transitions remain allowed but lower prior.

---

## 6. Two-Stage Scheduler Contract

### 6.1 Stage A: Task-Class Selection

Given current class `c`, compute class score:

`score(j) = b(j) + w1*backlog(j) + w2*staleness(j) + w3*scientific_value(j) + w4*blocker_pressure(j) + w5*adjacent(c,j) - w6*recent_overuse(j) - w7*cost_pressure(j)`

Where:
1. `adjacent(c,j)=1` if `c` and `j` share a Fano line; else `0`.
2. `recent_overuse(j)` is rolling share over trailing window.
3. `blocker_pressure(j)` increases for classes that resolve active failures.
4. `scientific_value(j)` is manager-priority weighted from active claim roadmap.

Sampling:
1. `P(next=j) = softmax(score(j)/temperature)`.
2. If hard constraints fail, re-sample from feasible set.

### 6.2 Stage B: Role and Model Selection

After class is selected:
1. choose role via `P(role | class)`,
2. choose model via existing probabilistic router `P(model | role, class, features)`.

Critical rule:
1. class selection must not be bypassed by a role default.

---

## 7. Hard Guardrails (Mandatory)

1. Max consecutive assignments of same class: `2`.
2. `N0` (Lean) share cap: `<= 40%` over trailing 20 assignments unless emergency override.
3. Mandatory `N5` (self-check) at least once every 4 rounds.
4. Mandatory `N6` (closure/integration) at least once every 6 rounds.
5. Duplicate active task key (same claim + same gate) blocks new assignment in that class until review.
6. If a worker produces 2 consecutive no-text/no-result outputs, force:
   - one `N4` repair task,
   - one `N5` verification task,
   - reroute next domain task to a different role/model.
7. Primitive-closure share floor: at least `60%` of trailing 20 assignments must map to primitive gates in Section 4.1.
8. Packet integrity: in any 3-task packet, no duplicate primitive gate IDs.
9. Independent audit rule: every primitive packet must include at least one audit task from a different model provider than the author task.

---

## 8. Class-to-Role Priors (Initial)

These are priors, not fixed routing:

1. `N0` Lean: Lean_Theorems_Expert (0.70), Verification_Clerk (0.20), Python_Simulation_Expert (0.10)
2. `N1` Simulation: Python_Simulation_Expert (0.65), Lean_Theorems_Expert (0.20), Verification_Clerk (0.15)
3. `N2` Pedagogy: Pedagogy_Curator (0.70), Web_Content_Writer (0.20), Verification_Clerk (0.10)
4. `N3` Theory: Research_Director_Assistant (0.50), Literature_Researcher (0.30), Lean_Theorems_Expert (0.20)
5. `N4` Self-Improvement: Dashboard_Engineer (0.35), Lab_Manager_Assistant (0.35), Verification_Clerk (0.30)
6. `N5` Self-Checking: Verification_Clerk (0.60), Skeptic_Reviewer (0.25), Lean_Theorems_Expert (0.15)
7. `N6` Closure: Claim_Integrator (0.50), Verification_Clerk (0.30), Pedagogy_Curator (0.20)

Constraint:
1. the worker that authored a change should not be first-choice verifier for that change.
2. remove global default fallback to `Lean_Theorems_Expert`; role must be explicit or class-derived.

Primitive-mode role priors (applied inside `N0/N1/N5` when a primitive gate is requested):
1. Author lanes:
   - `XOR_Gate_Auditor` (0.35)
   - `Python_Simulation_Expert` (0.35)
   - `Lean_Theorems_Expert` (0.30)
2. Audit lane:
   - `Verification_Clerk` (0.60)
   - `XOR_Gate_Auditor` (0.25)
   - `Lean_Theorems_Expert` (0.15)

---

## 9. Data and Telemetry Requirements

Add or extend these artifacts in orchestrator repo:

1. `task_class_registry.yml`
2. `fano_class_scheduler.yml`
3. `router_decisions.jsonl`
4. `class_metrics.json`

Minimum event fields:
1. `round_id`
2. `current_class`
3. `candidate_scores`
4. `chosen_class`
5. `chosen_role`
6. `chosen_model`
7. `hard_constraints_applied`
8. `override_reason` (if any)

---

## 10. Reward and Adaptive Tuning

Per-task reward:

`R = +a1*gate_closed + a2*tests_passed + a3*claim_promotion - b1*rework - b2*timeout - b3*duplicate_assignment - b4*cost_overrun`

Tuning policy:
1. online updates at task completion,
2. weekly parameter review by Lab Manager,
3. cap parameter deltas to avoid instability.

---

## 11. Rollout Plan

### Phase 0: Instrumentation Only (1-2 days)
1. add class labels to current assignments,
2. log hypothetical Fano class decisions in shadow mode.

### Phase 1: Shadow Scheduler (2-4 days)
1. run class selector without dispatch control,
2. compare shadow picks vs actual manager picks,
3. measure projected diversity and closure impact.

### Phase 2: Guarded Activation (3-7 days)
1. activate Stage A class dispatch,
2. keep manual override enabled,
3. enforce hard guardrails.

### Phase 3: Full Integration (1-2 weeks)
1. connect Stage B role/model priors,
2. activate adaptive tuning,
3. publish class-mix and closure metrics on dashboard.

### Phase 4: Primitive-Closure Packets (1 week)
1. enable packeted dispatch (`3-5` microtasks per packet) for primitive gates,
2. enforce independent audit task in each packet,
3. emit packet-level telemetry:
   - primitive IDs covered,
   - verifier pass rate,
   - replay determinism checks.
If manager output is single-task-per-round, execute packets as contiguous `3-5` rounds.

---

## 12. Acceptance Criteria

System is accepted when all hold for a 7-day evaluation window:

1. Lean class share remains in `[25%, 40%]` unless explicit emergency mode.
2. At least 5 of 7 classes receive assignments daily.
3. Duplicate-active-task incidents reduced by at least 70%.
4. No-text-output retry loops reduced by at least 80%.
5. Claim closure throughput is not degraded (equal or improved gate-closure/day).
6. Primitive-closure tasks remain at or above 60% share during active frontier research weeks.
7. At least one deterministic artifact is produced per primitive packet.
8. Cross-provider audit disagreement rate is tracked and remains below agreed threshold.

---

## 13. Risks and Mitigations

1. Risk: over-diversification harms critical-path claims.
   - Mitigation: scientific_value and blocker_pressure terms keep priority pressure.
2. Risk: too many constraints cause scheduler deadlocks.
   - Mitigation: fallback feasible-set relaxer with logged override reason.
3. Risk: role priors become stale.
   - Mitigation: weekly recalibration and drift alerts.

---

## 14. Open Decisions

1. Final cap for Lean class share (`35%` vs `40%`).
2. Trailing window length (`20` vs `30` assignments).
3. Whether `N6` closure tasks can be auto-generated by clerks from matrix diffs.
4. Emergency override governance:
   - who can trigger,
   - max duration,
   - required postmortem note.
5. Primitive packet size: fixed `3` vs adaptive `3-5`.
6. Whether primitive artifacts must be published to `website/data/` in real time or batch mode.

---

## 15. Recommended Immediate Actions

1. Add `task_class` field to assignment objects.
2. Add class picker in shadow mode using this RFC's score function.
3. Remove default-role fallback to `Lean_Theorems_Expert`.
4. Add duplicate-task keying (`claim_id + gate_id + artifact_target`) before dispatch.
5. Add no-text-output recovery policy (2-strike reroute + repair task).
6. Add `primitive_gate_id` to assignment metadata and telemetry.
7. Add packet scheduler support for `3-5` microtasks with one required independent audit task.

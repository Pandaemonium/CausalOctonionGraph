# RFC-055: Uncertainty, Entropy, and Coarse-Graining

Status: Active Draft - Contract Lock Candidate (2026-02-26)
Implements:
- `rfc/MASTER_IMPLEMENTATION_PLAN_V2.md` (WS-D, WS-E)
Companion:
- `rfc/RFC-036_Temperature_as_Coarse_Grained_Interaction_Intensity.md`
- `rfc/RFC-054_Observable_Equivalence_and_Physical_Indistinguishability.md`
Module:
- `COG.Theory.UncertaintyEntropy`
Depends on:
- `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`
- `rfc/RFC-036_Temperature_as_Coarse_Grained_Interaction_Intensity.md`
- `rfc/RFC-042_D4_D5_Implementation_Closure.md`
- `rfc/RFC-051_Scheduler_Semantics_and_Update_Cadence.md`
- `rfc/RFC-054_Observable_Equivalence_and_Physical_Indistinguishability.md`

---

## 1. Executive Summary

COG microdynamics are deterministic; uncertainty and entropy arise from observer coarse-graining, not from stochastic kernel evolution.

This RFC locks:
1. profile-indexed uncertainty semantics,
2. two compatible entropy families,
3. replay-safe measurement contracts,
4. claim-language governance for uncertainty statements.

Core statement:
1. "uncertainty" in COG is a property of information access, not a primitive source term.

---

## 2. Problem Statement

Current project language includes:
1. phase uncertainty (RFC-023),
2. projection profiles (RFC-042/RFC-054),
3. temperature proxy from interaction intensity (RFC-036).

What is missing:
1. one formal bridge from deterministic microstate to observer uncertainty/entropy metrics,
2. one standard for reporting and falsifying entropy claims.

---

## 3. Scope and Non-Scope

In scope:
1. observer-profile uncertainty definitions,
2. entropy computation on projection classes and projected traces,
3. relation-to-temperature hypotheses at coarse-grained level.

Out of scope:
1. introducing stochastic kernel dynamics,
2. claiming thermodynamic laws as proven in COG at this stage,
3. SI/Kelvin calibration (handled under scale-profile governance, RFC-052).

---

## 4. Formal Setup

Let:
1. `M` be microstate space,
2. `Pi_P : M -> Y_P` be projection map for profile `P`,
3. `m_t` be deterministic microstate trajectory under locked scheduler/update,
4. `y_t = Pi_P(m_t)` projected trajectory.

Define profile-equivalence class:
1. `[m]_P = {x in M | Pi_P(x) = Pi_P(m)}` (RFC-054 semantics).

Uncertainty depends on class size/structure, not on non-deterministic updates.

---

## 5. Entropy Functionals (Locked Family)

Two functionals are allowed in v1.

### 5.1 Hidden-state counting entropy

For finite tracked state domain:
1. `H_hidden(P, m) = log |[m]_P|`.

Interpretation:
1. amount of microstate ambiguity remaining after observing profile `P`.

### 5.2 Projected-trace Shannon entropy

For region `R` and window `W`, define empirical distribution over projected symbols/states:
1. `p_P(y ; R, W)`.

Then:
1. `H_proj(P; R, W) = - sum_y p_P(y;R,W) log p_P(y;R,W)`.

Interpretation:
1. coarse-grained variability in observed output stream.

Any entropy claim must declare which functional is used.

---

## 6. Decisions Locked by This RFC

### D1. Deterministic microstate axiom

Kernel-level randomness is excluded in claim-grade runs.

### D2. Profile-indexed uncertainty

Uncertainty/entropy statements are invalid without explicit `pi_obs_profile`.

### D3. Functional declaration requirement

Each entropy result must specify `entropy_functional_id`:
1. `hidden_count_v1` or
2. `projected_shannon_v1`.

### D4. Scheduler lock requirement

Entropy benchmarks must run under canonical scheduler mode (`snapshot_sync_v1`) unless explicitly marked sensitivity-only.

### D5. No energy-from-ignorance claim

Uncertainty does not directly imply physical energy injection.  
Any energy linkage must pass through explicit dynamic observables (for example interaction-rate/temperature proxies).

---

## 7. Relation to Temperature (Testable, Not Locked as Law)

From RFC-036, define `T_proxy(R,W)` as interaction-intensity observable.

Working hypothesis family:
1. increased interaction intensity may correlate with increased projected entropy production rate in some regimes.

Report-only quantities:
1. `dH_proj/dt`,
2. `corr(H_proj, T_proxy)`,
3. lagged correlation diagnostics.

This RFC does not claim universal monotonicity.

---

## 8. Invariants and Sanity Conditions

1. `H_hidden >= 0`.
2. `H_proj >= 0`.
3. Replay determinism: identical input and profile produce identical entropy traces.
4. Profile refinement expectation:
   - richer profile should not increase hidden-state ambiguity for same tracked domain.
5. Metadata completeness:
   - entropy output without region/window/profile is non-promotable.

---

## 9. Claim Metadata Contract

Any claim using uncertainty/entropy language must include:
1. `pi_obs_profile`,
2. `equivalence_mode` (from RFC-054),
3. `entropy_functional_id`,
4. `entropy_region_spec`,
5. `entropy_window_spec`,
6. `scheduler_mode`,
7. `entropy_artifact_ref`.

Optional:
1. `temperature_link_mode` (`none`, `correlative`, `modeled`).

---

## 10. Falsification Gates

### G1. Hidden nondeterminism
If repeated runs differ under fixed inputs/profile, entropy result is invalid.

### G2. Full-state exposure check
If uncertainty claim persists after exposing full microstate fields used by the claim, interpretation is invalid.

### G3. Undeclared functional
Entropy statement without declared functional fails.

### G4. Profile leakage
Comparing entropy numbers across profiles without profile disclosure fails.

### G5. Ad hoc coupling
Temperature-entropy linkage requiring per-scenario fitted parameters is invalid for promotion.

---

## 11. Benchmark Battery (Required)

Minimum benchmark suite:
1. **Vacuum-dominant motif**
   - expected low interaction intensity; baseline entropy behavior.
2. **Mixed interaction motif**
   - nontrivial projected entropy dynamics.
3. **High-load motif**
   - stress test for entropy/temperature proxy correlation claims.

Each benchmark must include:
1. replay hash,
2. profile declaration,
3. entropy functional declaration,
4. window/region declaration.

---

## 12. Implementation Plan

### 12.1 Python

Add:
1. `calc/entropy_profile_scan.py`
2. `calc/test_entropy_profile_scan.py`
3. `calc/entropy_temperature_link_scan.py`
4. `calc/test_entropy_temperature_link_scan.py`

Outputs:
1. `sources/entropy_profile_results.json`
2. `sources/entropy_profile_results.md`

### 12.2 Lean scaffold

Add:
1. `CausalGraphTheory/UncertaintyEntropy.lean`

Initial targets:
1. definitions of profile-equivalence class size on finite state subsets,
2. `hidden_entropy_nonneg`,
3. refinement monotonicity skeleton theorem for hidden ambiguity.

---

## 13. Governance Integration

Integrate with:
1. RFC-050 matrix fields:
   - `entropy_functional_id`,
   - `pi_obs_profile`,
   - `scheduler_mode`.
2. RFC-049 battery:
   - add uncertainty/entropy checks as named battery family.

Promotion rule:
1. entropy-bearing claims cannot be `supported` without benchmark artifact and metadata completeness.

---

## 14. Failure Modes

1. Treating projected variability as ontic randomness.
2. Mixing profiles in one reported entropy sequence.
3. Using entropy numbers without region/window specs.
4. Concluding thermal laws from one motif without declared benchmark coverage.
5. Equating uncertainty with energy absent dynamic mediator observables.

---

## 15. Acceptance Criteria

This RFC is closed when:
1. entropy functionals and metadata contract are implemented,
2. benchmark battery runs reproducibly under canonical scheduler,
3. at least one claim references entropy with full metadata and artifact links,
4. CI validates presence/consistency of uncertainty metadata in relevant claims.

---

## 16. Open Questions

1. Which finite-state domain truncation is most stable for `H_hidden` computation?
2. Should projected entropy be computed per-node, per-region, or both in v1?
3. Which correlation estimators are robust enough for `T_proxy` linkage in discrete short traces?

---

## 17. Decision Register

Locked now:
1. uncertainty is observer/profile dependent,
2. two entropy functional families are canonical in v1,
3. scheduler/profile metadata is mandatory.

Deferred:
1. universal entropy production law claims,
2. thermodynamic-limit statements beyond benchmark-defined motifs.


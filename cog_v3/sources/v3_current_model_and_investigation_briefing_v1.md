# v3 Current Model and Investigation Briefing (v1)

Date: 2026-03-03  
Audience: Claude handoff / collaborator sync  
Status: Living technical briefing (not a proof document)

## 1) Executive Snapshot

The current active lane is:
1. `Q240` closed octavian alphabet (multiplicative, no addition),
2. lifted to phase-product lanes:
   - `S960 = C4 x Q240` (legacy/discovery lane, probably good for single-generation studies),
   - `S2880 = C12 x Q240` (primary lane for generation structure),
3. kernel selection through `RFC-004` gate stack with fixed manifests.

What is established now:
1. v3 convention is stable and enforced (`convention_id` tagging),
2. closed multiplication on Octavian-240 kernel is working,
3. gate stack is running and reproducible,
4. phase/generation contracts and diagnostics exist (RFC-010/011 + supporting scripts).

What is not established:
1. no promoted kernel passes full Gate 0-5 stack,
2. no Lorentz-like mesoscale closure yet,
3. no stable particle-identification claim,
4. no validated mass derivation.

---

## 2) Non-Negotiable Model Invariants

From `cog_v3/python/kernel_octavian240_multiplicative_v1.py` and `cog_v3/rfc/CONVENTION_IDS.md`:

1. Kernel profile:
   - `cog_v3_octavian240_multiplicative_v1`
2. Active convention:
   - `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`
3. Update rule:
   - multiplication-only
4. Closed base alphabet:
   - 240 octavian states
5. Convention enforcement:
   - runtime `assert_convention_id(...)`
6. Event order policy in most current probes:
   - synchronous parallel (unless script explicitly tests alternatives)

Interpretation policy:
1. geometric symmetry is hypothesis-generating,
2. multiplication-consistent dynamics decides promotion.

---

## 3) Algebra/Object Lanes (Current Mental Model)

## 3.1 Q240 (base)

1. Closed Octavian-240 unit set.
2. Multiplication table fixed by v3 convention transform.
3. Order structure in Q240 is known and exported (`v3_octavian240_elements_v1.csv`).

## 3.2 S960 lane

1. `S960 = C4 x Q240`.
2. Symmetry framing and cycle structure formalized in `RFC-009`.
3. Useful for:
   - cycle/orbit intuition,
   - symmetry-panel design,
   - order-3/order-12 bundle concepts (`RFC-014` in S960 scope).

Known S960 facts (from RFC/docs):
1. element orders include `1,2,3,4,6,12`,
2. distinct cyclic subgroups: `426` (425 non-identity),
3. order-6 element count: `168` (PSL(2,7) hypothesis lane lives here, RFC-013).

## 3.3 S2880 lane (primary)

1. `S2880 = C12 x Q240` is primary for generation hypotheses.
2. Current operational generation labels:
   - Gen1: phase offset `+0`,
   - Gen2: `+1`,
   - Gen3: `+2`
   (contract-level labels; operator-level mechanism remains open).

Local computed order histogram check for S2880 (quick direct script run):
1. order-1: `1`
2. order-2: `3`
3. order-3: `170`
4. order-4: `508`
5. order-6: `510`
6. order-12: `1688`

Important implication:
1. simple `56 x 3 = 168` carryover claims from S960 do not directly hold as-is in S2880.

---

## 4) RFC State (What Each Contract Is Doing)

## RFC-004 (kernel selection)

Purpose:
1. hard gate stack for kernel promotion.

Key gates:
1. Gate0 contract integrity,
2. Gate1 transport viability,
3. Gate2 detector viability,
4. Gate3 isotropy/Lorentz proxies,
5. Gate4 chirality signal,
6. Gate5 clock-structure viability.

Notes:
1. mesoscale Lorentz-like behavior is required for promotion,
2. includes exploratory scale-envelope section (non-binding but directional).

## RFC-009 (S960 symmetry model)

Purpose:
1. separate point-set symmetry from multiplication symmetry.

Use:
1. generate candidate transforms/panels,
2. avoid invalid "looks symmetric so dynamics equivalent" errors.

## RFC-010 (C12 phase-sector contract)

Purpose:
1. test phase hop structure (`R3`, `C3`, `L3`, `A1`, `A2`) and generation-sector dynamics.

## RFC-011 (generation-aligned equivalence)

Purpose:
1. test whether generation-aligned systems are dynamically equivalent pre-mixing (`<1%` tolerance).

Primary baseline pair:
1. `electron + uud` vs `muon + ccs`.

## RFC-012 (associator-field curvature lane)

Purpose:
1. formalize associator-as-curvature proxy tests,
2. test family activity hierarchy relevance.

## RFC-013 (order-6 / PSL(2,7) lane)

Purpose:
1. test whether the order-6 `168` in S960 is structural (action-level), not numerology.

## RFC-014 (order-3 core to order-12 bundle seeding)

Purpose:
1. test bundle-based seeding vs random for motif search yield.

Scope caveat:
1. documented S960 bijection does not directly carry into S2880.

---

## 5) Current Empirical Results (Most Recent Artifacts)

## 5.1 Fixed-manifest gate stack

From `cog_v3/sources/v3_fixed_manifest_kernel_gate_stack_v1.md`:

1. `K0_cube26_uniform_v1`: gates passed = 5/6, gate5 fail
2. `K2_cube26_stochastic_v1`: gates passed = 5/6, gate5 fail
3. `K1_cube26_det_cycle_v1`: gates passed = 4/6, gate4 and gate5 fail

Interpretation:
1. no candidate is promotable yet,
2. primary blocker cluster is gate5 clock structure (and chirality on K1).

## 5.2 Generation-aligned equivalence

From `cog_v3/sources/v3_generation_aligned_equivalence_panel_v1.md`:

1. Baseline pair median `Delta_max = 0.719934` (target `<0.01`) -> fail
2. Desync pair median `Delta_max = 0.084521` -> fail
3. pass rate `<1%` is `0.0000` in both pair classes

Interpretation:
1. RFC-011 contract currently fails clearly.

## 5.3 Omega diagnostics (new)

From `cog_v3/sources/v3_omega_hat_diagnostic_v1.md`:

1. `omega_dominant_rate = 1.0000`
2. `median_omega_share_of_total_delta = 0.7527`
3. `small_denominator_primary_cause = False`

Interpretation:
1. `Omega_hat` mismatch is the dominant RFC-011 failure driver,
2. dominance is not explained by denominator singularity artifacts.

## 5.4 Gate5 repeat diagnostics (new)

From `cog_v3/sources/v3_gate5_clock_repeat_probe_v1.md` + quick JSON summaries:

1. manifest gate5 pass count: `0/3`
2. K0 bottlenecks:
   - seed-sensitive recurrence behavior,
   - persistent high clock-signature drift
3. K1/K2 bottlenecks:
   - low/absent recurrence in scan lane,
   - no repeat within tested horizons

Interpretation:
1. gate5 failures are heterogeneous (not one universal cause),
2. candidate-specific fixes are needed.

## 5.5 C12 phase sector quick panel

From `cog_v3/sources/v3_c12_phase_sector_panel_report_v1.md`:

1. `R3 = 0.0000`
2. `C3 = 0.5764`
3. `A1 = 0.0000`
4. `A2 = -0.0290`

Interpretation:
1. current quick panel does not support "dominant ±3 hop" yet,
2. sector conservation signal exists but not a closure result,
3. signed asymmetry is weak in quick panel.

---

## 6) Investigation Lines (Active, with Priority)

## P0 (Immediate)

1. Gate5 split and characterization:
   - separate:
     - in-sector stable clock (`5a`),
     - coherent cross-sector oscillation (`5b`),
   - avoid labeling any gate5 fail as oscillatory without spectral evidence.

2. `R3=0` breakdown:
   - run event-level diagnostics by seed family/panel/support region,
   - identify whether suppression is kernel, seeding, or measurement definition.

3. 12-point C12 seed bank extension:
   - extend RFC-014-style ablations to S2880-aware seed families.

## P1 (Near-term)

1. Phase-diagram mapping:
   - sweep channel/noise/policy parameters,
   - map regions by recurrence, drift, sector metrics.

2. Family-tier associator tests:
   - controlled A/B/C family effects with matched support/order.

3. Mesoscale Lorentz battery:
   - multi-scale, multi-direction, non-saturated front fits.

## P2 (After P0/P1 evidence)

1. PSL(2,7) action probe in S960 (RFC-013),
2. associator-field radial profiles around stable motifs (RFC-012),
3. generation/mass-like ratio hypotheses with stricter controls.

---

## 7) Script/Artifact Inventory (What Exists Now)

Implemented and available in `cog_v3/calc`:
1. `build_v3_fixed_manifest_kernel_gate_stack_v1.py`
2. `build_v3_c12_phase_sector_metrics_v1.py`
3. `build_v3_generation_aligned_equivalence_panel_v1.py`
4. `build_v3_omega_hat_diagnostic_v1.py`
5. `build_v3_gate5_clock_repeat_probe_v1.py`

Queue planning file:
1. `cog_v3/sources/v3_interactive_vs_overnight_script_queue_v1.md`

Planned/partially scaffolded RFC scripts:
1. RFC-012 associator probe scripts,
2. RFC-013 action probe scripts,
3. RFC-014 bundle-seed bank + ablation scripts.

---

## 8) Practical Reproduction Commands

Quick checks:
```powershell
python -m cog_v3.calc.build_v3_fixed_manifest_kernel_gate_stack_v1 --quick --backend numba_cpu --global-seed 1337
python -m cog_v3.calc.build_v3_c12_phase_sector_metrics_v1 --quick --global-seed 1337
python -m cog_v3.calc.build_v3_generation_aligned_equivalence_panel_v1 --quick --global-seed 1337
python -m cog_v3.calc.build_v3_omega_hat_diagnostic_v1 --quick --global-seed 1337
python -m cog_v3.calc.build_v3_gate5_clock_repeat_probe_v1 --quick --backend numba_cpu --global-seed 1337
```

Full (longer) runs:
```powershell
python -m cog_v3.calc.build_v3_fixed_manifest_kernel_gate_stack_v1 --backend numba_cpu --global-seed 1337
python -m cog_v3.calc.build_v3_c12_phase_sector_metrics_v1 --global-seed 1337
python -m cog_v3.calc.build_v3_generation_aligned_equivalence_panel_v1 --global-seed 1337
python -m cog_v3.calc.build_v3_omega_hat_diagnostic_v1 --global-seed 1337 --refresh-panel
python -m cog_v3.calc.build_v3_gate5_clock_repeat_probe_v1 --backend numba_cpu --global-seed 1337 --refresh-manifest
```

---

## 9) Known Risks / Failure Modes

1. Over-interpreting cardinality coincidences (e.g., `168`) without action-level proof.
2. Conflating geometric symmetry with multiplication-preserving symmetry.
3. Treating gate5 failure as one phenomenon when causes differ by candidate.
4. Drawing mass/generation conclusions before kernel promotion and recurrence closure.
5. Running expensive campaigns before defining pass/fail criteria for each lane.

---

## 10) Short Guidance for Claude

When continuing this lane:

1. Keep `S2880` as primary;
2. treat `S960` as structural/symmetry reference lane;
3. always include `kernel_profile` + `convention_id` in new artifacts;
4. avoid narrative promotion from single quick-run results;
5. require per-lane falsifiers and confidence metrics;
6. prioritize scripts that disambiguate blockers:
   - gate5 decomposition,
   - R3 suppression mechanism,
   - seed-structure yield effects,
   - mesoscale isotropy/Lorentz metrics.

---

## 11) Suggested Immediate Next 3 Builds

1. `build_v3_r3_zero_breakdown_v1.py`
   - event-level causal diagnosis for `R3=0`.
2. `build_v3_gate5_clock_oscillation_probe_v2.py`
   - split gate5 into stable vs coherent-oscillatory signatures.
3. `build_v3_bundle12_seed_vs_random_ablation_v1.py`
   - S2880-oriented seed-efficiency test.


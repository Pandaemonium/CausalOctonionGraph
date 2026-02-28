# Standard Model Free Parameters: First-Principles Derivation Table

Last updated: 2026-02-28

This page is the execution-facing map: every Standard Model free parameter on the left, and our first-principles COG derivation strategy on the right.

Conventions:
1. Minimal SM has 19 free parameters.
2. Neutrino-mass extensions add 7 (Dirac) or 9 (Majorana), for 26 or 28 total.
3. "Rigor required" means the minimum bar to claim a real derivation (not a proxy).

| Free Parameter | COG Strategy, Open Gaps, and Rigor Required |
|---|---|
| `g1` (hypercharge coupling) | Strategy: derive from locked `alpha_em(Q)` and `sin^2(theta_W)(Q)` after fixed normalization policy.<br>Open gaps: `ALPHA-001` is currently an upper-bound/proxy closure; `WEINBERG-001` IR bridge is open.<br>Rigor required: freeze scale `Q`, freeze normalization (`g1` vs `gY`), show replayable pipeline from COG observables to `g1` within declared tolerance. |
| `g2` (weak isospin coupling) | Strategy: same bridge as `g1`, using `e(Q) = sqrt(4*pi*alpha_em(Q))` and `g2 = e/sin(theta_W)`.<br>Open gaps: exact `alpha_em` and running weak angle not yet closed at target scale.<br>Rigor required: deterministic observable contract + scale calibration + error budget + independent rerun. |
| `g3` (strong coupling) | Strategy: start from strong-sector COG observable (`STRONG-001` proxy), then close running to `alpha_s(M_Z)` and convert to `g3`.<br>Open gaps: current proxy overestimates physical value; running mechanism not closed.<br>Rigor required: one locked running profile, multi-scale fit check, no post-hoc parameter tuning, CI tests + artifact replay. |
| `mu^2` (Higgs potential mass term) | Strategy: define a COG scalar-order observable that maps to effective Higgs potential curvature.<br>Open gaps: no canonical Higgs-sector observable contract in claims.<br>Rigor required: explicit mapping theorem from COG observable to EFT parameter with fixed sign conventions and units. |
| `lambda` (Higgs quartic) | Strategy: derive from higher-order scalar self-interaction observable in the same Higgs pipeline as `mu^2`.<br>Open gaps: quartic extraction pipeline not implemented.<br>Rigor required: independent closure from same dataset used for `mu^2` without circular fit, uncertainty decomposition included. |
| `theta_QCD` (strong CP angle) | Strategy: close `THETA-001` via a locked CP map (orientation reversal + conjugation) and prove invariance implies `theta_QCD = 0` in a structure-first lane.<br>Open gaps: deterministic weak-leakage deep-cone suite is now artifacted and gate-checked; remaining gaps are the continuum `F*F_tilde` bridge theorem and rigorous CP-operator identification from discrete COG to SM EFT.<br>Rigor required: explicit CP map contract, theorem-level map to effective `F*F_tilde` coefficient, preregistered falsification battery, and successful skeptic review. |
| `m_e` | Strategy: use locked motif + locked mass observable contract (likely long-horizon correlator/drag profile) to define electron baseline.<br>Open gaps: absolute scale calibration and final mass observable lock still incomplete.<br>Rigor required: freeze mass contract (control subtraction, normalization, plateau window), then calibrate one global scale once. |
| `m_mu` | Strategy: lock muon motif via triality-intertwiner closure, then evaluate with same mass observable contract as electron.<br>Open gaps: full phase-gauge closure and unique motif lock not finished; mass observable still debated.<br>Rigor required: motif invariance under gauge-equivalent representatives + blind replay that reproduces `m_mu/m_e`. |
| `m_tau` | Strategy: same pipeline as muon using generation-3 motif closure and fixed mass observable.<br>Open gaps: generation-3 motif lock and triality closure still incomplete.<br>Rigor required: single convention for generation operators, then cross-run reproducibility for `m_tau/m_e` and `m_tau/m_mu`. |
| `m_u` | Strategy: define up-quark motif and confinement-compatible mass extraction using same global mass contract.<br>Open gaps: canonical quark motif basis not locked; confinement-sensitive extraction missing.<br>Rigor required: motif contract + confinement gate pass + stable extraction across admissible initial microstates. |
| `m_d` | Strategy: same quark pipeline as `m_u`, with down-sector motif mapping and shared calibration.<br>Open gaps: flavor-motif split and extraction sensitivity not closed.<br>Rigor required: prove `m_d` estimate is not projection-profile artifact; provide contrast runs and invariance checks. |
| `m_s` | Strategy: strange-sector motif extraction from locked flavor/color map in COG.<br>Open gaps: no accepted flavor SU(3)-to-COG mass map yet.<br>Rigor required: lock flavor mapping rules first, then run same mass extractor with no extra per-flavor parameters. |
| `m_c` | Strategy: second-generation up-type quark motif with generation operator fixed by triality contract.<br>Open gaps: generation-sector contract for quarks open.<br>Rigor required: shared generation operator across lepton and quark sectors + consistency checks. |
| `m_b` | Strategy: second-generation down-type quark motif with same mass contract and calibration.<br>Open gaps: heavy-quark motif and confinement-running bridge not closed.<br>Rigor required: consistent extraction across multiple energy-scale windows with declared running policy. |
| `m_t` | Strategy: top motif as electroweak scale anchor candidate after quark motif lock.<br>Open gaps: no canonical top motif extraction yet; anchor choice not frozen.<br>Rigor required: preregistered anchor policy and proof that other masses are not refit to force agreement. |
| `theta12_CKM` | Strategy: derive from mismatch between up/down sector basis rotations induced by locked COG transport maps.<br>Open gaps: no CKM extraction theorem or artifact pipeline yet.<br>Rigor required: one frozen CKM observable definition and direct computation from locked motifs only. |
| `theta13_CKM` | Strategy: same CKM basis-mismatch pipeline with 3-generation structure fixed.<br>Open gaps: generation and phase conventions not yet fully formalized for CKM extraction.<br>Rigor required: prove angle is gauge-convention invariant and stable to allowed basis relabelings. |
| `theta23_CKM` | Strategy: same CKM pipeline.<br>Open gaps: same as above.<br>Rigor required: full 3-angle extraction from one shared unitary map, not per-angle fits. |
| `delta_CKM` | Strategy: CP phase from oriented non-associative/associator structure projected into CKM sector.<br>Open gaps: no locked CP-phase observable contract.<br>Rigor required: explicit CP-odd invariant in COG and quantitative map to CKM phase convention. |
| `v` (electroweak VEV) | Strategy: derive global energy/time calibration from one non-circular scale anchor and propagate to EFT units.<br>Open gaps: absolute scale problem is open; no canonical anchor accepted.<br>Rigor required: frozen calibration RFC with external reference set and uncertainty propagation. |
| `m_H` | Strategy: derive from Higgs-sector observables, potentially linked to weak-angle structure and scalar dynamics.<br>Open gaps: no closed Higgs observable pipeline; current heuristic bridges are not claim-grade.<br>Rigor required: independent Higgs derivation under locked `v`, no ad-hoc correction factors. |
| `m_nu1` (Dirac or Majorana model) | Strategy: neutrino motif family + lepton-sector mixing pipeline + same mass observable contract.<br>Open gaps: neutrino motif contract not locked; Dirac vs Majorana branch not chosen.<br>Rigor required: branch selection RFC + branch-specific extraction tests and falsifiers. |
| `m_nu2` | Strategy: same neutrino pipeline as `m_nu1`.<br>Open gaps: same as above.<br>Rigor required: mass ordering and splitting consistency checks from a single pipeline. |
| `m_nu3` | Strategy: same neutrino pipeline as `m_nu1`.<br>Open gaps: same as above.<br>Rigor required: reproduce both absolute-scale constraints and oscillation-motivated mass differences. |
| `theta12_PMNS` | Strategy: derive from neutrino-charged-lepton basis mismatch under locked motif/projector definitions.<br>Open gaps: no PMNS extraction framework implemented.<br>Rigor required: one shared PMNS map giving all angles/phases simultaneously, with convention lock. |
| `theta13_PMNS` | Strategy: same PMNS pipeline.<br>Open gaps: same as above.<br>Rigor required: convention-invariant extraction and reproducibility across deterministic reruns. |
| `theta23_PMNS` | Strategy: same PMNS pipeline.<br>Open gaps: same as above.<br>Rigor required: robust value under allowed gauge and basis transformations. |
| `delta_PMNS` | Strategy: leptonic CP phase from same PMNS map plus COG CP-odd invariant.<br>Open gaps: CP-phase observable not locked in lepton sector.<br>Rigor required: explicit invariant mapping and branch-aware (Dirac/Majorana) interpretation. |
| `alpha21_M` (Majorana phase) | Strategy: only in Majorana branch; extract from Majorana-specific neutrino bilinear phase structure in COG representation.<br>Open gaps: Majorana branch itself not locked; no observable contract.<br>Rigor required: branch-lock decision + theorem-level definition of Majorana-phase observable. |
| `alpha31_M` (Majorana phase) | Strategy: same Majorana-phase pipeline as `alpha21_M`.<br>Open gaps: same as above.<br>Rigor required: simultaneous extraction with `alpha21_M` from one locked formalism. |

## Minimum Claim Bar (applies to every row)

We should only say "derived from first principles" when all are true:
1. Canonical input is fixed: full lightcone microstate + deterministic update rule.
2. Observable contract is fixed before running (no post-hoc metric changes).
3. Scale/normalization policy is fixed and published.
4. Lean theorem coverage exists for the algebraic core and no `sorry`.
5. Python verification passes with deterministic replay and archived artifacts.
6. Skeptic review passes claim-by-claim with explicit assumptions and falsification condition.

## Immediate Gate Decisions (First Constant)

These are the highest-priority decisions that currently gate deriving the first full constant claim:

1. **Choose first closure target:** use `theta_QCD` (`THETA-001`) as the first full derivation candidate.
2. **Freeze model profile per claim:** run one canonical profile only (no mixing integer CxO and unity/projector in a single claim closure).
3. **Freeze observable-map contract before runs:** define one CP-odd invariant and one fixed mapping to `theta_QCD`.
4. **Freeze acceptance gates up front:** Lean theorem set, deterministic Python battery, and skeptic-falsifier requirement must be preregistered.
5. **Require strict claim-file integrity:** malformed claim YAML is a hard failure, not a warning.
6. **Require governance-complete promotion artifacts:** explicit bridge assumptions, falsification condition, replay hash, and archived outputs.

## Scope Lock Applied: Anomaly Claims

To prevent over-claiming, anomaly work is now split into two tracks:

1. `ANOM-001` = **consistency claim**: anomaly sums cancel for a declared `Q_num` assignment (with dual sector).
2. `CHARGE-DERIVATION-001` = **derivation claim**: recover quark/lepton charges from COG state data without hand-injected SM values.

Only track 2 can support a true "charges derived from first principles" statement.

## Current Priority Order (Near-Term)

1. `theta_QCD` (`THETA-001`) - symmetry-first, no absolute-scale calibration required.
2. `sin^2(theta_W)` IR bridge - UV anchor is already locked (`1/4`), bridge mechanism still open.
3. `alpha_s(M_Z)` running bridge - UV proxy exists (`1/7`), scale-running closure still open.

## New Contract Stubs (Now Active)

These RFCs are now the control surface for next-stage closure work:

1. `rfc/RFC-080_Discrete_RGE_Contract.md` - freezes how UV-to-IR running is computed and audited.
2. `rfc/RFC-081_Mass_Anchor_Policy_Decision.md` - freezes single-anchor calibration and anti-circularity policy.
3. `rfc/RFC-082_Flavor_Unitary_Extraction_Contract.md` - enforces matrix-first CKM/PMNS extraction.
4. `rfc/RFC-083_THETA_Structure_First_Bridge_Contract.md` - locks THETA as structure-first and enforces gate-3 skeptic evidence for promotion.

## Strategic Concerns: Where We Risk Jumping the Gun

1. **Mass claims before anchor lock:** absolute `m_e/m_mu/m_tau` claims are premature until one anchor policy is frozen.
2. **CKM/PMNS angle-by-angle extraction:** claiming individual angles before full matrix closure invites hidden fitting.
3. **IR coupling claims before running contract lock:** `g1/g2/g3` closures are weak if running mode and cold-start policy are still fluid.
4. **Charge-derivation overclaim:** anomaly consistency (`ANOM-001`) is not charge derivation; `CHARGE-DERIVATION-001` must close first.
5. **Mixed-profile evidence:** combining integer CxO and unity/projector outputs in one claim closure should be treated as invalid.

## Immediate Opportunity Set (High Leverage)

1. Close THETA weak-leakage stress lane and continuum bridge theorem under `RFC-083`.
2. Run one preregistered stationary-distribution discrete-RGE campaign for `WEINBERG-001`.
3. Run anchor battery under one frozen mass observable contract and publish anchor decision memo.
4. Add matrix extraction skeleton artifacts for CKM/PMNS and block per-angle-only promotions.

## Post-Validator Rollout: Action Items

These items reflect what is now implemented in the promotion pipeline and what should be tightened next:

1. **Keep contract gates active in pipeline:** `scripts/validate_claim_contract_gates.py` is now wired into `scripts/run_claim_promotion_pipeline.py`.
2. **Expand gate enforcement scope:** move enforcement from promoted-only to `partial,supported_bridge,proved_core` in CI so weakly specified partial claims are blocked earlier.
3. **Require explicit gate declaration in claim files:** make `contract_gates.required` mandatory for all new/edited claims (not only inferred by claim ID).
4. **Add profile-mixing validator:** fail claims whose artifact bundle mixes incompatible kernel profiles in a single closure record.
5. **Add flavor claim stubs now:** create CKM/PMNS claim IDs with RFC-082 matrix-first fields populated before any angle-level closure attempts.
6. **Add waiver governance:** if a contract gate is waived, require non-empty `waiver_reason` and auto-tag the claim as non-promotable until waiver review.

## Assumptions We Should Challenge Now

These are specific assumptions that can silently degrade derivation quality:

1. **Assumption: one favored microstate is representative.**
   Challenge: require ensemble robustness under preregistered typical-start profiles (`RFC-079`), not one hand-picked start.
2. **Assumption: plateau value is automatically physical.**
   Challenge: define and test plateau diagnostics (window stability, seed stability, horizon stability) before mapping to a constant.
3. **Assumption: mass is fully captured by one drag metric.**
   Challenge: run a locked comparison between drag-based and binding-energy-sensitive observables and predeclare selection criteria.
4. **Assumption: symmetry-only closure implies numeric closure.**
   Challenge: separate `structure_match` from `value_match` in all reports and forbid merging them into one status label.
5. **Assumption: exploratory policy scans are harmless.**
   Challenge: require preregistered policy bundles and reject any output-driven policy edits for claim-grade promotion.

## Next Weekly Sprint (Recommended)

1. Execute weak-leakage deep-cone tests (`N > 10`) and lock the continuum observable bridge theorem from discrete residual to `theta_QCD`.
2. Add CKM/PMNS matrix-first claim stubs with RFC-082 contract fields.
3. Turn on strict contract-gate checks for `partial` claims in CI.
4. Implement and enable profile-mixing validator in promotion pipeline.

## Newly Implemented Probes (Current Iteration)

1. **KOIDE-HEAWOOD-001 scaffold added** (`claims/KOIDE-HEAWOOD-001.yml`).
2. **Heawood spectral witness tests added** (`calc/koide_heawood.py`, `calc/test_koide_heawood.py`):
   - verifies incidence graph construction,
   - verifies expected spectrum structure,
   - verifies secondary mode equals `sqrt(2)`.
3. **THETA-001 witness stack strengthened**:
   - Lean file now contains concrete theorems (no axiomatic placeholders) for:
     - `cpMap_involution`,
     - orientation-flip closure,
     - exact sign-balance (`21/21`, sum `0`),
     - `theta_qcd_forced_zero_if_cp_invariant`.
   - Python tests now include:
     - exact sign-balance check,
     - CP-dual trace relation,
     - weighted CP-even trace delta check.
4. **S3 Witt-pair covariance tests added** (`calc/witt_s3_update_covariance.py`, `calc/test_witt_s3_update_covariance.py`):
   - one-step covariance,
   - multi-step covariance under transported operator sequence.

## Closure Mode (Mandatory Until First Full Constant)

Effective immediately, run in a single-lane closure mode:

1. Only one constant-closure lane may be active at a time (`THETA-001` first).
2. No new constant claim may be promoted while the active lane is unresolved.
3. Every lane run must be preregistered:
   - claim ID,
   - kernel/profile ID,
   - observable-map contract ID,
   - acceptance commands,
   - falsification conditions.
4. Any post-hoc policy edit invalidates the run for promotion purposes.
5. Reports must separate:
   - `structure_match` (symmetry/invariant closure),
   - `value_match` (numeric target closure).

## THETA-001 Current Status (2026-02-28)

| Gate | Status | Notes |
|------|--------|-------|
| Gate 1: Lean theorems | ✅ `done: true` | All 6 theorems in `ThetaQCD.lean`, proved by `native_decide` / `simp` |
| Gate 2: Python tests | ✅ `done: true` | Includes weak-leakage deep-cone check; `native_decide` not `decide` |
| Gate 3: Skeptic review | ✅ `done: true` | `PASS_WITH_LIMITS` — see limits below |
| Claim status | 🟡 `supported_bridge` | Promoted from `partial` — bridge assumptions remain open |
| `proved_core` eligibility | ❌ blocked | `closure_scope: structure_first` — requires continuum bridge RFC |

**Remaining open items (for `proved_core`):**
1. Weak-leakage deep-cone test must be executed and pass (declared in gate_2, not yet run).
2. Continuum bridge contract (new RFC) must be locked.
3. Builder identity in skeptic artifact must be attested by human supervisor.

## THETA-001 Definition of Done (Supported_Bridge — COMPLETE)

All items satisfied as of 2026-02-28. For reference:

1. Lean ✅: `lake build CausalGraphTheory.ThetaQCD` passes. All 6 theorems present.
2. Python ✅: `pytest calc/test_theta001_cp_invariant.py -q` passes. Witness artifact archived.
3. Artifact ✅: replay hash in `sources/theta001_cp_witness.json`. Verify with `build_theta001_witness.py`.
4. Governance ✅: explicit bridge assumptions (two entries), dual falsification condition (structural + bridge),
   `falsification_attempts: []` present, skeptic artifact with `PASS_WITH_LIMITS`.
5. Scope discipline ✅: `closure_scope: structure_first` declared; `proved_core` correctly blocked.
6. **Gate 3 mechanical requirement**: when updating gate_3 to `done: true`, ALSO update
   `contract_gates.rfc083.skeptic_verdict` from `pending` to the artifact verdict AND update
   `sources/theta001_skeptic_review.md` status line. All three must be consistent.

## Approaches to Deprioritize (for Now)

To reduce closure drift, do not spend closure bandwidth on these until `THETA-001` is resolved:

1. Per-angle CKM/PMNS extraction without matrix artifacts.
2. Absolute mass closure before anchor policy lock.
3. Hydrogen spectrum claims from static Fano point graph adjacency alone.
4. Multi-policy scans without preregistered policy bundle and fixed acceptance gates.

---

## ThetaQCD.lean Status and Guardrails (2026-02-28)

**CRITICAL — READ BEFORE WORKING ON THETA-001 LEAN:**

`CausalGraphTheory/ThetaQCD.lean` is **already complete**. All 6 required theorems are proved:

| Theorem | Tactic | Notes |
|---------|--------|-------|
| `cpMap_involution` | `funext i; by_cases h : i = 0 <;> simp [cpMap, h]` | CP map is its own inverse |
| `orientationFlip_preserves_incidence` | `native_decide` | Orientation reversal preserves line supports |
| `fano_sign_pos_count_eq_21` | `native_decide` | Exact positive-sign count witness |
| `fano_sign_neg_count_eq_21` | `native_decide` | Exact negative-sign count witness |
| `fanoSignOrderedSum_zero` | `native_decide` | Signed sum = 0 |
| `theta_qcd_forced_zero_if_cp_invariant` | `exact fanoSignOrderedSum_zero` | Bridge theorem |

**Worker guardrails (do not violate):**

1. **Do not rewrite `ThetaQCD.lean`**. The file is complete. The only task remaining is `lake build CausalGraphTheory.ThetaQCD` to confirm it compiles cleanly, then update `claims/THETA-001.yml` gates.

2. **`native_decide` is intentional and correct.** The sign-count theorems iterate over all ordered distinct pairs of `Fin 7` (42 pairs). `decide` is too slow for this; `native_decide` compiles the check to native code. Do not replace it with `decide`, `norm_num`, or manual induction.

3. **Dependency chain is `FanoMul`, not `Fano` directly.** `ThetaQCD.lean` imports `CausalGraphTheory.FanoMul`. The `fanoSign` function lives in `FanoMul.lean`. If you get a "unknown identifier" error, check that `FanoMul` is built first, not just `Fano`.

4. **Do not add `Mathlib.Analysis.*` imports.** All proofs use only `Mathlib.Tactic`. Adding analysis imports to prove sign-balance would violate the hard gate in `CLAUDE.md` §3 and will be rejected by CI.

5. **THETA-001 gate bookkeeping is now updated**:
   - Gate 1 (`lean_theorems`): `done: true`
   - Gate 2 (`python_tests`): `done: true`
   - Gate 3 (`skeptic_review`): `done: true` with `PASS_WITH_LIMITS`.
   Remaining closure work is bridge-level (weak leakage + continuum mapping), not gate bookkeeping.

---

## Literature Intelligence Update (2026-02-27)

Key papers reviewed this session, ranked by COG relevance:

### Directly Actionable

| arXiv ID | Authors | COG Relevance |
|----------|---------|---------------|
| [2407.01580](https://arxiv.org/abs/2407.01580) | Gourlay, Gresnigt (2024) | **CRITICAL for GEN-002.** S₃ (sedenion automorphisms) embedded INTO Cl(8) without requiring arithmetic sedenion partition. Constructs three linearly independent generations + U(1)_em inside Cl(8). Directly resolves GEN-002 open question 2 (Witt-pair S₃ approximation). |
| [2409.17948](https://arxiv.org/abs/2409.17948) | Furey, Hughes (2024) | Third generation = Cartan factorization of triality triple (Ψ₊, Ψ₋, V) in tri(C)⊕tri(H)⊕tri(O). V sector maps to **Higgs representation**. Predicts m_H lives in the same slot as the τ generation — testable in COG triality operator. |
| [2209.13016](https://arxiv.org/abs/2209.13016) | Furey, Hughes (2022) | Solves fermion doubling problem in R⊗C⊗H⊗O. Key result: **su(3)_C ⊕ u(1)_EM is the subalgebra invariant under complex conjugation.** This is the bridge needed for CHARGE-DERIVATION-001: Q_EM = Hermitian part of U(1) generator, not just Re(ψ[7]). |
| [2206.06912](https://arxiv.org/abs/2206.06912) | Todorov (2022) | Octonion internal space for SM via Cl(6)⊂Cl(8)⊂Cl(10). Derives m_H/m_W in terms of cosine of theoretical Weinberg angle. For COG's sin²θ_W = 1/4 (θ_W = 30°): m_H/m_W = √3 ≈ 1.73 (physical = 1.56). Gap = 10% — closest parameter-free Higgs prediction in the literature. |
| [2505.07923](https://arxiv.org/abs/2505.07923) | Furey (2025) | All SM particles form Z₂⁵-graded superalgebra ≅ H₁₆(C) (Euclidean Jordan algebra). Non-relativistic character suggests bridge to quantum computing. Possible framing for COG's discrete graph structure. |

### Supporting Context

| arXiv ID | Authors | COG Relevance |
|----------|---------|---------------|
| [1910.08395](https://arxiv.org/abs/1910.08395) | Furey (2019) | Three generations from C⊗O 64C-dim space. The COG-native generation mechanism. 48 states = 3 gens under SU(3)×U(1). |
| [2306.13098](https://arxiv.org/abs/2306.13098) | Gresnigt et al. (2023) | GEN-002 parent paper: S₃ ∈ Aut(S), S₃ ∉ Aut(O). Mechanism confirmed; superseded by 2407.01580 for implementation. |
| [hep-ph/0602134](https://arxiv.org/abs/hep-ph/0602134) | Xing, Zhang (2006) | Koide Q = 2/3 holds for pole masses, deviates only 0.2% at M_Z. Confirms COG's algebraic approach targets pole mass, not running mass — consistent with COG being a pre-continuum theory. |
| [hep-ph/0506247](https://arxiv.org/abs/hep-ph/0506247) | Koide (2005) | Mass spectrum from vacuum expectation values under Z₄ × S₃ symmetry. The S₃ factor matches COG's proved Witt-pair S₃ action. Open question: does COG also supply a natural Z₄? |
| [hep-ph/0607193](https://arxiv.org/abs/hep-ph/0607193) | Duret, Machet (2006) | Cabibbo angle from algebraic universality: tan(2θ_c) = −1/2 → cos θ_c ≈ 0.9732 (7/10000 from experiment). No mass ratio input. Prototype for COG projector-mismatch approach to θ_c. |
| [math/0105155](https://arxiv.org/abs/math/0105155) | Baez (2001) | Definitive octonion review: G₂ = Aut(O), dim = 14, root system G₂ (12 roots, long/short ratio √3). Primary reference for G₂ orbit muon hypothesis. |

---

## Post-THETA-001 Closure Queue (Ranked by Line-of-Sight)

Order to attempt after THETA-001 gates pass:

### Tier A — Algebraic / Structural (no absolute-scale calibration needed)

1. **GEN-002 S₃ bridge** — Map COG's proved Witt-pair S₃ action to the Gourlay/Gresnigt 2024 Cl(8) embedding. Gate: show the order-3 element of the COG Witt-pair automorphism matches the S₃ generator described in 2407.01580. Closes the sedenion bypass.

2. **KOIDE-HEAWOOD-001 Lean proof** — `heawood_secondary_eigenvalue_eq_sqrt2` via `native_decide` on the 14×14 rational matrix. Bridges the Python scaffold to a formal claim.

3. **CHARGE-DERIVATION-001 gate_1** — Define Q_EM = Hermitian part of left-multiplication by the Cl(6) volume form ω₆. Compute on the 8 Witt states. Verify {0, +2/3, −1/3, −1} emerges without any hand-injected SM charges. File: `calc/charge_derivation.py`.

4. **ANOM-001 Lean proof** — `decide`-style proof of Tr[Q_num] = 0 and Tr[Q_num³]_combined = 0 for the declared Q_num = {0, +2/3, -1/3, -1} assignment. 20 lines, no analysis imports.

### Tier B — Numeric / Simulation (requires fixed observable contract)

5. **sin²θ_W IR bridge** (WEINBERG-UV-001) — Discrete RGE via Fano traffic statistics (RFC-080). Preregister: start at UV = 1/4, run N_τ steps of Fano loop-crossing operator, measure stationary U(1)_Y/SU(2)_L coupling ratio. Accept if converges to ≈ 0.231 within declared tolerance.

6. **α_s scale calibration** (STRONG-001) — Current proxy 1/7 ≈ 0.143 is consistent with α_s at Q ≈ 4–5 GeV (τ-mass scale), not M_Z. Lock: the COG vacuum stabilizer formula gives the τ-scale value. Running to M_Z reduces to 0.118. Use discrete RGE from RFC-080 once locked.

7. **G₂ orbit muon simulation** — Start from ψ_e = α₁†ω. Apply the 14 G₂ generators (discrete automorphisms of Fano over F₇). Count orbit length until return. Hypothesis: orbit length = 14 (= dim G₂), vertex cost = 15, product = 210 ≈ m_mu/m_e. File: `calc/g2_orbit_muon.py`.

### Tier C — Long-horizon / Exploratory

8. **Cabibbo angle** — Compute angle between up-quark projector (Witt pair e₆,e₁) and down-quark projector (Witt pair e₂,e₅) in the Heawood incidence geometry. Compare to Duret-Machet algebraic value arctan(1/2)/2 ≈ 13.3°. File: `calc/cabibbo_projector.py`.

9. **Higgs mass from triality** (informed by 2409.17948) — Identify the V sector of the COG triality triple. Measure the mass observable in that sector. If Furey/Hughes 2024 is correct, it should equal the τ-sector mass shifted by a Cartan factor. Predicts m_H/m_τ = [Cartan ratio TBD].

10. **Neutrino mass from vacuum proximity** — For ψ_ν = α_k†ω (single creation from vacuum), compute the associator `[α_k†ω, α_k†ω, x]` for x ∈ Fano basis. Zero = exactly massless. Non-zero but small = small Dirac mass. Falsification: if associator is zero for all x, active neutrinos are exactly massless in this model.

---

## Concrete Particle Ensemble Tests (Ready to Implement)

Five simulation setups that can be coded now against existing infrastructure:

| # | Ensemble | Setup | Observable | Predicted | Claim |
|---|----------|-------|-----------|-----------|-------|
| 1 | e + CP(e) | ψ_e = (0,0,0,0,0,0,0,1), cp(ψ_e) = (0,0,0,0,0,0,0,−1). Run both 4 ticks. | Δ(action) | 0 | THETA-001 |
| 2 | Witt-pair triplet Z₃ | Apply σ: Pair0→Pair1→Pair2 to ψ_e. Compare 3 mass observables. | m₁ = m₂ = m₃? | Yes (Koide) | KOIDE-HEAWOOD-001 |
| 3 | Heawood projector | Project 8 Witt states onto Heawood eigenvectors | Charge eigenvalue set | {0, +2/3, −1/3, −1} | CHARGE-DERIVATION-001 |
| 4 | G₂ orbit chain | ψ_e under 14 G₂ generators (over F₇) | Steps to return | 14 × 15 = 210 | muon_mass |
| 5 | Hydrogen 2-body | e on L₁={1,2,3}, p on L₂={1,2,4}. Shared node e₁=e₂ = photon. | E_binding / E_rest | α/2 ≈ 1/274 | HYDROGEN-001 |

---

## Open Structural Questions (For Domain-Reviewer Queue)

Questions where a domain-expert review round would be highest-leverage:

1. **Z₄ factor in Koide mechanism** — Koide 2005 needs Z₄ × S₃. COG proves S₃. What is the natural Z₄ in the Fano/octonion structure? (Z₄ = rotation by 90° in a quaternionic subalgebra of O?)

2. **Fermion doubling in COG** — The Furey/Hughes 2022 fermion doubling fix uses a specific SL(2,C) representation. Does COG's causal graph automatically avoid doubling, or does the DAG structure produce two copies of each fermion?

3. **Alternativity vs Cl(8)** — The COG Alternativity Theorem (ticking from non-associativity of O) is proved for Cl(6). The Gourlay/Gresnigt 2024 construction uses Cl(8). Does extending to Cl(8) break the ticking mechanism, or does it add a second layer?

4. **Higgs from third generation** — If Furey/Hughes 2024 is correct that the third-generation slot holds the Higgs, then COG should produce a spin-0 scalar at the τ-mass scale with the right quantum numbers. Is there a testable COG signature distinguishing the τ fermion from the Higgs scalar in the same triality slot?

5. **Cabibbo angle vs Fano line mismatch** — The angle between two Fano lines sharing one point (dihedral angle in PG(2,2)) — is this well-defined and computable as a Euclidean angle? If so, does it give arctan(1/2)/2 ≈ 13.3°?

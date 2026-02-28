# RFC-077: CxO Unity Profile and Projection Update Rule

Status: Active Draft (Non-Canonical Research Profile)
Date: 2026-02-27
Owner: Research Director + Kernel Team
Depends on:
1. `rfc/CONVENTIONS.md`
2. `rfc/RFC-020_Kernel_Representation_Reconciliation.md`
3. `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
4. `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
5. `world_code/Python_code/minimal_world_kernel.py`
6. `world_code/Python_code/minimal_world_kernel_unity.py`

---

## 1. Executive Summary

Question:
Can we replace the current `CxO` integer-coefficient kernel with a unity-only coefficient model?

Answer:
1. There is no compelling literature result that forces `Z[i]` coefficients as a universal physical necessity.
2. However, a strict unity-coefficient set is not closed under the current bilinear update rule.
3. Therefore, moving to unity requires a projection operator in the dynamics.
4. A projection update rule can work as a deterministic exploratory profile.
5. It is not accepted as canonical for claim promotion until it passes explicit A/B falsification gates.

Decision in this RFC:
1. Keep integer-kernel profile canonical.
2. Admit unity-projection profile as non-canonical, explicitly labeled sensitivity profile.

---

## 2. Problem Statement

Current kernel uses `CxO` with Gaussian-integer coefficients and update:
1. fold all contributors in canonical order,
2. left-act payload on current state.

This is algebraically closed under multiplication and addition in `Z[i]`.

If coefficients are constrained to unity values (for example `{0, +1, -1, +i, -i}`), closure fails under addition. The existing update accumulates terms, so unity-only is not directly compatible without modifying the rule.

---

## 3. Literature Position (What Is and Is Not Established)

What is established:
1. Furey-style constructions are based on complex octonions (`C x O`) and ideal structure, not on a requirement that coefficients must be integers.
2. Complex-octonion Standard-Model representation work does not imply a unique integer-only coefficient policy.

Primary references:
1. C. Furey, 2016 thesis, `arXiv:1611.09182`
2. C. Furey, 2019, `arXiv:1910.08395`
3. C. Furey, 2014, `arXiv:1405.4601`

What is not established:
1. No known result shows that COG must use `Z[i]` coefficients as a physical law.
2. No known result shows that unity-projection dynamics is physically equivalent to the full integer kernel.

---

## 4. Algebraic Constraint

Let `U5 = {0, +1, -1, +i, -i}`.

1. `U5` is closed under multiplication.
2. `U5` is not closed under addition (example: `1 + 1 = 2`, not in `U5`).
3. Current `cxo_mul` computes sums of products.

Consequence:
1. A strict unity coefficient model requires a projection map after additive accumulation (or after each fold/update stage).

---

## 5. Unity Projection Contract

Define deterministic projection `Pi_U : Z[i] -> U5`:
1. `Pi_U(0) = 0`
2. if `|Re(z)| >= |Im(z)|`, map to sign of real axis (`+1` or `-1`)
3. else map to sign of imaginary axis (`+i` or `-i`)
4. tie-break to real axis for deterministic replay

Lift to octonion state component-wise:
1. `Pi_U_CxO(psi) := apply Pi_U to each basis coefficient`

Unity profile update:
1. `payload_t(v) := Pi_U_CxO( fold_{canonical}(messages_t(v)) )`
2. `psi_{t+1}(v) := Pi_U_CxO( payload_t(v) * psi_t(v) )`

This is the contract implemented in:
1. `world_code/Python_code/minimal_world_kernel_unity.py`

---

## 6. Impact on Current Update Rule

Unchanged:
1. same graph/lightcone semantics,
2. same canonical contributor ordering,
3. same left-action update orientation,
4. same deterministic replay structure.

Changed:
1. projection inserts nonlinearity into evolution,
2. bilinearity over coefficients is broken at profile level,
3. information is discarded each tick (amplitude/phase compression),
4. different representatives can collapse to same unity class.

Interpretation:
1. Unity profile is a quantized, lossy update surrogate for phase-dominant experiments.
2. It is not algebraically equivalent to the canonical integer profile.

---

## 7. Will Projection Update Rule Work?

Yes, for specific goals:
1. deterministic bounded-state simulations,
2. fast exploratory scans,
3. sensitivity tests focused on phase-channel behavior.

Not sufficient yet for canonical promotion:
1. can introduce aliasing artifacts,
2. can suppress physically relevant amplitude structure,
3. may preserve some observables while distorting others.

Policy:
1. works as non-canonical research mode,
2. does not replace canonical integer kernel without passing closure gates in Section 9.

---

## 8. Simulation Artifact Requirements (Unity Profile)

Any unity-profile artifact must include:
1. `kernel_profile: unity`
2. explicit `projection_rule_id` and tie-break rule
3. canonical baseline companion run (`kernel_profile: integer`)
4. delta report against baseline observables

`world_code/Python_code/generate_fine_structure_20_cases.py` now supports:
1. `--kernel-profile integer|unity`
2. warm-start and cold-baseline comparisons under same case grid

---

## 9. Closure Gates to Consider Unity as Canonical Candidate

Gate U1: Determinism
1. replay hash stable across repeated runs with unity profile.

Gate U2: Ordering Robustness
1. unity profile remains deterministic under canonical ordering constraints already locked in RFC-028.

Gate U3: Observable Fidelity
1. predefined benchmark observables stay within declared tolerance vs integer profile for required horizons.

Gate U4: No Hidden Retuning
1. no per-claim projection tuning allowed; one fixed `Pi_U` rule only.

Gate U5: Physics Utility
1. at least one target prediction class improves (or compute cost drops substantially at equal fidelity) without introducing contradiction events.

Until U1-U5 pass, unity remains non-canonical.

---

## 10. Governance Lock

Locked by this RFC:
1. integer profile stays canonical (`minimal_world_kernel.py`),
2. unity profile is explicitly non-canonical exploratory mode (`minimal_world_kernel_unity.py`),
3. any promoted claim must disclose profile and include integer baseline comparison.

Forbidden:
1. presenting unity-profile results as canonical-model derivations without integer baseline and declared deltas.

---

## 11. Immediate Next Steps

1. Add explicit profile metadata checks to claim validators for simulation-backed claims.
2. Add A/B battery script to compare integer vs unity across standard benchmark scenarios.
3. Add fail-fast guard in promotion pipeline: unity-only artifacts cannot promote without baseline pair.


# RFC-054: Observable Equivalence and Physical Indistinguishability

Status: Active Draft - Semantics and Governance Plan (2026-02-26)
Module:
- `COG.Governance.ObservableEquivalence`
Depends on:
- `rfc/RFC-042_D4_D5_Implementation_Closure.md`
- `rfc/RFC-044_Projection_Profile_Governance.md`
- `rfc/RFC-048_Two_Node_to_Many_Body_Bridge.md`
- `CausalGraphTheory/D4D5Contracts.lean`
- `CausalGraphTheory/UpdateRule.lean`

---

## 1. Executive Summary

COG has deterministic microdynamics but observer-dependent readout. This RFC defines when different microstates are physically indistinguishable under a declared projection profile and how that can be used (or not used) in claims.

Core position:
1. physical indistinguishability is profile-indexed (`piObs`-relative),
2. equivalence classes are valid observables, not microstate identities,
3. profile-sensitive equivalence must be disclosed in claims.

---

## 2. Problem Statement

`D4D5Contracts.lean` already defines:
1. `ObsEquivalent (piObs) m1 m2 : Prop := piObs m1 = piObs m2`
2. nontriviality/permutation contracts.

What is still missing:
1. governance-level semantics for equivalence classes,
2. transition semantics of equivalence through dynamics,
3. claim restrictions for profile-dependent equivalence.

Without this RFC, equivalence can be overused as a narrative shortcut.

---

## 3. Definitions

Let `P` be a declared projection profile map (`piObsMinimal` or `piObsWithSector`).

1. **Profile equivalence**  
   `m1 ~_P m2` iff `P(m1) = P(m2)`.

2. **Equivalence class**  
   `[m]_P := { x | x ~_P m }`.

3. **Profile-independent equivalence**  
   `m1 ~_* m2` iff `m1 ~_P m2` for all declared production profiles.

4. **Trajectory equivalence over horizon `H`**  
   `m1 ~_P^H m2` iff projected trace sequences match for `H` rounds under same rule/scheduler profile.

---

## 4. Theoretical Constraints

1. Equivalence is observer-relative, not absolute ontology.
2. Equivalence classes are many-to-one coarse-grainings by construction.
3. Equivalence claims are invalid without declared `pi_obs_profile`.
4. If profile changes, equivalence relation changes unless proven profile-independent.

---

## 5. Dynamics and Transport of Equivalence

Let `T` be one canonical round transition map.

Important distinction:
1. **Preserved equivalence:** `m1 ~_P m2` implies `T(m1) ~_P T(m2)`.
2. **Non-preserved equivalence:** same initial projection can evolve into different projections under hidden microstate differences.

This RFC does not assume universal preservation. Preservation must be proven per setting.

Required reporting:
1. claims must state whether they assume one-step or finite-horizon equivalence preservation,
2. if unproven, claims are restricted to static/readout statements only.

---

## 6. Claim-Language Contract

Allowed statements:
1. "Equivalent under `minimal` profile."
2. "Profile-independent across `minimal` and `with_sector`."
3. "Equivalent for horizon `H` under scheduler `S`."

Disallowed statements:
1. "Physically identical" without profile qualifier.
2. "Indistinguishable" when only one profile was checked but no disclosure provided.

---

## 7. Required Claim Metadata

For any claim using equivalence concepts:
1. `pi_obs_profile`
2. `equivalence_mode`: `static`, `one_step`, or `horizon`
3. `equivalence_horizon` (if `horizon`)
4. `equivalence_profile_scope`: `single_profile` or `profile_independent`
5. `equivalence_artifact` (proof/test reference)

---

## 8. Proof and Test Obligations

## 8.1 Lean obligations

1. `obs_equiv_is_equivalence_relation` (reflexive/symmetric/transitive for fixed profile).
2. `piObsPermutationInvariant`-based theorem for order independence.
3. optional preservation lemmas for selected dynamics contexts:
   - `obs_equiv_preserved_one_step_*` (only where true).

## 8.2 Python obligations

1. randomized pair/many-body sampling producing equivalence class reports.
2. finite-horizon divergence detector:
   - detect when static-equivalent microstates diverge at horizon `H`.
3. profile contrast reports (`minimal` vs `with_sector`).

---

## 9. Relationship to Projection Governance (RFC-044)

RFC-044 tells you which profile is allowed for which claim class.
RFC-054 tells you what "same physical output" means under that profile.

Both are required for reliable claim promotion.

---

## 10. Failure Modes

1. Equivalence leakage:
   - using `~_minimal` as if it implied `~_with_sector`.
2. Horizon confusion:
   - treating static equivalence as dynamic equivalence.
3. Profile ambiguity:
   - no declared profile in equivalence claim.
4. Over-strong language:
   - replacing "equivalent under profile" with "identical state."

---

## 11. Falsification Gates

1. claim uses equivalence without declared profile -> invalid.
2. stated profile-independent equivalence fails under contrast profile -> claim downgraded/falsified.
3. claimed dynamic equivalence fails before declared horizon -> claim fails.
4. equivalence artifacts are non-reproducible under replay -> claim blocked.

---

## 12. Acceptance Criteria

1. Equivalence semantics are documented and adopted in claim template.
2. At least one active claim uses profile-qualified equivalence language correctly.
3. CI checks enforce equivalence metadata for relevant claim classes.
4. At least one horizon-based equivalence report is archived.

---

## 13. References

1. Lamport, L. (1978), *Time, Clocks, and the Ordering of Events in a Distributed System*  
   https://www.microsoft.com/en-us/research/publication/time-clocks-ordering-events-distributed-system/
2. Chandy, K. M., Lamport, L. (1985), *Distributed Snapshots*  
   https://www.microsoft.com/en-us/research/publication/distributed-snapshots-determining-global-states-distributed-system/
3. Arrighi, P., Dowek, G. (2012), *Causal graph dynamics*  
   https://arxiv.org/abs/1202.1098

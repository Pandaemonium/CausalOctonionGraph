# Review: RFC-039 (Codex)

Date: 2026-02-26
File reviewed: rfc/RFC-039_Charge_as_Discrete_Z4_Cycle.md

## Overall

Strong conceptual direction. The document is useful as a unifying hypothesis, but several statements are currently stronger than the code/theorems support. The fix is straightforward: tighten wording around what is proved vs conjectured and align to existing module names/contracts.

## What is strong

1. Correctly emphasizes universal period-4 structure from imaginary-unit action.
2. Good use of division-algebra hierarchy as organizing language.
3. Connects charge-conjugation ideas to algebraic involution, which is a productive avenue.
4. Includes implementation targets and falsification checklist.

## Gaps / corrections needed

1. Dependency typo:
   - Lists `rfc/RFC-028_Update_Rule_Semantics_V2.md`.
   - Current canonical file is `rfc/RFC-028_Canonical_Update_Rule_Closure.md`.

2. Over-strong claim: "Charge is quantized because Z4-cycle eigenvalues are integers."
   - Not currently proved.
   - Better: Z4 provides periodic scaffold; quantization claims require explicit charge operator spectrum proofs.

3. Over-strong claim: "Every charge type is a discrete Z4 orbit" as a final statement.
   - Safer formulation: "COG working hypothesis: charge observables are realized through orbit structure in CxO; Z4 is the universal local periodic component."

4. Conflation risk:
   - Time-phase (tick/temporal commit) vs charge operator value should be separated explicitly.
   - Same period-4 does not imply same physical observable.

5. Confinement statements are aspirational.
   - Should be moved to falsifiable hypotheses, not asserted outcomes.

6. Lean target naming mismatch risk:
   - Proposed `ChargeStructure.lean` assumes operators not yet present in current core files.
   - Should stage as scaffold and theorem stubs first.

## Recommended edits to RFC-039

1. Add "Evidence levels" table:
   - Proved in Lean
   - Implemented in Python only
   - Hypothesis

2. Split core claim into two layers:
   - Layer A: universal period-4 orbit theorem (already proved)
   - Layer B: mapping from orbit/operator structure to physical charge spectra (open)

3. Replace hard claim language for confinement/quantization with gate language:
   - "accepted only after X theorem + Y simulation check"

4. Add direct alignment with current contracts:
   - `UpdateRule.isEnergyExchangeLocked`
   - `D4D5Contracts.piObsMinimal/piObsWithSector`
   - `WeakMixingObservable.u1Charge`

5. Add explicit non-goal:
   - "RFC-039 does not yet derive fractional charge spectrum from first principles in Lean."

## Bottom line

RFC-039 is valuable as a hypothesis-unification document. It should be retained, but treated as a research RFC with tightened claim discipline and clearer proof-state boundaries.

# RFC-074: Proof-First Generation Motif Lock Protocol

Status: Active Draft - Blocking Governance Contract (2026-02-27)
Module:
- `COG.Generation.Lock`
- `CausalGraphTheory.GenerationLockContract`
Depends on:
- `rfc/CONVENTIONS.md`
- `rfc/RFC-043_Motif_Catalog_v1.md`
- `rfc/RFC-068_Generation_Drag_from_Spinor_Frame_Scalar_Load.md`
- `CausalGraphTheory/Spinors.lean`
- `CausalGraphTheory/GenerationSeparation.lean`

---

## 1. Executive Summary

This RFC locks the process, not the final tau representative.

Decision:
1. lock projector and parenthesization conventions now,
2. keep `gen1` and `gen2` as currently constructed,
3. treat `gen3` as a derived target until Lean existence + uniqueness class is proved,
4. lock a canonical `gen3` representative only after the uniqueness class is formalized.

This avoids prematurely freezing a potentially gauge-dependent tau motif.

---

## 2. Problem

The current stack mixes:
1. hard-coded generation labels in prose/code,
2. candidate placeholders in Python mapping files,
3. incomplete Lean closure for tau-level representative identity.

If `gen3` is locked before formal uniqueness criteria are proved, downstream mass and drag claims are fragile.

---

## 3. Contract To Lock Immediately

These are now blocking contracts:

1. Sector mapping:
   - `gen1 = s · _ · S*`
   - `gen2 = s* · _ · S*`
   - `gen3 = s* · _ · S`
   - `sterile = s · _ · S`
2. Parenthesization:
   - always `left * (inner * right)`.
3. Integer scale:
   - use a declared fixed integer scale for identity checks (current workflow uses quadrupled states).
4. Replay policy:
   - motif identity checks are exact coefficient checks under the declared scale and parenthesization.

---

## 4. Proof-First Policy

`gen3` lock proceeds in phases:

1. Phase P1: Existence
   - prove non-empty `gen3` sector constructor family in Lean.
2. Phase P2: Uniqueness Class
   - prove uniqueness up to an explicitly declared equivalence relation (for example global Gaussian phase, if adopted).
3. Phase P3: Gauge Fix
   - choose one canonical representative from the proven class using a deterministic rule.
4. Phase P4: Registry Lock
   - publish canonical motif ID and remove `candidate` labels from runtime mapping files.

No claim can reference `gen3` as fully locked before Phase P3.

---

## 5. Required Lean Artifacts

Minimum theorem pack:

1. sector constructor predicates for `gen2` and `gen3`,
2. non-emptiness theorems for both sectors,
3. witness theorem that current `gen2StateQuadruple` inhabits `gen2` sector,
4. `gen3` existence theorem (derived target),
5. optional: uniqueness-up-to-equivalence theorem skeleton and proof plan.

---

## 6. Runtime Mapping Policy

Mapping files must distinguish:
1. locked motifs,
2. derived targets,
3. exploratory candidates.

`muon_candidate`/`tau_candidate` naming is deprecated for governance-grade outputs.

---

## 7. Acceptance Criteria

RFC-074 is `partial` when:
1. Lean contract file exists and builds without `sorry`,
2. mapping metadata marks lock state per motif,
3. docs stop implying `gen3` is fully locked before uniqueness closure.

RFC-074 is `supported` when:
1. P1-P2 are proved in Lean,
2. equivalence relation is explicitly declared,
3. canonical `gen3` representative lock (P3) is merged with tests.

---

## 8. Non-Goals

This RFC does not:
1. claim tau mass derivation is complete,
2. claim generation drag is solved,
3. introduce fitted continuous parameters.


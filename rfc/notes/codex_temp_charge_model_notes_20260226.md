# Codex Temp Notes: Charge/Motif/Rule Model (Working Memo)

Date: 2026-02-26
Context: Immediate scratchpad before formal RFC edits.

## 1) Core stance

- Keep kernel realism: state updates are in CxO first, observables second.
- Do not identify "charge" with "phase position" alone.
- Z4 periodicity is universal for imaginary-unit action, but gauge structure comes from subalgebra closure + stabilizer action + operator definitions.

## 2) What feels right

1. Charge as orbit structure is useful:
   - U(1): phase-orbit axis (vacuum-linked e7/U1 observable)
   - SU(2): quaternionic subalgebra rotations
   - SU(3): octonion/Fano color structure via Witt pairs

2. Particle motifs should be defined operationally:
   - motif = (state family, update map, observable signature, stability criterion)
   - not just a named vector

3. Interaction should stay local/deterministic:
   - boundary messages only
   - fixed order/parenthesization
   - no injected randomness

## 3) What is risky or likely wrong if stated too strongly

1. "Every charge is just Z4": too coarse. Needs qualification:
   - Z4 gives periodic scaffold
   - measured charges/couplings need operator-level definitions (number operator / projectors / generator norms)

2. "Charge quantized because Z4": incomplete.
   - Quantization likely from integer lattice + algebraic operator spectrum (e.g., number operators), not period-4 alone.

3. "Confinement follows automatically": unproven.
   - Must be a falsifiable theorem/simulation gate, not prose claim.

## 4) Missing pieces for a strong physical model

1. Canonical particle motif registry:
   - vacuum, electron, positron-like, quark candidates, proton prototype
   - each with Lean-level and Python-level contract tests

2. Canonical interaction-rule registry:
   - update, energy-exchange, spawn, projection, polarity
   - strict distinction between locked vs draft semantics

3. Charge-operator bridge:
   - relation between existing u1Charge definition and Furey-style number-operator picture
   - prove consistency or explicitly mark scope split

4. Running/coupling story:
   - do not fit constants
   - derive effective values from ensemble/environmental combinatorics with declared conditions

## 5) Practical next-step lens

- Build one RFC that is less metaphoric and more contract-like:
  - exact particle motifs
  - exact interaction rules
  - exact observables
  - exact falsification gates


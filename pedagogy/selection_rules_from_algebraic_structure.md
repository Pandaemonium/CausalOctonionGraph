# Selection Rules From Algebraic Structure

*An explanation for bright high schoolers and college students.*

In many physics classes, selection rules are presented as "nature allows this transition but forbids that one."  
In COG, the ambition is stronger:

- selection rules are not extra policy statements,
- they are direct consequences of the algebra that states live in.

Think of it like grammar. A language does not need a separate "ban list" for every bad sentence.  
The grammar itself decides what is valid.

---

## 1. What is a selection rule?

A selection rule is a yes/no gate on a possible state update:

- **allowed channel:** update gives a nonzero, valid next state,
- **forbidden channel:** update collapses to zero, or breaks a required invariant.

In this program, the gate is algebraic. We ask:

`does the product/composition exist in the required sector, with the required ordering constraints?`

---

## 2. Why octonions make this nontrivial

Octonions are non-associative. Usually:

`(a * b) * c != a * (b * c)`.

So update order matters. That already acts like a selection pressure:

- some ordered compositions stay in a clean subalgebra (stable channel),
- some jump into non-associative bookkeeping (costly or suppressed channel).

This is the "rules from structure" idea in its most direct form.

---

## 3. Four concrete COG selection mechanisms

## 3.1 Fano-line incidence (associative vs non-associative channels)

From `rfc/CONVENTIONS.md` and octonion structure:

- triples on one Fano line are associative (quaternionic subalgebra),
- most triples are not.

So you get a natural channel split:

1. line-aligned compositions are algebraically simple,
2. off-line compositions require explicit parenthesization and extra handling.

This is a selection rule at the level of composition cost and stability.

## 3.2 Witt nilpotency (Pauli-style exclusion gate)

Lean theorems:

- `WittBasis.wittLower_nilpotent`
- `WittBasis.wittRaise_nilpotent`

give:

`(alpha_j)^2 = 0` and `(alpha_j^dagger)^2 = 0` (in doubled normalization in code).

Interpretation:

- applying the same raising channel twice to the same mode is forbidden,
- the algebra returns zero automatically.

That is an exact, hard selection rule.

## 3.3 Vacuum annihilation and vacuum eigen-sectors

Lean theorems:

- `WittBasis.wittLower_annihilates_vacuum`
- `Spinors.e7Left_on_omegaDoubled`
- `Spinors.e7Left_on_leftVacConjDoubled`

say:

1. lowering operators annihilate vacuum (`alpha_j omega = 0`),
2. `e7` acts on `omega` and `omega^dagger` with opposite phase sign.

Interpretation:

- vacuum is not a generic state; it is a constrained algebraic sector,
- only specific channels can leave that sector nontrivially.

Again: selection rule from operator algebra, not from hand-written if/else tags.

## 3.4 Orbit and sector closure constraints

From the photon/vacuum stack (for example `vacuum_orbit_colorSector_zero` in claims):

- vacuum orbit under repeated `e7` action stays in `{e0, e7}` sector,
- no color-sector leakage appears in that orbit.

Interpretation:

- if a proposed channel predicts color excitation from pure vacuum orbit, it is rejected,
- because the proved algebraic orbit closure forbids it.

---

## 4. Big picture: "allowed" means "closure plus consistency"

A channel is physically admissible in COG when it passes all four gates:

1. algebraic product is nonzero,
2. required ordering is consistent with non-associativity rules,
3. sector invariants are preserved (or changed in a proved way),
4. causal-local update rules are respected.

If any gate fails, that channel is not "unlikely." It is structurally invalid.

---

## 5. Why this is useful

This approach reduces model arbitrariness.

Instead of:

- propose interaction first,
- then tune rules so it works,

you do:

- derive legal channels from the algebra,
- then test dynamics only inside that legal set.

That is a cleaner foundation for autonomous search too: agents can prune impossible channels early.

---

## 6. What is proved vs what is still open

## Proved/locked (current repo)

1. Nilpotency of Witt raise/lower operators.
2. Vacuum annihilation by lowering operators.
3. Opposite-sign vacuum/conjugate-vacuum eigenresponse under `e7`.
4. Period-4 structure under `e7` action.

## Active research direction

1. Full catalog of interaction channels grouped by algebraic admissibility class.
2. Quantitative mapping from "non-associative overhead" to measured mass/coupling observables.
3. Automated channel-classifier inside the orchestrator loop.

---

## 7. A one-line summary

In COG, a selection rule is the algebra saying:  
"this transition has a valid sentence in the language of C x O," or "it does not."


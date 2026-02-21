/-
  CausalGraphTheory/Algebra.lean
  Imports Mathlib's algebraic typeclasses and tactics.

  Provides: CommRing, ring, fin_cases, norm_num tactics.
  Previously contained a hand-rolled CommRing class; now uses Mathlib's.

  Allowed Mathlib imports (see CLAUDE.md §3):
  - Mathlib.Tactic.* (ring, fin_cases, norm_num, etc.)
  - Mathlib.Algebra.* (discrete algebra)
-/
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Data.Fin.Basic
import Mathlib.Data.Fintype.Basic

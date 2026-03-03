/-
  CausalGraphTheory/KoideFromKernelV5.lean

  Kernel-v5-to-Koide bridge (assumption-explicit, formally checked).

  This file packages the exact assumptions needed to turn the v5 kernel
  symmetry claims into the Koide equation, then applies existing proved lemmas:

    brannen_koide_from_z3_and_b2
    (from CausalGraphTheory/KoideGroupBridge.lean)

  Scope:
  - Formalizes the "if these kernel-derived constraints hold, Koide follows"
    theorem with no hidden fitting parameters.
  - Does NOT claim those constraints are already derived from dynamics.
-/

import CausalGraphTheory.KoideGroupBridge

namespace CausalGraph

/--
Kernel-v5 assumptions required for the exact Koide bridge.

Interpretation:
- `A, B` are amplitude parameters for sqrt-mass frequencies.
- `(c0, c1, c2)` are Z3 geometry coefficients.
- `hsum`, `hprod` are the Z3 sum/product identities.
- `hB2` is the exact ratio condition `B^2 = 2`.
-/
structure KernelV5KoideAxioms where
  A : Rat
  B : Rat
  c0 : Rat
  c1 : Rat
  c2 : Rat
  hsum : c0 + c1 + c2 = 0
  hprod : c0 * c1 + c1 * c2 + c2 * c0 = -3 / 4
  hB2 : B ^ 2 = 2

/-- Kernel-v5 Brannen-form sqrt-frequency for generation 0. -/
def f0 (K : KernelV5KoideAxioms) : Rat :=
  K.A * (1 + K.B * K.c0)

/-- Kernel-v5 Brannen-form sqrt-frequency for generation 1. -/
def f1 (K : KernelV5KoideAxioms) : Rat :=
  K.A * (1 + K.B * K.c1)

/-- Kernel-v5 Brannen-form sqrt-frequency for generation 2. -/
def f2 (K : KernelV5KoideAxioms) : Rat :=
  K.A * (1 + K.B * K.c2)

/-- SOS form implied by the kernel-v5 Koide assumptions. -/
theorem sos_from_kernel_v5_axioms (K : KernelV5KoideAxioms) :
    (f0 K) ^ 2 + (f1 K) ^ 2 + (f2 K) ^ 2 =
      4 * ((f0 K) * (f1 K) + (f1 K) * (f2 K) + (f2 K) * (f0 K)) := by
  unfold f0 f1 f2
  exact brannen_sos_from_z3_and_b2 K.A K.B K.c0 K.c1 K.c2 K.hsum K.hprod K.hB2

/--
Main kernel-v5 bridge theorem:
if the packaged v5 assumptions hold, the exact Koide equation follows.
-/
theorem koide_equation_from_kernel_v5_axioms (K : KernelV5KoideAxioms) :
    3 * ((f0 K) ^ 2 + (f1 K) ^ 2 + (f2 K) ^ 2) =
      2 * ((f0 K) + (f1 K) + (f2 K)) ^ 2 := by
  unfold f0 f1 f2
  exact brannen_koide_from_z3_and_b2 K.A K.B K.c0 K.c1 K.c2 K.hsum K.hprod K.hB2

end CausalGraph

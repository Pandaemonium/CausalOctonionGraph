/-
  CausalGraphTheory/KernelV2.lean

  Kernel v2 Runtime Contract -- Gate 1 and Gate 2
  =================================================
  Gate 1 (RFC-020): every node stores state in ComplexOctonion Z.
  Gate 2 (RFC-022 §4.2): every node carries colorLabel : FanoPoint.

  Purely algebraic over Z: no reals, no topology, no analysis.
-/

import CausalGraphTheory.ComplexOctonion
import CausalGraphTheory.Fano

namespace KernelV2

open FormalComplex

/-! ## Node state structure -/

/-- A node in the Kernel v2 causal graph.
    * nodeId     -- globally unique identifier
    * psi        -- state vector in ComplexOctonion Z (RFC-020 Gate 1)
    * tickCount  -- discrete ticks elapsed at this node
    * topoDepth  -- topological depth in the causal DAG
    * colorLabel -- static charge/direction axis in FanoPlane (RFC-022 Gate 2) -/
structure NodeStateV2 where
  nodeId     : Nat
  psi        : ComplexOctonion ℤ
  tickCount  : Nat
  topoDepth  : Nat
  colorLabel : FanoPoint

/-! ## Vacuum-orbit predicate -/

/-- isVacuumOrbit psi returns true iff psi is one of {2w, i*2w, -2w, -i*2w}
    where 2w = 1 + i*e7. -/
def isVacuumOrbit (psi : ComplexOctonion ℤ) : Bool :=
  (psi.c ⟨1, by omega⟩ == (0 : FormalComplex ℤ)) &&
  (psi.c ⟨2, by omega⟩ == (0 : FormalComplex ℤ)) &&
  (psi.c ⟨3, by omega⟩ == (0 : FormalComplex ℤ)) &&
  (psi.c ⟨4, by omega⟩ == (0 : FormalComplex ℤ)) &&
  (psi.c ⟨5, by omega⟩ == (0 : FormalComplex ℤ)) &&
  (psi.c ⟨6, by omega⟩ == (0 : FormalComplex ℤ)) &&
  let c0 := psi.c ⟨0, by omega⟩
  let c7 := psi.c ⟨7, by omega⟩
  (c0 == (⟨1, 0⟩  : FormalComplex ℤ) && c7 == (⟨0, 1⟩   : FormalComplex ℤ)) ||
  (c0 == (⟨0, 1⟩  : FormalComplex ℤ) && c7 == (⟨-1, 0⟩  : FormalComplex ℤ)) ||
  (c0 == (⟨-1, 0⟩ : FormalComplex ℤ) && c7 == (⟨0, -1⟩  : FormalComplex ℤ)) ||
  (c0 == (⟨0, -1⟩ : FormalComplex ℤ) && c7 == (⟨1, 0⟩   : FormalComplex ℤ))

-- isPhaseOnlyStep and isEnergyExchange stubs removed (RFC-028 D3, integration closure).
-- Canonical predicate: UpdateRule.isEnergyExchangeLocked
-- Takes List (ComplexOctonion ℤ) msgs, returns true iff k > 0 AND interactionFold msgs ≠ 1.

/-! ## Key elements -/

/-- 2w = 1 + i*e7 in ComplexOctonion Z. -/
def twoOmega : ComplexOctonion ℤ :=
  { c := fun i =>
      if i = (⟨0, by omega⟩ : Fin 8) then (⟨1, 0⟩ : FormalComplex ℤ)
      else if i = (⟨7, by omega⟩ : Fin 8) then (⟨0, 1⟩ : FormalComplex ℤ)
      else (⟨0, 0⟩ : FormalComplex ℤ) }

def omega_vac : ComplexOctonion ℤ := twoOmega

/-- The vacuum color label: FanoPoint index 6 (e7 pseudo-vector axis, RFC-022 §4.2). -/
def vacuumColorLabel : FanoPoint := ⟨6, by omega⟩

/-! ## Vacuum state -/

/-- The canonical vacuum node state for Kernel v2. -/
def vacuumState : NodeStateV2 :=
  { nodeId     := 0
    psi        := omega_vac
    tickCount  := 0
    topoDepth  := 0
    colorLabel := vacuumColorLabel }

/-! ## Gate 1 contract theorems -/

theorem omega_representable_in_kernel_v2 :
    ∃ s : NodeStateV2, s.psi = omega_vac :=
  ⟨{ nodeId := 0, psi := omega_vac, tickCount := 0, topoDepth := 0,
     colorLabel := vacuumColorLabel }, rfl⟩

theorem all_psi_representable :
    ∀ (o : ComplexOctonion ℤ), ∃ (s : NodeStateV2), s.psi = o := fun o =>
  ⟨{ nodeId := 0, psi := o, tickCount := 0, topoDepth := 0,
     colorLabel := vacuumColorLabel }, rfl⟩

/-! ## Gate 2 contract theorem -/

/-- Every FanoPoint can be the colorLabel of some NodeStateV2. -/
theorem colorLabel_representable (fp : FanoPoint) :
    ∃ s : NodeStateV2, s.colorLabel = fp :=
  ⟨{ nodeId := 0, psi := omega_vac, tickCount := 0, topoDepth := 0,
     colorLabel := fp }, rfl⟩

end KernelV2
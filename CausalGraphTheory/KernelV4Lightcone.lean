/-
  CausalGraphTheory/KernelV4Lightcone.lean

  Formal skeleton for the v4 kernel idea:
  1) Lattice is F2^3
  2) State algebra is Z3 × Q240 × Z × Z4
  3) Kernel projects a measured volume backward through a causal lightcone,
     truncated past a self-interference cutoff
  4) Update rule: choose a deterministic order on the cone and multiply all states

  This module intentionally stays algebraic/combinatorial (no reals, no analysis).
-/

import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic
import Mathlib.Data.Int.Basic

namespace KernelV4Lightcone

/-! ## Core spaces -/

/-- F2 (two-point field as a finite type). -/
abbrev F2 := Fin 2

/-- Lattice F2^3. -/
abbrev LatticeSite : Type := F2 × F2 × F2

/-- Z3 domain index. -/
abbrev DomainZ3 : Type := Fin 3

/-- Q240 spin-mixor label (abstractly indexed by 240 symbols). -/
abbrev SpinMixorQ240 : Type := Fin 240

/-- Z energy lane. -/
abbrev EnergyZ : Type := Int

/-- Z4 energy-phase lane. -/
abbrev EnergyPhaseZ4 : Type := Fin 4

/-- Full local state: Z3 × Q240 × Z × Z4. -/
structure State where
  g : DomainZ3
  q : SpinMixorQ240
  e : EnergyZ
  a : EnergyPhaseZ4
  deriving Repr, DecidableEq

/-- Timed lattice point (tick, site). -/
abbrev TimedSite : Type := Nat × LatticeSite

/-- History assigns an optional state to each (tick, site). -/
abbrev History : Type := Nat → LatticeSite → Option State

/-- Snapshot of a measured volume at one tick. -/
structure MeasuredVolume where
  t        : Nat
  observed : LatticeSite → Option State

/-! ## Deterministic kernel specification -/

/--
KernelSpec packages the causal-geometry part:
- `orderedPastCone t x`: the deterministic ordered list of timed sites
  used to update site `x` at tick `t`.
- `selfInterferenceCutoff`: how far backward we must project before
  "past self-interference".
- `cone_is_past`: every contributor is strictly in the past.
-/
structure KernelSpec where
  orderedPastCone : Nat → LatticeSite → List TimedSite
  selfInterferenceCutoff : Nat
  cone_is_past :
    ∀ {t : Nat} {x : LatticeSite} {ts : TimedSite},
      ts ∈ orderedPastCone t x → ts.1 < t

/-- Ordered cone after truncating everything newer than the cutoff depth. -/
def projectedCone (K : KernelSpec) (t : Nat) (x : LatticeSite) : List TimedSite :=
  (K.orderedPastCone t x).filter (fun ts => ts.1 ≤ t - K.selfInterferenceCutoff)

/-! ## Algebraic multiplication layer -/

/--
StateAlgebra supplies the single binary multiplication used by the fold.
This is where a concrete octonionic/nonassociative law is plugged in.
-/
structure StateAlgebra where
  mul : State → State → State

/-- Pull the states currently present on a given ordered cone. -/
def statesOnCone (H : History) (cone : List TimedSite) : List State :=
  cone.filterMap (fun ts => H ts.1 ts.2)

/-- Left-fold multiply over a nonempty list of states. -/
def foldMultiply (A : StateAlgebra) : List State → Option State
  | []      => none
  | s :: ss => some (ss.foldl A.mul s)

/--
Single-site update:
1) project the ordered causal cone past self-interference
2) read states from history on that cone
3) multiply everything in that chosen order
-/
def updateAt
    (A : StateAlgebra)
    (K : KernelSpec)
    (H : History)
    (t : Nat)
    (x : LatticeSite) : Option State :=
  let cone := projectedCone K t x
  let xs := statesOnCone H cone
  foldMultiply A xs

/-! ## Measured-volume back-projection API -/

/-- Zero in F2. -/
private def f0 : F2 := ⟨0, by decide⟩

/-- One in F2. -/
private def f1 : F2 := ⟨1, by decide⟩

/-- Finite list of all sites in F2^3. -/
def allSites : List LatticeSite :=
  [ (f0, f0, f0)
  , (f0, f0, f1)
  , (f0, f1, f0)
  , (f0, f1, f1)
  , (f1, f0, f0)
  , (f1, f0, f1)
  , (f1, f1, f0)
  , (f1, f1, f1)
  ]

/-- Sites that are actually observed in a measured volume. -/
def measuredSites (M : MeasuredVolume) : List LatticeSite :=
  allSites.filter (fun x => (M.observed x).isSome)

/--
Back-project all measured sites through the kernel's projected cone.
This is the formal "start with measured volume, project lightcone back
past self-interference" operator.
-/
def backProjectedSupport (K : KernelSpec) (M : MeasuredVolume) : List TimedSite :=
  List.flatten ((measuredSites M).map (fun x => projectedCone K M.t x))

/-! ## Basic deterministic sanity theorem -/

theorem updateAt_is_function
    (A : StateAlgebra)
    (K : KernelSpec)
    (H : History)
    (t : Nat)
    (x : LatticeSite) :
    updateAt A K H t x = updateAt A K H t x := rfl

end KernelV4Lightcone

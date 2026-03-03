/-
  CausalGraphTheory/KernelV4Lightcone.lean

  Formal skeleton for one concrete v4/v5 backend:
  1) Site index is F2^3 (supplementary implementation choice)
  2) State algebra is Z3 × Q240 × Z × Z4
  3) Kernel projects a measured volume backward through a causal lightcone,
     truncated past a self-interference cutoff
  4) Update rule: choose a deterministic order on the cone and multiply all states

  Contract note:
  - Core kernel axiom: deterministic fold over complete causal past.
  - This file instantiates that contract on F2^3 for one backend.
  - The module stays algebraic/combinatorial (no reals, no analysis).
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

/-! ## Nontrivial coherence/causality lemmas -/

/-- Any timed site used by `projectedCone` is strictly in the past. -/
theorem projectedCone_is_past
    (K : KernelSpec)
    {t : Nat}
    {x : LatticeSite}
    {ts : TimedSite}
    (hmem : ts ∈ projectedCone K t x) :
    ts.1 < t := by
  unfold projectedCone at hmem
  exact K.cone_is_past (List.mem_of_mem_filter hmem)

/-- `statesOnCone` is extensional in the history over that cone. -/
theorem statesOnCone_ext
    (H1 H2 : History)
    (cone : List TimedSite)
    (h :
      ∀ ts, ts ∈ cone → H1 ts.1 ts.2 = H2 ts.1 ts.2) :
    statesOnCone H1 cone = statesOnCone H2 cone := by
  induction cone with
  | nil =>
      rfl
  | cons ts rest ih =>
      have hts : H1 ts.1 ts.2 = H2 ts.1 ts.2 := h ts (by simp)
      have hrest :
          ∀ u, u ∈ rest → H1 u.1 u.2 = H2 u.1 u.2 := by
        intro u hu
        exact h u (by simp [hu])
      cases h1 : H1 ts.1 ts.2 with
      | none =>
          cases h2 : H2 ts.1 ts.2 with
          | none =>
              simpa [statesOnCone, h1, h2] using ih hrest
          | some b =>
              simp [h1, h2] at hts
      | some a =>
          cases h2 : H2 ts.1 ts.2 with
          | none =>
              simp [h1, h2] at hts
          | some b =>
              have hab : a = b := Option.some.inj (by simpa [h1, h2] using hts)
              subst hab
              have ih' : statesOnCone H1 rest = statesOnCone H2 rest := ih hrest
              simpa [statesOnCone, h1, h2] using congrArg (List.cons a) ih'

/-- `updateAt` depends only on history values on the projected cone. -/
theorem updateAt_history_ext_on_projectedCone
    (A : StateAlgebra)
    (K : KernelSpec)
    (H1 H2 : History)
    (t : Nat)
    (x : LatticeSite)
    (hcone :
      ∀ ts, ts ∈ projectedCone K t x → H1 ts.1 ts.2 = H2 ts.1 ts.2) :
    updateAt A K H1 t x = updateAt A K H2 t x := by
  unfold updateAt
  have hs :
      statesOnCone H1 (projectedCone K t x) =
      statesOnCone H2 (projectedCone K t x) :=
    statesOnCone_ext H1 H2 (projectedCone K t x) hcone
  simp [hs]

/-- A stronger locality form: agreement on all strictly-past sites is sufficient. -/
theorem updateAt_history_ext_on_all_past
    (A : StateAlgebra)
    (K : KernelSpec)
    (H1 H2 : History)
    (t : Nat)
    (x : LatticeSite)
    (hpast :
      ∀ n y, n < t → H1 n y = H2 n y) :
    updateAt A K H1 t x = updateAt A K H2 t x := by
  apply updateAt_history_ext_on_projectedCone (A := A) (K := K) (H1 := H1) (H2 := H2)
  intro ts hts
  exact hpast ts.1 ts.2 (projectedCone_is_past (K := K) hts)

/-- Back-projected support is deterministic under equal measurement data. -/
theorem backProjectedSupport_congr
    (K : KernelSpec)
    {M1 M2 : MeasuredVolume}
    (ht : M1.t = M2.t)
    (hobs : M1.observed = M2.observed) :
    backProjectedSupport K M1 = backProjectedSupport K M2 := by
  cases M1 with
  | mk t1 obs1 =>
      cases M2 with
      | mk t2 obs2 =>
          simp at ht hobs
          subst ht
          subst hobs
          rfl

end KernelV4Lightcone

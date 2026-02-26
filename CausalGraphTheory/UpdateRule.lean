/-
  CausalGraphTheory/UpdateRule.lean

  UPDATE-RULE-001 contract (RFC-022 §4.2)
  ========================================
  Defines the edge update operators for the Kernel v2 causal graph.

  * edgeOp             -- left-multiplication by a Fano basis element
  * edgeOp_unique      -- distinct labels give distinct maps
  * depthOrdered       -- canonical topological ordering of edges
  * temporal_commit    -- left-multiplication by e₇ (temporal step T)
  * temporal_first_preserves_phi4 -- e₇ maps vacuum orbit to vacuum orbit
  * combine            -- stub (RFC-022 §10 Q5)

  Purely algebraic over ℤ: no reals, no topology, no analysis.
-/

import CausalGraphTheory.KernelV2
import CausalGraphTheory.Fano

namespace UpdateRule

open KernelV2 FormalComplex Octonion

/-! ## Basis element constructor for ComplexOctonion ℤ -/

/-- The k-th basis element of ComplexOctonion ℤ:
    the element with component k equal to (1 + 0·i) and all others zero. -/
def cxoBasis (k : Fin 8) : ComplexOctonion ℤ :=
  Octonion.basis k

/-! ## Edge operator: left-multiplication by a Fano basis element -/

/-- edgeOp label psi = e_{label+1} * psi
    where e_{label+1} is the (label.val+1)-th basis element of ComplexOctonion ℤ.
    FanoPoint is 0-indexed (0..6), mapping to octonionic basis e₁..e₇. -/
def edgeOp (label : FanoPoint) (psi : ComplexOctonion ℤ) : ComplexOctonion ℤ :=
  cxoBasis ⟨label.val + 1, by omega⟩ * psi

/-! ## Uniqueness: distinct labels produce distinct maps -/

/-- Two edgeOp maps are equal as functions iff their labels are equal. -/
theorem edgeOp_unique (l₁ l₂ : FanoPoint) (h : l₁ ≠ l₂) :
    edgeOp l₁ ≠ edgeOp l₂ := by
  intro heq
  -- Apply both sides to the real unit e₀ = (1,0,...,0)
  have happ : edgeOp l₁ (cxoBasis ⟨0, by omega⟩) =
              edgeOp l₂ (cxoBasis ⟨0, by omega⟩) := by
    exact congr_fun (funext_iff.mpr (fun psi => congr_fun heq psi)) _
  -- edgeOp lₖ e₀ = e_{lₖ+1} * e₀ = e_{lₖ+1} (right-mult by identity)
  -- The component at position (lₖ+1) is 1, others are 0
  -- So equality of results forces l₁.val + 1 = l₂.val + 1, i.e. l₁ = l₂
  simp only [edgeOp, cxoBasis, Octonion.basis] at happ
  apply h
  -- Extract the relevant component: position l₁.val+1 of lhs = position l₁.val+1 of rhs
  have hcomp : ∀ (i : Fin 8),
      (Octonion.basis ⟨l₁.val + 1, by omega⟩ *
       Octonion.basis (R := FormalComplex ℤ) ⟨0, by omega⟩).c i =
      (Octonion.basis ⟨l₂.val + 1, by omega⟩ *
       Octonion.basis (R := FormalComplex ℤ) ⟨0, by omega⟩).c i := by
    intro i; exact congr_fun (congrArg Octonion.c happ) i
  -- e_k * e_0 = e_k, so c[l₁+1] of result = 1 iff i = l₁+1
  -- Both results agree, so l₁+1 = l₂+1
  fin_cases l₁ <;> fin_cases l₂ <;> simp_all (config := { decide := true }) [Fin.ext_iff]

/-! ## Depth-ordered edge list -/

/-- depthOrdered sorts a list of (source, target) edge pairs by source.topoDepth ascending.
    Ties are broken by source.nodeId. Uses a stable merge sort for canonicity. -/
def depthOrdered (edges : List (NodeStateV2 × NodeStateV2)) :
    List (NodeStateV2 × NodeStateV2) :=
  edges.mergeSort (fun e₁ e₂ =>
    if e₁.1.topoDepth < e₂.1.topoDepth then true
    else if e₁.1.topoDepth > e₂.1.topoDepth then false
    else e₁.1.nodeId ≤ e₂.1.nodeId)

/-! ## Temporal commit: left-multiplication by e₇ -/

/-- temporal_commit applies the temporal evolution operator e₇ to psi.
    This is left-multiplication by the 7th basis element (index 7 in Fin 8). -/
def temporal_commit (state : NodeStateV2) : ComplexOctonion ℤ :=
  cxoBasis ⟨7, by omega⟩ * state.psi

/-! ## Phi4 invariant: temporal commit preserves vacuum orbit -/

/-- temporal_first_preserves_phi4: applying the temporal commit operator (e₇ left-multiply)
    to the vacuumState produces a state still in the vacuum orbit {2w, i·2w, -2w, -i·2w}.

    Proof: e₇ · (e₀ + i·e₇) = e₇·e₀ + i·(e₇·e₇) = e₇ + i·(-e₀) = -i·e₀ + e₇
    The result (-i, 0,0,0,0,0,0, 1) in ComplexOctonion ℤ matches the fourth
    vacuum orbit element (c₀ = (0,-1), c₇ = (1,0)). -/
theorem temporal_first_preserves_phi4 :
    isVacuumOrbit (temporal_commit vacuumState) = true := by
  native_decide

/-! ## Combine operator (D1 locked: multiplicative, RFC-028) -/

/-- combine base interaction = base * interaction.
    RFC-028 D1 decision: the combine family is multiplicative.
    Left-multiplication preserves non-associative ordering established
    by the depth-ordered fold over incoming boundary messages. -/
def combine (base : ComplexOctonion ℤ) (interaction : ComplexOctonion ℤ) :
    ComplexOctonion ℤ :=
  base * interaction

/-! ## Interaction fold (D2 locked: Markov, no trace, RFC-028) -/

/-- interactionFold computes the ordered product of incoming boundary messages.
    With Markov semantics (D2), H_t is empty: no trace memory.
    Empty boundary returns 1 (multiplicative identity), so the transition
    reduces to temporal commit only when no incoming edges are present. -/
def interactionFold (msgs : List (ComplexOctonion ℤ)) : ComplexOctonion ℤ :=
  msgs.foldl (· * ·) 1

/-! ## Next state: full deterministic transition (RFC-028 skeleton) -/

/-- nextStateV2 applies the RFC-028 update skeleton:
      psi_{t+1}(v) = U(T(psi_t(v)), O_t(v), H_t(v))
    with T = temporal_commit (e7 * psi), combine = multiplicative, H = empty (Markov).
    tickCount advances by 1 on every transition. -/
def nextStateV2 (s : NodeStateV2) (msgs : List (ComplexOctonion ℤ)) : NodeStateV2 :=
  { s with
    psi       := combine (temporal_commit s) (interactionFold msgs)
    tickCount := s.tickCount + 1 }

/-! ## Energy-exchange predicate (D3 locked: RFC-028) -/

/-- isEnergyExchangeLocked: an energy-exchange event occurs iff the boundary is
    non-empty AND the folded interaction product differs from the identity.
    Supersedes the false stub in KernelV2 (RFC-028 D3 decision).
    Condition: k > 0 /\ interactionFold msgs /= 1 -/
def isEnergyExchangeLocked (msgs : List (ComplexOctonion ℤ)) : Bool :=
  !msgs.isEmpty && (interactionFold msgs != 1)

/-! ## Gate theorems (RFC-028 invariants) -/

/-- interactionFold of the empty list is the multiplicative identity. -/
theorem interactionFold_empty_eq_one :
    interactionFold [] = (1 : ComplexOctonion ℤ) := rfl

/-- combine is definitionally equal to octonion left-multiplication.
    D1 definitional contract: the combine family is multiplicative. -/
theorem combine_closed_coz (base interaction : ComplexOctonion ℤ) :
    combine base interaction = base * interaction := rfl

/-- With an empty boundary (k = 0), the transition is temporal commit only:
    psi_{t+1} = e7 * psi_t. No incoming messages -> only time ticks. -/
theorem nextStateV2_k0_eq_temporalCommit (s : NodeStateV2) :
    (nextStateV2 s []).psi = temporal_commit s := by
  show combine (temporal_commit s) (interactionFold []) = temporal_commit s
  rw [interactionFold_empty_eq_one, combine_closed_coz]
  exact Octonion.mul_one _

/-- update_deterministic: identical initial state and message list yield
    identical next state. The transition is a pure function — no entropy,
    no nondeterministic container order (RFC-028 §6 Invariant 1 and 2). -/
theorem update_deterministic (s1 s2 : NodeStateV2)
    (msgs1 msgs2 : List (ComplexOctonion ℤ))
    (hs : s1 = s2) (hm : msgs1 = msgs2) :
    nextStateV2 s1 msgs1 = nextStateV2 s2 msgs2 := by
  subst hs; subst hm; rfl

end UpdateRule
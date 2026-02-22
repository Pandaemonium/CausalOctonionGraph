# Key Literature Insights for COG Progression

**Written:** 2026-02-21 (pre-compaction notes — preserve these!)
**Purpose:** Distill the most actionable hints from the literature search into concrete
next-step guidance. Read this before starting any new implementation session.

---

## 1. The Single Most Important Insight: COG = CFS + Octonions

**Source:** Finster, Gresnigt et al. (arXiv:2403.00360) — "Causal Fermion Systems and Octonions"

The CFS-octonion bridge paper establishes that:
- Octonionic algebra (Furey program) provides the **symmetry/node data** of a fundamental theory
- Causal Fermion Systems (Finster) provide the **spacetime structure and dynamics** (causal action)
- **These two are complementary, not competing** — exactly the COG architecture!

COG is essentially a *discretized, deterministic* version of this union. The CFS causal action
principle is the continuum limit of COG's discrete update rule. This validates the entire
COG architecture from first principles and gives us the target: COG should converge to CFS
in the large-graph limit.

**Action:** Read Finster monograph (1605.04742) §4–6 to understand what the continuum target
looks like mathematically, before designing `Update.lean` and the Phase 5 convergence proofs.

---

## 2. Causal Invariance IS Lorentz Covariance

**Source:** Gorard (arXiv:2004.14810) — "Relativistic and Gravitational Properties of the Wolfram Model"

The proof that causal invariance (all causal graphs isomorphic regardless of update order)
↔ discrete general covariance was done rigorously for hypergraph rewriting systems.

**For COG:** The `RaceCondition.lean` confluence proof is not just a technical correctness
requirement — **it is the Lorentz symmetry proof**. If COG's `step` function is causally
invariant, Lorentz covariance is automatic.

**Action:** Prioritize `RaceCondition.lean` (confluence) immediately after `Update.lean`.
The proof strategy: show that two different orderings of Tick evaluations produce isomorphic
output DAGs (same edges/nodes up to relabeling). This is provable if:
- Batch operations are order-independent (they're associative by definition)
- Tick operations are order-independent *modulo the DAG node labels* (the non-associative
  evaluation order is fixed by the microstate, not by the evaluator)

---

## 3. Matter Arises From Causal Structure — Don't Hard-Code Edge Labels

**Source:** Rideout & Sorkin (gr-qc/9904062) — "Classical Sequential Growth Dynamics for Causal Sets"

Key result: matter can arise **dynamically from the causal set** without being built in
at the fundamental level. In their model, Ising spins on the causal set *relations* (edges)
give rise to matter fields.

**Implication for COG:** The edge labels (`U1`, `SU2`, `SU3`) should ideally **emerge**
from the octonionic algebra of the adjacent nodes, not be put in by hand as external data.
The Fano plane structure already determines which edge types are possible between which node
types: e.g., a $V \to S_+$ edge naturally carries a triality operator (SU3 color), while
a $S_+ \to S_-$ edge carries a weak isospin operator (SU2).

**Action:** In `State.lean`, don't just label edges with raw `EdgeLabel` — make the label
a *function* of the source/target node labels (their CO states and NodeLabels). This way,
the gauge group emerges from the algebraic structure, not from external input.

```lean
-- Preferred: label derived from node content
def edgeLabel (src tgt : Node) : EdgeLabel :=
  match src.label, tgt.label with
  | .V,      .S_plus  => .SU3 ...  -- triality edge = color
  | .S_plus, .S_minus => .SU2 ...  -- generation edge = weak
  | .V,      .V       => .U1       -- same-rep edge = EM
  | _,       .vacuum  => .SU3 0    -- vacuum coupling
```

---

## 4. Triality = Cube Roots of Unity (Clean Formalization!)

**Source:** McRae (arXiv:2502.14016) — "Exploring Triality Explicitly"

The triality automorphism of $\mathfrak{so}(8)$ acting on the three 8-dimensional
representations $(V, S_+, S_-)$ is simply **multiplication by third roots of unity**:
$$\tau: V \mapsto \omega V, \quad S_+ \mapsto \omega S_+, \quad S_- \mapsto \omega S_-$$
where $\omega = e^{2\pi i/3}$.

**For Lean formalization:** This is a `ZMod 3` action, not a continuous rotation. It can
be formalized purely discretely using `ZMod 3` — no real numbers needed!

**Action for `Triality.lean`:**
```lean
-- The triality action on NodeLabel: ZMod 3 acts by cyclic permutation
def trialityAct (k : ZMod 3) : NodeLabel → NodeLabel
  | .V      => if k = 0 then .V      else if k = 1 then .S_plus  else .S_minus
  | .S_plus => if k = 0 then .S_plus else if k = 1 then .S_minus else .V
  | .S_minus=> if k = 0 then .S_minus else if k = 1 then .V      else .S_plus
  | .vacuum => .vacuum  -- vacuum is triality-invariant

theorem triality_order_3 : ∀ n, trialityAct 1 (trialityAct 1 (trialityAct 1 n)) = n
```

**Also note McRae's warning:** Triality does not trivially explain three generations because
the three images of triality are not *independent* — they are all in the same $Spin(8)$ orbit.
To get genuinely distinct generations, COG needs an additional mechanism to break the
triality symmetry (e.g., the different VEVs of the three complex structures in Furey-Hughes FH2,
or the different tick frequencies of the three images).

---

## 5. The Koide Formula is Protected by Discreteness in COG

**Source:** Sumino (arXiv:0812.2103), Xing & Zhang (hep-ph/0602134)

The Koide formula $Q = 2/3$ holds for **pole masses** but not running masses. Sumino showed
this is because a $U(3)$ family gauge symmetry cancels QED radiative corrections.

**COG's explanation:** Tick counts are **integers** — they don't run. Mass = tick_count/depth
is a discrete, exact quantity with no renormalization group flow. This is why COG predicts
$Q = 2/3$ exactly, while QFT only predicts it approximately (at one loop, with the Sumino
cancellation).

**Action for `calc/koide.py`:**
```python
# Test: if tick ratios satisfy Q = 2/3 exactly, the integer nature is the explanation
# For leptons: find integer triples (n_e, n_mu, n_tau) such that
# (n_e + n_mu + n_tau) / (sqrt(n_e) + sqrt(n_mu) + sqrt(n_tau))^2 ≈ 2/3
# Known: n_e=1, n_mu≈207, n_tau≈3477 approximately satisfy this
# But these are NOT exact integers — the Koide formula constrains the allowed tick ratios

# Phase 4.3 target: find the triality-derived tick structure that produces these ratios
# Hypothesis: the tick excess for S_+ vs V nodes scales as m_mu/m_e due to the
# Fano penalty on V→S_+ triality transitions
```

---

## 6. The Tritium Microstate Has 10 Nodes — Fix This Early

**Source:** `sources/nuclear_hadron_physics.md` §5

The minimal COG representation of tritium requires:
- 9 quark nodes (3 per nucleon: udd, uud, uud)
- 1 vacuum node (for sterile neutrino / color neutrality)
- ~27 color edges (3 within each nucleon) + ~6 residual edges (between nucleons)

**Critical design decision for `calc/graph_sim.py`:** The initial microstate must be
completely specified — every node's CO state, every edge's operator. There is no
probabilistic initialization. The `step` function then evolves this deterministically.

**Action:** Create `calc/tritium_microstate.py` as the first physics simulation file,
defining the exact 10-node initial graph. Use conftest.py constants (FANO_CYCLES, etc.)
for all algebra. Then run `graph_sim.update_step()` for N steps and check for:
1. Color confinement: no net color escaping the nucleon motifs
2. Stability of deuterium sub-motif (p+n₁) while tritium as whole is metastable
3. Eventually: $W^-$ edge activates on one quark, triggering topology change

---

## 7. PhysLean Already Has SM Representations — Use It!

**Source:** Tooby-Smith (arXiv:2411.07667, 2505.07939) — PhysLean project

PhysLean is a Lean 4 library that already formalizes:
- Einstein index notation (tensors)
- Standard Model group representations
- Wick's theorem (formally proved)

**Action:** Before writing `GaugeGroup.lean`, check PhysLean:
1. Search `leanexplore.com` for "SU3", "Gell-Mann", "weak isospin"
2. If PhysLean has what we need, add it as a dependency (check it doesn't import forbidden modules)
3. The COG import chain would then be: `PhysLean → CausalGraphTheory.GaugeGroup`

**Warning:** PhysLean likely imports real analysis for continuous gauge groups. We may need
to use only its discrete/algebraic layer and avoid the differential geometry parts.

---

## 8. The Non-Associative Tick = The Jacobiator

**Source:** Kupriyanov & Szabo (arXiv:1601.03607), Farnsworth & Boyle (arXiv:1303.1782)

The non-associative star product for alternative algebras introduces a "Jacobiator" term:
$$[a \star (b \star c)] - [(a \star b) \star c] = J(a,b,c) \neq 0$$

This Jacobiator is the symbol-calculus version of COG's associator $[a,b,c] = (ab)c - a(bc)$.

**Key physical insight from DFT2:** The Jacobiator appears in the *modified uncertainty
relation* of a non-associative quantum mechanics. The alternative identity (Moufang) is
the *minimum* weakening of associativity that still permits a self-consistent star product.

**For COG:** The `Tick` vs `Batch` classifier in `Tick.lean` is detecting whether the
Jacobiator vanishes. Batch = $J = 0$ = associative subalgebra = can be parallelized.
Tick = $J \neq 0$ = full non-associativity = sequential evaluation forced = time tick.

**Action for `OctonionAlt.lean`:** After proving alternativity, add:
```lean
theorem associator_nonzero : ∃ a b c : Octonion ℤ, associator a b c ≠ 0
theorem moufang_implies_alternative : ∀ x y, moufang x y → left_alternative x y ∧ right_alternative x y
```

---

## 9. Ordered Implementation Path (Critical Path)

Based on the literature, the correct implementation order is:

```
Phase 1A (DONE by Gemini):
  ✓ calc/fano.py + calc/octonion.py + calc/complex_octonion.py
  ✓ calc/test_subalgebra.py (7 assoc / 28 non-assoc triples verified)
  ✓ ExportOracle.lean + calc/test_oracle.py
  ✓ Witt basis fix (α† = ½(-e_a + ie_b))

Phase 1B (NEXT - Lean algebraic foundations):
  → CausalGraphTheory/OctonionAlt.lean: prove left/right alternativity
  → CausalGraphTheory/OctonionNonAssoc.lean: prove ∃ non-assoc triple
  → CausalGraphTheory/SubalgebraDetect.lean: prove 7 assoc / 28 non-assoc count

Phase 2A (Graph engine):
  → CausalGraphTheory/State.lean: CausalGraph, NodeLabel, EdgeLabel, Node, Edge
  → CausalGraphTheory/Tick.lean: Batch/Tick classifier
  → CausalGraphTheory/Update.lean: single-step evolution (deterministic)
  → CausalGraphTheory/DAGProof.lean: step_preserves_acyclic

Phase 2B (Confluence = Lorentz covariance):
  → CausalGraphTheory/RaceCondition.lean: prove step is causally invariant
  *** THIS IS THE LORENTZ SYMMETRY PROOF — HIGH PRIORITY ***

Phase 3A (Python graph simulator):
  → calc/graph_sim.py: NetworkX DAG simulator
  → calc/tritium_microstate.py: 10-node initial state (NEW - use this as physics driver)
  → calc/test_tick.py: tick counter validation

Phase 4A (Gauge structure):
  → Check PhysLean first (leanexplore.com)
  → CausalGraphTheory/GaugeGroup.lean: SM gauge group from CO automorphisms
  → CausalGraphTheory/Triality.lean: ZMod 3 action on NodeLabel (trivial discrete proof)

Phase 4B (Mass predictions):
  → calc/koide.py: verify Koide formula from experimental masses
  → calc/mass_ratios.py: compute tick-ratio predictions

Phase 4C (Tritium simulation):
  → calc/hydrogen_sim.py → calc/deuterium_sim.py → calc/tritium_sim.py
  → Success criterion: tritium is metastable, deuterium is stable, beta decay occurs
```

---

## 10. The Hardest Open Problems (Flagged Proactively)

1. **Why does triality give INDEPENDENT generations?** McRae's paper warns that the three
   triality images are in the same $Spin(8)$ orbit. COG needs an additional mechanism.
   **Hypothesis:** The three images get different tick frequencies because the Fano penalty
   for $V \to S_+$ triality transition is different from $V \to S_-$. The asymmetry comes
   from the directed structure of the Fano plane (the 7 oriented cyclic triples break the
   $S_3$ permutation symmetry of $\{V, S_+, S_-\}$ down to $\mathbb{Z}_3$).

2. **How does beta decay emerge deterministically?** The $W^-$ edge must fire at a
   specific time (not probabilistically). COG's answer: the timing is encoded in the
   initial microstate — the parenthesization schedule in RFC-002 determines when the
   SU2 edge becomes "active". The half-life $t_{1/2} = 12.32$ yr = number of graph
   steps between the initial microstate and the topology-change event.

3. **Does the Koide formula follow from tick counts?** This is the key quantitative test.
   If the Fano penalty for $V \to S_+$ and $V \to S_-$ transitions can be computed from
   the Fano sign tensor, and if these penalties give tick count ratios satisfying $Q = 2/3$,
   the theory is internally consistent. This is the `calc/fano_penalty.py` computation.

4. **Mathlib continuum contamination.** The `CliffordAlgebra` module in Mathlib4 may
   transitively depend on Analysis via `NormedSpace`. Run `lake exe graph` and check.
   If contaminated, hand-roll $\mathbb{C}\ell(6)$ from `ComplexOctonion` directly.

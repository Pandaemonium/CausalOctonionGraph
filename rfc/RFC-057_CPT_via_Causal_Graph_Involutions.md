# RFC-057: CPT Symmetry via Causal Graph Involutions

Status: Stub (2026-02-26)
Module:
- `COG.Core.CPT`
Depends on:
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-039_Charge_as_Discrete_Z4_Cycle.md`
- `rfc/CONVENTIONS.md`
Literature basis:
- Jost (1957), Lüders (1954): CPT theorem (continuous QFT)
- Streater and Wightman (1964): *PCT, Spin and Statistics, and All That*
- Dowker (2010): CPT in causal set theory

---

## 1. Executive Summary

RFC-039 established charge conjugation C = complex conjugation on C⊗O
(following Furey). The other two discrete symmetries — parity P and
time reversal T — are undefined in the COG framework.

This RFC proposes concrete COG definitions for P and T, states the CPT
conjecture, and outlines what would constitute a proof.

---

## 2. Problem Statement

- **C** (charge conjugation): established. $ψ → ψ^*$ (complex conjugate
  of the node state). Particle ↔ antiparticle (Furey 2014, RFC-039).

- **P** (parity): undefined. In standard QFT, P is spatial reflection
  $ec{x} → -ec{x}$. COG has no background space. A COG-native definition
  must come from the automorphism structure of the Fano plane or the causal graph.

- **T** (time reversal): undefined. COG is a directed acyclic graph; time flows
  along edge direction. Reversing T = reversing all edge directions — but this
  changes the DAG structure fundamentally.

- **CPT**: The theorem that C∘P∘T is always a symmetry, even when individual
  symmetries are broken, is the most fundamental discrete symmetry result in QFT.
  COG must either prove an analog or identify where the standard proof breaks down.

---

## 3. Candidate Definitions

### 3.1 Parity via Fano involution

The automorphism group of the Fano plane is GL(3,2) ≅ PSL(2,7) with 168 elements.
Its involutions (order-2 elements) correspond to geometric “reflections” of the
projective plane — swapping pairs of points while fixing a third.

Candidate: **P = the involution of GL(3,2) that fixes the vacuum axis $e_7$
and swaps each Witt pair** $(e_a, e_b) → (e_b, e_a)$.

Under this map:
- $e_7 → e_7$ (vacuum fixed)
- $(e_6, e_1) → (e_1, e_6)$, $(e_2, e_5) → (e_5, e_2)$, $(e_3, e_4) → (e_4, e_3)$
- Color charges flip sign (like $ec{p} → -ec{p}$ in standard parity)

This must be verified to be an actual automorphism of the octonion multiplication table.

### 3.2 Time reversal via edge reversal

In the COG causal DAG: **T = reversal of all causal edge directions**.

Under T:
- The update rule `nextStateV2` (which reads parent states) must be replaced
  by a reverse rule reading child states.
- The DAG becomes a different DAG (the “time-reversed history”).
- T is not a symmetry of a generic COG history, but C∘P∘T may be.

---

## 4. CPT Conjecture

**Conjecture:** For any COG update sequence $H = (s_0, s_1, …, s_n)$,
the sequence $(C∘P∘T)(H)$ is also a valid COG update sequence
(i.e., satisfies the update rule, D3 gate, and spawn conditions).

**Strategy for proof:**
1. Show C∘P is an automorphism of the Witt state space
   (maps valid motifs to valid motifs).
2. Show T produces a well-defined reverse history.
3. Show that C∘P∘T maps any valid update sequence to a valid one.

---

## 5. Implementation Targets

### Lean
- `CausalGraphTheory/CPT.lean`
- Define `parityInvolution : Fin 7 → Fin 7` (Fano involution)
- Prove it is an octonion automorphism: `parity_is_automorphism`
- Define `chargeConjugate : ComplexOctonion Int → ComplexOctonion Int`
- State `cpt_conjecture` as a formal theorem (may remain `sorry` initially)

### Python
- `calc/cpt_symmetry.py`: verify P on benchmark motifs numerically
- Check: `P(electron) = positron-like` under the Fano involution
- Check: `C(P(electron)) = electron` (CP near-conservation)

---

## 6. Falsification Gates

1. If the candidate Fano involution is NOT an automorphism of octonion
   multiplication (i.e., does not preserve the Fano structure constants),
   reject the P definition.
2. If C∘P does not map the electron motif to a positron-like motif, reject.
3. If the CPT conjecture is shown false on a specific COG sequence, document
   the counterexample and downgrade to “CPT-violating theory” (a major result).

---

## 7. Sources

1. Jost (1957), *Eine Bemerkung zum CTP Theorem*, Helv. Phys. Acta
2. Lüders (1954), *On the Equivalence of Invariance under Time Reversal and
   under Particle-Antiparticle Conjugation*, Kong. Dan. Vid. Sel. Mat. Fys. Med.
3. Streater and Wightman (1964), *PCT, Spin and Statistics, and All That*
4. Dowker (2010), *Causal sets as discrete spacetime*, Contemp. Phys.
   https://arxiv.org/abs/gr-qc/0508109
5. Furey (2014), *Generations: three prints, in colour*
   https://arxiv.org/abs/1405.4601

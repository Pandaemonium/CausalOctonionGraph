# Research Director Primer: COG Kernel, Octonions, XOR Dynamics, and Particle Motifs

Status: Active working primer (2026-02-27)
Audience: Research Director and core leads
Purpose: One document that explains the current COG model end-to-end, with clear separation between locked facts, implemented machinery, and open research.

---

## 1. What This Model Is

COG models physics as:
1. a causal directed graph (DAG),
2. with node states in complex octonions over integers,
3. updated by deterministic local rules.

No real-valued differential equations are required at kernel level.

If you only keep one line in mind, keep this:
1. causality is graph structure,
2. dynamics are octonion multiplication,
3. observables are projections of full microstate.

---

## 2. Model State at a Glance

Use this as your current "truth map."

### 2.1 Locked conventions

1. Basis and signs are fixed by `rfc/CONVENTIONS.md`.
2. Fano orientation and Witt pairings are fixed.
3. Vacuum axis is `e7`.

### 2.2 Locked update choices

From RFC-028 path and implementation:
1. D1 combine: multiplicative.
2. D2 trace/fold: Markov fold over current messages.
3. D3 energy exchange: non-empty messages and fold not identity.

### 2.3 Implemented XOR stack

1. XOR octonion gate with handed sign behavior: `calc/xor_octonion_gate.py`.
2. Motif cycle scans and artifacts: `calc/xor_particle_motif_cycles.py`.
3. Vector vs spinor phase-cycle comparison: `calc/xor_vector_spinor_phase_cycles.py`.
4. Furey ideal cycles in XOR notation: `calc/xor_furey_ideals.py`.
5. Two-body edge-gap dynamics: `calc/xor_two_body_kinematics.py`.

### 2.4 Still open / in-progress closure areas

1. D4/D5 full integration and promotion closure (contracts and proofs exist in `CausalGraphTheory/D4D5Contracts.lean`; broader closure program tracked in `rfc/RFC-042_D4_D5_Implementation_Closure.md`).
2. Full many-body and bound-state closure.
3. Constant derivations that require non-fitted running mechanisms.

---

## 3. Core Algebra You Need to Operate the Model

## 3.1 State space is 16 integers per node

A node state is:
`psi in C x O over Z`

Write:
`psi = sum_{k=0..7} (a_k + i b_k) e_k`, with `a_k, b_k in Z`.

So every node has:
1. 8 octonion channels,
2. each channel has real and imaginary integer parts,
3. total: 16 integers.

Important distinction:
1. "8 components" means 8 basis channels.
2. "16 integers" means explicit storage form over `Z[i]`.

## 3.2 Identity and complex unit

1. `e0` is octonion multiplicative identity in the basis.
2. Complex `i` commutes with all octonion basis elements.
3. Do not conflate `e0` with complex scalar `1 + 0i`; `e0` is basis direction, coefficients live in `Z[i]`.

## 3.3 Multiplication source of truth

All signs and directed triples come from:
`rfc/CONVENTIONS.md`

Operationally:
1. `e_i * e_i = -e0` for `i in 1..7`,
2. distinct imaginary products follow directed Fano lines and antisymmetry.

---

## 4. XOR Octonions: Fast Execution Notation

XOR view is execution-level, not a new physics basis.

For distinct imaginary channels (`i,j in 1..7`, `i != j`):
1. output index uses XOR channel: `k = i xor j`,
2. sign is looked up from locked Fano orientation.

Special cases:
1. `i=0` or `j=0`: identity behavior,
2. `i=j!=0`: output `-e0`.

Handedness:
1. left-hit: `op * state`,
2. right-hit: `state * op`,
3. for distinct imaginaries, left and right share output index but flip sign.

See:
1. `rfc/RFC-063_XOR_Octonion_Gate_and_Signed_Handed_Dynamics.md`
2. `CausalGraphTheory/XorGate.lean`
3. `calc/xor_octonion_gate.py`

---

## 5. Discrete Phase Theory and Time

## 5.1 Temporal commit

Current kernel temporal step uses:
`T(psi) = e7 * psi`

This induces period-4 phase behavior on key orbits (including vacuum orbit).

## 5.2 Two clocks: do not confuse them

1. `topoDepth`: graph-causal depth (global causal layering).
2. `tickCount`: local update count for a node (interaction clock).

Interpretation:
1. topology gives causal placement,
2. ticks give local phase progression.

## 5.3 Superdeterministic reading

Given:
1. exact initial microstate,
2. fixed deterministic rulebook,
3. no exogenous runtime writes,

future state is fixed. Uncertainty is from missing light-cone information, not kernel randomness.

See:
`rfc/RFC-064_Superdeterminism_and_Lightcone_Information_Volume.md`

---

## 6. Update Rule: Practical Kernel Form

Canonical skeleton:
`psi_{t+1}(v) = U(T(psi_t(v)), ordered_boundary_msgs, local_trace_slice)`

Current locked runtime path:
1. temporal commit,
2. multiplicative fold of incoming messages,
3. multiplicative combine.

In XOR runtime helpers, this is mirrored in:
1. `calc/xor_update_rule.py`
2. `calc/xor_charge_sign_interaction_matrix.py`

---

## 7. D4 and D5: What They Are and Where They Stand

## 7.1 D4 (spawn semantics)

D4 answers:
1. when new nodes materialize,
2. how they initialize,
3. what determinism/locality/completeness laws must hold.

Current state:
1. contract definitions and concrete implementation/proofs exist in `CausalGraphTheory/D4D5Contracts.lean` (`shouldSpawnImpl`, `spawnInitImpl`, `applySpawnImpl` plus closure theorems),
2. broader closure and pipeline wiring still tracked by RFC-042.

## 7.2 D5 (observable projection contract)

D5 answers:
1. what observers can read from microstate,
2. minimal vs extended projection profiles,
3. invariance requirements (especially permutation invariance).

Current state:
1. minimal and extended projections are defined in `CausalGraphTheory/D4D5Contracts.lean`,
2. canonical profile is minimal projection (`piObsCanonical := piObsMinimal`),
3. promotion-grade integration still tracked by RFC-042/044 governance.

---

## 8. Distance, Interaction, and Kinematics in COG

Distance in current operational policy is graph-native:
1. edge separation count.

Two-body policy lock (`rfc/RFC-035_Distance_as_Next_Interaction_Node_Gap.md`):
1. one hop per tick,
2. impulse at message arrival from charge-sign relation,
3. topology/distance update every tick,
4. observable: `distance_delta = future_edge_distance - past_edge_distance`.

Important practical behavior:
1. interaction outcomes depend on relative phase at arrival (distance parity can gate repulsive/attractive vs neutral in current toy model).

---

## 9. Particle Motifs: Vector and Spinor Views

## 9.1 What a particle is in this program

A particle is not a hardcoded label. It is a stable motif under declared update policy:
1. seed state,
2. update family,
3. orbit/stability predicate,
4. observable signature.

See:
`rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md`

## 9.2 Vector motifs

Vector motifs are basis-sparse state patterns with cycle signatures under deterministic drives.
Current scans identify stable closures aligned with Fano-line structure under locked schedules.

## 9.3 Spinor motifs from Furey minimal left ideals

Repository implements Furey-style minimal left-ideal constructions (sometimes informally called "lower left ideals" in discussions):
1. vacuum idempotent (doubled form),
2. Witt raising/lowering operators,
3. electron and dual-electron chains.

In code:
1. `CausalGraphTheory/WittBasis.lean`
2. `CausalGraphTheory/FureyChain.lean`
3. `calc/xor_furey_ideals.py`

## 9.4 Why doubled convention appears

Factors of `1/2` in ladder operators are absorbed by doubled integer convention so states remain in integer-coefficient execution path.

---

## 10. Vacuum and "Photon" in Current Implementation

What is implemented now:
1. temporal vacuum drive (`e7` commit) is explicit and deterministic,
2. message passing through graph can perturb vacuum node states in event-engine simulations.

What is not yet fully implemented:
1. a first-class photon object with explicit emission, propagation, and detection state machine.

Current practical interpretation:
1. photon-like behavior is represented by message/update effects and vacuum-phase propagation patterns,
2. not yet by a fully locked standalone boson entity in kernel data structures.

---

## 11. What You Can Calculate Right Now

See roadmap:
`rfc/XOR_PHYSICS_CALCULABLES_ROADMAP.md`

Ready-now families include:
1. XOR multiplication/sign audits,
2. motif cycle spectra,
3. vector vs spinor cycle comparisons,
4. Furey ideal cycle artifacts,
5. perturbation-to-attractor matrices,
6. two-body edge-gap kinematics.

Near-term target families:
1. robust charge-sign interaction matrices,
2. hydrogen XOR bridge artifacts,
3. spinor ideal stabilization leakage benchmarks.

---

## 12. Minimal Command Set for the Research Director

Run these to regenerate core artifacts:

1. `python -m calc.xor_particle_motif_cycles`
2. `python -m calc.xor_vector_spinor_phase_cycles`
3. `python -m calc.xor_furey_ideals`
4. `python -m calc.xor_event_engine`
5. `python -m calc.xor_two_body_kinematics`
6. `python -m calc.xor_charge_sign_interaction_matrix`

Core verification:
1. `pytest calc/test_xor_octonion_gate.py -v`
2. `pytest calc/test_xor_particle_motif_cycles.py -v`
3. `pytest calc/test_xor_vector_spinor_phase_cycles.py -v`
4. `pytest calc/test_xor_furey_ideals.py -v`
5. `pytest calc/test_xor_two_body_kinematics.py -v`

---

## 13. How to Make Decisions Without Drifting

Use this governance rule before adopting any physics statement:
1. Is it Lean-proved?
2. If not, is it deterministic and replay-stable in Python?
3. Is it tagged as hypothesis if not proved?
4. Is the projection profile declared?
5. Is the claim specific about which update policy and motif class it used?

If any answer is no, do not promote the claim.

---

## 14. Immediate High-Leverage Next Moves

1. Finish D4/D5 promotion closure end-to-end (not just contract-local proofs).
2. Add explicit photon-proxy layer in event engine (vacuum phase pulse lifecycle).
3. Tighten spinor ideal stabilization pipeline (RFC-065 direction).
4. Push hydrogen from proxy-level to stronger bound-state gates with declared profile.
5. Keep all new claims pinned to replay artifacts and profile metadata.

---

## 15. Bottom Line

COG now has a serious discrete-algebraic execution core:
1. deterministic causal update,
2. locked octonion conventions,
3. practical XOR runtime,
4. motif-cycle tooling and artifacts.

The key strategic task is no longer "invent the kernel." It is:
1. close remaining integration contracts (D4/D5 and many-body bridges),
2. keep promotion discipline tight,
3. convert stable motif and vacuum-phase machinery into stronger, falsifiable physics claims.


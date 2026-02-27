# RFC-063: XOR Octonion Gate and Signed Handed Dynamics

Status: Active Draft - Implemented Scaffold (2026-02-27)
Module:
- `COG.Algebra.XORGate`
- `COG.Motifs.XORCycles`
Depends on:
- `rfc/CONVENTIONS.md` (locked Fano orientation)
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md` (deterministic update contract)
- `rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md` (motif semantics)
- `rfc/RFC-043_Motif_Catalog_v1.md` (motif catalog integration)
- `rfc/RFC-011_XOR_Basis_Efficiency_and_Spinor_Cost.md` (prior XOR framing)

---

## 1. Executive Summary

This RFC locks a concrete XOR interaction kernel for octonion basis-unit updates and
adds deterministic cycle-analysis artifacts for motif time structure.

Core contract for distinct imaginary basis units:
1. index channel: `k = i xor j`,
2. sign channel: `sign = FANO_SIGN(i,j) in {+1,-1}`,
3. handedness:
   - left-hit: `e_op * e_state`,
   - right-hit: `e_state * e_op`,
   - for distinct imaginaries, right sign is the negative of left sign at fixed output index.

This contract is now implemented and tested in Python, with Lean-side support theorems
for XOR index and handed sign behavior.

---

## 2. Problem Statement

Previous RFCs established XOR compatibility conceptually, but the project lacked:
1. one strict, executable gate contract for index+sign+handedness,
2. deterministic motif-level cycle extraction artifacts for analysis/dashboard use,
3. a support-closure stability criterion tied directly to the XOR kernel.

Without these, particle-motif cycle claims remain harder to audit and replay.

---

## 3. Algebraic Contract

### 3.1 Basis indexing

Use basis indices `0..7`:
1. `0 -> e0` (real identity),
2. `1..7 -> e1..e7` (imaginary units).

### 3.2 Multiplication contract

For basis multiplication `e_i * e_j`:
1. `i = 0`: output `+e_j`,
2. `j = 0`: output `+e_i`,
3. `i = j != 0`: output `-e0`,
4. `i,j in 1..7`, `i != j`: output `sign * e_(i xor j)` with `sign` from locked Fano orientation.

### 3.3 Handedness contract

Define handed operator action:
1. left: `LEFT(op, state) := e_op * e_state`,
2. right: `RIGHT(op, state) := e_state * e_op`.

Distinct-imaginary law:
1. output index is equal under left and right,
2. output sign flips: `sign_right = -sign_left`.

---

## 4. Stability and Time-Structure Contract

### 4.1 Support-closure stability

For triad motif support `M subset {1..7}` and state sequence `psi_t`:
1. motif is support-stable over horizon `T` iff
   `support(psi_t) subset M union {0}` for all `t <= T`.

This is a structural criterion (no physical calibration constants).

### 4.2 Cycle extraction

Given deterministic policy `F`, define:
1. first-repeat cycle start `s`,
2. period `p > 0` such that `psi_(s+p) = psi_s`,
3. full per-step trace artifact for replay and visualization.

---

## 5. Implemented Artifacts (Now Available)

### 5.1 Runtime kernels

1. `calc/xor_octonion_gate.py`
   - `mul_basis_fast`
   - `apply_handed_operator`
   - `handed_sign_flip_distinct_imag`
2. `calc/xor_stable_motif_scan.py`
   - triad scan over all 35 combinations
   - support-closure stability report
   - vacuum-drive period scan
3. `calc/xor_particle_motif_cycles.py`
   - full trace generator
   - JSON/CSV artifact writers

### 5.2 Saved datasets

1. `calc/xor_particle_motif_cycles.json`
2. `calc/xor_particle_motif_cycles.csv`
3. `website/data/xor_particle_motif_cycles.json`
4. `website/data/xor_particle_motif_cycles.csv`
5. `calc/xor_furey_ideal_cycles.json`
6. `calc/xor_furey_ideal_cycles.csv`
7. `website/data/xor_furey_ideal_cycles.json`
8. `website/data/xor_furey_ideal_cycles.csv`

These encode per-motif policy traces, cycle periods, and support-closure flags.
The Furey ideal dataset adds explicit lower-left-ideal motifs (`S^u`, `S^d`)
in doubled `Z[i]` coefficient form, executed with the same XOR index channel
and Fano sign channel.

---

## 6. Current Observations (Structural)

Under current deterministic triad schedules:
1. exactly 7 of 35 triads are support-stable,
2. they match the 7 canonical Fano lines,
3. stable triads under repeated `e7` drive show period 4.

This is not yet a full particle-spectrum derivation. It is a locked structural baseline.

---

## 7. Test and Replay Contract

Required tests:
1. `calc/test_xor_octonion_gate.py`
2. `calc/test_xor_particle_demo.py`
3. `calc/test_xor_stable_motif_scan.py`
4. `calc/test_xor_particle_motif_cycles.py`

Current status: passing in local run.

Rebuild command:
1. `python -m calc.xor_particle_motif_cycles`
2. or `python scripts/build_xor_particle_motif_cycles.py`

---

## 8. Relation to RFC-011

RFC-011 framed XOR basis primacy and triality-cost questions.
RFC-063 narrows scope to the executable gate contract and motif cycle extraction.

Interpretation:
1. RFC-011 remains the high-level efficiency/mass-overhead hypothesis document.
2. RFC-063 is the implementation-grade kernel and trace-governance layer.

---

## 9. Falsification Gates

Reject this RFC as implemented if any occur:
1. any distinct-imaginary pair violates `out_idx = i xor j`,
2. handed left/right fails sign-flip law on distinct-imaginary domain,
3. stable-triad scan returns support-stable non-line triads under locked schedules,
4. generated artifacts are not deterministic on replay under fixed code and inputs.

---

## 10. Acceptance Criteria

RFC-063 can be marked `partial` when:
1. XOR gate and handed tests pass in CI,
2. cycle artifact generation is integrated in artifact build flow,
3. at least one claim consumes `xor_particle_motif_cycles` artifact references.

RFC-063 can be marked `supported` when:
1. Lean and Python contracts are cross-linked to one shared claim gate,
2. motif-catalog entries consume the stable-cycle signatures without profile drift.

---

## 11. Next Steps

1. Wire cycle artifact generation into existing public artifact pipeline.
2. Add motif-catalog bindings:
   - `fano_line_l1..l7`,
   - `electron_line_l1`,
   - `proton_proto_t124` (explicitly non-closure under internal support criterion).
3. Add a website panel for layman view:
   - "motif rhythm" (period),
   - "stability" (closed/open support),
   - "vacuum-driven cycle" (period-4 view).
4. Add a Lean bridge theorem set for handed sign-flip and XOR index consistency, mapped to this RFC gates.

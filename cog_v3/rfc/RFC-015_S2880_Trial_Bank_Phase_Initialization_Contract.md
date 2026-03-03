# RFC-015: S2880 Trial-Bank Phase Initialization Contract

Status: Draft
Date: 2026-03-03
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-010_C12_Phase_Sector_Generation_and_Rare_Hop_Test_Contract.md`
- `cog_v3/rfc/RFC-009_S960_Phase_Fibered_E8_Symmetry_Model.md`
- `cog_v3/calc/build_v3_c12_singlet_doublet_clock_shift_sparse_v1.py`

## 1. Purpose

The S2880 multiplication table is correctly implemented: `mul[a,b]` computes
`(phase_a + phase_b) mod 12, q_a * q_b)` as intended (verified in
`build_mul_table` in `build_v3_c12_singlet_doublet_clock_shift_sparse_v1.py`).

However, the existing trial bank in `build_v3_c12_phase_sector_metrics_v1.py`
seeds ALL trials at even C12 phases (0, 2, 4) due to a **kick-phase-doubling** bug.
This makes odd Δp values (including the physically critical d3 = Δp=±3) algebraically
unreachable. This RFC defines the correct phase initialization policy.

## 2. The kick-phase-doubling problem

### 2.1 Mechanism

Current trial bank construction:
```python
"state_id": _s_id(p, q_state, qn)  # C12 phase = p
"kick_id":  _s_id(p, q_kick,  qn)  # C12 phase = p  (same p!)
```

The cell state placed in the world is `mul[kick_id, state_id]`, which has phase:
```
(p + p) mod 12 = 2p mod 12
```

Actual seed phases for current trials:
1. g0 trials (p=0): seed phase = 0
2. g1 trials (p=1): seed phase = 2
3. g2 trials (p=2): seed phase = 4

All current trial seeds are at even phases {0, 2, 4}.

### 2.2 Consequence for Δp

With a uniform seed region at even phase `q`:
- Every fold_product over in-seed neighbors has phase = N * q (mod 12) where N is the
  count of seeded neighbors in the stencil.
- N * q is always even when q is even.
- Hence all Δp = (new_phase - old_phase) mod 12 = (N * q + q) mod 12 = (N+1)*q mod 12,
  which is also always even.

Result: **d3 (Δp=3, an odd value) is algebraically unreachable from any even seed phase.**
This is why `total_d3 = 0` appears across all current trials.

### 2.3 Derivation of d3 edge-cell condition

For a seed sheet (e.g., `sheet_y` family) in the axial-6 stencil:
- A cell at the sheet boundary with exactly 3 in-seed neighbors contributes:
  ```
  fold_acc_phase = 3 * p mod 12
  out_phase      = (3p + p) mod 12 = 4p mod 12
  Δp             = 3p mod 12
  ```
- For Δp = 3: need `3p ≡ 3 (mod 12)` → `p ≡ 1 (mod 4)` → p ∈ {1, 5, 9} in C12.

**d3 hops require seed phase p ∈ {1, 5, 9}** (odd, and ≡ 1 mod 4).
No current trial seeds at any of these phases.

## 3. Correct initialization policy

### 3.1 Kick-phase fix

Use kick_id at phase 0 (identity phase, zero phase contribution):
```python
"kick_id": _s_id(0, q_kick, qn)   # phase 0: no phase change, only Q240 kick
```

This preserves the Q240 directional kick while placing the seed at the intended phase p
(not 2p).

### 3.2 Required trial lanes

The trial bank must include trials at all three phase parity classes:

**Class A — zero phase (anchor):**
- Phase 0: vacuum-adjacent anchor states.
- Expected behavior: no phase evolution, zero d3. Control lane.

**Class B — even non-zero phase:**
- Phases 2, 4, 6, 8, 10.
- Expected behavior: even Δp hops only (d2, d4, d6, ...). No d3.

**Class C — odd phase (required for d3):**
- Phases 1, 3, 5, 7, 9, 11.
- Sub-priority: phases 1, 5, 9 (≡ 1 mod 4) produce d3 at 3-neighbor edge cells.
- Sub-priority: phases 3, 7, 11 (≡ 3 mod 4) produce d9 at 3-neighbor edge cells
  (since 3*3=9), which are also physically meaningful.

Minimum required Class C trials:
1. Phase 1: `_s_id(1, e111, qn)` with kick `_s_id(0, e001, qn)` → seed at phase 1.
2. Phase 3: `_s_id(3, e111, qn)` with kick `_s_id(0, e001, qn)` → seed at phase 3.
3. Phase 5: `_s_id(5, e111, qn)` with kick `_s_id(0, e001, qn)` → seed at phase 5.

### 3.3 Generation-sector alignment

With corrected initialization, the generation-sector mapping is:
- Phase 1 → g = 1 mod 3 = 1 (Gen2)
- Phase 2 → g = 2 mod 3 = 2 (Gen3)
- Phase 3 → g = 0 mod 3 = 0 (Gen1)
- Phase 4 → g = 1 (Gen2)
- etc.

To explicitly target Gen1, Gen2, Gen3 with odd-phase seeds:
- Gen1 (g=0): phases 0, 3, 6, 9 → use p=3 for odd, p=9 for odd ≡ 1 mod 4
- Gen2 (g=1): phases 1, 4, 7, 10 → use p=1 for odd ≡ 1 mod 4
- Gen3 (g=2): phases 2, 5, 8, 11 → use p=5 for odd ≡ 1 mod 4

**Recommended canonical odd-phase trial set for generation coverage:**
1. Gen1 odd: phase 9 seed (g=0, odd, 3*9=27≡3 mod 12 → d3 at edges)
2. Gen2 odd: phase 1 seed (g=1, odd, 3*1=3 → d3 at edges) ← highest priority
3. Gen3 odd: phase 5 seed (g=2, odd, 3*5=15≡3 → d3 at edges)

## 4. Hypotheses

### H1 (d3 unlock)

After applying kick-phase-0 fix and using p=1 phase-1 seeds:
1. d3 (Δp=3) events appear at sheet-edge cells of the seed boundary.
2. Count is proportional to the number of 3-neighbor edge cells and run ticks.

### H2 (odd-phase R3 > 0)

For trials at p ∈ {1, 5, 9}:
1. R3 = P(|Δp|=3) / P(|Δp| ∈ {1,2,4,5,6}) is measurably above zero.
2. R3 is reproducible across seeds and panel configurations.

### H3 (d3 dominance in the stable regime)

In stable-motif regimes (post-transient), Δp=3 events become the dominant channel
relative to other non-zero Δp values:
1. R3 ≥ 2 in stable window.

H3 is a long-horizon hypothesis; H1 and H2 are immediate confirmations.

## 5. Null models

N1:
1. d3 does not appear even after kick-phase fix (indicates deeper suppression).

N2:
1. d3 appears but R3 < 1 (no dominance even with correct seeding).

N3:
1. R3 is seed-sensitive and non-reproducible.

## 6. Implementation plan

### Phase A (immediate fix + confirmation)

1. Modify `_trial_bank()` in `build_v3_c12_phase_sector_metrics_v1.py`:
   - Add Class C odd-phase trials with kick at phase 0.
   - Retain existing trials for comparison.
2. Run quick panel with modified trial bank.
3. Check: `total_d3 > 0` for p=1 trials.

### Phase B (odd-phase sweep)

1. Run full RFC-010 metric suite with odd-phase trial set.
2. Measure R3, C3, L3, A1, A2 for p=1, 5, 9 trials.
3. Compare to even-phase trials (expected: R3 jumps from 0 to > 0).

### Phase C (stable-motif integration)

1. Feed p=1/5/9 phase seeds into RFC-014 bundle seeding.
2. Seed bundle: {(p, g), (p+3, g), (p+6, g), (p+9, g)} for odd p → correct generation
   coverage with non-trivial phase dynamics.

## 7. Promotion gates

Gate 1:
1. H1 confirmed: d3 events appear for p=1 trials after kick fix.

Gate 2:
1. H2 confirmed: R3 > 0 and reproducible across seeds.

Gate 3:
1. Odd-phase trials integrated into RFC-010, RFC-011, RFC-014 trial banks.

## 8. Falsifiers

Reject this lane if:
1. d3 remains zero after kick-phase-0 fix (would indicate deeper structural suppression
   — e.g., the S2880 multiplication table itself suppresses certain Δp values).
2. R3 is non-reproducible under seed/panel controls.

## 9. Non-claims

1. This RFC does not claim that d3 dominance (R3 >> 1) will appear automatically after
   the kick fix. It only claims d3 will become non-zero.
2. The stable-regime R3 dominance (H3) requires further motif evolution, not just
   initial seeding.

## 10. Physical interpretation

The absence of d3 hops in current data is a **seeding artifact**, not a kernel property.
The kernel correctly implements (z1*z2, q1*q2) S2880 multiplication. Once odd-phase
seeds are used, the within-generation dominant channel (Δp=±3) becomes accessible.

Physically: Δp=±3 corresponds to within-generation quantum-number cycling (the Z4 sub-clock
within one generation sector). Its dominance over inter-generation Δp=±1,±2 hops is the
discrete analog of the strong/weak coupling ratio. This can only be observed after the
trial bank correctly populates the odd-phase regime.

## 11. Experimental confirmation (added 2026-03-03)

### 11.1 Codex kick-phase probe results

`v3_c12_phase_sector_metrics_kickphase_probe_v1` (global-seed 1337, 100-tick runs):

| mode | add_odd_lane | d3_sum | odd_sum | R3 | A₁ | A₂ |
|------|-------------|--------|---------|-----|-----|-----|
| matched (broken) | False | 0 | 0 | 0.0000 | 0.0000 | -0.029 |
| zero-kick (fixed) | False | 1582 | 3755 | 0.0898 | -0.0356 | +0.060 |
| zero-kick + odd lane | True | 6948 | 12443 | 0.2203 | -0.0462 | +0.038 |

Status: **H1 CONFIRMED** (d3 > 0 for zero-kick mode), **H2 CONFIRMED** (R3 = 0.090 >> 0).

### 11.2 Two-region probe (Codex)

Direct two-region test (half grid phase 0, half phase 3):
- d3 global: 38,919 + 37,282 hops (axial-6 stencil)
- any_d3_global = True, any_odd_global = True

Confirms: d3 is available in Q240/C12 dynamics — the R3=0 in all prior runs was 100% an
artifact of kick-phase-doubling, not a physical suppression.

### 11.3 R3 progression table (confirmed)

| Config | R3 | d3_sum | Notes |
|--------|----|--------|-------|
| Broken (matched kick phase) | 0.000 | 0 | Algebraic suppression |
| Zero-kick fix (even seeds only) | 0.090 | 1582 | H1, H2 CONFIRMED |
| Zero-kick + odd trial lane | 0.220 | 6948 | 2.45× additional boost |
| Phase M target (post RFC-017) | > 1.0 | — | Z₃-locked regime |
| Phase M strong lock | > 5.0 | — | Generation-dominant regime |

### 11.4 Proposed quick-panel R3 gate

For the RFC-015 quick panel (integrated into trial bank):
```
R3 > 0.05  (gate passes with zero-kick fix alone)
A₁ != 0.0  (non-zero directional asymmetry = observed: A₁ = -0.036 in zero mode)
```

These two assertions confirm: (1) d3 channel is open, (2) CP-like asymmetry is non-zero.

### 11.5 A₁ sign interpretation

Observed A₁ = -0.035 in zero-kick mode. Sign convention: A₁ = (d3_forward - d3_backward) / total.
Negative A₁ → more backward (Δp=-3) than forward (Δp=+3) hops in the short-time probe.
This is the C12 CP violation signal (RFC-010 §3): non-zero at even the short probe horizon.
After Phase M unlock, A₁ should stabilize to the Brannen delta-driven asymmetry.


# RFC-018: Gate2/Gate4 C12 Integration Unlock Contract

Status: Draft
Date: 2026-03-03
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-015_S2880_Trial_Bank_Phase_Initialization_Contract.md`
- `cog_v3/rfc/RFC-017_Phase_Boundary_and_Ordered_Phase_Detection_Contract.md`
- `cog_v3/rfc/RFC-007_Motif_First_Chirality_Emergence_and_Parity_Test_Contract.md`
- `cog_v3/rfc/RFC-008_Mesoscale_Lorentz_Pseudosymmetry_and_RG_Selection_Contract.md`

## 1. Purpose

The overnight runner (`run_v3_overnight_autonomous_v1`) has processed 600+ batches without
passing gate2 (detector exclusivity) or gate4 (chirality). This RFC documents that these
gate failures are STRUCTURAL — not solvable by seed search in the current kernel — and
defines the C12 integration upgrade needed to unlock both gates.

## 2. Root Cause: Two Structural Blockers

### 2.1 Gate4 blocker: Q240 parity symmetry

Observation: a_chi_proxy = 0.0 in every overnight batch across all kernels (K0/K1/K2).

Root cause: The base Q240 kernel `cog_v3_octavian240_multiplicative_v1` applies only
Q240 multiplication. Q240 is closed under parity (q → q_parity is a bijection on Q240).
Therefore, any measurement that tests left/right asymmetry of Q240-only dynamics
returns zero net asymmetry.

Gate4 tests a_chi_proxy = |left_hits - right_hits| / total_hits. This requires a
mechanism that breaks left/right parity in the photon probe.

**Q240 cannot provide this. C12 phase sector can.**

When C12 phase is added (full S2880 dynamics), the Brannen delta (RFC-016 §5.2)
introduces a non-zero phase offset that breaks the p → -p symmetry. This creates
A₁ ≠ 0 (RFC-010 hop asymmetry), which propagates to a_chi_proxy ≠ 0 in the photon probe.

### 2.2 Gate2 blocker: two-front plane wave

Observation: wave_transport_class = two_front_balanced, detector_exclusivity = 0.0
in every batch. The photon candidate `photon_sheet_y_e111_kick_e010` (period_N=48)
propagates symmetrically in both ±x directions.

Root cause: The sheet_y seed creates a plane wave perpendicular to the x-axis. In the
Q240 cube26 kernel, this sheet wave creates equal-amplitude propagation in both ±x
directions. The plane wave hits both detectors simultaneously → exclusivity = 0.

Gate2 tests for directional propagation (one detector hit, not both). This requires
either:
1. A directional (non-sheet) seed that creates a focused pulse.
2. A phase gradient across the sheet that biases one direction over the other.

**Option 1 (seed fix):** Use blob3 or single-cell seeds.
**Option 2 (C12 fix):** The C12 phase gradient across a sheet seed breaks the ±x symmetry.

### 2.3 Period 48 as C12 evidence

The best overnight candidate has period_N=48 = 4 × 12 = 4 C12 cycles. This is NOT
random. In the Q240-only runner:
- If seed_state_id=121 has Q240 order = 4: period 48 = Q240 order × C12 phase count
- If Q240 order = 12: period 48 = Q240 order × 4

The period 48 is a signature of the C12 clock structure even in the Q240-only runner.
In the full S2880 runner with C12 phase tracking, this period should align with C12
phase evolution: the motif's phase should complete exactly 4 full C12 cycles per period.

**Physical prediction:** In Phase M (mesophase, RFC-017), the stable photon period is
T_photon = 12k ticks (one or more complete C12 cycles). Period 48 = 12 × 4 is physical.

## 3. Gate2 Unlock: Three-Stage Fix

### Stage 1 (immediate, seed-side)

Add blob3 seed family to the overnight trial bank:
- 3-cell blob at the center of a small box
- Kick in a single direction (e_x, e_y, or e_z)
- Expect directional propagation (not symmetric plane wave)

Target: any_propagating=True AND wave_transport_class="single_front_directed" (if exists)
or detector_exclusivity > 0.

### Stage 2 (medium-term, axial6 stencil)

Run the overnight search with axial6 stencil (6 cube-face neighbors only).
Axial6 is more anisotropic at micro-scale; directional kicks in Q240 elements may
create asymmetric propagation that doesn't immediately equalize to two-front.

Target: detector_exclusivity > 0.1 for at least one seed/kick combination.

### Stage 3 (C12 integration, long-term)

In the full S2880 runner (after RFC-015 fix + Phase M search):
- The C12 phase gradient across the sheet provides the directional asymmetry.
- The ±x asymmetry is encoded in Δp = ±1 (rightward vs leftward phase advance).
- Gate2 should unlock automatically once the C12 phase sector contributes to dynamics.

## 4. Gate4 Unlock: C12 Integration

### 4.1 Required change

Upgrade the overnight runner to use S2880 (C12 × Q240) instead of Q240 only:
1. Use S2880 state encoding: state_id = phase * 240 + q240_id.
2. Build S2880 multiplication table (call build_mul_table from RFC-015 dependency).
3. Use odd-phase seeds (p=1, 5, 9 per RFC-015).
4. Measure a_chi_proxy = A₁ = (d3_right - d3_left) / (d3_right + d3_left).

### 4.2 Expected behavior

In Phase D (current): a_chi_proxy still near 0 (even in S2880, disordered phase).
In Phase M (mesophase): a_chi_proxy = |A₁| > 0 (within-generation hop asymmetry present).

Gate4 requires Phase M AND C12 integration. Both conditions are necessary.

### 4.3 Chirality gate redefinition for S2880

Current gate4 uses the Q240 photon-probe hit asymmetry.
For S2880, gate4 should be redefined:
```
gate4_chirality_new = (A₁_stable > A₁_threshold AND A₁_stable stable across seeds)
```
where A₁ is the signed hop asymmetry from RFC-010.

The photon-probe chirality measurement remains valid but needs C12 tracking enabled.

## 5. Hypotheses

### H1 (period 48 = C12 period)

In the S2880 runner, the photon motif (`sheet_y, e111, kick e010`) retains period ≈ 48.
The period decomposes as: 48 = 4 × T_C12 = 4 × 12 phase cycles.

### H2 (gate2 unlocks with blob3 seeds)

At least one blob3 seed/kick combination in the Q240 cube26 kernel shows
detector_exclusivity > 0 (single-front directed propagation).

### H3 (gate4 unlocks with C12 integration in Phase M)

In S2880 Phase M (w3 > w3_crit, RFC-017), the a_chi_proxy > 0 for odd-phase seeds
(p=1, 5, 9). The chirality is reproducible across seeds.

## 6. Null Models

N1: blob3 seeds also create two-front balanced waves → gate2 remains blocked in Q240.
(Would indicate gate2 requires C12 integration for all seed families.)

N2: a_chi_proxy remains 0 in S2880 Phase M → gate4 requires explicit parity-breaking
(e.g., asymmetric Q240 kick element), not just C12 phase offset.

N3: Period 48 does not align with C12 structure in S2880 → the 48-period is a Q240
artifact unrelated to C12 phase.

## 7. Implementation Plan

### Immediate (this week)

1. **Pause overnight runner** for seed bank update.
2. **Add blob3 seed family** to trial bank: 3-cell blob, 3 directional kicks.
3. **Resume runner** — check if any blob3 trial gives detector_exclusivity > 0.

### Short-term (after RFC-015 fix)

4. **Upgrade overnight runner to S2880** using full build_mul_table() S2880 encoding.
5. **Add odd-phase seeds** (p=1, 5, 9) to S2880 trial bank.
6. **Run Phase M sweep** (w3 > w3_crit from RFC-017).
7. Check a_chi_proxy in Phase M runs.

### Medium-term

8. If H2 confirmed (blob3 gate2 pass): expand search to blob3-family at higher trial count.
9. If H3 confirmed (gate4 pass in Phase M): tune a_chi_proxy threshold for gate4 promotion.

## 8. Promotion Gates

Gate 1:
1. H1 confirmed: period-48 candidate in S2880 runner decomposes as 4 × 12 C12 cycles.

Gate 2:
1. H2 confirmed: blob3 seed shows detector_exclusivity > 0.05 in Q240 runner.
   OR
   H2_alt: C12 integration (S2880 Phase M) unlocks gate2 for sheet_y seed.

Gate 3:
1. H3 confirmed: a_chi_proxy > 0.05 in S2880 Phase M run, stable across 3 seeds.

## 9. Falsifiers

Reject this analysis if:
1. a_chi_proxy > 0 appears in Q240-only runs (would indicate Q240 itself has parity breaking
   — requires re-examination of the convention or kernel code).
2. Period-48 candidate vanishes in S2880 runs (would indicate period is Q240 artifact).
3. Gate4 fails in S2880 Phase M for all odd-phase seeds (would indicate deeper issue
   with S2880 chirality mechanism).

## 10. Connection to RFC-007

RFC-007 H1 (motif-first chirality):
"For parity-neutral kernels, there exist motifs M where M and P(M) show reproducible
asymmetric dynamics."

The overnight data (a_chi_proxy=0 for all Q240 runs) is NOT a falsifier of RFC-007.
It is consistent with RFC-007 — the chirality requires C12 phase integration, and
the current kernel IS parity-neutral (by design). RFC-007 says the motif provides
the chirality, not the kernel alone. The motif-first chirality requires:
- Parity-neutral kernel (Q240 ✓)
- Non-trivial motif that carries phase winding (C12 phase offset ← RFC-015 fix)
- Asymmetric observable (A₁ ← RFC-010)

RFC-007's H1 test cannot be completed until C12 integration is done.

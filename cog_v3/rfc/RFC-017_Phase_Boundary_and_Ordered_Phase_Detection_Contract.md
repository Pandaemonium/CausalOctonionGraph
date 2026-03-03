# RFC-017: Phase Boundary and Ordered Phase Detection Contract

Status: Draft
Date: 2026-03-03
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-010_C12_Phase_Sector_Generation_and_Rare_Hop_Test_Contract.md`
- `cog_v3/rfc/RFC-015_S2880_Trial_Bank_Phase_Initialization_Contract.md`
- `cog_v3/sources/v3_gate5_clock_oscillation_probe_v2.md`

## 1. Purpose

Gate-5 probes show all current kernel configurations produce diffusive behavior
(no stable or coherent-oscillatory classification in quick mode). This RFC defines:

1. A formal classification of the S2880 dynamical phase diagram.
2. Operational detection criteria for each phase class.
3. A parameter sweep protocol to locate the ordered/disordered phase boundary.
4. Physical interpretation of each phase in terms of Standard Model phenomenology.

The goal is to find the parameter regime where R3 >> 1 (Δp=±3 dominant within-generation
channel) — the mesophase that corresponds to stable massive particles.

## 2. Phase Classification

### 2.1 Three dynamical phases

**Phase D (Disordered):**
- All 12 C12 phases appear with equal probability in long runs.
- R3 → 1 (all Δp channels equally probable).
- Kuramoto order parameter r → 0.
- Physical analog: deconfined high-temperature phase; no stable particles.

**Phase M (Mesophase / Z₃-locked):**
- Generation sectors locked: P(g=0) ≈ P(g=1) ≈ P(g=2) ≈ 1/3, but each fixed.
- Within-generation Z₄ sub-clock oscillating: Δp=±3 dominant (R3 >> 1).
- Kuramoto r → moderate (0.3–0.7), oscillating.
- Physical analog: stable generations with mass hierarchy; target regime for SM particles.

**Phase O (Ordered / Frozen):**
- All cells locked to a single C12 phase.
- R3 undefined (no transitions).
- Kuramoto r → 1.0, static.
- Physical analog: over-confined frozen state; no dynamics (not physical).

### 2.2 Target regime

Target: Phase M (mesophase) — the regime where particle physics emerges.
- Z₃-locked (stable generations)
- Z₄ oscillating (mass encoding via Koide mechanism, RFC-016)
- R3 ≥ 4 (strong within-generation dominance)

## 3. Detection Metrics

### 3.1 Kuramoto order parameter

```
r(t) = |mean(exp(2*pi*i * phase(x,t) / 12))|   over all x
```
Compute r as a function of tick t.

| Phase | mean(r) | std(r) over window |
|-------|---------|---------------------|
| Disordered (D) | < 0.15 | < 0.05 |
| Mesophase (M) | 0.15 – 0.7 | > 0.05 (oscillating) |
| Ordered (O) | > 0.7 | < 0.02 (stable) |

### 3.2 Generation lock score (GLS)

For each generation g ∈ {0,1,2}, compute:
```
GLS(g) = |P(current_phase_in_gen_g_orbit) - 1/3|
```
GLS → 0: perfect generation balance (disordered or perfectly mesophase).
GLS → 2/3: complete generation locking (only one generation active).

A useful mesophase indicator: GLS_var = variance over ticks is small AND R3 > 2.

### 3.3 R3 generation dominance ratio

From RFC-010:
```
R3 = P(|Δp|=3) / P(|Δp| ∈ {1,2,4,5,6})
```

| Phase | R3 |
|-------|----|
| Disordered (D) | ≈ 1 (all channels equal) |
| Mesophase (M) | >> 1 (within-gen dominant) |
| Ordered (O) | undefined (no transitions) |

R3 ≥ 2: provisional mesophase.
R3 ≥ 4: strong mesophase (RFC-010 strong threshold).

### 3.4 Spectral entropy

Compute PSD of r(t). Spectral entropy H = -Σ p(f) log p(f) (p(f) = PSD(f)/Σ PSD).

| Phase | H_spectral |
|-------|-----------|
| Disordered | → 1.0 (uniform spectrum) |
| Mesophase | < 0.5 (dominant frequency) |
| Ordered | → 0.0 (no dynamics) |

## 4. Parameter Sweep Protocol

### 4.1 Control parameter

The S2880 kernel has one primary control parameter: the channel weight distribution.
For the K0 (uniform) kernel, all 2880 output states are equally probable.
For biased kernels, the Δp=3 channel can be upweighted.

Define: `w3` = relative weight of Δp=±3 transitions in the update rule.
- w3 = 1: uniform (K0-like, current default)
- w3 > 1: Δp=3 upweighted (biased toward mesophase)
- w3 → ∞: pure Z₄ within-generation oscillation (ordered mesophase)

### 4.2 Sweep grid

Primary sweep:
```
w3 ∈ {0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0}
```
For each w3:
- Run 5 seeds × 200 ticks each
- Record: mean(r), std(r), R3, GLS_var, spectral entropy

Secondary parameter (optional):
- Seed density: sparse (10% occupied) vs dense (50%) — affects transition boundaries

### 4.3 Expected finding

At some w3_crit, the system transitions D → M:
- Below w3_crit: R3 ≈ 1, r → 0, H → 1 (disordered)
- Above w3_crit: R3 > 2, r > 0.3, H < 0.5 (mesophase)

w3_crit is the discrete analog of the inverse critical temperature T_c in the Z₁₂ clock model.

Physical prediction: the SM requires the kernel to be in the mesophase (w3 > w3_crit).
If K0 (w3=1) is already in the mesophase: existing simulations should show R3 > 1
(currently blocked by RFC-015 bug). If not, we need w3 > 1 for SM physics.

## 5. Hypotheses

### H1 (mesophase exists)

For some w3 > 1 in the S2880 kernel, the system transitions to mesophase:
1. R3 ≥ 2 across seeds and tick windows.
2. Kuramoto r oscillates coherently (std(r)/mean(r) > 0.3).
3. Generation lock scores stable (GLS_var < 0.1).

### H2 (K0 near critical)

The K0 (uniform) kernel is near the phase boundary:
1. Small biases w3 > 1 drive it into mesophase.
2. Evidence: K0 shows seed-sensitive recurrence (already observed in gate-5 data).

### H3 (Koide orbit selection in mesophase)

In the mesophase, stable motifs preferentially occupy the 120°-equispaced orbit {0,4,8}
(the Koide mass eigenstate orbit, RFC-016):
1. P(p=0) + P(p=4) + P(p=8) > P(p=1) + P(p=5) + P(p=9) in stable windows.
2. The Koide delta is measurable from this occupation asymmetry.

## 6. Physical Interpretation of Phase Diagram

| Phase | D (disordered) | M (mesophase) | O (ordered) |
|-------|---------------|--------------|-------------|
| SM analog | Pre-electroweak symmetric | Broken EW + QCD confined | Over-frozen (unphysical) |
| Particle content | No stable particles | Massive stable particles | Static frozen state |
| R3 | ~1 | >> 1 | undefined |
| Clock dynamics | Diffusive | Coherent oscillation | Frozen |
| Temperature analog | T > T_c | T < T_c | T = 0 |

The COG model predicts:
- The physical universe operates in Phase M.
- The K0 kernel represents an unphysical symmetric point (Phase D or near-critical).
- Renormalization group (RG) flow drives the effective kernel toward mesophase.
- The stable masses we observe correspond to the mesophase Koide orbit {0,4,8}.

## 7. Null Models

N1: No mesophase exists — the system only has Phase D and Phase O.
(Would indicate C12 is not rich enough for stable particle physics.)

N2: Mesophase exists but R3 saturates at R3 ≈ 2 (not >> 1).
(Would indicate weak within-generation coupling, incompatible with strong interaction.)

N3: The K0 kernel is far from critical — requires w3 >> 10 for mesophase.
(Would indicate the physical kernel has strongly biased within-generation coupling,
which is a constraint on allowed kernels, not a falsifier.)

## 8. Implementation Plan

### Phase A — Quick sweep (Codex lane)

Script: `cog_v3/calc/build_v3_phase_boundary_kernel_sweep_v1.py`

Requirements:
1. Parameterize Δp=3 channel weight `w3` in S2880 update.
2. For w3 in {1, 2, 4, 8, 16, 32}: run 5 seeds × 200 ticks.
3. Record: mean(r), std(r), R3, GLS_var, spectral_entropy.
4. Plot: R3 and mean(r) vs w3 to identify transition.

Output: `cog_v3/sources/v3_phase_boundary_sweep_v1.json` and `.md`

### Phase B — Odd-phase mesophase search

After RFC-015 fix: use odd-phase seeds (p=1, 5, 9) in the sweep.
Expected: odd-phase seeds enable R3 > 0, so the transition to mesophase is visible.

### Phase C — Koide orbit occupation

In stable runs at w3 > w3_crit: measure which C12 phases are preferentially occupied.
This directly tests H3 and feeds RFC-016 Phase B.

## 9. Promotion Gates

Gate 1:
1. H1 confirmed: mesophase found at some w3.
2. R3 > 2 and Kuramoto r oscillating coherently.

Gate 2:
1. H2 confirmed or falsified: K0 is or isn't near critical.
2. w3_crit measured with ≤50% uncertainty.

Gate 3:
1. H3 test: Koide orbit {0,4,8} preferentially occupied in mesophase.

## 10. Falsifiers

Reject this lane if:
1. No mesophase found for any w3 ≤ 100 (no R3 > 2, no coherent oscillation).
2. Phase diagram has only D and O (no intermediate M region).
3. Within-generation locking requires seed tuning that is physically unmotivated.

## 11. Cross-References

| RFC | Connection |
|-----|-----------|
| RFC-010 | R3 measurement protocol (the primary mesophase indicator) |
| RFC-015 | Odd-phase seeding required to unlock R3 measurement |
| RFC-016 | Koide orbit {0,4,8} = mesophase mass eigenstate |
| RFC-011-Amendment | Omega_hat scale ratio measurable only in mesophase |

# RFC-019: K4 Memory-2 Kernel as Phase M Mesophase Candidate

Status: Draft
Date: 2026-03-03
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-017_Phase_Boundary_and_Ordered_Phase_Detection_Contract.md`
- `cog_v3/rfc/RFC-010_C12_Phase_Sector_Generation_and_Rare_Hop_Test_Contract.md`
- `cog_v3/sources/v3_cycle_v2/round07_work_kernel_candidates_for_lorentz_pseudosymmetry.md`

## 1. Purpose

v3_cycle_v2 round07 identified K4 (memory-2 causal product kernel) as a candidate
with "inertia-like behavior and directional persistence." In the C12 context (RFC-017),
a memory-2 kernel is the natural mechanism for Z₄ within-generation orbit locking —
the defining property of Phase M (mesophase). This RFC formalizes K4 as the primary
Phase M mesophase candidate and defines how to parameterize it.

## 2. The Memory-2 Mechanism

### 2.1 Standard S2880 update (Markov, K0-like)

```
new_state = S2880_mul[stencil_fold, old_state]
new_phase = (fold_phase + old_phase) mod 12
```

The stencil_fold contributes a phase Δp. In Phase D (disordered), Δp is random → no locking.

### 2.2 Memory-2 S2880 update

```
new_state = S2880_mul[S2880_mul[memory_state, stencil_fold], old_state]
new_phase = (prev_phase + fold_phase + old_phase) mod 12
```

The memory factor `prev_phase` from the previous tick biases the new phase toward
continuing in the same Z₄ orbit. If prev_phase ∈ {p, p+3, p+6, p+9}, the memory
term keeps the new_phase in the same orbit with higher probability.

### 2.3 Why memory-2 enables Phase M

The Z₄ within-generation sub-clock {p, p+3, p+6, p+9} naturally cycles under Δp=3 hops.
In the Markov (memory-0) kernel: each tick's phase update is independent → the orbit
can escape to other generations.

In memory-2: the previous-tick phase provides an "inertia" that continues the Z₄ cycle:
- If prev_phase = 0: next step biased toward (0+Δp=3)=3, staying in Gen1
- This reduces the probability of inter-generation jumps (Δp=1, 2, 4, 5...)
- R3 increases (within-generation dominance) = Phase M signature

The memory term IS the physical mechanism for particle "mass" in the COG framework.
Mass = inertia of the C12 phase clock = resistance to changing generation.

## 3. Memory-2 Parameterization

### 3.1 Memory weight lambda

```
new_phase = (lambda * prev_phase + (1-lambda) * stencil_phase + old_phase) mod 12
```

Discretized version (lambda ∈ {0, 1/4, 1/2, 3/4, 1}):
- lambda=0: standard Markov (K0-like, Phase D)
- lambda=1/4: mild inertia (may or may not reach Phase M)
- lambda=1/2: moderate inertia
- lambda=3/4: strong inertia (expected Phase M for most seeds)
- lambda=1: pure memory-replay (trivial — no stencil contribution)

### 3.2 Discrete implementation

Rather than a fractional lambda, use a probabilistic schedule:
- With probability p_mem: use memory_state as additional stencil factor
- With probability (1-p_mem): standard Markov update

p_mem = 0: K0 (Markov), p_mem = 1: pure memory-2.

This is equivalent to K2 stochastic gating (RFC-008) but applied to the MEMORY FACTOR
rather than the stencil gates.

### 3.3 Connection to w3 (RFC-017)

The memory-2 mechanism is equivalent to the w3 upweighting (RFC-017):
- Memory adds a "previous within-generation" bias → effectively increases w3 for Δp=3
- The w3 sweep (RFC-017) and the lambda sweep (this RFC) are related parameters
- At lambda = lambda_M (phase M boundary): w3_eff = w3(lambda_M) ≥ w3_crit

A single combined sweep over (lambda, w3) maps the full phase diagram.

## 4. Physical Interpretation

### 4.1 Mass as phase inertia

Mass = lambda (memory weight). A higher lambda means stronger resistance to generation
change = heavier particle.

Prediction: within each generation, the mass hierarchy A < B < C (RFC-012 associator
activity) corresponds to:
- A-family: lower effective lambda (lightest, least inertia)
- C-family: higher effective lambda (heaviest, most inertia)

This connects to RFC-012: associator activity A < B < C exactly correlates with mass
ordering. Higher associator activity = more non-associative history = more memory-like
behavior = higher effective mass.

### 4.2 Particle stability as phase orbit coherence

In the memory-2 kernel, a stable particle is a coherent within-generation Z₄ orbit
that resists de-cohere into other generation sectors. The "lifetime" of a particle
is the time before the Z₄ orbit loses coherence (inter-generation hop occurs).

Heavy particles (high lambda) → longer Z₄ coherence → shorter lifetime (paradox?).
Actually: higher lambda → better orbit lock → MORE stable (longer lifetime).
Unstable particles = weak orbit lock = low lambda = lighter = more likely to decay.

This gives a mass-stability correlation: lighter particles are MORE stable (electron,
muon less than tau, and electron doesn't decay). ✓ Correct SM prediction.

## 5. Hypotheses

### H1 (Phase M at finite lambda)

For some lambda_M > 0 (non-trivial memory weight), the S2880 memory-2 kernel enters
Phase M: R3 ≥ 2, Kuramoto r > 0.3, stable across seeds.

### H2 (lambda ~ mass)

The memory weight lambda correlates with associator activity (RFC-012):
- A-family (Q240 order-3, lowest activity): lambda_A < lambda_B < lambda_C
- In the phase sweep: A-family seeds reach Phase M at higher w3 (more external bias needed)
- C-family seeds reach Phase M at lower w3 (self-inertia sufficient)

### H3 (memory-2 gate5 pass)

At lambda = lambda_M, K4 (memory-2 S2880) passes gate-5:
- Gate5a (stable clock): Z₄ orbit lock sustained for 1000+ ticks
- Gate5b (coherent oscillation): Kuramoto r oscillates with period ≈ 12k ticks

## 6. Null Models

N1: lambda does not help — R3 stays near 1 for all lambda (no Phase M from memory alone).
(Would indicate memory-2 is insufficient; need explicit stencil bias OR different kernel family.)

N2: lambda helps R3 but gate5 still fails (inertia without stability coherence).
(Partial Phase M — not the full ordered mesophase.)

N3: Memory-2 is equivalent to w3 sweep — no additional information.
(Combined sweep is redundant; only w3 matters independently.)

## 7. Implementation Plan

### Phase A — lambda sweep

Script: extend `build_v3_phase_boundary_kernel_sweep_v1.py` (RFC-017 script) to
include p_mem parameter:

```python
for p_mem in [0.0, 0.25, 0.5, 0.75, 1.0]:
    for w3 in [1, 2, 4, 8]:
        run_s2880_kernel(p_mem=p_mem, w3=w3, seeds=[p1, p5, p9], ticks=200)
        record(R3, r_mean, r_std, H_spectral)
```

This maps the full 2D phase diagram (p_mem, w3).

### Phase B — Associator-sorted seeds

Within the Phase M region (p_mem ≥ p_mem_M, w3 ≥ w3_crit):
1. Run seeds from A-family, B-family, C-family separately.
2. Measure R3 and Kuramoto r for each family.
3. Test whether C-family requires lower (p_mem, w3) to reach Phase M than A-family.

### Phase C — gate5 test

At best (p_mem, w3) from Phase A:
1. Run 1000+ tick runs.
2. Apply gate5 classification (Kuramoto r threshold, RFC-017).
3. Report stable/oscillatory/diffusive classification for K4.

## 8. Promotion Gates

Gate 1:
1. H1 confirmed: Phase M found at some (lambda, w3) with R3 > 2 and r > 0.3.

Gate 2:
1. H2 test: A/B/C family seeds reach Phase M at different (lambda, w3).
2. Ordering matches mass hierarchy (C-family easiest to Phase M).

Gate 3:
1. H3 confirmed: gate5 pass in K4 memory-2 at optimal (lambda, w3).

## 9. Relation to Other RFCs

| RFC | Connection |
|-----|-----------|
| RFC-017 | Phase M detection — K4 is candidate kernel to achieve it |
| RFC-012 | Associator activity A<B<C maps to lambda_A<lambda_B<lambda_C |
| RFC-016 | Koide delta = stable phase occupation in K4 Phase M |
| RFC-018 | Gate4 chirality — K4 in Phase M with odd-phase seeds unlocks gate4 |
| RFC-010 | R3 measurement — K4 mesophase should show R3 >> 1 |

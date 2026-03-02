# Round 11 Work - Integrated Experiment Matrix and Fail-Fast/Confirm Pipeline
Date: 2026-03-02
## Matrix axes
1. Kernel candidate: K1/K2/K3
2. Neighborhood: cube26 (default lane)
3. Seed class: P1/P2/P3/P4 from Round 01
4. Event-order seed: fixed deterministic stream per run
5. Boundary: fixed vacuum default
## Pipeline
1. **Stage A (cheap scan)**
   - short horizon
   - fail-fast criteria enabled
   - record all metrics
2. **Stage B (candidate replay)**
   - medium horizon
   - same seed and mirrored controls
3. **Stage C (confirm)**
   - longer horizon
   - coarse-grained anisotropy checks
## Pass thresholds (initial)
1. Stability:
   - no collapse in Stage A
   - repeatable loop indicator in Stage B
2. Chirality:
   - nontrivial chirality observable divergence between motif and mirror
3. Lorentz-like:
   - anisotropy decreases under coarse-graining (at least first two levels)
## Logging contract
Each run row must include:
- kernel_id
- seed_signature
- rng_seed
- survival_ticks
- period_estimate
- drift_vector
- chirality_vector
- anisotropy_micro
- anisotropy_block2
- anisotropy_block4
- status (pruned, candidate, confirmed)
## Next operational step
Implement runner update to enforce this staged pipeline uniformly.

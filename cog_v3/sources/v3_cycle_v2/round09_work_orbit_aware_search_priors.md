# Round 09 Work - Orbit-Aware Search Priors and Pruning
Date: 2026-03-02
## Objective
Reduce search complexity for stable motifs by using S960 structure as priors.
## Proposed prior features
1. Element order (1,2,3,4,6,12)
2. Q-family (A/B/C)
3. Conjugation-tier proxy (1/29/46)
4. Local neighborhood entropy (from seed voxel distribution)
5. e000/e111 occupancy ratio
## Candidate score (heuristic)
score = w1*order_signal + w2*family_mix + w3*conj_tier + w4*local_entropy + w5*anchor_balance
Initial directional weights (speculative):
- w1=0.30, w2=0.20, w3=0.20, w4=0.15, w5=0.15
## Fail-fast pruning
1. Stop at early horizon if motif mass decays below threshold.
2. Stop if anisotropy blow-up exceeds limit in first window.
3. Stop if mirrored control outruns candidate by large margin without stability gain.
## Data products to collect per batch
- survival_ticks
- period_estimate
- drift_vector
- chirality observables
- anisotropy metrics (micro + coarse-grained)
## Outcome
Use ranked prior queue rather than uniform random seeding for overnight runs.

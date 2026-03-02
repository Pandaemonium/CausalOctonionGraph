# Round 07 Work - Kernel Candidate Shortlist for Mesoscale Lorentz-Like Behavior
Date: 2026-03-02
## Candidate families
1. **K1 cube26-uniform-fold**
   - 26-neighbor support, deterministic seeded permutation per tick/layer.
   - Pros: best isotropy potential on cubic grid.
   - Risk: high mixing may erase motifs.
2. **K2 cube26-shell-scheduled**
   - Face/edge/corner shells processed in rotating seeded orders.
   - Pros: tunable anisotropy suppression while preserving locality hierarchy.
   - Risk: shell schedule may introduce periodic artifacts.
3. **K3 cube26-split-step**
   - Two or more sub-steps with disjoint neighbor subsets (quantum-walk-inspired structure).
   - Pros: better control of dispersion and chirality channels.
   - Risk: more parameters and larger search space.
4. **K4 memory-2 causal product**
   - Includes one-step historical factor (minimal non-Markov extension).
   - Pros: can model inertia-like behavior and directional persistence.
   - Risk: computational cost and calibration complexity.
## Discrimination metrics (must-pass)
1. Low-k velocity anisotropy (max directional spread / mean).
2. Front eccentricity for isotropic launch.
3. Bidirectional symmetry check for parity-neutral controls.
4. Motif retention score (ground and mildly excited motifs).
## Recommended priority
- First pass: K1 vs K2 head-to-head.
- If both fail anisotropy gate: evaluate K3.
- Only introduce K4 after baseline isotropy is acceptable.

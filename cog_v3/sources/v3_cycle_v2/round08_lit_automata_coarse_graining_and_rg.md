# Round 08 Literature - Coarse-Graining and RG for Automata
Date: 2026-03-02
## Sources reviewed
1. Coarse-graining cellular automata literature (Israeli & Goldenfeld direction; emergent effective laws).
2. QCA renormalization discussions in quantum-information and lattice communities.
3. Hydrodynamic/continuum emergence in discrete kinetic systems (LGA/LBM analogs).
## Key lessons
1. Mesoscale symmetry can emerge even when microscale rule is anisotropic.
2. Emergence typically requires:
   - averaging over many micro-events,
   - stable conserved/approximately conserved quantities,
   - weakly biased update order or symmetry-canceling schedules.
3. RG-style diagnostics are useful for rule selection:
   - define block observables,
   - test whether anisotropy shrinks under block scale.
## v3 translation
1. Add block-spin style diagnostics at block sizes 2, 4, 8, 16 voxels.
2. Require monotonic anisotropy decrease across at least first 2 coarse-grain levels.
3. Reject kernels where anisotropy plateaus or amplifies under coarse-graining.
## Round output
- Integrate RG anisotropy-decay metric into kernel selection contract.

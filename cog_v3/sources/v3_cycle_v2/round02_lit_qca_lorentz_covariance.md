# Round 02 Literature - QCA/QW Lorentz Emergence Constraints
Date: 2026-03-02
## Goal
Extract practical kernel constraints from Lorentz-emergence literature.
## Sources reviewed
1. Bialynicki-Birula, "Weyl, Dirac, and Maxwell equations on a lattice as unitary cellular automata" (1994).
2. D'Ariano, Perinotti et al., "Weyl, Dirac and Maxwell quantum cellular automata" (arXiv:1306.1934).
3. Bisio, D'Ariano, Perinotti, "Quantum walks, Weyl equation and Lorentz group" (arXiv line; Lorentz deformation at lattice scale).
4. Arrighi et al. (QCA causality/locality formalisms, representation constraints).
## What consistently matters
1. Exact microscale Lorentz invariance is generally impossible on a fixed lattice; target is low-k (long wavelength) isotropy/covariance.
2. Dispersion isotropy is the key quantitative discriminator:
   - group velocity should depend weakly on direction for small |k|.
3. Chiral sectors are easiest to preserve when update structure is factorized/split-step and symmetry constraints are explicit.
4. Locality + reversibility/unitarity analogs strongly constrain admissible rule families.
## Translating to our multiplicative COG setting
1. We should optimize for low-k directional degeneracy, not exact tick-level symmetry.
2. Kernel scoring must include shell-wise anisotropy tests in Fourier-like probes.
3. Event-order randomization can reduce systematic bias, but cannot replace structural isotropy.
4. Candidate kernels should be tested on multi-direction wavepacket propagation, not just axial launches.
## Round output
- Add mandatory metrics to kernel gate:
  - low-k velocity anisotropy,
  - front-shape eccentricity,
  - direction-dependent decay constants.

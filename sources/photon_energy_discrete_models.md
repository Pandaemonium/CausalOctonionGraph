# Photon Energy in Discrete and Algebraic Models: Literature Review

**Date:** 2026-02-24
**Purpose:** Ground RFC-015 (Photon Energy in COG). Covers four research threads:
(1) causal set / Sorkin-Johnston scalar QFT, (2) quantum cellular automata / D'Ariano-Perinotti,
(3) octonion / division algebra approaches to U(1)_EM, (4) CDT / spin foam / Wolfram models.

---

## §1. Causal Set Theory: Scalar QFT and Photon Propagation

### 1.1 Core Formalism

The Sorkin-Johnston (SJ) programme is the most developed rigorous framework for
quantum field theory on a discrete causal graph. The key result: the entire Gaussian
scalar QFT is encoded in the retarded Green function G(x,y), which is constructible
from the causal partial order alone. Particle energy is not assumed — it is an
eigenvalue of the discrete Pauli-Jordan function.

**Foundational papers:**

- **Johnston (2009), arXiv:0909.0944** — "Feynman Propagator for a Free Scalar Field on
  a Causal Set." Constructs G(x,y) from causal set structure; massless photon-like
  modes emerge from the m→0 limit. Energy is the eigenvalue structure of the
  propagator matrix, not an independent input.

- **Johnston (2010), arXiv:1010.5514** — Ph.D. thesis extending to interactions and
  fermions. The mass parameter appears as a discrete counting scale. **Direct support
  for COG: mass/energy as a purely combinatorial quantity.**

- **Sorkin (2011), arXiv:1107.0698** — Recasts as a histories/path-integral formulation.
  The d'Alembertian is the generalized inverse of the discrete retarded Green function.
  Crucially: energy is not mode-sharp on a causal set; it is an aggregate of the
  decoherence functional. Pure E=hf is an idealization requiring the continuum limit.

- **Sorkin (2017), arXiv:1703.00610** — "From Green Function to Quantum Field." Clean
  pedagogical statement: the entire QFT is recoverable from the causal structure alone.

- **Nomaan X (2023), arXiv:2306.04800** — 2023 review. Confirms: **photon/gauge boson
  fields on causal sets remain an open problem**. The SJ formalism applies to scalars;
  the electromagnetic (spin-1) field has no complete causal set treatment yet.

### 1.2 Photon Propagation on Causal Sets

- **Dowker, Henson, Sorkin (2010), arXiv:1009.3058** — "Discreteness and the
  Transmission of Light from Distant Sources." The massless scalar field (proxy for
  photon) propagates on a causal set without significant disruption to pulse timing or
  effective frequency. The discrete substrate does **not** modify E=hf in the IR limit.
  Key result: photon propagation on a causal set reproduces continuum behavior.

- **Sorkin (2009), arXiv:0910.0673** — "Light, Links and Causal Sets." The EM field
  produced by a moving charge is reconstructed by summing over past causal links.
  **Each link carries a retarded potential amplitude. Photon energy is carried on causal
  links — consistent with the COG claim that photon energy lives on graph edges.**

### 1.3 Discreteness Scale and UV Cutoff

- **Aslanbeigi, Saravani, Sorkin (2014), arXiv:1403.1622** — "Generalized Causal Set
  d'Alembertians." Constructs a family of nonlocal Lorentz-invariant d'Alembertians.
  For momenta |p| >> rho^{-1/4}, the dispersion relation deviates from E^2 = p^2c^2.
  The nonlocality scale 1/rho^{1/4} is a combinatorial time quantum — the literature's
  closest analogue to a "topological minimum interval." At low energy, E=|p|c exactly.

- **Belenchia, Benincasa, Dowker (2015), arXiv:1510.04656** — Rigorously proves the
  mean of the causal set d'Alembertian converges to Box in 4D Minkowski. E=|p|c is
  recovered exactly in the infrared. Also derives an R/2 curvature correction from
  discreteness not present in naive continuum approaches.

- **Buck, Dowker, Jubb, Sorkin (2016), arXiv:1609.03573** — Energy diverges at
  light-cone topology change: **energy is a topological residue of the causal
  structure, localized on light-cone boundaries (causal edges)**.

### 1.4 Sverdlov: Gauge/EM Field as Holonomy on Causal Links

- **Sverdlov (2008), arXiv:0807.2066** — Gauge fields on causal sets as holonomies
  around loops in the partial order. The photon field is parallel transport amplitude
  on causal links. Maxwell action recovered in the continuum limit.

- **Sverdlov (2009), arXiv:0905.2263** — Ph.D. thesis compiling gauge + spinor fields
  on causal sets. Photon energy is implicit in the Maxwell action sum over causal
  intervals; no discrete energy quantum per link is identified.

---

## §2. Quantum Cellular Automata: D'Ariano-Perinotti Photon

This is the most developed rigorous construction of photon energy from a discrete graph.

### 2.1 Photon as Composite Fermi-Pair

- **Bisio, D'Ariano, Perinotti (2014), arXiv:1407.6928** — **"Quantum Cellular
  Automaton Theory of Light."** **The central result for COG.** The photon is modeled
  as a composite boson built from two correlated massless Weyl fermions, each living
  on a QCA. Free Maxwell's equations emerge from two Weyl QCAs in the limit of small
  wave-vector k. Photon energy is NOT postulated — **it emerges from the bosonic
  statistics recovered when Fermi-pair density is low.** The frequency omega is the
  rate of phase accumulation in the QCA coin step — directly analogous to the COG
  notion of energy as computational tick frequency. Three testable predictions:
  dispersive propagation, small longitudinal polarization, Fermionic saturation.

- **D'Ariano, Mosco, Perinotti, Tosini (2016), arXiv:1603.06442** — 3+1D Dirac QCA.
  Mass enters as a discrete coin-rotation angle: **mass = frequency of evaluation
  ticks.** This is the QCA derivation of the COG mass-as-drag principle.

- **D'Ariano (2012), arXiv:1211.2479** — "The Dirac Quantum Automaton: a preview."
  QCA is the minimal-assumption extension of QFT to the Planck scale. Lorentz
  invariance is emergent. No continuum divergences by construction.

- **Suprano et al. (2024), arXiv:2402.07672** — First experimental photonic QCA
  implementation in 1+1D, observing Zitterbewegung. Validates QCA gives correct
  relativistic dynamics.

### 2.2 Feynman Checkerboard

- **Earle (2010), arXiv:1012.1564** — Reconciles two checkerboard formulations.
  Each direction reversal contributes amplitude iε ~ iℏ. The mass parameter
  m = ε/(lattice step) = density of reversals. **Direct grounding for ΔS = ℏ per
  edge and for mass as computational-reversal frequency.**

- **Smith (1995), arXiv:quant-ph/9503015** — 4D HyperDiamond checkerboard. The D4
  root lattice gives the checkerboard in 3+1D; exceptional groups E6/D5/D4 appear
  naturally. Octonion-related gauge group hierarchy from discrete path integral.

- **D'Ariano, Mosco, Perinotti, Tosini (2014), arXiv:1406.1021** — Exact analytical
  path-integral solution for 1+1D Dirac QCA via Jacobi polynomials. Generalizes
  Feynman checkerboard: each lattice step contributes a transition matrix factor.

### 2.3 Discrete U(1) Gauge Theory from Quantum Walks

- **Arnault, Debbasch (2015), arXiv:1508.00038** — "Quantum Walks and Discrete Gauge
  Theories." Proves quantum walks can simulate full U(1) gauge theories with exact
  discrete local gauge invariance. A discrete EM field tensor is constructed from gauge
  phases. **Discrete Maxwell equations are derived from the curvature of the gauge
  connection — photon energy encoded in discrete curvature, not assumed.**

- **Arnault et al. (2016), arXiv:1605.01605** — Extends to non-Abelian U(N)/SU(N)
  discrete gauge walks. First step toward discrete Yang-Mills from quantum walks.

- **Arnault et al. (2018), arXiv:1807.08303** — Quantum walks as fermions of lattice
  gauge theory. Shows fundamental tension between discrete gauge invariance and exact
  lattice translational symmetry (staggered fermion problem). Relevant to COG's
  treatment of discrete SU(3).

---

## §3. Octonion and Division Algebra Approaches to U(1)_EM

### 3.1 Summary Finding

**No paper in the division algebra / octonion literature derives photon energy.**
Furey and co-authors identify U(1)_EM as a symmetry group from the number operator
Q = N/3 = (1/3)Σ αᵢ†αᵢ, and mention "one photon" as a 1 representation of SU(3),
but no photon operator, propagator, or energy formula is given.

### 3.2 Furey: U(1)_EM from C⊗O

- **Furey (2016/2015), arXiv:1603.04078** — "Charge Quantization from a Number
  Operator." The U(1)_EM charge Q = N/3 built from three ladder operators; eigenvalues
  give all electric charges of one generation. **The U(1) photon is the gauge boson of
  this number operator; e7 is the vacuum axis fixed by SU(3).** No photon operator.

- **Furey (2019), arXiv:1910.08395** — Three generations in C⊗O acting on itself.
  In the Addendum: "gauge bosons should be associated with elements of a Jordan algebra
  subspace." Counts "one photon" among the singlet representations but does not
  identify a specific operator. Notes: "Still left to describe would be W bosons,
  the Higgs, and potentially right-handed neutrinos."

- **Furey (2018), arXiv:1806.00612** — Full SM gauge group SU(3)_C × SU(2)_L × U(1)_Y
  from R⊗C⊗H⊗O ladder symmetries. U(1)_Y hypercharge from U(n) octonion symmetry.
  U(1)_EM as the unbroken combination after electroweak breaking. No photon energy.

- **Furey, Hughes (2022), arXiv:2209.13016** — Gauge bosons + Higgs + fermions inside
  32C-dim A = R⊗C⊗H⊗O. U(1)_EM identified as the subalgebra invariant under complex
  conjugation. Photon is the gauge boson of this conjugation-invariant U(1), but no
  photon field or energy is written down.

- **Furey (2025), arXiv:2505.07923** — Gauge bosons + three fermion generations form
  a superalgebra isomorphic to H₁₆(C). The photon sits in the u(1)_EM sector, still
  without energy formula.

### 3.3 Nurowski: Split Octonions and Vacuum Maxwell Equations

**Critical result for COG:** The vacuum Maxwell equations can be written as the
octonionic analyticity condition ∂F = 0 using SPLIT octonions.

- **Nurowski (2009), arXiv:0906.2060** — "Split Octonions and Maxwell Equations."
  With F = (Ex + e7·Bx)e1 + (Ey + e7·By)e2 + (Ez + e7·Bz)e4 and gradient
  ∂ = e1∂x + e2∂y + e4∂z + e7∂t, the equation ∂F = 0 is exactly the four vacuum
  Maxwell equations. **The photon field F lives in the 6D space {e1,e2,e3,e4,e5,e6}
  perpendicular to e7. The e7 direction acts as the time-operator.** Only works for
  split octonions (not ordinary octonions).

- **Beradze, Shengelia (2016), arXiv:1610.06418** — Dirac + Maxwell from split-
  octonionic analyticity ∂F = 0 in an alternative basis.

- **Gogberashvili, Gurchumelia (2020), arXiv:2012.02255** — SO(4,4) triality gives
  both Dirac (spinor-like) and Maxwell (vector-like) Lagrangians from split octonions.

**COG implication from Nurowski:** The photon field in COG naturally lives in the
6D subspace {e1,e2,e3,e4,e5,e6}, with e7 as the causal (temporal) direction.
The COG convention (e7 = vacuum axis) is consistent with e7 as the time operator
in the split-octonionic EM framework. However, COG uses ordinary (not split) octonions,
so this is a structural analogy, not a direct import.

### 3.4 Manogue-Dray-Wilson: Gauge Bosons from Exceptional Algebras

- **Manogue, Dray (1998), arXiv:hep-th/9807044** — 10D octonionic Dirac equation with
  dimensional reduction. Produces massless leptons and massive quarks but does NOT
  produce a spin-1 photon from the spinor sector.

- **Dray, Manogue, Wilson (2023), arXiv:2309.00078** — New E8 decompositions.
  Photon implicit as gauge boson within SO(7,3) Standard Model embedding.

---

## §4. CDT, Spin Foam, and Wolfram Models

### 4.1 Causal Dynamical Triangulations

- **Ambjorn, Goerlich, Jurkiewicz, Loll (2008), arXiv:0807.4481** — 4D de Sitter
  spacetime emerges from summing over ~600,000 discrete simplices. Newton's constant
  and Planck energy emerge from combinatorial ratios. No continuous metric input.

- **Ambjorn, Gorlich, Jurkiewicz, Loll (2007), arXiv:0712.2485** — Planck length
  derived from ratio of lattice spacing to Newton's constant — purely algebraic.

- **Ambjorn, Loll (2024), arXiv:2401.09399** — Current review. Spectral dimension
  flows from 4 at large scales to ~2 at Planck scale. Spectral dimension (random walk
  diffusion rate) is the CDT analogue of "topological frequency."

### 4.2 Spin Foam / LQG

- **Yang, Ma (2008), arXiv:0812.3554** — "Quasi-Local Energy in LQG." Energy operators
  built from discrete area/volume eigenvalues. **Energy = algebraic function of spin
  network geometry, not a continuous field quantity.**

- **Alfaro, Palma (2005), arXiv:hep-th/0501116** — LQG modifies photon dispersion:
  v(E) = c(1 - kE/E_Planck). The modification is purely combinatorial; E_Planck is
  a counting scale. **Photon energy is modified from E=|p|c by graph discreteness.**

### 4.3 Wolfram Physics / Hypergraph Rewriting

- **Gorard (2020), arXiv:2011.12174** — "Algorithmic Causal Sets and the Wolfram Model."
  Proves hypergraph rewriting provides algorithmic dynamics for causal set evolution.
  Causal invariance → Lorentz symmetry from combinatorics. Benincasa-Dowker action
  recovered as special case. **Energy = combinatorial structure of the rewriting graph.**

- **Gorard (2021), arXiv:2102.09363** — Full GR (CCZ4 formalism) implemented on
  hypergraph. **Energy content = curvature of hypergraph topology.** Validated against
  Schwarzschild, Kerr, and binary merger.

### 4.4 "Topological Frequency" in the Literature

The concept appears under several names but is not a named concept:

- **Belenchia (2015), arXiv:1510.04665** — Nonlocality scale ρ^{1/4} acts as a
  combinatorial frequency cutoff: above ω_max ~ ρ^{1/4}, the discrete operator no
  longer approximates the continuum. This is the "topological Nyquist frequency."

- **Farrelly, Short (2013), arXiv:1303.4652** — Causal fermions in discrete spacetime
  as QCA. Lattice Nyquist frequency ω_max = π/a where a = lattice step. The COG
  notion of "topological frequency" as 1/(tick interval) is exactly this.

- **Johnston (2010), arXiv:1010.5514** — Positive-frequency modes (defining the vacuum)
  are determined by eigenvalues of a discrete matrix with entries ±1 from causal
  relations. **Energy is literally an eigenvalue of a combinatorial matrix.**

---

## §5. Key Results Table

| Claim | Best Reference | Verdict |
|---|---|---|
| Each causal link = one quantum of action | Johnston 1010.5514, Earle 1012.1564 | Well-supported |
| Photon energy emerges from graph statistics (not assumed) | D'Ariano et al. 1407.6928 (QCA photon) | Strong — QCA derivation |
| Photon propagation unmodified by causal set discreteness (IR) | Dowker, Henson, Sorkin 1009.3058 | Strong — direct proof |
| Photon field lives perpendicular to vacuum axis (split-octonion analogy) | Nurowski 0906.2060 | Structural analogy only |
| E=hf modified at Planck scale | Alfaro-Palma hep-th/0501116, Aslanbeigi et al. 1403.1622 | Literature consensus |
| Photon energy from octonion algebra | No paper found | Open problem |
| e7 as photon operator (explicitly) | No paper found | COG-native claim |
| "Topological frequency" as named concept | No paper found | COG-native terminology |
| Energy as discrete eigenvalue of combinatorial matrix | Johnston 1010.5514 | Well-supported |
| Energy = hypergraph curvature density | Gorard 2011.12174, 2102.09363 | Well-supported (Wolfram model) |
| Maxwell equations from split-octonion analyticity | Nurowski 0906.2060 | Proved (split octonions) |
| Discrete U(1) Maxwell from quantum walk curvature | Arnault, Debbasch 1508.00038 | Proved (QCA framework) |

---

## §6. Gaps for COG

1. **No paper derives photon energy from ordinary (not split) octonions.** Nurowski
   requires split octonions. The COG framework uses ordinary C⊗O. Bridging this is
   an open problem.

2. **No paper assigns e7 explicitly as a photon operator.** Furey and all division-
   algebra papers use e7 as the vacuum axis fixing SU(3). The COG claim (RFC-013) that
   L_{e7} IS the photon operator is a COG-native hypothesis not present in the literature.

3. **The D'Ariano-Perinotti QCA construction of the photon** (arXiv:1407.6928) is the
   most developed framework where photon energy truly emerges from graph statistics.
   The COG framework would benefit from alignment with this: if the photon is a
   composite Fermi-pair in C⊗O terms, what are the two Weyl components?

4. **Photon energy ∝ V_particle (transition energy)** — the correct directional
   relationship (E_mu_photon > E_e_photon) — has no direct literature analogue. It
   would emerge from a COG orbital level calculation analogous to the Bohr energy
   levels but using tick-counts in place of Coulomb energy.

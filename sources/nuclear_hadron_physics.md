# Nuclear & Hadronic Physics — Literature Survey for COG Simulation Targets

**Generated:** 2026-02-21
**Purpose:** Establish the empirical targets and theoretical models that COG's tritium simulation
must eventually reproduce. This file covers: nuclear structure, few-body methods, beta decay,
ab initio nuclear theory, and the quark-level picture of nucleons.
**Scope:** Targeted at COG Phases 4.4–4.6 (hydrogen → deuterium → tritium simulation).

---

## 1. The Target: What COG Must Reproduce

COG's immediate simulation goal (Phase 4.6) is a tritium microstate that:
1. Is **metatastable** — the tritium graph motif persists for many steps before decaying.
2. Undergoes **beta decay** — one neutron's quark content rearranges ($d \to u + W^- \to u + e^- + \bar{\nu}_e$), converting the neutron node into a proton + electron + antineutrino emission.
3. Has **deuterium as a stable sub-system** — the proton + neutron motif does not spontaneously decay.

The empirical facts that constrain this:

| Quantity | Value | Source |
|---|---|---|
| Tritium half-life | $12.32 \pm 0.02$ yr | Measured |
| Tritium binding energy | $8.482$ MeV ($= 2.829$ MeV/nucleon) | Measured |
| Deuterium binding energy | $2.225$ MeV (stable) | Measured |
| Proton mass | $938.272$ MeV/$c^2$ | PDG |
| Neutron mass | $939.565$ MeV/$c^2$ | PDG |
| $m_n - m_p$ | $1.293$ MeV/$c^2$ | PDG |
| Beta decay $Q$-value | $18.59$ keV (tritium) | Measured |
| Neutron lifetime | $879.4 \pm 0.6$ s (free) | PDG |

---

## 2. Ab Initio Nuclear Structure — Few-Body Sector

The most relevant physics for COG is the **A = 2, 3** sector (deuteron, triton, helion).
These are tractable with exact methods and provide the cleanest test of nuclear forces.

### N1. The Triton with Long-Range Chiral N3LO Three-Nucleon Forces (2011)
- **Authors:** Skibinski, Golak, Topolnicki, Witala, Epelbaum, Gloeckle, Krebs, Nogga, Kamada
- **arXiv:** [1107.5163](https://arxiv.org/abs/1107.5163) (nucl-th)
- **Key result:** First calculation of the triton binding energy including long-range N3LO
  three-nucleon forces from chiral EFT. The two short-range parameters are fixed from the
  triton binding energy + neutron-deuteron doublet scattering length. Three-nucleon force
  contributions range from 100 keV to ~1 MeV.
- **Relevance to COG:** Establishes the quantitative role of three-body forces in the triton.
  COG's model of tritium as three color-entangled nodes (two neutrons + one proton) must
  reproduce the ~8.48 MeV binding energy. The three-body force contribution (from residual
  $SU(3)$ color-leakage edges between quark nodes) is a non-negligible part of the binding.

### N2. Precision Nucleon-Nucleon Potential at Fifth Order in the Chiral Expansion (2014)
- **Authors:** Epelbaum, Krebs, Meissner
- **arXiv:** [1412.4623](https://arxiv.org/abs/1412.4623) (nucl-th, hep-ph)
- **Key result:** N5LO nucleon-nucleon potential from chiral EFT. Substantially improved
  description of NN phase shifts. Confirms good convergence of the chiral expansion. Opens
  the door to precision ab initio calculations in few-body systems.
- **Relevance to COG:** The most precise effective model of the NN force available. COG's
  strong-nuclear residual edges (color-leakage between proton and neutron nodes) must
  reproduce the NN potential qualitatively. The COG equivalent of "one-pion exchange" would
  be a single-edge interaction between quark nodes of different nucleons via $SU(3)$ edges.

### N3. Ab Initio Nuclear Reaction Theory with Applications to Astrophysics (2022)
- **Authors:** Petr Navratil, Sofia Quaglioni
- **arXiv:** [2204.01187](https://arxiv.org/abs/2204.01187) (nucl-th, nucl-ex)
- **Key result:** Overview of no-core shell model (NCSM) and NCSM with continuum (NCSMC)
  for ab initio nuclear reactions. Covers radiative capture and transfer reactions in light
  nuclei relevant for astrophysics ($p + d \to {}^3\text{He} + \gamma$, etc.).
- **Relevance to COG:** NCSM provides the state-of-the-art quantum mechanical description
  of tritium-relevant reactions. COG's graph motif for tritium should qualitatively reproduce
  the nuclear structure that NCSM computes.

### N4. A Guided Tour of Ab Initio Nuclear Many-Body Theory (2020)
- **Author:** Heiko Hergert
- **arXiv:** [2008.05061](https://arxiv.org/abs/2008.05061) (nucl-th, nucl-ex)
- **Key result:** Survey of ab initio nuclear methods: NCSM, coupled cluster, in-medium SRG,
  valence-space IMSRG. Coverage of light through medium-mass nuclei. Reviews achievements
  and open problems.
- **Relevance to COG:** Best overview of what "ab initio" means in nuclear physics. COG's
  simulation of tritium is an extreme version of this program: instead of an effective nuclear
  Hamiltonian, COG uses the octonionic DAG update rule, with no nuclear potential fitted
  to data.

### N5. Chiral Effective Field Theory after Thirty Years: Nuclear Lattice Simulations (2021)
- **Author:** Dean Lee
- **arXiv:** [2109.09582](https://arxiv.org/abs/2109.09582) (nucl-th, hep-lat)
- **Key result:** Review of nuclear lattice simulations based on chiral EFT. Lattice methods
  can directly compute nuclear structure without solving the Schrödinger equation analytically.
  Discusses the pinhole algorithm and Monte Carlo methods for light nuclei.
- **Relevance to COG:** Nuclear lattice simulations are conceptually the closest mainstream
  approach to COG: a discrete, graph-like substrate (the lattice) with local interaction rules
  (chiral EFT operators) produces nuclear bound states. COG differs by using an octonionic
  algebraic update rule instead of a fitted effective Hamiltonian.

### N6. Ab Initio Nuclear Thermodynamics from Lattice Effective Field Theory (2021)
- **Authors:** Lu, Li, Elhatisari, Lee, Drut, Lähde, Epelbaum, Meissner
- **arXiv:** [2112.01392](https://arxiv.org/abs/2112.01392) (nucl-th, hep-lat)
- **Key result:** Lattice EFT calculation of nuclear thermodynamics using the pinhole trace
  algorithm. Computes equation of state, liquid-vapor coexistence, and critical point of
  nuclear matter from first principles.
- **Relevance to COG:** Demonstrates that even nuclear thermodynamics can be computed from
  a discrete lattice substrate. The "pinhole algorithm" (fixing nucleon number in a finite
  box) is structurally analogous to COG's finite DAG with fixed node types.

---

## 3. Quark-Level Picture of Nucleons — COG Node Structure

In COG, nucleons are 3-node color-entangled motifs (quarks). Understanding the quark-level
picture of nucleons is essential for defining the COG microstate for tritium.

### Q1. Deep Inelastic Scattering with Application to Nuclear Targets (1985/2022)
- **Author:** Robert Jaffe
- **arXiv:** [2212.05616](https://arxiv.org/abs/2212.05616) (hep-ph, nucl-th)
- **Key result:** Classic lectures on parton model and DIS. Convolution formalism for
  nucleons, nucleon correlations. The quark-level description of nuclear targets. The EMC
  effect (quarks in nuclei differ from free quarks).
- **Relevance to COG:** Establishes what "quarks in nuclei" means. For COG, the quark nodes
  in a tritium motif are not free quarks — they are modified by their graph-topological
  environment (proximity to neighboring nucleon nodes). This is the COG analog of the EMC effect.

### Q2. Bound H-dibaryon from Full QCD Simulations on the Lattice (2011)
- **Authors:** HAL QCD Collaboration
- **arXiv:** [1111.5098](https://arxiv.org/abs/1111.5098) (hep-lat, hep-ph, nucl-th)
- **Key result:** H-dibaryon (two-baryon state with $S=-2$) is shown to be a bound state
  in flavor-$SU(3)$ symmetric QCD. Binding energy 20-50 MeV. The Bethe-Salpeter wave
  function method extracts the inter-baryon potential from lattice QCD.
- **Relevance to COG:** Demonstrates that lattice QCD can compute multi-baryon bound states.
  The HAL QCD Bethe-Salpeter method is the gold standard for deriving nuclear forces from QCD.
  COG's color-leakage residual edges should reproduce qualitatively the same short-range
  repulsion + medium-range attraction that HAL QCD finds.

### Q3. Three-Nucleon Forces Explored by Lattice QCD Simulations (2011)
- **Authors:** HAL QCD Collaboration
- **arXiv:** [1112.4103](https://arxiv.org/abs/1112.4103) (hep-lat)
- **Key result:** Three-nucleon force (3NF) calculated from lattice QCD in the triton
  channel ($I=1/2, J^P=1/2^+$). Linear geometry used to reduce computational cost. Repulsive
  3NF found at short distance (consistent with nuclear saturation).
- **Relevance to COG:** The 3NF in lattice QCD arises from the quark-gluon interactions
  between three nucleons simultaneously. In COG, the 3NF analog would be a three-body
  graph interaction term — residual $SU(3)$ edges that simultaneously connect quark nodes
  from all three nucleons in a triton motif.

---

## 4. Beta Decay — The Key Decay Mechanism

Tritium undergoes beta-minus decay: ${}^3\text{H} \to {}^3\text{He} + e^- + \bar{\nu}_e$.
At the quark level: $d \to u + W^- \to u + e^- + \bar{\nu}_e$ (one down quark in a neutron
converts to an up quark). COG must model this as a graph topology change.

### B1. Beta Decay in Medium-Mass Nuclei with the IMSRG (2021)
- **Author:** S.R. Stroberg
- **arXiv:** [2109.13462](https://arxiv.org/abs/2109.13462) (nucl-th)
- **Key result:** Review of ab initio calculations of allowed beta decays (Fermi and
  Gamow-Teller) in the valence-space IMSRG approach. Addresses the long-standing "quenching
  problem" of the axial coupling $g_A$.
- **Relevance to COG:** Establishes the nuclear structure context for beta decay calculations.
  In COG, beta decay is not mediated by $g_A$ coupling but by a graph topology change. However,
  COG must reproduce the correct $Q$-value (18.59 keV for tritium) and transition rate, which
  requires that the COG `SU2` edge operator implements the correct Fermi + Gamow-Teller matrix
  elements.

### B2. The Project 8 Neutrino Mass Experiment (2022)
- **Authors:** Project 8 Collaboration
- **arXiv:** [2203.07349](https://arxiv.org/abs/2203.07349) (nucl-ex)
- **Key result:** Tritium beta decay is the most sensitive probe of absolute neutrino mass.
  Project 8 uses Cyclotron Radiation Emission Spectroscopy (CRES) with atomic tritium to
  measure the endpoint of the beta spectrum. Target: 40 meV/$c^2$ neutrino mass sensitivity.
- **Relevance to COG:** Tritium beta decay is experimentally very well characterized. The
  phase space of the emitted electron and antineutrino is precisely known. COG's beta decay
  mechanism must be consistent with this endpoint spectrum (i.e., the antineutrino node
  emitted in the COG decay has a tick frequency consistent with sub-eV mass).

---

## 5. COG Simulation Architecture: Tritium Microstate Specification

Based on the above literature, the COG tritium microstate has the following structure:

### 5.1 Node Types Required

| Node | NodeLabel | CO state | Physical meaning |
|---|---|---|---|
| u quark (proton 1) | `V` | Witt vacuum + U(1) phase | up quark in proton |
| d quark (proton 2) | `V` | Witt vacuum + U(1) phase | down quark in proton |
| d quark (proton 3) | `V` | Witt vacuum + U(1) phase | down quark in proton |
| u quark (neutron₁ 1) | `V` | Witt vacuum | up quark in neutron 1 |
| d quark (neutron₁ 2) | `V` | Witt vacuum | down quark 1 in neutron 1 |
| d quark (neutron₁ 3) | `V` | Witt vacuum | down quark 2 in neutron 1 |
| u quark (neutron₂ 1) | `V` | Witt vacuum | up quark in neutron 2 |
| d quark (neutron₂ 2) | `V` | Witt vacuum | down quark 1 in neutron 2 |
| d quark (neutron₂ 3) | `V` | Witt vacuum | down quark 2 in neutron 2 |
| vacuum | `vacuum` | $e_7$ axis | Fock vacuum / sterile neutrino |

**Total: 9 quark nodes + 1 vacuum node = 10 nodes in the initial graph.**

### 5.2 Edge Types Required

| Edge | EdgeLabel | Physical meaning |
|---|---|---|
| Within-proton color | `SU3 i` ($i=0..7$) | Gluon exchange within proton (confining) |
| Within-neutron₁ color | `SU3 i` | Gluon exchange within neutron 1 |
| Within-neutron₂ color | `SU3 i` | Gluon exchange within neutron 2 |
| Proton ↔ neutron₁ | `SU3 i` (residual) | Nuclear strong force (color leakage) |
| Proton ↔ neutron₂ | `SU3 i` (residual) | Nuclear strong force |
| Neutron₁ ↔ neutron₂ | `SU3 i` (residual) | Nuclear strong force |
| Proton EM | `U1` | Coulomb repulsion |
| Vacuum coupling | `SU3 0` | Sterile neutrino (vacuum axis $e_7$) stabilization |

### 5.3 Beta Decay as Topology Change

Beta decay in the COG graph corresponds to:
1. One `d`-quark node in neutron₂ undergoes a `Tick` (non-associative evaluation forced).
2. The `SU2` edge carrying the $W^-$ operator fires: the node's CO state changes from
   $d$-quark state to $u$-quark state (ladder operator $a_j^\dagger$ applied).
3. Two new nodes are created: an electron (`S_minus` label) and an antineutrino (`vacuum` label).
4. New edges connect electron and antineutrino to the updated proton node.
5. Neutron₂ becomes a second proton (3 nodes: u, u, d).
6. The new graph motif is ${}^3\text{He}$ (2 protons + 1 neutron).

**Success criterion:** The beta decay topology change occurs spontaneously (i.e., the $W^-$
`SU2` edge becomes active) only after $\sim N_{\text{decay}}$ steps, where $N_{\text{decay}}$
scales with the tritium half-life in graph-step units.

---

## 6. Empirical Mass Targets for COG Tick-Frequency Calibration

COG's mass definition: $m(n) = \text{tick\_count}(n) / \text{graph\_depth}$.
To calibrate the tick unit, we use the electron mass as a reference.

| Particle | Mass (MeV/$c^2$) | Tick ratio (relative to $e^-$) |
|---|---|---|
| Electron $e^-$ | $0.511$ | $1$ (reference) |
| Muon $\mu^-$ | $105.658$ | $206.77$ |
| Tau $\tau^-$ | $1776.86$ | $3477.2$ |
| Up quark $u$ | $\sim 2.2$ | $4.3$ |
| Down quark $d$ | $\sim 4.7$ | $9.2$ |
| Proton $p$ | $938.272$ | $1836.2$ |
| Neutron $n$ | $939.565$ | $1838.7$ |
| $W$ boson | $80379$ | $157,000$ |

**Koide check for leptons:**
$\frac{m_e + m_\mu + m_\tau}{(\sqrt{m_e} + \sqrt{m_\mu} + \sqrt{m_\tau})^2} = \frac{2}{3}$
Valid to $\lesssim 0.01\%$ precision. COG must explain why the tick frequencies of `S_minus`
(electron), `S_minus` (muon), `S_minus` (tau) nodes satisfy this exact ratio.

---

## Cross-Reference Table

| COG simulation component | Best reference |
|---|---|
| 3-quark nucleon motif structure | Q1 (Jaffe), Q2 (HAL QCD) |
| Nuclear binding energy (triton) | N1 (Skibinski et al.), N2 (Epelbaum et al.) |
| Three-nucleon forces in triton | N1, Q3 (HAL QCD 3NF) |
| Beta decay mechanism | B1 (Stroberg), B2 (Project 8) |
| Ab initio benchmark for comparison | N3 (Navratil-Quaglioni), N4 (Hergert) |
| Nuclear lattice methods (closest to COG) | N5 (Lee), N6 (Lu et al.) |
| Quark-level EMC effect in nuclei | Q1 (Jaffe lectures) |

# v3 Comprehensive Symmetry + Kernel Literature Review (v2)

Date: 2026-03-02
Scope: S960/Q240 symmetry interpretation, chirality constraints, and emergent Lorentz strategy
Status: synthesis memo for RFC refinement

## 1) Executive synthesis

The strongest literature-backed direction is:
1. Keep `S960` geometric symmetry as a hypothesis engine,
2. Keep multiplication-respecting dynamics as the truth criterion,
3. Select kernels by mesoscale covariance metrics and coarse-graining behavior,
4. Treat chirality as an operational observable that must survive mirror controls and no-go-aware checks.

This supports the current v3 split:
1. `RFC-009` for symmetry interpretation and clock-aware motif priors,
2. `RFC-004` for hard selection gates.

## 2) Primary sources reviewed

## 2.1 Octonions / integral octonions / symmetry

1. Baez, *The Octonions* (Bull. AMS, 2002):
   - https://arxiv.org/abs/math/0105155
2. Conway-Smith review notes and E8/octonion integer discussion (Baez review page):
   - https://math.ucr.edu/home/baez/octonions/conway_smith/
3. Baez Week 193 (E8 roots and "rotate correctly" octonion closure explanation):
   - https://math.ucr.edu/home/baez/week193.html
4. Kim et al., *Multiplication of integral octonions* (2016):
   - https://doi.org/10.1142/S0219498816501449

## 2.2 Emergent Lorentz/covariance in discrete dynamics

1. Bialynicki-Birula, *Weyl, Dirac, and Maxwell equations on a lattice as unitary cellular automata* (1994):
   - https://doi.org/10.1103/PhysRevD.49.6920
2. Arrighi, Facchini, Forets, *Discrete Lorentz covariance for Quantum Walks and Quantum Cellular Automata* (2014):
   - https://arxiv.org/abs/1404.4499
3. Bisio et al., *Free quantum field theory from quantum cellular automata* (2016):
   - https://arxiv.org/abs/1601.04832
4. Trezzini, Bisio, Perinotti, *Renormalisation of Quantum Cellular Automata* (2024):
   - https://arxiv.org/abs/2407.12652
5. Duranthon & Di Molfetta, *Coarse-grained quantum cellular automata* (2021):
   - https://doi.org/10.1103/PhysRevA.103.032224

## 2.3 Chirality/no-go constraints on lattices

1. Nielsen & Ninomiya, *A no-go theorem for regularizing chiral fermions* (1981):
   - https://doi.org/10.1016/0370-2693(81)91026-1
2. Ginsparg & Wilson, *A remnant of chiral symmetry on the lattice* (1982):
   - https://doi.org/10.1103/PhysRevD.25.2649
3. Kaplan, *A Method for Simulating Chiral Fermions on the Lattice* (1992):
   - https://arxiv.org/abs/hep-lat/9206013
4. Neuberger, *Exactly massless quarks on the lattice* (1997):
   - https://arxiv.org/abs/hep-lat/9707022
5. Neuberger, *More about exactly massless quarks on the lattice* (1998):
   - https://arxiv.org/abs/hep-lat/9801031
6. Lüscher, *Exact chiral symmetry on the lattice and the Ginsparg-Wilson relation* (1998):
   - https://arxiv.org/abs/hep-lat/9802011

## 2.4 Coarse-graining and predictability in CA

1. Israeli & Goldenfeld, *Computational Irreducibility and the Predictability of Complex Physical Systems* (2004):
   - https://doi.org/10.1103/PhysRevLett.92.074105
2. Israeli & Goldenfeld, *Coarse-graining of cellular automata...* (2005):
   - https://arxiv.org/abs/nlin/0508033

## 2.5 Division-algebra particle-structure programs

1. Furey, *Standard model physics from an algebra?* (2016):
   - https://arxiv.org/abs/1611.09182
2. Furey, *Three generations, two unbroken gauge symmetries...* (2019):
   - https://arxiv.org/abs/1910.08395
3. Furey & Hughes, *Division algebraic symmetry breaking* (2022):
   - https://arxiv.org/abs/2210.10126
4. Manogue, Dray, Wilson, *Octions: An E8 description of the Standard Model* (2022):
   - https://arxiv.org/abs/2204.05310

## 3) Own analysis results (S960 clocks)

From `cog_v3/sources/v3_s960_elements_v1.csv` and subgroup decomposition:
1. Order classes: `1,2,3,4,6,12`.
2. Distinct cyclic subgroups: `426` total.
3. Non-identity cyclic subgroups: `425`.
4. Counts by order (distinct subgroups):
   - `2:3`, `3:28`, `4:254`, `6:84`, `12:56`.
5. Every order-12 subgroup contains exactly one subgroup for each divisor order (`1,2,3,4,6`).

Interpretation:
1. order-12 loops are structurally rich "clock bundles" (multiple embedded subclocks),
2. order-4 class is dominant and can act as sink/source,
3. motif search should explicitly monitor class-flow and avoid naive collapse.

## 4) Sharpened implications for v3

## 4.1 Symmetry interpretation

Use two-layer discipline:
1. point-set symmetry (rotation/reflection) for candidate generation,
2. multiplication symmetry for physical admissibility in-kernel.

This avoids over-claiming from visual invariance alone.

## 4.2 Chirality strategy

No-go literature implies chirality should be treated as a constrained observable, not a default assumption.

Operationally:
1. mirrored motif pair tests are mandatory,
2. parity-asymmetry must survive replay and placement controls,
3. no doubling-like artifact in same energy class for claimed chiral channels.

## 4.3 Lorentz-like strategy

QCA literature supports emergent covariance at long wavelengths, not exact tick-level invariance.

Operationally:
1. prioritize `cube26` lanes with anisotropy-decay under coarse-graining,
2. require multi-distance non-saturated fits and direction-consistent slopes,
3. reject kernels where anisotropy amplifies under block scale.

## 4.4 Clock-aware kernel tuning

Use period-flow as a first-class metric:
1. preserve nontrivial `12/6` lanes long enough to form motifs,
2. allow controlled leakage into lower-order anchors,
3. penalize immediate single-class collapse and full-class noise plateaus.

## 5) Open risks and unresolved assumptions

1. `Q240` as E8-root-shell is a standard and useful model, but implementation-specific orientation/convention still matters.
2. Point-set symmetries can overpredict dynamical equivalence in nonassociative settings.
3. Chirality emergence from motif alone remains unproven; kernel/event-order interactions can fake asymmetry.
4. Coarse-graining success metrics must be robust to boundary artifacts and finite-box effects.

## 6) Immediate recommendations

1. Add explicit citation block and confidence tiering to `RFC-009` and `RFC-004`.
2. Add a clock-flow diagnostic artifact to overnight runs.
3. Split scoring lanes (photon transport vs detector exclusivity vs chirality) to avoid objective conflict.
4. Promote kernels only when both Lorentz-like and clock-structure gates pass.

## 7) Confidence

1. High confidence: no-go/chiral-regularization constraints and QCA covariance principles.
2. Medium confidence: direct transfer of those principles to current multiplicative nonassociative kernel.
3. Exploratory: mapping clock bundles to particle motifs.

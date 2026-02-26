# Weak Mixing Angle Gap Review: From COG Baseline 1/2 to Physical 0.2312

Date: 2026-02-26
Scope: evaluate the current COG baseline `sin2ThetaWRaw = 1/2` and identify credible closure paths.

---

## 1. Executive Summary

Current COG result:
- `sin2ThetaWRaw = 1/2` is a formally locked baseline from coordinate-mask cardinalities.

Physical target:
- weak-mixing observables near the Z pole are about `0.231`.

Literature-backed conclusion:
1. Cardinality alone is not the physical observable for `sin^2(theta_W)`.
2. Running with scale is real and quantitatively important.
3. Any COG derivation must use generator/coupling normalization (trace- or norm-weighted), then optionally a scale bridge.
4. S4 symmetry is relevant to representation structure, but in mainstream usage S4 is mostly a flavor symmetry; it is not itself a standard direct predictor of electroweak gauge-coupling ratios.

---

## 2. What Is Firmly Established in Literature

## 2.1 Definition and scheme dependence

PDG electroweak review (2024) defines the weak mixing angle through electroweak couplings and renormalization-scheme dependent effective quantities, not through raw basis counts.

COG implication:
- `1/2` from mask cardinality is a structural checkpoint, not yet a physical `sin^2(theta_W)` observable.

## 2.2 Running is mandatory for cross-scale comparison

Erler and Ramsey-Musolf (2004/2007) and Erler et al. (2024) show controlled RG evolution of the weak mixing angle between Z-pole and low-energy regimes.

COG implication:
- if COG computes a high-scale boundary value, comparison at `M_Z` requires explicit running assumptions.

## 2.3 Canonical GUT normalization context

Canonical hypercharge normalization in simple-group embeddings (SU(5)/SO(10)/E6) is constrained by generator normalization (trace matching), not dimension counting.
Recent GUT-running literature (2019 EPJC) summarizes this normalization structure.

COG implication:
- if COG keeps a non-canonical effective normalization, that must be explicit and justified by the kernel representation map.

---

## 3. What the Current COG Baseline Means

`sin2ThetaWRaw = 2/4 = 1/2` currently means:
1. the locked projector definitions are coherent and reproducible;
2. electroweak sector bookkeeping is now guarded against retrofitting;
3. the gap to `~0.231` is now a real modeling target, not a moving denominator artifact.

This is useful progress, not failure.

---

## 4. Competing Explanations of the 1/2 -> 0.231 Gap

## H1: UV boundary plus running

Claim:
- COG baseline is a high-scale value that runs down to `~0.231` at Z-pole.

Evidence status:
- plausible in principle (running is real),
- but `1/2` is significantly above common canonical high-scale benchmarks like `3/8` in many unified embeddings.
- therefore this branch needs a concrete COG scale map and beta-function proxy before promotion.

## H2: Wrong metric (cardinality vs weighted projector)

Claim:
- physical observable should be a weighted ratio (trace/norm/coupling weighted), not cardinality.

Evidence status:
- strongly supported by standard electroweak formalism.
- this is the most direct, near-term branch for COG because it can be tested without adding full RG machinery first.

## H3: Electroweak sector basis too small

Claim:
- EW denominator should be larger than current 4-coordinate mask.

Evidence status:
- possible, but high numerology risk if the sector definition changes after seeing target mismatch.
- any expansion must be fixed by predeclared algebraic criteria and then frozen.

---

## 5. S4-Specific Assessment

S4 appears in two different roles:
1. In COG: vacuum-stabilizer action.
2. In mainstream model literature: mostly flavor-model symmetry (fermion mass/mixing textures).

Direct literature support for "S4 trace ratio directly predicts weak mixing angle" is weak.

COG implication:
- S4-weighted projector ratios are valid as a COG-internal hypothesis, but must be labeled as such and tested as new model content.

---

## 6. Recommended Closure Order

1. Keep `1/2` as locked baseline.
2. Add weighted-observable definition (`Tr(W_U1 P_U1)/Tr(W_EW P_EW)` or equivalent).
3. Prove basis/symmetry invariance in Lean for the chosen weighting map.
4. Run ablations across admissible weights/sector definitions declared before target comparison.
5. Only then evaluate whether an additional running bridge is needed.

---

## 7. References

1. PDG 2024, Electroweak Model and Constraints on New Physics:
   https://pdg.lbl.gov/2024/reviews/rpp2024-rev-standard-model.pdf
2. Georgi and Glashow (1974), Unity of All Elementary-Particle Forces:
   https://doi.org/10.1103/PhysRevLett.32.438
3. Erler and Ramsey-Musolf (2004/2007), Weak mixing angle at low energies:
   https://arxiv.org/abs/hep-ph/0409169
4. Erler, Ferro-Hernandez, Kuberski (2024), Theory Driven Evolution of the Weak Mixing Angle:
   https://arxiv.org/abs/2406.16691
5. Atzori Corona et al. (2024), Refined determination of the weak mixing angle at low energy:
   https://arxiv.org/abs/2405.09416
6. CMS (2024), Measurement of effective leptonic weak mixing angle at 13 TeV:
   https://arxiv.org/abs/2405.11484
7. Kim (2004), Trinification with `sin^2(theta_W)^0 = 3/8`:
   https://arxiv.org/abs/hep-ph/0403196
8. Schwichtenberg (2019), Gauge coupling unification without supersymmetry (hypercharge normalization discussion):
   https://doi.org/10.1140/epjc/s10052-019-6878-1
9. Bazzocchi, Merlo, Morisi (2009), S4-based fermion masses and mixings:
   https://arxiv.org/abs/0901.2086
10. Ding et al. (2024), Modular S4 lepton flavor models:
    https://arxiv.org/abs/2408.15988

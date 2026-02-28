# GR Limit Emergence Assessment (COG)

Date: 2026-02-28  
Scope: Evaluate whether and how General Relativity (GR) emerges as a limit of current COG architecture.

---

## 1. Executive Verdict

Short answer:
1. COG has credible structural ingredients for a GR-limit program.
2. COG does **not** yet demonstrate GR emergence as a closed result.
3. Current evidence supports "causal-graph kinematics + exploratory gravity mechanism," not "Einstein dynamics recovered."

Why:
1. Lorentz-recovery RFC is still a stub (`rfc/RFC-060_Lorentz_Symmetry_Recovery_from_Causal_DAG.md`).
2. Gravity RFC is exploratory and explicitly blocked by unresolved synchronization/metric contracts (`rfc/RFC-030_Gravity_as_Emergent_Graph_Density.md`).
3. Cosmology lane recently clarified that fixed-topology kernels cannot claim expansion from update alone (`rfc/RFC-087_Cosmological_Initial_State_Evolution_and_Seed_Classes.md`).

---

## 2. What Is Actually in Place

## 2.1 Causal time and ordering (strong)

Available:
1. Objective time as graph depth contract (`rfc/RFC-067_Objective_Time_as_Graph_Depth.md`).
2. Deterministic update kernels and replayability.

Interpretation:
1. COG has a clear causal substrate and a consistent notion of temporal ordering.
2. This is necessary but not sufficient for GR emergence.

## 2.2 Lightcone and finite propagation speed (moderate)

Available:
1. DAG/lightcone semantics RFC chain.
2. Speed-limit style tests (including toy checks in `calc/test_rel_emergence.py`).

Limit:
1. Existing "relativity emergence" test is largely scaffold-level and uses analytic formulas not directly derived from production COG microdynamics.
2. It does not yet establish Lorentz symmetry of the actual generated large-scale graph ensemble.

## 2.3 Gravity mechanism hypothesis (exploratory)

Available:
1. Emergent density/slowdown framing (`rfc/RFC-030_Gravity_as_Emergent_Graph_Density.md`).
2. No-singularity structural argument (`rfc/RFC-066_No_Singularities_Cosmological_Reframing.md`).

Limit:
1. Mechanism relies on assumptions not fully locked in canonical kernel semantics.
2. No claim-grade lensing battery against a pre-registered observable contract yet.

---

## 3. Critical Gap Analysis vs GR

To claim "GR emerges as a limit," COG must close all four layers:

1. **Kinematic Lorentz layer**
   - Need isotropic, frame-independent effective causal propagation in the large-scale limit.
   - Current status: open/stub (`RFC-060`).

2. **Metric-reconstruction layer**
   - Need map from graph observables to effective metric `g_mu_nu` (at least up to conformal factor, then volume/scale completion).
   - Current status: conceptual only.

3. **Dynamical curvature layer**
   - Need effective field equations approximating Einstein equations in weak-field/macroscopic regime, or a clearly specified alternative with equal/better empirical success.
   - Current status: absent.

4. **Phenomenology layer**
   - Need quantitative matches (Newtonian limit, lensing, redshift/time dilation, perihelion-scale effects, gravitational-wave-like propagation constraints, cosmological expansion profile).
   - Current status: exploratory/blocked by contracts and calibration.

---

## 4. Claim Hygiene Issue (Important)

`claims/causal_invariance.yml` currently marks `REL-001` as `proved`, while:
1. its `derivation_status` is `bridge_assumed`,
2. theorem set in `CausalGraphTheory/CausalInvariance.lean` proves basic tick/depth properties, not full Lorentz-recovery of the generated COG universe.

Recommendation:
1. Re-scope language from "special relativity emergence proved" to "causal invariance primitives proved; Lorentz recovery remains open."
2. Keep REL lane active until metric/dimension/isotropy gates are passed.

---

## 5. Minimum Viable GR-Limit Program (Concrete)

## Stage A: Kinematics (must close first)

A1. Effective dimension and cone scaling
1. Compute `|C+(v,n)|` across large ensembles.
2. Fit `|C+| ~ n^d_eff`.
3. Require stable `d_eff` in target band under seed/profile controls.

A2. Isotropy battery
1. Define directional anisotropy metrics on large cones.
2. Require anisotropy decay with scale.

A3. Operational Lorentz checks from actual COG histories
1. Time dilation and interval-like invariants measured from generated histories, not analytic plug-ins.

Exit gate A:
1. reproducible large-scale kinematic isotropy + Lorentz-like operational invariants.

## Stage B: Gravity as effective geometry

B1. Lock slowdown/curvature observable contract
1. Freeze exact field definition (e.g., `S(v)` or approved successor).
2. Freeze geodesic extraction method.

B2. Weak-field lensing test
1. Pre-register impact-parameter sweeps.
2. Measure deterministic deflection trends vs source intensity.

B3. Newtonian limit test
1. Derive effective acceleration law in weak, static regime.
2. Test whether leading behavior is inverse-square (or clearly quantify deviation).

Exit gate B:
1. quantitative weak-field predictions with robust replay and controls.

## Stage C: Cosmology and strong gravity

C1. Dynamic-topology closure
1. Need explicit spawn/topology-growth policy lock (fixed-topology kernels cannot establish expansion claims).

C2. FRW-like expansion observables
1. Hubble-like growth diagnostics from graph growth.
2. Isotropy/homogeneity checks over expanding ensembles.

C3. Compact-region / horizon behavior
1. Define horizon criteria in graph terms.
2. Run no-singularity and boundary-radiation analog tests under locked policies.

Exit gate C:
1. consistent cosmology narrative grounded in dynamic-topology artifacts.

---

## 6. Near-Term Priorities (2-4 weeks)

1. Demote over-strong REL wording or split REL into:
   - `REL-KIN-001` (proved primitives),
   - `REL-LIMIT-001` (actual emergent Lorentz limit, open).
2. Implement `calc/causal_cone.py` + tests as specified by `RFC-060`.
3. Replace or supplement `calc/test_rel_emergence.py` with measurements derived from real COG run artifacts.
4. Lock gravity observable contract before additional gravity claims.
5. Keep cosmology claims lane-labeled (`fixed_topology` vs `dynamic_topology`) per RFC-087.

---

## 7. Bottom Line

COG can plausibly target GR as an emergent macroscopic limit, but the project is currently in:
1. **structural groundwork** + **exploratory mechanism** phase,
not in
2. **closed emergence proof** phase.

The highest-leverage path is to close kinematic Lorentz/isotropy gates on real COG histories before attempting Einstein-equation-level closure claims.


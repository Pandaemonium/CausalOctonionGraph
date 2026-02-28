# Typical Starting Conditions and Cold-Start Controls (Lit Review)

Date: 2026-02-27  
Scope: determine whether COG should treat "cold start" as canonical, optional, or controlled baseline for constant-derivation simulations.

---

## 1. Local COG Status

Current internal policy is already strong on determinism:
1. `rfc/RFC-028_Canonical_Update_Rule_Closure.md` locks full-lightcone initialization for canonical runs.
2. `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md` locks "initial state + update rule + observable spec" as mandatory.
3. `rfc/RFC-072_Tritium_Typical_Microstate_Approximation_Strategies.md` treats "typical" initial states as an epistemic ensemble problem, not ontology.

Gap:
1. "Cold start vs preconditioned start" is not yet a single explicit cross-claim policy with required controls and reporting gates.

---

## 2. External Evidence

## 2.1 Thermalization/warm-up is standard in lattice gauge workflows

Lattice studies explicitly frame initialization and thermalization as first-class concerns:
1. Endres et al. describe multiscale thermalization for lattice gauge theory and motivate faster equilibration from better starts rather than ad hoc post-fit correction.
2. This supports a COG rule that preconditioning is a declared algorithmic stage, not hidden tuning.

Source:
1. Endres et al., *Multiscale Monte Carlo equilibration: Pure Yang-Mills theory*, arXiv:1510.04675, https://arxiv.org/abs/1510.04675

## 2.2 Initialization sensitivity should be audited via multiple starts

Convergence diagnostics literature recommends independent sequences and dispersed starts to detect initialization bias:
1. Gelman-Rubin's core recommendation is multiple independent starts, not single-chain trust.
2. For COG deterministic campaigns, this maps naturally to predeclared deterministic "start profiles" (cold/warm/structured), compared on a fixed observable contract.

Sources:
1. Gelman & Rubin (1992), *Inference from Iterative Simulation Using Multiple Sequences*, DOI:10.1214/ss/1177011136, https://doi.org/10.1214/ss/1177011136
2. Abstract mirror (CORE) with key recommendation text, https://core.ac.uk/display/28932160

## 2.3 Hot/cold starts and hysteresis are explicit analysis dimensions in lattice studies

Recent lattice analyses still report hot/cold starts and hysteresis behavior as part of phase-structure interpretation.
1. This reinforces that start-policy sensitivity is not optional metadata; it can change inferred macroscopic conclusions.

Source:
1. *Lattice Monte Carlo in low dimensions & its application to hadron resonances* (arXiv preprint listing), https://arxiv.org/abs/2412.20287

---

## 3. Synthesis for COG

From local and external evidence:
1. Cold start alone is not a sufficient canonical protocol for extraction claims.
2. Preconditioning/warm-up must be explicit, deterministic, and parameter-locked in artifact metadata.
3. Cold-start runs remain valuable as controls and falsification checks.
4. Typical-start claims should be ensemble-level and policy-locked (generator + constraints + selection metric), consistent with RFC-072.

---

## 4. Recommended Policy Direction

1. Canonical production profile: full lightcone + declared preconditioning ticks.
2. Mandatory control profile: matching cold-start run on same case grid.
3. Required reporting: delta between warm and cold trajectories over fixed post-overlap plateau.
4. Promotion gate: no claim promotion when warm/cold divergence exceeds declared tolerance.

---

## 5. References

1. Endres et al. (2015), arXiv:1510.04675, https://arxiv.org/abs/1510.04675
2. Gelman & Rubin (1992), DOI:10.1214/ss/1177011136, https://doi.org/10.1214/ss/1177011136
3. CORE abstract mirror for Gelman-Rubin summary, https://core.ac.uk/display/28932160
4. Lattice hot/cold start context (arXiv listing), https://arxiv.org/abs/2412.20287
5. Existing internal contract anchors:
   - `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
   - `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
   - `rfc/RFC-072_Tritium_Typical_Microstate_Approximation_Strategies.md`

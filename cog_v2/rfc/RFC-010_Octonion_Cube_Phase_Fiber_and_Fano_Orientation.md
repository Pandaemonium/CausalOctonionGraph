# RFC-010: Octonion Cube, Phase Fibers, and Fano Orientation

Status: Active  
Date: 2026-02-28  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-008_Layered_Causality_and_Defect_Falsification_Contract.md`
- `cog_v2/rfc/RFC-009_F2^3_Index_Geometry_and_Unique_Causal_Length.md`

## 1. Purpose

Formalize the canonical v2 geometric interpretation:

1. channel indices are the 8 vertices of an octonion-index cube (`F2^3`),
2. each channel carries a local phase fiber with values in a 4-cycle plus null occupancy,
3. coherent multiplication requires oriented Fano triads on the 7 nonzero channels.

This RFC defines structure-first geometry only. It does not claim continuum EFT closure.

## 2. Canonical Objects

### 2.1 Index base (octonion cube indexing)

1. channel set is `e000..e111`,
2. index labels are 3-bit vectors in `F2^3`,
3. index routing law is XOR (`k = i xor j`) for channel destination.

Interpretation:

1. this is the finite address geometry for interaction transport,
2. it is not yet the full multiplication law.

### 2.2 Local phase fiber

At each channel index `x`, coefficient values are in:

1. null occupancy: `0`,
2. active phase cycle: `{+1, +i, -1, -i}`.

Fiber interpretation:

1. null means channel not carrying active local amplitude,
2. non-null states form a `Z4` phase orbit,
3. projector dynamics move coefficients among these values deterministically.

### 2.3 Total state geometry

A node state is a section:

1. `psi : F2^3 -> {0, +/-1, +/-i}`.

So each event is a finite fiber assignment over 8 cube-indexed channels.

## 3. Why Fano Orientation Is Required

XOR routing alone does not determine multiplication sign or handedness.
For any nonzero pair `(i,j)`:

1. XOR fixes destination channel `k`,
2. sign and order behavior remain ambiguous without orientation data.

To get octonionic interaction behavior, we require:

1. a partition of the 7 nonzero channels into oriented triads (Fano lines),
2. directed cyclic rule on each triad:
   - `a * b = +c`,
   - reversed order gives minus.

Therefore:

1. cube indexing provides destination combinatorics,
2. Fano orientation provides chirality/sign structure.

This is the minimal decomposition compatible with canonical v2 multiplication semantics.

## 4. Structural Implications

### 4.1 Algebraic implications

1. index transport is finite and exact (`F2^3`, XOR-closed),
2. sign transport is orientation-sensitive (non-commutative order effect),
3. full product structure is not reducible to pure cube adjacency.

### 4.2 Dynamical implications

1. periodic motifs are finite orbits in a layered causal update graph,
2. stable triad-coherent motifs preferentially circulate on oriented Fano cycles,
3. perturbations that break triad coherence increase off-cycle support and can increase null/`e000` coupling lanes depending on kernel context.

### 4.3 Symmetry implications

1. kinematic channel-label symmetry: finite `F2^3` relabeling structure,
2. orientation reversal gives CP-like sign inversion lane,
3. effective symmetry in runtime is reduced by projector and deterministic event-order policy.

## 5. Falsification and Diagnostics

This geometry is falsified in a run if any of the following occur:

1. channel transport violates XOR destination law,
2. observed multiplication signs cannot be represented by any oriented Fano triad assignment (up to global orientation reversal),
3. coefficients leave allowed fiber set `{0, +/-1, +/-i}` in strict mode.

Recommended diagnostics:

1. XOR destination conformance table,
2. sign-consistency reconstruction against oriented triads,
3. phase-fiber closure test after each projector update.

## 6. Practical Modeling Guidance

When building simulations and bridges:

1. treat `F2^3` as the channel index manifold,
2. treat phase as a local `Z4` fiber plus null occupancy,
3. enforce oriented Fano signs as mandatory interaction structure,
4. avoid deriving physical conclusions from XOR-only models lacking orientation checks.

## 7. Relation to Other RFCs

1. RFC-008 fixes strict layered causal metric (`unique causal chain length`),
2. RFC-009 fixes `F2^3` index interpretation under canonical assumptions,
3. this RFC adds the local phase-fiber and oriented-triad synthesis.

Together they define the current canonical geometric language for v2:

1. layered time geometry,
2. cube-indexed channel geometry,
3. phase fiber dynamics,
4. oriented Fano sign structure.

## 8. Non-Goals

This RFC does not:

1. prove uniqueness of one specific physical interpretation of phase,
2. claim complete derivation of all Standard Model constants,
3. replace claim-specific bridge contracts.

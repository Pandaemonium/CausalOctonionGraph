# RFC-009: F2^3 Index Geometry and Unique Causal Length

Status: Active  
Date: 2026-02-28  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-008_Layered_Causality_and_Defect_Falsification_Contract.md`

## 1. Purpose

This RFC does four things:

1. states the canonical claim that any reachable pair `(A,B)` has exactly one causal edge count,
2. defines explicit falsification conditions for that claim,
3. gives a proof sketch that, under v2 canonical state/update axioms, the claim implies an `F2^3` index geometry for channel transport,
4. provides a clear physical exposition of what `F2^3` means for COG v2.

## 2. Canonical Claim

For canonical v2 runs (`causality_mode = layered_strict_v1`):

1. every primitive edge increments depth by exactly one,
2. for every reachable ordered pair `(A,B)`, all directed paths from `A` to `B` have the same length,
3. equivalently, causal edge count is unique and equals `depth(B) - depth(A)`.

This claim is normative for claim-grade artifacts.

## 3. Falsification Conditions

Let:

1. `Lmin(A,B)` be shortest directed path length,
2. `Lmax(A,B)` be longest directed path length,
3. `Delta(A,B) = Lmax(A,B) - Lmin(A,B)`.

The claim is falsified for a run if any of the following hold:

1. graph is not acyclic,
2. at least one edge violates `depth(dst) = depth(src) + 1`,
3. there exists a reachable pair with `Delta(A,B) > 0`.

Operational validator:

1. `cog_v2/scripts/validate_layered_causality_v1.py`
2. canonical pass requires:
   - `is_dag = true`,
   - `layer_violation_count = 0`,
   - `max_delta = 0`.

Reference theorem lane:

1. `cog_v2/lean/CausalGraphV2/LayeredCausality.lean`
2. theorem shape:
   - layered-edge axiom implies unique path length between fixed endpoints.

## 4. Assumptions Needed for F2^3 Implication

The unique-length claim alone does **not** force `F2^3`.
The implication uses the full canonical v2 bundle:

1. channel set has exactly 8 labeled channels (`e000..e111`),
2. channel transport is closed under binary XOR indexing,
3. coefficients are unity alphabet values with deterministic projection,
4. edge-time is one-step layered (Section 2).

Under these assumptions, index transport algebra is a finite 8-element, XOR-closed, characteristic-2 vector structure, hence isomorphic to `(Z2)^3 = F2^3`.

## 5. Proof Sketch (Structure-First)

### 5.1 Unique causal edge count

From strict layering:

1. each edge contributes exactly `+1` depth,
2. any path from `A` to `B` must accumulate the same total depth change,
3. therefore all `A -> B` paths have same length.

This is formalized in Lean via:

1. `path_depth_eq`,
2. `path_length_unique`,
3. `no_path_length_spread`.

### 5.2 Why the index algebra is F2^3

Given 8 channels and XOR-closed indexing:

1. channel indices form an 8-element set with binary composition,
2. XOR implies each element is self-inverse (`x xor x = 0`),
3. composition is commutative and associative at index level,
4. this exactly matches 3-bit vector addition mod 2.

Therefore channel indices are naturally represented as:

1. `000, 001, 010, 011, 100, 101, 110, 111`.

This is `F2^3`.

## 6. Lucid Exposition: What F2^3 Says About the Model

`F2^3` is the combinatoric backbone of v2 channel routing:

1. each channel label is a 3-bit coordinate,
2. combining channels at index level is XOR (`k = i xor j`),
3. index kinematics are finite, exact, and replay-deterministic.

It does **not** mean the full physics is only a cube:

1. `F2^3` governs channel addressing,
2. oriented Fano sign/orientation governs nontrivial multiplication structure,
3. layered DAG governs causal-time geometry.

So the full model is:

1. layered causal geometry in time,
2. `F2^3` index geometry for channels,
3. Fano-oriented algebra for interaction signs and non-associative structure.

## 7. Expected Artifacts

For any claim package adopting this RFC:

1. layered-causality validation JSON report,
2. canonical pass verdict (`max_delta = 0`),
3. explicit declaration of `F2^3` index mapping used by runtime and docs.

Recommended citation artifacts:

1. `cog_v2/sources/layered_causality_validation_demo_v1.json`,
2. `cog_v2/lean/CausalGraphV2/LayeredCausality.lean`.

## 8. Non-Goals

This RFC does not:

1. prove continuum EFT closure for any constant,
2. claim defect lanes are physically realized,
3. replace Fano orientation/sign structure with pure XOR.


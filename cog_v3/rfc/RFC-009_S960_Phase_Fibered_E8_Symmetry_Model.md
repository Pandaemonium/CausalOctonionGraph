# RFC-009: S960 Phase-Fibered E8 Symmetry Model

Status: Draft
Date: 2026-03-02
Owner: COG Core
Depends on:
- `cog_v3/sources/v3_s960_elements_v1.csv`
- `cog_v3/sources/v3_octavian240_elements_v1.csv`
- `cog_v3/rfc/CONVENTION_IDS.md`
- `cog_v3/rfc/RFC-004_Physics_Grounded_Kernel_Selection_Criteria.md`
- `cog_v3/sources/v3_s960_lit_action_backlog_v1.md`

## 1. Purpose

Define a precise geometric/symmetry model for `S960` when rotations and reflections are both allowed.

This RFC separates:
1. point-set symmetry of the alphabet,
2. algebra/multiplication symmetry of the update law,
so we do not mix geometric intuition with kernel claims.

Plain-English:
This RFC gives a clean mental model of the 960 states as a geometric object you can rotate or mirror, while also being clear that the kernel uses multiplication rules that are stricter than "looks symmetric." In short: geometry helps us think, multiplication decides what is physically allowed in the model.

## Reader's Guide (High-School Version)

If you only read one section, read this one.

## 1) The 30-second idea

We have a set of 960 allowed states (`S960`).

You can think of each state as:
1. a 4-step clock value (`1, i, -1, -i`), and
2. one of 240 special octavian states.

So:
1. `4 x 240 = 960`,
2. which is why the alphabet has exactly 960 states.

## 2) The picture in your head

Start with 240 points (the octavian shell).
Now make 4 copies of that same 240-point shape, one for each phase of the clock.

That gives 4 layers:
1. layer `1`,
2. layer `i`,
3. layer `-1`,
4. layer `-i`.

Total points:
1. `240 + 240 + 240 + 240 = 960`.

This is what "phase-fibered" means here: same base shape, copied across phase layers.

## 3) Why we talk about symmetry

A symmetry means "you move/rename things, but the overall pattern still matches itself."

In this RFC we care about two different symmetry questions:
1. **Shape symmetry**: does the point cloud still look the same after rotate/flip/mirror?
2. **Rule symmetry**: do the multiplication rules still behave the same after that transform?

Important:
1. shape symmetry and rule symmetry are not always the same.
2. A transform can preserve the picture but break the multiplication behavior.

## 4) Why that difference matters for physics

If a transform preserves only shape:
1. it is good for intuition and visualization,
2. but not enough to claim physical equivalence in the kernel.

If a transform preserves multiplication behavior too:
1. then it is much stronger evidence that the dynamics treat those cases as equivalent.

So our workflow is:
1. use geometry to propose tests,
2. use kernel dynamics to accept/reject those proposals.

## 5) What the cycles mean (simple version)

When you multiply by the same state repeatedly, eventually you loop back.

That loop length is the element's order (cycle length).
For `S960`, observed cycle lengths are:
1. `1, 2, 3, 4, 6, 12`.

This does **not** automatically mean "spinning 3D object."
It means "internal discrete clock/rotor in state space."

## 6) How this helps us find particles

Instead of searching blindly, we split candidates by structure:
1. phase layer,
2. octavian family class,
3. conjugation tier,
4. cycle length.

Then we run symmetry panels:
1. rotated versions,
2. mirrored versions,
3. multiplication-consistent comparison runs.

That lets us separate:
1. motifs that are only visually similar,
2. motifs that are dynamically equivalent under the kernel.

## 7) One-line friend explanation

"We built a 960-state system by taking 240 special states and copying them across a 4-step phase clock. We test both rotate/flip symmetries and multiplication-rule symmetries, because looking the same is not always the same as evolving the same."

## 8) Flow map

`Q240 (240 states)` + `C4 (4 phases)` -> `S960` -> propose geometric symmetries -> test multiplication dynamics -> keep only physically consistent symmetries for kernel decisions.

## 2. Definitions

1. `Q240`: the 240 octavian unit states used in v3.
2. `C4`: discrete phase set `{1, i, -1, -i}`.
3. `S960 = C4 x Q240` (shared-phase lane).
4. `point-set symmetry`: a bijection of states preserving pairwise geometric structure in the chosen embedding.
5. `algebra symmetry`: a bijection preserving multiplication structure (up to specified associator conventions).

Plain-English:
`S960` is built from two ingredients:
1. a 4-step phase clock (`C4`), and
2. a 240-state octavian set (`Q240`).
When we say "symmetry," we can mean either:
1. shape symmetry (the points still make the same pattern), or
2. rule symmetry (multiplication still works the same way).
Those are related but not identical.

## 3. Geometric Model

Plain-English:
We now describe the technical picture first, then explain what it means visually.

## 3.1 Q240 layer

Working model:
1. `Q240` is treated as the E8-root-shell realization (240 points in 8D).
2. Geometric symmetry of that shell is represented by E8 Weyl-type actions (reflection-generated finite symmetry group).

Plain-English:
Think of `Q240` as a very symmetric 8D point cloud. Mirror operations are not extra hacks here; they are built into the natural symmetry family of that cloud.

## 3.2 S960 lift

Constructive embedding:
1. Embed `C4` as a square on `S1` in `R2`.
2. Embed `Q240` in `R8`.
3. Form product points in `R10`:
   - `(phase_point, q240_point)`.

Result:
1. `S960` is a 4-layer phase fiber over the 240-point octavian shell.

Plain-English:
Take the 240-point cloud and copy it four times, once for each phase (`1, i, -1, -i`). Stack those copies as "phase layers." That is `S960`.

## 3.3 Optional identification

If states are interpreted only through product value `z*u`, then
1. `(z, u)` and `(-z, -u)` can represent the same product value,
2. giving a `Z2` identification.

Implementation note:
1. current v3 indexing keeps phase and octavian coordinates explicit,
2. so the operational alphabet is the full direct product, not quotient-collapsed.

Plain-English:
Mathematically, there is a common simplification where `(phase, octonion)` and `(-phase, -octonion)` are treated as equivalent. We are not doing that collapse in the current implementation. We keep all 960 states explicit.

## 4. Symmetry Statement (Point-Set)

Minimum practical symmetry claim:
1. phase layer admits square symmetries (`D4`: rotations + reflections),
2. octavian shell admits E8-root-set symmetries,
3. combined point-set symmetry is at least product-like (`D4 x E8-shell-symmetry`) in the lifted `R10` view.

Interpretation:
1. yes, mirror operations are naturally included,
2. not only pure rotations.

Plain-English:
If you allow flips and reflections in addition to rotations, the `S960` picture still has a coherent symmetry structure. So your "mirror too, not just spin" intuition is aligned with this model.

## 5. Critical Caveat: Geometry vs Multiplication

This RFC does not claim that all point-set symmetries are kernel symmetries.

Reason:
1. octonion multiplication is nonassociative,
2. v3 uses fixed convention/orientation and fixed update ordering,
3. therefore multiplication-preserving automorphisms are a stricter subset than geometric symmetries.

Operational rule:
1. treat geometric symmetry as a hypothesis generator,
2. treat multiplication symmetry as a testable constraint.

Plain-English:
This is the most important caution. A transform can look perfectly symmetric as a shape operation and still fail as a legal multiplication-preserving transform. So geometric symmetry suggests experiments; it does not prove kernel legality.

## 6. Cyclic-Mode Context in This Model

Observed in current exports:
1. `S960` element orders: `1, 2, 3, 4, 6, 12`.
2. Distinct cyclic subgroups in `S960`: `426`.
3. Non-identity cyclic subgroups: `425`.
4. Distinct subgroup counts by order:
   - order-2: `3`,
   - order-3: `28`,
   - order-4: `254`,
   - order-6: `84`,
   - order-12: `56`.
5. Every order-12 subgroup contains exactly one subgroup of each divisor order (`1,2,3,4,6`).

Meaning in this RFC:
1. these are internal discrete rotor modes in state space,
2. they are not automatically rigid 3D spatial spins.

Plain-English:
Cycle lengths tell you how states loop under repeated multiplication. You can think of these as internal clocks or rotors. That does not mean each one is literally a spinning 3D rigid body.

Plain-English (extra):
The order-12 loops are especially interesting because each one already contains smaller built-in subclocks (2, 3, 4, 6). So they are natural "clock bundles" for motif design.

## 7. Immediate Use for Search

Plain-English:
This section turns the symmetry model into practical search moves.

## 7.1 Stratified seeding

Use geometry-informed bins:
1. phase class (`C4` layer),
2. octavian family class (`A/B/C`),
3. conjugation-tier proxy (`1/29/46`),
4. order class (`1/2/3/4/6/12`).

Plain-English:
Do not search uniformly. Split the search by known structure classes so compute goes where nontrivial motifs are more likely.

## 7.2 Symmetry panels

For each motif candidate, run paired probes:
1. rotation panel (phase and spatial orientation permutations),
2. reflection panel (mirror transforms),
3. parity/multiplication panel (mirror plus multiplication replay).

Goal:
1. distinguish point-set invariance from true dynamical invariance.

Plain-English:
For every promising motif, test rotated and mirrored versions. If behavior survives only geometric relabeling, that is weaker. If it survives multiplication-consistent panels, that is stronger.

## 7.3 Promotion hint

Candidate motifs rank higher when:
1. stable under geometric transforms expected from this RFC,
2. while retaining distinct behavior where algebra symmetry is not expected.

Plain-English:
Best candidates are stable in the places they should be stable, and different in the places where the algebra predicts meaningful asymmetry.

## 8. Artifact Contract

Minimum required outputs for this RFC lane:
1. symmetry-transform manifest for each motif run,
2. per-transform survival/period/drift metrics,
3. reflection-vs-rotation comparison table,
4. explicit tag: `point_set_symmetric`, `algebra_symmetric`, or `mixed`.

Suggested files:
1. `cog_v3/sources/v3_s960_symmetry_panel_v1.json`
2. `cog_v3/sources/v3_s960_symmetry_panel_v1.md`

Plain-English:
We want this to be audit-ready. Every symmetry claim should come with a run manifest and a per-transform result table, not just narrative text.

## 9. Clock-Aware Motif Search Strategy

This section translates the cyclic-loop structure (`orders 1,2,3,4,6,12`) into immediate search policy.

## 9.1 Why clocks help motif discovery

1. stable motifs are more likely when local components repeatedly return to compatible cycle classes,
2. unstable motifs often show rapid period-class collapse (single sink class) or explosive class diffusion.

Plain-English:
If nearby voxels behave like clocks that can stay in rhythm, motifs last longer. If clocks instantly fall out of rhythm, the motif decays.

## 9.2 Seeding priors (operational)

Use stratified seed pools:
1. high-priority dynamic pool: period-12 and period-6,
2. medium pool: period-4 (for carrier-like scaffolds),
3. anchor/control pool: period-1/2/3 used sparsely.

Recommended motif pattern:
1. anchor core from low-order classes,
2. transport shell from higher-order classes.

Plain-English:
Start with rich clocks for motion, and a small number of simple clocks for stabilization.

## 9.3 Clock-signature logging

For each run, log a per-tick histogram:
1. `%order2`, `%order3`, `%order4`, `%order6`, `%order12`,
2. optionally split by core/shell spatial region.

Define:
1. `clock_signature(t)` = normalized order histogram at tick `t`,
2. `clock_signature_drift` = distance between signatures across windows.

Interpretation:
1. low drift after transient -> candidate stable motif regime,
2. monotone collapse to one class or high-noise oscillation -> weak candidate.

## 9.4 Promotion hints from clocks

Promote candidates when all hold:
1. repeatable period estimate or recurrence window,
2. bounded `clock_signature_drift` in post-transient windows,
3. survival under symmetry panels from Section 7.2.

Demote candidates when either holds:
1. fast collapse into trivial period mix with no coherent transport,
2. fast diffusion across all classes with no recurring structure.

Plain-English:
A good motif has a "fingerprint" of clock types that settles and repeats.

## 10. Clock-Aware Kernel Design Implications

Use clock flow as a kernel quality signal, not just visual behavior.

## 10.1 Period-flow matrix

For a given kernel policy, estimate transition tendencies between order classes:
1. `T[a,b] = tendency for local interactions from class a to produce class b`.

Desirable:
1. nontrivial retention lanes for period-12/6 classes,
2. controlled leakage into lower-order anchor classes,
3. avoid hard collapse where one class dominates almost all outcomes.

## 10.2 Kernel tuning objective

Add clock objective terms:
1. maximize post-transient signature stability for top candidates,
2. penalize premature single-class collapse,
3. penalize unstructured class diffusion.

Plain-English:
A better kernel keeps useful clocks alive long enough to build motifs.

## 10.3 Fail-fast with clock criteria

Early terminate runs when:
1. class entropy saturates at high noise with no recurrence trend, or
2. class occupancy collapses too quickly to trivial pattern without transport.

Retain runs when:
1. early clock signature moves toward a stable band and recurrence evidence appears.

## 11. Non-Claims

This RFC does not claim:
1. full equivalence between `S960` and a single classical polytope symmetry group,
2. that kernel dynamics already realize all geometric symmetries,
3. that any specific particle has been identified.

It only defines the high-value symmetry frame for analysis and testing.

Plain-English:
This RFC is a map, not a victory claim. It sets the coordinate system for better experiments.

## 12. Decision

Adopt this model as the default geometric interpretation layer for `S960`:
1. phase-fibered octavian shell in `R10`,
2. with both rotation and reflection operations in analysis,
3. and strict separation of geometric symmetry from multiplication symmetry in claims.

Plain-English:
From now on, use this two-layer view by default:
1. geometry tells us what transformations are natural to test,
2. multiplication tests decide what is physically admissible in-model.

## 13. Literature Anchors and Confidence Tiers

Primary anchors used for this RFC:
1. Baez, *The Octonions* (2002): `https://arxiv.org/abs/math/0105155`
2. Baez review notes (Conway-Smith / E8-octonion context): `https://math.ucr.edu/home/baez/octonions/conway_smith/`
3. Baez Week 193 (E8 roots and octonion closure orientation): `https://math.ucr.edu/home/baez/week193.html`
4. Kim et al., *Multiplication of integral octonions* (2016): `https://doi.org/10.1142/S0219498816501449`
5. Furey et al. line for division-algebra particle-structure context:
   - `https://arxiv.org/abs/1611.09182`
   - `https://arxiv.org/abs/1910.08395`
   - `https://arxiv.org/abs/2210.10126`

Confidence tiers:
1. High confidence:
   - two-layer distinction (point-set vs multiplication symmetry),
   - relevance of reflections in the geometric symmetry model.
2. Medium confidence:
   - specific practical embedding choices used for analysis panels.
3. Exploratory:
   - direct mapping from clock bundles to specific particle motifs.

## 14. Lit-Review Integration: What Is Usable Right Now

This section integrates high-signal points from:
1. `sources/s960_particle_morphology_search.md`,
2. `sources/s960_ca_lorentz_lit_review.md`,
3. `sources/s960_chirality_emergence_lit_review.md`,
4. `sources/s960_cyclic_loops_rotation_lit_review.md`.

### 14.1 Immediate additions to this RFC workflow

1. Keep symmetry panel logic exactly as a proposal engine:
   - generate rotated/mirrored/conjugated motif variants,
   - pass each variant to kernel-level replay and gates in `RFC-004`.
2. Add a strict distinction between:
   - visual/geometric equivalence,
   - multiplication-respecting equivalence.
3. Use cycle-class and conjugation-tier bins as first-pass search priors, not as identity claims.

Plain-English:
Use symmetry to choose what to test first. Do not treat symmetry resemblance as proof.

### 14.2 Chirality interpretation update

Working interpretation:
1. purely spatial left-right asymmetry is not sufficient as a chirality diagnostic,
2. algebra-aware chirality probes should be included in panels:
   - left-vs-right ordered evolution comparison,
   - associator-activity tracking along trajectories.

Non-claim:
1. this does not assert a finished chirality mechanism; it only improves diagnostics.

### 14.3 Lorentz interpretation update

Working interpretation:
1. symmetry arguments in this RFC support candidate construction,
2. Lorentz-like acceptance remains empirical and mesoscale,
3. claims of emergent Lorentz behavior are valid only after `RFC-004` Lorentz battery passes.

Plain-English:
This RFC can suggest where Lorentz-like behavior might come from, but only the measurements in `RFC-004` can confirm it.

### 14.4 Phase-Resolution and Extension-Architecture Update

Working interpretation:
1. `C4` is a practical phase discretization for current v3 search,
2. there is an unresolved resolution gap between `C4` and charge-like `1/3` structure often discussed in SM-inspired mappings,
3. the existing order-12 sector in `S960` is a testable bridge hypothesis (`effective C12` behavior).

Test-ready consequences:
1. run an `effective C12` diagnostic on order-12 motifs:
   - measure whether observables step through 12 distinct stable phase classes,
   - check reproducibility across seeds and panel transforms.
2. quantify the geometric-vs-multiplication symmetry gap explicitly:
   - compute multiplication-preserving automorphism set for current convention,
   - compare against geometric panel groups used in this RFC.
3. keep non-split phase extensions as exploratory kernel branch only:
   - do not merge into baseline until Gate 0 integrity and lane metrics pass.

Non-claim:
1. this RFC does not claim `C12` is required now; it only registers a concrete investigation line.

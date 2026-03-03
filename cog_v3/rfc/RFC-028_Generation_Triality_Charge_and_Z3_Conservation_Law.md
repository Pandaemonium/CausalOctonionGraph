# RFC-028: Generation Triality Charge and Z3 Conservation Law

Status: Draft (Idealized Algebraic Theorem + Kernel Contract Target)
Date: 2026-03-03
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-010_C12_Phase_Sector_Generation_and_Rare_Hop_Test_Contract.md`
- `cog_v3/rfc/RFC-016_Koide_Formula_C12_Generation_Phase_Derivation.md`
- `cog_v3/rfc/RFC-022_CKM_Mixing_from_C12_Hop_Statistics.md`
- `cog_v3/rfc/RFC-027_Solar_3Phase_Assimilation_Neutrino_Fronts_and_Extrasolar_Meteor_Rephasing_Contract.md`

---

## 1. Purpose

This RFC defines a strict target law for v3:

1. There is an exact generation triality charge `Gamma in Z3`.
2. `Gamma` is exactly conserved by kernel events.
3. Kernel events are synchronous conservative pair updates: two sites act on each other from the same pre-state, simultaneously.

This RFC is an idealized theorem and an implementation contract for future kernel revisions.
It is not a claim that the current executable kernel already satisfies these constraints.

---

## 2. Scope and Terminology

- `S2880 = C12 x Q240`.
- Site state: `s = (p, q)` with `p in Z12`, `q in Q240`.
- Generation index: `g = p mod 3`.
- Sub-clock index: `a = p mod 4`.
- Per-particle generation triality charge: `Gamma = g`.
- Global triality charge:
  - `Gamma_total = (sum_i g_i) mod 3`.

`Gamma_total` is the quantity this RFC requires to be exactly conserved by the kernel.

---

## 3. Correct Symmetry Statement

### 3.1 Generator

Define global generation relabeling:

`T: p -> p + 4 (mod 12)`.

Then:
- `a` is unchanged (`+4 mod 4 = 0`),
- `g -> g + 1 (mod 3)`.

So `T` generates the global `Z3` relabeling of generation sectors.

### 3.2 Important correction

For raw phase-addition product

`(p1, q1) * (p2, q2) = (p1 + p2 mod 12, q1 * q2)`,

we get:

`T(x) * T(y) = T^2(x * y)`,

not `T(x * y)`.

Therefore, `T` is not an automorphism of that binary product as written.

### 3.3 What we require instead

The kernel symmetry requirement is dynamic equivariance:

`K(T(S)) = T(K(S))`,

for global state `S` and one-step update map `K`.

This is the correct symmetry target for the executable model.

---

## 4. Exact Conservation Theorem (Target)

### 4.1 Pair-event model

Kernel update is decomposed into local pair events on interacting pairs `(i, j)`:

`(s_i, s_j) -> (s_i', s_j')`.

Events must be computed from the same pre-event states `(s_i, s_j)` and committed simultaneously.
No sequential "A updates B then B updates A from already-modified state" is allowed.

### 4.2 Triality conservation condition per event

Each pair event must satisfy:

`(g_i' + g_j') mod 3 = (g_i + g_j) mod 3`.

If this holds for every event, then global exact conservation follows:

`Gamma_total(t+1) = Gamma_total(t)`.

Proof is immediate by summing event-local equalities over a full tick.

### 4.3 Equivalent phase condition

Using `g = p mod 3`, the equivalent phase constraint is:

`(p_i' + p_j') mod 3 = (p_i + p_j) mod 3`.

This allows non-multiple-of-3 local hops (exchange between partners) while enforcing exact `Z3` conservation globally.

---

## 5. Conservative Pair-Event Kernel Contract

This section is normative for kernel redesign.

### 5.1 Event structure

For each active pair `(i, j)`:

1. Read pre-event states `s_i, s_j` and pre-event momenta/spins.
2. Compute both outputs from the same pre-event inputs.
3. Commit `(s_i', s_j')` simultaneously.

### 5.2 Conservation constraints per event

Each event map must preserve:

1. Triality:
   - `(g_i' + g_j') mod 3 = (g_i + g_j) mod 3`.
2. Linear momentum:
   - `P_i' + P_j' = P_i + P_j`.
3. Angular momentum:
   - `L_i' + L_j' + r_ij x (P_i' - P_i) = L_i + L_j`.
4. Energy:
   - `E_i' + E_j' = E_i + E_j`.

All four are event-local exact equalities (not only statistical averages).

### 5.3 Implementation pattern

Use a pair map over an extended local state:

`F_ij: (s_i, s_j, P_i, P_j, L_i, L_j, E_i, E_j) -> (...)'`

where `F_ij` is a bijection constrained by the four conservation laws above.

Practical coding rule:
- update both endpoints in one transaction,
- never re-read an endpoint after writing it within the same event.

### 5.4 Scheduling

To avoid conflicts while staying local:

- Partition lattice edges into non-overlapping matchings (edge coloring rounds).
- Execute one round at a time with barrier sync.
- This preserves pair simultaneity and removes fold-order partner desync.

Randomized round order is allowed (for unbiased timelines) if each round itself remains synchronous.

---

## 6. Relation to Discrete Noether

For this project, we use discrete Noether language as follows:

- The exact global `Z3` equivariance of `K` implies a conserved `Z3` charge label.
- In the executable kernel, that is enforced constructively by event-local conservation rules.

This RFC does not claim a full variational/action derivation of the current implementation.
It defines the symmetry-conserving target dynamics to which implementation must conform.

---

## 7. Physical Interpretation

If the kernel satisfies Section 5 exactly:

1. Generation sectors are symmetric labels under global relabeling.
2. Triality is transferred between interacting partners, not created or destroyed.
3. Same-phase suppression and off-phase conversion can exist without violating exact `Gamma` conservation.

This supports the assimilation narrative as a preregistered hypothesis, with strict charge accounting.

---

## 8. Preregistered Hypotheses (Not Yet Derived Facts)

The following are explicitly preregistered hypotheses pending kernel-conformant simulation and external-data checks:

1. Solar neighborhood phase assimilation structure (front/tail asymmetry).
2. Boundary-enhanced off-phase neutrino conversion.
3. Extrasolar object rephasing signatures.
4. Domain-wall-like large-scale phase boundaries.

These remain hypotheses until tested with the conservative pair-event kernel and measured against data.

---

## 9. Triality Governance Checklist

Every kernel/probe artifact in the triality lane must carry and pass this checklist.

### 9.1 State and frame hygiene

1. Report both `p` and `g = p mod 3`.
2. Mark which quantities are absolute labels (`g`) vs frame-invariant differences (`Delta_Gamma`).
3. Include `convention_id`, `kernel_profile`, and declared triality frame in artifact metadata.

### 9.2 Event semantics

1. Pair updates must be synchronous two-endpoint commits from a shared pre-state.
2. Per-event triality conservation must be audited:
   - `(g_i' + g_j') mod 3 = (g_i + g_j) mod 3`.
3. No one-sided fold step may update one partner before computing the other partner output.

### 9.3 Boundary accounting

1. Closed/periodic runs: require zero global triality flux.
2. Open/fixed runs: expose a boundary-flux accounting term (or a clear proxy) and do not call residual drift "conserved."
3. Report both global and interior-only triality audit statistics.

### 9.4 Symmetry regression

For any probe panel, include a regression check for global relabeling equivariance:

`K(T(S)) = T(K(S))`.

Failures are model failures, not presentation differences.

### 9.5 Claims discipline

1. Algebraic theorem statements, measured kernel behavior, and astrophysical hypotheses must be in separate labeled lanes.
2. Astrophysical consequences remain preregistered hypotheses until they pass kernel-conformant tests and external-data checks.

---

## 10. Acceptance Criteria

RFC-028 is considered implemented when all pass:

1. Unit tests show per-event exact conservation of `Gamma`, energy, linear momentum, angular momentum.
2. Global invariants remain exact over long runs (no drift beyond integer arithmetic identity).
3. `K(T(S)) = T(K(S))` holds in regression tests.
4. Pair simultaneity tests confirm no partner desync from fold order.

---

## 11. Immediate Follow-on Work

1. Implement `Phase M-conservative` kernel variant with pair transaction updates.
2. Add invariant-audit hooks: event-level delta logs for all four conserved quantities.
3. Re-run RFC-010/RFC-022 panels under the new kernel.
4. Re-evaluate RFC-027 hypotheses with preregistered pass/fail thresholds.

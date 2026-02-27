# RFC-048: Two-Node to Many-Body Bridge

Status: Active Draft - Lit-backed closure plan (2026-02-26)
Module:
- `COG.Core.MultiBodyBridge`
Depends on:
- `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-035_Distance_as_Next_Interaction_Node_Gap.md`
- `rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md`
- `CausalGraphTheory/TwoNodeSystem.lean`
- `CausalGraphTheory/D4D5Contracts.lean`
- `CausalGraphTheory/UpdateRule.lean`

---

## 1. Executive Summary

COG currently has deterministic two-node interaction classification (repulsive/attractive/neutral). This RFC defines the canonical bridge to many-body systems without changing locked kernel rules.

Core position:
1. many-body behavior must be composed from the same local update law (`nextStateV2` + D4),
2. pair metrics in many-body context must be explicit derived observables, not hidden side effects,
3. two-node semantics must be exactly recovered as a limiting case.

---

## 2. Why this needs a dedicated RFC

Pairwise rules do not close many-body dynamics by default. Higher-order correlations and scheduling choices can change effective pair behavior.

Unresolved issues:
1. concurrent multi-neighbor messages to one receiver,
2. tie-break and fold order under multi-source input,
3. pair metric extraction under background load,
4. distance-gap updates when D4 spawn changes topology.

Without a bridge contract, "pair attraction/repulsion in many-body" is ambiguous.

---

## 3. Literature Synthesis

## 3.1 Pairwise laws are not enough for many-body closure

Kinetic theory and BBGKY hierarchy show pair distributions generally depend on higher-order correlations; naive pair closure is not exact in many-body regimes.

Implication for COG:
1. pair classification from two-node tests cannot be assumed to transfer unchanged to dense many-body contexts,
2. pair observables must be defined with explicit conditioning on background state.

## 3.2 Deterministic composition is still possible

Distributed-systems and causal-graph results show deterministic global evolution can be built from local rules if causal order and tie-break policy are explicit.

Implication for COG:
1. use snapshot-style round semantics (same round-start state for all node updates),
2. enforce canonical ordering on incoming boundary messages,
3. keep no-RNG/no-wall-clock contract.

## 3.3 Update schedule choice materially affects dynamics

Synchronous vs asynchronous local updates can produce qualitatively different macroscopic behavior.

Implication for COG:
1. bridge must lock one scheduler semantics for claim-grade runs,
2. alternate scheduler experiments must be marked as sensitivity studies, not canonical outputs.

---

## 4. Canonical Bridge Semantics

Define one many-body round from microstate `ms_t`:

1. Freeze round-start snapshot `ms_t`.
2. For each existing node `v`, compute ordered active boundary payload list from `ms_t` only.
3. Compute updated node state `v' := nextStateV2(v, msgs_v)` from frozen snapshot.
4. Apply D4 spawn transition at round boundary using `applySpawnImpl` on active conditions.
5. Produce `ms_{t+1}`.

No in-round feedback from already-updated nodes is allowed.

Rationale:
1. preserves determinism and avoids order artifacts from container traversal,
2. keeps reduction to two-node semantics exact when background is absent.

---

## 5. Pair-Observable Contract in Many-Body Context

For any labeled pair `(a, b)`, define three observables:

1. **Direct pair channel** `P_direct(a,b,t)`:
   - uses only messages exchanged between `a` and `b` in round `t`.
2. **Background-conditioned pair channel** `P_cond(a,b,t)`:
   - computed in full many-body run with all active inputs present.
3. **Background drift** `Delta_bg(a,b,t)`:
   - `P_cond - P_direct` (signed difference under declared metric).

This split prevents overclaiming:
1. `P_direct` validates pair law inheritance,
2. `Delta_bg` quantifies many-body distortion explicitly.

---

## 6. Distance-Gap Integration (RFC-035)

Distance metric remains `d_next` (next-interaction node gap).

Lock for bridge runs:
1. recompute `d_next` once per round after D4 topology updates are finalized,
2. pair-distance trace must be reported alongside polarity trace,
3. any claim about "moving closer/farther" must cite whether it uses `P_direct` or `P_cond`.

---

## 7. Decisions to lock

## D1. Pair metric mode

Options:
1. receiver-oriented,
2. symmetric pair aggregation.

Recommendation:
1. lock symmetric aggregation for canonical bridge outputs,
2. keep receiver-oriented only as diagnostic.

## D2. Scheduler semantics

Options:
1. snapshot-synchronous,
2. asynchronous event-driven.

Recommendation:
1. lock snapshot-synchronous as canonical (matches current two-node semantics),
2. treat asynchronous as sensitivity mode only.

## D3. Background accounting

Options:
1. no decomposition (single metric),
2. explicit `P_direct/P_cond/Delta_bg`.

Recommendation:
1. lock explicit decomposition to prevent hidden many-body leakage.

## D4. Distance recomputation timing

Options:
1. pre-spawn,
2. post-spawn.

Recommendation:
1. lock post-spawn recompute, since interaction topology for the next round includes spawned nodes.

---

## 8. Deliverables

## 8.1 Python

1. `calc/many_body_bridge.py`
2. `calc/test_many_body_bridge.py`
3. artifacts:
   - pair traces (`P_direct`, `P_cond`, `Delta_bg`),
   - distance-gap traces,
   - replay hashes.

## 8.2 Lean

1. `CausalGraphTheory/MultiBodyBridge.lean` scaffold
2. initial lemmas:
   - two-node reduction theorem (special-case equivalence),
   - determinism theorem for frozen-snapshot round map,
   - permutation-invariant round outcome under canonical ordering assumptions.

## 8.3 Claim metadata

Add to relevant claims:
1. `pair_metric_mode`
2. `scheduler_mode`
3. `background_accounting_mode`
4. `distance_recompute_timing`

---

## 9. Falsification Gates

1. If two-node special case is not exactly recovered, bridge fails.
2. If many-body outcomes depend on node container order, bridge fails.
3. If pair conclusions flip between `P_direct` and `P_cond` without disclosure, claim fails.
4. If replay hashes diverge under fixed seed/config, bridge fails.
5. If nonlocal dependencies appear (outside cone-local inputs), bridge fails.

---

## 10. Acceptance Criteria

1. Two-node behavior is reproduced exactly as a special case.
2. Canonical many-body run is deterministic under replay.
3. Pair metrics include explicit background decomposition.
4. Distance-gap traces are generated under locked recompute policy.
5. At least one nontrivial many-body benchmark is archived with full provenance.

---

## 11. Sources

1. Kac (1956), *Foundations of kinetic theory*  
   https://projecteuclid.org/journals/proceedings-of-the-third-berkeley-symposium-on-mathematical-statistics-and-probability/volume-3/article/Foundations-of-kinetic-theory/10.1525/9780520313880-006
2. Braun and Hepp (1977), *The Vlasov Dynamics and Its Fluctuations in the 1/N Limit*  
   https://doi.org/10.1007/BF01614171
3. Lamport (1978), *Time, Clocks, and the Ordering of Events in a Distributed System*  
   https://www.microsoft.com/en-us/research/publication/time-clocks-ordering-events-distributed-system/
4. Chandy and Lamport (1985), *Distributed Snapshots*  
   https://www.microsoft.com/en-us/research/publication/distributed-snapshots-determining-global-states-distributed-system/
5. Arrighi and Dowek (2012), *Causal graph dynamics*  
   https://arxiv.org/abs/1202.1098
6. Schoenfisch and de Roos (1999), *Synchronous and asynchronous updating in cellular automata*  
   https://doi.org/10.1016/S0303-2647(99)00025-8

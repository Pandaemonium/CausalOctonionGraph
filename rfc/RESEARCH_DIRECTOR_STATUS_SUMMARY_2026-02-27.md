# Research Director Status Summary (2026-02-27)

Status: Active  
Audience: Research Director  
Purpose: Clear program snapshot, open questions, and priority targets requiring direction.

---

## 1. Executive Snapshot

The project has moved from "define basic algebra" to "close governed derivations."

What is strong right now:
1. deterministic `C x O` XOR update machinery is real and runnable,
2. full-lightcone simulation path is implemented and tested,
3. Furey minimal-left-ideal motifs are integrated in runtime and artifact pipelines,
4. reproducibility discipline (replay hashes, fixed condition files, tests) is materially better.

What is not strong yet:
1. generation hierarchy mechanism (electron/muon/tau separation) is still weakly evidenced,
2. photon model is still operational/proxy-level, not a locked first-class kernel entity,
3. fine-structure derivation remains open because key measurement conventions are not yet locked,
4. several high-level claims still rely on candidate motif mappings, not canonical motif locks.

Bottom line:
1. infrastructure is now good enough to run serious falsification campaigns,
2. physics closure is blocked by a short list of unresolved modeling decisions.

---

## 2. What Is Canonical vs Exploratory

## 2.1 Canonical (locked policy)

From current RFC and runtime path:
1. state space: integer-coefficient `C x O`,
2. deterministic update semantics (D1-D3) with no runtime RNG,
3. full past-lightcone contributor fold per tick in canonical simulation profile,
4. static-cone no-spawn policy path (D4 lock direction),
5. distance semantics are edge-count based and integer-valued.

Implementation notes:
1. non-integer edge distances are now explicitly rejected at runtime (`TypeError`),
2. full-cone and two-body pipelines pass deterministic replay tests.

## 2.2 Exploratory (not yet promotion-grade)

1. muon/tau candidate mappings used in current drag scans are placeholders,
2. generation-drag `C_t` stabilization work is currently estimated, not measured from explicit repair ops,
3. e7-ablation signal is visible at early depth but persistence and separation are unresolved,
4. photon interaction mechanism is represented as update effects, not yet a locked kernel object.

---

## 3. Current Technical Progress (Concrete)

## 3.1 Running and validated modules

1. Full-lightcone engine:
   - `calc/xor_full_lightcone_engine.py`
   - deterministic and tested.
2. Furey ideals:
   - `calc/xor_furey_ideals.py`
   - includes electron and dual electron doubled motifs.
3. Two-body edge-distance dynamics:
   - `calc/xor_two_body_kinematics.py`.
4. Generation-drag instrumentation (Phase A):
   - `calc/xor_generation_drag_metrics.py`
   - `calc/generation_drag_motif_mapping.json`
   - report: `sources/generation_drag_report.md`.
5. e7 muon ablation prep scan:
   - `calc/xor_e7_muon_ablation_scan.py`
   - conditions: `calc/e7_muon_ablation_conditions.json`
   - report: `sources/e7_muon_ablation_prep_report.md`.

## 3.2 Test status (recent)

Focused suites around these modules are passing, including:
1. full-lightcone tests,
2. generation-drag tests,
3. e7-ablation tests,
4. two-body and Furey-lightcone tests.

---

## 4. Physics Questions We Are Actively Asking

## 4.1 Generation hierarchy question

Can heavier leptons be explained as deterministic drag from:
1. scalar-channel load,
2. ideal misalignment,
3. stabilization/associator exposure,
under one XOR/lightcone kernel with no fitted attenuation?

Current answer:
1. instrumentation exists,
2. strong separation has not yet emerged under current candidate mappings.

## 4.2 e7-ablation question

Do muon-like motifs show persistent enhanced ablation when projected along e7 relative to electron baseline?

Current answer:
1. depth-0 deficit exists in current scan,
2. signal decays quickly in current horizon/case setup,
3. muon vs tau candidate separation is not resolved.

## 4.3 Fine-structure path question

Can alpha be derived from full-lightcone electron motif interaction metrics without introducing non-native fitting?

Current answer:
1. core scaffolding is in place,
2. closure blocked by unresolved metric-definition and photon-mechanism conventions.

---

## 5. Decisions Needed From Research Director

These are the highest-leverage decisions to unlock progress.

1. Lock canonical muon and tau motifs.
   - Required: explicit motif IDs and isomorphism rationale from electron motif.
2. Lock local-frame projection contract for spinor identity axis.
   - Needed to avoid ambiguity between global `e0` and frame-projected identity direction.
3. Lock pass/fail criterion for "enhanced ablation."
   - Example: persistence depth and cumulative projected ablation threshold.
4. Lock fine-structure observable definition.
   - Exact measurement formula, control subtraction rule, and plateau window.
5. Lock how photon is represented in this stage.
   - Message-level effect only vs explicit edge/boson motif representation.
6. Lock claim-promotion boundary.
   - What evidence level upgrades a result from exploratory to partial.

Without these locks, simulations run but remain hard to interpret as model-derived physics.

---

## 6. Top Targets (Priority Order)

## Target 1: Motif Lock Packet (immediate)

Deliverable:
1. short RFC/addendum that freezes electron/muon/tau motif mapping and frame-projection rules.

Why first:
1. all generation and e7-ablation claims depend on this.

## Target 2: Measured Stabilization Work (Phase B)

Deliverable:
1. replace estimated `C_t` with measured per-tick repair-operation counts from explicit stabilizer pass.

Why:
1. current hierarchy proxy is dominated by geometry term `A_t`, masking motif effects.

## Target 3: e7-Ablation Persistence Sweep

Deliverable:
1. distance and phase sweep with persistence metrics and controls.

Why:
1. confirms whether the observed depth-0 signal is physical or initialization artifact.

## Target 4: Photon Contract v1

Deliverable:
1. operational photon definition tied to `C x O` update events and e7/phase effects.

Why:
1. required for non-handwavy alpha derivation.

## Target 5: Fine-Structure Protocol Lock

Deliverable:
1. full measurement protocol (inputs, outputs, normalization, controls, uncertainty policy).

Why:
1. prevents curve fitting and keeps governance clean.

---

## 7. Risks If We Do Not Adjust

1. Runtime progress without physics closure:
   - many artifacts, little promotion-grade evidence.
2. Status inflation risk:
   - conclusions outpace locked observables.
3. Motif drift risk:
   - changing candidate mappings makes cross-run comparisons invalid.
4. Interpretability risk:
   - multiple competing axis/projection definitions produce contradictory narratives.

---

## 8. How the Research Director Can Help Most

Highest leverage actions:
1. make the motif/frame/projection decisions in one short "lock packet" this week,
2. require every new physics run to declare:
   - motif set,
   - projection profile,
   - control subtraction,
   - replay hash,
3. enforce "no promotion without locked metric definition."

If these are done, the current codebase can execute a serious falsification-driven campaign immediately.

---

## 9. Recommended Next 72 Hours

1. Approve motif lock packet (electron/muon/tau + projection axes).
2. Run measured-stabilization implementation task.
3. Run e7 persistence sweep over locked conditions.
4. Produce one go/no-go memo:
   - "generation drag supported or falsified under locked mapping."
5. If supported, move directly to photon contract and alpha protocol lock.
   - If falsified, branch to alternate mechanism with same governance.

---

## 10. Program State Summary

The project is now in a good engineering state for decisive physics tests.

The key bottleneck is no longer missing code.  
The bottleneck is unresolved model-definition decisions at the motif/projection/observable layer.

Once those are locked, the next wave of simulations can be interpreted as real evidence, not exploratory numerics.

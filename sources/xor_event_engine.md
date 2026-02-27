# XOR Event Engine (MVP)

Status: active scaffold artifact  
Primary code: `calc/xor_event_engine.py`  
Build script: `scripts/build_xor_event_engine_scenarios.py`

## Scope
1. Typed event-state model (`XNodeState`, `XEdgeOperator`, `XMessage`, `XEventState`).
2. Deterministic scheduler:
1. canonical edge/message ordering,
2. temporal commit,
3. ordered message fold.
3. Built-in simple scenarios:
1. single motif + vacuum drive,
2. two-node opposite-sign pair,
3. two-node same-sign pair.
4. Scenario traces and compact CSV output for dashboards.

## Artifacts
1. `calc/xor_event_engine_scenarios.json`
2. `calc/xor_event_engine_scenarios.csv`
3. `website/data/xor_event_engine_scenarios.json`
4. `website/data/xor_event_engine_scenarios.csv`

## Not Claimed
1. This MVP is deterministic event simulation, not a calibrated scattering engine.
2. No geometric distance/trajectory model is included.
3. Pair polarity labels are internal COG observables, not direct detector outputs.

## Large Integer Note
1. Exact coefficient histories are persisted in `node_state_exact_base8` as base-8 strings.
2. Per-node charges are persisted as `charges_base8`.
3. This avoids large-integer JSON parse limits while preserving exact values.

## Extension Clues
1. Add configurable message payload modes beyond `src_state`/`identity`.
2. Add scenario schema files (YAML) for clerk-authored runs.
3. Add event replay hash and promotion-grade invariant checks.
4. Add many-node topology and spawn hooks when D4/D5 extensions are promoted.

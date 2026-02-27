# XOR Scenario Loader

Primary code: `calc/xor_scenario_loader.py`

## Purpose
1. Load YAML scenario specs into typed structures.
2. Resolve motif IDs into canonical XOR seed states.
3. Build `XEventState` objects for deterministic event-engine execution.

## Key functions
1. `load_scenario_specs(path)`
2. `canonical_motif_state_map()`
3. `build_event_state_from_spec(spec)`
4. `run_loaded_scenario(spec)`

## Notes
1. Supports `motif_id` or explicit `state_base8` node definitions.
2. Edge definitions are validated against declared nodes.


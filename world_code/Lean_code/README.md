# Lean_code

`MinimalWorldKernel.lean` defines the smallest formal contract for simulation:

1. full predetermined lightcone input (`LightconeInput`),
2. deterministic local update rule (`KernelRule.updateRule`),
3. global deterministic evolution (`step`, `run`).

It intentionally contains no observable layer.


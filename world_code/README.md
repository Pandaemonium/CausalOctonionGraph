# world_code

This directory is the minimal simulation surface for COG.

The goal is to keep only the essentials needed to evolve a physical system from
a fully predetermined light cone:

1. full initial `C x O` lightcone microstate,
2. deterministic update rule.

Everything else (observables, dashboards, claims, pedagogy) is intentionally
outside this kernel.

## Layout

1. `Lean_code/`
   - Minimal formal kernel contract for deterministic lightcone evolution.
2. `Python_code/`
   - Minimal executable kernel using integer-complex octonions and a canonical
     Fano multiplication orientation.

## Contract

A conforming simulation package should include:

1. `initial_lightcone_state` (all nodes, all parent links, all node states),
2. `update_rule` (deterministic function),
3. `steps` (finite evolution horizon).


# Triplet-Decay Exact Model Formalization (v1)

Status: Active draft  
Date: 2026-02-28

## 1. What Is Formalized Now

This package now includes an exact deterministic simulator for:

1. a stable triplet quark motif,
2. an approaching high-energy perturbing motif,
3. perturbation-induced motif break,
4. decay interpretation from off-resonance dynamics.

Primary script:

1. `cog_v2/calc/build_triplet_decay_exact_simulation_v1.py`

Primary artifacts:

1. `cog_v2/sources/triplet_decay_exact_simulation_v1.json`
2. `cog_v2/sources/triplet_decay_exact_simulation_v1.md`

## 2. Kernel-Level Exactness

The simulation uses only canonical v2 operations:

1. `cog_v2/python/kernel_projective_unity.py`
2. Gaussian-integer arithmetic (exact integer operations),
3. deterministic projector (`pi_unity_axis_dominance_v1`),
4. no stochastic terms, no numerical integration.

All event states are exact finite values in the kernel representation.

## 3. Stable Motif and Perturbers

Default motif lanes:

1. `stable_triplet_quark_v1`
2. `high_energy_perturber_v1`
3. `xy_gut_boson_proxy_v1` (explicitly hypothetical proton-decay mediator proxy)

Note: X/Y bosons are not experimentally observed; this lane is a high-energy exploratory proxy.

## 4. Interaction Model

Per tick:

1. evolve quark motif by deterministic op sequence,
2. evolve perturber motif by deterministic op sequence,
3. decrease graph distance according to schedule,
4. compute coupling multiplicity from distance,
5. apply kick and coupling through canonical update rule.

Coupling rises as distance decreases:

1. `distance(t) = max(d_min, d_start - approach_speed * t)`
2. `coupling_mult = 0` for `distance > interaction_radius`
3. else `energy_scale * (interaction_radius - distance + 1)`

## 5. Decay Formalization

The script logs three distinct conditions:

1. motif break (`off_motif`) via triplet coherence threshold,
2. vacuum coupling (`vacuum_coupled`) via `e000` share threshold under active coupling,
3. daughter-channel production (`daughter_channels_present`) via non-triplet support.

Decay is defined as:

1. `off_motif AND (vacuum_coupled OR daughter_channels_present)`

This keeps decay semantics explicit rather than conflating all behavior into one scalar threshold.

## 6. Current Default Exact Results

From `triplet_decay_exact_simulation_v1.json`:

1. `scenario_count = 2`
2. `decay_hit_count = 2`
3. `xy_proxy_decay_hit_count = 1`

In both default scenarios, first decay appears at tick 6 under the current schedule.

## 7. Compute-Scalable Exact Mode

The simulator supports exact exhaustive sequence enumeration:

```bash
python -m cog_v2.calc.build_triplet_decay_exact_simulation_v1 \
  --ticks 192 \
  --exhaustive-op-length 6 \
  --max-scenarios 0 \
  --checkpoint-every 1000 \
  --checkpoint-dir cog_v2/sources/triplet_decay_checkpoints \
  --write-sources
```

Notes:

1. `--exhaustive-op-length L` enumerates exactly `7^L` perturber op sequences.
2. `--max-scenarios 0` means unbounded run.
3. checkpoint files are deterministic and hashable.

## 8. What Is Still Missing for Full Formal Closure

Not yet closed:

1. Lean theorem chain for this full dynamic decay map (currently Python-exact),
2. theorem-level equivalence between simulation decay criterion and a unique continuum EFT map,
3. exhaustive closure over all motif families and all depths.

So the current status is:

1. exact deterministic simulation formalization: present,
2. full theorem closure of dynamic decay in Lean: pending.


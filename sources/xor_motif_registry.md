# XOR Motif Registry (Canonical Seeds)

Status: active scaffold artifact  
Primary code: `calc/xor_motif_registry.py`  
Build script: `scripts/build_xor_motif_registry.py`

## Scope
1. One canonical registry for vector and spinor XOR motif seeds.
2. Deterministic per-motif metadata:
1. support indices and bit labels,
2. `u1_charge_proxy`,
3. `e7` left/right cycle periods,
4. stable-period-4 flag.
3. Stable registry hash for downstream reproducibility.

## Included Motif Families
1. Vector Fano-line motifs (`vector_fano_line_l*`).
2. Named vector aliases (`vector_electron_favored`, `vector_proton_proto_t124`).
3. Furey ideal spinor motifs (`Su`, `Sd` basis-like rows).
4. Named spinor aliases (`left_spinor_electron_ideal`, `right_spinor_electron_ideal`).

## Artifacts
1. `calc/xor_motif_registry.json`
2. `calc/xor_motif_registry.csv`
3. `website/data/xor_motif_registry.json`
4. `website/data/xor_motif_registry.csv`

## Not Claimed
1. Registry entries are structural seeds, not experimental particle IDs.
2. Charge proxy is an internal observable, not direct measured electric charge.
3. This artifact does not by itself validate bound-state energetics.

## Extension Clues
1. Add registry cross-links to claim YAML files (`claim_id`, gate refs).
2. Add projection-profile fields once D5 extended profile is promoted.
3. Add perturbation-basin metadata from future XCALC perturbation scans.


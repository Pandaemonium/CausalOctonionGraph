# Convention IDs

This file defines stable names for runtime conventions to prevent accidental mixing.

## Active default

- `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`
  - Status: active default
  - Kernel profile: `cog_v3_octavian240_multiplicative_v1`
  - Update rule: multiplication-only
  - Octavian alphabet: closed 240

## Legacy (read-only replay)

- `v2_furey_projective_unity_v1`
  - Status: legacy
  - Typical kernel profile: `cog_v2_projective_unity_v1`
  - Update rule: projective unity (non-multiplicative)

- `v2_octavian240_closed_cyclic_base_v1`
  - Status: legacy experimental
  - Kernel profile: `cog_v2_octavian240_closed_v1`
  - Update rule: multiplication-only
  - Basis: cyclic closed-240 base before v3 convention transform

## Naming rules

1. Prefix with major lane: `v2_`, `v3_`, ...
2. Include algebra/basis keyword: `furey`, `octavian240`, ...
3. Include transform identifier when relevant: `perm_...`, `sign_...`.
4. Never reuse an ID for a changed multiplication table or basis transform.
5. Every artifact must include `convention_id`.


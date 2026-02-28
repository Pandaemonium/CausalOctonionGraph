# THETA-002 Replication Pack (v1)

- Claim: `THETA-002`
- Replay hash: `05166766d01a1c6df342a51b29e79016f44f893d94f6f652d348988243402d37`
- Selected scenarios: `4`
- Fallback used: `False`

## Smoke Test
- all_squared_zero_expected: `True`
- all_oriented_cubic_excluding_t0_nonzero_expected: `True`

## Scenarios

| scenario_id | lane | sample_id | weak_kick | ckm_phase | period | sq_expected | cubic_ex_t0_expected | robust_anchor |
|---|---|---:|---:|---:|---:|---:|---:|---|
| theta002_replica_weak_01_sample234 | weak | 234 | 5 | 3 | 2 | 0 | 1816 | True |
| theta002_replica_weak_02_sample166 | weak | 166 | 11 | 3 | 3 | 0 | 4164 | True |
| theta002_replica_ckm_03_sample340 | ckm | 340 | 9 | -1 | 5 | 0 | 3624 | True |
| theta002_replica_ckm_04_sample206 | ckm | 206 | 11 | 1 | 2 | 0 | -2730 | True |

## Verification
- Runner: `python -m cog_v2.calc.build_theta002_replication_pack_v1 --write-sources`
- Verify: Compare replay_hash and each scenario_hash against published pack.

## Limits
- Replication pack is for THETA-002 exploratory lane.
- Does not modify THETA-001 supported_bridge contract.
- Any promotion requires independent skeptical review.

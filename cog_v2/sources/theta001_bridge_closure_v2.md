# THETA-001 Bridge Closure Artifact (v2)

- Claim: `THETA-001`
- Replay hash: `c737a82b2754553ca641e9712448736b5195ea790c9b856497ae8aaf441c80e0`
- Source script: `cog_v2/calc/build_theta001_bridge_closure_v2.py`

## Structural Residual
- Sign balance: +21 / -21
- Signed sum: `0`
- Orientation closed: `True`

## Weak Leakage
- Weak lane all zero: `True` (max abs 0)
- CKM-like lane all zero: `True` (max abs 0)

## Bridge Lanes
- Linear lane status: `primary_blocking`
- Linear cp odd all hold: `True`
- Linear zero anchor all hold: `True`
- Periodic lane status: `stub_non_blocking`

## Promotion Readiness
- bridge_ready_supported_bridge: `True`

## Replay
Run `python -m cog_v2.calc.build_theta001_bridge_closure_v2 --write-sources` and verify the replay hash is unchanged.

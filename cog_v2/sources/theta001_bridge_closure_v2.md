# THETA-001 Bridge Closure Artifact (v2)

- Claim: `THETA-001`
- Replay hash: `791cebf3dfd26c15cd11b2895ef48219d8e11f63e6da70b77f9a83275ad182aa`
- Source script: `cog_v2/calc/build_theta001_bridge_closure_v2.py`

## Structural Residual
- Sign balance: +21 / -21
- Signed sum: `0`
- Orientation closed: `True`

## Weak Leakage
- Stress profile depth: min 72 / max 72
- Weak grid size: 324
- CKM-like grid size: 1440
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

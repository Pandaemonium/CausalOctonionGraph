# THETA-001 Bridge Closure Artifact (v2)

- Claim: `THETA-001`
- Replay hash: `744d5ab2aade7c178cefac7e22a3e58f160c418be3b6c3382f037db7376a6849`
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

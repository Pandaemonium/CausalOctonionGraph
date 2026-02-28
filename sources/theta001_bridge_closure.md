# THETA-001 Bridge Closure Artifact

- Claim: `THETA-001`
- Policy: `theta001_bridge_closure_v1`
- Replay hash: `0dd84a9d04efe5bf60a9fb6cc19ace29cac475d1e31f7c41555478cfb041077c`

## Discrete Residual
- Positive count: 21
- Negative count: 21
- Signed sum: 0
- Residual zero: `True`

## Weak Leakage Suite
- Cases: 3
- Grid rows: 120
- Max abs strong residual: 0
- All zero: `True`

## CKM-Like Weak Leakage Suite
- Cases: 3
- Grid rows: 432
- Max abs strong residual: 0
- All zero: `True`

## CKM-Conjugate Falsifier Lane (Non-Blocking)
- Status: `exploratory_non_blocking`
- Promotion blocking: `False`
- Cases: 432
- Max abs strong residual: 736
- Any nonzero residual detected: `True`
- First nonzero tick (max case): `4`
- Max abs tick delta (max case): `256`

## Continuum Bridge Contract
- Mode: `conditional_linear_map_v1`
- Map form: `theta_continuum = scale * discrete_cp_residual`
- Conditional conclusion theta=0: `True`

### Lean Theorems
- `CausalGraph.discreteCpResidual_zero`
- `CausalGraph.theta_zero_if_direct_bridge`
- `CausalGraph.theta_zero_if_linear_bridge`
- `CausalGraph.theta_zero_if_affine_bridge`

## Periodic Angle Lane (Parallel Stub)
- Status: `stub_non_blocking`
- Promotion blocking: `False`
- Map form: `theta = wrap(k * discrete_cp_residual)`
- Probe k: `1.0`
- CP oddness mod 2pi all hold: `True`

## Linear Map Lane (Primary Blocking)
- Status: `primary_blocking`
- Promotion blocking: `True`
- Map form: `theta = scale * discrete_cp_residual`
- CP oddness all hold: `True`
- Zero anchor all hold: `True`

## Promotion Signal
- bridge_ready_supported_bridge: `True`

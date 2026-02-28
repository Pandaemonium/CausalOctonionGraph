# THETA-001 Bridge Closure Artifact

- Claim: `THETA-001`
- Policy: `theta001_bridge_closure_v1`
- Replay hash: `fb91dd494109d21543e924f62621ccef1c25a6bfa4b7951bdc53a10eb3be2305`

## Discrete Residual
- Positive count: 21
- Negative count: 21
- Signed sum: 0
- Residual zero: `True`

## Weak Leakage Suite
- Cases: 40
- Deep-cone length: 18
- Max abs strong residual: 0
- All zero: `True`

## Continuum Bridge Contract
- Mode: `conditional_linear_map_v1`
- Map form: `theta_continuum = scale * discrete_cp_residual`
- Conditional conclusion theta=0: `True`

### Lean Theorems
- `CausalGraph.discreteCpResidual_zero`
- `CausalGraph.theta_zero_if_direct_bridge`
- `CausalGraph.theta_zero_if_linear_bridge`
- `CausalGraph.theta_zero_if_affine_bridge`

## Promotion Signal
- bridge_ready_supported_bridge: `True`

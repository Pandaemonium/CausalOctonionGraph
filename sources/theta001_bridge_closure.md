# THETA-001 Bridge Closure Artifact

- Claim: `THETA-001`
- Policy: `theta001_bridge_closure_v1`
- Replay hash: `69c00eb2b951f9b4aa24e3303b772dcc60d39116ec8f1fdf6b93c83bb87fe20e`

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

## CKM-Like Weak Leakage Suite
- Cases: 144
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

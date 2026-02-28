# WEINBERG IR Bridge from Exact Lightcone Microstate (v1)

- Claim: `WEINBERG-001`
- Policy: `weinberg_ir_bridge_microstate_v1`
- Replay hash: `b3affe284aac15be252326c5a91116c9fc1c26081586c78631d22cf55a31b9e6`
- Bridge pass: `True`

## Locked Microstate Inputs
- node_ids: `['l0', 'l1', 'q0', 'q1', 'mix0', 'mix1', 'obs']`
- u1_channel: `7`
- weak_channels: `[1, 2, 3]`

## Bridge Policy
- uv_anchor: `0.25`
- leakage_coeff: `0.14285714285714285`
- formula: `sin2_ir = uv_anchor - leakage_coeff * mean_e000_share_stationary`

## Stationary Summary
- mean_e000_share_stationary: `0.1428571429`
- ir_bridge_estimate: `0.2295918367`
- target_sin2_theta_w: `0.23122000` at `M_Z`
- target_gap: `-0.0016281633`
- detected_period_ticks: `8`

## Acceptance Checks
- uv_anchor_exact_at_tick0: `True`
- stationary_period_detected: `True`
- no_output_tuned_parameter: `True`
- ir_bridge_within_2pct_target: `True`

## Tick-by-Tick Notes
The JSON artifact includes `running_trace` with exact node state for every tick/event.

# WEINBERG IR Bridge with Exact Combinatoric Constants (v2)

- Claim: `WEINBERG-001`
- Policy: `weinberg_ir_bridge_combinatoric_exact_v2`
- Replay hash: `61151632180b7256827391efa5b319f0d540d1f304b2b64ff3999d56b9687c1e`
- Bridge pass: `True`

## Exact Constants (No Tuning)
- uv_anchor = `1/4` (0.2500000000)
  from `exclusive_u1_card / electroweak_card` with cards `1/4`
- leakage_coeff = `1/7` (0.1428571429)
  from `e000_sink_card / non_e000_card` with cards `1/7`

## Bridge Formula
- `sin2_ir = uv_anchor - leakage_coeff * mean_e000_share_stationary`

## Stationary Summary
- mean_e000_share_stationary: `1/7` (0.1428571429)
- ir_bridge_estimate: `45/196` (0.2295918367)
- target_sin2_theta_w: `0.23122000` at `M_Z`
- target_gap: `-0.0016281633`
- detected_period_ticks: `8`

## Acceptance Checks
- uv_anchor_exact_at_tick0: `True`
- stationary_period_detected: `True`
- combinatoric_constants_exact: `True`
- no_output_tuned_parameter: `True`
- ir_bridge_within_2pct_target: `True`

## Tick-by-Tick Notes
The JSON artifact includes `running_trace` with exact node state for every tick/event.

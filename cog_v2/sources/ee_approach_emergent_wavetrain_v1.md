# Two-Electron Approach Emergent Wavetrain (v1)

## Setup

- Two identical electron motifs initialized far apart in 1D.
- Initial velocities point toward each other.
- State updates use only `kernel_projective_unity` update rules.
- Distance gates interaction multiplicity; no explicit Coulomb law term is injected.

## Parameters

- ticks: `200000`
- x_left_0, x_right_0: `-20000.0`, `20000.0`
- v_left_0, v_right_0: `0.35`, `-0.35`
- interaction_radius: `12.0`
- energy_scale: `2`
- accel_scale: `0.04`
- thin_output_step: `100`

## Outcome Summary

- first_interaction_tick: `57126`
- first_wavetrain_tick: `57126`
- first_left_reverse_tick: `57128`
- first_right_reverse_tick: `57128`
- first_separation_tick: `57128`
- any_reversal: `True`
- any_separation_after_approach: `True`
- min_distance: `10.960000006024636`
- final_distance: `105734.96000023163`
- recorded_row_count / total_tick_count: `2003` / `200000`

## Notes

- `wavetrain_coherence` is a mediator diagnostic from imaginary-spin content of the folded mediator state.
- `pressure_signal` is derived from mediator coherence and interaction multiplicity only.
- `tick_rows` may be thinned by `thin_output_step`; key event ticks are always retained.
- Full exact microstates are recoverable by rerunning with `--thin-output 1`.

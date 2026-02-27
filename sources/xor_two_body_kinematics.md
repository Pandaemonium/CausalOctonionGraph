# XOR Two-Body Kinematics

Primary code: `calc/xor_two_body_kinematics.py`  
Build script: `scripts/build_xor_two_body_kinematics.py`

## Policy Lock
1. Distance semantics: edge separation count.
2. Propagation: one hop per tick.
3. Impulse source: charge-sign relation at message arrival.
4. Topology update cadence: every tick.
5. Boundary condition: superdeterministic.
6. Observable: `distance_delta = future_edge_distance - past_edge_distance`.

## Artifacts
1. `calc/xor_two_body_kinematics.json`
2. `calc/xor_two_body_kinematics.csv`
3. `website/data/xor_two_body_kinematics.json`
4. `website/data/xor_two_body_kinematics.csv`


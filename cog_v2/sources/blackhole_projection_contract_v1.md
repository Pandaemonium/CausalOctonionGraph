# Black-Hole Projection Contract Witness (v1)

- Contract ID: `BH-PRJ-001`
- Replay hash: `c690c91f7121ea10bf5324b702c735d9e421271efaba6e6ad4c4496e84181451`
- Kernel profile: `cog_v2_projective_unity_v1`
- Projector: `pi_unity_axis_dominance_v1`
- Contract pass: `True`

## Graph Contract
- node_count: `7`
- edge_count: `10`
- black_hole_region: `['c0', 'c1', 'h0', 'h1']`
- exterior_region: `['o0', 'o1', 'o2']`
- horizon_nodes: `['h0', 'h1']`

## Falsification Tests
- T1 one-way isolation: pass=`True` crossing_edge_count=`0`
- T2 horizon ingress: pass=`True` horizon_count=`2`
- T3 exterior independence: pass=`True`
- T4 exterior->interior influence: pass=`True`
- T5 unity boundedness: pass=`True`

## Summary
- Black-hole region is defined as one-way topological sink (no outgoing edges).
- Horizon is ingress boundary from exterior into sink.
- Projection-kernel witness shows exterior independence from interior initialization.
- Unity closure remains bounded for all ticks under dense interior update flow.

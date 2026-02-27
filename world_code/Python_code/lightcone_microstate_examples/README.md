# lightcone_microstate_examples

A collection of ready-to-run full lightcone microstates in the minimal kernel format.

Each JSON file contains:
1. `node_ids`
2. `parents`
3. `init_state`

Run any file with:

```bash
python world_code/Python_code/minimal_world_kernel.py \
  --input world_code/Python_code/lightcone_microstate_examples/<file>.json \
  --steps 4 \
  --output world_code/Python_code/lightcone_microstate_examples/<file>.out.json
```

Notes:
1. These are deterministic starter configurations.
2. Names like `electron`/`proton` are motif labels for experimentation.
3. No observable logic is baked into these inputs.


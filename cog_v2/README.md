# COG v2 (Canonical Axiom Workspace)

`cog_v2/` is a clean-room workspace for the canonical axiom profile:

1. Universe is a DAG.
2. Node states are `C x O` over a unity alphabet.
3. Update rule is projection across the incoming light cone.
4. Basis channels are binary-labeled: `e000..e111`.
5. Runtime multiplication uses XOR index channel with oriented sign table.

This directory is intentionally isolated from legacy kernels and legacy claim plumbing.

## Layout

- `rfc/`: v2 canonical and migration RFCs.
- `python/`: reference kernel and deterministic tests.
- `lean/`: proof lane for canonical algebraic theorems.
- `claims/`: v2 claim stubs and gate tracking.
- `migration/`: source-to-v2 migration manifest.
- `scripts/`: support scripts and playbooks.

## Quickstart

Python tests:

```powershell
pytest cog_v2/python/tests/test_kernel_projective_unity.py `
  cog_v2/calc/test_theta001_cp_invariant_v2.py `
  cog_v2/calc/test_theta001_bridge_closure_v2.py -q
```

Run kernel:

```powershell
python cog_v2/python/kernel_projective_unity.py `
  --input cog_v2/python/lightcone_example.json `
  --steps 4 `
  --output cog_v2/python/out_example.json
```

Build THETA bridge artifact:

```powershell
python -m cog_v2.calc.build_theta001_bridge_closure_v2 --write-sources
```

Validate v2 claims:

```powershell
python cog_v2/scripts/validate_claim_contracts_v2.py --root . --claims-dir cog_v2/claims
```

Lean lane:

```powershell
cd cog_v2/lean
lake build
```

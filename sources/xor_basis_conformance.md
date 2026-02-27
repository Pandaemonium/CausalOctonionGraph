# XOR Basis Conformance (XCALC)

Status: active scaffold artifact  
Primary code: `calc/xor_basis_conformance.py`  
Build script: `scripts/build_xor_basis_conformance.py`

## Scope
1. Exhaustive `8 x 8` basis-product audit for `e_i * e_j` using XOR gate path.
2. Canonical-table parity check against locked Fano sign/third maps.
3. Handedness alignment check (`LEFT`/`RIGHT` operator application semantics).
4. Distinct-imag anti-commutation check.
5. Deterministic table hash for regression gating.

## Artifacts
1. `calc/xor_basis_conformance.json`
2. `calc/xor_basis_conformance.csv`
3. `website/data/xor_basis_conformance.json`
4. `website/data/xor_basis_conformance.csv`

## Not Claimed
1. This artifact does not calibrate to SI units.
2. This artifact does not prove physical constants.
3. This artifact is algebraic conformance only.

## Extension Clues
1. Add a CI gate that blocks merges if `table_sha256` changes unexpectedly.
2. Add a Lean-to-Python cross-check artifact if a serialized Lean basis table is available.
3. Add higher-order associator conformance checks for selected triples.


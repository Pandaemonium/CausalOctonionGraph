# HYDROGEN-001 Gate 1 Corrected Task Prompt

Status: Ready to Assign  
Claim: `HYDROGEN-001`  
Purpose: Replace drifted task wording with a source-of-truth aligned Gate 1 scaffold.

## 1. Why This Correction Exists

The previous prompt mixed valid scaffold ideas with invalid or unproven assumptions.

This corrected prompt enforces:
1. canonical Fano cycles from `rfc/CONVENTIONS.md`,
2. clear separation between proved structure vs hypothesis,
3. no unsupported charge or degeneracy assertions in Gate 1.

## 2. Locked Conventions (Do Not Deviate)

Use `rfc/CONVENTIONS.md` as source of truth.

Canonical one-indexed directed cycles:
1. `(1,2,3)`
2. `(1,4,5)`
3. `(1,7,6)`
4. `(2,4,6)`
5. `(2,5,7)`
6. `(3,4,7)`
7. `(3,6,5)`

In Python, use existing shared constants from `calc/conftest.py` (`FANO_CYCLES`, `FANO_SIGN`, `FANO_THIRD`).  
Do not redefine a custom multiplication table inside the test file.

## 3. Motif Contract for Gate 1

Gate 1 only closes a **structural scaffold**.

1. Electron motif (structural): `{e1,e2,e3}` (associative line / quaternionic subalgebra witness).
2. Proton-proto motif (hypothesis): `{e1,e2,e4}` (non-collinear triad used in existing overhead scaffolds).

Important:
1. Do not claim this triad is a fully closed proton model.
2. Do not claim physical energy levels or degeneracy from Gate 1.
3. Do not use index-parity as the charge law.

## 4. Assignment

Create:
1. `calc/hydrogen_binding.py`
2. `calc/test_hydrogen001_binding.py`
3. `claims/HYDROGEN-001.yml` (if missing)

## 5. Required Python API (`calc/hydrogen_binding.py`)

Provide these definitions:

1. `ELECTRON_MOTIF = frozenset({1, 2, 3})`
2. `PROTON_PROTO_MOTIF = frozenset({1, 2, 4})`
3. `motif_overlap(m1, m2) -> int`
4. `is_collinear_triad(motif, fano_cycles) -> bool`
5. `shared_pair(m1, m2) -> frozenset[int]`
6. `line_through_pair(pair, fano_cycles) -> tuple[int, int, int] | None`
7. `binding_proxy(shared_line_count: int) -> Fraction` where denominator is 7
8. `classify_motif(motif, fano_cycles) -> str` returning `associative_line` or `noncollinear_triad`

Implementation notes:
1. Keep one-indexed motif labels in this module (`1..7`) for readability.
2. Convert to zero-indexed only when using `calc/conftest.py` tables.
3. Use exact arithmetic (`fractions.Fraction`) for proxies.

## 6. Required Tests (`calc/test_hydrogen001_binding.py`)

Add exactly these 8 tests:

1. `test_fano_cycles_match_locked_conventions()`
2. `test_electron_motif_is_collinear_associative()`
3. `test_proton_proto_motif_is_noncollinear()`
4. `test_motif_overlap_is_two_points()`  (`{e1,e2}`)
5. `test_unique_line_through_shared_pair_is_l1()`  (line is `{e1,e2,e3}`)
6. `test_binding_proxy_positive_and_less_than_one()`
7. `test_motif_classification_is_deterministic()`
8. `test_hydrogen_claim_yaml_exists_and_partial()`

## 7. Claim File Requirements (`claims/HYDROGEN-001.yml`)

Minimum required fields:
1. `id: HYDROGEN-001`
2. `title`
3. `status: partial`
4. `python_test: calc/test_hydrogen001_binding.py`
5. `gates` with gate 1 marked passed after tests pass
6. `notes` including:
   - structural-only closure scope for Gate 1
   - explicit statement that proton motif is provisional
   - explicit "not claimed" boundary

Example "not claimed" note (required):
- "Gate 1 does not claim a full proton internal state, physical hydrogen spectrum, or calibrated binding energy."

## 8. Explicitly Forbidden in Gate 1

Do not include any of the following as closed results:
1. the non-canonical 7-cycle list `(1,2,4), (2,3,5), ...` (wrong for this repo),
2. proton charge `+1` derived from index sums mod 2,
3. ground-state degeneracy `= 4` as a proved output,
4. final mass-ratio closure claims.

## 9. Verification Commands

Run:

1. `python -m pytest calc/test_hydrogen001_binding.py -v`
2. `python -m pytest calc/ -q`

Success criteria:
1. all 8 hydrogen tests pass,
2. no regressions in broader `calc/` suite.

## 10. Promotion Scope

Gate 1 promotion target:
1. `HYDROGEN-001: stub -> partial` (or initialize directly as `partial` with Gate 1 closed)

Out of scope for Gate 1:
1. Lean theorem closure for hydrogen,
2. full two-body scattering kinematics,
3. physical calibration to spectroscopic observables.

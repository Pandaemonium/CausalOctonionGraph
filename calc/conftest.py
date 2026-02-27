import json
import pathlib

# Path to the oracle output
ORACLE_PATH = pathlib.Path(__file__).parent / "lean_outputs.json"

LEAN_DATA = {}
FANO_CYCLES = []

if ORACLE_PATH.exists():
    with open(ORACLE_PATH, "r") as f:
        LEAN_DATA = json.load(f)
    
    # Load Fano cycles from JSON
    # JSON structure: {"fano": {"cycles": [[0,1,2], ...]}}
    if "fano" in LEAN_DATA and "cycles" in LEAN_DATA["fano"]:
        raw_cycles = LEAN_DATA["fano"]["cycles"]
        FANO_CYCLES = [tuple(c) for c in raw_cycles]

if not FANO_CYCLES:
    # Fallback if JSON missing or invalid
    # rfc/CONVENTIONS.md §2 and §7
    # 0-indexed Fano lines (mapping to physics indices 1-7)
    FANO_CYCLES = [
        (0, 1, 2),  # (1,2,3)
        (0, 3, 4),  # (1,4,5)
        (0, 6, 5),  # (1,7,6)
        (1, 3, 5),  # (2,4,6)
        (1, 4, 6),  # (2,5,7)
        (2, 3, 6),  # (3,4,7)
        (2, 5, 4),  # (3,6,5)
    ]

# rfc/CONVENTIONS.md §2
# FANO_SIGN[(i,j)] = ±1  for e_{i+1} * e_{j+1}   (0-indexed imaginary units)
# FANO_THIRD[(i,j)] = k  where e_{i+1} * e_{j+1} = ±e_{k+1}
FANO_SIGN: dict[tuple[int, int], int] = {}
FANO_THIRD: dict[tuple[int, int], int] = {}
for _a, _b, _c in FANO_CYCLES:
    # Cyclic:      a*b=+c,  b*c=+a,  c*a=+b
    FANO_SIGN[(_a, _b)] = +1;  FANO_THIRD[(_a, _b)] = _c
    FANO_SIGN[(_b, _c)] = +1;  FANO_THIRD[(_b, _c)] = _a
    FANO_SIGN[(_c, _a)] = +1;  FANO_THIRD[(_c, _a)] = _b
    # Anti-cyclic: b*a=-c,  c*b=-a,  a*c=-b
    FANO_SIGN[(_b, _a)] = -1;  FANO_THIRD[(_b, _a)] = _c
    FANO_SIGN[(_c, _b)] = -1;  FANO_THIRD[(_c, _b)] = _a
    FANO_SIGN[(_a, _c)] = -1;  FANO_THIRD[(_a, _c)] = _b

# rfc/CONVENTIONS.md §5.2
# Witt basis pairs (0-indexed): (e_a, e_b) for color directions j = 1,2,3.
# Physics pairs: (e₆, e₁), (e₂, e₅), (e₃, e₄)  →  0-indexed: (5,0), (1,4), (2,3)
WITT_PAIRS: list[tuple[int, int]] = [
    (5, 0),  # Color 1: (e₆, e₁)  — Fano line (0,6,5) / physics L3 (1,7,6)
    (1, 4),  # Color 2: (e₂, e₅)  — Fano line (1,4,6) / physics L5 (2,5,7)
    (2, 3),  # Color 3: (e₃, e₄)  — Fano line (2,3,6) / physics L6 (3,4,7)
]

# rfc/CONVENTIONS.md §5.1
# Vacuum axis: 0-indexed Fano point for e₇ (symmetry-breaking axis)
VACUUM_AXIS: int = 6  # e₇ ↔ 0-indexed point 6

"""calc/gluon_assignment.py

Resolves RFC-001 §5.1: Gluon Assignment Table.

For each of the three SU(3) color exchanges, this script tests all candidate
gluon operators (the complement of the two Witt pairs) for associativity.

A gluon candidate g for exchange Color i ↔ j is evaluated by checking
triggers(s_src, g, s_dst) for all four combinations of
(s_src ∈ Witt_pair_i, s_dst ∈ Witt_pair_j).

Output: a table showing which gluon → (src, dst) pairs fire the
Alternativity Trigger (non-associative = extra ticks in the DAG).

Also verifies that each non-vacuum gluon correctly "routes" source Witt-pair
states to destination Witt-pair states under left-multiplication (i.e.,
e_src * e_gluon lies in the destination Witt pair).
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from conftest import FANO_CYCLES, FANO_SIGN, FANO_THIRD, WITT_PAIRS, VACUUM_AXIS

# ── Build lookup: frozenset of 3 indices → True if Fano collinear ───────────
FANO_TRIPLE_SET: set[frozenset] = set()
for _a, _b, _c in FANO_CYCLES:
    FANO_TRIPLE_SET.add(frozenset({_a, _b, _c}))


def is_fano_collinear(a: int, g: int, b: int) -> bool:
    """Return True if {a, g, b} is one of the 7 Fano lines (associative)."""
    if len({a, g, b}) < 3:
        return False  # repeated index: a²b or ab² — always associative
    return frozenset({a, g, b}) in FANO_TRIPLE_SET


def triggers(a: int, g: int, b: int) -> bool:
    """Return True if the Alternativity Trigger fires (non-associative product)."""
    return not is_fano_collinear(a, g, b)


def left_product(i: int, j: int) -> tuple[int, int]:
    """Compute e_i * e_j → (sign, result_index). i,j are 0-indexed imaginary units."""
    if i == j:
        return (-1, -1)   # e_i² = -1 (real part, no imaginary index)
    sign = FANO_SIGN[(i, j)]
    idx  = FANO_THIRD[(i, j)]
    return (sign, idx)


def phys(idx: int) -> str:
    """Return physics label e_{idx+1} for a 0-indexed imaginary unit."""
    return f"e{idx+1}"


# ── Witt pair bookkeeping ────────────────────────────────────────────────────
# WITT_PAIRS from conftest: [(5,0), (1,4), (2,3)]  (0-indexed)
# Color 1: {e6, e1} = {5, 0}
# Color 2: {e2, e5} = {1, 4}
# Color 3: {e3, e4} = {2, 3}
# Vacuum axis: 6 = e7

ALL_7 = set(range(7))

EXCHANGES = [
    ("Color 1 ↔ 2", 0, 1),
    ("Color 1 ↔ 3", 0, 2),
    ("Color 2 ↔ 3", 1, 2),
]

print("=" * 68)
print("GLUON ASSIGNMENT TABLE  —  RFC-001 §5.1")
print("=" * 68)

results: dict = {}

for name, pi, pj in EXCHANGES:
    pair_i = set(WITT_PAIRS[pi])   # source Witt pair
    pair_j = set(WITT_PAIRS[pj])   # destination Witt pair

    # Gluon candidates = everything outside both pairs.
    # We test the non-vacuum complement AND the vacuum axis separately.
    non_vacuum_complement = ALL_7 - pair_i - pair_j - {VACUUM_AXIS}
    all_candidates = ALL_7 - pair_i - pair_j   # includes vacuum

    print(f"\n{'-'*68}")
    print(f"  {name}")
    print(f"  Witt pair {pi+1} (src): {{ {', '.join(phys(x) for x in sorted(pair_i))} }}")
    print(f"  Witt pair {pj+1} (dst): {{ {', '.join(phys(x) for x in sorted(pair_j))} }}")
    print(f"  Non-vacuum candidates:  {{ {', '.join(phys(x) for x in sorted(non_vacuum_complement))} }}")
    print(f"  Vacuum axis tested too: {phys(VACUUM_AXIS)}")
    print()

    exchange_data: dict = {}

    for g in sorted(all_candidates):
        g_label = phys(g)
        rows = []
        for src in sorted(pair_i):
            for dst in sorted(pair_j):
                t = triggers(src, g, dst)
                # Also compute what e_src * e_gluon actually gives
                s_left, s_left_idx = left_product(src, g)
                route_label = (
                    f"{'+' if s_left > 0 else '-'}{phys(s_left_idx)}"
                    if s_left_idx >= 0 else "-1(real)"
                )
                in_dst_pair = (s_left_idx in pair_j) if s_left_idx >= 0 else False
                rows.append((src, g, dst, t, route_label, in_dst_pair))

        all_t  = all(r[3] for r in rows)
        none_t = not any(r[3] for r in rows)
        n_trigger = sum(r[3] for r in rows)
        is_vacuum = (g == VACUUM_AXIS)

        tag = ""
        if is_vacuum:
            tag = "  ← VACUUM AXIS"
        elif all_t:
            tag = "  ← ALL NON-ASSOC  ✓ (preferred)"
        elif none_t:
            tag = "  ← ALL ASSOC  (no branching)"
        else:
            tag = f"  ← MIXED ({n_trigger}/4 non-assoc)"

        # Check routing: does e_src * e_gluon land in the destination Witt pair?
        routing_ok = all(r[5] for r in rows)
        routing_tag = "  [routes correctly]" if routing_ok else "  [does NOT route to dst pair]"

        print(f"  Gluon {g_label}:{tag}{routing_tag}")
        for src, g_, dst, t, route, in_pair in rows:
            assoc_str = "NON-ASSOC ✓" if t else "  assoc   "
            pair_str  = "→ dst pair ✓" if in_pair else "→ dst pair ✗"
            print(f"    triggers({phys(src)}, {g_label}, {phys(dst)}) = {assoc_str}  "
                  f"|  {phys(src)}·{g_label} = {route} {pair_str}")
        print()

        exchange_data[g] = {
            "all_trigger": all_t,
            "none_trigger": none_t,
            "n_trigger": n_trigger,
            "routes_correctly": routing_ok,
            "is_vacuum": is_vacuum,
            "rows": rows,
        }

    results[(pi, pj)] = exchange_data

# ── Summary table ────────────────────────────────────────────────────────────
print("=" * 68)
print("SUMMARY")
print("=" * 68)
print()
print("  For each exchange, a gluon is 'preferred' if:")
print("  (a) triggers on ALL 4 (src,dst) combinations  [maximises branching]")
print("  (b) e_src * e_gluon correctly routes to the destination Witt pair")
print()

for name, pi, pj in EXCHANGES:
    print(f"  {name}:")
    for g, d in sorted(results[(pi, pj)].items()):
        preferred = d["all_trigger"] and d["routes_correctly"] and not d["is_vacuum"]
        good_route = d["routes_correctly"] and not d["is_vacuum"]
        marker = "  PREFERRED" if preferred else ("  routes OK, mixed trigger" if good_route else "")
        print(f"    {phys(g)}: all_trigger={d['all_trigger']}, "
              f"routes_correctly={d['routes_correctly']}, "
              f"vacuum={d['is_vacuum']}{marker}")
    print()

print("=" * 68)
print("RECOMMENDED GLUON ASSIGNMENT TABLE")
print("=" * 68)
print()
for name, pi, pj in EXCHANGES:
    preferred = [
        g for g, d in results[(pi, pj)].items()
        if d["all_trigger"] and d["routes_correctly"] and not d["is_vacuum"]
    ]
    routing_only = [
        g for g, d in results[(pi, pj)].items()
        if not d["all_trigger"] and d["routes_correctly"] and not d["is_vacuum"]
    ]
    if preferred:
        print(f"  {name}:  g = {{{', '.join(phys(g) for g in sorted(preferred))}}}  "
              f"[all-trigger, correct routing]")
    elif routing_only:
        print(f"  {name}:  g = {{{', '.join(phys(g) for g in sorted(routing_only))}}}  "
              f"[correct routing, mixed trigger — both needed]")
    else:
        print(f"  {name}:  NO clean candidate found.")
print()
print(f"  Vacuum axis {phys(VACUUM_AXIS)}: triggers ALL exchanges but is the U(1)/photon")
print(f"  direction, not an SU(3) color gluon.")

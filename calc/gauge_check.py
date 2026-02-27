"""
calc/gauge_check.py
Phase 4.1: Numerical validation of the discrete gauge group

Computationally cross-checks all four theorems from GaugeGroup.lean:
  1. |Aut(PG(2,2))| = 168  (fano_aut_count)
  2. |Stab(e₇)| = 24       (vacuum_stabilizer_count)
  3. 3 lines through e₇    (vacuum_lines_count)
  4. 7 × 24 = 168           (orbit_stabilizer_check)

Then examines the group structure:
  5. Transitive action: the orbit of every point has size 7
  6. Stabilizer action on Witt pairs: which permutations of the 3 color
     planes are induced by the 24-element vacuum stabilizer

All computations use only FANO_CYCLES, WITT_PAIRS, VACUUM_AXIS from
conftest.py (the locked convention source).
"""

from itertools import permutations
from collections import defaultdict
from calc.conftest import FANO_CYCLES, WITT_PAIRS, VACUUM_AXIS
from calc.fano import incident, fano_line_points

# ──────────────────────────────────────────────────────────────────────────────
# Core helpers
# ──────────────────────────────────────────────────────────────────────────────

def apply_perm(sigma: list[int], p: int) -> int:
    """Apply permutation σ (length-7 list) to Fano point p."""
    return sigma[p]


def is_fano_aut(sigma: list[int]) -> bool:
    """
    Check whether σ is a Fano automorphism:
    every line maps to a line under σ.

    σ must be a permutation of [0..6] (length 7).
    """
    for line_idx in range(7):
        pts = fano_line_points(line_idx)          # 3 points on this line
        img = [apply_perm(sigma, p) for p in pts]  # their images
        # Check if all 3 images lie on some line
        ok = False
        for l2 in range(7):
            pts2 = fano_line_points(l2)
            if all(q in pts2 for q in img):
                ok = True
                break
        if not ok:
            return False
    return True


def fixes_vacuum(sigma: list[int]) -> bool:
    """Check whether σ fixes the vacuum axis VACUUM_AXIS."""
    return sigma[VACUUM_AXIS] == VACUUM_AXIS


def all_fano_auts() -> list[list[int]]:
    """Enumerate all 168 Fano automorphisms by brute force over 7! = 5040 permutations."""
    return [list(p) for p in permutations(range(7)) if is_fano_aut(list(p))]


# ──────────────────────────────────────────────────────────────────────────────
# Main group computations
# ──────────────────────────────────────────────────────────────────────────────

def count_fano_auts(auts: list[list[int]]) -> int:
    """Return |Aut(PG(2,2))|."""
    return len(auts)


def vacuum_stabilizer(auts: list[list[int]]) -> list[list[int]]:
    """Return the subgroup of auts that fix VACUUM_AXIS."""
    return [s for s in auts if fixes_vacuum(s)]


def vacuum_lines() -> list[int]:
    """Return the indices of Fano lines through VACUUM_AXIS."""
    return [l for l in range(7) if incident(VACUUM_AXIS, l)]


def orbit_of(auts: list[list[int]], point: int) -> set[int]:
    """Return the orbit of `point` under the automorphism group."""
    return {apply_perm(sigma, point) for sigma in auts}


# ──────────────────────────────────────────────────────────────────────────────
# Witt pair analysis
# ──────────────────────────────────────────────────────────────────────────────

def witt_pair_action(stab: list[list[int]]) -> list[tuple[int, int, int]]:
    """
    Determine how each element of the vacuum stabilizer permutes the 3 Witt pairs.

    WITT_PAIRS = [(e_a, e_b) for each color j=1,2,3].
    A stabilizer element σ (which fixes e₇) maps each pair (e_a, e_b) to
    some other pair (e_{σ(a)}, e_{σ(b)}).  We record the resulting permutation
    of {0,1,2} (color indices).

    Returns a list of permutations-of-colors, one per stabilizer element.
    Each entry is a 3-tuple (c₀, c₁, c₂) meaning color j maps to color cⱼ.
    """
    results = []
    pair_to_color = {}
    for j, (a, b) in enumerate(WITT_PAIRS):
        pair_to_color[frozenset({a, b})] = j

    for sigma in stab:
        perm = []
        for a, b in WITT_PAIRS:
            sa, sb = sigma[a], sigma[b]
            img_set = frozenset({sa, sb})
            color = pair_to_color.get(img_set)
            perm.append(color)  # None if the image isn't a Witt pair
        results.append(tuple(perm))
    return results


def color_permutation_group(stab: list[list[int]]) -> set[tuple[int, int, int]]:
    """
    Return the group of color permutations induced by the vacuum stabilizer.
    Should be S₃ (all 6 permutations of 3 colors) or a subgroup.
    """
    return set(witt_pair_action(stab))


# ──────────────────────────────────────────────────────────────────────────────
# Composition and order utilities
# ──────────────────────────────────────────────────────────────────────────────

def compose(sigma: list[int], tau: list[int]) -> list[int]:
    """Compose permutations: (σ ∘ τ)(x) = σ(τ(x))."""
    return [sigma[tau[x]] for x in range(7)]


def perm_order(sigma: list[int]) -> int:
    """Compute the order of σ in the symmetric group S₇."""
    current = list(range(7))
    for k in range(1, 421):  # lcm(1..7) = 420
        current = [current[sigma[x]] for x in range(7)]
        if current == list(range(7)):
            return k
    return -1  # should not happen


def order_histogram(group: list[list[int]]) -> dict[int, int]:
    """Return a histogram of element orders within the group."""
    hist: dict[int, int] = defaultdict(int)
    for sigma in group:
        hist[perm_order(sigma)] += 1
    return dict(hist)


# ──────────────────────────────────────────────────────────────────────────────
# Diagnostic summary
# ──────────────────────────────────────────────────────────────────────────────

def summary() -> None:
    print("Gauge Group Check (cross-validates GaugeGroup.lean)")
    print("=" * 60)

    auts = all_fano_auts()
    stab = vacuum_stabilizer(auts)
    vlines = vacuum_lines()

    # ── Theorem 1: fano_aut_count ──────────────────────────────────
    print(f"\n1. |Aut(PG(2,2))|     = {len(auts)}  (expected 168)")
    assert len(auts) == 168, f"FAIL: got {len(auts)}"

    # ── Theorem 2: vacuum_stabilizer_count ────────────────────────
    print(f"2. |Stab(e7)|         = {len(stab)}   (expected 24)")
    assert len(stab) == 24, f"FAIL: got {len(stab)}"

    # ── Theorem 3: vacuum_lines_count ─────────────────────────────
    print(f"3. Lines through e7   = {len(vlines)}    (expected 3)")
    assert len(vlines) == 3, f"FAIL: got {len(vlines)}"
    print(f"   Line indices: {vlines}")
    for l in vlines:
        print(f"   Line {l}: {fano_line_points(l)} (physics {[p+1 for p in fano_line_points(l)]})")

    # ── Theorem 4: orbit_stabilizer_check ─────────────────────────
    print(f"\n4. Orbit-stabilizer:  7 x 24 = {7 * 24}  (expected 168)")
    assert 7 * 24 == 168

    # ── Extra: transitive action ───────────────────────────────────
    print("\n5. Orbit sizes (all points should have orbit = 7):")
    for p in range(7):
        orb = orbit_of(auts, p)
        print(f"   orbit({p}) = {sorted(orb)}  (size {len(orb)})")
        assert len(orb) == 7, f"FAIL: orbit of {p} has size {len(orb)}"
    print("   Aut(PG(2,2)) acts transitively on all 7 points PASS")

    # ── Extra: Witt pair permutations ─────────────────────────────
    print(f"\n6. Witt pair permutations induced by Stab(e7):")
    print(f"   Witt pairs: {WITT_PAIRS} (0-indexed, physics pairs)")
    color_perms = color_permutation_group(stab)
    print(f"   Induced color permutations: {len(color_perms)} distinct")
    print(f"   {sorted(color_perms)}")
    # The stabilizer should induce all 6 permutations of 3 colors (= S3)
    assert len(color_perms) == 6, (
        f"Expected S3 (6 permutations), got {len(color_perms)}: {sorted(color_perms)}"
    )
    print("   PASS: Vacuum stabilizer induces S3 on the 3 color planes")

    # ── Extra: element order histogram ────────────────────────────
    print(f"\n7. Element order histogram for Aut(PG(2,2)):")
    hist_full = order_histogram(auts)
    for order in sorted(hist_full):
        print(f"   order {order}: {hist_full[order]} elements")

    print(f"\n8. Element order histogram for Stab(e7):")
    hist_stab = order_histogram(stab)
    for order in sorted(hist_stab):
        print(f"   order {order}: {hist_stab[order]} elements")

    print("\nAll checks passed.")


if __name__ == "__main__":
    summary()

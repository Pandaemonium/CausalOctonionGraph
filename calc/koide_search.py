"""O(n^2) Diophantine search for Koide-ratio triples.

Exact Q=2/3 solution for fixed f1, f2: f3 = (f1+f2) +/- 2*sqrt(f1*f2)
(derived by solving (f1+f2+f3)^2 / (3*(f1^2+f2^2+f3^2)) = 2/3 for f3).
"""
import math

from calc.conftest import FANO_SIGN, FANO_THIRD


def koide_ratio(f1: int, f2: int, f3: int) -> float:
    """Koide ratio Q = (f1+f2+f3)^2 / (3*(f1^2+f2^2+f3^2))."""
    return (f1 + f2 + f3) ** 2 / (3 * (f1 ** 2 + f2 ** 2 + f3 ** 2))


def search_triples(n_max: int = 4000, target: float = 2/3, tol: float = 1e-4) -> list:
    """O(n^2) search using analytical reduction.

    Returns list of ((f1, f2, f3), ratio) pairs sorted by |ratio - target|.
    """
    results = []
    seen: set = set()
    for f1 in range(1, n_max + 1):
        sq1 = math.sqrt(f1)
        for f2 in range(f1, n_max + 1):
            sq2 = math.sqrt(f2)
            cross = sq1 * sq2
            for sign in (+1, -1):
                f3_exact = (f1 + f2) + sign * 2.0 * cross
                for f3 in {max(1, round(f3_exact)), max(1, int(f3_exact))}:
                    if f3 > n_max:
                        continue
                    ratio = koide_ratio(f1, f2, f3)
                    if abs(ratio - target) < tol:
                        triple = tuple(sorted([f1, f2, f3]))
                        if triple not in seen:
                            seen.add(triple)
                            results.append((triple, ratio))
    results.sort(key=lambda x: abs(x[1] - target))
    return results[:20]


if __name__ == '__main__':
    top_results = search_triples()
    for triple, ratio in top_results[:5]:
        print(f'{triple}: ratio={ratio}')
# Signed-by: Evelyn Carter

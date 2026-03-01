import pytest
from calc.koide_search import koide_ratio, search_triples
from calc.conftest import FANO_SIGN, FANO_THIRD


def test_koide_ratio_formula():
    # koide_ratio(1,1,1) = 9/9 = 1.0  (NOT 1/3 -- that is the limiting value when one term dominates)
    assert koide_ratio(1, 1, 1) == pytest.approx(1.0, rel=1e-9)
    assert koide_ratio(1, 2, 3) == pytest.approx(36/42, rel=1e-9)


def test_search_returns_results():
    results = search_triples(n_max=4000)
    assert len(results) >= 5


def test_top5_triples_match_target():
    results = search_triples(n_max=4000)
    for triple, ratio in results[:5]:
        f1, f2, f3 = triple
        assert abs(koide_ratio(f1, f2, f3) - 2/3) < 1e-4


def test_fano_imports():
    assert FANO_SIGN is not None
    assert FANO_THIRD is not None
# Signed-by: Evelyn Carter

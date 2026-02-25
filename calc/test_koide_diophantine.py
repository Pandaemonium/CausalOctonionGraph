import itertools
import pytest
from calc.conftest import FANO_CYCLES

def satisfies_brannen_koide_relation(f0, f1, f2):
    return f0 ** 2 + f1 ** 2 + f2 ** 2 == 4 * (f0 * f1 + f1 * f2 + f2 * f0)

def is_valid_fano_cycle(triple):
    for cycle in FANO_CYCLES:
        if set(cycle) <= set(triple):
            return True
    return False

def find_smallest_koide_triple():
    for f0, f1, f2 in itertools.combinations(range(1, 1001), 3):
        if is_valid_fano_cycle((f0, f1, f2)) and satisfies_brannen_koide_relation(f0, f1, f2):
            return f0, f1, f2
    return None

def test_koide_relation():
    result = find_smallest_koide_triple()
    if result:
        print(f"Smallest triple found: {result}")
    else:
        print("No solution found.")
    
    assert result is not None, "At least one satisfying triple must exist."

if __name__ == "__main__":
    pytest.main([__file__])
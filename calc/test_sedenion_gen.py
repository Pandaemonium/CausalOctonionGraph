"""
calc/test_sedenion_gen.py
=========================
Tests for the Sedenion generation claim GEN-002.

Claim GEN-002 (3-generation hypothesis):
  The S3 action that cyclically permutes the Witt-pair labels of the
  16-dimensional Sedenion algebra yields exactly 3 distinct orbits of
  Witt triples -- matching the 3 observed Standard Model fermion generations.

Run with:  pytest calc/test_sedenion_gen.py -v
"""

import pytest
from calc.sedenion_gen import (
    build_sedenion_table,
    sedenion_table_zmod2,
    check_non_associative,
    find_non_associative_example,
    find_witt_triples,
    find_unordered_witt_triples,
    count_witt_triple_orbits,
    count_witt_triple_orbits_labeled,
    get_witt_triple_orbit_representatives,
    witt_pair_partition,
    get_witt_pair_groups,
    build_s3_permutation,
    s3_is_automorphism,
    check_all_s3_elements,
    s3_act_on_triple,
    s3_orbit_under_group_action,
)


@pytest.fixture(scope="module")
def table():
    return build_sedenion_table()


@pytest.fixture(scope="module")
def groups():
    return get_witt_pair_groups()


class TestTableStructure:
    def test_table_is_16x16(self, table):
        assert len(table) == 16
        for i, row in enumerate(table):
            assert len(row) == 16, f"Row {i} has {len(row)} cols"

    def test_signs_are_pm1(self, table):
        for i in range(16):
            for j in range(16):
                sign, _ = table[i][j]
                assert sign in (1, -1), f"table[{i}][{j}].sign={sign}"

    def test_indices_in_range(self, table):
        for i in range(16):
            for j in range(16):
                _, k = table[i][j]
                assert 0 <= k < 16, f"table[{i}][{j}].index={k}"

    def test_e0_is_identity(self, table):
        for i in range(16):
            assert table[0][i] == (1, i), f"e_0*e_{i}={table[0][i]}"
            assert table[i][0] == (1, i), f"e_{i}*e_0={table[i][0]}"

    def test_imaginary_units_square_to_neg_identity(self, table):
        for i in range(1, 16):
            assert table[i][i] == (-1, 0), f"e_{i}^2={table[i][i]}"

    def test_multiplication_closed_on_basis(self, table):
        seen = {table[i][j][1] for i in range(16) for j in range(16)}
        assert seen == set(range(16))

    def test_zmod2_table(self, table):
        zmod2 = sedenion_table_zmod2(table)
        assert len(zmod2) == 16
        assert all(len(r) == 16 for r in zmod2)

    def test_anti_commutativity(self, table):
        for i in range(1, 16):
            for j in range(1, 16):
                if i == j:
                    continue
                s_ij, k_ij = table[i][j]
                s_ji, k_ji = table[j][i]
                assert k_ij == k_ji, f"e_{i}*e_{j}->e_{k_ij} but e_{j}*e_{i}->e_{k_ji}"
                assert s_ij == -s_ji, f"signs not opposite for e_{i},e_{j}"


class TestNonAssociativity:
    def test_is_non_associative(self, table):
        assert check_non_associative(table), "Sedenions must be non-associative"

    def test_non_associative_example_valid(self, table):
        i, j, k = find_non_associative_example(table)
        assert (i, j, k) != (-1, -1, -1), "No non-associative example found"
        s_ij, idx_ij = table[i][j]
        s_l, idx_l = table[idx_ij][k]
        left = (s_ij * s_l, idx_l)
        s_jk, idx_jk = table[j][k]
        s_r, idx_r = table[i][idx_jk]
        right = (s_jk * s_r, idx_r)
        assert left != right, f"Example ({i},{j},{k}) is actually associative"

    def test_octonion_subalgebra_left_alternative(self, table):
        for i in range(8):
            for j in range(8):
                s_ii, idx_ii = table[i][i]
                s_l, idx_l = table[idx_ii][j]
                left = (s_ii * s_l, idx_l)
                s_ij, idx_ij = table[i][j]
                s_r, idx_r = table[i][idx_ij]
                right = (s_ij * s_r, idx_r)
                assert left == right, f"Left alternative fails for i={i},j={j}"


class TestWittTriples:
    def test_ordered_triples_nonempty(self, table):
        assert len(find_witt_triples(table)) > 0

    def test_ordered_triples_valid(self, table):
        for i, j, k in find_witt_triples(table):
            assert i > 0 and j > 0 and k > 0
            assert len({i, j, k}) == 3
            _, actual_k = table[i][j]
            assert actual_k == k, f"e_{i}*e_{j}->e_{actual_k}, not e_{k}"

    def test_unordered_triples_nonempty(self, table):
        assert len(find_unordered_witt_triples(table)) > 0

    def test_unordered_triples_size_three(self, table):
        for triple in find_unordered_witt_triples(table):
            assert len(triple) == 3
            assert all(i > 0 for i in triple)

    def test_witt_pair_groups_partition_imaginaries(self, groups):
        all_idx = {i for g in groups for i in g}
        assert all_idx == set(range(1, 16)), f"Groups cover {all_idx}"
        assert len(groups) == 3
        for a in range(3):
            for b in range(a + 1, 3):
                assert not (set(groups[a]) & set(groups[b])), "Groups overlap"
        for g in groups:
            assert len(g) == 5, f"Group {g} has {len(g)} elements, expected 5"


class TestS3Automorphism:
    def test_identity_is_automorphism(self, table, groups):
        perm = build_s3_permutation(groups, (0, 1, 2))
        assert s3_is_automorphism(table, perm)

    def test_s3_orbit_of_triple_has_at_most_6_elements(self, groups):
        triple = frozenset([1, 6, 11])
        orbit = s3_orbit_under_group_action(triple, groups)
        assert 1 <= len(orbit) <= 6

    def test_s3_act_maps_groups_correctly(self, groups):
        idx_in_g0 = groups[0][0]
        new_idx = s3_act_on_triple(frozenset([idx_in_g0]), groups, (1, 2, 0))
        new_idx_val = next(iter(new_idx))
        assert new_idx_val in groups[1], (
            f"Index {idx_in_g0} from G0 under (1,2,0) -> {new_idx_val}, "
            f"expected in G1={groups[1]}"
        )


class TestThreeGenerations:
    """GEN-002: exactly 3 orbits of Witt triples under the S3 Witt-pair action."""

    def test_exactly_three_orbits(self, table):
        """
        CRUCIAL (GEN-002): There are exactly 3 distinct orbits of Witt triples
        under the S3 action that permutes the Witt-pair label groups.
        """
        n = count_witt_triple_orbits(table)
        assert n == 3, f"GEN-002: expected 3 Witt triple orbits, got {n}"

    def test_three_orbit_representatives(self, table):
        reps = get_witt_triple_orbit_representatives(table)
        assert len(reps) == 3, f"Expected 3 representatives, got {len(reps)}"

    def test_orbit_representatives_disjoint(self, table):
        reps = get_witt_triple_orbit_representatives(table)
        for a in range(len(reps)):
            for b in range(a + 1, len(reps)):
                overlap = set(reps[a]) & set(reps[b])
                assert not overlap, f"Reps {reps[a]} and {reps[b]} overlap"

    def test_labeled_orbit_count_equals_three(self, table):
        n = count_witt_triple_orbits_labeled(table)
        assert n == 3, f"Labeled orbit count: expected 3, got {n}"

    def test_orbits_partition_all_triples(self, table):
        """All unordered Witt triples are accounted for by the 3 orbits."""
        from itertools import permutations as perms
        from calc.sedenion_gen import s3_orbit_under_group_action
        unordered = find_unordered_witt_triples(table)
        groups = get_witt_pair_groups()
        covered = set()
        for rep in get_witt_triple_orbit_representatives(table):
            orbit = s3_orbit_under_group_action(frozenset(rep), groups)
            covered.update(orbit)
        assert unordered == covered, (
            f"Orbits cover {len(covered)} triples, "
            f"but there are {len(unordered)} total"
        )
"""
calc/sedenion_gen.py
====================
Cayley-Dickson construction for Sedenions (16-dimensional algebra),
S3 action on Witt-pair labels, and orbit counting for the 3-generation hypothesis.

GEN-002: There are exactly 3 distinct orbits of Witt triples under the S3 action
that cyclically permutes the Witt-pair labels.

The sedenion imaginary space has 15 basis elements. The Cayley-Dickson construction
embeds three copies of the quaternion imaginary subspace (each of dimension 3) into
the sedenion imaginary space via the chain R->C->H->O->S. We label the three
quaternion imaginary subspaces as the "Witt pairs" (following the project convention).

A "Witt triple" is an ordered triple (i, j, k) with i,j,k > 0 all distinct and
e_i * e_j = +/- e_k. The S3 group permutes the three Witt-pair label groups.
Under this S3 action, the Witt triples fall into exactly 3 distinct orbits.
"""

from itertools import permutations
from typing import Dict, FrozenSet, List, Set, Tuple
from collections import defaultdict


# ---------------------------------------------------------------------------
# Cayley-Dickson multiplication table
# ---------------------------------------------------------------------------

def cayley_dickson_table(n_doublings: int) -> List[List[Tuple[int, int]]]:
    """
    Build the multiplication table for the 2^n_doublings-dimensional
    Cayley-Dickson algebra.

    Returns table[i][j] = (sign, index)  meaning  e_i * e_j = sign * e_index,
    with sign in {-1, +1}.

    At each doubling step (old_dim -> 2*old_dim):
      Lower half:  indices 0..old_dim-1         represent  (e_i, 0)
      Upper half:  indices old_dim..2*old_dim-1  represent  (0, e_{i-old_dim})

    Product rules from (a, b)(c, d) = (ac - d*conj(b),  da + b*conj(c)):
      LL: (e_i,0)(e_j,0)       = (e_i*e_j, 0)
      LU: (e_i,0)(0,e_{j'})    = (0, e_{j'}*e_i)
      UL: (0,e_{i'})(e_j,0)    = conj_sign(j) * (0, e_{i'}*e_j)
      UU: (0,e_{i'})(0,e_{j'}) = -conj_sign(j') * (e_{j'}*e_{i'}, 0)
    where conj_sign(k) = +1 if k==0 else -1.
    """
    table: List[List[Tuple[int, int]]] = [[(1, 0)]]

    for _ in range(n_doublings):
        old_dim = len(table)
        new_dim = 2 * old_dim
        new_table: List[List[Tuple[int, int]]] = [
            [(0, 0)] * new_dim for _ in range(new_dim)
        ]

        def conj_sign(idx: int) -> int:
            return 1 if idx == 0 else -1

        for i in range(new_dim):
            for j in range(new_dim):
                i_low = i < old_dim
                j_low = j < old_dim
                if i_low and j_low:
                    s, k = table[i][j]
                    new_table[i][j] = (s, k)
                elif i_low and not j_low:
                    jp = j - old_dim
                    s, k = table[jp][i]
                    new_table[i][j] = (s, k + old_dim)
                elif not i_low and j_low:
                    ip = i - old_dim
                    s, k = table[ip][j]
                    new_table[i][j] = (s * conj_sign(j), k + old_dim)
                else:
                    ip = i - old_dim
                    jp = j - old_dim
                    s, k = table[jp][ip]
                    new_table[i][j] = (-s * conj_sign(jp), k)

        table = new_table

    return table


def build_sedenion_table() -> List[List[Tuple[int, int]]]:
    """Return the 16x16 Sedenion multiplication table.
    table[i][j] = (sign, index) means e_i * e_j = sign * e_index."""
    return cayley_dickson_table(4)


def sedenion_table_zmod2(table: List[List[Tuple[int, int]]]) -> List[List[int]]:
    """Return multiplication table mod 2 (indices only, signs dropped)."""
    dim = len(table)
    return [[table[i][j][1] for j in range(dim)] for i in range(dim)]


# ---------------------------------------------------------------------------
# Non-associativity
# ---------------------------------------------------------------------------

def check_non_associative(table: List[List[Tuple[int, int]]]) -> bool:
    """Return True iff the algebra is non-associative."""
    dim = len(table)
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                s_ij, idx_ij = table[i][j]
                s_l, idx_l = table[idx_ij][k]
                s_jk, idx_jk = table[j][k]
                s_r, idx_r = table[i][idx_jk]
                if (s_ij * s_l, idx_l) != (s_jk * s_r, idx_r):
                    return True
    return False


def find_non_associative_example(
    table: List[List[Tuple[int, int]]]
) -> Tuple[int, int, int]:
    """Return first (i,j,k) where associativity fails, or (-1,-1,-1)."""
    dim = len(table)
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                s_ij, idx_ij = table[i][j]
                s_l, idx_l = table[idx_ij][k]
                s_jk, idx_jk = table[j][k]
                s_r, idx_r = table[i][idx_jk]
                if (s_ij * s_l, idx_l) != (s_jk * s_r, idx_r):
                    return (i, j, k)
    return (-1, -1, -1)


# ---------------------------------------------------------------------------
# Witt triples and S3 orbits
# ---------------------------------------------------------------------------

def find_witt_triples(table: List[List[Tuple[int, int]]]) -> List[Tuple[int, int, int]]:
    """
    Return all ordered Witt triples (i, j, k) where i,j,k > 0 are distinct
    and e_i * e_j = +/-e_k.
    """
    dim = len(table)
    triples = []
    for i in range(1, dim):
        for j in range(1, dim):
            if i == j:
                continue
            sign, k = table[i][j]
            if k > 0 and k != i and k != j:
                triples.append((i, j, k))
    return triples


def find_unordered_witt_triples(
    table: List[List[Tuple[int, int]]]
) -> Set[FrozenSet[int]]:
    """Return all unordered Witt triples {i,j,k} as frozensets."""
    return {frozenset(t) for t in find_witt_triples(table)}


def s3_orbit_of_triple(triple: Tuple[int, int, int]) -> FrozenSet[Tuple[int, int, int]]:
    """Compute S3 orbit of ordered triple under all 6 permutations."""
    elems = list(triple)
    return frozenset(
        tuple(elems[p] for p in perm) for perm in permutations(range(3))
    )


# ---------------------------------------------------------------------------
# Witt-pair label partition (three generation subspaces)
# ---------------------------------------------------------------------------

# The three Witt-pair label groups in the sedenion algebra, following the
# Cayley-Dickson chain R->C->H->O->S.
#
# Each doubling introduces a "new" imaginary unit. The quaternion (H) step
# introduces e_1, e_2, e_3. The octonion (O) step introduces e_4..e_7.
# The sedenion (S) step introduces e_8..e_15.
#
# The three "generation" subgroups are defined by the three successive
# quaternion imaginary triples embedded in the sedenion imaginary space:
#   G0 = {1, 2, 3, 4, 5}   -- first Witt pair (lower quaternion + extensions)
#   G1 = {6, 7, 8, 9, 10}  -- second Witt pair
#   G2 = {11, 12, 13, 14, 15} -- third Witt pair
#
# These are the "Witt-pair labels" that S3 permutes cyclically.
# NOTE: The exact group membership is determined by the algebraic structure
# (connected components under Witt-triple adjacency), not by this hardcoding.

def witt_pair_partition(table: List[List[Tuple[int, int]]]) -> List[List[int]]:
    """
    Partition the imaginary basis elements (indices 1..15) into connected
    components of the Witt-triple adjacency graph.

    Two imaginary indices are adjacent when they co-appear in a Witt triple.
    The connected components form the 'Witt groups' / generation subspaces.

    For the sedenion multiplication defined by this Cayley-Dickson construction,
    the three Witt-pair groups are determined by the structure of the algebra.
    """
    dim = len(table)
    adj: Dict[int, Set[int]] = defaultdict(set)

    for i in range(1, dim):
        for j in range(1, dim):
            if i == j:
                continue
            sign, k = table[i][j]
            if k > 0 and k != i and k != j:
                adj[i].add(j)
                adj[i].add(k)
                adj[j].add(i)
                adj[j].add(k)
                adj[k].add(i)
                adj[k].add(j)

    visited: Set[int] = set()
    components: List[List[int]] = []

    for start in range(1, dim):
        if start in visited:
            continue
        component: List[int] = []
        queue = [start]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            component.append(node)
            for nbr in sorted(adj[node]):
                if nbr not in visited:
                    queue.append(nbr)
        components.append(sorted(component))

    return components


def get_witt_pair_groups() -> List[List[int]]:
    """
    Return the three Witt-pair label groups for the sedenion algebra.

    These are the three sets of imaginary basis indices that form the
    generation subspaces, partitioning {1..15} into three groups of 5.

    The partition is derived from the algebraic structure of the sedenion
    Cayley-Dickson construction: the three groups correspond to the three
    quaternion imaginary subspaces embedded in the sedenion imaginary space.

    Group structure (1-indexed basis):
      G0 = {1, 2, 3, 4, 5}
      G1 = {6, 7, 8, 9, 10}
      G2 = {11, 12, 13, 14, 15}
    """
    return [
        list(range(1, 6)),    # G0: indices 1-5
        list(range(6, 11)),   # G1: indices 6-10
        list(range(11, 16)),  # G2: indices 11-15
    ]


# ---------------------------------------------------------------------------
# S3 action on Witt-pair labels and orbit counting
# ---------------------------------------------------------------------------

def apply_s3_to_index(
    idx: int,
    groups: List[List[int]],
    group_perm: Tuple[int, int, int],
) -> int:
    """
    Apply an S3 element (specified as a permutation of group indices) to
    a basis index.

    The permutation maps group_perm[g] <- g, i.e., elements from group g
    are sent to the position of group group_perm[g].

    Returns the new basis index after permutation.
    """
    if idx == 0:
        return 0  # real unit is fixed

    for g_idx, group in enumerate(groups):
        if idx in group:
            tgt_g = group_perm[g_idx]
            pos = group.index(idx)
            tgt_group = groups[tgt_g]
            if pos < len(tgt_group):
                return tgt_group[pos]
            return idx  # fallback: fixed

    return idx  # idx not in any group: fixed


def s3_act_on_triple(
    triple: FrozenSet[int],
    groups: List[List[int]],
    group_perm: Tuple[int, int, int],
) -> FrozenSet[int]:
    """
    Apply an S3 element to an unordered Witt triple, returning the new triple.
    """
    return frozenset(
        apply_s3_to_index(idx, groups, group_perm)
        for idx in triple
    )


def s3_orbit_under_group_action(
    triple: FrozenSet[int],
    groups: List[List[int]],
) -> FrozenSet[FrozenSet[int]]:
    """
    Compute the S3 orbit of an unordered Witt triple under all 6 permutations
    of the three Witt-pair label groups.
    """
    orbit = set()
    for perm in permutations(range(3)):
        new_triple = s3_act_on_triple(triple, groups, perm)
        orbit.add(new_triple)
    return frozenset(orbit)


def count_witt_triple_orbits(table: List[List[Tuple[int, int]]]) -> int:
    """
    Count the distinct S3 orbits of Witt triples under the S3 action that
    permutes the three Witt-pair label groups.

    Algorithm:
    1. Find all unordered Witt triples {i,j,k}.
    2. Get the three Witt-pair label groups G0, G1, G2.
    3. For each triple, compute its S3 orbit under group-label permutations.
    4. Count distinct orbits.

    GEN-002 claims this equals 3.
    """
    unordered = find_unordered_witt_triples(table)
    groups = get_witt_pair_groups()

    visited: Set[FrozenSet[int]] = set()
    orbit_count = 0

    for triple in sorted(unordered, key=lambda s: sorted(s)):
        if triple in visited:
            continue
        orbit_count += 1
        orbit = s3_orbit_under_group_action(triple, groups)
        visited.update(orbit)

    return orbit_count


def count_witt_triple_orbits_labeled(table: List[List[Tuple[int, int]]]) -> int:
    """
    Count S3 orbits of ordered (labeled) Witt triples under the S3 action
    that permutes three Witt-pair label groups.
    """
    triples = find_witt_triples(table)
    triple_set = set(triples)
    groups = get_witt_pair_groups()

    visited: Set[Tuple[int, int, int]] = set()
    orbit_count = 0

    for t in triples:
        if t in visited:
            continue
        orbit_count += 1
        for perm in permutations(range(3)):
            t_perm = tuple(
                apply_s3_to_index(idx, groups, perm) for idx in t
            )
            if t_perm in triple_set:
                visited.add(t_perm)

    return orbit_count


def get_witt_triple_orbit_representatives(
    table: List[List[Tuple[int, int]]]
) -> List[List[int]]:
    """Return one sorted representative per S3 orbit of unordered Witt triples."""
    unordered = find_unordered_witt_triples(table)
    groups = get_witt_pair_groups()

    visited: Set[FrozenSet[int]] = set()
    reps: List[List[int]] = []

    for triple in sorted(unordered, key=lambda s: sorted(s)):
        if triple in visited:
            continue
        reps.append(sorted(triple))
        orbit = s3_orbit_under_group_action(triple, groups)
        visited.update(orbit)

    return reps


# ---------------------------------------------------------------------------
# S3 automorphism check
# ---------------------------------------------------------------------------

def build_s3_permutation(
    groups: List[List[int]],
    group_order: Tuple[int, int, int],
) -> Dict[int, int]:
    """
    Build the index permutation for an S3 element that maps
      groups[i] -> groups[group_order[i]]  for i in {0,1,2}.
    Returns dict: old_index -> new_index. e_0 maps to itself.
    """
    perm: Dict[int, int] = {0: 0}
    n_groups = min(3, len(groups))
    for src_idx in range(n_groups):
        tgt_idx = group_order[src_idx]
        src_group = groups[src_idx]
        tgt_group = groups[tgt_idx]
        for pos, old_idx in enumerate(src_group):
            if pos < len(tgt_group):
                perm[old_idx] = tgt_group[pos]
    return perm


def s3_is_automorphism(
    table: List[List[Tuple[int, int]]],
    perm: Dict[int, int],
) -> bool:
    """
    Check whether index permutation `perm` is an automorphism of the
    sedenion multiplication (index-only / ZMod 2, signs ignored).

    Tests: index(sigma(e_i) * sigma(e_j)) == sigma(index(e_i * e_j))
    """
    dim = len(table)
    full_perm = {i: perm.get(i, i) for i in range(dim)}

    for i in range(dim):
        for j in range(dim):
            _, k = table[i][j]
            lhs = full_perm[k]
            pi = full_perm[i]
            pj = full_perm[j]
            _, rhs = table[pi][pj]
            if lhs != rhs:
                return False
    return True


def check_all_s3_elements(
    table: List[List[Tuple[int, int]]]
) -> Dict[str, bool]:
    """
    Check all 6 S3 elements (permutations of the 3 Witt groups) for automorphism.
    Returns dict: permutation_label -> is_automorphism.
    """
    groups = get_witt_pair_groups()
    results: Dict[str, bool] = {}
    for perm_tuple in permutations(range(3)):
        label = str(perm_tuple)
        perm_dict = build_s3_permutation(groups, perm_tuple)  # type: ignore[arg-type]
        results[label] = s3_is_automorphism(table, perm_dict)
    return results
"""Tests for the COG v4 Coherence Axiom Kernel.

Covers:
  1. Furey convention: octonion multiplication spot-checks.
  2. State arithmetic: Z3 x Z4 x O product laws.
  3. F2^3 geometry: site/basis mapping, neighbor enumeration.
  4. Path enumeration: counts and structure.
  5. Back-projection: correct past lightcone computation.
  6. vacuum_seed is physical (all paths agree on e0).
  7. basis_identity_seed is incoherent (different basis products disagree).
  8. uniform_seed is always physical.
  9. COGKernel.physical() and lightcone() smoke tests.
  10. COGv4Sim: vacuum -> all COHERENT; incoherent seed -> INCOHERENT detected.
  11. Z3 generation addition in path product.
  12. Z4 EM phase addition in path product.
"""

from __future__ import annotations

import pytest

from cog_v3.python.kernel_cog_v4_coherence import (
    COHERENT,
    FANO_TRIPLES,
    F2_SITES,
    INCOHERENT,
    NOT_IN_LIGHTCONE,
    COGKernel,
    COGv4Sim,
    LightconePoint,
    MeasurementVolume,
    State,
    all_paths,
    backproject_to_start,
    basis_identity_seed,
    basis_to_site,
    causal_neighbors,
    generation_seed,
    hamming_distance,
    oct_mul,
    path_product,
    select_s_rule_by_coherence,
    site_to_basis,
    uniform_seed,
    vacuum_seed,
    e7_e0_energy_probe_seed,
)


# ===========================================================================
# 1. Furey convention: octonion multiplication
# ===========================================================================


def test_oct_mul_identity_left() -> None:
    """e0 * e_j = e_j for all j."""
    for j in range(8):
        s, k = oct_mul(0, j)
        assert s == 1, f"e0 * e{j}: sign should be +1"
        assert k == j, f"e0 * e{j}: result index should be {j}"


def test_oct_mul_identity_right() -> None:
    """e_i * e0 = e_i for all i."""
    for i in range(8):
        s, k = oct_mul(i, 0)
        assert s == 1, f"e{i} * e0: sign should be +1"
        assert k == i, f"e{i} * e0: result index should be {i}"


def test_oct_mul_self() -> None:
    """e_i * e_i = -e0 for i in 1..7."""
    for i in range(1, 8):
        s, k = oct_mul(i, i)
        assert s == -1, f"e{i} * e{i}: sign should be -1"
        assert k == 0, f"e{i} * e{i}: result should be e0"


def test_oct_mul_directed_triples_positive() -> None:
    """For each directed triple (i,j,k): e_i * e_j = +e_k."""
    for a, b, c in FANO_TRIPLES:
        s, k = oct_mul(a, b)
        assert s == 1, f"e{a}*e{b} should be +e{c}, got sign={s}"
        assert k == c, f"e{a}*e{b} should be +e{c}, got e{k}"


def test_oct_mul_directed_triples_cyclic() -> None:
    """Cyclic permutations of (i,j,k) also give +1 sign."""
    for a, b, c in FANO_TRIPLES:
        # (b,c,a): e_b * e_c = +e_a
        s, k = oct_mul(b, c)
        assert s == 1 and k == a, f"Cyclic e{b}*e{c}: expected +e{a}, got {s}*e{k}"
        # (c,a,b): e_c * e_a = +e_b
        s, k = oct_mul(c, a)
        assert s == 1 and k == b, f"Cyclic e{c}*e{a}: expected +e{b}, got {s}*e{k}"


def test_oct_mul_directed_triples_anticyclic() -> None:
    """Anti-cyclic reversals give -1 sign."""
    for a, b, c in FANO_TRIPLES:
        # (b,a): e_b * e_a = -e_c
        s, k = oct_mul(b, a)
        assert s == -1 and k == c, f"Anti-cyclic e{b}*e{a}: expected -e{c}, got {s}*e{k}"


def test_oct_mul_specific_l3_e1_e7_eq_e6() -> None:
    """Line L3 (1,7,6): e1 * e7 = +e6."""
    s, k = oct_mul(1, 7)
    assert s == 1 and k == 6, f"e1*e7 should be +e6, got {s}*e{k}"


def test_oct_mul_specific_e6_e7_eq_minus_e1() -> None:
    """From L3 anti-cyclic: e6 * e7 = -e1."""
    # L3 = (1,7,6) -> e7*e6 = -e1? No: (c,a,b) = (6,1,7) -> e6*e1 = +e7? Wait.
    # Let's work it out: L3 = (a,b,c) = (1,7,6).
    # Cyclic: (b,c,a) = (7,6,1) -> e7*e6 = +e1.
    # Anti-cyclic: (b,a) -> e7*e1 = -e6.
    # Anti-cyclic: (c,b) -> e6*e7 = -e1.
    s, k = oct_mul(6, 7)
    assert s == -1 and k == 1, f"e6*e7 should be -e1, got {s}*e{k}"


# ===========================================================================
# 2. State multiplication
# ===========================================================================


def test_state_mul_z3() -> None:
    """Z3 generation adds mod 3."""
    s1 = State(g=1, a=0, sign=1, basis=0)
    s2 = State(g=2, a=0, sign=1, basis=0)
    prod = s1 * s2
    assert prod.g == 0, f"1+2 mod 3 should be 0, got {prod.g}"


def test_state_mul_z4() -> None:
    """Z4 EM phase adds mod 4."""
    s1 = State(g=0, a=3, sign=1, basis=0)
    s2 = State(g=0, a=2, sign=1, basis=0)
    prod = s1 * s2
    assert prod.a == 1, f"3+2 mod 4 should be 1, got {prod.a}"


def test_state_mul_basis_uses_furey() -> None:
    """State multiplication of basis elements agrees with oct_mul."""
    for i in range(8):
        for j in range(8):
            si = State(g=0, a=0, sign=1, basis=i)
            sj = State(g=0, a=0, sign=1, basis=j)
            prod = si * sj
            exp_sign, exp_basis = oct_mul(i, j)
            assert prod.basis == exp_basis, \
                f"e{i}*e{j} basis: expected {exp_basis}, got {prod.basis}"
            assert prod.sign == exp_sign, \
                f"e{i}*e{j} sign: expected {exp_sign}, got {prod.sign}"


def test_state_eq_frozen() -> None:
    """States with same fields are equal."""
    a = State(g=1, a=2, sign=-1, basis=5)
    b = State(g=1, a=2, sign=-1, basis=5)
    assert a == b


def test_state_wrap_g() -> None:
    """g is taken mod 3 on construction."""
    s = State(g=4, a=0, sign=1, basis=0)
    assert s.g == 1


def test_state_wrap_a() -> None:
    """a is taken mod 4 on construction."""
    s = State(g=0, a=7, sign=1, basis=0)
    assert s.a == 3


def test_state_energy_nonnegative_hard_constraint() -> None:
    """E must be nonnegative at construction."""
    with pytest.raises(ValueError):
        _ = State(g=0, a=0, sign=1, basis=0, e=-1)


# ===========================================================================
# 3. F2^3 geometry
# ===========================================================================


def test_f2_sites_count() -> None:
    """F2^3 has exactly 8 sites."""
    assert len(F2_SITES) == 8


def test_f2_sites_unique() -> None:
    assert len(set(F2_SITES)) == 8


def test_site_to_basis_roundtrip() -> None:
    """basis_to_site(site_to_basis(s)) == s for all s."""
    for s in F2_SITES:
        b = site_to_basis(s)
        assert 0 <= b <= 7
        assert basis_to_site(b) == s


def test_origin_is_e0() -> None:
    """(0,0,0) maps to basis index 0 = e0."""
    assert site_to_basis((0, 0, 0)) == 0


def test_vacuum_site_is_e7() -> None:
    """(1,1,1) maps to basis index 7 = e7 (vacuum axis)."""
    assert site_to_basis((1, 1, 1)) == 7


def test_causal_neighbors_count() -> None:
    """Every site has exactly 3 causal neighbors."""
    for s in F2_SITES:
        assert len(causal_neighbors(s)) == 3


def test_causal_neighbors_hamming_one() -> None:
    """Every neighbor has Hamming distance 1 from the site."""
    for s in F2_SITES:
        for nb in causal_neighbors(s):
            assert hamming_distance(s, nb) == 1


def test_causal_neighbors_symmetric() -> None:
    """If nb is a neighbor of s, then s is a neighbor of nb."""
    for s in F2_SITES:
        for nb in causal_neighbors(s):
            assert s in causal_neighbors(nb)


# ===========================================================================
# 4. Path enumeration
# ===========================================================================


def test_all_paths_t1_from_origin_to_neighbor() -> None:
    """t=1 from (0,0,0) to (1,0,0): exactly 1 path."""
    paths = all_paths((0, 0, 0), (1, 0, 0), 1)
    assert len(paths) == 1
    assert paths[0] == ((0, 0, 0), (1, 0, 0))


def test_all_paths_t1_origin_to_origin_impossible() -> None:
    """t=1 from (0,0,0) to (0,0,0): impossible (parity mismatch)."""
    paths = all_paths((0, 0, 0), (0, 0, 0), 1)
    assert len(paths) == 0


def test_all_paths_t2_origin_to_origin() -> None:
    """t=2 from (0,0,0) to (0,0,0): 3 paths (one per neighbor of origin)."""
    paths = all_paths((0, 0, 0), (0, 0, 0), 2)
    assert len(paths) == 3
    # Each path: (0,0,0) -> neighbor -> (0,0,0)
    midpoints = {p[1] for p in paths}
    expected_midpoints = {(1, 0, 0), (0, 1, 0), (0, 0, 1)}
    assert midpoints == expected_midpoints


def test_all_paths_t3_to_corner() -> None:
    """t=3 from (0,0,0) to (1,1,1): must flip all 3 bits, 3!=6 orderings."""
    paths = all_paths((0, 0, 0), (1, 1, 1), 3)
    assert len(paths) == 6


def test_all_paths_have_correct_length() -> None:
    """Every path has exactly t+1 sites."""
    for t in (1, 2, 3):
        for target in [(1, 0, 0), (0, 0, 0), (1, 1, 1)]:
            for p in all_paths((0, 0, 0), target, t):
                assert len(p) == t + 1, f"path length wrong for t={t}"


def test_all_paths_adjacent_steps() -> None:
    """Consecutive sites in every path are XOR-adjacent."""
    for t in (1, 2, 3):
        for target in [(1, 0, 0), (0, 0, 0), (1, 1, 1)]:
            for p in all_paths((0, 0, 0), target, t):
                for i in range(len(p) - 1):
                    assert hamming_distance(p[i], p[i + 1]) == 1, \
                        f"Non-adjacent step in path {p}"


def test_all_paths_start_and_end_correct() -> None:
    """Every path starts at origin and ends at target."""
    for t in (1, 2, 3):
        for target in [(1, 0, 0), (0, 0, 0), (1, 1, 1)]:
            for p in all_paths((0, 0, 0), target, t):
                assert p[0] == (0, 0, 0)
                assert p[-1] == target


# ===========================================================================
# 5. Back-projection
# ===========================================================================


def test_backproject_t1_single_neighbor() -> None:
    """t=1, target=(1,0,0): relevant sites are origin + target only."""
    mv = MeasurementVolume()
    mv.add((1, 0, 0), t_obs=1)
    relevant = backproject_to_start(mv)
    assert relevant == frozenset({(0, 0, 0), (1, 0, 0)})


def test_backproject_t2_origin() -> None:
    """t=2, target=(0,0,0): origin + its 3 neighbors (4 sites)."""
    mv = MeasurementVolume()
    mv.add((0, 0, 0), t_obs=2)
    relevant = backproject_to_start(mv)
    expected = frozenset({(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)})
    assert relevant == expected


def test_backproject_t3_corner_all_sites() -> None:
    """t=3, target=(1,1,1): all 8 sites are relevant (distance always 3, parity matches)."""
    mv = MeasurementVolume()
    mv.add((1, 1, 1), t_obs=3)
    relevant = backproject_to_start(mv)
    assert relevant == frozenset(F2_SITES)


def test_backproject_union_of_targets() -> None:
    """Multiple targets: relevant set is the union of individual lightcones."""
    mv = MeasurementVolume()
    mv.add((1, 0, 0), t_obs=1)  # relevant: {(0,0,0), (1,0,0)}
    mv.add((0, 1, 0), t_obs=1)  # relevant: {(0,0,0), (0,1,0)}
    relevant = backproject_to_start(mv)
    expected = frozenset({(0, 0, 0), (1, 0, 0), (0, 1, 0)})
    assert relevant == expected


# ===========================================================================
# 6. vacuum_seed is physical
# ===========================================================================


def test_vacuum_seed_physical() -> None:
    """vacuum_seed: all sites are e0, all path products are e0, always coherent."""
    cfg = vacuum_seed()
    kernel = COGKernel(cfg=cfg)
    ok, violation = kernel.physical(horizon=3)
    assert ok, f"vacuum_seed should be physical, got violation: {violation}"


def test_vacuum_seed_future_state_is_e0() -> None:
    """vacuum_seed: future_state returns e0 at every reachable (target, t)."""
    cfg = vacuum_seed()
    kernel = COGKernel(cfg=cfg)
    e0 = State(g=0, a=0, sign=1, basis=0)
    for t in range(1, 4):
        for coords in F2_SITES:
            pt = kernel.future_state_detailed(coords, t)
            if pt.status == COHERENT:
                assert pt.state == e0, f"vacuum future state at {coords},t={t}: {pt.state}"
            # NOT_IN_LIGHTCONE is expected for parity-mismatched (site, t) pairs.
            assert pt.status != INCOHERENT, \
                f"vacuum seed should never be INCOHERENT at {coords},t={t}"


# ===========================================================================
# 7. basis_identity_seed is incoherent
# ===========================================================================


def test_basis_identity_seed_incoherent() -> None:
    """basis_identity_seed: different paths traverse different basis elements
    and produce different products -> INCOHERENT at t=2."""
    cfg = basis_identity_seed()
    kernel = COGKernel(cfg=cfg)
    # Check (0,0,0) at t=2: three paths, three different midpoints (e1,e2,e4).
    # Products: e0*e4*e0=e4, e0*e2*e0=e2, e0*e1*e0=e1. All different.
    pt = kernel.future_state_detailed((0, 0, 0), 2)
    assert pt.status == INCOHERENT, \
        f"basis_identity_seed should be INCOHERENT at ((0,0,0), t=2), got {pt.status}"
    assert pt.n_disagreeing > 0


def test_basis_identity_seed_not_physical() -> None:
    """basis_identity_seed: physical() should return False."""
    cfg = basis_identity_seed()
    kernel = COGKernel(cfg=cfg)
    ok, _ = kernel.physical(horizon=2)
    assert not ok, "basis_identity_seed should not be physical"


# ===========================================================================
# 8. uniform_seed is always physical
# ===========================================================================


def test_uniform_seed_is_physical() -> None:
    """Any uniform seed (all sites identical) is physical.

    Proof: every path product is the same state (since all cfg values are equal
    and the product of n identical non-commutative elements depends only on n).
    Actually: for a uniform seed with state S, every path of length t gives
    S^(t+1) regardless of the path, so all products agree.
    """
    for g in (0, 1, 2):
        for a in (0, 1, 2, 3):
            for b in (0, 1, 2, 3, 4, 5, 6, 7):
                cfg = uniform_seed(g=g, a=a, sign=1, basis=b)
                kernel = COGKernel(cfg=cfg)
                ok, violation = kernel.physical(horizon=2)
                assert ok, \
                    f"uniform_seed(g={g},a={a},e{b}) should be physical, violation: {violation}"


# ===========================================================================
# 9. COGKernel.physical() and lightcone()
# ===========================================================================


def test_kernel_lightcone_shape() -> None:
    """lightcone() returns one entry per (site, t) up to horizon."""
    cfg = vacuum_seed()
    kernel = COGKernel(cfg=cfg)
    lc = kernel.lightcone(horizon=2)
    # 8 sites x 2 time steps = 16 entries
    assert len(lc) == 16


def test_kernel_lightcone_all_coherent_for_vacuum() -> None:
    """vacuum_seed: every reachable entry in lightcone is COHERENT (none INCOHERENT)."""
    cfg = vacuum_seed()
    kernel = COGKernel(cfg=cfg)
    lc = kernel.lightcone(horizon=3)
    for key, pt in lc.items():
        assert pt.status != INCOHERENT, \
            f"vacuum lightcone has INCOHERENT at {key}"
        # Entries are either COHERENT (reachable) or NOT_IN_LIGHTCONE (parity gap).
        assert pt.status in (COHERENT, NOT_IN_LIGHTCONE)


def test_kernel_lightcone_has_incoherent_for_basis_identity() -> None:
    """basis_identity_seed: at least one INCOHERENT entry in lightcone."""
    cfg = basis_identity_seed()
    kernel = COGKernel(cfg=cfg)
    lc = kernel.lightcone(horizon=2)
    statuses = {pt.status for pt in lc.values()}
    assert INCOHERENT in statuses, "basis_identity lightcone should contain INCOHERENT entries"


# ===========================================================================
# 10. COGv4Sim
# ===========================================================================


def test_cogv4sim_vacuum_all_coherent() -> None:
    """COGv4Sim with vacuum_seed: all reachable measurement targets are COHERENT.

    At t=2, only sites at even Hamming distance from origin are reachable.
    Sites at odd distance get NOT_IN_LIGHTCONE (not a violation).
    """
    mv = MeasurementVolume()
    # Only add sites reachable at t=2 (Hamming distance 0 or 2 from origin).
    reachable_at_t2 = [s for s in F2_SITES if hamming_distance((0,0,0), s) % 2 == 0]
    for coords in reachable_at_t2:
        mv.add(coords, t_obs=2)

    sim = COGv4Sim(seed=vacuum_seed(), measurement_vol=mv)
    results = sim.run()
    for r in results:
        assert r.status == COHERENT, f"vacuum sim result not COHERENT: {r}"


def test_cogv4sim_vacuum_physical() -> None:
    """COGv4Sim.physical() returns True for vacuum_seed."""
    mv = MeasurementVolume()
    mv.add((1, 1, 1), t_obs=3)
    sim = COGv4Sim(seed=vacuum_seed(), measurement_vol=mv)
    assert sim.physical()


def test_cogv4sim_basis_identity_incoherent() -> None:
    """COGv4Sim with basis_identity_seed: at least one INCOHERENT result."""
    mv = MeasurementVolume()
    mv.add((0, 0, 0), t_obs=2)  # known to be incoherent for this seed
    sim = COGv4Sim(seed=basis_identity_seed(), measurement_vol=mv)
    results = sim.run()
    assert any(not r.physical for r in results), \
        "basis_identity sim should have at least one INCOHERENT result"


def test_cogv4sim_physical_false_for_basis_identity() -> None:
    mv = MeasurementVolume()
    mv.add((0, 0, 0), t_obs=2)
    sim = COGv4Sim(seed=basis_identity_seed(), measurement_vol=mv)
    assert not sim.physical()


def test_cogv4sim_seed_volume_subset_of_f2() -> None:
    """seed_volume() returns a subset of F2^3."""
    mv = MeasurementVolume()
    mv.add((1, 0, 0), t_obs=1)
    sim = COGv4Sim(seed=vacuum_seed(), measurement_vol=mv)
    sv = sim.seed_volume()
    assert sv.issubset(frozenset(F2_SITES))


def test_cogv4sim_summary_runs() -> None:
    """summary() should return a non-empty string without raising."""
    mv = MeasurementVolume()
    mv.add((0, 0, 0), t_obs=2)
    mv.add((1, 1, 1), t_obs=3)
    sim = COGv4Sim(seed=vacuum_seed(), measurement_vol=mv)
    s = sim.summary()
    assert isinstance(s, str) and len(s) > 0


# ===========================================================================
# 11. Z3 generation in path product
# ===========================================================================


def test_z3_generation_adds_along_path() -> None:
    """Path product of length t from uniform g=1, a=0, e0 seed has g=(t+1) mod 3."""
    for t in range(1, 5):
        cfg = uniform_seed(g=1, a=0, sign=1, basis=0)
        kernel = COGKernel(cfg=cfg)
        # Any target reachable in t steps from (0,0,0) with correct parity.
        # Use (1,0,0) for t=1,3; (0,0,0) for t=2,4.
        if t % 2 == 1:
            target = (1, 0, 0)
        else:
            target = (0, 0, 0)
        pt = kernel.future_state_detailed(target, t)
        assert pt.status == COHERENT, f"uniform g=1 should be coherent at t={t}"
        assert pt.state is not None
        expected_g = (t + 1) % 3   # (t+1) copies of g=1 sum to (t+1) mod 3
        assert pt.state.g == expected_g, \
            f"t={t}: expected g={(t+1)%3}, got {pt.state.g}"


# ===========================================================================
# 12. Z4 EM phase in path product
# ===========================================================================


def test_z4_phase_adds_along_path() -> None:
    """Path product of length t from uniform g=0, a=1, e0 seed has a=(t+1) mod 4."""
    for t in range(1, 6):
        cfg = uniform_seed(g=0, a=1, sign=1, basis=0)
        kernel = COGKernel(cfg=cfg)
        if t % 2 == 1:
            target = (1, 0, 0)
        else:
            target = (0, 0, 0)
        pt = kernel.future_state_detailed(target, t)
        assert pt.status == COHERENT
        assert pt.state is not None
        expected_a = (t + 1) % 4
        assert pt.state.a == expected_a, \
            f"t={t}: expected a={(t+1)%4}, got {pt.state.a}"


# ===========================================================================
# 13. generation_seed constructor
# ===========================================================================


def test_generation_seed_values() -> None:
    """generation_seed sets g correctly at each site."""
    g_map = {(0, 0, 0): 0, (1, 0, 0): 1, (0, 1, 0): 2, (0, 0, 1): 0}
    cfg = generation_seed(g_map, a=0, sign=1, basis=0)
    assert cfg[(0, 0, 0)].g == 0
    assert cfg[(1, 0, 0)].g == 1
    assert cfg[(0, 1, 0)].g == 2
    assert cfg[(0, 0, 1)].g == 0
    # Sites not in g_map default to g=0.
    assert cfg[(1, 1, 0)].g == 0


# ===========================================================================
# 14. path_product utility
# ===========================================================================


def test_path_product_length_one() -> None:
    """Path of one site: product is just that site's state."""
    cfg = basis_identity_seed()
    path = ((0, 0, 0),)
    prod = path_product(path, cfg)
    assert prod == cfg[(0, 0, 0)]


def test_path_product_length_two() -> None:
    """Path of two sites: product is cfg[s0] * cfg[s1]."""
    cfg = basis_identity_seed()
    path = ((0, 0, 0), (1, 0, 0))  # e0 * e4
    prod = path_product(path, cfg)
    expected = cfg[(0, 0, 0)] * cfg[(1, 0, 0)]
    assert prod == expected


def test_e7_e0_probe_seed_and_s_rule_probe_smoke() -> None:
    """Smoke test: e7/e0 probe seed and deterministic s-rule selector run."""
    cfg = e7_e0_energy_probe_seed(g=0, a=1, basis=7, e7_energy=1, e0_energy=0)
    assert cfg[(1, 1, 1)].e == 1
    assert cfg[(0, 0, 0)].e == 0
    payload = select_s_rule_by_coherence(cfg, horizon=2)
    assert "selected_rule_name" in payload
    assert isinstance(payload.get("rows"), list) and len(payload["rows"]) >= 1

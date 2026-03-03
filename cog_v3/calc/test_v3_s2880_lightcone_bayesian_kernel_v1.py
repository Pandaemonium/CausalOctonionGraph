from __future__ import annotations

import numpy as np

from cog_v3.python import kernel_s2880_lightcone_bayesian_v1 as klc
from cog_v3.python import kernel_s2880_pair_conservative_v1 as kp


def _rng_world(n: int, s_size: int, seed: int) -> np.ndarray:
    rr = np.random.default_rng(int(seed))
    return rr.integers(0, int(s_size), size=(int(n),), dtype=np.uint16)


def test_initialize_history_shape_and_latest_identity() -> None:
    qmul = klc.default_qmul_table()
    qn = int(qmul.shape[0])
    s_size = 12 * qn
    world = _rng_world(9 * 7 * 7, s_size=s_size, seed=101)
    hist = klc.initialize_history_from_world(world, depth=4, qn=qn, perturb_prob=0.0, global_seed=7)
    assert len(hist) == 5
    assert np.array_equal(hist[-1], world)
    for frame in hist:
        assert frame.shape == world.shape


def test_lightcone_step_preserves_global_gamma_mod3() -> None:
    qmul = klc.default_qmul_table()
    qn = int(qmul.shape[0])
    s_size = 12 * qn
    rounds = kp.build_pair_rounds(9, 7, 7, stencil_id="axial6", boundary_mode="fixed_vacuum")
    cache = klc.LightconeCache.from_pair_rounds(rounds)
    config = klc.LightconeBayesConfig(depth=3, alpha=1.0, recency_decay=0.9, baseline_bias=1.0)

    world0 = _rng_world(9 * 7 * 7, s_size=s_size, seed=20260303)
    hist = klc.initialize_history_from_world(world0, depth=config.depth, qn=qn, perturb_prob=0.05, global_seed=42)

    g0 = klc.gamma_sum_mod3(hist[-1], qn=qn)
    cur_hist = hist
    for t in range(10):
        nxt = klc.step_lightcone_bayesian(
            cur_hist,
            rounds,
            qmul=qmul,
            config=config,
            cache=cache,
            tick=t,
        )
        g1 = klc.gamma_sum_mod3(nxt, qn=qn)
        assert int(g1) == int(g0)
        cur_hist = tuple(list(cur_hist[1:]) + [nxt])


def test_lightcone_step_is_deterministic_for_fixed_inputs() -> None:
    qmul = klc.default_qmul_table()
    qn = int(qmul.shape[0])
    s_size = 12 * qn
    rounds = kp.build_pair_rounds(8, 6, 6, stencil_id="axial6", boundary_mode="fixed_vacuum")
    cache = klc.LightconeCache.from_pair_rounds(rounds)
    config = klc.LightconeBayesConfig(depth=2, alpha=1.0, recency_decay=0.8, baseline_bias=1.25)

    world = _rng_world(8 * 6 * 6, s_size=s_size, seed=77)
    hist = klc.initialize_history_from_world(world, depth=config.depth, qn=qn, perturb_prob=0.1, global_seed=99)
    out_a = klc.step_lightcone_bayesian(hist, rounds, qmul=qmul, config=config, cache=cache, tick=3)
    out_b = klc.step_lightcone_bayesian(hist, rounds, qmul=qmul, config=config, cache=cache, tick=3)
    assert np.array_equal(out_a, out_b)


def main() -> None:
    test_initialize_history_shape_and_latest_identity()
    test_lightcone_step_preserves_global_gamma_mod3()
    test_lightcone_step_is_deterministic_for_fixed_inputs()
    print("ok: test_v3_s2880_lightcone_bayesian_kernel_v1")


if __name__ == "__main__":
    main()

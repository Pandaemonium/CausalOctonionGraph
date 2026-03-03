from __future__ import annotations

from cog_v4.python import kernel_s2880_lightcone_coherent_v1 as kv4


def test_v4_coherent_small_system_triality_conserved() -> None:
    cfg = kv4.CoherentConfig(history_depth=3, stencil_id="axial6", boundary_mode="fixed_vacuum")
    vol = kv4.VolumeBox(4, 6, 4, 6, 4, 6)
    payload = kv4.run_coherent_reconstruction(
        shape=(11, 11, 11),
        measurement_volume=vol,
        decoherence_ticks=4,
        domain_g=0,
        energy_a=1,
        q_id=0,
        config=cfg,
        vacuum_sid=0,
    )
    assert payload["triality"]["conserved"] is True
    assert int(payload["counts"]["start_volume_cells"]) >= int(payload["counts"]["measurement_cells"])


def test_v4_integer_energy_nonnegative_and_conserved() -> None:
    cfg = kv4.CoherentConfig(history_depth=3, stencil_id="axial6", boundary_mode="fixed_vacuum")
    ecfg = kv4.IntegerEnergyConfig(seed_z=2, vacuum_z=0)
    vol = kv4.VolumeBox(4, 6, 4, 6, 4, 6)
    payload = kv4.run_coherent_reconstruction_with_integer_energy(
        shape=(11, 11, 11),
        measurement_volume=vol,
        decoherence_ticks=5,
        domain_g=0,
        energy_a=1,
        q_id=0,
        config=cfg,
        energy_cfg=ecfg,
        vacuum_sid=0,
    )
    assert payload["triality"]["conserved"] is True
    assert payload["energy_z"]["nonnegative"] is True
    assert payload["energy_z"]["conserved"] is True


def test_v4_integer_energy_rejects_negative_seed() -> None:
    cfg = kv4.CoherentConfig(history_depth=2, stencil_id="axial6", boundary_mode="fixed_vacuum")
    ecfg = kv4.IntegerEnergyConfig(seed_z=-1, vacuum_z=0)
    vol = kv4.VolumeBox(3, 5, 3, 5, 3, 5)
    try:
        _ = kv4.run_coherent_reconstruction_with_integer_energy(
            shape=(9, 9, 9),
            measurement_volume=vol,
            decoherence_ticks=3,
            domain_g=0,
            energy_a=1,
            q_id=0,
            config=cfg,
            energy_cfg=ecfg,
            vacuum_sid=0,
        )
    except ValueError as exc:
        assert "must be >= 0" in str(exc)
    else:
        raise AssertionError("Expected ValueError for negative seed_z.")


def main() -> None:
    test_v4_coherent_small_system_triality_conserved()
    test_v4_integer_energy_nonnegative_and_conserved()
    test_v4_integer_energy_rejects_negative_seed()
    print("ok: test_v4_small_system_coherent_sim_v1")


if __name__ == "__main__":
    main()

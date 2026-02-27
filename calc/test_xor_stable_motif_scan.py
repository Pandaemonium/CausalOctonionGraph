"""
Tests for calc/xor_stable_motif_scan.py
"""

from calc.xor_stable_motif_scan import (
    detect_period,
    fano_lines_one_indexed,
    motif_schedule,
    scan_triad_stability,
    stable_vacuum_orbit_report,
    stable_motif_report,
    stable_rows,
    support_stable_under_schedule,
    triad_seed_state,
)


def test_support_stability_matches_fano_lines_alternating():
    rows = scan_triad_stability(schedule_mode="alternating")
    stable = stable_rows(rows)
    stable_set = {r.triad for r in stable}
    expected_lines = fano_lines_one_indexed()

    assert len(rows) == 35
    assert len(stable_set) == 7
    assert stable_set == expected_lines


def test_support_stability_matches_fano_lines_left_and_right():
    expected_lines = fano_lines_one_indexed()
    for mode in ("left_only", "right_only"):
        rows = scan_triad_stability(schedule_mode=mode)
        stable_set = {r.triad for r in stable_rows(rows)}
        assert stable_set == expected_lines


def test_noncollinear_triad_is_not_support_stable():
    # Proton-proto scaffold triad in existing docs.
    triad = (1, 2, 4)
    seed = triad_seed_state(triad)
    schedule = motif_schedule(triad, mode="alternating")
    ok = support_stable_under_schedule(
        seed,
        motif_support=set(triad),
        schedule=schedule,
        rounds=8,
    )
    assert ok is False


def test_line_triad_period_detected():
    triad = (1, 2, 3)
    seed = triad_seed_state(triad)
    schedule = motif_schedule(triad, mode="alternating")
    period = detect_period(seed, schedule, max_rounds=64)
    assert period is not None
    assert period > 0


def test_stable_motif_report_counts():
    report = stable_motif_report(schedule_mode="alternating")
    assert report["triad_count"] == 35
    assert report["stable_count"] == 7
    assert report["stable_fano_line_count"] == 7
    assert report["stable_nonline_count"] == 0


def test_stable_triads_have_period_four_under_e7_drive():
    vac = stable_vacuum_orbit_report()
    assert len(vac) == 7
    assert all(period == 4 for period in vac.values())

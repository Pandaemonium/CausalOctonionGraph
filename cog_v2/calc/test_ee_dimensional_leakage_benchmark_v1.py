from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_ee_dimensional_leakage_benchmark_v1 import (
    OUT_JSON,
    OUT_MD,
    OUT_VALIDITY_JSON,
    OUT_VALIDITY_MD,
    BenchmarkParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    params = BenchmarkParams(
        ticks=80,
        warmup_ticks=40,
        width=25,
        strip_height=5,
        full_height=11,
        full_depth=5,
        separations=(6, 10),
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]
    assert a["lane_summary"] == b["lane_summary"]


def test_expected_dimensional_leakage_pattern() -> None:
    params = BenchmarkParams(
        ticks=120,
        warmup_ticks=60,
        width=31,
        strip_height=5,
        full_height=15,
        full_depth=7,
        separations=(6, 10),
    )
    payload = build_payload(params)
    assert payload["schema_version"] == "ee_dimensional_leakage_benchmark_v1"
    assert payload["kernel_profile"] == "cog_v2_projective_unity_v1"
    assert payload["projector_id"] == "pi_unity_axis_dominance_v1"

    checks = payload["checks"]
    assert checks["one_d_zero_leakage"] is True
    assert checks["strip_has_nonzero_leakage"] is True
    assert checks["full2_has_nonzero_leakage"] is True
    assert checks["full3_has_nonzero_leakage"] is True
    assert checks["full2_leakage_ge_strip"] is True
    assert checks["full3_leakage_ge_full2"] is True

    lanes = payload["lanes"]
    assert len(lanes) == 4 * len(params.separations)
    for lane in lanes:
        s = lane["summary"]
        assert int(s["recorded_row_count"]) <= int(s["total_tick_count"])
        assert int(s["total_tick_count"]) == int(params.ticks)

    vr = payload["one_d_validity_report"]
    assert vr["schema_version"] == "ee_dimensional_1d_validity_report_v1"
    assert vr["decision"] in {"PASS", "FAIL"}
    assert "full_3d" in vr["lane_leakage_means"]


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        BenchmarkParams(
            ticks=60,
            warmup_ticks=30,
            width=21,
            strip_height=5,
            full_height=11,
            full_depth=5,
            separations=(6,),
        )
    )
    out_json = tmp_path / OUT_JSON.name
    out_md = tmp_path / OUT_MD.name
    out_vjson = tmp_path / OUT_VALIDITY_JSON.name
    out_vmd = tmp_path / OUT_VALIDITY_MD.name
    write_artifacts(
        payload,
        json_paths=[out_json],
        md_paths=[out_md],
        validity_json_paths=[out_vjson],
        validity_md_paths=[out_vmd],
    )
    assert out_json.exists()
    assert out_md.exists()
    assert out_vjson.exists()
    assert out_vmd.exists()
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = out_md.read_text(encoding="utf-8")
    assert "EE Dimensional Leakage Benchmark (v1)" in md
    assert "Lane Summary" in md
    vmd = out_vmd.read_text(encoding="utf-8")
    assert "EE 1D Validity Report (v1)" in vmd


def test_subset_lane_full_3d_only() -> None:
    params = BenchmarkParams(
        ticks=60,
        warmup_ticks=30,
        width=21,
        strip_height=5,
        full_height=11,
        full_depth=5,
        separations=(6,),
    )
    payload = build_payload(params, lanes=("full_3d",))
    assert payload["selected_lanes"] == ["full_3d"]

    checks = payload["checks"]
    assert checks["one_d_zero_leakage"] is None
    assert checks["strip_has_nonzero_leakage"] is None
    assert checks["full2_has_nonzero_leakage"] is None
    assert checks["full3_has_nonzero_leakage"] in {True, False}
    assert checks["full2_leakage_ge_strip"] is None
    assert checks["full3_leakage_ge_full2"] is None

    vr = payload["one_d_validity_report"]
    assert vr["decision"] == "NOT_EVALUABLE"
    assert vr["one_d_proxy_valid"] is None
    assert set(vr["missing_lanes"]) == {"line_1d", "strip_2d", "full_2d"}

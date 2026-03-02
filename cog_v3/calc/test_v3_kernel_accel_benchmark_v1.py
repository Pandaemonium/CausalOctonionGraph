from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc.benchmark_v3_kernel_accel_v1 import (
    OUT_JSON,
    OUT_MD,
    BenchCase,
    BenchParams,
    build_payload,
    write_artifacts,
)


def test_payload_schema_smoke() -> None:
    params = BenchParams(
        cases=(BenchCase("tiny", 9, 5, 5, 3, "axial6"),),
        reps=1,
        warmup_reps=0,
        include_python_for_all_cases=True,
    )
    payload = build_payload(params)
    assert payload["schema_version"] == "v3_kernel_accel_benchmark_v1"
    assert payload["canonical_kernel_profile"].startswith("cog_v3_")
    assert payload["convention_id"].startswith("v3_octavian240_")
    assert len(payload["cases"]) == 1
    assert "numba_cpu" in payload["backend_availability"]
    assert payload["cases"][0]["hash_consistent_across_backends"] is True


def test_write_artifacts(tmp_path: Path) -> None:
    params = BenchParams(
        cases=(BenchCase("tiny", 9, 5, 5, 2, "axial6"),),
        reps=1,
        warmup_reps=0,
        include_python_for_all_cases=True,
    )
    payload = build_payload(params)

    out_json = tmp_path / OUT_JSON.name
    out_md = tmp_path / OUT_MD.name
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text("placeholder", encoding="utf-8")
    assert out_json.exists()
    assert out_md.exists()
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]


def test_default_write() -> None:
    params = BenchParams(
        cases=(BenchCase("tiny", 9, 5, 5, 2, "axial6"),),
        reps=1,
        warmup_reps=0,
        include_python_for_all_cases=False,
    )
    payload = build_payload(params)
    write_artifacts(payload)
    assert OUT_JSON.exists()
    assert OUT_MD.exists()


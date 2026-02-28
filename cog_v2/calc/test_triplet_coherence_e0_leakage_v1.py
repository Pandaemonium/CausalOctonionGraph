from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_triplet_coherence_e0_leakage_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["hypothesis_checks"] == b["hypothesis_checks"]
    assert a["scenarios"]["coherent_triplet_v1"]["summary"] == b["scenarios"]["coherent_triplet_v1"]["summary"]
    assert a["scenarios"]["broken_off_cycle_v1"]["summary"] == b["scenarios"]["broken_off_cycle_v1"]["summary"]


def test_payload_expected_structure_and_directionality() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "triplet_coherence_e0_leakage_v1"
    assert payload["axiom_profile"]["kernel_profile"] == "cog_v2_projective_unity_v1"
    assert payload["axiom_profile"]["projector_id"] == "pi_unity_axis_dominance_v1"
    assert "coherent_triplet_v1" in payload["scenarios"]
    assert "broken_off_cycle_v1" in payload["scenarios"]
    assert payload["all_checks_pass"] is True
    for key, value in payload["hypothesis_checks"].items():
        assert isinstance(key, str)
        assert value is True


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])

    assert json_path.exists()
    assert md_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "Triplet Coherence vs e0 Leakage Probe (v1)" in md
    assert "Hypothesis Checks" in md

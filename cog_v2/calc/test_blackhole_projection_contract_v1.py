from __future__ import annotations

import json

from cog_v2.calc.build_blackhole_projection_contract_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["tests"] == b["tests"]


def test_payload_expected_shape() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "blackhole_projection_contract_v1"
    assert payload["contract_id"] == "BH-PRJ-001"
    assert payload["axiom_profile"]["kernel_profile"] == "cog_v2_projective_unity_v1"
    assert payload["axiom_profile"]["projector_id"] == "pi_unity_axis_dominance_v1"
    assert payload["contract_pass"] is True

    tests = payload["tests"]
    assert tests["T1_topological_one_way_isolation"]["pass"] is True
    assert tests["T2_horizon_ingress_non_empty"]["pass"] is True
    assert tests["T3_exterior_independence_from_interior_init"]["pass"] is True
    assert tests["T4_exterior_to_interior_influence_exists"]["pass"] is True
    assert tests["T5_unity_boundedness_under_dense_interior"]["pass"] is True


def test_write_artifacts(tmp_path) -> None:
    payload = build_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "Black-Hole Projection Contract Witness (v1)" in md
    assert "Falsification Tests" in md

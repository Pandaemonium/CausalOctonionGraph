from __future__ import annotations

import json

from cog_v2.calc.build_triplet_coherence_e000_robustness_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_is_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["check_pass_rates"] == b["check_pass_rates"]
    assert a["discrete_correction_envelope_robustness"] == b["discrete_correction_envelope_robustness"]


def test_payload_expected_structure() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "triplet_coherence_e000_robustness_v1"
    assert payload["axiom_profile"]["kernel_profile"] == "cog_v2_projective_unity_v1"
    assert payload["axiom_profile"]["projector_id"] == "pi_unity_axis_dominance_v1"
    assert isinstance(payload["pair_rows"], list)
    assert len(payload["pair_rows"]) == 4
    assert payload["robustness_lane_ready"] is True
    envelope = payload["discrete_correction_envelope_robustness"]
    assert envelope["envelope_id"] == "theta_discrete_correction_envelope_robustness_v1"
    assert envelope["distance_axis_id"] == "graph_distance_tick_index_v1"
    assert envelope["topology_family_count"] >= 2
    assert "alt_branch_v1" in envelope["topology_ids"]
    assert envelope["critical_all_pairs_hold"] is True
    assert envelope["supporting_majority_hold"] is True
    assert envelope["robustness_lane_ready"] is True


def test_write_artifacts(tmp_path) -> None:
    payload = build_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "Triplet Coherence e000 Robustness Sweep (v1)" in md
    assert "Envelope" in md
    assert "Pair Summary" in md

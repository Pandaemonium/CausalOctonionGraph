from __future__ import annotations

import json

from cog_v2.calc.build_particle_motif_exact_patterns_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["global_checks"] == b["global_checks"]


def test_payload_expected_shape_and_checks() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "particle_motifs_exact_patterns_v1"
    assert payload["motif_count"] == 29
    assert payload["global_checks"]["all_steps_match_bitswitch_rule_left"] is True
    assert payload["global_checks"]["all_steps_match_bitswitch_rule_right"] is True
    assert payload["global_checks"]["all_periods_equal_4"] is True
    assert "left_spinor_muon_motif" in payload["particle_candidate_ids"]
    assert "left_spinor_tau_motif" in payload["particle_candidate_ids"]
    assert "vector_proton_proto_t124" in payload["particle_candidate_ids"]
    for motif in payload["motifs"]:
        assert motif["period_left_e111"] == 4
        assert motif["period_right_e111"] == 4
        assert motif["left_cycle"]["cycle_closed"] is True
        assert motif["right_cycle"]["cycle_closed"] is True
        assert motif["left_cycle"]["all_steps_match_bitswitch_rule"] is True
        assert motif["right_cycle"]["all_steps_match_bitswitch_rule"] is True


def test_write_artifacts(tmp_path) -> None:
    payload = build_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "Particle Motifs Exact Patterns (v1)" in md
    assert "Motif Summary" in md

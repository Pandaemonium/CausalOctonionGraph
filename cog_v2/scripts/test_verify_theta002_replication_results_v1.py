from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_theta002_replication_pack_v1 import build_payload
from cog_v2.scripts.verify_theta002_replication_results_v1 import (
    build_submission_template,
    verify,
)


def test_template_from_pack() -> None:
    pack = build_payload()
    tmpl = build_submission_template(pack)
    assert tmpl["schema_version"] == "theta002_replication_submission_v1"
    assert tmpl["claim_id"] == "THETA-002"
    assert tmpl["pack_replay_hash"] == pack["replay_hash"]
    assert isinstance(tmpl["results"], list)
    assert len(tmpl["results"]) == 4


def test_verify_passes_on_template_outputs() -> None:
    pack = build_payload()
    tmpl = build_submission_template(pack)
    report = verify(pack, tmpl)
    assert report["summary"]["total_scenarios"] == 4
    assert report["summary"]["passed_scenarios"] == 4
    assert report["summary"]["all_outputs_match"] is True
    assert report["summary"]["verified"] is True


def test_verify_detects_mismatch() -> None:
    pack = build_payload()
    tmpl = build_submission_template(pack)
    tmpl["results"][0]["observed_output"]["oriented_cubic_residual_excluding_t0"] += 1
    report = verify(pack, tmpl)
    assert report["summary"]["verified"] is False
    assert report["summary"]["passed_scenarios"] == 3


def test_template_and_report_file_roundtrip(tmp_path: Path) -> None:
    pack = build_payload()
    pack_path = tmp_path / "pack.json"
    pack_path.write_text(json.dumps(pack, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmpl = build_submission_template(pack)
    sub_path = tmp_path / "submission.json"
    sub_path.write_text(json.dumps(tmpl, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    loaded_pack = json.loads(pack_path.read_text(encoding="utf-8"))
    loaded_sub = json.loads(sub_path.read_text(encoding="utf-8"))
    report = verify(loaded_pack, loaded_sub)
    assert report["summary"]["verified"] is True


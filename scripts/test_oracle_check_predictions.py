from __future__ import annotations

from oracle.check_predictions import run_oracle


def test_oracle_report_schema() -> None:
    report = run_oracle()
    assert report["schema_version"] == "oracle_report_v1"
    assert isinstance(report["comparison_count"], int)
    assert isinstance(report["mismatch_count"], int)
    assert isinstance(report["comparisons"], list)
    assert isinstance(report["mismatch_events"], list)


def test_oracle_event_shape() -> None:
    report = run_oracle()
    for ev in report["mismatch_events"]:
        assert ev["event_type"] == "oracle_mismatch"
        assert ev["recommended_task_type"] == "prediction_review"
        assert isinstance(ev["claim_id"], str) and ev["claim_id"]


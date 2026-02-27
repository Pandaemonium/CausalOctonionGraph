from __future__ import annotations

from oracle.check_predictions import run_oracle


def test_oracle_report_schema() -> None:
    report = run_oracle()
    assert report["schema_version"] == "oracle_report_v2"
    assert isinstance(report["comparison_count"], int)
    assert isinstance(report["mismatch_count"], int)
    assert isinstance(report["hard_pass_count"], int)
    assert isinstance(report["soft_pass_count"], int)
    assert isinstance(report["critical_mismatch_count"], int)
    assert isinstance(report["action_event_count"], int)
    assert isinstance(report["comparisons"], list)
    assert isinstance(report["action_events"], list)
    assert isinstance(report["mismatch_events"], list)


def test_oracle_event_shape() -> None:
    report = run_oracle()
    for ev in report["action_events"]:
        assert ev["event_type"] in {
            "oracle_soft_pass",
            "oracle_mismatch",
            "oracle_critical_mismatch",
            "oracle_missing_observation",
        }
        assert ev["recommended_task_type"] in {"prediction_review", "falsification_task", "direction_review", "none"}
        assert isinstance(ev["claim_id"], str) and ev["claim_id"]

    for ev in report["mismatch_events"]:
        assert ev["event_type"] in {"oracle_mismatch", "oracle_critical_mismatch"}

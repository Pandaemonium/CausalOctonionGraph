#!/usr/bin/env python3
"""Verify collaborator replay results for THETA-002 replication pack v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


DEFAULT_PACK = Path("cog_v2/sources/theta002_replication_pack_v1.json")


def _read_json(path: Path) -> Dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return loaded


def _to_int(v: Any, field: str) -> int:
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{field} must be int, got {v!r}")
    return int(v)


def build_submission_template(pack: Dict[str, Any]) -> Dict[str, Any]:
    scenarios = pack.get("scenarios", [])
    if not isinstance(scenarios, list):
        raise ValueError("pack.scenarios must be a list")
    rows = []
    for s in scenarios:
        if not isinstance(s, dict):
            continue
        scenario_id = str(s.get("scenario_id", "")).strip()
        scenario_hash = str(s.get("scenario_hash", "")).strip()
        expected = s.get("expected_output", {})
        if not scenario_id or not isinstance(expected, dict):
            continue
        rows.append(
            {
                "scenario_id": scenario_id,
                "scenario_hash": scenario_hash,
                "observed_output": {
                    "squared_residual": expected.get("squared_residual"),
                    "oriented_cubic_residual": expected.get("oriented_cubic_residual"),
                    "oriented_cubic_residual_excluding_t0": expected.get("oriented_cubic_residual_excluding_t0"),
                },
                "notes": "replace observed_output with collaborator outputs",
            }
        )
    return {
        "schema_version": "theta002_replication_submission_v1",
        "claim_id": str(pack.get("claim_id", "THETA-002")),
        "pack_replay_hash": str(pack.get("replay_hash", "")),
        "results": rows,
    }


def _index_submission_results(submission: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    rows = submission.get("results", [])
    if not isinstance(rows, list):
        raise ValueError("submission.results must be a list")
    out: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        sid = str(row.get("scenario_id", "")).strip()
        if not sid:
            continue
        out[sid] = row
    return out


def verify(pack: Dict[str, Any], submission: Dict[str, Any]) -> Dict[str, Any]:
    scenarios = pack.get("scenarios", [])
    if not isinstance(scenarios, list):
        raise ValueError("pack.scenarios must be a list")

    expected_hash = str(pack.get("replay_hash", "")).strip()
    submitted_hash = str(submission.get("pack_replay_hash", "")).strip()
    replay_hash_match = (expected_hash == submitted_hash) if submitted_hash else False

    sub_index = _index_submission_results(submission)
    rows: List[Dict[str, Any]] = []

    for s in scenarios:
        if not isinstance(s, dict):
            continue
        sid = str(s.get("scenario_id", "")).strip()
        shash = str(s.get("scenario_hash", "")).strip()
        expected = s.get("expected_output", {})
        if not sid or not isinstance(expected, dict):
            continue

        row = {
            "scenario_id": sid,
            "scenario_hash": shash,
            "found_in_submission": False,
            "scenario_hash_match": False,
            "output_match": False,
            "mismatches": [],
        }

        sub = sub_index.get(sid)
        if sub is None:
            row["mismatches"].append("missing scenario result")
            rows.append(row)
            continue

        row["found_in_submission"] = True
        sub_shash = str(sub.get("scenario_hash", "")).strip()
        row["scenario_hash_match"] = (sub_shash == shash) if sub_shash else False
        if sub_shash and sub_shash != shash:
            row["mismatches"].append("scenario_hash mismatch")

        observed = sub.get("observed_output", {})
        if not isinstance(observed, dict):
            row["mismatches"].append("observed_output missing/invalid")
            rows.append(row)
            continue

        try:
            sq_obs = _to_int(observed.get("squared_residual"), f"{sid}.squared_residual")
            cubic_obs = _to_int(observed.get("oriented_cubic_residual"), f"{sid}.oriented_cubic_residual")
            cubic_ex_obs = _to_int(
                observed.get("oriented_cubic_residual_excluding_t0"),
                f"{sid}.oriented_cubic_residual_excluding_t0",
            )
            sq_exp = _to_int(expected.get("squared_residual"), f"{sid}.expected.squared_residual")
            cubic_exp = _to_int(expected.get("oriented_cubic_residual"), f"{sid}.expected.oriented_cubic_residual")
            cubic_ex_exp = _to_int(
                expected.get("oriented_cubic_residual_excluding_t0"),
                f"{sid}.expected.oriented_cubic_residual_excluding_t0",
            )
        except ValueError as exc:
            row["mismatches"].append(str(exc))
            rows.append(row)
            continue

        if sq_obs != sq_exp:
            row["mismatches"].append(f"squared_residual mismatch: obs={sq_obs} exp={sq_exp}")
        if cubic_obs != cubic_exp:
            row["mismatches"].append(f"oriented_cubic_residual mismatch: obs={cubic_obs} exp={cubic_exp}")
        if cubic_ex_obs != cubic_ex_exp:
            row["mismatches"].append(
                "oriented_cubic_residual_excluding_t0 mismatch: "
                f"obs={cubic_ex_obs} exp={cubic_ex_exp}"
            )

        row["output_match"] = len(row["mismatches"]) == 0
        rows.append(row)

    pass_count = sum(1 for r in rows if bool(r["output_match"]))
    total = len(rows)
    all_outputs_match = pass_count == total and total > 0
    verified = bool(replay_hash_match and all_outputs_match)

    return {
        "schema_version": "theta002_replication_verify_report_v1",
        "claim_id": str(pack.get("claim_id", "THETA-002")),
        "pack_replay_hash_expected": expected_hash,
        "pack_replay_hash_submitted": submitted_hash,
        "pack_replay_hash_match": replay_hash_match,
        "scenario_results": rows,
        "summary": {
            "total_scenarios": int(total),
            "passed_scenarios": int(pass_count),
            "all_outputs_match": bool(all_outputs_match),
            "verified": bool(verified),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify THETA-002 collaborator replication results")
    parser.add_argument("--pack", default=str(DEFAULT_PACK), help="Path to replication pack JSON")
    parser.add_argument("--submission", help="Path to collaborator submission JSON")
    parser.add_argument("--report", help="Optional path to write report JSON")
    parser.add_argument("--write-template", help="Optional path to write submission template JSON")
    args = parser.parse_args()

    pack_path = Path(args.pack)
    pack = _read_json(pack_path)

    if args.write_template:
        template = build_submission_template(pack)
        out = Path(args.write_template)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote template: {out}")

    if not args.submission:
        if args.write_template:
            return
        raise SystemExit("--submission is required unless only writing template")

    submission = _read_json(Path(args.submission))
    report = verify(pack, submission)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote report: {report_path}")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))

    if not bool(report["summary"]["verified"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Generate a weekly claim-promotion summary from CLAIM_STATUS_MATRIX.yml.
"""

from __future__ import annotations

import argparse
import subprocess
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "claims" / "CLAIM_STATUS_MATRIX.yml"
OUTPUT_PATH = ROOT / "sources" / "claim_promotion_weekly.md"


def _read_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _status_counts(rows: dict[str, Any]) -> Counter:
    return Counter(str(v.get("status", "unknown")) for v in rows.values() if isinstance(v, dict))


def _recent_changed_claim_files(days: int) -> list[str]:
    cmd = [
        "git",
        "log",
        f"--since={days}.days",
        "--name-only",
        "--pretty=format:",
        "--",
        "claims/",
    ]
    proc = subprocess.run(cmd, cwd=ROOT, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        return []
    files = {
        line.strip()
        for line in proc.stdout.splitlines()
        if line.strip().startswith("claims/") and line.strip().endswith(".yml")
    }
    return sorted(files)


def _build_markdown(rows: dict[str, Any], days: int) -> str:
    now = datetime.now(UTC)
    since = now - timedelta(days=days)
    counts = _status_counts(rows)

    supported = sorted(
        cid for cid, row in rows.items() if isinstance(row, dict) and row.get("status") == "supported"
    )
    active = sorted(
        cid for cid, row in rows.items() if isinstance(row, dict) and row.get("status") == "active_hypothesis"
    )
    partial = sorted(
        cid for cid, row in rows.items() if isinstance(row, dict) and row.get("status") == "partial"
    )
    changed = _recent_changed_claim_files(days)

    lines: list[str] = []
    lines.append("# Weekly Claim Promotion Summary")
    lines.append("")
    lines.append(f"- generated_at_utc: `{now.isoformat().replace('+00:00', 'Z')}`")
    lines.append(f"- window_start_utc: `{since.isoformat().replace('+00:00', 'Z')}`")
    lines.append(f"- total_rows: `{len(rows)}`")
    lines.append("")
    lines.append("## Status Counts")
    lines.append("")
    lines.append("| status | count |")
    lines.append("|---|---:|")
    for status in sorted(counts.keys()):
        lines.append(f"| {status} | {counts[status]} |")
    lines.append("")
    lines.append("## Supported Claims")
    lines.append("")
    if supported:
        for cid in supported:
            lines.append(f"- `{cid}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Active Hypotheses")
    lines.append("")
    for cid in active[:20]:
        lines.append(f"- `{cid}`")
    if len(active) > 20:
        lines.append(f"- ... and {len(active) - 20} more")
    lines.append("")
    lines.append("## Partial Claims")
    lines.append("")
    for cid in partial[:20]:
        lines.append(f"- `{cid}`")
    if len(partial) > 20:
        lines.append(f"- ... and {len(partial) - 20} more")
    lines.append("")
    lines.append(f"## Changed Claim Files ({days}d)")
    lines.append("")
    if changed:
        for path in changed:
            lines.append(f"- `{path}`")
    else:
        lines.append("- none detected in git log window")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This report is generated from `claims/CLAIM_STATUS_MATRIX.yml`.")
    lines.append("- Promotion gating logic runs through `scripts/run_claim_promotion_pipeline.py`.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7, help="Lookback window for changed claim files.")
    parser.add_argument("--output", default=str(OUTPUT_PATH), help="Output markdown path.")
    args = parser.parse_args()

    if not MATRIX_PATH.exists():
        raise SystemExit(f"Matrix file missing: {MATRIX_PATH}")
    matrix = _read_yaml(MATRIX_PATH)
    rows = matrix.get("rows", {})
    if not isinstance(rows, dict):
        raise SystemExit("Invalid matrix rows")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_build_markdown(rows, args.days), encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

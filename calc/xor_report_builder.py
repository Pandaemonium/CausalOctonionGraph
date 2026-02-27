"""
calc/xor_report_builder.py

Build compact, public-facing summaries from XOR ensemble datasets.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _safe_float(v: Any) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def build_ensemble_report(dataset: Dict[str, Any]) -> Dict[str, Any]:
    runs = list(dataset.get("runs", []))
    run_count = int(dataset.get("run_count", len(runs)))
    agg = dict(dataset.get("aggregate_observables", {}))

    scenario_cards: List[Dict[str, Any]] = []
    for row in runs:
        obs = row.get("observables", {})
        scenario_cards.append(
            {
                "scenario_id": row.get("scenario_id"),
                "title": row.get("title", row.get("scenario_id")),
                "steps": row.get("steps"),
                "initial_pair_kind": obs.get("initial_pair_kind"),
                "final_pair_kind": obs.get("final_pair_kind"),
                "pair_kind_entropy_bits": _safe_float(obs.get("pair_kind_entropy_bits")),
                "pair_kind_transition_count": _safe_float(obs.get("pair_kind_transition_count")),
            }
        )

    scenario_cards = sorted(
        scenario_cards,
        key=lambda c: c["pair_kind_entropy_bits"],
        reverse=True,
    )

    headline = {
        "run_count": run_count,
        "avg_pair_kind_entropy_bits": _safe_float(agg.get("avg_pair_kind_entropy_bits")),
        "avg_pair_kind_transition_count": _safe_float(agg.get("avg_pair_kind_transition_count")),
        "pair_kind_totals": agg.get("pair_kind_counts_total", {}),
    }

    return {
        "schema_version": "xor_ensemble_report_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "headline": headline,
        "scenario_cards": scenario_cards,
        "source_dataset_schema": dataset.get("schema_version"),
    }


def render_markdown_report(report: Dict[str, Any]) -> str:
    h = report["headline"]
    lines = [
        "# XOR Ensemble Report",
        "",
        f"Generated: {report['generated_at_utc']}",
        "",
        "## Headline",
        f"- Runs: {h['run_count']}",
        f"- Avg pair-kind entropy (bits): {h['avg_pair_kind_entropy_bits']:.4f}",
        f"- Avg pair-kind transitions: {h['avg_pair_kind_transition_count']:.4f}",
        f"- Pair-kind totals: `{json.dumps(h['pair_kind_totals'], sort_keys=True)}`",
        "",
        "## Scenario Cards",
    ]
    for card in report["scenario_cards"]:
        lines.extend(
            [
                f"- `{card['scenario_id']}` ({card['title']})",
                f"  - steps: {card['steps']}",
                f"  - pair kind: {card['initial_pair_kind']} -> {card['final_pair_kind']}",
                f"  - entropy bits: {card['pair_kind_entropy_bits']:.4f}",
                f"  - transitions: {card['pair_kind_transition_count']:.0f}",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def write_xor_report_artifacts(
    report: Dict[str, Any],
    json_paths: Optional[List[Path]] = None,
    md_paths: Optional[List[Path]] = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_ensemble_report.json")]
    if md_paths is None:
        md_paths = [Path("sources/xor_ensemble_report.md")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    md = render_markdown_report(report)
    for path in md_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def build_report_from_dataset_path(path: str | Path) -> Dict[str, Any]:
    dataset = json.loads(Path(path).read_text(encoding="utf-8"))
    return build_ensemble_report(dataset)


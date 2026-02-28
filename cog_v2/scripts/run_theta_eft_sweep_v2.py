#!/usr/bin/env python3
"""Run THETA v2 continuum-EFT bridge probes and emit artifact files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Sequence

try:
    from cog_v2.calc.theta_eft_map_v2 import build_theta_eft_bridge_payload
except ModuleNotFoundError:
    # Support direct execution: python cog_v2/scripts/run_theta_eft_sweep_v2.py
    REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from cog_v2.calc.theta_eft_map_v2 import build_theta_eft_bridge_payload


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "theta001_eft_bridge_v2.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "theta001_eft_bridge_v2.md"


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def render_markdown(payload: Dict[str, Any]) -> str:
    map_suite = payload["map_suite"]
    map_identification = payload.get("map_identification", {})
    qtop = payload["q_top_proxy_suite"]
    readiness = payload["continuum_eft_bridge_readiness"]
    lines = [
        "# THETA-001 EFT Bridge Probe (v2)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Scope: `{payload['closure_scope']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        "",
        "## Map Suite",
        f"- Map count: {len(map_suite['rows'])}",
        f"- CP-odd all-hold (all maps): `{map_suite['cp_odd_all_hold']}`",
        f"- Zero-anchor all-hold (all maps): `{map_suite['zero_anchor_all_hold']}`",
        "",
        "| Map ID | Mode | CP odd all hold | Zero anchor all hold | Max CP odd violation |",
        "|---|---|---|---|---:|",
    ]
    for row in map_suite["rows"]:
        lines.append(
            f"| {row['map_id']} | {row['mode']} | {row['cp_odd_all_hold']} | "
            f"{row['zero_anchor_all_hold']} | {row['max_cp_odd_violation']} |"
        )

    lines.extend(
        [
            "",
            "## Map Identification",
            f"- Policy ID: `{map_identification.get('policy_id', '')}`",
            f"- Eligible maps: `{map_identification.get('eligible_map_ids', [])}`",
            f"- Selected map: `{map_identification.get('selected_map_id', '')}`",
            f"- Selected unique: `{map_identification.get('selected_unique', False)}`",
        ]
    )

    lines.extend(
        [
            "",
            "## Q_top Proxy Suite",
            f"- CP-odd all hold: `{qtop['cp_odd_all_hold']}`",
            f"- Max abs Q_top proxy: {qtop['max_abs_q_top_proxy']}",
            "",
            "| Case | Q_top proxy | CP-dual Q_top | CP odd holds |",
            "|---|---:|---:|---|",
        ]
    )
    for row in qtop["rows"]:
        lines.append(
            f"| {row['case_id']} | {row['q_top_proxy']} | {row['q_top_proxy_cp_dual']} | {row['cp_odd_holds']} |"
        )

    lines.extend(
        [
            "",
            "## Readiness",
            f"- cp_odd_proxy_consistent: `{readiness['cp_odd_proxy_consistent']}`",
            f"- map_suite_has_cp_odd_candidate: `{readiness['map_suite_has_cp_odd_candidate']}`",
            f"- map_identification_locked: `{readiness.get('map_identification_locked', False)}`",
            f"- full_value_closure_ready: `{readiness['full_value_closure_ready']}`",
            "",
            "## Notes",
            "- This artifact is an EFT-bridge probe, not full continuum closure.",
            "- Non-zero affine offsets are included intentionally to expose zero-anchor violations.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: Dict[str, Any],
    *,
    json_paths: Sequence[Path] | None = None,
    md_paths: Sequence[Path] | None = None,
) -> None:
    j_paths = list(json_paths) if json_paths is not None else [OUT_JSON]
    m_paths = list(md_paths) if md_paths is not None else [OUT_MD]
    for path in j_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_markdown(payload)
    for path in m_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run THETA v2 EFT bridge probe sweep")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write artifacts to cog_v2/sources")
    args = parser.parse_args()

    payload = build_theta_eft_bridge_payload()
    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {_to_repo_path(OUT_JSON)}")
        print(f"Wrote {_to_repo_path(OUT_MD)}")
        return
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    print(
        "theta001_eft_bridge_v2: "
        f"cp_odd_proxy_consistent={payload['continuum_eft_bridge_readiness']['cp_odd_proxy_consistent']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

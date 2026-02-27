"""
RFC-029 weighted Weinberg-angle estimator.

Pipeline:
  1) Run H2 policy-locked weighted observable ablation.
  2) Optionally apply H1 discrete scale-bridge policies.
  3) Emit deterministic artifacts for review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, List

from calc.gauge_scale_bridge import (
    BRIDGE_POLICY_FILE_DEFAULT,
    run_bridge_grid,
)
from calc.weinberg_s4_decomp import POLICY_FILE_DEFAULT, run_h2_ablation

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "sources" / "weinberg_weighted_estimate_results.json"
OUT_MD = ROOT / "sources" / "weinberg_weighted_estimate_results.md"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def to_repo_path(path: Path) -> str:
    try:
        rel = str(path.resolve().relative_to(ROOT.resolve()))
        return rel.replace("\\", "/")
    except ValueError:
        return str(path)


def _best_row(rows: List[Dict[str, object]], key: str) -> Dict[str, object] | None:
    if not rows:
        return None
    return min(rows, key=lambda r: abs(float(r[key])))


def build_payload(include_bridge: bool = True) -> Dict[str, object]:
    h2_rows = run_h2_ablation(POLICY_FILE_DEFAULT)
    h2_best = _best_row(
        [
            {
                "policy_id": row["policy_id"],
                "sin2_theta_w_obs": row["observable"]["sin2_theta_w_obs"],
                "gap_from_target": row["observable"]["gap_from_target"],
                "policy_checksum": row["policy_checksum"],
            }
            for row in h2_rows
        ],
        "gap_from_target",
    )

    bridge_rows: List[Dict[str, object]] = []
    bridge_best = None
    if include_bridge:
        bridge_rows = run_bridge_grid(h2_rows, BRIDGE_POLICY_FILE_DEFAULT)
        bridge_best = _best_row(bridge_rows, "gap_from_target")

    return {
        "rfc": "RFC-029",
        "target_scale": "M_Z",
        "h2_policy_file": to_repo_path(POLICY_FILE_DEFAULT),
        "h2_policy_file_sha256": file_sha256(POLICY_FILE_DEFAULT),
        "h1_bridge_file": to_repo_path(BRIDGE_POLICY_FILE_DEFAULT),
        "h1_bridge_file_sha256": file_sha256(BRIDGE_POLICY_FILE_DEFAULT),
        "h2_rows": h2_rows,
        "h2_best_by_abs_gap": h2_best,
        "h1_enabled": include_bridge,
        "h1_rows": bridge_rows,
        "h1_best_by_abs_gap": bridge_best,
    }


def _format_row_h2(row: Dict[str, object]) -> str:
    obs = row["observable"]
    return (
        f"| {row['policy_id']} | {obs['sin2_theta_w_obs']:.8f} | "
        f"{obs['gap_from_target']:+.8f} | `{row['policy_checksum'][:16]}` |"
    )


def _format_row_h1(row: Dict[str, object]) -> str:
    return (
        f"| {row['uv_policy_id']} | {row['bridge_policy_id']} | "
        f"{row['sin2_theta_w_bridged']:.8f} | {row['gap_from_target']:+.8f} | "
        f"{row['steps']} | {row['attenuation']:.6f} | "
        f"`{row['bridge_policy_checksum'][:16]}` |"
    )


def render_markdown(payload: Dict[str, object]) -> str:
    lines: List[str] = [
        "# RFC-029 Weighted Weinberg Estimate",
        "",
        f"Target scale: `{payload['target_scale']}`",
        "",
        "## Governance",
        f"- H2 policy file: `{payload['h2_policy_file']}`",
        f"- H2 policy file sha256: `{payload['h2_policy_file_sha256']}`",
        f"- H1 bridge file: `{payload['h1_bridge_file']}`",
        f"- H1 bridge file sha256: `{payload['h1_bridge_file_sha256']}`",
        "",
        "## H2 Results",
        "",
        "| H2 policy | sin^2(theta_W)_obs | Gap from target | Policy checksum |",
        "|---|---:|---:|---|",
    ]
    for row in payload["h2_rows"]:
        lines.append(_format_row_h2(row))

    h2_best = payload["h2_best_by_abs_gap"]
    if h2_best:
        lines.extend(
            [
                "",
                f"Best H2 (abs gap): `{h2_best['policy_id']}` with gap `{h2_best['gap_from_target']:+.8f}`",
            ]
        )

    if payload["h1_enabled"]:
        lines.extend(
            [
                "",
                "## H1 Bridge Results",
                "",
                "| H2 policy | H1 bridge policy | Bridged sin^2(theta_W) | Gap from target | Steps | Attenuation | Bridge checksum |",
                "|---|---|---:|---:|---:|---:|---|",
            ]
        )
        for row in payload["h1_rows"]:
            lines.append(_format_row_h1(row))

        h1_best = payload["h1_best_by_abs_gap"]
        if h1_best:
            lines.extend(
                [
                    "",
                    "Best H1+H2 (abs gap): "
                    f"`{h1_best['uv_policy_id']} + {h1_best['bridge_policy_id']}` "
                    f"with gap `{h1_best['gap_from_target']:+.8f}`",
                ]
            )

    lines.extend(
        [
            "",
            "## Notes",
            "- This report is descriptive, not a proof of mechanism.",
            "- Policies are predeclared; no output-driven tuning was applied.",
            "- Promotion of WEINBERG-001 requires RFC-029 acceptance gates.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(payload: Dict[str, object]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="RFC-029 weighted Weinberg estimator")
    parser.add_argument(
        "--skip-bridge",
        action="store_true",
        help="Only run H2 weighted observable, skip H1 bridge policies.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print payload JSON to stdout.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Do not write sources artifacts.",
    )
    args = parser.parse_args()

    payload = build_payload(include_bridge=not args.skip_bridge)
    if not args.no_write:
        write_artifacts(payload)
        print(f"Wrote {OUT_JSON}")
        print(f"Wrote {OUT_MD}")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

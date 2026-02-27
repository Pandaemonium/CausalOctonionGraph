"""
Run RFC-029 H2 ablation across all predeclared policies and write artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path

from calc.weinberg_s4_decomp import POLICY_FILE_DEFAULT, run_h2_ablation

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "sources" / "weinberg_h2_ablation_results.json"
OUT_MD = ROOT / "sources" / "weinberg_h2_ablation_results.md"


def _render_markdown(rows: list[dict]) -> str:
    if not rows:
        return "# RFC-029 H2 Ablation Results\n\nNo rows generated.\n"

    target = rows[0]["target_sin2_theta_w"]
    scale = rows[0]["target_scale"]
    lines = [
        "# RFC-029 H2 Ablation Results",
        "",
        f"Target: sin^2(theta_W) = {target:.8f} at scale {scale}",
        "",
        "| Policy ID | sin^2(theta_W)_obs | Gap from target | Policy checksum |",
        "|---|---:|---:|---|",
    ]
    for row in rows:
        obs = row["observable"]
        lines.append(
            "| {pid} | {val:.8f} | {gap:+.8f} | `{chk}` |".format(
                pid=row["policy_id"],
                val=obs["sin2_theta_w_obs"],
                gap=obs["gap_from_target"],
                chk=row["policy_checksum"][:16],
            )
        )

    lines.extend(
        [
            "",
            "## Governance",
            "- Policies were loaded from `calc/weinberg_h2_policies.json`.",
            "- No policy selection by output was performed.",
            "- Structural S4 invariants are validated before evaluation.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = run_h2_ablation(POLICY_FILE_DEFAULT)
    OUT_JSON.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_markdown(rows), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()


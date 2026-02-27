"""
Deterministic ALPHA-001 simulation scan over full-cone preconditioned scenarios.

This script does not claim a derivation. It produces reproducible simulation-backed
proxy tables from predeclared conditions:
1) full-cone site-count proxy,
2) electron exact-cycle tick proxy,
3) simple hybrid proxy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONDITIONS = Path(__file__).with_name("alpha_simulation_conditions.json")
OUT_JSON = ROOT / "sources" / "alpha_simulation_scan.json"
OUT_MD = ROOT / "sources" / "alpha_simulation_scan.md"


def _sha(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load_conditions(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_CONDITIONS
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def validate_conditions(data: dict[str, Any]) -> None:
    if data.get("mode") != "deterministic_full_cone_preconditioned":
        raise ValueError("conditions.mode must be deterministic_full_cone_preconditioned")
    if "target" not in data or "alpha" not in data["target"]:
        raise ValueError("conditions.target.alpha is required")
    if "conditions" not in data or not isinstance(data["conditions"], list):
        raise ValueError("conditions list is required")
    seen: set[str] = set()
    for row in data["conditions"]:
        cid = row.get("condition_id")
        if not cid:
            raise ValueError("each condition must have condition_id")
        if cid in seen:
            raise ValueError(f"duplicate condition_id: {cid}")
        seen.add(cid)
        depth = int(row.get("cone_depth", -1))
        if depth < 0:
            raise ValueError(f"{cid}: cone_depth must be >= 0")


def _full_cone_site_count(depth: int) -> int:
    # 1+1D light-cone lattice count: sum_{t=0..d} (2t+1) = (d+1)^2
    return (depth + 1) * (depth + 1)


def _ce_calibration_locked(n_vacuum: int) -> dict[str, int]:
    """
    Locked RFC-012/QED calibration identities (deterministic, no fitting):
      Ce_exact = 4
      Ce_L1 = 2
      tick_per_cycle = n_vacuum + 1
      Ce_ticks_exact = Ce_exact * tick_per_cycle
    """
    ce_exact = 4
    ce_l1 = 2
    tick_per_cycle = n_vacuum + 1
    return {
        "Ce_exact": ce_exact,
        "Ce_L1": ce_l1,
        "tick_per_cycle": tick_per_cycle,
        "Ce_ticks_exact": ce_exact * tick_per_cycle,
    }


def run_condition(condition: dict[str, Any], target_alpha: float) -> dict[str, Any]:
    cid = condition["condition_id"]
    depth = int(condition["cone_depth"])
    ce = _ce_calibration_locked(depth)

    cone_sites = _full_cone_site_count(depth)
    ce_ticks_exact = int(ce["Ce_ticks_exact"])

    proxies = {
        "alpha_proxy_cone_sites": 1.0 / float(cone_sites),
        "alpha_proxy_cycle_ticks": 1.0 / float(ce_ticks_exact),
        "alpha_proxy_hybrid_sites_plus_ticks": 1.0 / float(cone_sites + ce_ticks_exact),
    }
    gaps = {k: abs(v - target_alpha) / target_alpha for k, v in proxies.items()}
    best_proxy_id = min(gaps, key=gaps.get)

    replay_payload = {
        "condition_id": cid,
        "cone_depth": depth,
        "cone_sites": cone_sites,
        "ce_ticks_exact": ce_ticks_exact,
        "proxies": proxies,
    }
    return {
        "condition_id": cid,
        "description": condition.get("description", ""),
        "cone_depth": depth,
        "full_cone_sites": cone_sites,
        "ce_exact": int(ce["Ce_exact"]),
        "ce_l1": int(ce["Ce_L1"]),
        "ce_ticks_exact": ce_ticks_exact,
        "tick_per_cycle": int(ce["tick_per_cycle"]),
        "proxies": proxies,
        "relative_gaps": gaps,
        "best_proxy_id": best_proxy_id,
        "best_proxy_value": proxies[best_proxy_id],
        "best_proxy_relative_gap": gaps[best_proxy_id],
        "replay_hash": _sha(replay_payload),
    }


def run_scan(path: Path | None = None) -> list[dict[str, Any]]:
    data = load_conditions(path)
    validate_conditions(data)
    target_alpha = float(data["target"]["alpha"])
    return [run_condition(c, target_alpha) for c in data["conditions"]]


def _render_markdown(data: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    target = float(data["target"]["alpha"])
    lines = [
        "# ALPHA-001 Deterministic Full-Cone Simulation Scan",
        "",
        f"Target alpha: {target:.13f} ({data['target']['source']}, {data['target']['scale']})",
        "",
        "| Condition | Cone depth | Cone sites | Ce_ticks_exact | Best proxy | Best value | Rel gap | Replay hash |",
        "|---|---:|---:|---:|---|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            "| {cid} | {d} | {sites} | {ticks} | {pid} | {val:.12f} | {gap:.2%} | `{rh}` |".format(
                cid=r["condition_id"],
                d=r["cone_depth"],
                sites=r["full_cone_sites"],
                ticks=r["ce_ticks_exact"],
                pid=r["best_proxy_id"],
                val=r["best_proxy_value"],
                gap=r["best_proxy_relative_gap"],
                rh=r["replay_hash"][:16],
            )
        )

    best_global = min(rows, key=lambda r: r["best_proxy_relative_gap"])
    lines.extend(
        [
            "",
            "## Governance",
            "- All conditions are predeclared in `calc/alpha_simulation_conditions.json`.",
            "- Full-cone preconditioning is enforced by condition schema (`cone_depth`, full-cone site count).",
            "- No fitted attenuation parameters are used.",
            "",
            "## Best Row",
            (
                f"- `{best_global['condition_id']}` "
                f"({best_global['best_proxy_id']} = {best_global['best_proxy_value']:.12f}, "
                f"relative gap {best_global['best_proxy_relative_gap']:.2%})"
            ),
            "",
            "## Note",
            "These are simulation-backed proxy observables, not a closed first-principles derivation.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic full-cone alpha simulation scan")
    parser.add_argument("--conditions-file", type=Path, default=DEFAULT_CONDITIONS)
    parser.add_argument("--json", action="store_true", help="Emit JSON rows")
    parser.add_argument("--write-sources", action="store_true", help="Write sources artifacts")
    args = parser.parse_args()

    data = load_conditions(args.conditions_file)
    rows = run_scan(args.conditions_file)

    if args.write_sources:
        payload = {
            "schema_version": "alpha_simulation_scan_v1",
            "conditions_checksum": _sha(data),
            "rows": rows,
        }
        OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUT_MD.write_text(_render_markdown(data, rows), encoding="utf-8")
        print(f"Wrote {OUT_JSON}")
        print(f"Wrote {OUT_MD}")
        return

    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return

    for r in rows:
        print(
            f"{r['condition_id']}: best={r['best_proxy_id']} "
            f"value={r['best_proxy_value']:.12f} gap={r['best_proxy_relative_gap']:.2%}"
        )


if __name__ == "__main__":
    main()

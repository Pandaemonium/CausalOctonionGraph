"""Diagnose why Omega_hat dominates RFC-011 generation-equivalence mismatch."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any, Dict, List, Tuple

from cog_v3.calc import build_v3_generation_aligned_equivalence_panel_v1 as panel
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]

IN_PANEL_JSON = ROOT / "cog_v3" / "sources" / "v3_generation_aligned_equivalence_panel_v1.json"
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_omega_hat_diagnostic_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_omega_hat_diagnostic_v1.md"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_omega_hat_diagnostic_v1.py"
PANEL_SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_generation_aligned_equivalence_panel_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _quantiles(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"p10": 0.0, "p50": 0.0, "p90": 0.0}
    v = sorted(float(x) for x in values)
    n = len(v)
    return {
        "p10": float(v[max(0, int(0.10 * (n - 1)))]),
        "p50": float(v[max(0, int(0.50 * (n - 1)))]),
        "p90": float(v[max(0, int(0.90 * (n - 1)))]),
    }


def _median(values: List[float]) -> float:
    if not values:
        return 0.0
    return float(statistics.median([float(x) for x in values]))


def _system_key(row: Dict[str, Any]) -> Tuple[str, int, str, str, int, int, int]:
    return (
        str(row["system_id"]),
        int(row["seed_id"]),
        str(row["boundary_mode"]),
        str(row["orientation"]),
        int(row["size"][0]),
        int(row["size"][1]),
        int(row["size"][2]),
    )


def _pair_key(pair_row: Dict[str, Any], *, use_lhs: bool) -> Tuple[str, int, str, str, int, int, int]:
    sid = str(pair_row["lhs_system_id"] if use_lhs else pair_row["rhs_system_id"])
    return (
        sid,
        int(pair_row["seed_id"]),
        str(pair_row["boundary_mode"]),
        str(pair_row["orientation"]),
        int(pair_row["size_x"]),
        int(pair_row["size_y"]),
        int(pair_row["size_z"]),
    )


def _load_or_build_panel(*, global_seed: int, quick: bool, refresh: bool) -> Dict[str, Any]:
    if bool(refresh) or (not IN_PANEL_JSON.exists()):
        payload = panel.build_payload(global_seed=int(global_seed), quick=bool(quick))
        panel.write_artifacts(payload)
        return payload
    return json.loads(IN_PANEL_JSON.read_text(encoding="utf-8"))


def _render_md(payload: Dict[str, Any]) -> str:
    s = payload["summary"]
    flags = payload["diagnostic_flags"]
    lines = [
        "# v3 Omega Hat Diagnostic (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- pair_rows_analyzed: `{int(s['pair_row_count'])}`",
        "",
        "## Core Findings",
        "",
        f"- omega_dominant_rate: `{float(s['omega_dominant_rate']):.4f}`",
        f"- median_omega_share_of_total_delta: `{float(s['median_omega_share']):.4f}`",
        f"- median_omega_relative_delta: `{float(s['median_omega_relative_delta']):.6f}`",
        f"- median_omega_abs_diff: `{float(s['median_omega_abs_diff']):.6f}`",
        f"- sign_flip_rate: `{float(s['sign_flip_rate']):.4f}`",
        "",
        "## Denominator Stress",
        "",
        f"- denom_lt_1e-3_rate: `{float(s['denom_lt_1e3_rate']):.4f}`",
        f"- denom_lt_1e-2_rate: `{float(s['denom_lt_1e2_rate']):.4f}`",
        f"- denom_lt_5e-2_rate: `{float(s['denom_lt_5e2_rate']):.4f}`",
        "",
        "## Interpretation Flags",
        "",
        f"- omega_is_primary_driver: `{bool(flags['omega_is_primary_driver'])}`",
        f"- small_denominator_primary_cause: `{bool(flags['small_denominator_primary_cause'])}`",
        f"- frequent_sign_inversion: `{bool(flags['frequent_sign_inversion'])}`",
        "",
        "## Pair Breakdown",
        "",
        "| pair_id | count | omega_dominant_rate | median_omega_delta | median_omega_abs_diff | sign_flip_rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload["pair_breakdown"]:
        lines.append(
            f"| `{row['pair_id']}` | {int(row['count'])} | {float(row['omega_dominant_rate']):.4f} | "
            f"{float(row['median_omega_relative_delta']):.6f} | {float(row['median_omega_abs_diff']):.6f} | {float(row['sign_flip_rate']):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Top Cases (Omega Relative Delta)",
            "",
            "| pair_id | seed | size | boundary | orientation | omega_lhs | omega_rhs | omega_delta_rel | omega_abs_diff | max_metric |",
            "|---|---:|---|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in payload["top_cases"]:
        sz = f"{int(row['size_x'])}x{int(row['size_y'])}x{int(row['size_z'])}"
        lines.append(
            f"| `{row['pair_id']}` | {int(row['seed_id'])} | `{sz}` | `{row['boundary_mode']}` | `{row['orientation']}` | "
            f"{float(row['omega_lhs']):.6f} | {float(row['omega_rhs']):.6f} | {float(row['omega_relative_delta']):.6f} | "
            f"{float(row['omega_abs_diff']):.6f} | `{row['max_metric_name']}` |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Diagnostic is post-hoc over RFC-011 rows (no new physics claim).",
            "- If `small_denominator_primary_cause=false`, Omega dominance is not mainly a near-zero denominator artifact.",
        ]
    )
    return "\n".join(lines)


def build_payload(*, global_seed: int = 1337, quick: bool = False, refresh_panel: bool = False, top_k: int = 16) -> Dict[str, Any]:
    panel_payload = _load_or_build_panel(global_seed=int(global_seed), quick=bool(quick), refresh=bool(refresh_panel))
    if str(panel_payload.get("schema_version", "")) != "v3_generation_aligned_equivalence_panel_v1":
        raise ValueError("Unexpected input schema for generation panel.")

    system_rows = panel_payload.get("system_rows", [])
    pair_rows = panel_payload.get("pair_rows", [])
    by_system: Dict[Tuple[str, int, str, str, int, int, int], Dict[str, Any]] = {
        _system_key(r): r for r in system_rows
    }

    diag_rows: List[Dict[str, Any]] = []
    for pr in pair_rows:
        lhs = by_system[_pair_key(pr, use_lhs=True)]
        rhs = by_system[_pair_key(pr, use_lhs=False)]
        omega_lhs = float(lhs["Omega_hat"])
        omega_rhs = float(rhs["Omega_hat"])
        abs_diff = float(abs(omega_lhs - omega_rhs))
        denom = float(max(abs(omega_lhs), abs(omega_rhs), 1e-9))
        rel = float(abs_diff / denom)
        sym_rel = float(abs_diff / max(1e-9, abs(omega_lhs) + abs(omega_rhs)))
        deltas = {str(km): float(v) for km, v in pr["delta_metrics"].items()}
        max_metric_name = max(deltas.items(), key=lambda kv: kv[1])[0]
        total = float(sum(deltas.values()))
        omega_share = float(deltas.get("Omega_hat", 0.0) / total) if total > 0 else 0.0

        diag_rows.append(
            {
                "pair_id": str(pr["pair_id"]),
                "seed_id": int(pr["seed_id"]),
                "size_x": int(pr["size_x"]),
                "size_y": int(pr["size_y"]),
                "size_z": int(pr["size_z"]),
                "boundary_mode": str(pr["boundary_mode"]),
                "orientation": str(pr["orientation"]),
                "omega_lhs": float(omega_lhs),
                "omega_rhs": float(omega_rhs),
                "omega_abs_diff": float(abs_diff),
                "omega_denominator": float(denom),
                "omega_relative_delta": float(rel),
                "omega_symmetric_relative_delta": float(sym_rel),
                "omega_share_of_total_delta": float(omega_share),
                "omega_is_max_metric": bool(max_metric_name == "Omega_hat"),
                "max_metric_name": str(max_metric_name),
                "sign_flip": bool(omega_lhs * omega_rhs < 0.0),
                "delta_metrics": deltas,
            }
        )

    pair_row_count = int(len(diag_rows))
    omega_rel = [float(r["omega_relative_delta"]) for r in diag_rows]
    omega_abs = [float(r["omega_abs_diff"]) for r in diag_rows]
    omega_share = [float(r["omega_share_of_total_delta"]) for r in diag_rows]
    denoms = [float(r["omega_denominator"]) for r in diag_rows]
    omega_dominant_rate = float(
        sum(1 for r in diag_rows if bool(r["omega_is_max_metric"])) / max(1, pair_row_count)
    )
    sign_flip_rate = float(sum(1 for r in diag_rows if bool(r["sign_flip"])) / max(1, pair_row_count))

    metric_names = ["T_cycle", "R_hat", "Omega_hat", "S_stab", "V_hat"]
    metric_medians: Dict[str, float] = {}
    for mn in metric_names:
        metric_medians[str(mn)] = _median([float(r["delta_metrics"][mn]) for r in diag_rows])

    pair_breakdown: List[Dict[str, Any]] = []
    for pid in sorted(set(str(r["pair_id"]) for r in diag_rows)):
        rows = [r for r in diag_rows if str(r["pair_id"]) == pid]
        pair_breakdown.append(
            {
                "pair_id": str(pid),
                "count": int(len(rows)),
                "omega_dominant_rate": float(
                    sum(1 for r in rows if bool(r["omega_is_max_metric"])) / max(1, len(rows))
                ),
                "median_omega_relative_delta": float(_median([float(r["omega_relative_delta"]) for r in rows])),
                "median_omega_abs_diff": float(_median([float(r["omega_abs_diff"]) for r in rows])),
                "median_denominator": float(_median([float(r["omega_denominator"]) for r in rows])),
                "sign_flip_rate": float(sum(1 for r in rows if bool(r["sign_flip"])) / max(1, len(rows))),
            }
        )

    top_rows = sorted(diag_rows, key=lambda r: float(r["omega_relative_delta"]), reverse=True)[: max(1, int(top_k))]
    summary = {
        "pair_row_count": int(pair_row_count),
        "omega_dominant_rate": float(omega_dominant_rate),
        "median_omega_share": float(_median(omega_share)),
        "median_omega_relative_delta": float(_median(omega_rel)),
        "median_omega_abs_diff": float(_median(omega_abs)),
        "median_omega_denominator": float(_median(denoms)),
        "sign_flip_rate": float(sign_flip_rate),
        "denom_lt_1e3_rate": float(sum(1 for d in denoms if d < 1e-3) / max(1, pair_row_count)),
        "denom_lt_1e2_rate": float(sum(1 for d in denoms if d < 1e-2) / max(1, pair_row_count)),
        "denom_lt_5e2_rate": float(sum(1 for d in denoms if d < 5e-2) / max(1, pair_row_count)),
        "omega_relative_quantiles": _quantiles(omega_rel),
        "omega_abs_quantiles": _quantiles(omega_abs),
        "denominator_quantiles": _quantiles(denoms),
        "delta_metric_medians": metric_medians,
    }
    diagnostic_flags = {
        "omega_is_primary_driver": bool(omega_dominant_rate >= 0.70 and summary["median_omega_share"] >= 0.40),
        "small_denominator_primary_cause": bool(summary["denom_lt_1e2_rate"] >= 0.50),
        "frequent_sign_inversion": bool(sign_flip_rate >= 0.40),
    }

    payload: Dict[str, Any] = {
        "schema_version": "v3_omega_hat_diagnostic_v1",
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "global_seed": int(global_seed),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "panel_script": PANEL_SCRIPT_REPO_PATH,
        "panel_script_sha256": _sha_file(ROOT / PANEL_SCRIPT_REPO_PATH),
        "panel_artifact": str(IN_PANEL_JSON.relative_to(ROOT)),
        "panel_artifact_sha256": _sha_file(IN_PANEL_JSON) if IN_PANEL_JSON.exists() else "",
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "summary": summary,
        "diagnostic_flags": diagnostic_flags,
        "pair_breakdown": pair_breakdown,
        "top_cases": top_rows,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--global-seed", type=int, default=1337)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--refresh-panel", action="store_true")
    parser.add_argument("--top-k", type=int, default=16)
    args = parser.parse_args()

    payload = build_payload(
        global_seed=int(args.global_seed),
        quick=bool(args.quick),
        refresh_panel=bool(args.refresh_panel),
        top_k=int(args.top_k),
    )
    write_artifacts(payload)
    s = payload["summary"]
    print(
        "v3_omega_hat_diagnostic_v1: "
        f"rows={int(s['pair_row_count'])}, "
        f"omega_dominant_rate={float(s['omega_dominant_rate']):.4f}, "
        f"median_omega_delta={float(s['median_omega_relative_delta']):.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


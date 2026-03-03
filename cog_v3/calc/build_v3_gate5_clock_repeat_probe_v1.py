"""Probe gate-5 failure causes for fixed-manifest kernel candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from cog_v3.calc import build_v3_fixed_manifest_kernel_gate_stack_v1 as gate_stack
from cog_v3.calc import run_v3_overnight_autonomous_v1 as runner
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]

IN_GATE_STACK_JSON = ROOT / "cog_v3" / "sources" / "v3_fixed_manifest_kernel_gate_stack_v1.json"
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_gate5_clock_repeat_probe_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_gate5_clock_repeat_probe_v1.md"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_gate5_clock_repeat_probe_v1.py"
GATE_STACK_SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_fixed_manifest_kernel_gate_stack_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _load_or_build_manifest(*, backend: str, global_seed: int, quick: bool, refresh: bool) -> Dict[str, Any]:
    if bool(refresh) or (not IN_GATE_STACK_JSON.exists()):
        payload = gate_stack.build_payload(backend=str(backend), global_seed=int(global_seed), quick=bool(quick))
        gate_stack.write_artifacts(payload)
        return payload
    return json.loads(IN_GATE_STACK_JSON.read_text(encoding="utf-8"))


def _gate5_components(row: Dict[str, Any]) -> Dict[str, Any]:
    cm = row["clock_metrics"]
    recurrence_ok = bool(row.get("scan_checks", {}).get("any_recurrence", False))
    drift_ok = bool(float(cm["clock_signature_drift"]) <= 0.35)
    collapse_ok = bool(not bool(cm["clock_collapse_flag"]))
    noise_ok = bool(not bool(cm["clock_noise_plateau_flag"]))
    gate5_expected = bool(recurrence_ok and drift_ok and collapse_ok and noise_ok)

    fail_reasons: List[str] = []
    if not recurrence_ok:
        fail_reasons.append("scan_any_recurrence_false")
    if not drift_ok:
        fail_reasons.append("clock_signature_drift_gt_0p35")
    if not collapse_ok:
        fail_reasons.append("clock_collapse_true")
    if not noise_ok:
        fail_reasons.append("clock_noise_plateau_true")

    return {
        "scan_recurrence_ok": bool(recurrence_ok),
        "clock_drift_ok": bool(drift_ok),
        "clock_collapse_ok": bool(collapse_ok),
        "clock_noise_ok": bool(noise_ok),
        "gate5_expected_from_components": bool(gate5_expected),
        "fail_reasons": fail_reasons,
    }


def _repeat_horizon_probe(
    *,
    backend: str,
    channel_policy_id: str,
    global_seed: int,
    candidate_index: int,
    horizons: List[int],
    seeds_per_horizon: int,
) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for h in horizons:
        for s in range(max(1, int(seeds_per_horizon))):
            policy_seed = int(global_seed) + 13007 * int(candidate_index) + 101 * int(h) + 17 * int(s)
            warmup = max(8, int(h) // 6)
            probe = gate_stack._clock_signature_probe(  # noqa: SLF001
                backend=str(backend),
                channel_policy_id=str(channel_policy_id),
                policy_seed=int(policy_seed),
                ticks=int(h),
                warmup_ticks=int(warmup),
            )
            fr = probe.get("first_repeat")
            rows.append(
                {
                    "horizon_ticks": int(h),
                    "seed_idx": int(s),
                    "policy_seed": int(policy_seed),
                    "warmup_ticks": int(warmup),
                    "repeat_found": bool(fr is not None),
                    "repeat_period": int(fr["period"]) if isinstance(fr, dict) and "period" in fr else None,
                    "clock_signature_drift": float(probe["clock_signature_drift"]),
                    "clock_collapse_flag": bool(probe["clock_collapse_flag"]),
                    "clock_noise_plateau_flag": bool(probe["clock_noise_plateau_flag"]),
                    "clock_quality": float(probe["clock_quality"]),
                }
            )

    by_h: Dict[int, List[Dict[str, Any]]] = {}
    for r in rows:
        by_h.setdefault(int(r["horizon_ticks"]), []).append(r)

    horizon_summary: List[Dict[str, Any]] = []
    for h in sorted(by_h.keys()):
        rr = by_h[h]
        repeat_rate = float(sum(1 for x in rr if bool(x["repeat_found"])) / max(1, len(rr)))
        periods = [int(x["repeat_period"]) for x in rr if x["repeat_period"] is not None]
        drifts = [float(x["clock_signature_drift"]) for x in rr]
        collapse_rate = float(sum(1 for x in rr if bool(x["clock_collapse_flag"])) / max(1, len(rr)))
        noise_rate = float(sum(1 for x in rr if bool(x["clock_noise_plateau_flag"])) / max(1, len(rr)))
        horizon_summary.append(
            {
                "horizon_ticks": int(h),
                "seed_count": int(len(rr)),
                "repeat_rate": float(repeat_rate),
                "median_repeat_period": float(sorted(periods)[len(periods) // 2]) if periods else None,
                "median_drift": float(sorted(drifts)[len(drifts) // 2]) if drifts else 0.0,
                "collapse_rate": float(collapse_rate),
                "noise_rate": float(noise_rate),
            }
        )

    return {"rows": rows, "horizon_summary": horizon_summary}


def _scan_recurrence_sweep(
    *,
    backend: str,
    channel_policy_id: str,
    global_seed: int,
    candidate_index: int,
    scan_seed_count: int,
    quick: bool,
) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for s in range(max(1, int(scan_seed_count))):
        seed = int(global_seed) + 17011 * int(candidate_index) + 97 * int(s)
        params = runner.FastScanParams(
            ticks=(40 if bool(quick) else 72),
            size_x=(19 if bool(quick) else 27),
            size_y=9,
            size_z=9,
            stencil_id="cube26",
            thin_step=4,
            max_trials=(3 if bool(quick) else 8),
            global_seed=int(seed),
            channel_policy_id=str(channel_policy_id),
            policy_seed=int(seed + 1003),
        )
        scan = runner.run_fast_motif_scan(params, backend=str(backend))
        checks = scan.get("checks", {})
        rows.append(
            {
                "scan_seed_idx": int(s),
                "global_seed": int(seed),
                "policy_seed": int(seed + 1003),
                "any_recurrence": bool(checks.get("any_recurrence", False)),
                "any_propagating": bool(checks.get("any_propagating", False)),
                "best_score": float(checks.get("best_score", 0.0)),
                "trial_count": int(checks.get("trial_count", 0)),
            }
        )

    recurrence_rate = float(sum(1 for r in rows if bool(r["any_recurrence"])) / max(1, len(rows)))
    propagating_rate = float(sum(1 for r in rows if bool(r["any_propagating"])) / max(1, len(rows)))
    best_scores = sorted(float(r["best_score"]) for r in rows)
    return {
        "rows": rows,
        "summary": {
            "scan_seed_count": int(len(rows)),
            "recurrence_rate": float(recurrence_rate),
            "propagating_rate": float(propagating_rate),
            "median_best_score": float(best_scores[len(best_scores) // 2]) if best_scores else 0.0,
        },
    }


def _classify_bottlenecks(
    *,
    component_status: Dict[str, Any],
    repeat_summary: List[Dict[str, Any]],
    scan_summary: Dict[str, Any],
) -> List[str]:
    issues: List[str] = []
    if not bool(component_status["scan_recurrence_ok"]):
        if float(scan_summary.get("recurrence_rate", 0.0)) < 0.20:
            issues.append("primary:scan_recurrence_absent")
        else:
            issues.append("primary:manifest_recurrence_absent_seed_sensitive")

    if not bool(component_status["clock_drift_ok"]):
        issues.append("primary:clock_signature_drift_high")
    if not bool(component_status["clock_collapse_ok"]):
        issues.append("primary:clock_collapse")
    if not bool(component_status["clock_noise_ok"]):
        issues.append("primary:clock_noise_plateau")

    if repeat_summary:
        max_repeat_rate = max(float(r["repeat_rate"]) for r in repeat_summary)
        if max_repeat_rate <= 0.0:
            issues.append("secondary:no_world_state_repeat_within_horizon")
    return issues


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Gate-5 Clock Repeat Probe (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- backend: `{payload['backend']}`",
        f"- candidate_count: `{int(payload['summary']['candidate_count'])}`",
        "",
        "## Candidate Status",
        "",
        "| kernel_candidate_id | channel_policy_id | manifest_gate5 | scan_recurrence_ok | drift_ok | collapse_ok | noise_ok | likely_bottlenecks |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in payload["candidate_rows"]:
        c = r["component_status"]
        issues = ", ".join(r["likely_bottlenecks"]) if r["likely_bottlenecks"] else "-"
        lines.append(
            f"| `{r['kernel_candidate_id']}` | `{r['channel_policy_id']}` | {bool(r['manifest_gate5'])} | "
            f"{bool(c['scan_recurrence_ok'])} | {bool(c['clock_drift_ok'])} | {bool(c['clock_collapse_ok'])} | {bool(c['clock_noise_ok'])} | {issues} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- manifest_gate5_pass_count: `{int(payload['summary']['manifest_gate5_pass_count'])}`",
            f"- candidates_with_scan_recurrence_rate_lt_0p2: `{int(payload['summary']['scan_recurrence_lt_0p2_count'])}`",
            "",
            "## Notes",
            "",
            "- Gate-5 requires both recurrence from fast scan and clock-structure quality checks.",
            "- Repeat-horizon probe is diagnostic only; it does not modify the fixed-manifest gate contract.",
        ]
    )
    return "\n".join(lines)


def build_payload(
    *,
    backend: str = "numba_cpu",
    global_seed: int = 1337,
    quick: bool = False,
    refresh_manifest: bool = False,
) -> Dict[str, Any]:
    manifest = _load_or_build_manifest(
        backend=str(backend),
        global_seed=int(global_seed),
        quick=bool(quick),
        refresh=bool(refresh_manifest),
    )
    if str(manifest.get("schema_version", "")) != "v3_fixed_manifest_kernel_gate_stack_v1":
        raise ValueError("Unexpected input schema for gate-stack manifest.")

    candidate_rows: List[Dict[str, Any]] = []
    horizons = [64, 128, 192] if bool(quick) else [96, 192, 384]
    seeds_per_horizon = 1 if bool(quick) else 2
    scan_seed_count = 2 if bool(quick) else 4

    for idx, row in enumerate(manifest.get("rows", [])):
        comp = _gate5_components(row)
        repeat_probe = _repeat_horizon_probe(
            backend=str(backend),
            channel_policy_id=str(row["channel_policy_id"]),
            global_seed=int(global_seed),
            candidate_index=int(idx),
            horizons=horizons,
            seeds_per_horizon=int(seeds_per_horizon),
        )
        scan_probe = _scan_recurrence_sweep(
            backend=str(backend),
            channel_policy_id=str(row["channel_policy_id"]),
            global_seed=int(global_seed),
            candidate_index=int(idx),
            scan_seed_count=int(scan_seed_count),
            quick=bool(quick),
        )
        bottlenecks = _classify_bottlenecks(
            component_status=comp,
            repeat_summary=repeat_probe["horizon_summary"],
            scan_summary=scan_probe["summary"],
        )

        candidate_rows.append(
            {
                "kernel_candidate_id": str(row["kernel_candidate_id"]),
                "channel_policy_id": str(row["channel_policy_id"]),
                "manifest_score_total": float(row["score_total"]),
                "manifest_gate5": bool(row["gate_results"]["gate5_clock_structure"]),
                "component_status": comp,
                "manifest_clock_metrics": row["clock_metrics"],
                "manifest_scan_checks": row["scan_checks"],
                "repeat_probe": repeat_probe,
                "scan_recurrence_probe": scan_probe,
                "likely_bottlenecks": bottlenecks,
            }
        )

    gate5_pass_count = int(sum(1 for r in candidate_rows if bool(r["manifest_gate5"])))
    scan_lt_count = int(
        sum(
            1
            for r in candidate_rows
            if float(r["scan_recurrence_probe"]["summary"]["recurrence_rate"]) < 0.20
        )
    )

    payload: Dict[str, Any] = {
        "schema_version": "v3_gate5_clock_repeat_probe_v1",
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "backend": str(backend),
        "global_seed": int(global_seed),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "gate_stack_script": GATE_STACK_SCRIPT_REPO_PATH,
        "gate_stack_script_sha256": _sha_file(ROOT / GATE_STACK_SCRIPT_REPO_PATH),
        "gate_stack_artifact": str(IN_GATE_STACK_JSON.relative_to(ROOT)),
        "gate_stack_artifact_sha256": _sha_file(IN_GATE_STACK_JSON) if IN_GATE_STACK_JSON.exists() else "",
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "candidate_rows": candidate_rows,
        "summary": {
            "candidate_count": int(len(candidate_rows)),
            "manifest_gate5_pass_count": int(gate5_pass_count),
            "scan_recurrence_lt_0p2_count": int(scan_lt_count),
            "horizons": [int(x) for x in horizons],
            "seeds_per_horizon": int(seeds_per_horizon),
            "scan_seed_count": int(scan_seed_count),
        },
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", type=str, default="numba_cpu", choices=["python", "numba_cpu"])
    parser.add_argument("--global-seed", type=int, default=1337)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--refresh-manifest", action="store_true")
    args = parser.parse_args()

    payload = build_payload(
        backend=str(args.backend),
        global_seed=int(args.global_seed),
        quick=bool(args.quick),
        refresh_manifest=bool(args.refresh_manifest),
    )
    write_artifacts(payload)
    print(
        "v3_gate5_clock_repeat_probe_v1: "
        f"candidates={int(payload['summary']['candidate_count'])}, "
        f"manifest_gate5_pass={int(payload['summary']['manifest_gate5_pass_count'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


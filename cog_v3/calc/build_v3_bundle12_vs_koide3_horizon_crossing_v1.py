"""Compare bundle12 vs koide3 drift across horizons."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from cog_v3.calc import build_v3_bundle12_seed_vs_random_ablation_v1 as ab
from cog_v3.calc import build_v3_c12_phase_sector_metrics_v1 as psec
from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_bundle12_vs_koide3_horizon_crossing_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_bundle12_vs_koide3_horizon_crossing_v1.md"
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_bundle12_vs_koide3_horizon_crossing_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Bundle12 vs Koide3 Horizon Crossing (v1)",
        "",
        f"- runs_per_strategy: `{payload['params']['runs_per_strategy']}`",
        f"- horizons: `{payload['params']['horizons']}`",
        "",
        "| ticks | median_drift_koide3 | median_drift_bundle12 | bundle12_minus_koide3 |",
        "|---:|---:|---:|---:|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| {int(row['ticks'])} | {float(row['median_drift_koide3']):.6f} | "
            f"{float(row['median_drift_bundle12']):.6f} | {float(row['delta_bundle12_minus_koide3']):.6f} |"
        )
    lines.extend(
        [
            "",
            f"- crossing_found: `{payload['crossing']['found']}`",
            f"- crossing_tick: `{payload['crossing']['tick']}`",
        ]
    )
    return "\n".join(lines)


def build_payload(*, runs_per_strategy: int = 48, horizons: List[int] | None = None, global_seed: int = 1337) -> Dict[str, Any]:
    hz = horizons if horizons is not None else [100, 300, 600, 1000]
    qmul = c12.build_qmul_table()
    qn = int(qmul.shape[0])
    mul = c12.build_mul_table(phase_count=12, qmul=qmul)
    neighbors = psec._build_neighbors(31, 11, 11, psec._offsets("cube26"), boundary_mode="fixed_vacuum")  # noqa: SLF001
    policy_neighbors = psec._prepare_policy_neighbors(31, 11, 11, "cube26", "fixed_vacuum")  # noqa: SLF001
    preferred = ab._load_preferred_qids()  # noqa: SLF001
    nonidentity = [i for i in range(int(qn * 12)) if int(i) != int(c12.s_identity_id())]

    rows: List[Dict[str, Any]] = []
    for ticks in hz:
        drifts: Dict[str, List[float]] = {"koide3": [], "bundle12": []}
        for st in ("koide3", "bundle12"):
            for run_idx in range(int(runs_per_strategy)):
                params = ab.AblationParams(
                    runs_per_strategy=1,
                    ticks=int(ticks),
                    warmup_ticks=max(10, min(40, int(ticks // 8))),
                    size_x=31,
                    size_y=11,
                    size_z=11,
                    stencil_id="cube26",
                    boundary_mode="fixed_vacuum",
                    channel_policy_id="uniform_all",
                    global_seed=int(global_seed + 997 * ticks),
                )
                out = ab._run_one(  # noqa: SLF001
                    params=params,
                    strategy=str(st),
                    run_idx=int(run_idx),
                    mul=mul,
                    qn=int(qn),
                    neighbors=neighbors,
                    policy_neighbors=policy_neighbors,
                    order12_ids=preferred,
                    nonidentity_ids=nonidentity,
                )
                drifts[str(st)].append(float(out["clock_signature_drift"]))
        md_k = float(np.median(np.asarray(drifts["koide3"], dtype=np.float64)))
        md_b = float(np.median(np.asarray(drifts["bundle12"], dtype=np.float64)))
        rows.append(
            {
                "ticks": int(ticks),
                "median_drift_koide3": md_k,
                "median_drift_bundle12": md_b,
                "delta_bundle12_minus_koide3": float(md_b - md_k),
            }
        )

    crossing_tick = None
    for r in rows:
        if float(r["delta_bundle12_minus_koide3"]) < 0.0:
            crossing_tick = int(r["ticks"])
            break

    payload: Dict[str, Any] = {
        "schema_version": "v3_bundle12_vs_koide3_horizon_crossing_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "params": {
            "runs_per_strategy": int(runs_per_strategy),
            "horizons": [int(x) for x in hz],
            "global_seed": int(global_seed),
        },
        "rows": rows,
        "crossing": {"found": bool(crossing_tick is not None), "tick": int(crossing_tick) if crossing_tick is not None else None},
    }
    payload["replay_hash"] = _sha_payload(payload)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write(_render_md(payload))
        f.write("\n")
    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Run bundle12 vs koide3 horizon crossing study.")
    ap.add_argument("--runs-per-strategy", type=int, default=48)
    ap.add_argument("--horizons", type=str, default="100,300,600,1000")
    ap.add_argument("--global-seed", type=int, default=1337)
    args = ap.parse_args()
    hz = [int(x.strip()) for x in str(args.horizons).split(",") if x.strip()]
    payload = build_payload(runs_per_strategy=int(args.runs_per_strategy), horizons=hz, global_seed=int(args.global_seed))
    print(f"crossing_found={payload['crossing']['found']}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()


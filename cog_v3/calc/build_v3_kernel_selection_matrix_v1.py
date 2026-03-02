"""Build kernel-selection matrix artifacts for v3 (RFC-004)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from cog_v3.calc import run_v3_overnight_autonomous_v1 as runner
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_kernel_selection_matrix_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_kernel_selection_matrix_v1.md"


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Kernel Selection Matrix (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- event_order_policy: `{payload['event_order_policy']}`",
        f"- batches: `{payload['params']['batches']}`",
        "",
        "## Ranked Candidates (Last Batch)",
        "",
        "| rank | kernel_candidate_id | channel_policy_id | score_total | gate0 | gate1 | gate2 | gate3 | gate4 | det_excl | anisotropy |",
        "|---:|---|---|---:|---|---|---|---|---|---:|---:|",
    ]
    rows = payload["last_batch"]["kernel_selection_matrix"]
    for i, r in enumerate(rows, start=1):
        g = r["gate_results"]
        det = float(r["photon_probe"]["detector_exclusivity"])
        an = r["anisotropy_metrics"].get("anisotropy_ratio_max_over_min")
        lines.append(
            f"| {i} | `{r['kernel_candidate_id']}` | `{r['channel_policy_id']}` | {float(r['score_total']):.6f} | "
            f"{g['gate0_contract']} | {g['gate1_transport']} | {g['gate2_detector']} | {g['gate3_isotropy']} | {g['gate4_chirality']} | "
            f"{det:.6f} | {an} |"
        )
    lines.extend(["", "## Notes", "", "- This matrix is exploratory and should be rerun across seed sets before any promotion."])
    return "\n".join(lines)


def build_payload(*, batches: int, global_seed: int, backend: str) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    best_score_so_far = -1e18
    no_improve_streak = 0
    for b in range(int(batches)):
        row = runner._run_batch(  # noqa: SLF001 - internal call by design for matrix runner.
            b,
            backend=str(backend),
            global_seed=int(global_seed),
            no_improve_streak=int(no_improve_streak),
        )
        rows.append(row)
        s = float(row["best_score"])
        if s > best_score_so_far + 1e-12:
            best_score_so_far = s
            no_improve_streak = 0
        else:
            no_improve_streak += 1

    payload: Dict[str, Any] = {
        "schema_version": "v3_kernel_selection_matrix_v1",
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "event_order_policy": "synchronous_parallel_v1",
        "params": {
            "batches": int(batches),
            "global_seed": int(global_seed),
            "backend": str(backend),
        },
        "best_score_so_far": float(best_score_so_far),
        "rows": rows,
        "last_batch": rows[-1] if rows else None,
    }
    return payload


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batches", type=int, default=8)
    parser.add_argument("--global-seed", type=int, default=1337)
    parser.add_argument("--backend", type=str, default="numba_cpu", choices=["python", "numba_cpu"])
    args = parser.parse_args()
    payload = build_payload(batches=int(args.batches), global_seed=int(args.global_seed), backend=str(args.backend))
    write_artifacts(payload)
    print(
        "v3_kernel_selection_matrix_v1: "
        f"batches={int(args.batches)}, best_score={float(payload['best_score_so_far']):.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

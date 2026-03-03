"""Ablation: matched-phase kick vs zero-phase kick in RFC-010 trial bank."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from cog_v3.calc import build_v3_c12_phase_sector_metrics_v1 as psec
from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]

OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_r3_kick_phase_ablation_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_r3_kick_phase_ablation_v1.md"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_r3_kick_phase_ablation_v1.py"
PHASE_SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_c12_phase_sector_metrics_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"

PHASE_COUNT = 12


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _safe_div(a: float, b: float) -> float:
    if abs(float(b)) < 1e-12:
        return 0.0
    return float(a) / float(b)


def _s_id(phase: int, qid: int, qn: int) -> int:
    return int((int(phase) % PHASE_COUNT) * int(qn) + int(qid))


def _build_trials(qn: int, mode: str) -> List[Dict[str, Any]]:
    base = psec._trial_bank(int(qn))  # noqa: SLF001
    out: List[Dict[str, Any]] = []
    for tr in base:
        kick = int(tr["kick_id"])
        if str(mode) == "zero":
            kick_qid = int(kick % int(qn))
            kick = _s_id(0, int(kick_qid), int(qn))
        out.append(
            {
                **tr,
                "kick_id": int(kick),
            }
        )
    return out


def _run_quick_panel(*, global_seed: int, kick_phase_mode: str) -> Dict[str, Any]:
    cfg = psec.PanelConfig(
        panel_id=f"P0_quick_fixed_sync_axial6_{kick_phase_mode}",
        boundary_mode="fixed_vacuum",
        event_order_policy="synchronous_parallel_v1",
        stencil_id="axial6",
        ticks=24,
        warmup_ticks=6,
        runs_per_trial=1,
        size_x=11,
        size_y=7,
        size_z=7,
        channel_policy_id="uniform_all",
    )

    qmul = c12.build_qmul_table()
    mul = c12.build_mul_table(phase_count=PHASE_COUNT, qmul=qmul)
    qn = int(qmul.shape[0])
    vac_id = int(c12.s_identity_id())
    trials = _build_trials(qn, str(kick_phase_mode))
    policy_neighbors = psec._prepare_policy_neighbors(  # noqa: SLF001
        int(cfg.size_x),
        int(cfg.size_y),
        int(cfg.size_z),
        str(cfg.stencil_id),
        str(cfg.boundary_mode),
    )
    neighbors = policy_neighbors["all"]
    n_cells = int(cfg.size_x) * int(cfg.size_y) * int(cfg.size_z)

    delta_counts = np.zeros((PHASE_COUNT,), dtype=np.int64)
    trial_rows: List[Dict[str, Any]] = []

    for ti, tr in enumerate(trials):
        rr = random.Random(int(global_seed) + 10007 * (ti + 1))
        world = np.full((n_cells,), np.uint16(vac_id), dtype=np.uint16)
        psec._apply_seed(  # noqa: SLF001
            world,
            int(cfg.size_x),
            int(cfg.size_y),
            int(cfg.size_z),
            family=str(tr["seed_family"]),
            state_id=int(tr["state_id"]),
            kick_id=int(tr["kick_id"]),
            mul=mul,
        )
        tr_delta = np.zeros((PHASE_COUNT,), dtype=np.int64)
        tr_events = 0

        for t in range(1, int(cfg.ticks) + 1):
            old = world
            world = psec._step_sync(old, neighbors, mul, vac_id=vac_id)  # noqa: SLF001
            if t <= int(cfg.warmup_ticks):
                continue
            old_phase = (old.astype(np.int32) // int(qn)).astype(np.int16)
            new_phase = (world.astype(np.int32) // int(qn)).astype(np.int16)
            d = ((new_phase - old_phase) % PHASE_COUNT).astype(np.int16)
            support = (old != np.uint16(vac_id)) | (world != np.uint16(vac_id))
            if not bool(np.any(support)):
                continue
            bc = np.bincount(d[support].astype(np.int32), minlength=PHASE_COUNT)
            tr_delta += bc.astype(np.int64)
            tr_events += int(np.sum(bc))

        delta_counts += tr_delta
        qn_local = int(qn)
        trial_phase = int(int(tr["state_id"]) // qn_local)
        placed_phase = int((int(trial_phase) + int(tr["kick_id"] // qn_local)) % PHASE_COUNT)
        trial_rows.append(
            {
                "trial_id": str(tr["trial_id"]),
                "seed_family": str(tr["seed_family"]),
                "trial_phase": int(trial_phase),
                "kick_phase": int(int(tr["kick_id"]) // qn_local),
                "placed_phase_proxy": int(placed_phase),
                "events": int(tr_events),
                "d3": int(tr_delta[3] + tr_delta[9]),
                "odd_sum": int(sum(int(tr_delta[i]) for i in [1, 3, 5, 7, 9, 11])),
                "delta_counts": [int(x) for x in tr_delta.tolist()],
            }
        )
        _ = rr  # deterministic RNG retained for parity with panel config style.

    mag = {m: 0 for m in (0, 1, 2, 3, 4, 5, 6)}
    for d_idx in range(PHASE_COUNT):
        m = int(min(d_idx, PHASE_COUNT - d_idx))
        mag[m] += int(delta_counts[d_idx])
    non3 = int(mag[1] + mag[2] + mag[4] + mag[5] + mag[6])
    r3 = _safe_div(float(mag[3]), float(non3))
    odd_sum = int(sum(int(delta_counts[i]) for i in [1, 3, 5, 7, 9, 11]))
    total_events = int(np.sum(delta_counts))

    return {
        "kick_phase_mode": str(kick_phase_mode),
        "panel_id": str(cfg.panel_id),
        "total_events": int(total_events),
        "d3_sum": int(mag[3]),
        "odd_sum": int(odd_sum),
        "non3_sum": int(non3),
        "R3": float(r3),
        "delta_counts": [int(x) for x in delta_counts.tolist()],
        "trial_rows": trial_rows,
    }


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 R3 Kick-Phase Ablation (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        "",
        "| mode | total_events | d3_sum | odd_sum | non3_sum | R3 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in payload["rows"]:
        lines.append(
            f"| `{r['kick_phase_mode']}` | {int(r['total_events'])} | {int(r['d3_sum'])} | "
            f"{int(r['odd_sum'])} | {int(r['non3_sum'])} | {float(r['R3']):.6f} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `matched`: original trial-bank behavior (`kick phase = trial phase`).",
            "- `zero`: ablation behavior (`kick phase = 0`, Q240 kick preserved).",
        ]
    )
    return "\n".join(lines)


def build_payload(*, global_seed: int = 1337) -> Dict[str, Any]:
    rows = [
        _run_quick_panel(global_seed=int(global_seed), kick_phase_mode="matched"),
        _run_quick_panel(global_seed=int(global_seed), kick_phase_mode="zero"),
    ]
    payload: Dict[str, Any] = {
        "schema_version": "v3_r3_kick_phase_ablation_v1",
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "global_seed": int(global_seed),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "phase_metrics_script": PHASE_SCRIPT_REPO_PATH,
        "phase_metrics_script_sha256": _sha_file(ROOT / PHASE_SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "rows": rows,
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
    args = parser.parse_args()

    payload = build_payload(global_seed=int(args.global_seed))
    write_artifacts(payload)
    print(
        "v3_r3_kick_phase_ablation_v1: "
        + ", ".join(
            f"{r['kick_phase_mode']}_R3={float(r['R3']):.6f}, d3={int(r['d3_sum'])}, odd={int(r['odd_sum'])}"
            for r in payload["rows"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


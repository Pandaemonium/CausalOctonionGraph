"""Probe RFC-010 metrics under kick-phase mode changes and odd-phase seed lanes."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from cog_v3.calc import build_v3_c12_phase_sector_metrics_v1 as psec
from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_c12_phase_sector_metrics_kickphase_probe_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_c12_phase_sector_metrics_kickphase_probe_v1.md"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_c12_phase_sector_metrics_kickphase_probe_v1.py"
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


def _trial_bank_custom(qn: int, *, kick_phase_mode: str, add_odd_lane: bool) -> List[Dict[str, Any]]:
    base = psec._trial_bank(int(qn))  # noqa: SLF001
    out: List[Dict[str, Any]] = []
    for tr in base:
        st = int(tr["state_id"])
        kx = int(tr["kick_id"])
        sp = int(st // int(qn))
        kq = int(kx % int(qn))
        kp = int(sp if str(kick_phase_mode) == "matched" else 0)
        out.append({**tr, "kick_id": int(_s_id(kp, int(kq), int(qn)))})

    if bool(add_odd_lane):
        e111 = psec._q_basis_id(7, +1)  # noqa: SLF001
        e001 = psec._q_basis_id(1, +1)  # noqa: SLF001
        for p in (1, 5, 9):
            out.append(
                {
                    "trial_id": f"sheet_x_oddp{p}",
                    "seed_family": "sheet_x",
                    "state_id": _s_id(int(p), int(e111), int(qn)),
                    "kick_id": _s_id(0, int(e001), int(qn)),
                }
            )
    return out


def _run_quick(
    *,
    global_seed: int,
    kick_phase_mode: str,
    add_odd_lane: bool,
) -> Dict[str, Any]:
    cfg = psec.PanelConfig(
        panel_id=f"P0_quick_{kick_phase_mode}_{'odd' if add_odd_lane else 'base'}",
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
    trials = _trial_bank_custom(int(qn), kick_phase_mode=str(kick_phase_mode), add_odd_lane=bool(add_odd_lane))
    policy_neighbors = psec._prepare_policy_neighbors(  # noqa: SLF001
        int(cfg.size_x), int(cfg.size_y), int(cfg.size_z), str(cfg.stencil_id), str(cfg.boundary_mode)
    )
    neighbors = policy_neighbors["all"]
    n_cells = int(cfg.size_x) * int(cfg.size_y) * int(cfg.size_z)

    delta_counts = np.zeros((PHASE_COUNT,), dtype=np.int64)
    transition_counts = np.zeros((3, 3), dtype=np.int64)
    g_old_counts = np.zeros((3,), dtype=np.int64)
    signed_p1 = signed_m1 = signed_p2 = signed_m2 = 0
    run_lengths: List[int] = []
    prev_g = np.full((n_cells,), -1, dtype=np.int8)
    run_len = np.zeros((n_cells,), dtype=np.int32)
    total_events = 0

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
            d_sup = d[support]
            old_phase_sup = old_phase[support]
            new_phase_sup = new_phase[support]
            g_old = (old_phase_sup % 3).astype(np.int8)
            g_new = (new_phase_sup % 3).astype(np.int8)

            bc = np.bincount(d_sup.astype(np.int32), minlength=PHASE_COUNT)
            delta_counts += bc.astype(np.int64)
            total_events += int(d_sup.shape[0])

            g_old_bc = np.bincount(g_old.astype(np.int32), minlength=3)
            g_old_counts += g_old_bc.astype(np.int64)
            mix = (d_sup % 3) != 0
            if bool(np.any(mix)):
                go = g_old[mix].astype(np.int32)
                gn = g_new[mix].astype(np.int32)
                for i in range(go.shape[0]):
                    transition_counts[int(go[i]), int(gn[i])] += 1

            signed = d_sup.copy()
            signed[signed > 6] -= 12
            signed_p1 += int(np.count_nonzero(signed == 1))
            signed_m1 += int(np.count_nonzero(signed == -1))
            signed_p2 += int(np.count_nonzero(signed == 2))
            signed_m2 += int(np.count_nonzero(signed == -2))

            support_idx = np.flatnonzero(support)
            old_g_full = (old_phase % 3).astype(np.int8)
            for idx in support_idx.tolist():
                g = int(old_g_full[int(idx)])
                if int(prev_g[int(idx)]) < 0:
                    prev_g[int(idx)] = np.int8(g)
                    run_len[int(idx)] = np.int32(1)
                elif int(prev_g[int(idx)]) == g:
                    run_len[int(idx)] = np.int32(int(run_len[int(idx)]) + 1)
                else:
                    run_lengths.append(int(run_len[int(idx)]))
                    prev_g[int(idx)] = np.int8(g)
                    run_len[int(idx)] = np.int32(1)
        _ = rr

    for i in range(n_cells):
        if int(run_len[i]) > 0:
            run_lengths.append(int(run_len[i]))

    mag_counts = {m: 0 for m in (0, 1, 2, 3, 4, 5, 6)}
    for d in range(PHASE_COUNT):
        m = int(min(d, PHASE_COUNT - d))
        mag_counts[m] = int(mag_counts.get(m, 0) + int(delta_counts[d]))

    numerator = float(mag_counts[3])
    denominator = float(mag_counts[1] + mag_counts[2] + mag_counts[4] + mag_counts[5] + mag_counts[6])
    r3 = _safe_div(numerator, denominator)
    c3 = _safe_div(
        float(sum(int(delta_counts[d]) for d in range(PHASE_COUNT) if (d % 3) == 0)),
        float(max(1, int(total_events))),
    )
    p_g = np.asarray(g_old_counts, dtype=np.float64) / max(1.0, float(np.sum(g_old_counts)))
    l3_null = _safe_div(1.0, float(max(1e-12, 1.0 - float(np.sum(p_g * p_g)))))
    l3 = float(np.mean(np.asarray(run_lengths, dtype=np.float64))) if run_lengths else 0.0
    a1 = _safe_div(float(signed_p1 - signed_m1), float(signed_p1 + signed_m1))
    a2 = _safe_div(float(signed_p2 - signed_m2), float(signed_p2 + signed_m2))
    odd_sum = int(sum(int(delta_counts[i]) for i in [1, 3, 5, 7, 9, 11]))

    return {
        "panel_id": str(cfg.panel_id),
        "kick_phase_mode": str(kick_phase_mode),
        "add_odd_lane": bool(add_odd_lane),
        "trial_count": int(len(trials)),
        "total_events": int(total_events),
        "delta_counts": [int(x) for x in delta_counts.tolist()],
        "odd_sum": int(odd_sum),
        "d3_sum": int(mag_counts[3]),
        "R3": float(r3),
        "C3": float(c3),
        "L3": float(l3),
        "L3_null_baseline": float(l3_null),
        "A1": float(a1),
        "A2": float(a2),
        "T_counts": transition_counts.astype(int).tolist(),
    }


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 C12 Phase-Sector Kick-Phase Probe (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        "",
        "| kick_phase_mode | add_odd_lane | trial_count | total_events | d3_sum | odd_sum | R3 | C3 | A1 | A2 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in payload["rows"]:
        lines.append(
            f"| `{r['kick_phase_mode']}` | {bool(r['add_odd_lane'])} | {int(r['trial_count'])} | {int(r['total_events'])} | "
            f"{int(r['d3_sum'])} | {int(r['odd_sum'])} | {float(r['R3']):.6f} | {float(r['C3']):.6f} | {float(r['A1']):.6f} | {float(r['A2']):.6f} |"
        )
    return "\n".join(lines)


def build_payload(*, global_seed: int = 1337) -> Dict[str, Any]:
    rows = [
        _run_quick(global_seed=int(global_seed), kick_phase_mode="matched", add_odd_lane=False),
        _run_quick(global_seed=int(global_seed), kick_phase_mode="zero", add_odd_lane=False),
        _run_quick(global_seed=int(global_seed), kick_phase_mode="zero", add_odd_lane=True),
    ]
    payload: Dict[str, Any] = {
        "schema_version": "v3_c12_phase_sector_metrics_kickphase_probe_v1",
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
        "v3_c12_phase_sector_metrics_kickphase_probe_v1: "
        + ", ".join(
            f"{r['kick_phase_mode']}{'_odd' if r['add_odd_lane'] else ''}:R3={float(r['R3']):.6f},d3={int(r['d3_sum'])},odd={int(r['odd_sum'])}"
            for r in payload["rows"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

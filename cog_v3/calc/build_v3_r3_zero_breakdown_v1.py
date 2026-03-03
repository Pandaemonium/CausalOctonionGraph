"""Break down why RFC-010 reports R3=0 in C12 phase-sector metrics."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Sequence

import numpy as np

from cog_v3.calc import build_v3_c12_phase_sector_metrics_v1 as psec
from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]

OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_r3_zero_breakdown_v1.json"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_r3_zero_breakdown_v1.csv"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_r3_zero_breakdown_v1.md"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_r3_zero_breakdown_v1.py"
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


def _panel_set(quick: bool) -> List[psec.PanelConfig]:
    if bool(quick):
        return [
            psec.PanelConfig(
                panel_id="P0_quick_fixed_sync_axial6",
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
            ),
        ]
    return [
        psec.PanelConfig(
            panel_id="P0_fixed_sync_cube26",
            boundary_mode="fixed_vacuum",
            event_order_policy="synchronous_parallel_v1",
            stencil_id="cube26",
            ticks=84,
            warmup_ticks=18,
            runs_per_trial=3,
            size_x=23,
            size_y=9,
            size_z=9,
            channel_policy_id="uniform_all",
        ),
        psec.PanelConfig(
            panel_id="P1_fixed_async_cube26",
            boundary_mode="fixed_vacuum",
            event_order_policy="seeded_async_v1",
            stencil_id="cube26",
            ticks=70,
            warmup_ticks=16,
            runs_per_trial=2,
            size_x=19,
            size_y=9,
            size_z=9,
            channel_policy_id="deterministic_cycle_v1",
        ),
        psec.PanelConfig(
            panel_id="P2_periodic_sync_axial6",
            boundary_mode="periodic",
            event_order_policy="synchronous_parallel_v1",
            stencil_id="axial6",
            ticks=64,
            warmup_ticks=14,
            runs_per_trial=2,
            size_x=19,
            size_y=9,
            size_z=9,
            channel_policy_id="uniform_all",
        ),
    ]


def _run_panel_breakdown(cfg: psec.PanelConfig, *, panel_seed: int) -> Dict[str, Any]:
    qmul = c12.build_qmul_table()
    mul = c12.build_mul_table(phase_count=PHASE_COUNT, qmul=qmul)
    qn = int(qmul.shape[0])
    vac_id = int(c12.s_identity_id())
    trials = psec._trial_bank(qn)  # noqa: SLF001
    policy_neighbors = psec._prepare_policy_neighbors(  # noqa: SLF001
        int(cfg.size_x),
        int(cfg.size_y),
        int(cfg.size_z),
        str(cfg.stencil_id),
        str(cfg.boundary_mode),
    )
    neighbors_default = policy_neighbors["all"]

    n_cells = int(cfg.size_x) * int(cfg.size_y) * int(cfg.size_z)
    row_records: List[Dict[str, Any]] = []

    panel_delta_counts = np.zeros((PHASE_COUNT,), dtype=np.int64)
    panel_mag_counts = {m: 0 for m in (0, 1, 2, 3, 4, 5, 6)}
    panel_total_events = 0
    panel_support_created = 0
    panel_support_persist = 0
    panel_support_annihilated = 0

    for ti, tr in enumerate(trials):
        trial_phase = int(int(tr["state_id"]) // qn)
        trial_gen = int(trial_phase % 3)
        for r in range(int(cfg.runs_per_trial)):
            rr = random.Random(int(panel_seed) + 10007 * (ti + 1) + 7919 * (r + 1))
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

            delta_counts = np.zeros((PHASE_COUNT,), dtype=np.int64)
            support_created = 0
            support_persist = 0
            support_annihilated = 0
            total_events = 0

            old_g_mix_counts = np.zeros((3,), dtype=np.int64)
            mix_transition_counts = np.zeros((3, 3), dtype=np.int64)

            for t in range(1, int(cfg.ticks) + 1):
                combo = psec._policy_combo(str(cfg.channel_policy_id), int(t), int(panel_seed) + r + ti)  # noqa: SLF001
                neighbors = policy_neighbors.get(combo, neighbors_default)
                old = world
                if str(cfg.event_order_policy) == "seeded_async_v1":
                    world = psec._step_async(old, neighbors, mul, vac_id=vac_id, rng=rr)  # noqa: SLF001
                else:
                    world = psec._step_sync(old, neighbors, mul, vac_id=vac_id)  # noqa: SLF001

                if t <= int(cfg.warmup_ticks):
                    continue

                old_nonvac = old != np.uint16(vac_id)
                new_nonvac = world != np.uint16(vac_id)
                support = old_nonvac | new_nonvac
                if not bool(np.any(support)):
                    continue

                old_phase = (old.astype(np.int32) // int(qn)).astype(np.int16)
                new_phase = (world.astype(np.int32) // int(qn)).astype(np.int16)
                d = ((new_phase - old_phase) % PHASE_COUNT).astype(np.int16)
                d_sup = d[support]
                old_phase_sup = old_phase[support]
                new_phase_sup = new_phase[support]
                g_old = (old_phase_sup % 3).astype(np.int8)
                g_new = (new_phase_sup % 3).astype(np.int8)

                bc = np.bincount(d_sup.astype(np.int32), minlength=PHASE_COUNT)
                delta_counts += bc.astype(np.int64)
                total_events += int(d_sup.shape[0])

                created = (~old_nonvac) & new_nonvac
                persist = old_nonvac & new_nonvac
                annih = old_nonvac & (~new_nonvac)
                support_created += int(np.count_nonzero(created))
                support_persist += int(np.count_nonzero(persist))
                support_annihilated += int(np.count_nonzero(annih))

                mix = (d_sup % 3) != 0
                if bool(np.any(mix)):
                    go = g_old[mix].astype(np.int32)
                    gn = g_new[mix].astype(np.int32)
                    old_g_bc = np.bincount(go, minlength=3)
                    old_g_mix_counts += old_g_bc.astype(np.int64)
                    for i in range(go.shape[0]):
                        mix_transition_counts[int(go[i]), int(gn[i])] += 1

            mag_counts = {m: 0 for m in (0, 1, 2, 3, 4, 5, 6)}
            for d_idx in range(PHASE_COUNT):
                mag = int(min(d_idx, PHASE_COUNT - d_idx))
                mag_counts[mag] = int(mag_counts[mag] + int(delta_counts[d_idx]))
            non3 = int(mag_counts[1] + mag_counts[2] + mag_counts[4] + mag_counts[5] + mag_counts[6])
            r3 = _safe_div(float(mag_counts[3]), float(non3))

            row_records.append(
                {
                    "panel_id": str(cfg.panel_id),
                    "trial_id": str(tr["trial_id"]),
                    "seed_family": str(tr["seed_family"]),
                    "trial_phase": int(trial_phase),
                    "trial_generation_g": int(trial_gen),
                    "run_id": int(r),
                    "total_events": int(total_events),
                    "d0": int(delta_counts[0]),
                    "d1": int(delta_counts[1]),
                    "d2": int(delta_counts[2]),
                    "d3": int(delta_counts[3]),
                    "d4": int(delta_counts[4]),
                    "d5": int(delta_counts[5]),
                    "d6": int(delta_counts[6]),
                    "d7": int(delta_counts[7]),
                    "d8": int(delta_counts[8]),
                    "d9": int(delta_counts[9]),
                    "d10": int(delta_counts[10]),
                    "d11": int(delta_counts[11]),
                    "mag_0": int(mag_counts[0]),
                    "mag_1": int(mag_counts[1]),
                    "mag_2": int(mag_counts[2]),
                    "mag_3": int(mag_counts[3]),
                    "mag_4": int(mag_counts[4]),
                    "mag_5": int(mag_counts[5]),
                    "mag_6": int(mag_counts[6]),
                    "r3_local": float(r3),
                    "support_created": int(support_created),
                    "support_persist": int(support_persist),
                    "support_annihilated": int(support_annihilated),
                    "mix_g0_count": int(old_g_mix_counts[0]),
                    "mix_g1_count": int(old_g_mix_counts[1]),
                    "mix_g2_count": int(old_g_mix_counts[2]),
                    "mix_t00": int(mix_transition_counts[0, 0]),
                    "mix_t01": int(mix_transition_counts[0, 1]),
                    "mix_t02": int(mix_transition_counts[0, 2]),
                    "mix_t10": int(mix_transition_counts[1, 0]),
                    "mix_t11": int(mix_transition_counts[1, 1]),
                    "mix_t12": int(mix_transition_counts[1, 2]),
                    "mix_t20": int(mix_transition_counts[2, 0]),
                    "mix_t21": int(mix_transition_counts[2, 1]),
                    "mix_t22": int(mix_transition_counts[2, 2]),
                }
            )

            panel_delta_counts += delta_counts
            for m in panel_mag_counts:
                panel_mag_counts[m] = int(panel_mag_counts[m] + int(mag_counts[m]))
            panel_total_events += int(total_events)
            panel_support_created += int(support_created)
            panel_support_persist += int(support_persist)
            panel_support_annihilated += int(support_annihilated)

    panel_non3 = int(panel_mag_counts[1] + panel_mag_counts[2] + panel_mag_counts[4] + panel_mag_counts[5] + panel_mag_counts[6])
    panel_r3 = _safe_div(float(panel_mag_counts[3]), float(panel_non3))
    panel_summary = {
        "panel_id": str(cfg.panel_id),
        "config": asdict(cfg),
        "total_events": int(panel_total_events),
        "delta_counts": {str(i): int(panel_delta_counts[i]) for i in range(PHASE_COUNT)},
        "mag_counts": {str(m): int(v) for m, v in panel_mag_counts.items()},
        "r3_panel": float(panel_r3),
        "non3_panel": int(panel_non3),
        "d3_panel": int(panel_mag_counts[3]),
        "support_created": int(panel_support_created),
        "support_persist": int(panel_support_persist),
        "support_annihilated": int(panel_support_annihilated),
        "created_rate": _safe_div(float(panel_support_created), float(panel_support_created + panel_support_persist + panel_support_annihilated)),
        "persist_rate": _safe_div(float(panel_support_persist), float(panel_support_created + panel_support_persist + panel_support_annihilated)),
        "annihilated_rate": _safe_div(float(panel_support_annihilated), float(panel_support_created + panel_support_persist + panel_support_annihilated)),
    }
    return {"panel_summary": panel_summary, "rows": row_records}


def _family_summary(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        key = f"{r['panel_id']}|{r['seed_family']}|g{int(r['trial_generation_g'])}"
        groups.setdefault(key, []).append(r)
    out: List[Dict[str, Any]] = []
    for key in sorted(groups.keys()):
        rr = groups[key]
        panel_id, seed_family, gsig = key.split("|")
        total_events = int(sum(int(x["total_events"]) for x in rr))
        d3 = int(sum(int(x["mag_3"]) for x in rr))
        non3 = int(sum(int(x["mag_1"] + x["mag_2"] + x["mag_4"] + x["mag_5"] + x["mag_6"]) for x in rr))
        out.append(
            {
                "panel_id": panel_id,
                "seed_family": seed_family,
                "generation_signature": gsig,
                "sample_count": int(len(rr)),
                "total_events": int(total_events),
                "d3": int(d3),
                "non3": int(non3),
                "r3": float(_safe_div(float(d3), float(non3))),
                "median_r3_local": float(np.median(np.asarray([float(x["r3_local"]) for x in rr], dtype=np.float64))),
            }
        )
    return out


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 R3 Zero Breakdown (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- panel_count: `{len(payload['panel_summaries'])}`",
        f"- row_count: `{int(payload['summary']['row_count'])}`",
        "",
        "## Panel Summary",
        "",
        "| panel_id | total_events | d3_panel | non3_panel | r3_panel | created_rate | persist_rate | annihilated_rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for p in payload["panel_summaries"]:
        lines.append(
            f"| `{p['panel_id']}` | {int(p['total_events'])} | {int(p['d3_panel'])} | {int(p['non3_panel'])} | "
            f"{float(p['r3_panel']):.6f} | {float(p['created_rate']):.4f} | {float(p['persist_rate']):.4f} | {float(p['annihilated_rate']):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Family/Generation Summary",
            "",
            "| panel_id | seed_family | gen_sig | samples | total_events | d3 | non3 | r3 | median_r3_local |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for r in payload["family_summary"]:
        lines.append(
            f"| `{r['panel_id']}` | `{r['seed_family']}` | `{r['generation_signature']}` | {int(r['sample_count'])} | "
            f"{int(r['total_events'])} | {int(r['d3'])} | {int(r['non3'])} | {float(r['r3']):.6f} | {float(r['median_r3_local']):.6f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Flags",
            "",
            f"- any_d3_observed: `{bool(payload['summary']['any_d3_observed'])}`",
            f"- d3_global_rate: `{float(payload['summary']['d3_global_rate']):.8f}`",
            f"- non3_global_rate: `{float(payload['summary']['non3_global_rate']):.8f}`",
            "",
            "## Notes",
            "",
            "- This artifact is diagnostic (root-cause support), not a closure claim.",
            "- `r3_panel = d3_panel / non3_panel` matches RFC-010 denominator convention.",
        ]
    )
    return "\n".join(lines)


def build_payload(*, global_seed: int = 1337, quick: bool = False) -> Dict[str, Any]:
    panel_cfgs = _panel_set(bool(quick))
    panel_summaries: List[Dict[str, Any]] = []
    rows: List[Dict[str, Any]] = []

    for i, cfg in enumerate(panel_cfgs):
        out = _run_panel_breakdown(cfg, panel_seed=int(global_seed) + 9001 * (i + 1))
        panel_summaries.append(out["panel_summary"])
        rows.extend(out["rows"])

    total_events = int(sum(int(r["total_events"]) for r in rows))
    total_d3 = int(sum(int(r["mag_3"]) for r in rows))
    total_non3 = int(sum(int(r["mag_1"] + r["mag_2"] + r["mag_4"] + r["mag_5"] + r["mag_6"]) for r in rows))
    summary = {
        "row_count": int(len(rows)),
        "total_events": int(total_events),
        "total_d3": int(total_d3),
        "total_non3": int(total_non3),
        "r3_global": float(_safe_div(float(total_d3), float(total_non3))),
        "d3_global_rate": float(_safe_div(float(total_d3), float(total_events))),
        "non3_global_rate": float(_safe_div(float(total_non3), float(total_events))),
        "any_d3_observed": bool(total_d3 > 0),
    }
    family_summary = _family_summary(rows)

    payload: Dict[str, Any] = {
        "schema_version": "v3_r3_zero_breakdown_v1",
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "global_seed": int(global_seed),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "phase_metrics_script": PHASE_SCRIPT_REPO_PATH,
        "phase_metrics_script_sha256": _sha_file(ROOT / PHASE_SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "panel_summaries": panel_summaries,
        "family_summary": family_summary,
        "summary": summary,
        "rows": rows,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "panel_id",
                "trial_id",
                "seed_family",
                "trial_phase",
                "trial_generation_g",
                "run_id",
                "total_events",
                "d0",
                "d1",
                "d2",
                "d3",
                "d4",
                "d5",
                "d6",
                "d7",
                "d8",
                "d9",
                "d10",
                "d11",
                "mag_0",
                "mag_1",
                "mag_2",
                "mag_3",
                "mag_4",
                "mag_5",
                "mag_6",
                "r3_local",
                "support_created",
                "support_persist",
                "support_annihilated",
                "mix_g0_count",
                "mix_g1_count",
                "mix_g2_count",
                "mix_t00",
                "mix_t01",
                "mix_t02",
                "mix_t10",
                "mix_t11",
                "mix_t12",
                "mix_t20",
                "mix_t21",
                "mix_t22",
            ]
        )
        for r in payload["rows"]:
            w.writerow(
                [
                    str(r["panel_id"]),
                    str(r["trial_id"]),
                    str(r["seed_family"]),
                    int(r["trial_phase"]),
                    int(r["trial_generation_g"]),
                    int(r["run_id"]),
                    int(r["total_events"]),
                    int(r["d0"]),
                    int(r["d1"]),
                    int(r["d2"]),
                    int(r["d3"]),
                    int(r["d4"]),
                    int(r["d5"]),
                    int(r["d6"]),
                    int(r["d7"]),
                    int(r["d8"]),
                    int(r["d9"]),
                    int(r["d10"]),
                    int(r["d11"]),
                    int(r["mag_0"]),
                    int(r["mag_1"]),
                    int(r["mag_2"]),
                    int(r["mag_3"]),
                    int(r["mag_4"]),
                    int(r["mag_5"]),
                    int(r["mag_6"]),
                    float(r["r3_local"]),
                    int(r["support_created"]),
                    int(r["support_persist"]),
                    int(r["support_annihilated"]),
                    int(r["mix_g0_count"]),
                    int(r["mix_g1_count"]),
                    int(r["mix_g2_count"]),
                    int(r["mix_t00"]),
                    int(r["mix_t01"]),
                    int(r["mix_t02"]),
                    int(r["mix_t10"]),
                    int(r["mix_t11"]),
                    int(r["mix_t12"]),
                    int(r["mix_t20"]),
                    int(r["mix_t21"]),
                    int(r["mix_t22"]),
                ]
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--global-seed", type=int, default=1337)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    payload = build_payload(global_seed=int(args.global_seed), quick=bool(args.quick))
    write_artifacts(payload)
    s = payload["summary"]
    print(
        "v3_r3_zero_breakdown_v1: "
        f"rows={int(s['row_count'])}, "
        f"total_d3={int(s['total_d3'])}, "
        f"r3_global={float(s['r3_global']):.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


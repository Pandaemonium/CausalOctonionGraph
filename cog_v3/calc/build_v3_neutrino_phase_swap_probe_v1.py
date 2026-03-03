"""Probe whether neutrino-like seeds show phase-swap behavior on C12.

This probe tests the hypothesis:
1) neutrino passes through in-phase material,
2) neutrino phase-swaps with out-of-phase material.

It runs matched simulations with:
- seed_q = identity (neutrino-like proxy in current mapping),
- seed_q = e111 (control),
across background phase conditions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from cog_v3.calc import build_v3_c12_phase_sector_metrics_v1 as psec
from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]

OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_neutrino_phase_swap_probe_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_neutrino_phase_swap_probe_v1.md"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_neutrino_phase_swap_probe_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"
PHASE_SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_c12_phase_sector_metrics_v1.py"

PHASE_COUNT = 12


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _q_basis_id(i: int, sign: int = 1) -> int:
    v = [k.Fraction(0, 1) for _ in range(8)]
    v[int(i)] = k.Fraction(int(sign), 1)
    return int(k.ALPHABET_INDEX[tuple(v)])  # type: ignore[index]


def _s_id(phase: int, qid: int, qn: int) -> int:
    return int((int(phase) % PHASE_COUNT) * int(qn) + int(qid))


def _idx(x: int, y: int, z: int, ny: int, nz: int) -> int:
    return (x * ny + y) * nz + z


def _run_case(
    *,
    bg_phase: int,
    seed_phase: int,
    seed_qid: int,
    mat_qid: int,
    ticks: int,
    nx: int,
    ny: int,
    nz: int,
) -> Dict[str, float]:
    qmul = c12.build_qmul_table()
    mul = c12.build_mul_table(phase_count=PHASE_COUNT, qmul=qmul)
    qn = int(qmul.shape[0])
    vac_id = int(c12.s_identity_id())
    neighbors = psec._prepare_policy_neighbors(nx, ny, nz, "cube26", "fixed_vacuum")["all"]  # noqa: SLF001

    bg_sid = _s_id(int(bg_phase), int(mat_qid), qn)
    seed_sid = _s_id(int(seed_phase), int(seed_qid), qn)
    n_cells = int(nx * ny * nz)
    world = np.full((n_cells,), np.uint16(int(bg_sid)), dtype=np.uint16)

    cx, cy, cz = int(nx // 2), int(ny // 2), int(nz // 2)
    center = _idx(cx, cy, cz, int(ny), int(nz))
    world[int(center)] = np.uint16(int(seed_sid))

    local_mask = np.zeros((n_cells,), dtype=bool)
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                if abs(int(x) - cx) + abs(int(y) - cy) + abs(int(z) - cz) <= 2:
                    local_mask[_idx(int(x), int(y), int(z), int(ny), int(nz))] = True

    seed_g = int(seed_phase) % 3

    total_non3_global = 0
    total_all_global = 0
    total_non3_local = 0
    total_all_local = 0

    swap_num_local = 0
    swap_den_local = 0
    swap_num_global = 0
    swap_den_global = 0

    for _ in range(int(ticks)):
        old = world
        world = psec._step_sync(old, neighbors, mul, vac_id=vac_id)  # noqa: SLF001

        old_phase = (old.astype(np.int32) // int(qn)).astype(np.int16)
        new_phase = (world.astype(np.int32) // int(qn)).astype(np.int16)
        d = ((new_phase - old_phase) % PHASE_COUNT).astype(np.int16)
        non3 = (d % 3) != 0

        old_g = (old_phase % 3).astype(np.int16)
        new_g = (new_phase % 3).astype(np.int16)
        off_old = old_g != int(seed_g)
        to_seed = new_g == int(seed_g)

        total_non3_global += int(np.count_nonzero(non3))
        total_all_global += int(non3.size)
        total_non3_local += int(np.count_nonzero(non3[local_mask]))
        total_all_local += int(np.count_nonzero(local_mask))

        swap_num_global += int(np.count_nonzero(to_seed & off_old))
        swap_den_global += int(np.count_nonzero(off_old))
        local_off = off_old & local_mask
        swap_num_local += int(np.count_nonzero(to_seed & local_off))
        swap_den_local += int(np.count_nonzero(local_off))

    return {
        "odd_non3_rate_global": float(total_non3_global) / float(max(1, total_all_global)),
        "odd_non3_rate_local": float(total_non3_local) / float(max(1, total_all_local)),
        "swap_to_seed_g_rate_global": float(swap_num_global) / float(max(1, swap_den_global)),
        "swap_to_seed_g_rate_local": float(swap_num_local) / float(max(1, swap_den_local)),
    }


def build_payload(*, ticks: int, nx: int, ny: int, nz: int) -> Dict[str, Any]:
    neutrino_qid = int(k.IDENTITY_ID)
    control_qid = int(_q_basis_id(7, +1))  # +e111
    mat_qid = int(_q_basis_id(7, +1))

    cases: List[Tuple[str, int, int]] = [
        ("in_phase", 1, 1),
        ("same_gen_diff_subphase", 4, 1),
        ("off_phase_g0", 0, 1),
        ("off_phase_g2", 2, 1),
    ]

    rows: List[Dict[str, Any]] = []
    for seed_label, seed_qid in (
        ("neutrino_like_identity", neutrino_qid),
        ("control_e111", control_qid),
    ):
        for case_id, bg_phase, seed_phase in cases:
            m = _run_case(
                bg_phase=int(bg_phase),
                seed_phase=int(seed_phase),
                seed_qid=int(seed_qid),
                mat_qid=int(mat_qid),
                ticks=int(ticks),
                nx=int(nx),
                ny=int(ny),
                nz=int(nz),
            )
            rows.append(
                {
                    "seed_label": str(seed_label),
                    "seed_qid": int(seed_qid),
                    "seed_q_label": str(k.elem_label(int(seed_qid))),
                    "case_id": str(case_id),
                    "bg_phase": int(bg_phase),
                    "seed_phase": int(seed_phase),
                    **m,
                }
            )

    by_key = {(r["seed_label"], r["case_id"]): r for r in rows}
    deltas: List[Dict[str, Any]] = []
    for case_id, _, _ in cases:
        n = by_key[("neutrino_like_identity", case_id)]
        c = by_key[("control_e111", case_id)]
        deltas.append(
            {
                "case_id": str(case_id),
                "delta_odd_non3_rate_local": float(n["odd_non3_rate_local"]) - float(c["odd_non3_rate_local"]),
                "delta_swap_to_seed_g_rate_local": float(n["swap_to_seed_g_rate_local"]) - float(c["swap_to_seed_g_rate_local"]),
            }
        )

    payload: Dict[str, Any] = {
        "schema_version": "v3_neutrino_phase_swap_probe_v1",
        "kernel_profile": str(k.KERNEL_PROFILE),
        "convention_id": str(k.CONVENTION_ID),
        "ticks": int(ticks),
        "size": [int(nx), int(ny), int(nz)],
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "phase_metrics_script": PHASE_SCRIPT_REPO_PATH,
        "phase_metrics_script_sha256": _sha_file(ROOT / PHASE_SCRIPT_REPO_PATH),
        "rows": rows,
        "control_deltas": deltas,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Neutrino Phase-Swap Probe (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- ticks: `{payload['ticks']}`",
        f"- size: `{payload['size']}`",
        "",
        "| seed_label | case_id | odd_non3_rate_local | swap_to_seed_g_rate_local |",
        "|---|---|---:|---:|",
    ]
    for r in payload["rows"]:
        lines.append(
            f"| `{r['seed_label']}` | `{r['case_id']}` | "
            f"{float(r['odd_non3_rate_local']):.6f} | {float(r['swap_to_seed_g_rate_local']):.6f} |"
        )

    lines.extend(
        [
            "",
            "## Neutrino-vs-Control Deltas",
            "",
            "| case_id | delta_odd_non3_rate_local | delta_swap_to_seed_g_rate_local |",
            "|---|---:|---:|",
        ]
    )
    for d in payload["control_deltas"]:
        lines.append(
            f"| `{d['case_id']}` | {float(d['delta_odd_non3_rate_local']):.6f} | "
            f"{float(d['delta_swap_to_seed_g_rate_local']):.6f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation Hint",
            "",
            "- If deltas are near zero across cases, behavior is phase-generic in current kernel (not neutrino-specific).",
            "- If off-phase cases are high for both seed types, that indicates mismatch-driven dynamics rather than neutrino-unique swapping.",
        ]
    )
    return "\n".join(lines)


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ticks", type=int, default=20)
    ap.add_argument("--size-x", type=int, default=15)
    ap.add_argument("--size-y", type=int, default=9)
    ap.add_argument("--size-z", type=int, default=9)
    args = ap.parse_args()

    payload = build_payload(
        ticks=int(args.ticks),
        nx=int(args.size_x),
        ny=int(args.size_y),
        nz=int(args.size_z),
    )
    write_artifacts(payload)
    print("v3_neutrino_phase_swap_probe_v1: wrote JSON+MD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


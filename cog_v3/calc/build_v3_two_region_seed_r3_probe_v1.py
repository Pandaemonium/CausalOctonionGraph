"""Two-region mixed-phase probe for R3 suppression diagnosis.

Seeds a sharp boundary:
1. left half of box at phase 0,
2. right half of box at phase 3,
with shared Q240 component, then tracks phase-hop channels.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

import numpy as np

from cog_v3.calc import build_v3_c12_phase_sector_metrics_v1 as psec
from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]

OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_two_region_seed_r3_probe_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_two_region_seed_r3_probe_v1.md"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_two_region_seed_r3_probe_v1.py"
PHASE_SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_c12_phase_sector_metrics_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"

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


def _build_two_region_seed(
    *,
    nx: int,
    ny: int,
    nz: int,
    qn: int,
    qid: int,
    left_phase: int,
    right_phase: int,
) -> np.ndarray:
    n = int(nx * ny * nz)
    world = np.zeros((n,), dtype=np.uint16)
    split = int(nx // 2)
    sid_left = _s_id(int(left_phase), int(qid), int(qn))
    sid_right = _s_id(int(right_phase), int(qid), int(qn))
    for x in range(nx):
        sid = sid_left if x < split else sid_right
        for y in range(ny):
            for z in range(nz):
                world[_idx(x, y, z, ny, nz)] = np.uint16(int(sid))
    return world


def _probe_one(
    *,
    panel_id: str,
    stencil_id: str,
    ticks: int,
    nx: int,
    ny: int,
    nz: int,
    left_phase: int,
    right_phase: int,
    qid: int,
) -> Dict[str, Any]:
    qmul = c12.build_qmul_table()
    mul = c12.build_mul_table(phase_count=PHASE_COUNT, qmul=qmul)
    qn = int(qmul.shape[0])
    vac_id = int(c12.s_identity_id())
    world = _build_two_region_seed(
        nx=int(nx),
        ny=int(ny),
        nz=int(nz),
        qn=qn,
        qid=int(qid),
        left_phase=int(left_phase),
        right_phase=int(right_phase),
    )
    policy_neighbors = psec._prepare_policy_neighbors(  # noqa: SLF001
        int(nx),
        int(ny),
        int(nz),
        str(stencil_id),
        "fixed_vacuum",
    )
    neighbors = policy_neighbors["all"]

    split = int(nx // 2)
    boundary_idx: List[int] = []
    for x in (split - 1, split):
        if not (0 <= x < nx):
            continue
        for y in range(ny):
            for z in range(nz):
                boundary_idx.append(_idx(int(x), int(y), int(z), ny, nz))
    bmask = np.zeros((nx * ny * nz,), dtype=bool)
    bmask[np.asarray(boundary_idx, dtype=np.int32)] = True

    delta_counts = np.zeros((PHASE_COUNT,), dtype=np.int64)
    delta_counts_boundary = np.zeros((PHASE_COUNT,), dtype=np.int64)
    phase_hist_snapshots: List[Dict[str, Any]] = []
    snap_ticks = {1, 10, 50}

    for t in range(1, int(ticks) + 1):
        old = world
        world = psec._step_sync(old, neighbors, mul, vac_id=vac_id)  # noqa: SLF001

        old_phase = (old.astype(np.int32) // qn).astype(np.int16)
        new_phase = (world.astype(np.int32) // qn).astype(np.int16)
        d = ((new_phase - old_phase) % PHASE_COUNT).astype(np.int16)

        support = (old != np.uint16(vac_id)) | (world != np.uint16(vac_id))
        if bool(np.any(support)):
            bc = np.bincount(d[support].astype(np.int32), minlength=PHASE_COUNT)
            delta_counts += bc.astype(np.int64)

        support_b = support & bmask
        if bool(np.any(support_b)):
            bc_b = np.bincount(d[support_b].astype(np.int32), minlength=PHASE_COUNT)
            delta_counts_boundary += bc_b.astype(np.int64)

        if t in snap_ticks:
            ph = (world.astype(np.int32) // qn).astype(np.int16)
            hist = np.bincount(ph.astype(np.int32), minlength=PHASE_COUNT)
            hist_b = np.bincount(ph[bmask].astype(np.int32), minlength=PHASE_COUNT)
            phase_hist_snapshots.append(
                {
                    "tick": int(t),
                    "phase_hist_global": [int(x) for x in hist.tolist()],
                    "phase_hist_boundary": [int(x) for x in hist_b.tolist()],
                }
            )

    odd_ids = [1, 3, 5, 7, 9, 11]
    any_d3 = bool(int(delta_counts[3]) > 0 or int(delta_counts[9]) > 0)
    any_d3_boundary = bool(int(delta_counts_boundary[3]) > 0 or int(delta_counts_boundary[9]) > 0)
    any_odd = bool(sum(int(delta_counts[i]) for i in odd_ids) > 0)
    any_odd_boundary = bool(sum(int(delta_counts_boundary[i]) for i in odd_ids) > 0)

    return {
        "panel_id": str(panel_id),
        "stencil_id": str(stencil_id),
        "size": [int(nx), int(ny), int(nz)],
        "ticks": int(ticks),
        "left_phase": int(left_phase),
        "right_phase": int(right_phase),
        "q240_seed_id": int(qid),
        "q240_seed_label": k.elem_label(int(qid)),
        "delta_counts_global": [int(x) for x in delta_counts.tolist()],
        "delta_counts_boundary": [int(x) for x in delta_counts_boundary.tolist()],
        "any_d3_global": bool(any_d3),
        "any_d3_boundary": bool(any_d3_boundary),
        "any_odd_global": bool(any_odd),
        "any_odd_boundary": bool(any_odd_boundary),
        "phase_hist_snapshots": phase_hist_snapshots,
    }


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Two-Region Seed R3 Probe (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        "",
        "| panel_id | stencil | any_d3_global | any_d3_boundary | any_odd_global | any_odd_boundary |",
        "|---|---|---|---|---|---|",
    ]
    for r in payload["rows"]:
        lines.append(
            f"| `{r['panel_id']}` | `{r['stencil_id']}` | {bool(r['any_d3_global'])} | {bool(r['any_d3_boundary'])} | "
            f"{bool(r['any_odd_global'])} | {bool(r['any_odd_boundary'])} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Seed is a sharp boundary: left half `phase=0`, right half `phase=3`, same Q240 element.",
            "- Probe reports both global and boundary-only hop activity.",
            "- Snapshots include phase histograms at ticks 1, 10, 50.",
        ]
    )
    return "\n".join(lines)


def build_payload(*, ticks: int = 60, nx: int = 23, ny: int = 11, nz: int = 11) -> Dict[str, Any]:
    qid = _q_basis_id(7, +1)  # e111
    rows = [
        _probe_one(
            panel_id="P0_axial6_two_region_0_vs_3",
            stencil_id="axial6",
            ticks=int(ticks),
            nx=int(nx),
            ny=int(ny),
            nz=int(nz),
            left_phase=0,
            right_phase=3,
            qid=int(qid),
        ),
        _probe_one(
            panel_id="P1_cube26_two_region_0_vs_3",
            stencil_id="cube26",
            ticks=int(ticks),
            nx=int(nx),
            ny=int(ny),
            nz=int(nz),
            left_phase=0,
            right_phase=3,
            qid=int(qid),
        ),
    ]
    payload: Dict[str, Any] = {
        "schema_version": "v3_two_region_seed_r3_probe_v1",
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
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
    parser.add_argument("--ticks", type=int, default=60)
    parser.add_argument("--size-x", type=int, default=23)
    parser.add_argument("--size-y", type=int, default=11)
    parser.add_argument("--size-z", type=int, default=11)
    args = parser.parse_args()

    payload = build_payload(
        ticks=int(args.ticks),
        nx=int(args.size_x),
        ny=int(args.size_y),
        nz=int(args.size_z),
    )
    write_artifacts(payload)
    d3_any = any(bool(r["any_d3_global"]) for r in payload["rows"])
    odd_any = any(bool(r["any_odd_global"]) for r in payload["rows"])
    print(
        "v3_two_region_seed_r3_probe_v1: "
        f"panels={len(payload['rows'])}, any_d3_global={d3_any}, any_odd_global={odd_any}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


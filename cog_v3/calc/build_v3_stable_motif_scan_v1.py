"""Search for stable/near-stable motifs in COG v3 (3D, fixed-vacuum boundaries).

This scanner is intentionally permissive:
- It reports strict periodic-shift locks and relaxed candidate locks.
- Relaxed mode is robust to boundary artifacts and partially unresolved transients.

Kernel lane:
- closed Octavian-240 alphabet
- multiplication-only update
- explicit convention_id in all artifacts
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_stable_motif_scan_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_stable_motif_scan_v1.md"
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_stable_motif_scan_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"


@dataclass(frozen=True)
class ScanParams:
    ticks: int = 128
    size_x: int = 39
    size_y: int = 11
    size_z: int = 11
    stencil_id: str = "axial6"  # axial6 | cube26 | cube124
    warmup_ticks: int = 28
    min_period: int = 2
    max_period: int = 24
    max_shift_x: int = 6
    repeat_checks: int = 2
    min_support_cells: int = 8
    min_support_match_ratio: float = 0.90
    min_global_match_ratio: float = 0.75
    max_trials: int = 8
    thin_output_step: int = 4


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _basis_id(i: int, sign: int = 1) -> int:
    v = [k.Fraction(0, 1) for _ in range(8)]
    v[int(i)] = k.Fraction(int(sign), 1)
    return int(k.ALPHABET_INDEX[tuple(v)])  # type: ignore[index]


def _index(x: int, y: int, z: int, ny: int, nz: int) -> int:
    return (x * ny + y) * nz + z


def _offsets(stencil_id: str) -> List[Tuple[int, int, int]]:
    sid = str(stencil_id)
    if sid == "axial6":
        return [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
    if sid == "cube26":
        out: List[Tuple[int, int, int]] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    out.append((dx, dy, dz))
        return out
    if sid == "cube124":
        out = []
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                for dz in (-2, -1, 0, 1, 2):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    out.append((dx, dy, dz))
        return out
    raise ValueError(f"Unknown stencil_id: {sid}")


def _neighbor_table(
    nx: int, ny: int, nz: int, offsets: Sequence[Tuple[int, int, int]]
) -> List[List[int]]:
    tab: List[List[int]] = []
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                row: List[int] = []
                for dx, dy, dz in offsets:
                    qx, qy, qz = x + int(dx), y + int(dy), z + int(dz)
                    if 0 <= qx < nx and 0 <= qy < ny and 0 <= qz < nz:
                        row.append(_index(qx, qy, qz, ny, nz))
                    else:
                        row.append(-1)  # fixed-vacuum boundary
                tab.append(row)
    return tab


def _apply_seed(
    world: List[int],
    nx: int,
    ny: int,
    nz: int,
    *,
    family: str,
    state_id: int,
    kick_id: int,
    apply_kick: bool,
) -> Dict[str, Any]:
    cx, cy, cz = nx // 2, ny // 2, nz // 2
    seeded: List[int] = []

    def set_state(x: int, y: int, z: int, sid: int) -> None:
        if 0 <= x < nx and 0 <= y < ny and 0 <= z < nz:
            idx = _index(x, y, z, ny, nz)
            world[idx] = int(sid)
            seeded.append(idx)

    fam = str(family)
    if fam == "single_unit":
        set_state(cx, cy, cz, int(state_id))
    elif fam == "coherent_blob_3":
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    set_state(cx + dx, cy + dy, cz + dz, int(state_id))
    elif fam == "dipole_pair_x":
        set_state(cx - 1, cy, cz, int(state_id))
        set_state(cx + 1, cy, cz, int(k.multiply_ids(_basis_id(0, -1), int(state_id))))
    elif fam == "photon_sheet_x":
        x0 = max(1, nx // 4)
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                set_state(x0, cy + dy, cz + dz, int(state_id))
    else:
        raise ValueError(f"Unknown seed family: {fam}")

    if bool(apply_kick):
        for idx in seeded:
            world[idx] = int(k.multiply_ids(int(kick_id), int(world[idx])))

    return {
        "seed_family": fam,
        "seeded_cell_count": int(len(set(seeded))),
        "seed_state_id": int(state_id),
        "seed_state_label": k.elem_label(int(state_id)),
        "kick_id": int(kick_id),
        "kick_label": k.elem_label(int(kick_id)),
        "kick_applied": bool(apply_kick),
    }


def _step(world: List[int], neighbors: Sequence[Sequence[int]], vac_id: int) -> List[int]:
    nxt = [int(vac_id) for _ in world]
    for idx, nb in enumerate(neighbors):
        acc = int(vac_id)
        for q in nb:
            msg = int(vac_id) if int(q) < 0 else int(world[int(q)])
            acc = int(k.multiply_ids(int(acc), int(msg)))
        nxt[idx] = int(k.multiply_ids(int(acc), int(world[idx])))
    return nxt


def _shift_x_fixed(world: Sequence[int], nx: int, ny: int, nz: int, dx: int, vac_id: int) -> List[int]:
    out = [int(vac_id) for _ in range(len(world))]
    for x in range(nx):
        src_x = x - int(dx)
        for y in range(ny):
            for z in range(nz):
                dst = _index(x, y, z, ny, nz)
                if 0 <= src_x < nx:
                    src = _index(src_x, y, z, ny, nz)
                    out[dst] = int(world[src])
                else:
                    out[dst] = int(vac_id)
    return out


def _match_metrics(cur: Sequence[int], shifted_prev: Sequence[int], vac_id: int) -> Dict[str, Any]:
    n = len(cur)
    global_matches = 0
    support_matches = 0
    support_count = 0
    nonvac_cur = 0
    for a, b in zip(cur, shifted_prev):
        if int(a) == int(b):
            global_matches += 1
        in_support = (int(a) != int(vac_id)) or (int(b) != int(vac_id))
        if in_support:
            support_count += 1
            if int(a) == int(b):
                support_matches += 1
        if int(a) != int(vac_id):
            nonvac_cur += 1
    global_ratio = float(global_matches / max(1, n))
    support_ratio = float(support_matches / max(1, support_count)) if support_count > 0 else 0.0
    return {
        "global_match_ratio": float(global_ratio),
        "support_match_ratio": float(support_ratio),
        "support_count": int(support_count),
        "nonvac_cells_current": int(nonvac_cur),
    }


def _classify_candidate(
    history: Sequence[List[int]],
    *,
    t1: int,
    period: int,
    dx: int,
    nx: int,
    ny: int,
    nz: int,
    vac_id: int,
    repeat_checks: int,
    min_support_cells: int,
    min_support_match_ratio: float,
    min_global_match_ratio: float,
) -> Dict[str, Any] | None:
    if t1 - period < 0:
        return None

    ratios: List[Dict[str, Any]] = []
    comparisons = 0
    for r in range(int(repeat_checks)):
        ta = int(t1 + r * period)
        tb = int(ta - period)
        if ta >= len(history) or tb < 0:
            break
        shifted = _shift_x_fixed(history[tb], nx, ny, nz, int(dx), int(vac_id))
        mm = _match_metrics(history[ta], shifted, int(vac_id))
        ratios.append(mm)
        comparisons += 1

    if comparisons == 0:
        return None

    mean_support = float(sum(r["support_match_ratio"] for r in ratios) / comparisons)
    mean_global = float(sum(r["global_match_ratio"] for r in ratios) / comparisons)
    min_support = int(min(r["support_count"] for r in ratios))
    min_nonvac = int(min(r["nonvac_cells_current"] for r in ratios))

    if min_support < int(min_support_cells):
        return None
    if mean_support < float(min_support_match_ratio):
        return None
    if mean_global < float(min_global_match_ratio):
        return None

    strict = bool(
        all(
            abs(float(r["support_match_ratio"]) - 1.0) < 1e-12
            and abs(float(r["global_match_ratio"]) - 1.0) < 1e-12
            for r in ratios
        )
    )
    cls = "strict_lock" if strict else "candidate_lock"
    motion_cls = "stationary" if int(dx) == 0 else "propagating"
    score = float(mean_support + 0.35 * mean_global + 0.04 * comparisons + 0.01 * abs(int(dx)))

    return {
        "classification": cls,
        "motion_class": motion_cls,
        "score": float(score),
        "t1": int(t1),
        "period_N": int(period),
        "shift_dx": int(dx),
        "comparisons": int(comparisons),
        "mean_support_match_ratio": float(mean_support),
        "mean_global_match_ratio": float(mean_global),
        "min_support_count": int(min_support),
        "min_nonvac_cells_current": int(min_nonvac),
        "comparison_rows": ratios,
    }


def _trial_summary(history: Sequence[List[int]], vac_id: int, nx: int, ny: int, nz: int) -> Dict[str, Any]:
    n = nx * ny * nz
    nonvac_by_tick = [sum(1 for v in row if int(v) != int(vac_id)) for row in history]

    def centroid_x(row: Sequence[int]) -> float:
        total = 0
        wsum = 0
        for x in range(nx):
            for y in range(ny):
                for z in range(nz):
                    idx = _index(x, y, z, ny, nz)
                    w = 1 if int(row[idx]) != int(vac_id) else 0
                    total += w
                    wsum += w * x
        return float(wsum / total) if total > 0 else float(nx // 2)

    cx0 = centroid_x(history[0])
    cxf = centroid_x(history[-1])
    return {
        "ticks": int(len(history) - 1),
        "max_nonvac_cells": int(max(nonvac_by_tick) if nonvac_by_tick else 0),
        "final_nonvac_cells": int(nonvac_by_tick[-1] if nonvac_by_tick else 0),
        "initial_nonvac_cells": int(nonvac_by_tick[0] if nonvac_by_tick else 0),
        "centroid_x_initial": float(cx0),
        "centroid_x_final": float(cxf),
        "centroid_x_delta": float(cxf - cx0),
        "nonvac_density_final": float((nonvac_by_tick[-1] if nonvac_by_tick else 0) / max(1, n)),
    }


def _build_trials(max_trials: int) -> List[Dict[str, Any]]:
    # Photon-first plus localized motif prototypes.
    e111 = _basis_id(7, +1)
    e001 = _basis_id(1, +1)
    e010 = _basis_id(2, +1)
    e100 = _basis_id(4, +1)
    trial_bank = [
        {"trial_id": "photon_sheet_e111_kick_e001", "seed_family": "photon_sheet_x", "seed_state_id": e111, "kick_id": e001},
        {"trial_id": "photon_sheet_e111_kick_e010", "seed_family": "photon_sheet_x", "seed_state_id": e111, "kick_id": e010},
        {"trial_id": "single_e111_kick_e001", "seed_family": "single_unit", "seed_state_id": e111, "kick_id": e001},
        {"trial_id": "single_e001_kick_e111", "seed_family": "single_unit", "seed_state_id": e001, "kick_id": e111},
        {"trial_id": "blob3_e111_kick_e010", "seed_family": "coherent_blob_3", "seed_state_id": e111, "kick_id": e010},
        {"trial_id": "blob3_e100_kick_e111", "seed_family": "coherent_blob_3", "seed_state_id": e100, "kick_id": e111},
        {"trial_id": "dipole_e111_kick_e001", "seed_family": "dipole_pair_x", "seed_state_id": e111, "kick_id": e001},
        {"trial_id": "dipole_e010_kick_e111", "seed_family": "dipole_pair_x", "seed_state_id": e010, "kick_id": e111},
    ]
    return trial_bank[: max(1, int(max_trials))]


def build_payload(params: ScanParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else ScanParams()
    if int(p.ticks) < 16:
        raise ValueError("ticks must be >= 16")
    if int(p.warmup_ticks) >= int(p.ticks):
        raise ValueError("warmup_ticks must be < ticks")
    if int(p.min_period) < 1 or int(p.max_period) < int(p.min_period):
        raise ValueError("invalid period range")
    if int(p.size_x) < 9 or int(p.size_y) < 5 or int(p.size_z) < 5:
        raise ValueError("grid too small for 3D motif scan")

    nx, ny, nz = int(p.size_x), int(p.size_y), int(p.size_z)
    vac_id = int(k.IDENTITY_ID)
    offsets = _offsets(p.stencil_id)
    neighbors = _neighbor_table(nx, ny, nz, offsets)
    trials = _build_trials(int(p.max_trials))

    trial_rows: List[Dict[str, Any]] = []
    for tr in trials:
        world = [int(vac_id) for _ in range(nx * ny * nz)]
        seed_info = _apply_seed(
            world,
            nx,
            ny,
            nz,
            family=str(tr["seed_family"]),
            state_id=int(tr["seed_state_id"]),
            kick_id=int(tr["kick_id"]),
            apply_kick=True,
        )

        history: List[List[int]] = [list(world)]
        for _ in range(int(p.ticks)):
            world = _step(world, neighbors, int(vac_id))
            history.append(list(world))

        candidates: List[Dict[str, Any]] = []
        for period in range(int(p.min_period), int(p.max_period) + 1):
            t_start = int(max(int(p.warmup_ticks), period))
            for t1 in range(t_start, int(p.ticks) + 1):
                for dx in range(-int(p.max_shift_x), int(p.max_shift_x) + 1):
                    cand = _classify_candidate(
                        history,
                        t1=int(t1),
                        period=int(period),
                        dx=int(dx),
                        nx=nx,
                        ny=ny,
                        nz=nz,
                        vac_id=int(vac_id),
                        repeat_checks=int(p.repeat_checks),
                        min_support_cells=int(p.min_support_cells),
                        min_support_match_ratio=float(p.min_support_match_ratio),
                        min_global_match_ratio=float(p.min_global_match_ratio),
                    )
                    if cand is not None:
                        candidates.append(cand)

        candidates = sorted(candidates, key=lambda r: (float(r["score"]), float(r["mean_support_match_ratio"])), reverse=True)
        top = candidates[:3]
        summary = _trial_summary(history, int(vac_id), nx, ny, nz)

        thin = max(1, int(p.thin_output_step))
        trace_rows = []
        for t, row in enumerate(history):
            if (t % thin == 0) or (t == int(p.ticks)):
                nonvac = sum(1 for v in row if int(v) != int(vac_id))
                trace_rows.append({"tick": int(t), "nonvac_cells": int(nonvac)})

        trial_rows.append(
            {
                "trial_id": str(tr["trial_id"]),
                "seed": seed_info,
                "summary": summary,
                "candidate_count": int(len(candidates)),
                "top_candidates": top,
                "trace_thin": trace_rows,
            }
        )

    checks = {
        "trial_count": int(len(trial_rows)),
        "any_strict_lock": bool(any(any(c["classification"] == "strict_lock" for c in tr["top_candidates"]) for tr in trial_rows)),
        "any_candidate_lock": bool(any(len(tr["top_candidates"]) > 0 for tr in trial_rows)),
        "any_stationary_candidate": bool(
            any(any(c.get("motion_class") == "stationary" for c in tr["top_candidates"]) for tr in trial_rows)
        ),
        "any_propagating_candidate": bool(
            any(any(c.get("motion_class") == "propagating" for c in tr["top_candidates"]) for tr in trial_rows)
        ),
    }

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "v3_stable_motif_scan_v1",
        "claim_id": "COG-V3-MOTIF-SCAN-001",
        "mode": "simulation_first_structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "params": {
            "ticks": int(p.ticks),
            "size_x": int(p.size_x),
            "size_y": int(p.size_y),
            "size_z": int(p.size_z),
            "boundary_mode": "fixed_vacuum",
            "stencil_id": str(p.stencil_id),
            "stencil_size": int(len(offsets)),
            "warmup_ticks": int(p.warmup_ticks),
            "min_period": int(p.min_period),
            "max_period": int(p.max_period),
            "max_shift_x": int(p.max_shift_x),
            "repeat_checks": int(p.repeat_checks),
            "min_support_cells": int(p.min_support_cells),
            "min_support_match_ratio": float(p.min_support_match_ratio),
            "min_global_match_ratio": float(p.min_global_match_ratio),
            "max_trials": int(p.max_trials),
            "thin_output_step": int(max(1, int(p.thin_output_step))),
        },
        "trials": trial_rows,
        "checks": checks,
        "notes": [
            "Primary default is 3D fixed-vacuum with axial6 stencil (tractable baseline).",
            "Broader stencils (cube26/cube124) are available to probe missed-physics risk.",
            "Candidate locks are intentionally permissive to survive finite-box artifacts and residual transients.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    lines = [
        "# COG v3 Stable Motif Scan (v1)",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- size: `{p['size_x']} x {p['size_y']} x {p['size_z']}`",
        f"- boundary_mode: `{p['boundary_mode']}`",
        f"- stencil_id: `{p['stencil_id']}` (size `{p['stencil_size']}`)",
        f"- period range: `{p['min_period']}..{p['max_period']}`",
        f"- max_shift_x: `{p['max_shift_x']}`",
        f"- repeat_checks: `{p['repeat_checks']}`",
        "",
        "## Trial Summary",
        "",
        "| trial_id | seed_family | seeded_cells | candidate_count | best_class | best_period | best_dx | best_support_ratio |",
        "|---|---|---:|---:|---|---:|---:|---:|",
    ]
    for tr in payload["trials"]:
        best = tr["top_candidates"][0] if tr["top_candidates"] else None
        if best is None:
            lines.append(
                f"| `{tr['trial_id']}` | `{tr['seed']['seed_family']}` | {tr['seed']['seeded_cell_count']} | "
                f"{tr['candidate_count']} | - | - | - | - |"
            )
        else:
            lines.append(
                f"| `{tr['trial_id']}` | `{tr['seed']['seed_family']}` | {tr['seed']['seeded_cell_count']} | "
                f"{tr['candidate_count']} | `{best['classification']}/{best.get('motion_class', 'unknown')}` | {best['period_N']} | {best['shift_dx']} | "
                f"{best['mean_support_match_ratio']:.6f} |"
            )
    lines.extend(["", "## Checks", ""])
    for ck, cv in payload["checks"].items():
        lines.append(f"- {ck}: `{cv}`")
    lines.append("")
    return "\n".join(lines)


def write_artifacts(
    payload: Dict[str, Any],
    json_paths: Sequence[Path] = (OUT_JSON,),
    md_paths: Sequence[Path] = (OUT_MD,),
) -> None:
    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = _render_md(payload)
    for path in md_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticks", type=int, default=ScanParams.ticks)
    parser.add_argument("--size-x", type=int, default=ScanParams.size_x)
    parser.add_argument("--size-y", type=int, default=ScanParams.size_y)
    parser.add_argument("--size-z", type=int, default=ScanParams.size_z)
    parser.add_argument("--stencil-id", type=str, default=ScanParams.stencil_id, choices=["axial6", "cube26", "cube124"])
    parser.add_argument("--warmup", type=int, default=ScanParams.warmup_ticks)
    parser.add_argument("--min-period", type=int, default=ScanParams.min_period)
    parser.add_argument("--max-period", type=int, default=ScanParams.max_period)
    parser.add_argument("--max-shift-x", type=int, default=ScanParams.max_shift_x)
    parser.add_argument("--repeat-checks", type=int, default=ScanParams.repeat_checks)
    parser.add_argument("--min-support-cells", type=int, default=ScanParams.min_support_cells)
    parser.add_argument("--min-support-match-ratio", type=float, default=ScanParams.min_support_match_ratio)
    parser.add_argument("--min-global-match-ratio", type=float, default=ScanParams.min_global_match_ratio)
    parser.add_argument("--max-trials", type=int, default=ScanParams.max_trials)
    parser.add_argument("--thin-output-step", type=int, default=ScanParams.thin_output_step)
    args = parser.parse_args()

    params = ScanParams(
        ticks=int(args.ticks),
        size_x=int(args.size_x),
        size_y=int(args.size_y),
        size_z=int(args.size_z),
        stencil_id=str(args.stencil_id),
        warmup_ticks=int(args.warmup),
        min_period=int(args.min_period),
        max_period=int(args.max_period),
        max_shift_x=int(args.max_shift_x),
        repeat_checks=int(args.repeat_checks),
        min_support_cells=int(args.min_support_cells),
        min_support_match_ratio=float(args.min_support_match_ratio),
        min_global_match_ratio=float(args.min_global_match_ratio),
        max_trials=int(args.max_trials),
        thin_output_step=int(args.thin_output_step),
    )
    payload = build_payload(params)
    write_artifacts(payload)
    print(
        "v3_stable_motif_scan_v1: "
        f"trials={payload['checks']['trial_count']}, "
        f"any_candidate_lock={payload['checks']['any_candidate_lock']}, "
        f"any_strict_lock={payload['checks']['any_strict_lock']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

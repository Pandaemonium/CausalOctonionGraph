"""RFC-012 associator-field probe for COG v3.

Artifacts:
1) cog_v3/sources/v3_associator_field_probe_v1.json
2) cog_v3/sources/v3_associator_radial_profiles_v1.csv
3) cog_v3/sources/v3_associator_family_activity_v1.csv
4) cog_v3/sources/v3_associator_field_probe_v1.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_associator_field_probe_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_associator_field_probe_v1.md"
OUT_RADIAL_CSV = ROOT / "cog_v3" / "sources" / "v3_associator_radial_profiles_v1.csv"
OUT_FAMILY_CSV = ROOT / "cog_v3" / "sources" / "v3_associator_family_activity_v1.csv"
ORDER_CSV = ROOT / "cog_v3" / "sources" / "v3_octavian240_elements_v1.csv"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_associator_field_probe_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _idx(x: int, y: int, z: int, ny: int, nz: int) -> int:
    return (x * ny + y) * nz + z


def _offsets(stencil_id: str) -> List[Tuple[int, int, int]]:
    if str(stencil_id) == "axial6":
        return [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
    if str(stencil_id) == "cube26":
        out: List[Tuple[int, int, int]] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    out.append((dx, dy, dz))
        return out
    raise ValueError(f"Unknown stencil_id: {stencil_id}")


def _build_neighbors(
    nx: int,
    ny: int,
    nz: int,
    offsets: Sequence[Tuple[int, int, int]],
    boundary_mode: str,
) -> np.ndarray:
    n = int(nx) * int(ny) * int(nz)
    m = len(offsets)
    tab = np.full((n, m), -1, dtype=np.int32)
    wrap = str(boundary_mode) == "periodic"
    row = 0
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                for j, (dx, dy, dz) in enumerate(offsets):
                    qx = x + int(dx)
                    qy = y + int(dy)
                    qz = z + int(dz)
                    if wrap:
                        qx %= nx
                        qy %= ny
                        qz %= nz
                        tab[row, j] = _idx(qx, qy, qz, ny, nz)
                    else:
                        if 0 <= qx < nx and 0 <= qy < ny and 0 <= qz < nz:
                            tab[row, j] = _idx(qx, qy, qz, ny, nz)
                row += 1
    return tab


def _build_mul_table() -> np.ndarray:
    n = int(k.ALPHABET_SIZE)
    out = np.empty((n, n), dtype=np.uint16)
    for a in range(n):
        for b in range(n):
            out[a, b] = np.uint16(int(k.multiply_ids(int(a), int(b))))
    return out


def _step_sync(world: np.ndarray, neighbors: np.ndarray, mul: np.ndarray, vac_id: int) -> np.ndarray:
    n, m = neighbors.shape
    out = np.empty_like(world)
    vac = int(vac_id)
    for i in range(n):
        acc = vac
        for j in range(m):
            q = int(neighbors[i, j])
            msg = vac if q < 0 else int(world[q])
            acc = int(mul[acc, msg])
        out[i] = np.uint16(int(mul[acc, int(world[i])]))
    return out


def _apply_blob3(world: np.ndarray, nx: int, ny: int, nz: int, sid: int) -> None:
    cx, cy, cz = nx // 2, ny // 2, nz // 2
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                x, y, z = cx + dx, cy + dy, cz + dz
                if 0 <= x < nx and 0 <= y < ny and 0 <= z < nz:
                    world[_idx(x, y, z, ny, nz)] = np.uint16(int(sid))


def _centroid(world: np.ndarray, nx: int, ny: int, nz: int, vac_id: int) -> Tuple[float, float, float]:
    ids = np.flatnonzero(world != np.uint16(vac_id))
    if ids.size == 0:
        return (float(nx // 2), float(ny // 2), float(nz // 2))
    xs = ids // (ny * nz)
    rem = ids % (ny * nz)
    ys = rem // nz
    zs = rem % nz
    return (float(np.mean(xs)), float(np.mean(ys)), float(np.mean(zs)))


def _assoc_indicator(a: int, b: int, c: int, mul: np.ndarray) -> int:
    left = int(mul[int(mul[int(a), int(b)]), int(c)])
    right = int(mul[int(a), int(mul[int(b), int(c)])])
    return int(left != right)


def _a_local_field(world: np.ndarray, neighbors: np.ndarray, mul: np.ndarray, vac_id: int) -> np.ndarray:
    n, m = neighbors.shape
    out = np.zeros((n,), dtype=np.float64)
    vac = int(vac_id)
    for i in range(n):
        vals: List[int] = []
        for j in range(m):
            q = int(neighbors[i, j])
            vals.append(vac if q < 0 else int(world[q]))
        if len(vals) < 3:
            out[i] = 0.0
            continue
        picks = [(0, 1, 2)]
        if len(vals) >= 5:
            picks.append((0, 2, 4))
        if len(vals) >= 6:
            picks.append((1, 3, 5))
        s = 0.0
        for ia, ib, ic in picks:
            s += float(_assoc_indicator(vals[ia], vals[ib], vals[ic], mul))
        out[i] = s / float(len(picks))
    return out


def _radial_profiles(
    a_local: np.ndarray,
    nx: int,
    ny: int,
    nz: int,
    center: Tuple[float, float, float],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    cx, cy, cz = center
    shells: Dict[int, List[float]] = {}
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                r = int(math.floor(math.sqrt((x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2)))
                shells.setdefault(r, []).append(float(a_local[_idx(x, y, z, ny, nz)]))
    shell_rows: List[Dict[str, Any]] = []
    var_rows: List[Dict[str, Any]] = []
    for r in sorted(shells.keys()):
        vals = np.asarray(shells[r], dtype=np.float64)
        shell_rows.append({"r": int(r), "mean": float(np.mean(vals)), "n": int(vals.size)})
        var_rows.append({"r": int(r), "var": float(np.var(vals)), "n": int(vals.size)})
    return shell_rows, var_rows


def _fit_scores(shell_rows: Sequence[Dict[str, Any]], a_bg: float) -> Dict[str, float]:
    rr: List[float] = []
    yy: List[float] = []
    for row in shell_rows:
        r = int(row["r"])
        if r <= 0:
            continue
        rr.append(float(r))
        yy.append(max(1e-12, float(row["mean"]) - float(a_bg)))
    if len(rr) < 3:
        return {"rmse_flat": float("inf"), "rmse_power": float("inf"), "rmse_exponential": float("inf")}
    r = np.asarray(rr, dtype=np.float64)
    y = np.asarray(yy, dtype=np.float64)
    rmse_flat = float(np.sqrt(np.mean((y - 0.0) ** 2)))
    # log(y)=alpha-beta*log(r)
    Xp = np.stack([np.ones_like(r), -np.log(r)], axis=1)
    bp, *_ = np.linalg.lstsq(Xp, np.log(y), rcond=None)
    yhat_p = np.exp(Xp @ bp)
    rmse_power = float(np.sqrt(np.mean((y - yhat_p) ** 2)))
    # log(y)=alpha-beta*r
    Xe = np.stack([np.ones_like(r), -r], axis=1)
    be, *_ = np.linalg.lstsq(Xe, np.log(y), rcond=None)
    yhat_e = np.exp(Xe @ be)
    rmse_exponential = float(np.sqrt(np.mean((y - yhat_e) ** 2)))
    return {"rmse_flat": rmse_flat, "rmse_power": rmse_power, "rmse_exponential": rmse_exponential}


def _load_family_tags() -> Dict[int, str]:
    out: Dict[int, str] = {}
    with ORDER_CSV.open("r", newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            out[int(row["id"])] = str(row["family_tag"])
    return out


def _family_associator_activity(mul: np.ndarray, family_tags: Dict[int, str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    qn = int(mul.shape[0])
    bc = mul.astype(np.int32)
    rows: List[Dict[str, Any]] = []
    by_family: Dict[str, List[float]] = {}
    for a in range(qn):
        ab = bc[a, :]
        left = bc[ab, :]
        right = bc[a, bc]
        mismatch = float(np.mean(left != right))
        fam = str(family_tags.get(int(a), "UNKNOWN"))
        rows.append({"q_id": int(a), "family_tag": fam, "assoc_activity": mismatch})
        by_family.setdefault(fam, []).append(mismatch)
    summary: Dict[str, Any] = {}
    for fam, vals in sorted(by_family.items()):
        arr = np.asarray(vals, dtype=np.float64)
        summary[fam] = {
            "count": int(arr.size),
            "mean": float(np.mean(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
        }
    return rows, summary


def _seed_ids_from_families(family_tags: Dict[int, str]) -> List[Tuple[str, int]]:
    seed_rows: List[Tuple[str, int]] = []
    seen = set()
    for qid in sorted(family_tags.keys()):
        fam = family_tags[qid]
        if fam not in seen and qid != int(k.IDENTITY_ID):
            seen.add(fam)
            seed_rows.append((fam, int(qid)))
    return seed_rows


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Associator Field Probe (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- stencil_id: `{payload['stencil_id']}`",
        f"- A_bg: `{payload['A_bg']:.6f}`",
        "",
        "## Gate Results",
        "",
        f"- gate1_delta_peak: `{payload['gate_results']['gate1_delta_peak']}`",
        f"- gate2_radial_fit: `{payload['gate_results']['gate2_radial_fit']}`",
        f"- gate3_family_hierarchy: `{payload['gate_results']['gate3_family_hierarchy']}`",
        "",
        "## Seed Snapshots",
        "",
    ]
    for row in payload["seed_profiles"]:
        lines.append(
            f"- `{row['seed_id']}`: DeltaA_peak={float(row['DeltaA_peak']):.6f}, "
            f"rmse_flat={float(row['fit_scores']['rmse_flat']):.6f}, "
            f"rmse_power={float(row['fit_scores']['rmse_power']):.6f}, "
            f"rmse_exponential={float(row['fit_scores']['rmse_exponential']):.6f}"
        )
    return "\n".join(lines)


def build_payload(
    *,
    ticks: int = 72,
    warmup_ticks: int = 18,
    size_x: int = 21,
    size_y: int = 9,
    size_z: int = 9,
    stencil_id: str = "cube26",
    boundary_mode: str = "fixed_vacuum",
) -> Dict[str, Any]:
    nx, ny, nz = int(size_x), int(size_y), int(size_z)
    vac = int(k.IDENTITY_ID)
    mul = _build_mul_table()
    neighbors = _build_neighbors(nx, ny, nz, _offsets(str(stencil_id)), str(boundary_mode))
    family_tags = _load_family_tags()

    # Vacuum baseline
    world_bg = np.full((nx * ny * nz,), np.uint16(vac), dtype=np.uint16)
    bg_vals: List[float] = []
    for t in range(1, int(ticks) + 1):
        world_bg = _step_sync(world_bg, neighbors, mul, vac_id=vac)
        if t >= int(warmup_ticks):
            a_local = _a_local_field(world_bg, neighbors, mul, vac_id=vac)
            bg_vals.append(float(np.mean(a_local)))
    a_bg = float(np.mean(bg_vals)) if bg_vals else 0.0
    a_bg_std = float(np.std(np.asarray(bg_vals, dtype=np.float64))) if bg_vals else 0.0

    family_rows, family_summary = _family_associator_activity(mul, family_tags)
    seeds = _seed_ids_from_families(family_tags)

    seed_profiles: List[Dict[str, Any]] = []
    radial_rows: List[Dict[str, Any]] = []
    all_delta: List[float] = []
    fit_win_count = 0

    for fam, sid in seeds:
        world = np.full((nx * ny * nz,), np.uint16(vac), dtype=np.uint16)
        _apply_blob3(world, nx, ny, nz, sid=int(sid))
        for _ in range(int(ticks)):
            world = _step_sync(world, neighbors, mul, vac_id=vac)
        a_local = _a_local_field(world, neighbors, mul, vac_id=vac)
        center = _centroid(world, nx, ny, nz, vac_id=vac)
        shell_rows, var_rows = _radial_profiles(a_local, nx, ny, nz, center)
        fits = _fit_scores(shell_rows, a_bg=a_bg)
        delta_peak = float(max((float(r["mean"]) - a_bg) for r in shell_rows)) if shell_rows else 0.0
        all_delta.append(delta_peak)
        if min(float(fits["rmse_power"]), float(fits["rmse_exponential"])) < float(fits["rmse_flat"]):
            fit_win_count += 1

        seed_id = f"seed_{fam}_{sid}"
        seed_profiles.append(
            {
                "seed_id": seed_id,
                "family_tag": fam,
                "state_id": int(sid),
                "A_shell_profile": shell_rows,
                "A_var_profile": var_rows,
                "DeltaA_peak": float(delta_peak),
                "fit_scores": fits,
            }
        )
        for rrow, vrow in zip(shell_rows, var_rows):
            radial_rows.append(
                {
                    "seed_id": seed_id,
                    "family_tag": fam,
                    "state_id": int(sid),
                    "r": int(rrow["r"]),
                    "A_shell": float(rrow["mean"]),
                    "A_var": float(vrow["var"]),
                    "n": int(rrow["n"]),
                }
            )

    # Family hierarchy gate (A < B < C) on means
    a_mean = float(family_summary.get("A16_basis_signed_unit", {}).get("mean", 0.0))
    b_mean = float(family_summary.get("B112_line_plus_e000_halfsum", {}).get("mean", 0.0))
    c_mean = float(family_summary.get("C112_complement_halfsum", {}).get("mean", 0.0))
    g3 = bool(a_mean < b_mean < c_mean)

    payload: Dict[str, Any] = {
        "schema_version": "v3_associator_field_probe_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "stencil_id": str(stencil_id),
        "boundary_mode": str(boundary_mode),
        "params": {
            "ticks": int(ticks),
            "warmup_ticks": int(warmup_ticks),
            "size_x": int(size_x),
            "size_y": int(size_y),
            "size_z": int(size_z),
        },
        "A_bg": float(a_bg),
        "A_bg_std": float(a_bg_std),
        "seed_profiles": seed_profiles,
        "A_shell_profile": seed_profiles[0]["A_shell_profile"] if seed_profiles else [],
        "A_var_profile": seed_profiles[0]["A_var_profile"] if seed_profiles else [],
        "fit_scores": seed_profiles[0]["fit_scores"] if seed_profiles else {},
        "seed_id": seed_profiles[0]["seed_id"] if seed_profiles else "",
        "family_activity_summary": family_summary,
        "gate_results": {
            "gate1_delta_peak": bool(max(all_delta) > max(0.002, 2.0 * a_bg_std)) if all_delta else False,
            "gate2_radial_fit": bool(fit_win_count >= max(1, len(seed_profiles) // 2)),
            "gate3_family_hierarchy": bool(g3),
        },
    }
    payload["replay_hash"] = _sha_payload(payload)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write(_render_md(payload))
        f.write("\n")

    with OUT_RADIAL_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["seed_id", "family_tag", "state_id", "r", "A_shell", "A_var", "n"],
        )
        w.writeheader()
        for row in radial_rows:
            w.writerow(row)

    with OUT_FAMILY_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["q_id", "family_tag", "assoc_activity"])
        w.writeheader()
        for row in family_rows:
            w.writerow(row)

    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Run v3 associator-field probe (RFC-012).")
    ap.add_argument("--ticks", type=int, default=72)
    ap.add_argument("--warmup-ticks", type=int, default=18)
    ap.add_argument("--size-x", type=int, default=21)
    ap.add_argument("--size-y", type=int, default=9)
    ap.add_argument("--size-z", type=int, default=9)
    ap.add_argument("--stencil-id", type=str, default="cube26", choices=["axial6", "cube26"])
    ap.add_argument("--boundary-mode", type=str, default="fixed_vacuum", choices=["fixed_vacuum", "periodic"])
    args = ap.parse_args()

    build_payload(
        ticks=int(args.ticks),
        warmup_ticks=int(args.warmup_ticks),
        size_x=int(args.size_x),
        size_y=int(args.size_y),
        size_z=int(args.size_z),
        stencil_id=str(args.stencil_id),
        boundary_mode=str(args.boundary_mode),
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_RADIAL_CSV}")
    print(f"Wrote {OUT_FAMILY_CSV}")


if __name__ == "__main__":
    main()


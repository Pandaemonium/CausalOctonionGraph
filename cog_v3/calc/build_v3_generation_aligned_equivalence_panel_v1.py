"""Build RFC-011 generation-aligned equivalence artifacts (S2880 lane)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_accel_v1 as accel
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_generation_aligned_equivalence_panel_v1.json"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_generation_aligned_equivalence_panel_v1.csv"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_generation_aligned_equivalence_panel_v1.md"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_generation_aligned_equivalence_panel_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"
PHASE_COUNT = 12


@dataclass(frozen=True)
class SystemSpec:
    system_id: str
    lepton_kind: str
    baryon_kind: str
    generation_offset: int


@dataclass(frozen=True)
class RunConfig:
    ticks: int
    warmup_ticks: int
    perturb_tick: int
    size_x: int
    size_y: int
    size_z: int
    boundary_mode: str
    stencil_id: str
    channel_policy_id: str
    seed_id: int
    orientation: str


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
    raise ValueError(f"Unknown stencil_id: {sid}")


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


def _policy_combo(policy_id: str, tick: int, seed: int) -> str:
    pid = str(policy_id)
    t = int(tick)
    if pid == "uniform_all":
        return "all"
    if pid == "deterministic_cycle_v1":
        m = t % 12
        face_on = m in {0, 1, 2, 3, 4, 6, 8, 10}
        corner_on = m in {0, 1, 3, 5, 7, 9, 10}
        if face_on and corner_on:
            return "all"
        if face_on and (not corner_on):
            return "axis_face"
        if (not face_on) and corner_on:
            return "axis_corner"
        return "axis"
    return "all"


def _offset_class(dx: int, dy: int, dz: int) -> str:
    nnz = int((dx != 0) + (dy != 0) + (dz != 0))
    if nnz <= 1:
        return "axis"
    if nnz == 2:
        return "face"
    return "corner"


def _prepare_policy_neighbors(
    nx: int,
    ny: int,
    nz: int,
    stencil_id: str,
    boundary_mode: str,
) -> Dict[str, np.ndarray]:
    offsets = _offsets(stencil_id)
    axis = [o for o in offsets if _offset_class(int(o[0]), int(o[1]), int(o[2])) == "axis"]
    face = [o for o in offsets if _offset_class(int(o[0]), int(o[1]), int(o[2])) == "face"]
    corner = [o for o in offsets if _offset_class(int(o[0]), int(o[1]), int(o[2])) == "corner"]

    def tbl(v: List[Tuple[int, int, int]]) -> np.ndarray:
        vv = v if len(v) > 0 else axis
        return _build_neighbors(nx, ny, nz, vv, boundary_mode=boundary_mode)

    axis_face = axis + face if len(face) > 0 else axis
    axis_corner = axis + corner if len(corner) > 0 else axis
    all_offsets = axis + face + corner if len(face) + len(corner) > 0 else axis
    return {
        "axis": tbl(axis),
        "axis_face": tbl(axis_face),
        "axis_corner": tbl(axis_corner),
        "all": tbl(all_offsets),
    }


def _rotate_xyz(pos: Tuple[int, int, int], orientation: str) -> Tuple[int, int, int]:
    x, y, z = int(pos[0]), int(pos[1]), int(pos[2])
    o = str(orientation)
    if o == "x":
        return (x, y, z)
    if o == "y":
        return (y, z, x)
    if o == "z":
        return (z, x, y)
    raise ValueError(f"Unknown orientation: {o}")


def _seed_system(
    world: np.ndarray,
    nx: int,
    ny: int,
    nz: int,
    *,
    spec: SystemSpec,
    orientation: str,
    qn: int,
) -> Dict[str, Any]:
    q_u = _q_basis_id(1, +1)   # e001
    q_d = _q_basis_id(2, +1)   # e010
    q_c = _q_basis_id(4, +1)   # e100
    q_s = _q_basis_id(3, +1)   # e011
    q_e = _q_basis_id(7, +1)   # e111
    q_mu = _q_basis_id(6, +1)  # e110
    q_tau = _q_basis_id(5, +1) # e101

    lepton_q = {"electron": q_e, "muon": q_mu, "tau": q_tau}[str(spec.lepton_kind)]
    baryon_qs = {
        "uud": [q_u, q_u, q_d],
        "ccs": [q_c, q_c, q_s],
    }[str(spec.baryon_kind)]

    phase = int(spec.generation_offset) % PHASE_COUNT
    cx, cy, cz = nx // 2, ny // 2, nz // 2
    placed = []

    def put_local(pos: Tuple[int, int, int], sid: int) -> None:
        px, py, pz = _rotate_xyz(pos, orientation)
        x = cx + int(px)
        y = cy + int(py)
        z = cz + int(pz)
        if 0 <= x < nx and 0 <= y < ny and 0 <= z < nz:
            idx = _idx(x, y, z, ny, nz)
            world[idx] = np.uint16(int(sid))
            placed.append(int(idx))

    put_local((-1, 0, 0), _s_id(phase, baryon_qs[0], qn))
    put_local((0, 0, 0), _s_id(phase, baryon_qs[1], qn))
    put_local((1, 0, 0), _s_id(phase, baryon_qs[2], qn))
    put_local((0, 2, 0), _s_id(phase, lepton_q, qn))

    return {
        "seeded_count": int(len(placed)),
        "generation_offset": int(phase),
        "lepton_kind": str(spec.lepton_kind),
        "baryon_kind": str(spec.baryon_kind),
    }


def _inject_non_synced_perturbation(
    world: np.ndarray,
    nx: int,
    ny: int,
    nz: int,
    *,
    qn: int,
    generation_offset: int,
) -> None:
    q_noise = _q_basis_id(1, +1)
    p = (int(generation_offset) + 5) % PHASE_COUNT
    sid = _s_id(p, q_noise, qn)
    y0 = ny // 2
    z0 = nz // 2
    for dz in (-1, 0, 1):
        idx = _idx(1, y0, z0 + dz, ny, nz)
        world[idx] = np.uint16(int(sid))


def _centroid(world: np.ndarray, nx: int, ny: int, nz: int, vac_id: int) -> Tuple[float, float, float]:
    ids = np.flatnonzero(world != np.uint16(vac_id))
    if ids.size == 0:
        return (float(nx // 2), float(ny // 2), float(nz // 2))
    xs = ids // (ny * nz)
    rem = ids % (ny * nz)
    ys = rem // nz
    zs = rem % nz
    return (float(np.mean(xs)), float(np.mean(ys)), float(np.mean(zs)))


def _support_radius(world: np.ndarray, nx: int, ny: int, nz: int, vac_id: int) -> float:
    c = _centroid(world, nx, ny, nz, vac_id)
    ids = np.flatnonzero(world != np.uint16(vac_id))
    if ids.size == 0:
        return 0.0
    xs = ids // (ny * nz)
    rem = ids % (ny * nz)
    ys = rem // nz
    zs = rem % nz
    dx = xs.astype(np.float64) - c[0]
    dy = ys.astype(np.float64) - c[1]
    dz = zs.astype(np.float64) - c[2]
    r = np.sqrt(dx * dx + dy * dy + dz * dz)
    return float(np.mean(r))


def _run_system(spec: SystemSpec, cfg: RunConfig, *, global_seed: int) -> Dict[str, Any]:
    qmul = c12.build_qmul_table()
    mul = c12.build_mul_table(phase_count=PHASE_COUNT, qmul=qmul)
    qn = int(qmul.shape[0])
    vac_id = int(c12.s_identity_id())

    nx, ny, nz = int(cfg.size_x), int(cfg.size_y), int(cfg.size_z)
    n_cells = nx * ny * nz
    world = np.full((n_cells,), np.uint16(vac_id), dtype=np.uint16)
    seed_meta = _seed_system(
        world,
        nx,
        ny,
        nz,
        spec=spec,
        orientation=str(cfg.orientation),
        qn=qn,
    )
    policy_neighbors = _prepare_policy_neighbors(nx, ny, nz, str(cfg.stencil_id), str(cfg.boundary_mode))
    neighbors_default = policy_neighbors["all"]

    h_seen: Dict[int, int] = {}
    first_repeat: Dict[str, int] | None = None
    support_radii: List[float] = []
    centroids: List[Tuple[float, float, float]] = []
    phase_counts = np.zeros((PHASE_COUNT,), dtype=np.int64)
    recurrence_rows: List[float] = []
    pre_mix_hashes: List[int] = []

    c0 = _centroid(world, nx, ny, nz, vac_id)
    centroids.append(c0)
    r0 = max(1e-9, _support_radius(world, nx, ny, nz, vac_id))

    for t in range(1, int(cfg.ticks) + 1):
        if t == int(cfg.perturb_tick):
            _inject_non_synced_perturbation(
                world,
                nx,
                ny,
                nz,
                qn=qn,
                generation_offset=int(spec.generation_offset),
            )

        combo = _policy_combo(str(cfg.channel_policy_id), int(t), int(global_seed) + int(cfg.seed_id))
        neighbors = policy_neighbors.get(combo, neighbors_default)
        old = world
        world = accel.step_numba_cpu(old, neighbors, mul, vac_id=vac_id, identity_id=vac_id)

        d = ((world.astype(np.int32) // qn - old.astype(np.int32) // qn) % PHASE_COUNT).astype(np.int16)
        support = (old != np.uint16(vac_id)) | (world != np.uint16(vac_id))
        if bool(np.any(support)) and t >= int(cfg.warmup_ticks):
            bc = np.bincount(d[support].astype(np.int32), minlength=PHASE_COUNT)
            phase_counts += bc.astype(np.int64)

        if t >= int(cfg.warmup_ticks) and t < int(cfg.perturb_tick):
            h = hash(world.tobytes())
            pre_mix_hashes.append(int(h))
            prev = h_seen.get(int(h))
            if first_repeat is None:
                if prev is not None:
                    first_repeat = {"t_prev": int(prev), "t_now": int(t), "period": int(t - prev)}
                else:
                    h_seen[int(h)] = int(t)

            c = _centroid(world, nx, ny, nz, vac_id)
            centroids.append(c)
            support_radii.append(_support_radius(world, nx, ny, nz, vac_id))

            if first_repeat is not None:
                p = int(first_repeat["period"])
                if (t - p) >= int(cfg.warmup_ticks):
                    # recurrence fidelity in support region
                    # use hash-level proxy as robust discrete score.
                    rec = 1.0 if pre_mix_hashes[-1] == pre_mix_hashes[-1 - p] else 0.0
                    recurrence_rows.append(float(rec))

    c_last = centroids[-1] if centroids else c0
    drift = math.sqrt((c_last[0] - c0[0]) ** 2 + (c_last[1] - c0[1]) ** 2 + (c_last[2] - c0[2]) ** 2)
    ticks_pre = max(1, int(cfg.perturb_tick) - int(cfg.warmup_ticks))
    v_hat = float(drift / float(ticks_pre))

    r_mean = float(sum(support_radii) / max(1, len(support_radii))) if support_radii else float(r0)
    r_hat = float(r_mean / max(1e-9, r0))

    signed = np.arange(PHASE_COUNT, dtype=np.int16)
    signed[signed > 6] -= 12
    omega_num = float(np.sum(phase_counts.astype(np.float64) * signed.astype(np.float64)))
    omega_den = float(max(1, np.sum(phase_counts)))
    omega_hat = float((omega_num / omega_den) / 3.141592653589793)

    if first_repeat is not None:
        t_cycle = int(first_repeat["period"])
    else:
        t_cycle = 0

    s_stab = float(sum(recurrence_rows) / max(1, len(recurrence_rows))) if recurrence_rows else 0.0

    top = sorted([(i, int(phase_counts[i])) for i in range(PHASE_COUNT)], key=lambda x: x[1], reverse=True)[:3]
    h_summary = ",".join(f"{int(i)}:{int(v)}" for i, v in top)

    return {
        "system_id": str(spec.system_id),
        "generation_offset_signature": f"g{int(spec.generation_offset)}",
        "seed_meta": seed_meta,
        "window_id": "window_pre_mix",
        "T_cycle": int(t_cycle),
        "R_hat": float(r_hat),
        "Omega_hat": float(omega_hat),
        "S_stab": float(s_stab),
        "V_hat": float(v_hat),
        "H_phase_summary": str(h_summary),
        "phase_counts": [int(x) for x in phase_counts.tolist()],
    }


def _delta(a: float, b: float) -> float:
    den = max(abs(float(a)), abs(float(b)), 1e-9)
    return float(abs(float(a) - float(b)) / den)


def _pair_delta(row_a: Dict[str, Any], row_b: Dict[str, Any]) -> Dict[str, Any]:
    dm = {
        "T_cycle": _delta(float(row_a["T_cycle"]), float(row_b["T_cycle"])),
        "R_hat": _delta(float(row_a["R_hat"]), float(row_b["R_hat"])),
        "Omega_hat": _delta(float(row_a["Omega_hat"]), float(row_b["Omega_hat"])),
        "S_stab": _delta(float(row_a["S_stab"]), float(row_b["S_stab"])),
        "V_hat": _delta(float(row_a["V_hat"]), float(row_b["V_hat"])),
    }
    dmax = max(dm.values()) if dm else 0.0
    return {"delta_metrics": dm, "Delta_max_pair": float(dmax), "pass_flag_lt_1pct": bool(dmax < 0.01)}


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Generation-Aligned Equivalence Panel (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- pair_count: `{len(payload['pair_rows'])}`",
        "",
        "## Pair Summary",
        "",
        "| pair_id | window | median_Delta_max | pass_rate_lt_1pct |",
        "|---|---|---:|---:|",
    ]
    for row in payload["pair_summary"]:
        lines.append(
            f"| `{row['pair_id']}` | `{row['window_id']}` | {float(row['median_Delta_max']):.6f} | {float(row['pass_rate_lt_1pct']):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Contract threshold follows RFC-011 (`Delta_max < 1%`).",
            "- This artifact is a test lane, not closure evidence.",
        ]
    )
    return "\n".join(lines)


def build_payload(*, global_seed: int = 1337, quick: bool = False) -> Dict[str, Any]:
    systems = [
        SystemSpec("S_A_e_uud_g0", "electron", "uud", 0),
        SystemSpec("S_B_mu_ccs_g1", "muon", "ccs", 1),
        SystemSpec("S_C_mu_uud_g1", "muon", "uud", 1),
        SystemSpec("S_D_tau_ccs_g2", "tau", "ccs", 2),
    ]

    pair_defs = [
        {"pair_id": "P_baseline_e_uud_vs_mu_ccs", "lhs": "S_A_e_uud_g0", "rhs": "S_B_mu_ccs_g1"},
        {"pair_id": "P_desync_mu_uud_vs_tau_ccs", "lhs": "S_C_mu_uud_g1", "rhs": "S_D_tau_ccs_g2"},
    ]

    if bool(quick):
        seeds = [0, 1]
        sizes = [(15, 7, 7)]
        boundaries = ["fixed_vacuum"]
        orientations = ["x"]
        ticks = 42
        warmup = 8
        perturb = 30
    else:
        seeds = [0, 1, 2, 3, 4]
        sizes = [(27, 9, 9), (39, 11, 11)]
        boundaries = ["fixed_vacuum", "periodic"]
        orientations = ["x", "y", "z"]
        ticks = 84
        warmup = 16
        perturb = 60

    system_rows: List[Dict[str, Any]] = []
    by_key: Dict[Tuple[str, int, Tuple[int, int, int], str, str], Dict[str, Any]] = {}

    for spec in systems:
        for seed in seeds:
            for size in sizes:
                for boundary in boundaries:
                    for ori in orientations:
                        cfg = RunConfig(
                            ticks=int(ticks),
                            warmup_ticks=int(warmup),
                            perturb_tick=int(perturb),
                            size_x=int(size[0]),
                            size_y=int(size[1]),
                            size_z=int(size[2]),
                            boundary_mode=str(boundary),
                            stencil_id="cube26",
                            channel_policy_id="uniform_all",
                            seed_id=int(seed),
                            orientation=str(ori),
                        )
                        row = _run_system(spec, cfg, global_seed=int(global_seed))
                        row["kernel_profile"] = k.KERNEL_PROFILE
                        row["convention_id"] = k.CONVENTION_ID
                        row["stencil_id"] = "cube26"
                        row["seed_id"] = int(seed)
                        row["size"] = [int(size[0]), int(size[1]), int(size[2])]
                        row["boundary_mode"] = str(boundary)
                        row["orientation"] = str(ori)
                        row["run_config"] = asdict(cfg)
                        system_rows.append(row)
                        by_key[(str(spec.system_id), int(seed), size, str(boundary), str(ori))] = row

    pair_rows: List[Dict[str, Any]] = []
    for pd in pair_defs:
        for seed in seeds:
            for size in sizes:
                for boundary in boundaries:
                    for ori in orientations:
                        a = by_key[(str(pd["lhs"]), int(seed), size, str(boundary), str(ori))]
                        b = by_key[(str(pd["rhs"]), int(seed), size, str(boundary), str(ori))]
                        dd = _pair_delta(a, b)
                        pair_rows.append(
                            {
                                "pair_id": str(pd["pair_id"]),
                                "window_id": "window_pre_mix",
                                "lhs_system_id": str(pd["lhs"]),
                                "rhs_system_id": str(pd["rhs"]),
                                "seed_id": int(seed),
                                "size_x": int(size[0]),
                                "size_y": int(size[1]),
                                "size_z": int(size[2]),
                                "boundary_mode": str(boundary),
                                "orientation": str(ori),
                                "Delta_max_pair": float(dd["Delta_max_pair"]),
                                "pass_flag_lt_1pct": bool(dd["pass_flag_lt_1pct"]),
                                "delta_metrics": dd["delta_metrics"],
                            }
                        )

    pair_summary: List[Dict[str, Any]] = []
    pair_ids = sorted(set(str(r["pair_id"]) for r in pair_rows))
    for pid in pair_ids:
        rows = [r for r in pair_rows if str(r["pair_id"]) == pid]
        vals = sorted(float(r["Delta_max_pair"]) for r in rows)
        med = vals[len(vals) // 2] if vals else 0.0
        pass_rate = float(sum(1 for r in rows if bool(r["pass_flag_lt_1pct"])) / max(1, len(rows)))
        pair_summary.append(
            {
                "pair_id": str(pid),
                "window_id": "window_pre_mix",
                "median_Delta_max": float(med),
                "pass_rate_lt_1pct": float(pass_rate),
                "sample_count": int(len(rows)),
            }
        )

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "v3_generation_aligned_equivalence_panel_v1",
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "global_seed": int(global_seed),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "systems": [asdict(s) for s in systems],
        "pair_defs": pair_defs,
        "system_rows": system_rows,
        "pair_rows": pair_rows,
        "pair_summary": pair_summary,
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
                "kernel_profile",
                "convention_id",
                "stencil_id",
                "seed_id",
                "system_id",
                "generation_offset_signature",
                "window_id",
                "T_cycle",
                "R_hat",
                "Omega_hat",
                "S_stab",
                "V_hat",
                "H_phase_summary",
                "pair_id",
                "Delta_max_pair",
                "pass_flag_lt_1pct",
            ]
        )
        pair_lookup: Dict[Tuple[str, int, str, str, int, int, int], Tuple[str, float, bool]] = {}
        for pr in payload["pair_rows"]:
            lk = (
                str(pr["lhs_system_id"]),
                int(pr["seed_id"]),
                str(pr["boundary_mode"]),
                str(pr["orientation"]),
                int(pr["size_x"]),
                int(pr["size_y"]),
                int(pr["size_z"]),
            )
            rk = (
                str(pr["rhs_system_id"]),
                int(pr["seed_id"]),
                str(pr["boundary_mode"]),
                str(pr["orientation"]),
                int(pr["size_x"]),
                int(pr["size_y"]),
                int(pr["size_z"]),
            )
            val = (str(pr["pair_id"]), float(pr["Delta_max_pair"]), bool(pr["pass_flag_lt_1pct"]))
            pair_lookup[lk] = val
            pair_lookup[rk] = val

        for row in payload["system_rows"]:
            key = (
                str(row["system_id"]),
                int(row["seed_id"]),
                str(row["boundary_mode"]),
                str(row["orientation"]),
                int(row["size"][0]),
                int(row["size"][1]),
                int(row["size"][2]),
            )
            p = pair_lookup.get(key, ("", 0.0, False))
            w.writerow(
                [
                    str(row["kernel_profile"]),
                    str(row["convention_id"]),
                    str(row["stencil_id"]),
                    int(row["seed_id"]),
                    str(row["system_id"]),
                    str(row["generation_offset_signature"]),
                    str(row["window_id"]),
                    int(row["T_cycle"]),
                    float(row["R_hat"]),
                    float(row["Omega_hat"]),
                    float(row["S_stab"]),
                    float(row["V_hat"]),
                    str(row["H_phase_summary"]),
                    str(p[0]),
                    float(p[1]),
                    bool(p[2]),
                ]
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--global-seed", type=int, default=1337)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    payload = build_payload(global_seed=int(args.global_seed), quick=bool(args.quick))
    write_artifacts(payload)
    top = payload["pair_summary"][0] if payload["pair_summary"] else {}
    print(
        "v3_generation_aligned_equivalence_panel_v1: "
        f"pairs={len(payload['pair_summary'])}, "
        f"top_pair_median_Delta_max={float(top.get('median_Delta_max', 0.0)):.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Render one-particle ground vs excited motif visualization (v1).

Outputs:
1) comparative GIF with three panels:
   - ground motif (E0 control)
   - excited motif #1
   - excited motif #2
2) manifest JSON and companion markdown.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from calc.xor_scenario_loader import canonical_motif_state_map
from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_REPO_PATH = "cog_v2/calc/build_particle_ground_vs_excited_visual_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
LIB_JSON = ROOT / "cog_v2" / "sources" / "particle_excited_propagation_cycle_library_v1.json"
OUT_DIR = ROOT / "website" / "data" / "visuals" / "motif_gifs"
OUT_JSON = ROOT / "cog_v2" / "sources" / "particle_ground_vs_excited_motif_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "particle_ground_vs_excited_motif_v1.md"


@dataclass(frozen=True)
class VizParams:
    particle_id: str = "left_spinor_muon_motif"
    fps: int = 2
    dpi: int = 120
    ticks_ground: int = 24
    burn_in_ground: int = 6
    max_period_ground: int = 12
    size_xyz_ground: int = 7
    fold_offsets_ground: Tuple[Tuple[int, int, int], ...] = (
        (-1, 0, 0),
        (1, 0, 0),
        (0, -1, 0),
        (0, 1, 0),
        (0, 0, -1),
        (0, 0, 1),
    )
    render_gif: bool = True


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_cxo(state_gi: Sequence[Tuple[int, int]]) -> k.CxO:
    vals = [k.GInt(int(re), int(im)) for re, im in state_gi]
    return k.project_cxo_to_unity((vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7]))


def _serialize_state(state: k.CxO) -> List[List[int]]:
    return [[int(z.re), int(z.im)] for z in state]


def _idx(x: int, y: int, z: int, n: int) -> int:
    return (int(x) * int(n) + int(y)) * int(n) + int(z)


def _cell_nonvac_power(cell: Sequence[Sequence[int]]) -> float:
    return float(sum(int(v[0]) * int(v[0]) + int(v[1]) * int(v[1]) for v in cell[1:8]))


def _x_profile_from_world_dense(world_state_dense: Sequence[Sequence[Sequence[int]]]) -> List[float]:
    n3 = len(world_state_dense)
    n = round(n3 ** (1.0 / 3.0))
    if n * n * n != n3:
        raise ValueError(f"world_state_dense length {n3} is not cubic")
    out = [0.0 for _ in range(n)]
    for x, y, z in itertools.product(range(n), repeat=3):
        cell = world_state_dense[_idx(x, y, z, n)]
        out[x] += _cell_nonvac_power(cell)
    return out


def _roll_until_equal(history: Sequence[List[k.CxO]], start: int, max_period: int) -> int | None:
    tmax = len(history) - 1
    for t0 in range(int(start), tmax):
        for p in range(1, int(max_period) + 1):
            t1 = t0 + p
            if t1 > tmax:
                break
            if history[t0] == history[t1]:
                return int(p)
    return None


def _build_ground_cycle_rows(params: VizParams, particle_state: k.CxO) -> List[Dict[str, Any]]:
    n = int(params.size_xyz_ground)
    center = (n // 2, n // 2, n // 2)
    world: List[k.CxO] = [k.cxo_one() for _ in range(n * n * n)]
    world[_idx(center[0], center[1], center[2], n)] = particle_state

    history: List[List[k.CxO]] = [list(world)]
    for _ in range(int(params.ticks_ground)):
        old = world
        nxt: List[k.CxO] = [k.cxo_one() for _ in range(n * n * n)]
        for x, y, z in itertools.product(range(n), repeat=3):
            msgs: List[k.CxO] = []
            for dx, dy, dz in params.fold_offsets_ground:
                qx = (x + int(dx)) % n
                qy = (y + int(dy)) % n
                qz = (z + int(dz)) % n
                msgs.append(old[_idx(qx, qy, qz, n)])
            nxt[_idx(x, y, z, n)] = k.update_rule(old[_idx(x, y, z, n)], msgs)
        world = nxt
        history.append(list(world))

    period = _roll_until_equal(history, start=int(params.burn_in_ground), max_period=int(params.max_period_ground))
    if period is None:
        period = 1
    t0 = int(params.burn_in_ground)
    rows: List[Dict[str, Any]] = []
    for step in range(int(period)):
        world_row = history[t0 + step]
        rows.append(
            {
                "cycle_step": int(step),
                "tick": int(t0 + step),
                "world_state_dense": [_serialize_state(s) for s in world_row],
            }
        )
    return rows


def _load_excited_cases(particle_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    payload = json.loads(LIB_JSON.read_text(encoding="utf-8"))
    for prow in payload.get("particles", []):
        if str(prow.get("particle_id")) != str(particle_id):
            continue
        cases = list(prow.get("selected_cases", []))
        if len(cases) < 2:
            raise ValueError(f"particle {particle_id} has <2 excited cases in library")
        return cases[0], cases[1]
    raise KeyError(f"particle_id not found in excited cycle library: {particle_id}")


def _render_gif(
    *,
    particle_id: str,
    gif_path: Path,
    lanes: Sequence[Dict[str, Any]],
    fps: int,
    dpi: int,
) -> Dict[str, Any]:
    # Determine frame count as lcm of lane periods.
    periods = [max(1, int(len(l["cycle_rows"]))) for l in lanes]
    frame_count = 1
    for p in periods:
        frame_count = math.lcm(frame_count, int(p))

    x_len = len(_x_profile_from_world_dense(lanes[0]["cycle_rows"][0]["world_state_dense"]))
    max_y = 1.0
    lane_profiles: List[List[List[float]]] = []
    for lane in lanes:
        seq = []
        for row in lane["cycle_rows"]:
            prof = _x_profile_from_world_dense(row["world_state_dense"])
            seq.append(prof)
            max_y = max(max_y, max(prof) if prof else 0.0)
        lane_profiles.append(seq)

    fig, axes = plt.subplots(3, 1, figsize=(10.8, 7.2), facecolor="#0B1021", sharex=True)
    for ax in axes:
        ax.set_facecolor("#101A34")
        ax.grid(True, color="#294062", alpha=0.4, linestyle="--", linewidth=0.7)
        for spine in ax.spines.values():
            spine.set_color("#355377")
            spine.set_linewidth(1.0)
        ax.tick_params(colors="#D2E4F6")
    lines = []
    for i, ax in enumerate(axes):
        (ln,) = ax.plot(range(x_len), [0.0] * x_len, color=["#58A6FF", "#F4B400", "#64D992"][i], linewidth=2.2)
        lines.append(ln)
        ax.set_ylim(0.0, max_y * 1.10)
        ax.set_ylabel("Non-vac power", color="#D2E4F6", fontsize=9)
        ax.set_title(lanes[i]["label"], color="#F4F8FF", fontsize=11, loc="left")
    axes[-1].set_xlabel("x channel index", color="#D2E4F6")
    suptitle = fig.suptitle("", color="#F4F8FF", fontsize=13, fontweight="bold")

    def update(frame: int) -> List[Any]:
        artists: List[Any] = [suptitle]
        for i, ln in enumerate(lines):
            seq = lane_profiles[i]
            prof = seq[frame % len(seq)]
            ln.set_data(list(range(len(prof))), prof)
            artists.append(ln)
        suptitle.set_text(f"{particle_id}  |  frame {frame + 1}/{frame_count}")
        return artists

    anim = FuncAnimation(fig, update, frames=frame_count, interval=max(120, int(1000 / max(1, fps))), blit=False)
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    anim.save(str(gif_path), writer=PillowWriter(fps=max(1, int(fps))), dpi=int(dpi))
    plt.close(fig)
    return {
        "frame_count": int(frame_count),
        "periods": [int(p) for p in periods],
        "x_len": int(x_len),
        "max_nonvac_power": float(max_y),
    }


def build_payload(params: VizParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else VizParams()
    motifs = canonical_motif_state_map()
    if p.particle_id not in motifs:
        raise KeyError(f"unknown particle_id: {p.particle_id}")
    particle_state = _to_cxo(motifs[p.particle_id])

    ground_rows = _build_ground_cycle_rows(p, particle_state)
    ex1, ex2 = _load_excited_cases(p.particle_id)

    lanes = [
        {
            "label": "Ground (E0 control)",
            "energy_id": "E0_control",
            "cycle_rows": ground_rows,
        },
        {
            "label": f"Excited #1 ({ex1['energy_id']})",
            "energy_id": str(ex1["energy_id"]),
            "cycle_rows": ex1["cycle_rows_post_transient"],
            "selected_op_idx": int(ex1["perturbation"]["center_op_idx"]),
        },
        {
            "label": f"Excited #2 ({ex2['energy_id']})",
            "energy_id": str(ex2["energy_id"]),
            "cycle_rows": ex2["cycle_rows_post_transient"],
            "selected_op_idx": int(ex2["perturbation"]["center_op_idx"]),
        },
    ]

    gif_name = f"{p.particle_id}_ground_vs_excited_v1.gif"
    gif_path = OUT_DIR / gif_name
    render_meta: Dict[str, Any] = {
        "frame_count": 0,
        "periods": [len(l["cycle_rows"]) for l in lanes],
        "x_len": 0,
        "max_nonvac_power": 0.0,
    }
    if p.render_gif:
        render_meta = _render_gif(
            particle_id=p.particle_id,
            gif_path=gif_path,
            lanes=lanes,
            fps=int(p.fps),
            dpi=int(p.dpi),
        )

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "particle_ground_vs_excited_visual_v1",
        "claim_id": "MOTIF-VIS-001",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "projector_id": k.PROJECTOR_ID,
        "particle_id": p.particle_id,
        "params": {
            "fps": int(p.fps),
            "dpi": int(p.dpi),
            "ticks_ground": int(p.ticks_ground),
            "burn_in_ground": int(p.burn_in_ground),
            "max_period_ground": int(p.max_period_ground),
            "size_xyz_ground": int(p.size_xyz_ground),
            "render_gif": bool(p.render_gif),
        },
        "lanes": [
            {
                "label": str(l["label"]),
                "energy_id": str(l["energy_id"]),
                "period_ticks": int(len(l["cycle_rows"])),
                "selected_op_idx": l.get("selected_op_idx"),
            }
            for l in lanes
        ],
        "gif_repo_path": str(gif_path.relative_to(ROOT)).replace("\\", "/") if p.render_gif else None,
        "render": render_meta,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# Particle Ground vs Excited Visualization (v1)",
        "",
        f"- particle_id: `{payload['particle_id']}`",
        f"- replay_hash: `{payload['replay_hash']}`",
        "",
        "## Lanes",
        "",
        "| label | energy_id | period_ticks | op_idx |",
        "|---|---|---:|---:|",
    ]
    for lane in payload["lanes"]:
        op = lane["selected_op_idx"]
        op_txt = "n/a" if op is None else str(op)
        lines.append(f"| `{lane['label']}` | `{lane['energy_id']}` | {lane['period_ticks']} | {op_txt} |")
    gif_path = payload.get("gif_repo_path")
    if gif_path:
        rp = str(gif_path).replace("\\", "/")
        web_path = "/" + rp
        if rp.startswith("website/data/"):
            web_path = "/web/data/" + rp[len("website/data/") :]
        lines.extend(
            [
                "",
                "## GIF",
                "",
                f"- file: `{gif_path}`",
                "",
                f"![{payload['particle_id']} ground vs excited]({web_path})",
            ]
        )
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
    parser.add_argument("--particle-id", type=str, default=VizParams.particle_id)
    parser.add_argument("--fps", type=int, default=VizParams.fps)
    parser.add_argument("--dpi", type=int, default=VizParams.dpi)
    parser.add_argument("--ticks-ground", type=int, default=VizParams.ticks_ground)
    parser.add_argument("--burn-in-ground", type=int, default=VizParams.burn_in_ground)
    parser.add_argument("--max-period-ground", type=int, default=VizParams.max_period_ground)
    parser.add_argument("--size-ground", type=int, default=VizParams.size_xyz_ground)
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args()

    payload = build_payload(
        VizParams(
            particle_id=str(args.particle_id),
            fps=int(args.fps),
            dpi=int(args.dpi),
            ticks_ground=int(args.ticks_ground),
            burn_in_ground=int(args.burn_in_ground),
            max_period_ground=int(args.max_period_ground),
            size_xyz_ground=int(args.size_ground),
            render_gif=not bool(args.no_render),
        )
    )
    write_artifacts(payload)
    print(
        "particle_ground_vs_excited_visual_v1: "
        f"particle={payload['particle_id']}, "
        f"periods={[l['period_ticks'] for l in payload['lanes']]}, "
        f"rendered={payload['gif_repo_path'] is not None}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

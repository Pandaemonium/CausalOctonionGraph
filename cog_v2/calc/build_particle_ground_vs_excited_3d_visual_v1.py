"""Render 3D ground-vs-excited motif visuals for one particle (v1).

Artifacts:
1) 3D overview GIF (ground + two excited lanes),
2) 16-panel channel/component atlas GIF for excited lane #1,
3) JSON + markdown manifest.
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

from calc.xor_scenario_loader import canonical_motif_state_map
from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_REPO_PATH = "cog_v2/calc/build_particle_ground_vs_excited_3d_visual_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
LIB_JSON = ROOT / "cog_v2" / "sources" / "particle_excited_propagation_cycle_library_v2.json"
OUT_DIR = ROOT / "website" / "data" / "visuals" / "motif_gifs"
OUT_JSON = ROOT / "cog_v2" / "sources" / "particle_ground_vs_excited_3d_visual_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "particle_ground_vs_excited_3d_visual_v1.md"


@dataclass(frozen=True)
class Viz3DParams:
    particle_id: str = "left_spinor_muon_motif"
    fps: int = 2
    dpi: int = 120
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


def _world_to_nonvac_grid(world_state_dense: Sequence[Sequence[Sequence[int]]]) -> np.ndarray:
    import numpy as np

    n3 = len(world_state_dense)
    n = round(n3 ** (1.0 / 3.0))
    if n * n * n != n3:
        raise ValueError(f"world_state_dense length {n3} is not cubic")
    arr = np.zeros((n, n, n), dtype=float)
    for x, y, z in itertools.product(range(n), repeat=3):
        arr[x, y, z] = _cell_nonvac_power(world_state_dense[_idx(x, y, z, n)])
    return arr


def _world_to_delta_grid(
    curr_world: Sequence[Sequence[Sequence[int]]],
    prev_world: Sequence[Sequence[Sequence[int]]],
) -> np.ndarray:
    """Per-voxel change intensity: number of changed octonion coefficients (0..8)."""
    import numpy as np

    n3 = len(curr_world)
    n = round(n3 ** (1.0 / 3.0))
    if n * n * n != n3 or len(prev_world) != n3:
        raise ValueError("delta grid inputs must be equally sized cubic worlds")
    arr = np.zeros((n, n, n), dtype=float)
    for x, y, z in itertools.product(range(n), repeat=3):
        i = _idx(x, y, z, n)
        c = curr_world[i]
        p = prev_world[i]
        arr[x, y, z] = float(sum(1 for a, b in zip(c, p) if a != b))
    return arr


def _world_to_channel_component_maps(
    world_state_dense: Sequence[Sequence[Sequence[int]]],
) -> np.ndarray:
    import numpy as np

    """Returns array [8,2,n,n] with z-summed signed maps for each channel/component."""
    n3 = len(world_state_dense)
    n = round(n3 ** (1.0 / 3.0))
    if n * n * n != n3:
        raise ValueError(f"world_state_dense length {n3} is not cubic")
    out = np.zeros((8, 2, n, n), dtype=float)
    for x, y, z in itertools.product(range(n), repeat=3):
        cell = world_state_dense[_idx(x, y, z, n)]
        for ch in range(8):
            re, im = int(cell[ch][0]), int(cell[ch][1])
            out[ch, 0, x, y] += float(re)
            out[ch, 1, x, y] += float(im)
    return out


def _load_excited_cases(particle_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    payload = json.loads(LIB_JSON.read_text(encoding="utf-8"))
    for prow in payload.get("particles", []):
        if str(prow.get("particle_id")) != str(particle_id):
            continue
        cases = list(prow.get("selected_cases", []))
        if len(cases) < 2:
            raise ValueError(f"particle {particle_id} has <2 excited cases in v2 library")
        return cases[0], cases[1]
    raise KeyError(f"particle_id not found in v2 excited cycle library: {particle_id}")


def _build_ground_row(particle_id: str, n: int) -> Dict[str, Any]:
    motifs = canonical_motif_state_map()
    if particle_id not in motifs:
        raise KeyError(f"unknown particle_id: {particle_id}")
    particle_state = _to_cxo(motifs[particle_id])
    world: List[k.CxO] = [k.cxo_one() for _ in range(n * n * n)]
    c = n // 2
    world[_idx(c, c, c, n)] = particle_state
    return {
        "cycle_step": 0,
        "tick": 0,
        "world_state_dense": [_serialize_state(s) for s in world],
    }


def _render_3d_overview_gif(
    *,
    particle_id: str,
    lanes: Sequence[Dict[str, Any]],
    out_path: Path,
    fps: int,
    dpi: int,
) -> Dict[str, Any]:
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    import numpy as np

    periods = [max(1, int(len(l["cycle_rows"]))) for l in lanes]
    frame_count = 1
    for p in periods:
        frame_count = math.lcm(frame_count, int(p))

    sample_grid = _world_to_nonvac_grid(lanes[0]["cycle_rows"][0]["world_state_dense"])
    n = int(sample_grid.shape[0])
    coords = np.array(list(itertools.product(range(n), range(n), range(n))), dtype=float)

    lane_grids: List[List[np.ndarray]] = []
    lane_modes: List[str] = []
    vmax = 1.0
    for lane in lanes:
        rows = lane["cycle_rows"]
        period = max(1, len(rows))
        if period <= 1:
            seq = [_world_to_nonvac_grid(rows[0]["world_state_dense"])]
            lane_modes.append("nonvac")
        else:
            # Dynamic mode for excited lanes: visualize per-step change, not invariant magnitude.
            seq = []
            for i in range(period):
                curr = rows[i]["world_state_dense"]
                prev = rows[(i - 1) % period]["world_state_dense"]
                seq.append(_world_to_delta_grid(curr, prev))
            lane_modes.append("delta")
        for g in seq:
            vmax = max(vmax, float(np.max(g)))
        lane_grids.append(seq)

    fig = plt.figure(figsize=(12.8, 4.8), facecolor="#0B1021")
    axes = [
        fig.add_subplot(1, 3, 1, projection="3d"),
        fig.add_subplot(1, 3, 2, projection="3d"),
        fig.add_subplot(1, 3, 3, projection="3d"),
    ]
    scatters = []
    for i, ax in enumerate(axes):
        ax.set_facecolor("#101A34")
        ax.set_xlim(0, n - 1)
        ax.set_ylim(0, n - 1)
        ax.set_zlim(0, n - 1)
        ax.set_xlabel("x", color="#D2E4F6", fontsize=8)
        ax.set_ylabel("y", color="#D2E4F6", fontsize=8)
        ax.set_zlabel("z", color="#D2E4F6", fontsize=8)
        ax.tick_params(colors="#D2E4F6", labelsize=7)
        ax.set_title(lanes[i]["label"], color="#F4F8FF", fontsize=10)
        sc = ax.scatter([], [], [], c=[], cmap="viridis", vmin=0.0, vmax=vmax, s=16, alpha=0.9)
        scatters.append(sc)
    title = fig.suptitle("", color="#F4F8FF", fontsize=12, fontweight="bold")

    def update(frame: int) -> List[Any]:
        artists: List[Any] = [title]
        for li, sc in enumerate(scatters):
            grid = lane_grids[li][frame % len(lane_grids[li])]
            flat = grid.reshape(-1)
            mask = flat > 0.0
            pts = coords[mask]
            vals = flat[mask]
            if len(pts) == 0:
                pts = np.array([[0.0, 0.0, 0.0]])
                vals = np.array([0.0])
            sc._offsets3d = (pts[:, 0], pts[:, 1], pts[:, 2])  # noqa: SLF001
            sc.set_array(vals)
            artists.append(sc)
        title.set_text(f"{particle_id} | 3D overview (nonvac/delta) | frame {frame + 1}/{frame_count}")
        return artists

    anim = FuncAnimation(fig, update, frames=frame_count, interval=max(120, int(1000 / max(1, fps))), blit=False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    anim.save(str(out_path), writer=PillowWriter(fps=max(1, int(fps))), dpi=int(dpi))
    plt.close(fig)
    return {
        "frame_count": int(frame_count),
        "periods": [int(p) for p in periods],
        "lane_modes": lane_modes,
        "grid_size": int(n),
        "max_nonvac_power": float(vmax),
    }


def _render_channel16_gif(
    *,
    particle_id: str,
    lane_label: str,
    cycle_rows: Sequence[Dict[str, Any]],
    out_path: Path,
    fps: int,
    dpi: int,
) -> Dict[str, Any]:
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    import numpy as np

    period = int(max(1, len(cycle_rows)))
    maps = [_world_to_channel_component_maps(row["world_state_dense"]) for row in cycle_rows]
    vmax = max(1.0, max(float(np.max(np.abs(m))) for m in maps))
    n = int(maps[0].shape[-1])

    fig, axes = plt.subplots(8, 2, figsize=(8.4, 18.0), facecolor="#0B1021")
    ims = []
    for ch in range(8):
        for c in range(2):
            ax = axes[ch, c]
            ax.set_facecolor("#101A34")
            ax.set_xticks([])
            ax.set_yticks([])
            if ch == 0:
                ax.set_title("Re" if c == 0 else "Im", color="#F4F8FF", fontsize=9)
            if c == 0:
                ax.set_ylabel(f"e{ch:03b}", color="#D2E4F6", fontsize=8, rotation=0, labelpad=18, va="center")
            im = ax.imshow(np.zeros((n, n), dtype=float), cmap="coolwarm", vmin=-vmax, vmax=vmax, origin="lower")
            ims.append((ch, c, im))
    title = fig.suptitle("", color="#F4F8FF", fontsize=12, fontweight="bold")

    def update(frame: int) -> List[Any]:
        artists: List[Any] = [title]
        mp = maps[frame % period]
        for ch, c, im in ims:
            im.set_data(mp[ch, c])
            artists.append(im)
        title.set_text(f"{particle_id} | {lane_label} | channel(8) x component(2) | frame {frame + 1}/{period}")
        return artists

    anim = FuncAnimation(fig, update, frames=period, interval=max(120, int(1000 / max(1, fps))), blit=False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    anim.save(str(out_path), writer=PillowWriter(fps=max(1, int(fps))), dpi=int(dpi))
    plt.close(fig)
    return {
        "frame_count": int(period),
        "grid_size": int(n),
        "value_abs_max": float(vmax),
    }


def build_payload(params: Viz3DParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else Viz3DParams()
    ex1, ex2 = _load_excited_cases(p.particle_id)
    n3 = len(ex1["cycle_rows_post_transient"][0]["world_state_dense"])
    n = round(n3 ** (1.0 / 3.0))
    if n * n * n != n3:
        raise ValueError("excited cycle world is not cubic")

    ground = _build_ground_row(p.particle_id, n)
    lanes = [
        {"label": "Ground (E0 control)", "energy_id": "E0_control", "cycle_rows": [ground]},
        {"label": f"Excited #1 ({ex1['energy_id']}, op {ex1['perturbation']['center_op_idx']})", "energy_id": ex1["energy_id"], "cycle_rows": ex1["cycle_rows_post_transient"]},
        {"label": f"Excited #2 ({ex2['energy_id']}, op {ex2['perturbation']['center_op_idx']})", "energy_id": ex2["energy_id"], "cycle_rows": ex2["cycle_rows_post_transient"]},
    ]

    overview_gif = OUT_DIR / f"{p.particle_id}_ground_vs_excited_3d_overview_v1.gif"
    atlas_gif = OUT_DIR / f"{p.particle_id}_excited1_channel16_v1.gif"
    overview_meta = {"frame_count": 0, "periods": [len(l["cycle_rows"]) for l in lanes], "grid_size": int(n), "max_nonvac_power": 0.0}
    atlas_meta = {"frame_count": 0, "grid_size": int(n), "value_abs_max": 0.0}
    if p.render_gif:
        overview_meta = _render_3d_overview_gif(
            particle_id=p.particle_id,
            lanes=lanes,
            out_path=overview_gif,
            fps=int(p.fps),
            dpi=int(p.dpi),
        )
        atlas_meta = _render_channel16_gif(
            particle_id=p.particle_id,
            lane_label="Excited #1",
            cycle_rows=ex1["cycle_rows_post_transient"],
            out_path=atlas_gif,
            fps=int(p.fps),
            dpi=int(p.dpi),
        )

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "particle_ground_vs_excited_3d_visual_v1",
        "claim_id": "MOTIF-VIS-3D-001",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "projector_id": k.PROJECTOR_ID,
        "library_source": str(LIB_JSON.relative_to(ROOT)).replace("\\", "/"),
        "particle_id": p.particle_id,
        "params": {"fps": int(p.fps), "dpi": int(p.dpi), "render_gif": bool(p.render_gif)},
        "lanes": [
            {"label": str(l["label"]), "energy_id": str(l["energy_id"]), "period_ticks": int(len(l["cycle_rows"]))}
            for l in lanes
        ],
        "overview_gif_repo_path": str(overview_gif.relative_to(ROOT)).replace("\\", "/") if p.render_gif else None,
        "channel16_gif_repo_path": str(atlas_gif.relative_to(ROOT)).replace("\\", "/") if p.render_gif else None,
        "overview_render": overview_meta,
        "channel16_render": atlas_meta,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _to_web_path(repo_path: str | None) -> str | None:
    if repo_path is None:
        return None
    rp = str(repo_path).replace("\\", "/")
    if rp.startswith("website/data/"):
        return "/web/data/" + rp[len("website/data/") :]
    return "/" + rp


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# Particle Ground vs Excited 3D Visualization (v1)",
        "",
        f"- particle_id: `{payload['particle_id']}`",
        f"- replay_hash: `{payload['replay_hash']}`",
        "",
        "## Lanes",
        "",
        "| label | energy_id | period_ticks |",
        "|---|---|---:|",
    ]
    for lane in payload["lanes"]:
        lines.append(f"| `{lane['label']}` | `{lane['energy_id']}` | {lane['period_ticks']} |")

    ov_repo = payload.get("overview_gif_repo_path")
    ch_repo = payload.get("channel16_gif_repo_path")
    ov_web = _to_web_path(ov_repo)
    ch_web = _to_web_path(ch_repo)
    if ov_repo:
        lines.extend(
            [
                "",
                "## 3D Overview GIF",
                "",
                f"- file: `{ov_repo}`",
                "",
                f"![{payload['particle_id']} 3d overview]({ov_web})",
            ]
        )
    if ch_repo:
        lines.extend(
            [
                "",
                "## Channel x Component (16) GIF",
                "",
                f"- file: `{ch_repo}`",
                "",
                f"![{payload['particle_id']} channel16 atlas]({ch_web})",
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
    parser.add_argument("--particle-id", type=str, default=Viz3DParams.particle_id)
    parser.add_argument("--fps", type=int, default=Viz3DParams.fps)
    parser.add_argument("--dpi", type=int, default=Viz3DParams.dpi)
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args()
    payload = build_payload(
        Viz3DParams(
            particle_id=str(args.particle_id),
            fps=int(args.fps),
            dpi=int(args.dpi),
            render_gif=not bool(args.no_render),
        )
    )
    write_artifacts(payload)
    print(
        "particle_ground_vs_excited_3d_visual_v1: "
        f"particle={payload['particle_id']}, "
        f"overview_rendered={payload['overview_gif_repo_path'] is not None}, "
        f"channel16_rendered={payload['channel16_gif_repo_path'] is not None}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

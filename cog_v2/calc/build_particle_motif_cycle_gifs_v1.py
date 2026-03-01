"""Render one-cycle, tick-by-tick GIFs for canonical XOR particle motifs.

This script builds visual artifacts for the website:
  - GIF per motif (one full period under e111 action)
  - manifest JSON with deterministic ordering and metadata
  - companion markdown index for quick embedding/review
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from calc.xor_furey_ideals import StateGI, detect_period, e7_left, e7_right, gi_is_zero
from calc.xor_scenario_loader import canonical_motif_state_map


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_REPO_PATH = "cog_v2/calc/build_particle_motif_cycle_gifs_v1.py"
OUT_DIR = ROOT / "website" / "data" / "visuals" / "motif_gifs"
OUT_JSON = OUT_DIR / "particle_motif_cycle_gifs_v1.json"
OUT_MD = ROOT / "website" / "pages" / "particle_motif_cycle_gif_atlas.md"
OUT_INDEX_MD = ROOT / "cog_v2" / "sources" / "particle_motif_cycle_gifs_v1.md"
MAX_PERIOD_SCAN = 64
OP_INDEX = 7  # e111
DEFAULT_HAND = "left"
CANVAS_DPI = 130
GIF_FPS = 2


PHASE_COLORS = {
    "0": "#27364E",
    "+1": "#FFD166",
    "-1": "#EF476F",
    "+i": "#06D6A0",
    "-i": "#118AB2",
}

TEXT_COLOR = "#E8F3FF"
MUTED_TEXT_COLOR = "#AFC5DD"
EDGE_COLOR = "#436184"
PANEL_BG = "#0B1021"
PLOT_BG = "#101A34"


PRETTY_LABELS = {
    "left_spinor_electron_ideal": "Electron (left spinor ideal)",
    "right_spinor_electron_ideal": "Dual Electron (right spinor ideal)",
    "su_triple_electron": "Electron Triple (Su)",
    "sd_triple_dual_electron": "Dual Electron Triple (Sd)",
    "vector_proton_proto_t124": "Proton-Proto Vector Motif",
    "vector_electron_favored": "Electron-Favored Vector Motif",
    "su_vacuum_omega": "Vacuum Omega (Su)",
    "sd_vacuum_omega_dag": "Vacuum Omega Dagger (Sd)",
    "left_spinor_muon_motif": "Muon Motif (left spinor)",
    "left_spinor_tau_motif": "Tau Motif (left spinor)",
}


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _channel_label(idx: int) -> str:
    return f"e{idx:03b}"


def _format_coeff(coeff: Tuple[int, int]) -> str:
    re, im = int(coeff[0]), int(coeff[1])
    if re == 0 and im == 0:
        return "0"
    if im == 0:
        return str(re)
    if re == 0:
        return f"{im}i"
    sign = "+" if im >= 0 else "-"
    return f"{re}{sign}{abs(im)}i"


def _dominant_phase(coeff: Tuple[int, int]) -> str:
    re, im = int(coeff[0]), int(coeff[1])
    if re == 0 and im == 0:
        return "0"
    if abs(re) >= abs(im):
        return "+1" if re >= 0 else "-1"
    return "+i" if im >= 0 else "-i"


def _abs2(coeff: Tuple[int, int]) -> int:
    return int(coeff[0] * coeff[0] + coeff[1] * coeff[1])


def _projected_coords(idx: int) -> Tuple[float, float]:
    x = float((idx >> 2) & 1)
    y = float((idx >> 1) & 1)
    z = float(idx & 1)
    return (x + 0.42 * z, y + 0.30 * z)


def _cube_edges() -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    for i in range(8):
        for j in range(i + 1, 8):
            if bin(i ^ j).count("1") == 1:
                out.append((i, j))
    return out


def _friendly_motif_label(motif_id: str) -> str:
    return PRETTY_LABELS.get(motif_id, motif_id.replace("_", " ").title())


def _gif_filename(motif_id: str, hand: str) -> str:
    safe = motif_id.replace("/", "_").replace("\\", "_")
    return f"{safe}_e111_{hand}_cycle.gif"


def _is_particle_candidate(motif_id: str) -> bool:
    keys = ("electron", "muon", "tau", "proton", "vacuum", "neutrino", "photon")
    lower = motif_id.lower()
    return any(k in lower for k in keys)


def _candidate_motif_ids(all_ids: Iterable[str]) -> List[str]:
    keep = [mid for mid in sorted(all_ids) if _is_particle_candidate(mid)]
    return keep


def _state_support_labels(state: StateGI) -> List[str]:
    return [_channel_label(i) for i, coeff in enumerate(state) if not gi_is_zero(coeff)]


def _build_cycle_states(initial: StateGI, hand: str) -> Tuple[List[StateGI], int]:
    step_fn = e7_left if hand == "left" else e7_right
    period_raw = detect_period(initial, step_fn, max_steps=MAX_PERIOD_SCAN)
    period = int(period_raw) if period_raw is not None and int(period_raw) > 0 else 1
    states = [initial]
    cur = initial
    for _ in range(1, period):
        cur = step_fn(cur)
        states.append(cur)
    return states, period


def _render_single_gif(
    *,
    motif_id: str,
    motif_label: str,
    state0: StateGI,
    hand: str,
    out_path: Path,
) -> Dict[str, Any]:
    states, period = _build_cycle_states(state0, hand=hand)

    fig = plt.figure(figsize=(9.4, 5.2), facecolor=PANEL_BG)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.35, 1.0], height_ratios=[1.0, 1.0], wspace=0.15, hspace=0.18)
    ax_cube = fig.add_subplot(gs[:, 0])
    ax_text = fig.add_subplot(gs[0, 1])
    ax_bar = fig.add_subplot(gs[1, 1])

    for ax in (ax_cube, ax_text, ax_bar):
        ax.set_facecolor(PLOT_BG)

    coords = [_projected_coords(i) for i in range(8)]
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]

    for i, j in _cube_edges():
        ax_cube.plot([coords[i][0], coords[j][0]], [coords[i][1], coords[j][1]], color=EDGE_COLOR, lw=1.2, alpha=0.8)

    node_labels = []
    coeff_labels = []
    for i, (x, y) in enumerate(coords):
        node_labels.append(
            ax_cube.text(
                x,
                y - 0.08,
                _channel_label(i),
                color=MUTED_TEXT_COLOR,
                fontsize=9,
                ha="center",
                va="top",
                fontweight="bold",
            )
        )
        coeff_labels.append(
            ax_cube.text(
                x,
                y + 0.08,
                "",
                color=TEXT_COLOR,
                fontsize=8.5,
                ha="center",
                va="bottom",
            )
        )

    scatter = ax_cube.scatter(xs, ys, s=[140] * 8, c=[PHASE_COLORS["0"]] * 8, edgecolors="#D8E5F5", linewidths=1.0)

    ax_cube.set_xlim(min(xs) - 0.25, max(xs) + 0.25)
    ax_cube.set_ylim(min(ys) - 0.24, max(ys) + 0.26)
    ax_cube.set_xticks([])
    ax_cube.set_yticks([])
    ax_cube.set_aspect("equal")
    ax_cube.set_title("Octonion Cube Channels (e000..e111)", color=TEXT_COLOR, fontsize=12, pad=10, fontweight="bold")

    for spine in ax_cube.spines.values():
        spine.set_color("#284061")
        spine.set_linewidth(1.1)

    ax_text.set_xticks([])
    ax_text.set_yticks([])
    for spine in ax_text.spines.values():
        spine.set_color("#284061")
        spine.set_linewidth(1.1)
    info_text = ax_text.text(
        0.03,
        0.94,
        "",
        transform=ax_text.transAxes,
        color=TEXT_COLOR,
        fontsize=10.0,
        va="top",
        ha="left",
        linespacing=1.35,
    )

    bar_labels = [_channel_label(i) for i in range(8)]
    bars = ax_bar.bar(range(8), [0.0] * 8, color=[PHASE_COLORS["0"]] * 8, edgecolor="#D8E5F5", linewidth=0.8)
    ax_bar.set_xticks(range(8))
    ax_bar.set_xticklabels(bar_labels, rotation=35, ha="right", color=MUTED_TEXT_COLOR, fontsize=8.3)
    ax_bar.tick_params(axis="y", colors=MUTED_TEXT_COLOR, labelsize=8)
    ax_bar.set_ylabel("Magnitude", color=MUTED_TEXT_COLOR, fontsize=9)
    ax_bar.grid(axis="y", color="#233752", alpha=0.45, linewidth=0.8)
    for spine in ax_bar.spines.values():
        spine.set_color("#284061")
        spine.set_linewidth(1.1)

    max_mag = max(1.0, max(math.sqrt(_abs2(coeff)) for st in states for coeff in st))
    ax_bar.set_ylim(0.0, max_mag * 1.15)

    fig.suptitle(
        f"{motif_label}  |  One Full Cycle ({period} ticks)",
        color=TEXT_COLOR,
        fontsize=14.2,
        fontweight="bold",
        y=0.975,
    )

    def _update(frame: int):
        st = states[frame]
        colors: List[str] = []
        sizes: List[float] = []
        active_lines: List[str] = []

        for i, coeff in enumerate(st):
            ph = _dominant_phase(coeff)
            colors.append(PHASE_COLORS[ph])
            mag = math.sqrt(float(_abs2(coeff)))
            sizes.append(120.0 + 280.0 * (mag / max_mag if max_mag > 0 else 0.0))
            coeff_labels[i].set_text(_format_coeff(coeff) if not gi_is_zero(coeff) else "")

            if not gi_is_zero(coeff):
                active_lines.append(f"- {_channel_label(i)} = {_format_coeff(coeff)} ({ph})")

        scatter.set_color(colors)
        scatter.set_sizes(sizes)

        for i, coeff in enumerate(st):
            mag = math.sqrt(float(_abs2(coeff)))
            bars[i].set_height(mag)
            bars[i].set_color(PHASE_COLORS[_dominant_phase(coeff)])

        info_lines = [
            f"Motif: {motif_id}",
            f"Operator: e111 ({hand} action)",
            f"Tick: {frame + 1}/{period}",
            f"Support: {', '.join(_state_support_labels(st)) or 'none'}",
            "",
            "Active Channels:",
        ]
        if active_lines:
            info_lines.extend(active_lines[:8])
        else:
            info_lines.append("- none")
        info_text.set_text("\n".join(info_lines))

        return [scatter, info_text, *bars, *coeff_labels, *node_labels]

    anim = FuncAnimation(fig, _update, frames=len(states), interval=900, blit=False, repeat=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    anim.save(out_path, writer=PillowWriter(fps=GIF_FPS), dpi=CANVAS_DPI)
    plt.close(fig)

    entry: Dict[str, Any] = {
        "motif_id": motif_id,
        "motif_label": motif_label,
        "hand": hand,
        "period_ticks": int(period),
        "tick_frame_count": len(states),
        "support_labels_initial": _state_support_labels(state0),
        "gif_repo_path": _to_repo_path(out_path),
        "gif_web_path": "/" + _to_repo_path(out_path).replace("website/", "web/"),
        "gif_sha256": _sha_file(out_path),
        "operator_label": _channel_label(OP_INDEX),
    }
    return entry


def _render_index_markdown(payload: Dict[str, Any]) -> str:
    lines: List[str] = [
        "# Particle Motif Cycle GIFs (v1)",
        "",
        f"- generated_count: `{payload['generated_count']}`",
        f"- replay_hash: `{payload['replay_hash']}`",
        f"- operator: `{payload['operator_label']}`",
        "",
        "## Artifacts",
        "",
    ]
    for row in payload["artifacts"]:
        lines.extend(
            [
                f"### {row['motif_label']}",
                "",
                f"- motif_id: `{row['motif_id']}`",
                f"- period_ticks: `{row['period_ticks']}`",
                f"- support_initial: `{row['support_labels_initial']}`",
                f"- gif: `{row['gif_repo_path']}`",
                "",
                f"![{row['motif_label']}]({row['gif_web_path']})",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_website_page(payload: Dict[str, Any]) -> str:
    motif_ids = [str(x) for x in payload.get("motif_ids", [])]
    has_photon = any("photon" in m.lower() for m in motif_ids)
    has_neutrino = any("neutrino" in m.lower() for m in motif_ids)

    lines: List[str] = [
        "# Particle Motif GIF Atlas",
        "",
        "One-cycle, tick-by-tick visualizations of canonical XOR octonion motifs.",
        "",
        "Each panel shows:",
        "- left: octonion cube channels `e000..e111` (color = dominant phase, size = magnitude)",
        "- right: exact per-tick channel values and channel magnitude bars",
        "",
        "Update operator for this atlas: `e111` with **left action**.",
        "",
        "See also: [Cycle Atlas](/web/pages/cycle_atlas)",
        "",
    ]

    if not has_photon or not has_neutrino:
        missing: List[str] = []
        if not has_photon:
            missing.append("photon")
        if not has_neutrino:
            missing.append("neutrino")
        lines.extend(
            [
                f"Scope note: canonical motif map currently has no explicit `{', '.join(missing)}` motif IDs.",
                "Once those motif IDs are registered in `calc/xor_scenario_loader.py::canonical_motif_state_map`, this page can be regenerated to include them automatically.",
                "",
            ]
        )

    for row in payload["artifacts"]:
        lines.extend(
            [
                f"## {row['motif_label']}",
                "",
                f"- Motif ID: `{row['motif_id']}`",
                f"- Cycle period: `{row['period_ticks']}` ticks",
                f"- Initial support: `{row['support_labels_initial']}`",
                "",
                f"![{row['motif_label']} cycle]({row['gif_web_path']})",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def build_payload(motif_ids: Sequence[str] | None = None, hand: str = DEFAULT_HAND) -> Dict[str, Any]:
    if hand not in {"left", "right"}:
        raise ValueError("hand must be 'left' or 'right'")

    motifs = canonical_motif_state_map()
    selected_ids = list(motif_ids) if motif_ids else _candidate_motif_ids(motifs.keys())

    artifacts: List[Dict[str, Any]] = []
    for motif_id in selected_ids:
        if motif_id not in motifs:
            raise KeyError(f"unknown motif_id: {motif_id}")
        label = _friendly_motif_label(motif_id)
        gif_name = _gif_filename(motif_id, hand=hand)
        entry = _render_single_gif(
            motif_id=motif_id,
            motif_label=label,
            state0=motifs[motif_id],
            hand=hand,
            out_path=OUT_DIR / gif_name,
        )
        artifacts.append(entry)

    payload: Dict[str, Any] = {
        "schema_version": "particle_motif_cycle_gifs_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "operator_label": _channel_label(OP_INDEX),
        "hand": hand,
        "max_period_scan": int(MAX_PERIOD_SCAN),
        "generated_count": len(artifacts),
        "motif_ids": selected_ids,
        "artifacts": artifacts,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    OUT_INDEX_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_INDEX_MD.write_text(_render_index_markdown(payload), encoding="utf-8")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(_render_website_page(payload), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build particle motif one-cycle GIF atlas.")
    p.add_argument("--hand", choices=["left", "right"], default=DEFAULT_HAND, help="e111 action side")
    p.add_argument(
        "--motif-id",
        action="append",
        default=None,
        help="optional motif id (repeat flag to include multiple); default = all particle-candidate motifs",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload(motif_ids=args.motif_id, hand=args.hand)
    write_artifacts(payload)
    print(json.dumps({"generated_count": payload["generated_count"], "replay_hash": payload["replay_hash"]}, indent=2))


if __name__ == "__main__":
    main()

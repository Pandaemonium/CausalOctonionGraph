"""Generate 20 deterministic fine-structure test cases using world_code kernel.

Each case simulates:
1) two electron seeds separated by integer edge distance N,
2) relative phase offset P (applied as left e7 temporal commits),
3) deterministic per-tick CxO updates on a fixed 1D lightcone corridor.

Output:
1) JSON dataset with per-step photon-coupling rates once cones overlap,
2) CSV table with per-step rows across all cases.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, List, Tuple

from minimal_world_kernel import (
    CxO,
    GInt,
    ONE_G,
    ZERO_G,
    World,
    cxo_mul,
    step,
)


RESULTS_ROOT = Path("world_code/Python_code/results/fine_structure_20_cases")


@dataclass(frozen=True)
class CaseConfig:
    case_id: str
    edge_distance: int
    steps: int
    phase_offset: int


def _basis_state(idx: int, coeff: GInt) -> CxO:
    vals = [ZERO_G for _ in range(8)]
    vals[idx] = coeff
    return (
        vals[0],
        vals[1],
        vals[2],
        vals[3],
        vals[4],
        vals[5],
        vals[6],
        vals[7],
    )


def _electron_seed() -> CxO:
    vals = [ZERO_G for _ in range(8)]
    vals[1] = ONE_G
    vals[2] = ONE_G
    vals[3] = ONE_G
    return (
        vals[0],
        vals[1],
        vals[2],
        vals[3],
        vals[4],
        vals[5],
        vals[6],
        vals[7],
    )


def _vacuum_seed() -> CxO:
    return _basis_state(7, ONE_G)


def _temporal_commit(state: CxO) -> CxO:
    e7 = _basis_state(7, ONE_G)
    return cxo_mul(e7, state)


def _apply_phase_offset(state: CxO, offset: int) -> CxO:
    out = state
    for _ in range(max(0, int(offset))):
        out = _temporal_commit(out)
    return out


def _phase_bucket_8(z: GInt) -> int:
    re = int(z.re)
    im = int(z.im)
    if re == 0 and im == 0:
        return 0
    ar = abs(re)
    ai = abs(im)
    if re >= 0 and im >= 0:
        return 1 if ai > ar else 0
    if re < 0 and im >= 0:
        return 3 if ai > ar else 4
    if re < 0 and im < 0:
        return 5 if ai > ar else 4
    return 7 if ai > ar else 0


def _phase_jump_mod8(prev_bucket: int, cur_bucket: int) -> int:
    d = (cur_bucket - prev_bucket) % 8
    return min(d, 8 - d)


def _node_name(pos: int) -> str:
    if pos < 0:
        return f"x_m{abs(pos)}"
    return f"x_{pos}"


def _build_world(edge_distance: int, steps: int, phase_offset: int) -> Tuple[World, List[int], int, int]:
    left_pos = 0
    right_pos = int(edge_distance)
    extent = int(steps)
    min_pos = left_pos - extent
    max_pos = right_pos + extent
    positions = list(range(min_pos, max_pos + 1))
    node_ids = [_node_name(p) for p in positions]
    by_pos = {p: _node_name(p) for p in positions}

    parents: Dict[str, List[str]] = {}
    for p in positions:
        pids: List[str] = []
        for q in (p - 1, p, p + 1):
            if q in by_pos:
                pids.append(by_pos[q])
        parents[by_pos[p]] = pids

    init_state: Dict[str, CxO] = {nid: _vacuum_seed() for nid in node_ids}
    init_state[by_pos[left_pos]] = _electron_seed()
    init_state[by_pos[right_pos]] = _apply_phase_offset(_electron_seed(), phase_offset)

    world = World(
        node_ids=node_ids,
        parents=parents,
        states=init_state,
        tick=0,
    )
    return world, positions, left_pos, right_pos


def _overlap_positions(positions: List[int], left_pos: int, right_pos: int, tick: int) -> List[int]:
    out: List[int] = []
    for p in positions:
        if abs(p - left_pos) <= tick and abs(p - right_pos) <= tick:
            out.append(p)
    return out


def _make_case_grid() -> List[CaseConfig]:
    distances = [4, 6, 8, 10, 12]
    phase_offsets = [0, 1, 2, 3]
    out: List[CaseConfig] = []
    idx = 0
    for d in distances:
        for p in phase_offsets:
            steps = d + 8 + 2 * p
            out.append(
                CaseConfig(
                    case_id=f"alpha_case_{idx:02d}",
                    edge_distance=d,
                    steps=steps,
                    phase_offset=p,
                )
            )
            idx += 1
    if len(out) != 20:
        raise ValueError(f"expected 20 cases, got {len(out)}")
    return out


def _simulate_case(cfg: CaseConfig) -> Dict[str, object]:
    world, positions, left_pos, right_pos = _build_world(
        edge_distance=cfg.edge_distance,
        steps=cfg.steps,
        phase_offset=cfg.phase_offset,
    )
    pos_to_node = {p: _node_name(p) for p in positions}
    overlap_start_tick = (cfg.edge_distance + 1) // 2

    step_rows: List[Dict[str, object]] = []
    prev_buckets: Dict[int, int] = {}
    for p in positions:
        z = world.states[pos_to_node[p]][7]
        prev_buckets[p] = _phase_bucket_8(z)

    post_overlap_rates: List[float] = []
    for t in range(1, cfg.steps + 1):
        world = step(world)

        overlap = _overlap_positions(positions, left_pos, right_pos, t)
        phase_jumps: List[int] = []
        for p in overlap:
            cur_bucket = _phase_bucket_8(world.states[pos_to_node[p]][7])
            jump = _phase_jump_mod8(prev_buckets[p], cur_bucket)
            phase_jumps.append(jump)
            prev_buckets[p] = cur_bucket

        for p in positions:
            if p not in overlap:
                prev_buckets[p] = _phase_bucket_8(world.states[pos_to_node[p]][7])

        if overlap:
            coupling_rate = float(sum(phase_jumps)) / float(len(overlap) * 8)
        else:
            coupling_rate = 0.0

        in_overlap_window = t >= overlap_start_tick
        if in_overlap_window:
            post_overlap_rates.append(coupling_rate)

        step_rows.append(
            {
                "tick": t,
                "overlap_started": in_overlap_window,
                "overlap_node_count": len(overlap),
                "phase_jump_sum": int(sum(phase_jumps)),
                "photon_coupling_rate": coupling_rate,
            }
        )

    mean_post = sum(post_overlap_rates) / len(post_overlap_rates) if post_overlap_rates else 0.0
    max_post = max(post_overlap_rates) if post_overlap_rates else 0.0

    return {
        "case_id": cfg.case_id,
        "edge_distance": cfg.edge_distance,
        "steps": cfg.steps,
        "phase_offset": cfg.phase_offset,
        "overlap_start_tick": overlap_start_tick,
        "summary": {
            "mean_coupling_rate_post_overlap": mean_post,
            "max_coupling_rate_post_overlap": max_post,
        },
        "step_rows": step_rows,
    }


def run_cases() -> Dict[str, object]:
    cases = _make_case_grid()
    payload_cases = [_simulate_case(cfg) for cfg in cases]
    return {
        "schema_version": "fine_structure_20_cases_v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "kernel": "world_code/Python_code/minimal_world_kernel.py",
        "definition": {
            "signal": "photon_coupling_rate = mean phase-jump(e7 channel) over overlap nodes / 8",
            "overlap_rule": "lightcone overlap when abs(x-left)<=t and abs(x-right)<=t",
            "phase_offset_rule": "right electron receives P temporal commits before tick 0",
        },
        "case_count": len(payload_cases),
        "cases": payload_cases,
    }


def write_outputs(payload: Dict[str, object], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "fine_structure_20_cases.json"
    csv_path = out_dir / "fine_structure_20_cases.csv"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    fieldnames = [
        "case_id",
        "edge_distance",
        "steps",
        "phase_offset",
        "overlap_start_tick",
        "tick",
        "overlap_started",
        "overlap_node_count",
        "phase_jump_sum",
        "photon_coupling_rate",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for case in payload["cases"]:
            case_obj = case
            for row in case_obj["step_rows"]:
                w.writerow(
                    {
                        "case_id": case_obj["case_id"],
                        "edge_distance": case_obj["edge_distance"],
                        "steps": case_obj["steps"],
                        "phase_offset": case_obj["phase_offset"],
                        "overlap_start_tick": case_obj["overlap_start_tick"],
                        "tick": row["tick"],
                        "overlap_started": row["overlap_started"],
                        "overlap_node_count": row["overlap_node_count"],
                        "phase_jump_sum": row["phase_jump_sum"],
                        "photon_coupling_rate": row["photon_coupling_rate"],
                    }
                )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 20 fine-structure COG test cases in world_code.")
    parser.add_argument(
        "--output-dir",
        default=str(RESULTS_ROOT),
        help="Output directory for JSON/CSV artifacts.",
    )
    args = parser.parse_args()

    # Long-running line (uncomment on your local machine when ready):
    payload = run_cases()
    raise SystemExit(
        "Execution is disabled by default to avoid long runs here. "
        "Uncomment `payload = run_cases()` in main() to run locally."
    )
    write_outputs(payload, Path(args.output_dir))
    print(f"Generated {payload['case_count']} cases")
    print(f"Wrote {Path(args.output_dir) / 'fine_structure_20_cases.json'}")
    print(f"Wrote {Path(args.output_dir) / 'fine_structure_20_cases.csv'}")


if __name__ == "__main__":
    main()

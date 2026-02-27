"""Run a standardized world_code simulation campaign over many lightcone examples.

This script is designed for autonomous-worker execution with deterministic outputs.
It saves:
1) per-example per-step evolved states,
2) per-example metric summaries,
3) one campaign manifest.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

from minimal_world_kernel import World, load_world, run, save_world


EXAMPLES_DIR = Path("world_code/Python_code/lightcone_microstate_examples")
RESULTS_DIR = Path("world_code/Python_code/results")


@dataclass(frozen=True)
class CampaignConfig:
    campaign_id: str
    examples: List[str]
    steps: List[int]
    notes: str = ""


def _load_config(path: Path) -> CampaignConfig:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return CampaignConfig(
        campaign_id=str(raw["campaign_id"]),
        examples=[str(x) for x in raw["examples"]],
        steps=[int(x) for x in raw["steps"]],
        notes=str(raw.get("notes", "")),
    )


def _depths(world: World) -> Dict[str, int]:
    memo: Dict[str, int] = {}

    def depth_of(nid: str) -> int:
        if nid in memo:
            return memo[nid]
        parents = world.parents.get(nid, [])
        if not parents:
            memo[nid] = 0
            return 0
        d = 1 + max(depth_of(pid) for pid in parents)
        memo[nid] = d
        return d

    for nid in world.node_ids:
        depth_of(nid)
    return memo


def _basis_l1_totals(world: World) -> List[int]:
    totals = [0 for _ in range(8)]
    for nid in world.node_ids:
        state = world.states[nid]
        for i, z in enumerate(state):
            totals[i] += abs(z.re) + abs(z.im)
    return totals


def _metrics(world: World) -> Dict[str, Any]:
    depths = _depths(world)
    depth_hist: Dict[str, int] = {}
    for d in depths.values():
        k = str(d)
        depth_hist[k] = depth_hist.get(k, 0) + 1

    basis = _basis_l1_totals(world)
    active_coeff = 0
    for nid in world.node_ids:
        state = world.states[nid]
        active_coeff += sum(1 for z in state if (z.re != 0 or z.im != 0))

    out: Dict[str, Any] = {
        "tick": world.tick,
        "node_count": len(world.node_ids),
        "edge_count": sum(len(world.parents.get(nid, [])) for nid in world.node_ids),
        "max_depth": max(depths.values()) if depths else 0,
        "depth_histogram": depth_hist,
        "active_coeff_count": active_coeff,
        "basis_l1_totals": basis,
        "axis_weights": {
            "e0": basis[0],
            "e7": basis[7],
        },
    }
    out["axis_weights"]["e0_over_e7"] = None if basis[7] == 0 else (basis[0] / basis[7])
    return out


def _run_one_example(example_file: str, steps: List[int], out_dir: Path) -> Dict[str, Any]:
    in_path = EXAMPLES_DIR / example_file
    world0 = load_world(str(in_path))

    example_name = in_path.stem
    example_dir = out_dir / example_name
    example_dir.mkdir(parents=True, exist_ok=True)

    per_step: List[Dict[str, Any]] = []
    for s in steps:
        world_s = run(world0, s)
        out_state = example_dir / f"step_{s:04d}.json"
        save_world(str(out_state), world_s)
        per_step.append(
            {
                "steps": s,
                "state_file": out_state.as_posix(),
                "metrics": _metrics(world_s),
            }
        )

    summary = {
        "example_file": example_file,
        "example_name": example_name,
        "input_file": in_path.as_posix(),
        "runs": per_step,
    }
    (example_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_campaign(config: CampaignConfig) -> Dict[str, Any]:
    out_dir = RESULTS_DIR / config.campaign_id
    out_dir.mkdir(parents=True, exist_ok=True)

    summaries: List[Dict[str, Any]] = []
    for ex in config.examples:
        summaries.append(_run_one_example(ex, config.steps, out_dir))

    manifest = {
        "campaign_id": config.campaign_id,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "config": asdict(config),
        "examples_dir": EXAMPLES_DIR.as_posix(),
        "results_dir": out_dir.as_posix(),
        "example_count": len(summaries),
        "summaries": [s["example_name"] for s in summaries],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out_dir / "campaign_summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a world_code simulation campaign.")
    parser.add_argument(
        "--config",
        default="world_code/Python_code/campaign_configs/baseline_scan.json",
        help="Path to campaign config JSON.",
    )
    args = parser.parse_args()

    cfg = _load_config(Path(args.config))
    if not cfg.examples:
        raise ValueError("Campaign config must include at least one example.")
    if not cfg.steps:
        raise ValueError("Campaign config must include at least one step count.")
    if any(s < 0 for s in cfg.steps):
        raise ValueError("Step counts must be >= 0.")

    manifest = run_campaign(cfg)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()


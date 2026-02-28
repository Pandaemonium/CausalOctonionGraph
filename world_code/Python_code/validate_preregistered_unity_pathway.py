"""Front-to-back validation runner for preregistered unity CxO pathway.

Checks:
1) schema + eval plan load,
2) deterministic replay (two runs, identical output hash),
3) unity coefficient closure in final state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, List

from minimal_world_kernel_preregistered_unity import (
    GInt,
    World,
    load_world,
    run,
    save_world,
)


UNITY_TUPLES = {(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)}


def _state_payload(world: World) -> Dict[str, List[List[int]]]:
    out: Dict[str, List[List[int]]] = {}
    for nid in sorted(world.node_ids):
        out[nid] = [[z.re, z.im] for z in world.states[nid]]
    return out


def _hash_world_state(world: World) -> str:
    payload = {
        "tick": world.tick,
        "state": _state_payload(world),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _all_coeffs_in_unity_set(world: World) -> bool:
    for nid in world.node_ids:
        for z in world.states[nid]:
            pair = (int(z.re), int(z.im))
            if pair not in UNITY_TUPLES:
                return False
    return True


def validate_pathway(input_path: Path, steps: int, output_path: Path, report_path: Path) -> None:
    world0 = load_world(str(input_path))
    world_a = run(world0, steps)

    # Replay check from same initial artifact.
    world0_replay = load_world(str(input_path))
    world_b = run(world0_replay, steps)

    hash_a = _hash_world_state(world_a)
    hash_b = _hash_world_state(world_b)
    replay_equal = hash_a == hash_b
    unity_closed = _all_coeffs_in_unity_set(world_a)

    save_world(str(output_path), world_a)
    report = {
        "schema_version": "preregistered_unity_validation_v1",
        "input": str(input_path),
        "steps": steps,
        "output": str(output_path),
        "state_hash_a": hash_a,
        "state_hash_b": hash_b,
        "replay_equal": replay_equal,
        "unity_closed": unity_closed,
        "passed": bool(replay_equal and unity_closed),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if not report["passed"]:
        raise SystemExit(
            "Validation failed: "
            f"replay_equal={replay_equal}, unity_closed={unity_closed}. "
            f"See {report_path}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate preregistered unity CxO pathway.")
    parser.add_argument(
        "--input",
        default="world_code/Python_code/lightcone_example_preregistered_unity.json",
        help="Path to preregistered unity input JSON.",
    )
    parser.add_argument("--steps", type=int, default=4, help="Ticks to run.")
    parser.add_argument(
        "--output",
        default="world_code/Python_code/results/preregistered_unity/out.json",
        help="Path to write final state JSON.",
    )
    parser.add_argument(
        "--report",
        default="world_code/Python_code/results/preregistered_unity/validation_report.json",
        help="Path to write validation report JSON.",
    )
    args = parser.parse_args()

    if args.steps < 0:
        raise ValueError("--steps must be >= 0")

    output_path = Path(args.output)
    report_path = Path(args.report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    validate_pathway(
        input_path=Path(args.input),
        steps=args.steps,
        output_path=output_path,
        report_path=report_path,
    )
    print("Validation passed.")
    print(f"Wrote {output_path}")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()


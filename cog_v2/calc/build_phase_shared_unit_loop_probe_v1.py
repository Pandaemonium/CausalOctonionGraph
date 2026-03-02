"""Probe for phase-shared closed multiplicative loop kernel (v1)."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.python import kernel_phase_shared_unit_loop_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "phase_shared_unit_loop_probe_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "phase_shared_unit_loop_probe_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_phase_shared_unit_loop_probe_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_phase_shared_unit_loop_v1.py"

NODE_IDS: Tuple[str, ...] = ("l0", "l1", "q0", "q1", "mix0", "mix1", "obs")
PARENTS: Dict[str, List[str]] = {
    "l0": [],
    "l1": [],
    "q0": [],
    "q1": [],
    "mix0": ["l0", "q0"],
    "mix1": ["l1", "q1", "mix0"],
    "obs": ["mix0", "mix1", "q1"],
}


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _world_signature(world: k.World) -> Tuple[int, ...]:
    return tuple(int(world.states[nid]) for nid in sorted(world.node_ids))


def _detect_period(signatures: Sequence[Tuple[int, ...]], max_period: int) -> int | None:
    n = len(signatures)
    if n < 4:
        return None
    tail_start = max(0, n // 2)
    for p in range(1, int(max_period) + 1):
        ok = True
        for t in range(tail_start, n - p):
            if signatures[t] != signatures[t + p]:
                ok = False
                break
        if ok:
            return int(p)
    return None


def _closure_checks() -> Dict[str, Any]:
    bad: List[Dict[str, Any]] = []
    for a in range(k.ALPHABET_SIZE):
        for b in range(k.ALPHABET_SIZE):
            c = k.multiply(a, b)
            if not (0 <= int(c) < k.ALPHABET_SIZE):
                bad.append({"a": int(a), "b": int(b), "c": int(c)})
    return {
        "pair_count": int(k.ALPHABET_SIZE * k.ALPHABET_SIZE),
        "closed_under_multiplication": bool(len(bad) == 0),
        "counterexample_count": int(len(bad)),
        "counterexamples": bad[:8],
    }


def _initial_world() -> k.World:
    # Deterministic nontrivial seed using mixed phases and channels.
    s = {
        "l0": 2 * 8 + 1,    # +i * e001
        "l1": 3 * 8 + 2,    # -i * e010
        "q0": 0 * 8 + 3,    # +1 * e011
        "q1": 0 * 8 + 7,    # +1 * e111
        "mix0": 0 * 8 + 0,  # +1 * e000
        "mix1": 0 * 8 + 0,  # +1 * e000
        "obs": 0 * 8 + 0,   # +1 * e000
    }
    return k.World(
        node_ids=list(NODE_IDS),
        parents={nid: list(PARENTS[nid]) for nid in NODE_IDS},
        states=s,
        event_order=None,
        tick=0,
    )


def build_payload(ticks: int = 128, thin_output_step: int = 1) -> Dict[str, Any]:
    if int(ticks) < 8:
        raise ValueError("ticks must be >= 8")
    thin = max(1, int(thin_output_step))

    closure = _closure_checks()
    world = _initial_world()
    rows: List[Dict[str, Any]] = []
    signatures: List[Tuple[int, ...]] = []

    for _ in range(int(ticks) + 1):
        signatures.append(_world_signature(world))
        if (world.tick % thin == 0) or (world.tick == int(ticks)):
            rows.append(
                {
                    "tick": int(world.tick),
                    "states": {nid: int(world.states[nid]) for nid in sorted(world.node_ids)},
                    "labels": {nid: k.label(int(world.states[nid])) for nid in sorted(world.node_ids)},
                }
            )
        if world.tick < int(ticks):
            world = k.step(world)

    period = _detect_period(signatures, max_period=64)
    checks = {
        "closure_pair_scan_ok": bool(closure["closed_under_multiplication"]),
        "all_states_always_in_alphabet": bool(
            all(0 <= v < k.ALPHABET_SIZE for sig in signatures for v in sig)
        ),
        "deterministic_period_detected": bool(period is not None),
    }

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "phase_shared_unit_loop_probe_v1",
        "claim_id": "KERNEL-PHASE-SHARED-UNIT-LOOP-001",
        "mode": "exploratory_multiplication_only",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "params": {
            "ticks": int(ticks),
            "thin_output_step": int(thin),
            "alphabet_size": int(k.ALPHABET_SIZE),
            "phase_labels": list(k.PHASE_LABELS),
            "basis_labels": list(k.BASIS_LABELS),
        },
        "closure_checks": closure,
        "world_trace": rows,
        "period_detected": None if period is None else int(period),
        "checks": checks,
        "notes": [
            "Runtime update uses multiplication only.",
            "No additive fold or projector snapping in this lane.",
            "Local state alphabet is finite (32 nonzero symbols).",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    c = payload["closure_checks"]
    lines = [
        "# Phase-Shared Unit Loop Probe (v1)",
        "",
        "## Scope",
        "",
        "- Finite phase-shared alphabet over octonion basis units",
        "- Strictly multiplication-only runtime update",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- thin_output_step: `{p['thin_output_step']}`",
        f"- alphabet_size: `{p['alphabet_size']}`",
        "",
        "## Closure",
        "",
        f"- pair_count: `{c['pair_count']}`",
        f"- closed_under_multiplication: `{c['closed_under_multiplication']}`",
        f"- counterexample_count: `{c['counterexample_count']}`",
        "",
        "## Dynamics",
        "",
        f"- period_detected: `{payload['period_detected']}`",
        "",
        "## Checks",
        "",
    ]
    for kx, vx in payload["checks"].items():
        lines.append(f"- {kx}: `{vx}`")
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
    parser.add_argument("--ticks", type=int, default=128)
    parser.add_argument("--thin-output-step", type=int, default=1)
    args = parser.parse_args()

    payload = build_payload(ticks=int(args.ticks), thin_output_step=int(args.thin_output_step))
    write_artifacts(payload)
    print(
        "phase_shared_unit_loop_probe_v1: "
        f"closure_ok={payload['checks']['closure_pair_scan_ok']}, "
        f"period={payload['period_detected']}, "
        f"alphabet_ok={payload['checks']['all_states_always_in_alphabet']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


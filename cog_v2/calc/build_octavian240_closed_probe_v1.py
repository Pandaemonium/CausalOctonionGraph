"""Probe for closed Octavian-240 alphabet over cyclic octonion multiplication."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.python import kernel_octavian240_closed_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "octavian240_closed_probe_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "octavian240_closed_probe_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_octavian240_closed_probe_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_octavian240_closed_v1.py"

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


def _closure_checks(limit_rows: int = 8) -> Dict[str, Any]:
    bad: List[Dict[str, Any]] = []
    for a in range(k.ALPHABET_SIZE):
        for b in range(k.ALPHABET_SIZE):
            try:
                _ = k.multiply_ids(int(a), int(b))
            except ValueError:
                if len(bad) < int(limit_rows):
                    bad.append({"a": int(a), "b": int(b)})
    return {
        "pair_count": int(k.ALPHABET_SIZE * k.ALPHABET_SIZE),
        "closed_under_multiplication": bool(len(bad) == 0),
        "counterexample_count": int(len(bad)),
        "counterexamples": bad,
    }


def _norm_checks(limit_rows: int = 8) -> Dict[str, Any]:
    bad: List[Dict[str, Any]] = []
    for idx, x in enumerate(k.ALPHABET):
        ns = k.oct_norm_scalar(x)
        rz = k.oct_norm_residual_zero(x)
        if not (ns == 1 and rz):
            if len(bad) < int(limit_rows):
                bad.append(
                    {
                        "id": int(idx),
                        "label": k.elem_label(int(idx)),
                        "norm_scalar": str(ns),
                        "norm_residual_zero": bool(rz),
                    }
                )
    return {
        "alphabet_size": int(k.ALPHABET_SIZE),
        "all_norm_one": bool(len(bad) == 0),
        "counterexample_count": int(len(bad)),
        "counterexamples": bad,
    }


def _first_non_identity_ids(count: int) -> List[int]:
    out: List[int] = []
    for i in range(k.ALPHABET_SIZE):
        if i == k.IDENTITY_ID:
            continue
        out.append(int(i))
        if len(out) == int(count):
            break
    return out


def _simulate_trace(ticks: int, thin_output_step: int) -> Dict[str, Any]:
    seed_ids = _first_non_identity_ids(4)
    world = k.World(
        node_ids=list(NODE_IDS),
        parents={nid: list(PARENTS[nid]) for nid in NODE_IDS},
        states={
            "l0": seed_ids[0],
            "l1": seed_ids[1],
            "q0": seed_ids[2],
            "q1": seed_ids[3],
            "mix0": int(k.IDENTITY_ID),
            "mix1": int(k.IDENTITY_ID),
            "obs": int(k.IDENTITY_ID),
        },
        event_order=None,
        tick=0,
    )

    thin = max(1, int(thin_output_step))
    rows: List[Dict[str, Any]] = []

    for _ in range(int(ticks) + 1):
        if (world.tick % thin == 0) or (world.tick == int(ticks)):
            rows.append(
                {
                    "tick": int(world.tick),
                    "states": {nid: int(world.states[nid]) for nid in sorted(world.node_ids)},
                    "labels": {nid: k.elem_label(int(world.states[nid])) for nid in sorted(world.node_ids)},
                }
            )
        if world.tick < int(ticks):
            world = k.step(world)

    return {
        "requested_ticks": int(ticks),
        "completed_tick": int(world.tick),
        "trace": rows,
    }


def build_payload(ticks: int = 96, thin_output_step: int = 3) -> Dict[str, Any]:
    if int(ticks) < 8:
        raise ValueError("ticks must be >= 8")
    thin = max(1, int(thin_output_step))

    closure = _closure_checks()
    norms = _norm_checks()
    scenario = _simulate_trace(ticks=int(ticks), thin_output_step=thin)

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "octavian240_closed_probe_v1",
        "claim_id": "KERNEL-OCTAVIAN240-CLOSED-001",
        "mode": "multiplication_only",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "params": {
            "ticks": int(ticks),
            "thin_output_step": int(thin),
            "alphabet_size": int(k.ALPHABET_SIZE),
            "identity_id": int(k.IDENTITY_ID),
            "basis_labels": list(k.BASIS_LABELS),
            "cyclic_oriented_triples": [list(t) for t in k.CYCLIC_ORIENTED_TRIPLES],
        },
        "alphabet_norm_checks": norms,
        "closure_checks": closure,
        "scenario": scenario,
        "checks": {
            "alphabet_size_240": bool(k.ALPHABET_SIZE == 240),
            "alphabet_norm_one_all": bool(norms["all_norm_one"]),
            "closure_pair_scan_ok": bool(closure["closed_under_multiplication"]),
        },
        "notes": [
            "Closed alphabet is built from norm-1 points in an Octavian integer lattice.",
            "Update rule is multiplication-only, no additive fold and no projection snapping.",
            "Cyclic Fano orientation is used for valid octonion composition behavior.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    c = payload["closure_checks"]
    n = payload["alphabet_norm_checks"]
    lines = [
        "# Octavian-240 Closed Probe (v1)",
        "",
        "## Scope",
        "",
        "- Closed 240-state alphabet",
        "- Cyclic octonion multiplication",
        "- Multiplication-only runtime update",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- thin_output_step: `{p['thin_output_step']}`",
        f"- alphabet_size: `{p['alphabet_size']}`",
        f"- identity_id: `{p['identity_id']}`",
        "",
        "## Norm",
        "",
        f"- all_norm_one: `{n['all_norm_one']}`",
        f"- counterexample_count: `{n['counterexample_count']}`",
        "",
        "## Closure",
        "",
        f"- pair_count: `{c['pair_count']}`",
        f"- closed_under_multiplication: `{c['closed_under_multiplication']}`",
        f"- counterexample_count: `{c['counterexample_count']}`",
        "",
        "## Scenario",
        "",
        f"- completed_tick: `{payload['scenario']['completed_tick']}`",
        "",
    ]
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
    parser.add_argument("--ticks", type=int, default=96)
    parser.add_argument("--thin-output-step", type=int, default=3)
    args = parser.parse_args()

    payload = build_payload(ticks=int(args.ticks), thin_output_step=int(args.thin_output_step))
    write_artifacts(payload)
    print(
        "octavian240_closed_probe_v1: "
        f"norm_ok={payload['checks']['alphabet_norm_one_all']}, "
        f"closure_ok={payload['checks']['closure_pair_scan_ok']}, "
        f"counterexamples={payload['closure_checks']['counterexample_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


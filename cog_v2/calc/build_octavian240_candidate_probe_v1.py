"""Probe for full Octavian-240 candidate alphabet (canonical XOR/Fano product)."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.python import kernel_octavian240_candidate_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "octavian240_candidate_probe_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "octavian240_candidate_probe_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_octavian240_candidate_probe_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_octavian240_candidate_v1.py"

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


def _fraction_str(x: Fraction) -> str:
    return str(x)


def _oct_str(x: k.Oct) -> List[str]:
    return [_fraction_str(c) for c in x]


def _basis_id(i: int, sign: int = 1) -> int:
    v = [Fraction(0, 1) for _ in range(8)]
    v[int(i)] = Fraction(int(sign), 1)
    return int(k.ALPHABET_INDEX[tuple(v)])  # type: ignore[index]


def _closure_checks(limit_rows: int = 16) -> Dict[str, Any]:
    bad: List[Dict[str, Any]] = []
    for a in range(k.ALPHABET_SIZE):
        for b in range(k.ALPHABET_SIZE):
            prod = k.oct_mul(k.ALPHABET[a], k.ALPHABET[b])
            out = k.ALPHABET_INDEX.get(prod)
            if out is None and len(bad) < int(limit_rows):
                bad.append(
                    {
                        "a": int(a),
                        "b": int(b),
                        "a_label": k.elem_label(int(a)),
                        "b_label": k.elem_label(int(b)),
                        "product_coeffs": _oct_str(prod),
                        "product_norm_scalar": _fraction_str(k.oct_norm_scalar(prod)),
                        "product_norm_residual_zero": bool(k.oct_norm_residual_zero(prod)),
                    }
                )
    counterexample_count = 0
    for a in range(k.ALPHABET_SIZE):
        for b in range(k.ALPHABET_SIZE):
            if k.multiply_ids(int(a), int(b)) is None:
                counterexample_count += 1
    return {
        "pair_count": int(k.ALPHABET_SIZE * k.ALPHABET_SIZE),
        "closed_under_multiplication": bool(counterexample_count == 0),
        "counterexample_count": int(counterexample_count),
        "counterexamples": bad,
    }


def _alphabet_norm_checks(limit_rows: int = 12) -> Dict[str, Any]:
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
                        "norm_scalar": _fraction_str(ns),
                        "norm_residual_zero": bool(rz),
                    }
                )
    return {
        "alphabet_size": int(k.ALPHABET_SIZE),
        "all_norm_one": bool(len(bad) == 0),
        "counterexample_count": int(len(bad)),
        "counterexamples": bad,
    }


def _simulate_trace(seed: Dict[str, int], ticks: int, thin_output_step: int) -> Dict[str, Any]:
    world = k.World(
        node_ids=list(NODE_IDS),
        parents={nid: list(PARENTS[nid]) for nid in NODE_IDS},
        states={nid: int(seed[nid]) for nid in NODE_IDS},
        event_order=None,
        tick=0,
    )
    rows: List[Dict[str, Any]] = []
    thin = max(1, int(thin_output_step))
    failure_tick: int | None = None

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
            nxt = k.step(world, strict=False)
            if nxt is None:
                failure_tick = int(world.tick + 1)
                break
            world = nxt

    return {
        "requested_ticks": int(ticks),
        "completed_tick": int(world.tick),
        "failure_tick": failure_tick,
        "trace": rows,
    }


def build_payload(ticks: int = 64, thin_output_step: int = 1) -> Dict[str, Any]:
    if int(ticks) < 4:
        raise ValueError("ticks must be >= 4")
    thin = max(1, int(thin_output_step))

    closure = _closure_checks()
    norms = _alphabet_norm_checks()

    seed_monomial = {
        "l0": _basis_id(1, +1),
        "l1": _basis_id(2, -1),
        "q0": _basis_id(4, +1),
        "q1": _basis_id(7, -1),
        "mix0": _basis_id(0, +1),
        "mix1": _basis_id(0, +1),
        "obs": _basis_id(0, +1),
    }
    seed_halfsum = {
        "l0": 16,
        "l1": 17,
        "q0": 128,
        "q1": 129,
        "mix0": _basis_id(0, +1),
        "mix1": _basis_id(0, +1),
        "obs": _basis_id(0, +1),
    }

    scenarios = {
        "monomial_seed": _simulate_trace(seed_monomial, ticks=int(ticks), thin_output_step=thin),
        "halfsum_seed": _simulate_trace(seed_halfsum, ticks=int(ticks), thin_output_step=thin),
    }

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH

    checks = {
        "alphabet_size_240": bool(k.ALPHABET_SIZE == 240),
        "alphabet_norm_one_all": bool(norms["all_norm_one"]),
        "closure_pair_scan_ok": bool(closure["closed_under_multiplication"]),
    }

    payload: Dict[str, Any] = {
        "schema_version": "octavian240_candidate_probe_v1",
        "claim_id": "KERNEL-OCTAVIAN240-CANDIDATE-001",
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
            "basis_labels": list(k.BASIS_LABELS),
            "xor_triples": [list(t) for t in k.XOR_ORIENTED_TRIPLES],
        },
        "alphabet_norm_checks": norms,
        "closure_checks": closure,
        "scenarios": scenarios,
        "checks": checks,
        "notes": [
            "This uses the full 240-state candidate alphabet under canonical XOR/Fano multiplication.",
            "Runtime update is multiplication-only (no additive fold and no projection snap).",
            "Any closure failure is reported directly rather than hidden by projection.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    c = payload["closure_checks"]
    n = payload["alphabet_norm_checks"]
    lines = [
        "# Octavian-240 Candidate Probe (v1)",
        "",
        "## Scope",
        "",
        "- Full 240-state candidate alphabet",
        "- Canonical XOR/Fano octonion multiplication",
        "- Multiplication-only runtime update",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- thin_output_step: `{p['thin_output_step']}`",
        f"- alphabet_size: `{p['alphabet_size']}`",
        "",
        "## Alphabet Norm",
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
        "## Scenario Summary",
        "",
    ]
    for name, run in payload["scenarios"].items():
        lines.append(
            f"- {name}: completed_tick=`{run['completed_tick']}`, failure_tick=`{run['failure_tick']}`"
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
    parser.add_argument("--ticks", type=int, default=64)
    parser.add_argument("--thin-output-step", type=int, default=1)
    args = parser.parse_args()

    payload = build_payload(ticks=int(args.ticks), thin_output_step=int(args.thin_output_step))
    write_artifacts(payload)
    print(
        "octavian240_candidate_probe_v1: "
        f"norm_ok={payload['checks']['alphabet_norm_one_all']}, "
        f"closure_ok={payload['checks']['closure_pair_scan_ok']}, "
        f"counterexamples={payload['closure_checks']['counterexample_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


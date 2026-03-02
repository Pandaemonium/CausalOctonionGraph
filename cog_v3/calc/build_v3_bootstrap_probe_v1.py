"""Bootstrap probe for COG v3 Octavian-240 multiplicative kernel."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_bootstrap_probe_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_bootstrap_probe_v1.md"
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_bootstrap_probe_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"

NODE_IDS: Tuple[str, ...] = ("a0", "a1", "b0", "b1", "mix0", "mix1", "obs")
PARENTS: Dict[str, List[str]] = {
    "a0": [],
    "a1": [],
    "b0": [],
    "b1": [],
    "mix0": ["a0", "b0"],
    "mix1": ["a1", "b1", "mix0"],
    "obs": ["mix0", "mix1", "b1"],
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


def _triplet_checks() -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    all_ok = True
    for i, j, t in k.TARGET_POSITIVE_TRIPLETS:
        s = k.basis_triplet_sign(int(i), int(j), int(t))
        ok = bool(s == 1)
        all_ok = all_ok and ok
        rows.append(
            {
                "lhs": [int(i), int(j)],
                "rhs": int(t),
                "sign": int(s),
                "ok": ok,
            }
        )
    # User-requested triplet set included an algebraically inconsistent first item.
    # We record that explicitly to avoid silent convention mixing.
    impossible_request = {"lhs": [6, 7], "rhs": 3}  # e110*e111 = +e011 request
    try:
        s_bad = k.basis_triplet_sign(6, 7, 3)
        impossible_ok = bool(s_bad == 1)
    except ValueError:
        impossible_ok = False
        s_bad = None
    return {
        "target_triplets_all_positive": bool(all_ok),
        "target_triplets": rows,
        "inconsistent_requested_triplet": {
            **impossible_request,
            "sign_if_forced": s_bad,
            "satisfiable": bool(impossible_ok),
            "note": "No valid octonion basis convention can satisfy this with other unit constraints.",
        },
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
            "a0": seed_ids[0],
            "a1": seed_ids[1],
            "b0": seed_ids[2],
            "b1": seed_ids[3],
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
    triplets = _triplet_checks()
    scenario = _simulate_trace(ticks=int(ticks), thin_output_step=thin)

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "v3_bootstrap_probe_v1",
        "claim_id": "COG-V3-BOOTSTRAP-001",
        "mode": "multiplication_only",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "params": {
            "ticks": int(ticks),
            "thin_output_step": int(thin),
            "alphabet_size": int(k.ALPHABET_SIZE),
            "identity_id": int(k.IDENTITY_ID),
            "basis_labels": list(k.BASIS_LABELS),
            "new_to_old_permutation": list(k.NEW_TO_OLD),
            "sign_vector": list(k.SIGN),
        },
        "alphabet_norm_checks": norms,
        "closure_checks": closure,
        "triplet_checks": triplets,
        "scenario": scenario,
        "checks": {
            "alphabet_size_240": bool(k.ALPHABET_SIZE == 240),
            "alphabet_norm_one_all": bool(norms["all_norm_one"]),
            "closure_pair_scan_ok": bool(closure["closed_under_multiplication"]),
            "target_triplets_all_positive": bool(triplets["target_triplets_all_positive"]),
        },
        "notes": [
            "COG v3 bootstrap uses a basis-convention transform over the closed Octavian 240 lane.",
            "Update rule is strictly multiplicative.",
            "Requested inconsistent triplet is explicitly recorded and rejected.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    _assert_payload_contract(payload)
    return payload


def _assert_payload_contract(payload: Dict[str, Any]) -> None:
    if payload.get("kernel_profile") != k.KERNEL_PROFILE:
        raise ValueError("Payload missing/invalid kernel_profile.")
    if payload.get("convention_id") != k.CONVENTION_ID:
        raise ValueError("Payload missing/invalid convention_id.")
    if payload.get("mode") != "multiplication_only":
        raise ValueError("Payload mode must be multiplication_only.")


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    c = payload["closure_checks"]
    n = payload["alphabet_norm_checks"]
    t = payload["triplet_checks"]
    lines = [
        "# COG v3 Bootstrap Probe (v1)",
        "",
        "## Scope",
        "",
        "- Closed Octavian-240 basis",
        "- Multiplication-only update",
        "- v3 convention mapping recorded in payload",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- thin_output_step: `{p['thin_output_step']}`",
        f"- alphabet_size: `{p['alphabet_size']}`",
        f"- identity_id: `{p['identity_id']}`",
        "",
        "## Norm and Closure",
        "",
        f"- all_norm_one: `{n['all_norm_one']}`",
        f"- closed_under_multiplication: `{c['closed_under_multiplication']}`",
        f"- pair_count: `{c['pair_count']}`",
        "",
        "## Target Triplets",
        "",
        f"- all_target_triplets_positive: `{t['target_triplets_all_positive']}`",
        f"- inconsistent_requested_triplet_satisfiable: `{t['inconsistent_requested_triplet']['satisfiable']}`",
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
    _assert_payload_contract(payload)
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
        "v3_bootstrap_probe_v1: "
        f"norm_ok={payload['checks']['alphabet_norm_one_all']}, "
        f"closure_ok={payload['checks']['closure_pair_scan_ok']}, "
        f"triplets_ok={payload['checks']['target_triplets_all_positive']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

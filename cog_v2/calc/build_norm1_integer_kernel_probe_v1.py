"""Probe norm-1 integer CxO multiplicative kernel viability (v1).

This is an exploratory A/B lane for:
1) closure under multiplication on constructive norm-1 states,
2) norm preservation under world updates without projection,
3) short-horizon growth behavior (coefficient magnitude drift).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.python import kernel_norm1_integer_v1 as kn1


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "norm1_integer_kernel_probe_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "norm1_integer_kernel_probe_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_norm1_integer_kernel_probe_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_norm1_integer_v1.py"


@dataclass(frozen=True)
class ProbeParams:
    range_limit: int = 2
    family_sample_cap: int = 36
    ticks: int = 12
    thin_output_step: int = 1


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
PAIR_ORDER: Tuple[Tuple[int, int], ...] = ((1, 2), (1, 4), (2, 4), (3, 5), (3, 6), (5, 6))


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _serialize_g(z: kn1.GInt) -> List[int]:
    return [int(z.re), int(z.im)]


def _serialize_cxo(x: kn1.CxO) -> List[List[int]]:
    return [_serialize_g(z) for z in x]


def _norm1_family_state(m: int, n: int, i: int, j: int) -> kn1.CxO:
    # Constructive infinite family:
    # a = m + n i, b = n - m i, and a^2 + b^2 = 0 in Z[i].
    # State x = e0 + a*ei + b*ej then satisfies N(x)=1.
    a = kn1.GInt(int(m), int(n))
    b = kn1.GInt(int(n), int(-m))
    vals = [kn1.ZERO_G for _ in range(8)]
    vals[0] = kn1.ONE_G
    vals[int(i)] = a
    vals[int(j)] = b
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _build_family_states(p: ProbeParams) -> List[kn1.CxO]:
    out: List[kn1.CxO] = []
    for m in range(-int(p.range_limit), int(p.range_limit) + 1):
        for n in range(-int(p.range_limit), int(p.range_limit) + 1):
            if m == 0 and n == 0:
                continue
            for i, j in PAIR_ORDER:
                st = _norm1_family_state(m, n, i, j)
                if kn1.cxo_is_norm_one(st):
                    out.append(st)
                if len(out) >= int(p.family_sample_cap):
                    return out
    return out


def _world_signature(world: kn1.World) -> Tuple[Tuple[Tuple[int, int], ...], ...]:
    return tuple(tuple((z.re, z.im) for z in world.states[nid]) for nid in world.node_ids)


def _detect_period(signatures: Sequence[Tuple[Tuple[Tuple[int, int], ...], ...]], max_period: int) -> int | None:
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


def _closure_probe(states: Sequence[kn1.CxO]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    closure_ok = True
    max_coeff = 0
    fail_count = 0
    first_fail: Dict[str, Any] | None = None
    for ai, a in enumerate(states):
        for bi, b in enumerate(states):
            prod = kn1.cxo_mul(a, b)
            is_norm_one = bool(kn1.cxo_is_norm_one(prod))
            if not is_norm_one:
                closure_ok = False
                fail_count += 1
                if first_fail is None:
                    first_fail = {
                        "a_index": int(ai),
                        "b_index": int(bi),
                        "product_norm": _serialize_g(kn1.cxo_composition_norm(prod)),
                        "product_norm_residual_linf": int(kn1.cxo_norm_residual_linf(prod)),
                        "product_coeff_linf": int(kn1.cxo_max_coeff_linf(prod)),
                    }
            coeff_linf = int(kn1.cxo_max_coeff_linf(prod))
            max_coeff = max(max_coeff, coeff_linf)
            if ai < 3 and bi < 3:
                rows.append(
                    {
                        "a_index": int(ai),
                        "b_index": int(bi),
                        "product_is_norm_one": bool(is_norm_one),
                        "product_norm": _serialize_g(kn1.cxo_composition_norm(prod)),
                        "product_norm_residual_linf": int(kn1.cxo_norm_residual_linf(prod)),
                        "product_coeff_linf": int(coeff_linf),
                    }
                )
    return {
        "pair_count": int(len(states) * len(states)),
        "all_products_norm_one": bool(closure_ok),
        "failed_pair_count": int(fail_count),
        "first_counterexample": first_fail,
        "max_product_coeff_linf": int(max_coeff),
        "sample_rows": rows,
    }


def _build_probe_world(states: Sequence[kn1.CxO]) -> kn1.World:
    if len(states) < len(NODE_IDS):
        raise ValueError("Need at least as many states as nodes to initialize world probe.")
    init = {nid: states[i] for i, nid in enumerate(NODE_IDS)}
    return kn1.World(
        node_ids=list(NODE_IDS),
        parents={nid: list(PARENTS[nid]) for nid in NODE_IDS},
        states=init,
        event_order=None,
        tick=0,
    )


def _world_probe(states: Sequence[kn1.CxO], p: ProbeParams) -> Dict[str, Any]:
    world = _build_probe_world(states)
    thin = max(1, int(p.thin_output_step))
    rows: List[Dict[str, Any]] = []
    signatures: List[Tuple[Tuple[Tuple[int, int], ...], ...]] = []
    norm_all = True
    max_coeff_digits = 0
    max_norm_residual = 0

    for _ in range(int(p.ticks) + 1):
        signatures.append(_world_signature(world))
        node_norm_ok = all(kn1.cxo_is_norm_one(world.states[nid]) for nid in world.node_ids)
        norm_all = bool(norm_all and node_norm_ok)
        row_coeff = max(kn1.cxo_max_coeff_linf(world.states[nid]) for nid in world.node_ids)
        row_coeff_digits = len(str(abs(int(row_coeff))))
        row_residual = max(kn1.cxo_norm_residual_linf(world.states[nid]) for nid in world.node_ids)
        max_coeff_digits = max(max_coeff_digits, int(row_coeff_digits))
        max_norm_residual = max(max_norm_residual, int(row_residual))
        if (world.tick % thin == 0) or (world.tick == int(p.ticks)):
            rows.append(
                {
                    "tick": int(world.tick),
                    "all_nodes_norm_one": bool(node_norm_ok),
                    "max_coeff_linf_digits": int(row_coeff_digits),
                    "max_norm_residual_linf": int(row_residual),
                }
            )
        if world.tick < int(p.ticks):
            world = kn1.step(world)

    period = _detect_period(signatures, max_period=12)
    start_digits = int(rows[0]["max_coeff_linf_digits"]) if rows else 1
    growth_log10_est = int(max_coeff_digits - start_digits)
    return {
        "all_ticks_all_nodes_norm_one": bool(norm_all),
        "max_coeff_linf_digits_any_tick": int(max_coeff_digits),
        "max_norm_residual_linf_any_tick": int(max_norm_residual),
        "detected_period": None if period is None else int(period),
        "growth_log10_est_vs_tick0": int(growth_log10_est),
        "rows": rows,
    }


def _vacuum_probe(p: ProbeParams) -> Dict[str, Any]:
    vac = kn1.cxo_one()
    world = kn1.World(
        node_ids=list(NODE_IDS),
        parents={nid: list(PARENTS[nid]) for nid in NODE_IDS},
        states={nid: vac for nid in NODE_IDS},
        event_order=None,
        tick=0,
    )
    stable = True
    for _ in range(int(p.ticks)):
        world = kn1.step(world)
        stable = bool(stable and all(world.states[nid] == vac for nid in world.node_ids))
    return {"vacuum_fixed_point": bool(stable)}


def build_payload(params: ProbeParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else ProbeParams()
    if int(p.range_limit) < 1:
        raise ValueError("range_limit must be >= 1")
    if int(p.family_sample_cap) < 8:
        raise ValueError("family_sample_cap must be >= 8")
    if int(p.ticks) < 8:
        raise ValueError("ticks must be >= 8")

    states = _build_family_states(p)
    if len(states) < len(NODE_IDS):
        raise ValueError("Constructed family too small for world probe.")

    closure = _closure_probe(states)
    world = _world_probe(states, p)
    vacuum = _vacuum_probe(p)

    checks = {
        "family_states_constructed_norm_one": bool(all(kn1.cxo_is_norm_one(s) for s in states)),
        "closure_pair_products_norm_one": bool(closure["all_products_norm_one"]),
        "world_evolution_preserves_norm_one": bool(world["all_ticks_all_nodes_norm_one"]),
        "vacuum_fixed_point": bool(vacuum["vacuum_fixed_point"]),
    }

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "norm1_integer_kernel_probe_v1",
        "claim_id": "KERNEL-NORM1-INTEGER-EXPLORATION-001",
        "mode": "exploratory_parallel_kernel_lane",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": kn1.KERNEL_PROFILE,
        "params": {
            "range_limit": int(p.range_limit),
            "family_sample_cap": int(p.family_sample_cap),
            "ticks": int(p.ticks),
            "thin_output_step": int(max(1, int(p.thin_output_step))),
        },
        "family_summary": {
            "state_count": int(len(states)),
            "seed_examples": [_serialize_cxo(states[i]) for i in range(min(3, len(states)))],
        },
        "closure_probe": closure,
        "world_probe": world,
        "vacuum_probe": vacuum,
        "checks": checks,
        "notes": [
            "Norm definition is octonion composition norm N(x)=x*x_bar scalar component over Z[i].",
            "This lane uses multiplicative updates only: payload fold then left multiply onto current state.",
            "Coefficient growth is tracked because norm-one closure alone does not bound coefficient magnitudes.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    c = payload["closure_probe"]
    w = payload["world_probe"]
    lines = [
        "# Norm1 Integer Multiplicative Kernel Probe (v1)",
        "",
        "## Scope",
        "",
        "- Experimental lane: CxO over integers with multiplicative norm-one family",
        "- Update rule: pure multiplication, no projector snapping",
        "",
        "## Params",
        "",
        f"- range_limit: `{p['range_limit']}`",
        f"- family_sample_cap: `{p['family_sample_cap']}`",
        f"- ticks: `{p['ticks']}`",
        f"- thin_output_step: `{p['thin_output_step']}`",
        "",
        "## Summary",
        "",
        f"- family_state_count: `{payload['family_summary']['state_count']}`",
        f"- closure_pair_count: `{c['pair_count']}`",
        f"- closure_pair_products_norm_one: `{c['all_products_norm_one']}`",
        f"- closure_failed_pair_count: `{c['failed_pair_count']}`",
        f"- world_evolution_preserves_norm_one: `{w['all_ticks_all_nodes_norm_one']}`",
        f"- vacuum_fixed_point: `{payload['vacuum_probe']['vacuum_fixed_point']}`",
        f"- max_product_coeff_linf: `{c['max_product_coeff_linf']}`",
        f"- world_max_coeff_linf_digits_any_tick: `{w['max_coeff_linf_digits_any_tick']}`",
        f"- world_growth_log10_est_vs_tick0: `{w['growth_log10_est_vs_tick0']}`",
        f"- detected_period: `{w['detected_period']}`",
        "",
        "## Checks",
        "",
    ]
    for kx, vx in payload["checks"].items():
        lines.append(f"- {kx}: `{vx}`")
    lines.append("")
    return "\n".join(lines)


def render_failure_cases_md(
    failures_payload: Dict[str, Any],
) -> str:
    """Render failure cases in explicit 4-line block format.

    Format per case:
    [factor_a ...]
    [factor_b ...]
    [product ...]
    norm: ...
    """

    def _fmt_coeff(pair: Sequence[int]) -> str:
        re = int(pair[0])
        im = int(pair[1])
        if im == 0:
            return f"{re}"
        if re == 0:
            if im == 1:
                return "i"
            if im == -1:
                return "-i"
            return f"{im}i"
        sign = "+" if im > 0 else "-"
        imag_abs = abs(im)
        imag_part = "i" if imag_abs == 1 else f"{imag_abs}i"
        return f"{re}{sign}{imag_part}"

    def _fmt_state(state: Sequence[Sequence[int]]) -> str:
        return "[" + ", ".join(_fmt_coeff(pair) for pair in state) + "]"

    lines: List[str] = [
        "# Norm1 Integer Failure Cases (v1)",
        "",
        f"state_count: {int(failures_payload.get('state_count', 0))}",
        f"failure_count: {int(failures_payload.get('failure_count', 0))}",
        "",
    ]
    failures = failures_payload.get("failures", [])
    for row in failures:
        lines.append(_fmt_state(row["factor_a"]))
        lines.append(_fmt_state(row["factor_b"]))
        lines.append(_fmt_state(row["product"]))
        nr, ni = row["product_norm"]
        lines.append(
            f"norm: {int(nr)}{('+' if int(ni) >= 0 else '')}{int(ni)}i; "
            f"residual_linf={int(row['product_norm_residual_linf'])}; "
            f"max_coeff_linf={int(row['product_max_coeff_linf'])}; "
            f"indices=({int(row['a_index'])},{int(row['b_index'])})"
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
    parser.add_argument("--range-limit", type=int, default=ProbeParams.range_limit)
    parser.add_argument("--family-sample-cap", type=int, default=ProbeParams.family_sample_cap)
    parser.add_argument("--ticks", type=int, default=ProbeParams.ticks)
    parser.add_argument("--thin-output-step", type=int, default=ProbeParams.thin_output_step)
    args = parser.parse_args()

    payload = build_payload(
        ProbeParams(
            range_limit=int(args.range_limit),
            family_sample_cap=int(args.family_sample_cap),
            ticks=int(args.ticks),
            thin_output_step=int(args.thin_output_step),
        )
    )
    write_artifacts(payload)
    print(
        "norm1_integer_kernel_probe_v1: "
        f"closure_ok={payload['checks']['closure_pair_products_norm_one']}, "
        f"world_norm_ok={payload['checks']['world_evolution_preserves_norm_one']}, "
        f"growth_log10_est={payload['world_probe']['growth_log10_est_vs_tick0']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

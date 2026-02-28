"""Build black-hole/horizon contract witness under the v2 projective kernel."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Tuple

from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "blackhole_projection_contract_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "blackhole_projection_contract_v1.md"

SCRIPT_REPO_PATH = "cog_v2/calc/build_blackhole_projection_contract_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
RFC_REPO_PATH = "cog_v2/rfc/RFC-005_Black_Hole_Horizon_Projection_Kernel_Contract.md"

NODE_IDS: List[str] = [
    "o0",
    "o1",
    "o2",
    "h0",
    "h1",
    "c0",
    "c1",
]

PARENTS: Dict[str, List[str]] = {
    "o0": [],
    "o1": ["o0"],
    "o2": ["o1"],
    "h0": ["o1", "o2"],
    "h1": ["o2"],
    "c0": ["h0", "h1"],
    "c1": ["h0", "h1", "c0"],
}

BLACK_HOLE_REGION: Set[str] = {"h0", "h1", "c0", "c1"}
INTERIOR_ORDER: List[str] = ["h0", "h1", "c0", "c1"]
EXTERIOR_ORDER: List[str] = ["o0", "o1", "o2"]

TICKS = 12


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _cxo_from_pairs(pairs: Sequence[Tuple[int, int]]) -> k.CxO:
    if len(pairs) != 8:
        raise ValueError("pairs must have length 8")
    vals = [k.GInt(int(re), int(im)) for re, im in pairs]
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _state_signature(state: k.CxO) -> Tuple[Tuple[int, int], ...]:
    return tuple((z.re, z.im) for z in state)


def _subset_signature(world: k.World, subset: Sequence[str]) -> Tuple[Tuple[Tuple[int, int], ...], ...]:
    return tuple(_state_signature(world.states[nid]) for nid in subset)


def _make_initial_state(*, exterior_variant: int, interior_variant: int) -> Dict[str, k.CxO]:
    ext_a = _cxo_from_pairs(((1, 0), (0, 1), (0, 0), (-1, 0), (0, -1), (0, 0), (1, 0), (0, 0)))
    ext_b = _cxo_from_pairs(((0, 1), (1, 0), (0, 0), (0, -1), (-1, 0), (0, 0), (0, 1), (0, 0)))
    int_a = _cxo_from_pairs(((1, 0), (0, 0), (1, 0), (0, 1), (0, 0), (-1, 0), (0, -1), (1, 0)))
    int_b = _cxo_from_pairs(((0, -1), (1, 0), (0, 1), (0, 0), (-1, 0), (0, 0), (1, 0), (0, 1)))

    ext_state = ext_a if exterior_variant == 0 else ext_b
    int_state = int_a if interior_variant == 0 else int_b

    init: Dict[str, k.CxO] = {}
    for nid in EXTERIOR_ORDER:
        init[nid] = ext_state
    for nid in INTERIOR_ORDER:
        init[nid] = int_state
    return init


def _run_trajectory(initial: Dict[str, k.CxO], ticks: int) -> List[k.World]:
    world = k.World(
        node_ids=list(NODE_IDS),
        parents={nid: list(PARENTS[nid]) for nid in NODE_IDS},
        states={nid: initial[nid] for nid in NODE_IDS},
        event_order=None,
        tick=0,
    )
    out = [world]
    cur = world
    for _ in range(ticks):
        cur = k.step(cur)
        out.append(cur)
    return out


def _all_edges(parents: Dict[str, List[str]]) -> List[Tuple[str, str]]:
    edges: List[Tuple[str, str]] = []
    for v, pids in parents.items():
        for u in pids:
            edges.append((u, v))
    return edges


def _horizon_nodes(region: Set[str], parents: Dict[str, List[str]]) -> List[str]:
    out: List[str] = []
    for v in sorted(region):
        pids = parents.get(v, [])
        if any(pid not in region for pid in pids):
            out.append(v)
    return out


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    rfc_path = ROOT / RFC_REPO_PATH

    edges = _all_edges(PARENTS)
    crossing_out = [(u, v) for (u, v) in edges if (u in BLACK_HOLE_REGION and v not in BLACK_HOLE_REGION)]
    horizon = _horizon_nodes(BLACK_HOLE_REGION, PARENTS)

    traj_interior_a = _run_trajectory(_make_initial_state(exterior_variant=0, interior_variant=0), TICKS)
    traj_interior_b = _run_trajectory(_make_initial_state(exterior_variant=0, interior_variant=1), TICKS)

    exterior_equal_by_tick: List[bool] = []
    for t in range(TICKS + 1):
        sig_a = _subset_signature(traj_interior_a[t], EXTERIOR_ORDER)
        sig_b = _subset_signature(traj_interior_b[t], EXTERIOR_ORDER)
        exterior_equal_by_tick.append(sig_a == sig_b)
    t3_pass = all(exterior_equal_by_tick)

    traj_exterior_a = _run_trajectory(_make_initial_state(exterior_variant=0, interior_variant=0), TICKS)
    traj_exterior_b = _run_trajectory(_make_initial_state(exterior_variant=1, interior_variant=0), TICKS)
    interior_diff_by_tick: List[bool] = []
    for t in range(TICKS + 1):
        sig_a = _subset_signature(traj_exterior_a[t], INTERIOR_ORDER)
        sig_b = _subset_signature(traj_exterior_b[t], INTERIOR_ORDER)
        interior_diff_by_tick.append(sig_a != sig_b)
    t4_pass = any(interior_diff_by_tick[1:])

    unity_all = True
    for world in traj_exterior_a:
        for nid in NODE_IDS:
            if not k.cxo_is_unity(world.states[nid]):
                unity_all = False
                break
        if not unity_all:
            break

    t1_pass = len(crossing_out) == 0
    t2_pass = len(horizon) > 0 and all(any(pid not in BLACK_HOLE_REGION for pid in PARENTS[h]) for h in horizon)
    t5_pass = bool(unity_all)

    tests = {
        "T1_topological_one_way_isolation": {
            "pass": bool(t1_pass),
            "crossing_outgoing_edges": crossing_out,
            "crossing_outgoing_edge_count": len(crossing_out),
        },
        "T2_horizon_ingress_non_empty": {
            "pass": bool(t2_pass),
            "horizon_nodes": horizon,
            "horizon_node_count": len(horizon),
        },
        "T3_exterior_independence_from_interior_init": {
            "pass": bool(t3_pass),
            "exterior_equal_by_tick": exterior_equal_by_tick,
        },
        "T4_exterior_to_interior_influence_exists": {
            "pass": bool(t4_pass),
            "interior_diff_by_tick": interior_diff_by_tick,
        },
        "T5_unity_boundedness_under_dense_interior": {
            "pass": bool(t5_pass),
            "ticks": TICKS,
            "unity_closed_all_nodes_all_ticks": bool(t5_pass),
        },
    }

    contract_pass = all(bool(row["pass"]) for row in tests.values())
    payload: Dict[str, Any] = {
        "schema_version": "blackhole_projection_contract_v1",
        "contract_id": "BH-PRJ-001",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "contract_rfc": RFC_REPO_PATH,
        "contract_rfc_sha256": _sha_file(rfc_path),
        "axiom_profile": {
            "state_domain": "cxo_over_unity",
            "kernel_profile": k.KERNEL_PROFILE,
            "projector_id": k.PROJECTOR_ID,
            "index_channel": "xor",
        },
        "graph_contract": {
            "node_count": len(NODE_IDS),
            "edge_count": len(edges),
            "black_hole_region": sorted(BLACK_HOLE_REGION),
            "exterior_region": sorted(set(NODE_IDS) - set(BLACK_HOLE_REGION)),
            "horizon_nodes": horizon,
            "horizon_count": len(horizon),
        },
        "tests": tests,
        "contract_pass": bool(contract_pass),
        "summary": [
            "Black-hole region is defined as one-way topological sink (no outgoing edges).",
            "Horizon is ingress boundary from exterior into sink.",
            "Projection-kernel witness shows exterior independence from interior initialization.",
            "Unity closure remains bounded for all ticks under dense interior update flow.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# Black-Hole Projection Contract Witness (v1)",
        "",
        f"- Contract ID: `{payload['contract_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        f"- Kernel profile: `{payload['axiom_profile']['kernel_profile']}`",
        f"- Projector: `{payload['axiom_profile']['projector_id']}`",
        f"- Contract pass: `{payload['contract_pass']}`",
        "",
        "## Graph Contract",
        f"- node_count: `{payload['graph_contract']['node_count']}`",
        f"- edge_count: `{payload['graph_contract']['edge_count']}`",
        f"- black_hole_region: `{payload['graph_contract']['black_hole_region']}`",
        f"- exterior_region: `{payload['graph_contract']['exterior_region']}`",
        f"- horizon_nodes: `{payload['graph_contract']['horizon_nodes']}`",
        "",
        "## Falsification Tests",
    ]
    tests = payload["tests"]
    lines.extend(
        [
            f"- T1 one-way isolation: pass=`{tests['T1_topological_one_way_isolation']['pass']}` "
            f"crossing_edge_count=`{tests['T1_topological_one_way_isolation']['crossing_outgoing_edge_count']}`",
            f"- T2 horizon ingress: pass=`{tests['T2_horizon_ingress_non_empty']['pass']}` "
            f"horizon_count=`{tests['T2_horizon_ingress_non_empty']['horizon_node_count']}`",
            f"- T3 exterior independence: pass=`{tests['T3_exterior_independence_from_interior_init']['pass']}`",
            f"- T4 exterior->interior influence: pass=`{tests['T4_exterior_to_interior_influence_exists']['pass']}`",
            f"- T5 unity boundedness: pass=`{tests['T5_unity_boundedness_under_dense_interior']['pass']}`",
        ]
    )
    lines.extend(["", "## Summary"])
    for s in payload["summary"]:
        lines.append(f"- {s}")
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: Dict[str, Any],
    *,
    json_paths: Sequence[Path] | None = None,
    md_paths: Sequence[Path] | None = None,
) -> None:
    j_paths = list(json_paths) if json_paths is not None else [OUT_JSON]
    m_paths = list(md_paths) if md_paths is not None else [OUT_MD]
    for path in j_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_markdown(payload)
    for path in m_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build black-hole projection contract witness (v1)")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write artifacts to cog_v2/sources")
    args = parser.parse_args()

    payload = build_payload()
    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {_to_repo_path(OUT_JSON)}")
        print(f"Wrote {_to_repo_path(OUT_MD)}")
        return
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        "blackhole_projection_contract_v1: "
        f"contract_pass={payload['contract_pass']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate strict layered causality and probe topological defects on DAGs."""

from __future__ import annotations

import argparse
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple


NodeId = str
Edge = Tuple[NodeId, NodeId]


@dataclass(frozen=True)
class ValidationConfig:
    max_sources: int = 128
    include_pair_examples: int = 16
    include_violation_examples: int = 32


def _read_json(path: Path) -> Dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected object JSON at {path}")
    return loaded


def _normalize_nodes(payload: Mapping[str, Any]) -> Dict[NodeId, int]:
    raw = payload.get("nodes")
    if not isinstance(raw, list):
        raise ValueError("nodes must be a list")
    out: Dict[NodeId, int] = {}
    for row in raw:
        if not isinstance(row, dict):
            raise ValueError("node rows must be objects")
        nid = str(row.get("id", "")).strip()
        if not nid:
            raise ValueError("node id missing/empty")
        if nid in out:
            raise ValueError(f"duplicate node id: {nid}")
        depth = row.get("depth")
        if not isinstance(depth, int) or depth < 0:
            raise ValueError(f"node depth must be non-negative int: {nid}")
        out[nid] = int(depth)
    return out


def _normalize_edges(payload: Mapping[str, Any]) -> List[Edge]:
    raw = payload.get("edges")
    if not isinstance(raw, list):
        raise ValueError("edges must be a list")
    out: List[Edge] = []
    for row in raw:
        if isinstance(row, list) and len(row) == 2:
            src = str(row[0]).strip()
            dst = str(row[1]).strip()
        elif isinstance(row, dict):
            src = str(row.get("src", "")).strip()
            dst = str(row.get("dst", "")).strip()
        else:
            raise ValueError("edge rows must be [src, dst] or {src,dst}")
        if not src or not dst:
            raise ValueError("edge src/dst missing")
        out.append((src, dst))
    return out


def _build_graph(nodes: Mapping[NodeId, int], edges: Sequence[Edge]) -> Tuple[Dict[NodeId, List[NodeId]], Dict[NodeId, int]]:
    adj: Dict[NodeId, List[NodeId]] = {nid: [] for nid in nodes}
    indeg: Dict[NodeId, int] = {nid: 0 for nid in nodes}
    for src, dst in edges:
        if src not in nodes:
            raise ValueError(f"edge src not in nodes: {src}")
        if dst not in nodes:
            raise ValueError(f"edge dst not in nodes: {dst}")
        adj[src].append(dst)
        indeg[dst] += 1
    return adj, indeg


def _topological_order(adj: Mapping[NodeId, Sequence[NodeId]], indeg_in: Mapping[NodeId, int]) -> Tuple[bool, List[NodeId]]:
    indeg = dict(indeg_in)
    q: deque[NodeId] = deque(sorted([n for n, d in indeg.items() if d == 0]))
    order: List[NodeId] = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj.get(u, []):
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return len(order) == len(indeg), order


def _layer_violations(nodes: Mapping[NodeId, int], edges: Sequence[Edge]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for src, dst in edges:
        d_src = int(nodes[src])
        d_dst = int(nodes[dst])
        if d_dst != d_src + 1:
            out.append(
                {
                    "src": src,
                    "dst": dst,
                    "depth_src": d_src,
                    "depth_dst": d_dst,
                    "depth_delta": d_dst - d_src,
                }
            )
    return out


def _path_spread_for_source(
    source: NodeId,
    nodes: Mapping[NodeId, int],
    adj: Mapping[NodeId, Sequence[NodeId]],
    topo: Sequence[NodeId],
) -> List[Dict[str, Any]]:
    inf = 10**18
    dmin: Dict[NodeId, int] = {n: inf for n in nodes}
    dmax: Dict[NodeId, int] = {n: -inf for n in nodes}
    dmin[source] = 0
    dmax[source] = 0

    seen_source = False
    for u in topo:
        if u == source:
            seen_source = True
        if not seen_source:
            continue
        if dmax[u] < 0:
            continue
        for v in adj.get(u, []):
            cand_min = dmin[u] + 1
            cand_max = dmax[u] + 1
            if cand_min < dmin[v]:
                dmin[v] = cand_min
            if cand_max > dmax[v]:
                dmax[v] = cand_max

    rows: List[Dict[str, Any]] = []
    for target in nodes:
        if target == source:
            continue
        if dmax[target] < 0:
            continue
        lmin = int(dmin[target])
        lmax = int(dmax[target])
        rows.append(
            {
                "src": source,
                "dst": target,
                "lmin": lmin,
                "lmax": lmax,
                "delta": lmax - lmin,
                "depth_src": int(nodes[source]),
                "depth_dst": int(nodes[target]),
                "depth_diff": int(nodes[target]) - int(nodes[source]),
            }
        )
    return rows


def analyze_graph(payload: Mapping[str, Any], cfg: ValidationConfig | None = None) -> Dict[str, Any]:
    config = cfg if cfg is not None else ValidationConfig()
    nodes = _normalize_nodes(payload)
    edges = _normalize_edges(payload)
    adj, indeg = _build_graph(nodes, edges)
    is_dag, topo = _topological_order(adj, indeg)

    violations = _layer_violations(nodes, edges)
    strict_layering = len(violations) == 0

    pair_rows: List[Dict[str, Any]] = []
    defect_rows: List[Dict[str, Any]] = []
    sampled_sources = sorted(nodes.keys())[: max(0, int(config.max_sources))]
    if is_dag:
        for src in sampled_sources:
            rows = _path_spread_for_source(src, nodes, adj, topo)
            pair_rows.extend(rows)
            defect_rows.extend([r for r in rows if int(r["delta"]) > 0])

    max_delta = max((int(r["delta"]) for r in pair_rows), default=0)
    canonical_pass = bool(is_dag and strict_layering and max_delta == 0)

    return {
        "schema_version": "layered_causality_validation_v1",
        "canonical_profile_id": "layered_strict_v1",
        "summary": {
            "node_count": int(len(nodes)),
            "edge_count": int(len(edges)),
            "is_dag": bool(is_dag),
            "strict_layering_holds": bool(strict_layering),
            "layer_violation_count": int(len(violations)),
            "sampled_source_count": int(len(sampled_sources)),
            "sampled_pair_count": int(len(pair_rows)),
            "defect_pair_count": int(len(defect_rows)),
            "max_delta": int(max_delta),
            "has_multi_length_paths": bool(max_delta > 0),
            "canonical_layered_verdict": "pass" if canonical_pass else "fail",
        },
        "layer_violations_examples": violations[: max(0, int(config.include_violation_examples))],
        "defect_pair_examples": defect_rows[: max(0, int(config.include_pair_examples))],
        "notes": [
            "Delta(A,B)=Lmax-Lmin over directed A->B paths.",
            "Canonical strict layering expects no edge-depth violations and max_delta=0.",
            "If transitive shortcut edges are present in input, defect metrics can be inflated.",
        ],
    }


def _demo_graphs() -> Dict[str, Dict[str, Any]]:
    layered_ok = {
        "nodes": [
            {"id": "A0", "depth": 0},
            {"id": "B1", "depth": 1},
            {"id": "C1", "depth": 1},
            {"id": "D2", "depth": 2},
            {"id": "E3", "depth": 3},
        ],
        "edges": [
            ["A0", "B1"],
            ["A0", "C1"],
            ["B1", "D2"],
            ["C1", "D2"],
            ["D2", "E3"],
        ],
    }

    shortcut_defect = {
        "nodes": [
            {"id": "A0", "depth": 0},
            {"id": "B1", "depth": 1},
            {"id": "C2", "depth": 2},
            {"id": "D3", "depth": 3},
        ],
        "edges": [
            ["A0", "B1"],
            ["B1", "C2"],
            ["C2", "D3"],
            ["A0", "C2"],  # skip edge, depth jump +2
        ],
    }
    return {"layered_ok": layered_ok, "shortcut_defect": shortcut_defect}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate strict layered causality on DAG input")
    parser.add_argument("--input", type=str, default="", help="Path to graph JSON ({nodes,edges})")
    parser.add_argument("--output", type=str, default="", help="Optional output JSON path")
    parser.add_argument("--max-sources", type=int, default=128, help="Max sources to sample")
    parser.add_argument("--include-pair-examples", type=int, default=16, help="Number of defect pair examples")
    parser.add_argument(
        "--include-violation-examples", type=int, default=32, help="Number of edge-layer violation examples"
    )
    parser.add_argument("--demo", action="store_true", help="Run built-in demo graphs")
    args = parser.parse_args()

    cfg = ValidationConfig(
        max_sources=int(args.max_sources),
        include_pair_examples=int(args.include_pair_examples),
        include_violation_examples=int(args.include_violation_examples),
    )

    if args.demo:
        results: Dict[str, Any] = {}
        for name, graph in _demo_graphs().items():
            results[name] = analyze_graph(graph, cfg)
        payload: Dict[str, Any] = {
            "schema_version": "layered_causality_validation_demo_v1",
            "results": results,
        }
    else:
        if not str(args.input).strip():
            raise SystemExit("--input is required unless --demo is set")
        graph = _read_json(Path(str(args.input)))
        payload = analyze_graph(graph, cfg)

    if str(args.output).strip():
        out = Path(str(args.output))
        _write_json(out, payload)
        print(f"Wrote {out}")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

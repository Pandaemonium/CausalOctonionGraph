"""
calc/xor_proton_gluon_braid.py

Deterministic three-quark proton-proxy simulation with a cyclic gluon braid.

This module stays in the XOR runtime path and uses:
1) locked Fano/Witt conventions from calc.conftest,
2) the typed event engine state transition,
3) deterministic edge ordering and no randomness.

The braid demonstrated here is a directed 3-cycle of gluon-tagged edges:
  q0 -> q1 -> q2 -> q0
with each edge operator selected to route from source Witt pair to destination Witt pair.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from calc.conftest import FANO_THIRD, WITT_PAIRS
from calc.xor_event_engine import (
    XEdgeOperator,
    XEventState,
    XNodeState,
    canonical_node_ids,
    run_event_steps,
)
from calc.xor_furey_ideals import StateGI, state_basis

# Directed color-exchange cycle across the three Witt pairs.
EXCHANGE_CYCLE: Tuple[Tuple[int, int], ...] = ((0, 1), (1, 2), (2, 0))


def _to_base8(n: int) -> str:
    sign = "-" if n < 0 else ""
    return sign + format(abs(n), "o")


def dominant_imag_channel(state: StateGI) -> int:
    """
    Return dominant imaginary channel index (1..7) by L1 coefficient magnitude.
    Tie-break by smaller channel index.
    """
    best_idx: int = 1
    best_abs = -1
    for i in range(1, 8):
        re, im = state[i]
        mag = abs(re) + abs(im)
        if mag > best_abs or (mag == best_abs and i < best_idx):
            best_abs = mag
            best_idx = i
    return best_idx


def _valid_gluon_candidates(src_pair_idx: int, dst_pair_idx: int) -> List[int]:
    """
    Return zero-index imaginary channels g such that:
      for each src in source Witt pair, src * g lands in destination Witt pair.
    """
    src_pair = set(WITT_PAIRS[src_pair_idx])
    dst_pair = set(WITT_PAIRS[dst_pair_idx])
    out: List[int] = []
    for g in range(7):
        if g in src_pair or g in dst_pair:
            continue
        ok = True
        for src in src_pair:
            if src == g:
                ok = False
                break
            target = FANO_THIRD[(src, g)]
            if target not in dst_pair:
                ok = False
                break
        if ok:
            out.append(g)
    return out


def select_gluon_operator(src_pair_idx: int, dst_pair_idx: int) -> int:
    """
    Deterministically choose one routing gluon operator index in event-engine form (1..7).
    Policy: pick smallest valid zero-index channel g and return g+1.
    """
    candidates = _valid_gluon_candidates(src_pair_idx, dst_pair_idx)
    if not candidates:
        raise ValueError(f"No routing gluon candidate for pair exchange {src_pair_idx}->{dst_pair_idx}")
    return candidates[0] + 1


def proton_quark_seed_states() -> Tuple[StateGI, StateGI, StateGI]:
    """
    Build three quark-proxy seed states (one per Witt pair).
    Uses the first channel from each pair as deterministic representative.
    """
    q0 = state_basis(WITT_PAIRS[0][0] + 1, (1, 0))
    q1 = state_basis(WITT_PAIRS[1][0] + 1, (1, 0))
    q2 = state_basis(WITT_PAIRS[2][0] + 1, (1, 0))
    return q0, q1, q2


def build_proton_gluon_braid_initial_state() -> XEventState:
    """
    Construct initial event state:
    1) three quark nodes q0,q1,q2,
    2) three directed gluon edges in the exchange cycle.
    """
    q0, q1, q2 = proton_quark_seed_states()
    nodes = {
        0: XNodeState(node_id=0, state=q0, tick_count=0, topo_depth=0),
        1: XNodeState(node_id=1, state=q1, tick_count=0, topo_depth=0),
        2: XNodeState(node_id=2, state=q2, tick_count=0, topo_depth=0),
    }

    edges: List[XEdgeOperator] = []
    for order, (src_pair, dst_pair) in enumerate(EXCHANGE_CYCLE):
        op_idx = select_gluon_operator(src_pair, dst_pair)
        edges.append(
            XEdgeOperator(
                edge_id=f"q{src_pair}_to_q{dst_pair}",
                src_node_id=src_pair,
                dst_node_id=dst_pair,
                op_idx=op_idx,
                hand="left",
                payload_mode="src_state",
                order=order,
            )
        )

    return XEventState(
        nodes=nodes,
        edges=tuple(edges),
        pending_messages=tuple(),
        step_index=0,
        event_log=tuple(),
    )


def _dominant_tuple(state: XEventState) -> Tuple[int, int, int]:
    ids = canonical_node_ids(state)
    return tuple(dominant_imag_channel(state.nodes[i].state) for i in ids)  # type: ignore[return-value]


def _detect_period(seq: Sequence[Tuple[int, int, int]]) -> Optional[int]:
    if not seq:
        return None
    initial = seq[0]
    for i in range(1, len(seq)):
        if seq[i] == initial:
            return i
    return None


def build_proton_gluon_braid_dataset(steps: int = 24) -> Dict[str, Any]:
    if steps < 1:
        raise ValueError("steps must be >= 1")

    initial = build_proton_gluon_braid_initial_state()
    trace = run_event_steps(initial, steps=steps)

    dominant_seq: List[Tuple[int, int, int]] = [_dominant_tuple(s) for s in trace]
    period = _detect_period(dominant_seq)

    trace_rows: List[Dict[str, Any]] = []
    for st, dom in zip(trace, dominant_seq):
        ids = canonical_node_ids(st)
        trace_rows.append(
            {
                "step_index": st.step_index,
                "dominant_channels": list(dom),
                "states_base8": {
                    str(i): [[_to_base8(re), _to_base8(im)] for (re, im) in st.nodes[i].state]
                    for i in ids
                },
            }
        )

    edge_cycle = [
        {
            "edge_id": e.edge_id,
            "src_node_id": e.src_node_id,
            "dst_node_id": e.dst_node_id,
            "op_idx": e.op_idx,
            "hand": e.hand,
            "payload_mode": e.payload_mode,
            "order": e.order,
        }
        for e in sorted(initial.edges, key=lambda x: x.order)
    ]

    braid_hash = hashlib.sha256(
        json.dumps([row["dominant_channels"] for row in trace_rows], separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "schema_version": "xor_proton_gluon_braid_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "policy_lock": {
            "deterministic": True,
            "runtime": "xor_event_engine",
            "edge_cycle": "q0->q1->q2->q0",
            "edge_operator_selection": "smallest_valid_routing_gluon_per_pair_exchange",
        },
        "steps": steps,
        "exchange_cycle": [list(p) for p in EXCHANGE_CYCLE],
        "edge_cycle": edge_cycle,
        "dominant_channel_period": period,
        "braid_detected": period is not None and period > 1,
        "dominant_sequence_hash": braid_hash,
        "trace": trace_rows,
    }


def write_proton_gluon_braid_artifacts(
    dataset: Dict[str, Any],
    json_paths: Optional[List[Path]] = None,
    csv_paths: Optional[List[Path]] = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_proton_gluon_braid.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_proton_gluon_braid.csv")]

    for p in json_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = ["step_index", "dominant_q0", "dominant_q1", "dominant_q2"]
    rows = []
    for r in dataset["trace"]:
        d0, d1, d2 = r["dominant_channels"]
        rows.append(
            {
                "step_index": r["step_index"],
                "dominant_q0": d0,
                "dominant_q1": d1,
                "dominant_q2": d2,
            }
        )

    for p in csv_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)


def main() -> int:
    dataset = build_proton_gluon_braid_dataset(steps=24)
    write_proton_gluon_braid_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_proton_gluon_braid.json"),
            Path("website/data/xor_proton_gluon_braid.json"),
        ],
        csv_paths=[
            Path("calc/xor_proton_gluon_braid.csv"),
            Path("website/data/xor_proton_gluon_braid.csv"),
        ],
    )
    print("Wrote calc/xor_proton_gluon_braid.json")
    print("Wrote calc/xor_proton_gluon_braid.csv")
    print("Wrote website/data/xor_proton_gluon_braid.json")
    print("Wrote website/data/xor_proton_gluon_braid.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


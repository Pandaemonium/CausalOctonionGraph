"""
calc/xor_observables.py

Shared observables/metrics utilities for XOR scenario and ensemble analysis.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Tuple


def decode_base8_int(value: str) -> int:
    """
    Decode signed base-8 string to integer.
    """
    if not isinstance(value, str):
        raise TypeError("value must be a str")
    if value == "":
        raise ValueError("empty base8 string")
    sign = -1 if value.startswith("-") else 1
    raw = value[1:] if sign < 0 else value
    if raw == "":
        raise ValueError("invalid base8 string")
    if any(ch not in "01234567" for ch in raw):
        raise ValueError(f"invalid base8 digits: {value}")
    return sign * int(raw, 8)


def shannon_entropy_from_counts(counts: Dict[str, int]) -> float:
    total = sum(max(0, int(v)) for v in counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for v in counts.values():
        n = max(0, int(v))
        if n == 0:
            continue
        p = n / total
        h -= p * math.log2(p)
    return h


def _node_ids_from_trace(trace: List[Dict[str, Any]]) -> List[str]:
    if not trace:
        return []
    return sorted(trace[0].get("charge_signs", {}).keys())


def charge_sign_flip_count(trace: List[Dict[str, Any]], node_id: str) -> int:
    flips = 0
    prev = None
    for row in trace:
        cur = row.get("charge_signs", {}).get(node_id)
        if prev is not None and cur is not None and cur != prev:
            flips += 1
        prev = cur
    return flips


def support_variation_count(trace: List[Dict[str, Any]], node_id: str) -> int:
    seen = set()
    for row in trace:
        support = row.get("supports", {}).get(node_id, [])
        seen.add(tuple(support))
    return len(seen)


def pair_kind_series(trace: List[Dict[str, Any]]) -> List[str]:
    out: List[str] = []
    for row in trace:
        k = row.get("pair_interaction_kind")
        out.append("none" if k is None else str(k))
    return out


def pair_kind_transition_count(trace: List[Dict[str, Any]]) -> int:
    seq = pair_kind_series(trace)
    if not seq:
        return 0
    n = 0
    for i in range(1, len(seq)):
        if seq[i] != seq[i - 1]:
            n += 1
    return n


def scenario_observables(scenario_result: Dict[str, Any]) -> Dict[str, Any]:
    trace = scenario_result.get("trace", [])
    pair_counts = scenario_result.get("pair_kind_counts", {})
    periods = scenario_result.get("periods", {})
    node_ids = _node_ids_from_trace(trace)

    node_metrics: Dict[str, Dict[str, Any]] = {}
    for node_id in node_ids:
        node_metrics[node_id] = {
            "charge_sign_flips": charge_sign_flip_count(trace, node_id),
            "support_variation_count": support_variation_count(trace, node_id),
            "period": periods.get(node_id),
        }

    return {
        "scenario_id": scenario_result.get("scenario_id"),
        "steps": scenario_result.get("steps"),
        "initial_pair_kind": scenario_result.get("initial_pair_kind"),
        "final_pair_kind": scenario_result.get("final_step", {}).get("pair_interaction_kind"),
        "pair_kind_counts": pair_counts,
        "pair_kind_entropy_bits": shannon_entropy_from_counts(pair_counts),
        "pair_kind_transition_count": pair_kind_transition_count(trace),
        "node_metrics": node_metrics,
    }


def aggregate_ensemble_observables(items: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(items)
    if not rows:
        return {
            "run_count": 0,
            "avg_pair_kind_entropy_bits": 0.0,
            "avg_pair_kind_transition_count": 0.0,
            "pair_kind_counts_total": {},
        }

    ent = 0.0
    trans = 0.0
    total_counts: Dict[str, int] = {}
    for row in rows:
        ent += float(row.get("pair_kind_entropy_bits", 0.0))
        trans += float(row.get("pair_kind_transition_count", 0.0))
        for k, v in row.get("pair_kind_counts", {}).items():
            total_counts[k] = total_counts.get(k, 0) + int(v)

    n = len(rows)
    return {
        "run_count": n,
        "avg_pair_kind_entropy_bits": ent / n,
        "avg_pair_kind_transition_count": trans / n,
        "pair_kind_counts_total": total_counts,
        "pair_kind_counts_total_entropy_bits": shannon_entropy_from_counts(total_counts),
    }


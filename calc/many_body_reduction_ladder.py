"""RFC-053 many-body reduction ladder artifact generator.

This module provides a deterministic, governance-friendly baseline for:
1. direct pair channel extraction,
2. background-conditioned pair channel extraction,
3. reduction error metrics for N -> 2 analysis.

The model here is intentionally simple and discrete:
- pair polarity is determined by charge-sign interaction class
- background influence is deterministic and order-invariant
- no RNG, no wall-clock dependence
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Node:
    node_id: str
    charge: float


def _sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def direct_score(charge_a: float, charge_b: float) -> int:
    """Pair-only channel score.

    Convention:
    - opposite nonzero charges -> attractive -> -1
    - same-sign nonzero charges -> repulsive -> +1
    - any vacuum/zero charge involvement -> neutral -> 0
    """
    if charge_a == 0.0 or charge_b == 0.0:
        return 0
    if _sign(charge_a) == _sign(charge_b):
        return 1
    return -1


def conditioned_score(charge_a: float, charge_b: float, external_charges: Iterable[float]) -> int:
    """Many-body conditioned channel score.

    Background drift term:
    - depends on net pair sign and count of nonzero external charges
    - is permutation-invariant over external nodes
    """
    base = direct_score(charge_a, charge_b)
    net_pair = charge_a + charge_b
    if net_pair == 0.0:
        return base

    nonzero_external = sum(1 for q in external_charges if q != 0.0)
    drift = _sign(net_pair) * nonzero_external
    return base + drift


def classify_from_score(score: int) -> str:
    if score > 0:
        return "repulsive"
    if score < 0:
        return "attractive"
    return "neutral"


def pair_step_metrics(nodes: list[Node], pair_ids: tuple[str, str]) -> dict:
    a_id, b_id = pair_ids
    by_id = {n.node_id: n for n in nodes}
    a = by_id[a_id]
    b = by_id[b_id]

    externals = [n.charge for n in nodes if n.node_id not in pair_ids]
    score_direct = direct_score(a.charge, b.charge)
    score_cond = conditioned_score(a.charge, b.charge, externals)

    return {
        "score_direct": score_direct,
        "score_conditioned": score_cond,
        "channel_direct": classify_from_score(score_direct),
        "channel_conditioned": classify_from_score(score_cond),
        "delta_bg": score_cond - score_direct,
        "error_abs": abs(score_cond - score_direct),
    }


def run_scenario(name: str, nodes: list[Node], pair_ids: tuple[str, str], horizon: int = 8, eps: int = 0) -> dict:
    if horizon <= 0:
        raise ValueError("horizon must be positive")

    per_tick = []
    for tick in range(horizon):
        metrics = pair_step_metrics(nodes, pair_ids)
        metrics["tick"] = tick
        per_tick.append(metrics)

    errors = [row["error_abs"] for row in per_tick]
    e_max = max(errors)
    e_mean = sum(errors) / len(errors)

    divergence_tick = next((i for i, e in enumerate(errors) if e > eps), None)
    reduction_mode = "exact" if e_max == 0 else "approx"

    return {
        "scenario": name,
        "pair_ids": list(pair_ids),
        "horizon": horizon,
        "eps": eps,
        "reduction_mode": reduction_mode,
        "error_max": e_max,
        "error_mean": e_mean,
        "divergence_tick": divergence_tick,
        "spawn_affected": False,
        "trace": per_tick,
    }


def ladder_scenarios() -> list[dict]:
    pair = ("a", "b")

    n2 = [Node("a", -0.5), Node("b", -0.5)]
    n3_inert = [Node("a", -0.5), Node("b", -0.5), Node("c", 0.0)]
    n3_active = [Node("a", -0.5), Node("b", -0.5), Node("c", +0.5)]
    n4_mixed = [
        Node("a", -0.5),
        Node("b", -0.5),
        Node("c", +0.5),
        Node("d", -0.5),
    ]

    return [
        run_scenario("N2_baseline", n2, pair_ids=pair),
        run_scenario("N3_inert_spectator", n3_inert, pair_ids=pair),
        run_scenario("N3_active_spectator", n3_active, pair_ids=pair),
        run_scenario("N4_mixed_background", n4_mixed, pair_ids=pair),
    ]


def _canonical_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def run_ladder() -> dict:
    scenarios = ladder_scenarios()
    payload = {"rfc": "RFC-053", "scheduler_mode": "snapshot_sync_v1", "scenarios": scenarios}
    payload["replay_hash"] = sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return payload


def _render_markdown(result: dict) -> str:
    lines = [
        "# Many-Body Reduction Ladder Results",
        "",
        f"- RFC: `{result['rfc']}`",
        f"- scheduler_mode: `{result['scheduler_mode']}`",
        f"- replay_hash: `{result['replay_hash']}`",
        "",
        "| Scenario | Mode | E_max | E_mean | k* |",
        "|---|---:|---:|---:|---:|",
    ]
    for sc in result["scenarios"]:
        k_star = "none" if sc["divergence_tick"] is None else str(sc["divergence_tick"])
        lines.append(
            f"| {sc['scenario']} | {sc['reduction_mode']} | {sc['error_max']} | {sc['error_mean']:.3f} | {k_star} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_artifacts(
    result: dict,
    json_path: str = "sources/many_body_reduction_ladder.json",
    md_path: str = "sources/many_body_reduction_ladder.md",
) -> tuple[Path, Path]:
    json_out = Path(json_path)
    md_out = Path(md_path)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)

    json_out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    md_out.write_text(_render_markdown(result), encoding="utf-8")
    return json_out, md_out


def main() -> int:
    result = run_ladder()
    json_out, md_out = write_artifacts(result)
    print(f"Wrote {json_out}")
    print(f"Wrote {md_out}")
    print(f"replay_hash={result['replay_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


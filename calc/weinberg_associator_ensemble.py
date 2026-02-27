"""
RFC-037 Avenue 13 ensemble:
statistical combinatoric averages under predeclared environmental conditions.

This script aggregates deterministic rollout members into condition-level
ensemble trajectories, avoiding single-policy cherry-picking.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, pstdev
from typing import Dict, List, Sequence, Tuple

from calc.weinberg_associator_running import (
    RolloutPolicy,
    series_from_load_sequence,
    simulate_policy,
    summary_from_series,
    triple_loads,
)

ROOT = Path(__file__).resolve().parents[1]
CONDITION_FILE_DEFAULT = Path(__file__).with_name("weinberg_associator_ensemble_conditions.json")
OUT_JSON = ROOT / "sources" / "weinberg_associator_ensemble_results.json"
OUT_MD = ROOT / "sources" / "weinberg_associator_ensemble_results.md"


@dataclass(frozen=True)
class EnsembleCondition:
    condition_id: str
    description: str
    central_colors: Tuple[int, ...]
    source_triples: Tuple[Tuple[int, int, int], ...]
    source_orders: Tuple[str, ...]
    basis_selectors: Tuple[str, ...]
    init_modes: Tuple[str, ...]
    projection: str


def load_condition_bundle(path: Path | None = None) -> Dict[str, object]:
    p = path or CONDITION_FILE_DEFAULT
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def bundle_checksum(bundle: Dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _parse_conditions(bundle: Dict[str, object]) -> List[EnsembleCondition]:
    out: List[EnsembleCondition] = []
    for row in bundle["conditions"]:
        central = tuple(int(c) for c in row["central_colors"])
        triples = tuple(tuple(int(x) for x in t) for t in row["source_triples"])
        for c in central:
            if c < 0 or c > 6:
                raise ValueError(f"central color out of range [0,6]: {c}")
        for t in triples:
            if len(t) != 3:
                raise ValueError(f"source triple must have length 3: {t}")
            for x in t:
                if x < 0 or x > 6:
                    raise ValueError(f"source color out of range [0,6]: {x}")
        out.append(
            EnsembleCondition(
                condition_id=str(row["condition_id"]),
                description=str(row["description"]),
                central_colors=central,
                source_triples=triples,
                source_orders=tuple(str(x) for x in row["source_orders"]),
                basis_selectors=tuple(str(x) for x in row["basis_selectors"]),
                init_modes=tuple(str(x) for x in row["init_modes"]),
                projection=str(row["projection"]),
            )
        )
    return out


def predeclared_condition_ids(path: Path | None = None) -> List[str]:
    bundle = load_condition_bundle(path)
    return [str(c["condition_id"]) for c in bundle["conditions"]]


def _member_policy_id(
    condition_id: str,
    central: int,
    triple: Tuple[int, int, int],
    order: str,
    selector: str,
    init_mode: str,
) -> str:
    return (
        f"{condition_id}__c{central}__s{triple[0]}-{triple[1]}-{triple[2]}"
        f"__o{order}__b{selector}__i{init_mode}"
    )


def _condition_members(condition: EnsembleCondition) -> List[RolloutPolicy]:
    members: List[RolloutPolicy] = []
    for c in condition.central_colors:
        for triple in condition.source_triples:
            for order in condition.source_orders:
                for selector in condition.basis_selectors:
                    for init_mode in condition.init_modes:
                        members.append(
                            RolloutPolicy(
                                policy_id=_member_policy_id(
                                    condition.condition_id, c, triple, order, selector, init_mode
                                ),
                                description=condition.description,
                                central_color=c,
                                source_colors=triple,
                                source_order=order,
                                basis_selector=selector,
                                init_mode=init_mode,
                                projection=condition.projection,
                            )
                        )
    return members


def _aggregate_tickwise(member_rows: Sequence[Dict[str, object]], ticks: int) -> List[Dict[str, float]]:
    avg_loads: List[Tuple[float, float, float]] = []
    for t in range(ticks):
        ex = mean(float(r["tick_loads"][t]["exclusive_u1"]) for r in member_rows)
        inc = mean(float(r["tick_loads"][t]["u1_inclusive"]) for r in member_rows)
        w = mean(float(r["tick_loads"][t]["weak"]) for r in member_rows)
        avg_loads.append((ex, inc, w))
    return series_from_load_sequence(avg_loads)


def _aggregate_hist(member_rows: Sequence[Dict[str, object]], ticks: int) -> List[Dict[str, float]]:
    counter: Counter[Tuple[int, int, int]] = Counter()
    for r in member_rows:
        for t in r["triples_seq"]:
            counter[(int(t[0]), int(t[1]), int(t[2]))] += 1
    total = sum(counter.values())
    if total == 0:
        mean_load = (0.0, 0.0, 0.0)
    else:
        ex = inc = w = 0.0
        for triple, n in counter.items():
            l_ex, l_inc, l_w = triple_loads(triple)
            p = float(n) / float(total)
            ex += p * l_ex
            inc += p * l_inc
            w += p * l_w
        mean_load = (ex, inc, w)
    return series_from_load_sequence([mean_load] * ticks)


def _condition_summary(member_rows: Sequence[Dict[str, object]], ticks: int) -> Dict[str, object]:
    finals = [float(r["summary_seq"]["final_sin2_assoc_exclusive"]) for r in member_rows]
    deltas = [float(r["summary_seq"]["delta_sin2_assoc_exclusive"]) for r in member_rows]

    tickwise_series = _aggregate_tickwise(member_rows, ticks)
    hist_series = _aggregate_hist(member_rows, ticks)

    return {
        "member_count": len(member_rows),
        "final_member_mean": mean(finals) if finals else float("nan"),
        "final_member_std": pstdev(finals) if len(finals) > 1 else 0.0,
        "final_member_min": min(finals) if finals else float("nan"),
        "final_member_max": max(finals) if finals else float("nan"),
        "fraction_negative_delta": (
            float(sum(1 for d in deltas if d < 0.0)) / float(len(deltas)) if deltas else float("nan")
        ),
        "series_tickwise_avg": tickwise_series,
        "series_hist_avg": hist_series,
        "summary_tickwise_avg": summary_from_series(tickwise_series),
        "summary_hist_avg": summary_from_series(hist_series),
    }


def evaluate_condition(condition: EnsembleCondition, ticks: int) -> Dict[str, object]:
    members = _condition_members(condition)
    rows = [simulate_policy(m, ticks=ticks) for m in members]
    summary = _condition_summary(rows, ticks)
    return {
        "condition_id": condition.condition_id,
        "description": condition.description,
        "members": rows,
        "summary": summary,
    }


def run_all(path: Path | None = None) -> Dict[str, object]:
    bundle = load_condition_bundle(path)
    ticks = int(bundle["ticks"])
    conditions = _parse_conditions(bundle)
    rows = [evaluate_condition(c, ticks) for c in conditions]
    return {
        "rfc": str(bundle["rfc"]),
        "avenue": str(bundle["avenue"]),
        "target_scale": bundle["target"]["scale"],
        "target_sin2_theta_w": float(bundle["target"]["sin2_theta_w"]),
        "ticks": ticks,
        "condition_file": str((path or CONDITION_FILE_DEFAULT).name),
        "condition_checksum": bundle_checksum(bundle),
        "rows": rows,
    }


def render_markdown(payload: Dict[str, object]) -> str:
    lines = [
        "# RFC-037 Avenue 13 Ensemble Results",
        "",
        "Statistical combinatoric averaging over predeclared environmental conditions.",
        f"Target: sin^2(theta_W) = {payload['target_sin2_theta_w']:.8f} at scale {payload['target_scale']}",
        f"Ticks: `{payload['ticks']}`",
        f"Condition checksum: `{payload['condition_checksum']}`",
        "",
        "| Condition | Members | Tickwise final | Hist final | Mean member final | Fraction negative delta |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload["rows"]:
        s = row["summary"]
        lines.append(
            "| {cid} | {m} | {tf:.8f} | {hf:.8f} | {mf:.8f} | {neg:.3f} |".format(
                cid=row["condition_id"],
                m=s["member_count"],
                tf=s["summary_tickwise_avg"]["final_sin2_assoc_exclusive"],
                hf=s["summary_hist_avg"]["final_sin2_assoc_exclusive"],
                mf=s["final_member_mean"],
                neg=s["fraction_negative_delta"],
            )
        )

    lines.extend(
        [
            "",
            "## Notes",
            "- Tickwise average: average per-tick associator loads across members.",
            "- Histogram average: average loads from aggregated triple frequencies.",
            "- No target-driven member selection is performed.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(payload: Dict[str, object]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="RFC-037 Avenue 13 ensemble evaluator")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload to stdout.")
    parser.add_argument("--no-write", action="store_true", help="Do not write artifacts.")
    args = parser.parse_args()

    payload = run_all(CONDITION_FILE_DEFAULT)
    if not args.no_write:
        write_artifacts(payload)
        print(f"Wrote {OUT_JSON}")
        print(f"Wrote {OUT_MD}")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

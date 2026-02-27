"""
S4 character-theory weighting probes for WEINBERG-001.

Purpose:
  Explore fixed, representation-derived class weights (RFC-029 H2 avenue)
  without output-driven tuning.

This script is descriptive: it reports all predeclared combinations in a
deterministic table and does not select a winning policy.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from calc.weinberg_s4_decomp import CLASS_LABELS, s4_conjugacy_class_sizes

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "sources" / "weinberg_s4_character_weight_scan.json"
OUT_MD = ROOT / "sources" / "weinberg_s4_character_weight_scan.md"
TARGET = 0.23122

# S4 irreducible characters by class in CLASS_LABELS order:
# labels: 1^4, 2,1,1, 2,2, 3,1, 4
S4_CHAR_TABLE: Dict[str, Dict[str, int]] = {
    "chi_trivial": {
        "1^4": 1,
        "2,1,1": 1,
        "2,2": 1,
        "3,1": 1,
        "4": 1,
    },
    "chi_sign": {
        "1^4": 1,
        "2,1,1": -1,
        "2,2": 1,
        "3,1": 1,
        "4": -1,
    },
    "chi_2d": {
        "1^4": 2,
        "2,1,1": 0,
        "2,2": 2,
        "3,1": -1,
        "4": 0,
    },
    "chi_3d_std": {
        "1^4": 3,
        "2,1,1": 1,
        "2,2": -1,
        "3,1": 0,
        "4": -1,
    },
    "chi_3d_twist": {
        "1^4": 3,
        "2,1,1": -1,
        "2,2": -1,
        "3,1": 0,
        "4": 1,
    },
}


@dataclass(frozen=True)
class CharacterPolicy:
    transform: str
    u1_irrep: str
    ew_irrep: str


def transform_weight(value: int, transform: str) -> float:
    if transform == "square":
        return float(value * value)
    if transform == "absolute":
        return float(abs(value))
    raise ValueError(f"unknown transform: {transform}")


def class_weight_vector(irrep: str, transform: str) -> Dict[str, float]:
    chars = S4_CHAR_TABLE[irrep]
    return {label: transform_weight(chars[label], transform) for label in CLASS_LABELS}


def weighted_sum(class_sizes: Dict[str, int], weights: Dict[str, float]) -> float:
    return float(sum(class_sizes[label] * weights[label] for label in CLASS_LABELS))


def evaluate_policy(policy: CharacterPolicy, class_sizes: Dict[str, int]) -> Dict[str, object]:
    w_u1 = class_weight_vector(policy.u1_irrep, policy.transform)
    w_ew = class_weight_vector(policy.ew_irrep, policy.transform)
    num = weighted_sum(class_sizes, w_u1)
    den = weighted_sum(class_sizes, w_ew)
    if den == 0:
        ratio = float("inf")
        gap = float("inf")
    else:
        ratio = num / den
        gap = ratio - TARGET
    return {
        "transform": policy.transform,
        "u1_irrep": policy.u1_irrep,
        "ew_irrep": policy.ew_irrep,
        "numerator": num,
        "denominator": den,
        "sin2_theta_w_obs": ratio,
        "gap_from_target": gap,
    }


def predeclared_character_policies() -> List[CharacterPolicy]:
    policies: List[CharacterPolicy] = []
    irreps = sorted(S4_CHAR_TABLE.keys())
    for transform in ("square", "absolute"):
        for u1 in irreps:
            for ew in irreps:
                policies.append(CharacterPolicy(transform=transform, u1_irrep=u1, ew_irrep=ew))
    return policies


def run_scan() -> Dict[str, object]:
    class_sizes = s4_conjugacy_class_sizes()
    rows = [evaluate_policy(p, class_sizes) for p in predeclared_character_policies()]
    rows_sorted = sorted(rows, key=lambda r: abs(float(r["gap_from_target"])))
    return {
        "target_sin2_theta_w": TARGET,
        "class_sizes": class_sizes,
        "rows": rows,
        "best_by_abs_gap": rows_sorted[0] if rows_sorted else None,
    }


def render_markdown(payload: Dict[str, object]) -> str:
    lines = [
        "# S4 Character-Weight Weinberg Scan",
        "",
        "Deterministic scan over predeclared irrep-weight combinations.",
        f"Target: `sin^2(theta_W) = {payload['target_sin2_theta_w']:.5f}`",
        "",
        "| Transform | U1 irrep | EW irrep | sin^2(theta_W)_obs | Gap |",
        "|---|---|---|---:|---:|",
    ]
    rows = sorted(payload["rows"], key=lambda r: abs(float(r["gap_from_target"])))
    for row in rows[:20]:
        lines.append(
            f"| {row['transform']} | {row['u1_irrep']} | {row['ew_irrep']} | "
            f"{row['sin2_theta_w_obs']:.8f} | {row['gap_from_target']:+.8f} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "- This is an avenue probe, not a promoted observable contract.",
            "- No policy was selected post-hoc for claim promotion.",
            "- Use this to decide which irrep-based weighting families are worth formalizing in Lean.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(payload: Dict[str, object]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")


def main() -> None:
    payload = run_scan()
    write_artifacts(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()


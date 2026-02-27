"""
calc/weinberg_s4_decomp.py

WEINBERG-001 utilities:
1) Legacy S4 vs SL(2,3) decomposition checks (kept for compatibility).
2) RFC-029 H2 falsification harness with policy-locked weighted observables.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import permutations, product
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

Perm = Tuple[int, ...]

CLASS_LABELS = ("1^4", "2,1,1", "2,2", "3,1", "4")
POLICY_FILE_DEFAULT = Path(__file__).with_name("weinberg_h2_policies.json")


def _compose_perms(p: Perm, q: Perm) -> Perm:
    """Compose permutations: result[i] = q[p[i]] (apply p then q)."""
    return tuple(q[p[i]] for i in range(len(p)))


def _perm_order(perm: Perm) -> int:
    """Order of a permutation by repeated composition."""
    identity = tuple(range(len(perm)))
    current = perm
    order = 1
    while current != identity:
        current = _compose_perms(current, perm)
        order += 1
        if order > 1000:
            raise ValueError(f"Order diverged for {perm}")
    return order


def _perm_inverse(perm: Perm) -> Perm:
    out = [0] * len(perm)
    for i, image in enumerate(perm):
        out[image] = i
    return tuple(out)


def _cycle_lengths(perm: Perm) -> Tuple[int, ...]:
    seen = [False] * len(perm)
    lengths = []
    for i in range(len(perm)):
        if seen[i]:
            continue
        cur = i
        n = 0
        while not seen[cur]:
            seen[cur] = True
            cur = perm[cur]
            n += 1
        lengths.append(n)
    return tuple(sorted(lengths))


def _cycle_type_label_s4(perm: Perm) -> str:
    lengths = _cycle_lengths(perm)
    mapping = {
        (1, 1, 1, 1): "1^4",
        (1, 1, 2): "2,1,1",
        (2, 2): "2,2",
        (1, 3): "3,1",
        (4,): "4",
    }
    if lengths not in mapping:
        raise ValueError(f"Unexpected S4 cycle structure: {lengths}")
    return mapping[lengths]


def _s4_group() -> List[Perm]:
    return [tuple(p) for p in permutations(range(4))]


def s4_element_order_histogram() -> Dict[int, int]:
    """
    Return order-of-element histogram for S4.

    Expected: {1: 1, 2: 9, 3: 8, 4: 6}.
    """
    hist: Dict[int, int] = {}
    for perm in _s4_group():
        ord_ = _perm_order(perm)
        hist[ord_] = hist.get(ord_, 0) + 1
    return dict(sorted(hist.items()))


def s4_conjugacy_class_sizes() -> Dict[str, int]:
    """Return S4 conjugacy class sizes keyed by cycle type label."""
    counts = {label: 0 for label in CLASS_LABELS}
    for perm in _s4_group():
        counts[_cycle_type_label_s4(perm)] += 1
    return counts


def s4_irrep_dimensions() -> Tuple[int, int, int, int, int]:
    """Character-theory irrep dimensions of S4 (fixed)."""
    return (1, 1, 2, 3, 3)


def _subgroup_closure(generators: Iterable[Perm], group: Sequence[Perm]) -> set[Perm]:
    identity = tuple(range(4))
    subgroup = set(generators)
    subgroup.add(identity)
    changed = True
    while changed:
        changed = False
        current = list(subgroup)
        for a, b in product(current, repeat=2):
            c = _compose_perms(a, b)
            if c not in subgroup:
                subgroup.add(c)
                changed = True
            inv = _perm_inverse(a)
            if inv not in subgroup:
                subgroup.add(inv)
                changed = True
    group_set = set(group)
    if not subgroup.issubset(group_set):
        raise ValueError("Generated subgroup leaked outside S4")
    return subgroup


def s4_subgroup_order_histogram() -> Dict[int, int]:
    """Return histogram of subgroup orders in S4."""
    group = _s4_group()
    identity = tuple(range(4))
    seen = {frozenset({identity})}
    queue = [frozenset({identity})]

    while queue:
        h = set(queue.pop())
        for g in group:
            if g in h:
                continue
            k = frozenset(_subgroup_closure(h | {g}, group))
            if k not in seen:
                seen.add(k)
                queue.append(k)

    hist: Dict[int, int] = {}
    for subgroup in seen:
        order = len(subgroup)
        hist[order] = hist.get(order, 0) + 1
    return dict(sorted(hist.items()))


def structural_invariants() -> Dict[str, object]:
    """Canonical S4 structural invariants used for policy-governance checks."""
    payload = {
        "s4_class_sizes": s4_conjugacy_class_sizes(),
        "s4_irrep_dims": list(s4_irrep_dimensions()),
        "s4_subgroup_order_histogram": s4_subgroup_order_histogram(),
    }
    payload["structural_checksum"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return payload


def _gf3_det(m: Tuple[int, int, int, int]) -> int:
    """Determinant of 2x2 matrix m = (a,b,c,d) over GF(3)."""
    a, b, c, d = m
    return (a * d - b * c) % 3


def _gf3_matmul(
    m1: Tuple[int, int, int, int], m2: Tuple[int, int, int, int]
) -> Tuple[int, int, int, int]:
    """Multiply two 2x2 matrices over GF(3)."""
    a1, b1, c1, d1 = m1
    a2, b2, c2, d2 = m2
    return (
        (a1 * a2 + b1 * c2) % 3,
        (a1 * b2 + b1 * d2) % 3,
        (c1 * a2 + d1 * c2) % 3,
        (c1 * b2 + d1 * d2) % 3,
    )


def _matrix_order_gf3(m: Tuple[int, int, int, int]) -> int:
    """Compute the order of a matrix in SL(2,3) by repeated multiplication."""
    identity = (1, 0, 0, 1)
    current = m
    order = 1
    while current != identity:
        current = _gf3_matmul(current, m)
        order += 1
        if order > 100:
            raise ValueError(f"Order diverged for {m}")
    return order


def sl23_element_order_histogram() -> Dict[int, int]:
    """
    Return the order-of-element histogram for SL(2,3).

    Expected: {1:1, 2:1, 3:8, 4:6, 6:8}.
    """
    hist: Dict[int, int] = {}
    for a in range(3):
        for b in range(3):
            for c in range(3):
                for d in range(3):
                    m = (a, b, c, d)
                    if _gf3_det(m) == 1:
                        ord_ = _matrix_order_gf3(m)
                        hist[ord_] = hist.get(ord_, 0) + 1
    return dict(sorted(hist.items()))


def s4_subgroup_chain() -> List[Tuple[str, int]]:
    """
    Return the electroweak symmetry breaking subgroup chain in the COG model.
    """
    return [
        ("GL(3,2)", 168),
        ("S4", 24),
        ("V4", 4),
        ("Z2", 2),
        ("1", 1),
    ]


def weinberg_angle_estimate() -> float:
    """Legacy estimate from subgroup-index ratio: |V4|/|S4| = 4/24."""
    return 4 / 24


def s4_vs_sl23_distinguisher() -> bool:
    """Return True when S4 and SL(2,3) histograms differ."""
    return s4_element_order_histogram() != sl23_element_order_histogram()


def load_h2_policy_bundle(policy_file: Path | None = None) -> Dict[str, object]:
    """Load versioned H2 policy bundle from JSON."""
    path = policy_file or POLICY_FILE_DEFAULT
    with path.open("r", encoding="utf-8") as f:
        bundle = json.load(f)
    return bundle


def predeclared_h2_policy_ids(policy_file: Path | None = None) -> List[str]:
    bundle = load_h2_policy_bundle(policy_file)
    return [p["policy_id"] for p in bundle["policies"]]


def _policy_checksum(policy: Dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(policy, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _normalize_hist_keys(raw: Dict[object, object]) -> Dict[int, int]:
    return {int(k): int(v) for k, v in raw.items()}


def validate_policy_bundle(bundle: Dict[str, object]) -> None:
    """Governance check: pinned invariants in bundle must match computed S4 facts."""
    computed = structural_invariants()
    declared = bundle["structural_invariants"]

    if declared["s4_class_sizes"] != computed["s4_class_sizes"]:
        raise ValueError("Policy bundle class-size invariants mismatch computed S4 values")
    if list(declared["s4_irrep_dims"]) != list(computed["s4_irrep_dims"]):
        raise ValueError("Policy bundle irrep dims mismatch computed S4 values")

    declared_hist = _normalize_hist_keys(declared["s4_subgroup_order_histogram"])
    computed_hist = _normalize_hist_keys(computed["s4_subgroup_order_histogram"])
    if declared_hist != computed_hist:
        raise ValueError("Policy bundle subgroup-order histogram mismatch computed S4 values")


def _weighted_sum(
    class_sizes: Dict[str, int], weights: Dict[str, float]
) -> float:
    return float(sum(class_sizes[label] * float(weights[label]) for label in CLASS_LABELS))


def run_h2_policy(
    policy_id: str, policy_file: Path | None = None
) -> Dict[str, object]:
    """Evaluate one predeclared RFC-029 H2 policy."""
    bundle = load_h2_policy_bundle(policy_file)
    validate_policy_bundle(bundle)

    policies = bundle["policies"]
    selected = None
    for p in policies:
        if p["policy_id"] == policy_id:
            selected = p
            break
    if selected is None:
        available = ", ".join(sorted(p["policy_id"] for p in policies))
        raise KeyError(f"unknown policy_id '{policy_id}'. available: {available}")

    class_sizes = s4_conjugacy_class_sizes()
    numerator = _weighted_sum(class_sizes, selected["u1_weights"])
    denominator = _weighted_sum(class_sizes, selected["ew_weights"])
    if denominator == 0:
        raise ValueError(f"{policy_id}: denominator is zero")

    ratio = numerator / denominator
    target = float(bundle["target"]["sin2_theta_w"])
    result = {
        "rfc": "RFC-029",
        "branch": "H2",
        "mode": "falsification",
        "target_scale": bundle["target"]["scale"],
        "target_sin2_theta_w": target,
        "policy_id": selected["policy_id"],
        "policy_description": selected["description"],
        "policy_checksum": _policy_checksum(selected),
        "structural_checksum": structural_invariants()["structural_checksum"],
        "observable": {
            "numerator": numerator,
            "denominator": denominator,
            "sin2_theta_w_obs": ratio,
            "gap_from_target": ratio - target,
        },
    }
    return result


def run_h2_ablation(policy_file: Path | None = None) -> List[Dict[str, object]]:
    """Evaluate all predeclared policies exactly once, in declared order."""
    bundle = load_h2_policy_bundle(policy_file)
    return [run_h2_policy(p["policy_id"], policy_file) for p in bundle["policies"]]


def _print_legacy_summary() -> None:
    print("=" * 60)
    print("WEINBERG-001: S4 vs SL(2,3) Decomposition")
    print("=" * 60)

    h_s4 = s4_element_order_histogram()
    print(f"\nS4 element order histogram:      {h_s4}")
    print(f"S4 total elements:               {sum(h_s4.values())}")

    h_sl23 = sl23_element_order_histogram()
    print(f"\nSL(2,3) element order histogram: {h_sl23}")
    print(f"SL(2,3) total elements:          {sum(h_sl23.values())}")

    print(f"\nNon-isomorphic? {s4_vs_sl23_distinguisher()}")

    print("\nSubgroup chain:")
    chain = s4_subgroup_chain()
    for i, (name, order) in enumerate(chain):
        if i < len(chain) - 1:
            idx = order // chain[i + 1][1]
            print(f"  {name:10s} (order {order:4d})  [index {idx} down]")
        else:
            print(f"  {name:10s} (order {order:4d})")

    theta = weinberg_angle_estimate()
    print("\nCOG Weinberg estimate:")
    print(f"  sin^2(theta_W) = 4/24 = {theta:.6f}")
    print("  Physical:        0.2312")
    print(f"  Discrepancy:     {(0.2312 - theta) / 0.2312 * 100:.1f}% undershoot")


def main() -> None:
    parser = argparse.ArgumentParser(description="WEINBERG-001 S4 tooling")
    parser.add_argument(
        "--h2-policy-id",
        help="Run RFC-029 H2 evaluation for this predeclared policy_id.",
    )
    parser.add_argument(
        "--h2-ablation",
        action="store_true",
        help="Run all predeclared RFC-029 H2 policies in declaration order.",
    )
    parser.add_argument(
        "--list-policies",
        action="store_true",
        help="List predeclared H2 policy ids and exit.",
    )
    parser.add_argument(
        "--policy-file",
        type=Path,
        default=POLICY_FILE_DEFAULT,
        help="Path to policy bundle JSON.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output for H2 mode.",
    )
    args = parser.parse_args()

    if args.list_policies:
        bundle = load_h2_policy_bundle(args.policy_file)
        for p in bundle["policies"]:
            print(f"{p['policy_id']}: {p['description']}")
        return

    if args.h2_ablation:
        payload = run_h2_ablation(args.policy_file)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
            return
        print("=== RFC-029 H2 ablation ===")
        for row in payload:
            obs = row["observable"]
            print(
                f"{row['policy_id']}: sin2={obs['sin2_theta_w_obs']:.8f}, "
                f"gap={obs['gap_from_target']:+.8f}, "
                f"policy_checksum={row['policy_checksum'][:12]}..."
            )
        return

    if args.h2_policy_id:
        payload = run_h2_policy(args.h2_policy_id, args.policy_file)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
            return
        obs = payload["observable"]
        print("=== RFC-029 H2 policy evaluation ===")
        print(f"policy_id:          {payload['policy_id']}")
        print(f"policy_checksum:    {payload['policy_checksum']}")
        print(f"structural_checksum:{payload['structural_checksum']}")
        print(f"target_scale:       {payload['target_scale']}")
        print(f"sin2_theta_w_obs:   {obs['sin2_theta_w_obs']:.8f}")
        print(f"target:             {payload['target_sin2_theta_w']:.8f}")
        print(f"gap_from_target:    {obs['gap_from_target']:+.8f}")
        return

    _print_legacy_summary()


if __name__ == "__main__":
    main()

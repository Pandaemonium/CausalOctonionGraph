"""
ALPHA-001 policy-governed estimator.

Evaluates predeclared discrete-only candidate policies from `calc/alpha_policies.json`
and emits deterministic artifacts with policy checksums and replay hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

POLICY_FILE_DEFAULT = Path(__file__).with_name("alpha_policies.json")
ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "sources" / "alpha_policy_results.json"
OUT_MD = ROOT / "sources" / "alpha_policy_results.md"


def _sha(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load_policy_bundle(policy_file: Path | None = None) -> dict[str, Any]:
    path = policy_file or POLICY_FILE_DEFAULT
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _assert_no_forbidden_keys(obj: Any) -> None:
    forbidden = {"attenuation", "fit_param", "fitted_param", "tuned_param"}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in forbidden:
                raise ValueError(f"Forbidden key in policy bundle: {k}")
            _assert_no_forbidden_keys(v)
        return
    if isinstance(obj, list):
        for v in obj:
            _assert_no_forbidden_keys(v)


def _to_fraction(x: Any) -> Fraction:
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x, 1)
    if isinstance(x, str):
        return Fraction(x)
    if isinstance(x, float):
        return Fraction(str(x))
    raise TypeError(f"Unsupported numeric value: {x!r}")


def _eval_expr(expr: dict[str, Any], inputs: dict[str, int]) -> Fraction:
    op = expr.get("op")
    if op == "const":
        return _to_fraction(expr["value"])
    if op == "input":
        name = expr["name"]
        if name not in inputs:
            raise KeyError(f"Unknown input name: {name}")
        return _to_fraction(inputs[name])
    if op == "add":
        return sum((_eval_expr(e, inputs) for e in expr["args"]), Fraction(0, 1))
    if op == "sub":
        return _eval_expr(expr["left"], inputs) - _eval_expr(expr["right"], inputs)
    if op == "mul":
        out = Fraction(1, 1)
        for e in expr["args"]:
            out *= _eval_expr(e, inputs)
        return out
    if op == "pow":
        base = _eval_expr(expr["base"], inputs)
        exp = int(expr["exp"])
        if exp < 0:
            raise ValueError("Negative exponent not allowed in discrete policy expressions")
        return base**exp
    raise ValueError(f"Unsupported expression op: {op}")


def validate_policy_bundle(bundle: dict[str, Any]) -> None:
    if "target" not in bundle or "alpha" not in bundle["target"]:
        raise ValueError("Policy bundle must define target.alpha")
    if "discrete_inputs" not in bundle:
        raise ValueError("Policy bundle must define discrete_inputs")
    if "policies" not in bundle or not isinstance(bundle["policies"], list):
        raise ValueError("Policy bundle must define policies[]")

    _assert_no_forbidden_keys(bundle)

    inputs = bundle["discrete_inputs"]
    known_inputs = set(inputs.keys())
    seen_ids: set[str] = set()

    for policy in bundle["policies"]:
        pid = policy.get("policy_id")
        if not pid:
            raise ValueError("Every policy must have policy_id")
        if pid in seen_ids:
            raise ValueError(f"Duplicate policy_id: {pid}")
        seen_ids.add(pid)

        if policy.get("no_fitted_attenuation") is not True:
            raise ValueError(f"{pid}: no_fitted_attenuation must be true")

        allowed = set(policy.get("allowed_inputs", []))
        if not allowed:
            raise ValueError(f"{pid}: allowed_inputs must be non-empty")
        if not allowed.issubset(known_inputs):
            raise ValueError(f"{pid}: allowed_inputs include unknown keys")

        formula = policy.get("formula", {})
        if "numerator" not in formula or "denominator" not in formula:
            raise ValueError(f"{pid}: formula must include numerator and denominator")


def predeclared_policy_ids(policy_file: Path | None = None) -> list[str]:
    bundle = load_policy_bundle(policy_file)
    validate_policy_bundle(bundle)
    return [p["policy_id"] for p in bundle["policies"]]


def _policy_checksum(policy: dict[str, Any]) -> str:
    return _sha(policy)


def run_policy(policy_id: str, policy_file: Path | None = None) -> dict[str, Any]:
    bundle = load_policy_bundle(policy_file)
    validate_policy_bundle(bundle)

    selected = next((p for p in bundle["policies"] if p["policy_id"] == policy_id), None)
    if selected is None:
        available = ", ".join(sorted(p["policy_id"] for p in bundle["policies"]))
        raise KeyError(f"unknown policy_id '{policy_id}'. available: {available}")

    inputs = bundle["discrete_inputs"]
    formula = selected["formula"]
    num = _eval_expr(formula["numerator"], inputs)
    den = _eval_expr(formula["denominator"], inputs)
    if den == 0:
        raise ValueError(f"{policy_id}: denominator evaluated to zero")

    value = num / den
    target = _to_fraction(bundle["target"]["alpha"])
    abs_gap = abs(value - target)
    rel_gap = abs_gap / target if target != 0 else Fraction(0, 1)
    policy_checksum = _policy_checksum(selected)

    replay_payload = {
        "policy_id": policy_id,
        "candidate_fraction": f"{value.numerator}/{value.denominator}",
        "target_fraction": f"{target.numerator}/{target.denominator}",
        "policy_checksum": policy_checksum,
    }

    return {
        "rfc": "ALPHA-001",
        "target_source": bundle["target"]["source"],
        "target_scale": bundle["target"]["scale"],
        "policy_id": policy_id,
        "policy_description": selected["description"],
        "policy_checksum": policy_checksum,
        "bundle_checksum": _sha(
            {
                "target": bundle["target"],
                "discrete_inputs": bundle["discrete_inputs"],
                "policy_ids": [p["policy_id"] for p in bundle["policies"]],
            }
        ),
        "candidate": {
            "fraction": f"{value.numerator}/{value.denominator}",
            "value": float(value),
        },
        "target": {
            "fraction": f"{target.numerator}/{target.denominator}",
            "value": float(target),
        },
        "absolute_gap": {
            "fraction": f"{abs_gap.numerator}/{abs_gap.denominator}",
            "value": float(abs_gap),
        },
        "relative_gap": {
            "fraction": f"{rel_gap.numerator}/{rel_gap.denominator}",
            "value": float(rel_gap),
        },
        "pass_gate_rel_gap_le_0p15": float(rel_gap) <= 0.15,
        "replay_hash": _sha(replay_payload),
    }


def run_ablation(policy_file: Path | None = None) -> list[dict[str, Any]]:
    bundle = load_policy_bundle(policy_file)
    validate_policy_bundle(bundle)
    return [run_policy(p["policy_id"], policy_file) for p in bundle["policies"]]


def _render_markdown(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "# ALPHA-001 Policy Results\n\nNo rows produced.\n"

    lines = [
        "# ALPHA-001 Policy Results",
        "",
        "Target: CODATA-2022 alpha at Q->0",
        "",
        "| Policy ID | Candidate | Relative gap | Gate (<=15%) | Policy checksum | Replay hash |",
        "|---|---:|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {pid} | {val:.12f} | {gap:.2%} | {gate} | `{pch}` | `{rch}` |".format(
                pid=row["policy_id"],
                val=row["candidate"]["value"],
                gap=row["relative_gap"]["value"],
                gate="PASS" if row["pass_gate_rel_gap_le_0p15"] else "FAIL",
                pch=row["policy_checksum"][:16],
                rch=row["replay_hash"][:16],
            )
        )

    passed = sum(1 for row in rows if row["pass_gate_rel_gap_le_0p15"])
    best = min(rows, key=lambda row: row["relative_gap"]["value"])

    lines.extend(
        [
            "",
            "## Governance",
            "- Policies are loaded from `calc/alpha_policies.json`.",
            "- Policies are predeclared and evaluated in file order (no output-driven selection).",
            "- No fitted attenuation parameters are allowed in the bundle.",
            "- Replay hashes are deterministic for identical policy + target inputs.",
            "",
            "## No-Fit Declaration",
            "This artifact is a frozen policy comparison only. It is not a parameter fit.",
            "",
            "## Pass/Fail Summary",
            f"- Passing rows (relative gap <= 15%): {passed}/{len(rows)}",
            (
                f"- Best row: `{best['policy_id']}` "
                f"(candidate={best['candidate']['value']:.12f}, "
                f"relative gap={best['relative_gap']['value']:.2%})"
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="ALPHA-001 policy estimator")
    parser.add_argument("--policy-id", help="Run one predeclared policy id")
    parser.add_argument("--ablation", action="store_true", help="Run all policies")
    parser.add_argument("--list-policies", action="store_true", help="List policy ids")
    parser.add_argument("--policy-file", type=Path, default=POLICY_FILE_DEFAULT)
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    parser.add_argument(
        "--write-sources",
        action="store_true",
        help="Write `sources/alpha_policy_results.json` and `.md` (ablation mode)",
    )
    args = parser.parse_args()

    if args.list_policies:
        for pid in predeclared_policy_ids(args.policy_file):
            print(pid)
        return

    if args.policy_id:
        payload = run_policy(args.policy_id, args.policy_file)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
            return
        print(
            f"{payload['policy_id']}: "
            f"alpha={payload['candidate']['value']:.12f}, "
            f"rel_gap={payload['relative_gap']['value']:.2%}, "
            f"replay_hash={payload['replay_hash'][:16]}..."
        )
        return

    rows = run_ablation(args.policy_file)
    if args.write_sources:
        OUT_JSON.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUT_MD.write_text(_render_markdown(rows), encoding="utf-8")
        print(f"Wrote {OUT_JSON}")
        print(f"Wrote {OUT_MD}")
        return

    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return

    for row in rows:
        print(
            f"{row['policy_id']}: alpha={row['candidate']['value']:.12f}, "
            f"rel_gap={row['relative_gap']['value']:.2%}, "
            f"replay_hash={row['replay_hash'][:16]}..."
        )


if __name__ == "__main__":
    main()


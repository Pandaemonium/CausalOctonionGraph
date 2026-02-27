"""
RFC-037 Avenue 7 scaffold: coupling-ratio Weinberg observable.

This module evaluates predeclared discrete coupling proxies and computes
    sin^2(theta_W) = g'^2 / (g^2 + g'^2)
without output-driven policy selection.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
POLICY_FILE_DEFAULT = Path(__file__).with_name("weinberg_coupling_policies.json")
OUT_JSON = ROOT / "sources" / "weinberg_coupling_ratio_results.json"
OUT_MD = ROOT / "sources" / "weinberg_coupling_ratio_results.md"


def locked_discrete_observables() -> Dict[str, int]:
    """
    Locked integer observables from the current weak-mixing mask formalization.

    These correspond to Lean-proven mask cardinalities:
      u1_card = 2, weak_card = 3, ew_card = 4, overlap = 1.
    """
    u1_card = 2
    weak_card = 3
    ew_card = 4
    overlap = 1
    obs = {
        "u1_card": u1_card,
        "weak_card": weak_card,
        "ew_card": ew_card,
        "u1_weak_overlap_card": overlap,
        "exclusive_u1_card": u1_card - overlap,
        "weak_exclusive_card": weak_card - overlap,
        "ew_minus_u1_card": ew_card - u1_card,
    }
    if any(v < 0 for v in obs.values()):
        raise ValueError(f"invalid locked observables: {obs}")
    return obs


def observables_checksum(observables: Dict[str, int]) -> str:
    return hashlib.sha256(
        json.dumps(observables, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _policy_checksum(policy: Dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(policy, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load_policy_bundle(policy_file: Path | None = None) -> Dict[str, object]:
    path = policy_file or POLICY_FILE_DEFAULT
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def predeclared_policy_ids(policy_file: Path | None = None) -> List[str]:
    bundle = load_policy_bundle(policy_file)
    return [str(p["policy_id"]) for p in bundle["policies"]]


def _resolve_source(source_key: str, obs: Dict[str, int]) -> float:
    if source_key not in obs:
        available = ", ".join(sorted(obs.keys()))
        raise KeyError(f"unknown source key '{source_key}'. available: {available}")
    return float(obs[source_key])


def validate_policy_bundle(bundle: Dict[str, object]) -> None:
    obs = locked_discrete_observables()
    declared_checksum = str(bundle["observables_checksum"])
    computed_checksum = observables_checksum(obs)
    if declared_checksum != computed_checksum:
        raise ValueError(
            "policy bundle observables checksum mismatch locked weak-mixing observables"
        )

    for p in bundle["policies"]:
        _resolve_source(str(p["gprime_sq_source"]), obs)
        _resolve_source(str(p["g_sq_source"]), obs)


def coupling_ratio(gprime_sq: float, g_sq: float) -> float:
    denom = gprime_sq + g_sq
    if denom <= 0:
        raise ValueError(f"non-positive denominator: g'^2={gprime_sq}, g^2={g_sq}")
    return gprime_sq / denom


def run_policy(policy_id: str, policy_file: Path | None = None) -> Dict[str, object]:
    bundle = load_policy_bundle(policy_file)
    validate_policy_bundle(bundle)
    obs = locked_discrete_observables()
    target = float(bundle["target"]["sin2_theta_w"])

    selected = None
    for p in bundle["policies"]:
        if p["policy_id"] == policy_id:
            selected = p
            break
    if selected is None:
        available = ", ".join(predeclared_policy_ids(policy_file))
        raise KeyError(f"unknown policy_id '{policy_id}'. available: {available}")

    gprime_sq = _resolve_source(str(selected["gprime_sq_source"]), obs)
    g_sq = _resolve_source(str(selected["g_sq_source"]), obs)
    value = coupling_ratio(gprime_sq, g_sq)

    return {
        "rfc": "RFC-037",
        "avenue": "A7",
        "target_scale": bundle["target"]["scale"],
        "target_sin2_theta_w": target,
        "policy_id": selected["policy_id"],
        "policy_description": selected["description"],
        "policy_checksum": _policy_checksum(selected),
        "observables_checksum": observables_checksum(obs),
        "gprime_sq_source": selected["gprime_sq_source"],
        "g_sq_source": selected["g_sq_source"],
        "gprime_sq": gprime_sq,
        "g_sq": g_sq,
        "sin2_theta_w_obs": value,
        "gap_from_target": value - target,
    }


def run_all_policies(policy_file: Path | None = None) -> List[Dict[str, object]]:
    bundle = load_policy_bundle(policy_file)
    return [run_policy(str(p["policy_id"]), policy_file) for p in bundle["policies"]]


def best_row_by_abs_gap(rows: List[Dict[str, object]]) -> Dict[str, object] | None:
    if not rows:
        return None
    return min(rows, key=lambda r: abs(float(r["gap_from_target"])))


def render_markdown(rows: List[Dict[str, object]]) -> str:
    if not rows:
        return "# RFC-037 Avenue 7 Coupling-Ratio Results\n\nNo rows generated.\n"

    target = rows[0]["target_sin2_theta_w"]
    scale = rows[0]["target_scale"]
    best = best_row_by_abs_gap(rows)

    lines = [
        "# RFC-037 Avenue 7 Coupling-Ratio Results",
        "",
        f"Target: sin^2(theta_W) = {target:.8f} at scale {scale}",
        "",
        "| Policy ID | g'^2 source | g^2 source | sin^2(theta_W)_obs | Gap from target | Policy checksum |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {pid} | {gps} | {gs} | {val:.8f} | {gap:+.8f} | `{chk}` |".format(
                pid=row["policy_id"],
                gps=row["gprime_sq_source"],
                gs=row["g_sq_source"],
                val=row["sin2_theta_w_obs"],
                gap=row["gap_from_target"],
                chk=str(row["policy_checksum"])[:16],
            )
        )

    if best is not None:
        lines.extend(
            [
                "",
                "Best Avenue-7 row by absolute gap:",
                f"- `{best['policy_id']}` with sin^2(theta_W)={best['sin2_theta_w_obs']:.8f}, gap={best['gap_from_target']:+.8f}",
            ]
        )

    lines.extend(
        [
            "",
            "## Governance",
            "- Policies are predeclared in `calc/weinberg_coupling_policies.json`.",
            "- Coupling proxies are fixed to locked weak-mixing observables before evaluation.",
            "- No output-driven policy selection is applied.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(rows: List[Dict[str, object]]) -> None:
    payload = {
        "rfc": "RFC-037",
        "avenue": "A7",
        "rows": rows,
        "best_by_abs_gap": best_row_by_abs_gap(rows),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(rows), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="RFC-037 Avenue 7 coupling-ratio scan")
    parser.add_argument(
        "--policy-id",
        help="Run a single predeclared policy ID.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON to stdout.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Do not write sources artifacts.",
    )
    args = parser.parse_args()

    if args.policy_id:
        row = run_policy(args.policy_id)
        if args.json:
            print(json.dumps(row, indent=2, sort_keys=True))
        else:
            print(
                f"{row['policy_id']}: sin2={row['sin2_theta_w_obs']:.8f}, "
                f"gap={row['gap_from_target']:+.8f}"
            )
        return

    rows = run_all_policies()
    if not args.no_write:
        write_artifacts(rows)
        print(f"Wrote {OUT_JSON}")
        print(f"Wrote {OUT_MD}")
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

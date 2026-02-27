"""
ALPHA-001 helper: select a predeclared alpha policy row and emit alpha_em proxy.

This is a thin wrapper over `estimate_alpha_from_policy.py` so downstream
pipelines can request a single candidate row deterministically.
"""

from __future__ import annotations

import argparse
import json

try:
    from calc.estimate_alpha_from_policy import run_ablation, run_policy
except ModuleNotFoundError:  # direct script execution from repo root
    from estimate_alpha_from_policy import run_ablation, run_policy


def estimate_alpha_em(policy_id: str | None = None) -> dict:
    if policy_id is not None:
        row = run_policy(policy_id)
    else:
        rows = run_ablation()
        row = min(rows, key=lambda r: r["relative_gap"]["value"])

    return {
        "claim_id": "ALPHA-001",
        "mode": "policy_locked_proxy",
        "policy_id": row["policy_id"],
        "alpha_em_candidate": row["candidate"]["value"],
        "relative_gap_to_target": row["relative_gap"]["value"],
        "policy_checksum": row["policy_checksum"],
        "replay_hash": row["replay_hash"],
        "no_fit": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate alpha_em from frozen ALPHA policies")
    parser.add_argument("--policy-id", help="Use this predeclared policy_id")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = estimate_alpha_em(args.policy_id)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    print(
        f"{payload['policy_id']}: alpha_em={payload['alpha_em_candidate']:.12f}, "
        f"rel_gap={payload['relative_gap_to_target']:.2%}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

"""
Discrete scale-bridge utilities for RFC-029 H1 (UV boundary + running).

This module intentionally uses predeclared policies and deterministic maps only.
No fit/search is performed here.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List

BRIDGE_POLICY_FILE_DEFAULT = Path(__file__).with_name("weinberg_h1_bridge_policies.json")


def apply_discrete_running(uv_value: float, steps: int, attenuation: float) -> float:
    """
    Apply a discrete running map:
        value_ref = uv_value * attenuation ^ steps

    Constraints:
      - steps >= 0
      - 0 < attenuation <= 1
    """
    if steps < 0:
        raise ValueError("steps must be >= 0")
    if not (0.0 < attenuation <= 1.0):
        raise ValueError("attenuation must satisfy 0 < attenuation <= 1")
    return uv_value * (attenuation ** steps)


def required_attenuation_for_target(uv_value: float, target_value: float, steps: int) -> float:
    """
    Compute attenuation needed to hit target exactly in 'steps' updates:
        attenuation = (target/uv)^(1/steps)

    Only for diagnostics; not used for policy selection.
    """
    if steps <= 0:
        raise ValueError("steps must be > 0")
    if uv_value <= 0 or target_value <= 0:
        raise ValueError("uv_value and target_value must be > 0")
    return (target_value / uv_value) ** (1.0 / steps)


def load_bridge_policy_bundle(path: Path | None = None) -> Dict[str, object]:
    policy_path = path or BRIDGE_POLICY_FILE_DEFAULT
    with policy_path.open("r", encoding="utf-8") as f:
        bundle = json.load(f)
    return bundle


def bridge_policy_checksum(policy: Dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(policy, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def validate_bridge_policy_bundle(bundle: Dict[str, object]) -> None:
    if "target" not in bundle:
        raise ValueError("missing 'target' in bridge policy bundle")
    if "policies" not in bundle:
        raise ValueError("missing 'policies' in bridge policy bundle")
    for policy in bundle["policies"]:
        for key in ("policy_id", "description", "steps", "attenuation"):
            if key not in policy:
                raise ValueError(f"bridge policy missing key: {key}")
        apply_discrete_running(1.0, int(policy["steps"]), float(policy["attenuation"]))


def predeclared_bridge_policy_ids(path: Path | None = None) -> List[str]:
    bundle = load_bridge_policy_bundle(path)
    validate_bridge_policy_bundle(bundle)
    return [policy["policy_id"] for policy in bundle["policies"]]


def run_bridge_for_value(
    uv_value: float,
    uv_policy_id: str,
    path: Path | None = None,
) -> List[Dict[str, object]]:
    """
    Apply all predeclared bridge policies to one UV input value.
    """
    bundle = load_bridge_policy_bundle(path)
    validate_bridge_policy_bundle(bundle)
    target = float(bundle["target"]["sin2_theta_w"])
    scale = bundle["target"]["scale"]

    out: List[Dict[str, object]] = []
    for policy in bundle["policies"]:
        steps = int(policy["steps"])
        attenuation = float(policy["attenuation"])
        bridged = apply_discrete_running(uv_value, steps, attenuation)
        out.append(
            {
                "uv_policy_id": uv_policy_id,
                "bridge_policy_id": policy["policy_id"],
                "bridge_policy_description": policy["description"],
                "bridge_policy_checksum": bridge_policy_checksum(policy),
                "steps": steps,
                "attenuation": attenuation,
                "target_scale": scale,
                "target_sin2_theta_w": target,
                "sin2_theta_w_bridged": bridged,
                "gap_from_target": bridged - target,
            }
        )
    return out


def run_bridge_grid(
    h2_rows: List[Dict[str, object]],
    path: Path | None = None,
) -> List[Dict[str, object]]:
    """
    Apply all predeclared bridge policies to all H2 rows.
    """
    out: List[Dict[str, object]] = []
    for row in h2_rows:
        uv_value = float(row["observable"]["sin2_theta_w_obs"])
        uv_policy_id = str(row["policy_id"])
        out.extend(run_bridge_for_value(uv_value, uv_policy_id, path))
    return out


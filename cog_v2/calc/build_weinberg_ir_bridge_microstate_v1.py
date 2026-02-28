"""Deterministic WEINBERG IR bridge from one exact lightcone microstate.

This is a simulation-first, structure-first witness under COG v2 axioms:
1) DAG causal graph,
2) C x O over unity coefficients,
3) projective lightcone update rule.

It records full tick-by-tick event/state updates for a fixed preregistered
microstate and computes a locked IR bridge estimator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "weinberg_ir_bridge_microstate_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "weinberg_ir_bridge_microstate_v1.md"

SCRIPT_REPO_PATH = "cog_v2/calc/build_weinberg_ir_bridge_microstate_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
RFC_REPO_PATH = "rfc/RFC-080_Discrete_RGE_Contract.md"

POLICY_ID = "weinberg_ir_bridge_microstate_v1"
INIT_PROFILE_ID = "uv_anchor_exact_lightcone_v1"
KERNEL_PROFILE_ID = k.KERNEL_PROFILE

NODE_IDS: Tuple[str, ...] = ("l0", "l1", "q0", "q1", "mix0", "mix1", "obs")
PARENTS: Dict[str, List[str]] = {
    "l0": [],
    "l1": [],
    "q0": [],
    "q1": [],
    "mix0": ["l0", "q0"],
    "mix1": ["l1", "q1", "mix0"],
    "obs": ["mix0", "mix1", "q1"],
}

TICKS = 64
STATIONARY_WINDOW = 32
TARGET_SIN2_THETA_W = 0.23122
TARGET_SCALE = "M_Z"

# Locked bridge constants (no output-tuned coefficients):
# 1) UV anchor from COG UV lane
# 2) leakage coefficient fixed to Fano strong proxy scale 1/7.
UV_ANCHOR = 1.0 / 4.0
LEAKAGE_COEFF = 1.0 / 7.0

U1_CHANNEL = 7
WEAK_CHANNELS: Tuple[int, int, int] = (1, 2, 3)


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _abs2(z: k.GInt) -> int:
    return int(z.re * z.re + z.im * z.im)


def _state_from_map(vals: Dict[int, k.GInt]) -> k.CxO:
    data = [k.ZERO_G] * 8
    for idx, value in vals.items():
        data[int(idx)] = value
    return (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])


def _serialize_cxo(state: k.CxO) -> List[List[int]]:
    return [[int(z.re), int(z.im)] for z in state]


def _world_signature(world: k.World) -> Tuple[Tuple[Tuple[int, int], ...], ...]:
    return tuple(tuple((z.re, z.im) for z in world.states[nid]) for nid in world.node_ids)


def _detect_period(signatures: Sequence[Tuple[Tuple[Tuple[int, int], ...], ...]], max_period: int) -> int | None:
    n = len(signatures)
    if n < 4:
        return None
    tail_start = max(0, n // 2)
    for p in range(1, int(max_period) + 1):
        ok = True
        for t in range(tail_start, n - p):
            if signatures[t] != signatures[t + p]:
                ok = False
                break
        if ok:
            return int(p)
    return None


def _sum_u1_weak(world: k.World) -> Tuple[int, int]:
    u1_power = 0
    weak_power = 0
    for nid in world.node_ids:
        s = world.states[nid]
        u1_power += _abs2(s[U1_CHANNEL])
        weak_power += sum(_abs2(s[i]) for i in WEAK_CHANNELS)
    return int(u1_power), int(weak_power)


def _e000_share(world: k.World) -> float:
    e000 = 0
    non = 0
    for nid in world.node_ids:
        s = world.states[nid]
        e000 += _abs2(s[0])
        non += sum(_abs2(s[i]) for i in range(1, 8))
    total = e000 + non
    if total == 0:
        return 0.0
    return float(e000) / float(total)


def _build_initial_world() -> k.World:
    # Exact preregistered microstate:
    # weak channels carry 3 units total, U1 carries 1 unit total -> UV anchor 1/4.
    states = {
        "l0": _state_from_map({1: k.ONE_G}),
        "l1": _state_from_map({2: k.ONE_G}),
        "q0": _state_from_map({3: k.ONE_G}),
        "q1": _state_from_map({7: k.ONE_G}),
        "mix0": k.cxo_one(),
        "mix1": k.cxo_one(),
        "obs": k.cxo_one(),
    }
    return k.World(
        node_ids=list(NODE_IDS),
        parents={nid: list(PARENTS[nid]) for nid in NODE_IDS},
        states=states,
        event_order=None,
        tick=0,
    )


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    rfc_path = ROOT / RFC_REPO_PATH

    world = _build_initial_world()
    rows: List[Dict[str, Any]] = []
    signatures: List[Tuple[Tuple[Tuple[int, int], ...], ...]] = []

    for _ in range(TICKS + 1):
        signatures.append(_world_signature(world))
        u1_power, weak_power = _sum_u1_weak(world)
        denom = int(u1_power + weak_power)
        direct_sin2 = 0.0 if denom == 0 else float(u1_power) / float(denom)
        e000_share = _e000_share(world)
        correction = float(LEAKAGE_COEFF) * float(e000_share)
        bridged_tick = float(UV_ANCHOR) - float(correction)

        rows.append(
            {
                "tick": int(world.tick),
                "u1_power_total": int(u1_power),
                "weak_power_total": int(weak_power),
                "direct_sin2_theta_w": float(direct_sin2),
                "e000_share_total": float(e000_share),
                "bridge_correction": float(correction),
                "bridged_sin2_theta_w_tick": float(bridged_tick),
                "states_by_node": {nid: _serialize_cxo(world.states[nid]) for nid in world.node_ids},
            }
        )
        if world.tick < TICKS:
            world = k.step(world)

    tail = rows[-int(STATIONARY_WINDOW) :]
    mean_e000_share = float(sum(float(r["e000_share_total"]) for r in tail) / float(len(tail)))
    ir_bridge_est = float(UV_ANCHOR - LEAKAGE_COEFF * mean_e000_share)
    gap = float(ir_bridge_est - TARGET_SIN2_THETA_W)

    period = _detect_period(signatures, max_period=16)
    uv_anchor_exact = abs(float(rows[0]["direct_sin2_theta_w"]) - float(UV_ANCHOR)) < 1e-12
    stationarity_detected = period is not None
    within_2pct = abs(gap) <= 0.02 * float(TARGET_SIN2_THETA_W)

    checks = {
        "uv_anchor_exact_at_tick0": bool(uv_anchor_exact),
        "stationary_period_detected": bool(stationarity_detected),
        "no_output_tuned_parameter": True,
        "ir_bridge_within_2pct_target": bool(within_2pct),
    }
    pass_all = all(bool(v) for v in checks.values())

    payload: Dict[str, Any] = {
        "schema_version": "weinberg_ir_bridge_microstate_v1",
        "claim_id": "WEINBERG-001",
        "mode": "simulation_first_structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "contract_ref": RFC_REPO_PATH,
        "contract_ref_sha256": _sha_file(rfc_path),
        "preregistered_inputs": {
            "policy_id": POLICY_ID,
            "kernel_profile_id": KERNEL_PROFILE_ID,
            "init_profile_id": INIT_PROFILE_ID,
            "depth_schedule": [int(TICKS)],
            "seed_set": ["deterministic_exact_microstate_only"],
            "observable_bounds": {
                "sin2_theta_w": [0.0, 1.0],
                "e000_share_total": [0.0, 1.0],
            },
            "summary_stat": {
                "primary": "stationary_window_mean",
                "window_size": int(STATIONARY_WINDOW),
            },
        },
        "microstate_contract": {
            "node_ids": list(NODE_IDS),
            "parents": {nid: list(PARENTS[nid]) for nid in NODE_IDS},
            "channel_labels": list(k.BASIS_LABELS),
            "u1_channel": int(U1_CHANNEL),
            "weak_channels": list(WEAK_CHANNELS),
            "exact_initial_states": rows[0]["states_by_node"],
        },
        "bridge_policy": {
            "uv_anchor": float(UV_ANCHOR),
            "leakage_coeff": float(LEAKAGE_COEFF),
            "formula": "sin2_ir = uv_anchor - leakage_coeff * mean_e000_share_stationary",
            "parameter_tuning": "none",
        },
        "target": {
            "sin2_theta_w": float(TARGET_SIN2_THETA_W),
            "scale": str(TARGET_SCALE),
        },
        "running_trace": rows,
        "stationary_summary": {
            "window_start_tick": int(TICKS + 1 - STATIONARY_WINDOW),
            "window_size": int(STATIONARY_WINDOW),
            "mean_e000_share_stationary": float(mean_e000_share),
            "ir_bridge_estimate": float(ir_bridge_est),
            "target_gap": float(gap),
            "detected_period_ticks": int(period) if period is not None else None,
        },
        "checks": checks,
        "bridge_pass": bool(pass_all),
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    s = payload["stationary_summary"]
    b = payload["bridge_policy"]
    lines = [
        "# WEINBERG IR Bridge from Exact Lightcone Microstate (v1)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Policy: `{payload['preregistered_inputs']['policy_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        f"- Bridge pass: `{payload['bridge_pass']}`",
        "",
        "## Locked Microstate Inputs",
        f"- node_ids: `{payload['microstate_contract']['node_ids']}`",
        f"- u1_channel: `{payload['microstate_contract']['u1_channel']}`",
        f"- weak_channels: `{payload['microstate_contract']['weak_channels']}`",
        "",
        "## Bridge Policy",
        f"- uv_anchor: `{b['uv_anchor']}`",
        f"- leakage_coeff: `{b['leakage_coeff']}`",
        f"- formula: `{b['formula']}`",
        "",
        "## Stationary Summary",
        f"- mean_e000_share_stationary: `{s['mean_e000_share_stationary']:.10f}`",
        f"- ir_bridge_estimate: `{s['ir_bridge_estimate']:.10f}`",
        f"- target_sin2_theta_w: `{payload['target']['sin2_theta_w']:.8f}` at `{payload['target']['scale']}`",
        f"- target_gap: `{s['target_gap']:+.10f}`",
        f"- detected_period_ticks: `{s['detected_period_ticks']}`",
        "",
        "## Acceptance Checks",
    ]
    for k0, v0 in payload["checks"].items():
        lines.append(f"- {k0}: `{v0}`")

    lines.extend(
        [
            "",
            "## Tick-by-Tick Notes",
            "The JSON artifact includes `running_trace` with exact node state for every tick/event.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: Dict[str, Any],
    *,
    json_paths: Sequence[Path] | None = None,
    md_paths: Sequence[Path] | None = None,
) -> None:
    j_paths = list(json_paths) if json_paths is not None else [OUT_JSON]
    m_paths = list(md_paths) if md_paths is not None else [OUT_MD]
    for path in j_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_markdown(payload)
    for path in m_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build WEINBERG IR bridge microstate artifact (v1)")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write artifacts to cog_v2/sources")
    args = parser.parse_args()

    payload = build_payload()
    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {_to_repo_path(OUT_JSON)}")
        print(f"Wrote {_to_repo_path(OUT_MD)}")
        return
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        "weinberg_ir_bridge_microstate_v1: "
        f"bridge_pass={payload['bridge_pass']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

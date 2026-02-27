"""
calc/xor_full_lightcone_engine.py

Phase 1-2 runtime:
1) canonical full past-lightcone contributor fold per tick,
2) fixed predetermined cone (no spawn),
3) deterministic ordering and replay hash.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from calc.xor_charge_sign_interaction_matrix import (
    is_energy_exchange_locked_xor,
    next_state_v2_xor,
    temporal_commit,
    u1_charge,
)
from calc.xor_furey_ideals import (
    GI,
    StateGI,
    furey_dual_electron_doubled,
    furey_electron_doubled,
    ideal_sd_basis_doubled,
    ideal_su_basis_doubled,
    state_basis,
    vacuum_doubled,
)


def _require_int(name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    return int(value)


def _sha(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _to_base8(n: int) -> str:
    sign = "-" if n < 0 else ""
    return sign + format(abs(n), "o")


def _state_to_base8(state: StateGI) -> List[List[str]]:
    return [[_to_base8(re), _to_base8(im)] for (re, im) in state]


def _depth_range(min_pos0: int, max_pos0: int, depth: int) -> range:
    return range(min_pos0 - depth, max_pos0 + depth + 1)


def _can_reach(src_depth: int, src_pos: int, dst_depth: int, dst_pos: int) -> bool:
    dt = dst_depth - src_depth
    if dt <= 0:
        return False
    dx = abs(dst_pos - src_pos)
    if dx > dt:
        return False
    return ((dt - dx) % 2) == 0


def _background_state(background_id: str) -> StateGI:
    if background_id == "vacuum_doubled":
        return vacuum_doubled()
    if background_id == "identity_e0":
        return state_basis(0, (1, 0))
    raise KeyError(f"unknown background_id: {background_id}")


def _motif_state(motif_id: str) -> StateGI:
    motifs: Dict[str, StateGI] = {
        "furey_electron_doubled": furey_electron_doubled(),
        "furey_dual_electron_doubled": furey_dual_electron_doubled(),
        "identity_e0": state_basis(0, (1, 0)),
    }
    motifs.update(ideal_su_basis_doubled())
    motifs.update(ideal_sd_basis_doubled())
    if motif_id not in motifs:
        raise KeyError(f"unknown motif_id: {motif_id}")
    return motifs[motif_id]


def _ordered_contributors(
    history: List[Dict[int, StateGI]],
    dst_depth: int,
    dst_pos: int,
) -> List[Tuple[int, int, StateGI]]:
    out: List[Tuple[int, int, StateGI]] = []
    # Canonical order: topoDepth ascending, then node id (position) ascending.
    for src_depth, slice_map in enumerate(history):
        for src_pos in sorted(slice_map.keys()):
            if _can_reach(src_depth=src_depth, src_pos=src_pos, dst_depth=dst_depth, dst_pos=dst_pos):
                out.append((src_depth, src_pos, slice_map[src_pos]))
    return out


def _initial_slice(
    min_pos0: int,
    max_pos0: int,
    left_state: StateGI,
    right_state: StateGI,
    background: StateGI,
) -> Dict[int, StateGI]:
    out: Dict[int, StateGI] = {}
    for pos in _depth_range(min_pos0, max_pos0, 0):
        out[pos] = background
    out[min_pos0] = left_state
    out[max_pos0] = right_state
    return out


def _simulate_raw(
    *,
    depth_horizon: int,
    min_pos0: int,
    max_pos0: int,
    left_state: StateGI,
    right_state: StateGI,
    background: StateGI,
) -> Dict[str, Any]:
    depth_horizon = _require_int("depth_horizon", depth_horizon)
    min_pos0 = _require_int("min_pos0", min_pos0)
    max_pos0 = _require_int("max_pos0", max_pos0)
    if depth_horizon < 0:
        raise ValueError("depth_horizon must be >= 0")
    if min_pos0 >= max_pos0:
        raise ValueError("min_pos0 must be < max_pos0")

    slices: List[Dict[int, StateGI]] = []
    telemetry: List[Dict[int, Dict[str, Any]]] = []

    d0 = _initial_slice(min_pos0, max_pos0, left_state, right_state, background)
    slices.append(d0)
    telemetry.append(
        {
            pos: {
                "contributor_count": 0,
                "interaction_observed": False,
                "u1_charge": u1_charge(st),
            }
            for pos, st in d0.items()
        }
    )

    for depth in range(depth_horizon):
        prev = slices[depth]
        next_depth = depth + 1
        next_slice: Dict[int, StateGI] = {}
        next_meta: Dict[int, Dict[str, Any]] = {}

        for pos in _depth_range(min_pos0, max_pos0, next_depth):
            current_state = prev.get(pos, background)
            contributors = _ordered_contributors(slices, dst_depth=next_depth, dst_pos=pos)
            msgs = [st for (_, _, st) in contributors]
            next_state = next_state_v2_xor(current_state, msgs)
            next_slice[pos] = next_state
            next_meta[pos] = {
                "contributor_count": len(msgs),
                "interaction_observed": bool(is_energy_exchange_locked_xor(msgs)),
                "u1_charge": u1_charge(next_state),
            }

        slices.append(next_slice)
        telemetry.append(next_meta)

    return {
        "slices_raw": slices,
        "telemetry_raw": telemetry,
    }


def simulate_full_lightcone(
    *,
    channel_id: str,
    depth_horizon: int,
    initial_edge_distance: int,
    left_motif_id: str,
    right_motif_id: str,
    background_id: str = "vacuum_doubled",
    left_precommit_ticks: int = 0,
    right_precommit_ticks: int = 0,
) -> Dict[str, Any]:
    depth_horizon = _require_int("depth_horizon", depth_horizon)
    initial_edge_distance = _require_int("initial_edge_distance", initial_edge_distance)
    left_precommit_ticks = _require_int("left_precommit_ticks", left_precommit_ticks)
    right_precommit_ticks = _require_int("right_precommit_ticks", right_precommit_ticks)
    if initial_edge_distance < 1:
        raise ValueError("initial_edge_distance must be >= 1")
    min_pos0 = 0
    max_pos0 = initial_edge_distance
    left_state = _motif_state(left_motif_id)
    right_state = _motif_state(right_motif_id)
    background = _background_state(background_id)
    if left_precommit_ticks < 0 or right_precommit_ticks < 0:
        raise ValueError("precommit ticks must be >= 0")
    for _ in range(left_precommit_ticks):
        left_state = temporal_commit(left_state)
    for _ in range(right_precommit_ticks):
        right_state = temporal_commit(right_state)

    raw = _simulate_raw(
        depth_horizon=depth_horizon,
        min_pos0=min_pos0,
        max_pos0=max_pos0,
        left_state=left_state,
        right_state=right_state,
        background=background,
    )

    slices_raw: List[Dict[int, StateGI]] = raw["slices_raw"]
    telemetry_raw: List[Dict[int, Dict[str, Any]]] = raw["telemetry_raw"]

    depth_rows: List[Dict[str, Any]] = []
    csv_rows: List[Dict[str, Any]] = []
    for depth, (slice_map, meta_map) in enumerate(zip(slices_raw, telemetry_raw)):
        positions = sorted(slice_map.keys())
        row = {
            "depth": depth,
            "min_pos": positions[0],
            "max_pos": positions[-1],
            "node_count": len(positions),
            "interaction_observed_count": sum(1 for p in positions if bool(meta_map[p]["interaction_observed"])),
            "max_contributor_count": max(int(meta_map[p]["contributor_count"]) for p in positions),
        }
        depth_rows.append(row)
        for pos in positions:
            st = slice_map[pos]
            meta = meta_map[pos]
            csv_rows.append(
                {
                    "depth": depth,
                    "pos": pos,
                    "contributor_count": int(meta["contributor_count"]),
                    "interaction_observed": bool(meta["interaction_observed"]),
                    "u1_charge_base8": _to_base8(int(meta["u1_charge"])),
                    "state_base8": json.dumps(_state_to_base8(st), separators=(",", ":")),
                }
            )

    serializable = {
        "schema_version": "xor_full_lightcone_engine_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "channel_id": channel_id,
        "kernel": {
            "interaction_scope": "full_past_lightcone_all_contributors",
            "ordering": "topoDepth_then_position",
            "no_spawn": True,
            "full_lightcone_preconditioned": True,
            "update_rule": "next_state_v2_xor",
        },
        "config": {
            "depth_horizon": depth_horizon,
            "initial_edge_distance": initial_edge_distance,
            "min_pos0": min_pos0,
            "max_pos0": max_pos0,
            "left_motif_id": left_motif_id,
            "right_motif_id": right_motif_id,
            "background_id": background_id,
            "left_precommit_ticks": left_precommit_ticks,
            "right_precommit_ticks": right_precommit_ticks,
        },
        "depth_summary": depth_rows,
        "csv_rows": csv_rows,
        # Deterministic payload for replay hash excludes generated_at_utc.
        "slices_base8": [
            {str(pos): _state_to_base8(slice_map[pos]) for pos in sorted(slice_map.keys())}
            for slice_map in slices_raw
        ],
    }

    deterministic_payload = dict(serializable)
    deterministic_payload.pop("generated_at_utc", None)
    serializable["replay_hash"] = _sha(deterministic_payload)
    return serializable


def run_builtin_full_lightcone_cases(
    *,
    depth_horizon: int = 12,
    initial_edge_distance: int = 5,
) -> Dict[str, Any]:
    ee = simulate_full_lightcone(
        channel_id="electron_electron",
        depth_horizon=depth_horizon,
        initial_edge_distance=initial_edge_distance,
        left_motif_id="furey_electron_doubled",
        right_motif_id="furey_electron_doubled",
    )
    ep = simulate_full_lightcone(
        channel_id="electron_positron",
        depth_horizon=depth_horizon,
        initial_edge_distance=initial_edge_distance,
        left_motif_id="furey_electron_doubled",
        right_motif_id="furey_dual_electron_doubled",
    )
    return {
        "schema_version": "xor_full_lightcone_cases_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "depth_horizon": depth_horizon,
        "initial_edge_distance": initial_edge_distance,
        "cases": {
            "electron_electron": ee,
            "electron_positron": ep,
        },
    }


def write_full_lightcone_artifacts(
    dataset: Dict[str, Any],
    *,
    json_paths: List[Path] | None = None,
    csv_paths: List[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_full_lightcone_engine.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_full_lightcone_engine.csv")]

    for p in json_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "case_id",
        "depth",
        "pos",
        "contributor_count",
        "interaction_observed",
        "u1_charge_base8",
        "state_base8",
    ]
    rows: List[Dict[str, Any]] = []
    for case_id, payload in dataset["cases"].items():
        for row in payload["csv_rows"]:
            rows.append({"case_id": case_id, **row})

    for p in csv_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)


def main() -> int:
    data = run_builtin_full_lightcone_cases(depth_horizon=12, initial_edge_distance=5)
    write_full_lightcone_artifacts(
        data,
        json_paths=[
            Path("calc/xor_full_lightcone_engine.json"),
            Path("website/data/xor_full_lightcone_engine.json"),
        ],
        csv_paths=[
            Path("calc/xor_full_lightcone_engine.csv"),
            Path("website/data/xor_full_lightcone_engine.csv"),
        ],
    )
    print("Wrote calc/xor_full_lightcone_engine.json")
    print("Wrote calc/xor_full_lightcone_engine.csv")
    print("Wrote website/data/xor_full_lightcone_engine.json")
    print("Wrote website/data/xor_full_lightcone_engine.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
calc/xor_motif_tracker.py

Phase 1 motif-tracking utilities:
1) deterministic motif score and tie-break,
2) per-depth motif path extraction from full-lightcone runs,
3) edge-distance series between tracked motifs.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from calc.xor_furey_ideals import StateGI, furey_dual_electron_doubled, furey_electron_doubled
from calc.xor_full_lightcone_engine import run_builtin_full_lightcone_cases


def _to_base8(n: int) -> str:
    sign = "-" if n < 0 else ""
    return sign + format(abs(n), "o")


def _from_base8(s: str) -> int:
    if s.startswith("-"):
        return -int(s[1:], 8)
    return int(s, 8)


def _motif_state(motif_id: str) -> StateGI:
    if motif_id == "furey_electron_doubled":
        return furey_electron_doubled()
    if motif_id == "furey_dual_electron_doubled":
        return furey_dual_electron_doubled()
    raise KeyError(f"unknown motif_id: {motif_id}")


def _decode_state_base8(encoded: List[List[str]]) -> StateGI:
    if len(encoded) != 8:
        raise ValueError("state encoding must have 8 channels")
    out: List[Tuple[int, int]] = []
    for row in encoded:
        if len(row) != 2:
            raise ValueError("state row must be [re, im]")
        out.append((_from_base8(row[0]), _from_base8(row[1])))
    return tuple(out)  # type: ignore[return-value]


def motif_l1_distance(state: StateGI, motif: StateGI) -> int:
    total = 0
    for i in range(8):
        total += abs(state[i][0] - motif[i][0]) + abs(state[i][1] - motif[i][1])
    return total


def motif_score(state: StateGI, motif: StateGI) -> int:
    return -motif_l1_distance(state, motif)


def best_motif_position(
    *,
    depth_slice: Dict[str, List[List[str]]],
    motif: StateGI,
    side_preference: str = "left",
) -> Dict[str, Any]:
    if side_preference not in {"left", "right"}:
        raise ValueError("side_preference must be 'left' or 'right'")
    candidates: List[Tuple[int, int, bool]] = []
    for pos_s, enc in depth_slice.items():
        pos = int(pos_s)
        state = _decode_state_base8(enc)
        dist = motif_l1_distance(state, motif)
        score = -dist
        exact = dist == 0
        # Tie-break: higher score first, then side-anchored position.
        candidates.append((score, pos, exact))

    if not candidates:
        raise ValueError("depth_slice has no nodes")
    if side_preference == "left":
        candidates.sort(key=lambda row: (-row[0], row[1]))
    else:
        candidates.sort(key=lambda row: (-row[0], -row[1]))
    best_score, best_pos, best_exact = candidates[0]
    return {
        "pos": best_pos,
        "score": best_score,
        "exact_match": bool(best_exact),
    }


def track_motif_path(
    *,
    run_payload: Dict[str, Any],
    motif_id: str,
    track_id: str,
    side_preference: str = "left",
) -> List[Dict[str, Any]]:
    motif = _motif_state(motif_id)
    slices = run_payload["slices_base8"]
    out: List[Dict[str, Any]] = []
    for depth, depth_slice in enumerate(slices):
        best = best_motif_position(depth_slice=depth_slice, motif=motif, side_preference=side_preference)
        out.append(
            {
                "track_id": track_id,
                "motif_id": motif_id,
                "depth": depth,
                "pos": best["pos"],
                "score": best["score"],
                "exact_match": best["exact_match"],
            }
        )
    return out


def edge_distance_series(path_a: List[Dict[str, Any]], path_b: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if len(path_a) != len(path_b):
        raise ValueError("path lengths must match")
    out: List[Dict[str, Any]] = []
    for a, b in zip(path_a, path_b):
        if int(a["depth"]) != int(b["depth"]):
            raise ValueError("depth mismatch between paths")
        d = int(a["depth"])
        dist = abs(int(a["pos"]) - int(b["pos"]))
        out.append(
            {
                "depth": d,
                "pos_a": int(a["pos"]),
                "pos_b": int(b["pos"]),
                "edge_distance": dist,
            }
        )
    return out


def run_builtin_motif_tracking(
    *,
    depth_horizon: int = 12,
    initial_edge_distance: int = 5,
) -> Dict[str, Any]:
    cases = run_builtin_full_lightcone_cases(
        depth_horizon=depth_horizon,
        initial_edge_distance=initial_edge_distance,
    )["cases"]

    ee = cases["electron_electron"]
    ep = cases["electron_positron"]

    ee_left = track_motif_path(
        run_payload=ee,
        motif_id="furey_electron_doubled",
        track_id="ee_left_e",
        side_preference="left",
    )
    ee_right = track_motif_path(
        run_payload=ee,
        motif_id="furey_electron_doubled",
        track_id="ee_right_e",
        side_preference="right",
    )
    ee_dist = edge_distance_series(ee_left, ee_right)

    ep_left = track_motif_path(
        run_payload=ep,
        motif_id="furey_electron_doubled",
        track_id="ep_left_e",
        side_preference="left",
    )
    ep_right = track_motif_path(
        run_payload=ep,
        motif_id="furey_dual_electron_doubled",
        track_id="ep_right_p",
        side_preference="right",
    )
    ep_dist = edge_distance_series(ep_left, ep_right)

    return {
        "schema_version": "xor_motif_tracker_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "depth_horizon": depth_horizon,
        "initial_edge_distance": initial_edge_distance,
        "cases": {
            "electron_electron": {
                "track_a": ee_left,
                "track_b": ee_right,
                "distance": ee_dist,
                "final_distance": ee_dist[-1]["edge_distance"],
            },
            "electron_positron": {
                "track_a": ep_left,
                "track_b": ep_right,
                "distance": ep_dist,
                "final_distance": ep_dist[-1]["edge_distance"],
            },
        },
    }


def write_motif_tracking_artifacts(
    dataset: Dict[str, Any],
    *,
    json_paths: List[Path] | None = None,
    csv_paths: List[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_motif_tracker.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_motif_tracker.csv")]

    for p in json_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "case_id",
        "depth",
        "pos_a",
        "pos_b",
        "edge_distance",
    ]
    rows: List[Dict[str, Any]] = []
    for case_id, payload in dataset["cases"].items():
        for row in payload["distance"]:
            rows.append({"case_id": case_id, **row})

    for p in csv_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in rows:
                w.writerow(row)


def main() -> int:
    data = run_builtin_motif_tracking(depth_horizon=12, initial_edge_distance=5)
    write_motif_tracking_artifacts(
        data,
        json_paths=[
            Path("calc/xor_motif_tracker.json"),
            Path("website/data/xor_motif_tracker.json"),
        ],
        csv_paths=[
            Path("calc/xor_motif_tracker.csv"),
            Path("website/data/xor_motif_tracker.csv"),
        ],
    )
    print("Wrote calc/xor_motif_tracker.json")
    print("Wrote calc/xor_motif_tracker.csv")
    print("Wrote website/data/xor_motif_tracker.json")
    print("Wrote website/data/xor_motif_tracker.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

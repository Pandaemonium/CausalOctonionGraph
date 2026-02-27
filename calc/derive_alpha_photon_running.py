"""
Derive ALPHA running profile from full lightcone CxO simulation.

Signal definition:
  - track two electron motifs in a full predetermined cone,
  - define photon interaction events as changes in relative complex discrete phase
    (e7 channel phase bucket difference) between tracked motifs,
  - map event timing + edge distance into a dimensionless alpha proxy.

This script is deterministic and governance-locked by
calc/alpha_photon_running_conditions.json.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from calc.xor_full_lightcone_engine import simulate_full_lightcone
    from calc.xor_motif_tracker import (
        best_motif_position,
        decode_state_base8,
        edge_distance_series,
        motif_l1_distance,
    )
    from calc.xor_charge_sign_interaction_matrix import temporal_commit
    from calc.xor_furey_ideals import (
        StateGI,
        furey_dual_electron_doubled,
        furey_electron_doubled,
        state_basis,
    )
except ModuleNotFoundError:  # direct script execution fallback
    from xor_full_lightcone_engine import simulate_full_lightcone
    from xor_motif_tracker import best_motif_position, decode_state_base8, edge_distance_series, motif_l1_distance
    from xor_charge_sign_interaction_matrix import temporal_commit
    from xor_furey_ideals import (
        StateGI,
        furey_dual_electron_doubled,
        furey_electron_doubled,
        state_basis,
    )


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONDITIONS = Path(__file__).with_name("alpha_photon_running_conditions.json")
OUT_JSON = ROOT / "sources" / "alpha_photon_running.json"
OUT_CSV = ROOT / "sources" / "alpha_photon_running.csv"
OUT_MD = ROOT / "sources" / "alpha_photon_running.md"


def _sha(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _median(xs: List[float]) -> Optional[float]:
    if not xs:
        return None
    return float(statistics.median(xs))


def _mad(xs: List[float], center: float) -> Optional[float]:
    if not xs:
        return None
    return float(statistics.median(abs(x - center) for x in xs))


def _to_base8(n: int) -> str:
    sign = "-" if n < 0 else ""
    return sign + format(abs(n), "o")


def load_conditions(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_CONDITIONS
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def _assert_no_forbidden_keys(obj: Any) -> None:
    forbidden = {"attenuation", "fit_param", "fitted_param", "tuned_param"}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in forbidden:
                raise ValueError(f"Forbidden key in conditions: {k}")
            _assert_no_forbidden_keys(v)
        return
    if isinstance(obj, list):
        for v in obj:
            _assert_no_forbidden_keys(v)


def validate_conditions(data: dict[str, Any]) -> None:
    if data.get("mode") != "deterministic_full_cone_preconditioned":
        raise ValueError("mode must be deterministic_full_cone_preconditioned")
    if "target" not in data or "alpha" not in data["target"]:
        raise ValueError("target.alpha is required")
    if "signal_channel" not in data:
        raise ValueError("signal_channel is required")
    if "initial_edge_distances" not in data or not isinstance(data["initial_edge_distances"], list):
        raise ValueError("initial_edge_distances list is required")
    if "depth_horizon_rule" not in data:
        raise ValueError("depth_horizon_rule is required")
    if "phase_offsets" not in data or not isinstance(data["phase_offsets"], list) or not data["phase_offsets"]:
        raise ValueError("phase_offsets non-empty list is required")
    _assert_no_forbidden_keys(data)

    kernel = data.get("kernel", {})
    if kernel.get("interaction_scope") != "full_past_lightcone_all_contributors":
        raise ValueError("kernel.interaction_scope must be full_past_lightcone_all_contributors")
    if kernel.get("no_spawn") is not True:
        raise ValueError("kernel.no_spawn must be true")
    if kernel.get("full_lightcone_preconditioned") is not True:
        raise ValueError("kernel.full_lightcone_preconditioned must be true")

    for d0 in data["initial_edge_distances"]:
        if int(d0) < 1:
            raise ValueError("initial_edge_distances must be >= 1")
    for p in data["phase_offsets"]:
        if int(p) < 0:
            raise ValueError("phase_offsets entries must be >= 0")

    rule = data["depth_horizon_rule"]
    if rule.get("type") != "linear":
        raise ValueError("depth_horizon_rule.type must be linear")
    for key in ("slope", "intercept", "min_depth"):
        if int(rule.get(key, -1)) < 0:
            raise ValueError(f"depth_horizon_rule.{key} must be >= 0")

    mu_eff = float(data["mass_normalization"]["mu_eff"])
    if mu_eff <= 0:
        raise ValueError("mu_eff must be > 0")


def depth_horizon_for_distance(data: dict[str, Any], d0: int) -> int:
    rule = data["depth_horizon_rule"]
    slope = int(rule["slope"])
    intercept = int(rule["intercept"])
    min_depth = int(rule["min_depth"])
    return max(min_depth, slope * int(d0) + intercept)


def _phase8_from_complex_coeff(coeff: tuple[int, int]) -> int:
    """
    Map Gaussian integer (re, im) to an 8-phase bucket around the complex plane.
    Buckets increase counterclockwise.
    """
    re, im = coeff
    if re == 0 and im == 0:
        return 0
    ar = abs(re)
    ai = abs(im)
    if re >= 0 and im >= 0:
        return 1 if ai > ar else 0
    if re < 0 and im >= 0:
        return 3 if ai > ar else 4
    if re < 0 and im < 0:
        return 5 if ai > ar else 4
    # re >= 0 and im < 0
    return 7 if ai > ar else 0


def _cyclic_delta_mod(a: int, b: int, mod: int) -> int:
    d = (b - a) % mod
    return min(d, mod - d)


def _relative_phase_series(run_payload: dict[str, Any], path_a: List[dict[str, Any]], path_b: List[dict[str, Any]]) -> List[Dict[str, int]]:
    slices = run_payload["slices_base8"]
    out: List[Dict[str, int]] = []
    for row_a, row_b in zip(path_a, path_b):
        depth = int(row_a["depth"])
        if depth != int(row_b["depth"]):
            raise ValueError("path depth mismatch")
        pos_a = int(row_a["pos"])
        pos_b = int(row_b["pos"])
        st_a = decode_state_base8(slices[depth][str(pos_a)])
        st_b = decode_state_base8(slices[depth][str(pos_b)])
        phase_a = _phase8_from_complex_coeff(st_a[7])
        phase_b = _phase8_from_complex_coeff(st_b[7])
        rel = (phase_b - phase_a) % 8
        out.append(
            {
                "depth": depth,
                "phase_a": phase_a,
                "phase_b": phase_b,
                "relative_phase": rel,
            }
        )
    return out


def _phase_interaction_events(phase_rows: List[Dict[str, int]]) -> List[Dict[str, int]]:
    events: List[Dict[str, int]] = []
    if len(phase_rows) < 2:
        return events
    prev = phase_rows[0]
    for row in phase_rows[1:]:
        if int(row["relative_phase"]) != int(prev["relative_phase"]):
            events.append(
                {
                    "depth": int(row["depth"]),
                    "relative_phase_prev": int(prev["relative_phase"]),
                    "relative_phase_now": int(row["relative_phase"]),
                    "phase_jump": _cyclic_delta_mod(
                        int(prev["relative_phase"]), int(row["relative_phase"]), 8
                    ),
                }
            )
        prev = row
    return events


def _distance_map(distance_rows: List[Dict[str, int]]) -> Dict[int, int]:
    return {int(r["depth"]): int(r["edge_distance"]) for r in distance_rows}


def _alpha_samples_from_events(
    *,
    events: List[Dict[str, int]],
    distance_by_depth: Dict[int, int],
    mu_eff: float,
    depth_horizon: int,
) -> List[Dict[str, float]]:
    out: List[Dict[str, float]] = []
    if len(events) < 1:
        return out
    depths = [int(e["depth"]) for e in events]
    jump_by_depth = {int(e["depth"]): int(e["phase_jump"]) for e in events}
    for i in range(0, len(depths)):
        d_now = depths[i]
        if i == 0:
            past_gap = d_now
        else:
            past_gap = d_now - depths[i - 1]
        if i == len(depths) - 1:
            future_gap = depth_horizon - d_now
        else:
            future_gap = depths[i + 1] - d_now
        v_proxy = future_gap - past_gap
        edge_dist = int(distance_by_depth.get(d_now, 0))
        if edge_dist <= 0:
            continue
        spin_kick = int(jump_by_depth[d_now])
        alpha_hat = mu_eff * abs(float(v_proxy)) * float(spin_kick) / float(edge_dist * edge_dist)
        out.append(
            {
                "depth": float(d_now),
                "past_gap": float(past_gap),
                "future_gap": float(future_gap),
                "v_proxy": float(v_proxy),
                "edge_distance": float(edge_dist),
                "spin_kick": float(spin_kick),
                "alpha_hat": float(alpha_hat),
            }
        )
    return out


def _run_channel(
    *,
    channel_id: str,
    left_motif_id: str,
    right_motif_id: str,
    d0: int,
    depth_horizon: int,
    track_right_side: str = "right",
    left_precommit_ticks: int = 0,
    right_precommit_ticks: int = 0,
) -> Dict[str, Any]:
    run = simulate_full_lightcone(
        channel_id=channel_id,
        depth_horizon=depth_horizon,
        initial_edge_distance=d0,
        left_motif_id=left_motif_id,
        right_motif_id=right_motif_id,
        left_precommit_ticks=left_precommit_ticks,
        right_precommit_ticks=right_precommit_ticks,
    )
    def motif_state_from_id(mid: str) -> StateGI:
        if mid == "furey_electron_doubled":
            return furey_electron_doubled()
        if mid == "furey_dual_electron_doubled":
            return furey_dual_electron_doubled()
        if mid == "identity_e0":
            return state_basis(0, (1, 0))
        raise KeyError(f"unknown motif_id: {mid}")

    def apply_precommit(state: StateGI, n_ticks: int) -> StateGI:
        out = state
        for _ in range(n_ticks):
            out = temporal_commit(out)
        return out

    def track_with_state(
        run_payload: Dict[str, Any],
        motif_state: StateGI,
        track_id: str,
        side_preference: str,
    ) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for depth, depth_slice in enumerate(run_payload["slices_base8"]):
            # Reuse canonical tie-break by building transient score slice via existing helper.
            # best_motif_position expects encoded slice + motif state.
            best = best_motif_position(
                depth_slice=depth_slice,
                motif=motif_state,
                side_preference=side_preference,
            )
            out.append(
                {
                    "track_id": track_id,
                    "depth": depth,
                    "pos": int(best["pos"]),
                    "score": int(best["score"]),
                    "exact_match": bool(best["exact_match"]),
                }
            )
        return out

    left_track_state = apply_precommit(motif_state_from_id(left_motif_id), left_precommit_ticks)
    right_track_state = apply_precommit(motif_state_from_id(right_motif_id), right_precommit_ticks)

    path_a = track_with_state(run, left_track_state, f"{channel_id}_left", "left")
    path_b = track_with_state(run, right_track_state, f"{channel_id}_right", track_right_side)
    dist = edge_distance_series(path_a, path_b)
    phase = _relative_phase_series(run_payload=run, path_a=path_a, path_b=path_b)
    events = _phase_interaction_events(phase)
    return {
        "run_payload": run,
        "path_a": path_a,
        "path_b": path_b,
        "distance": dist,
        "phase_rows": phase,
        "phase_events": events,
    }


def run_alpha_photon_running(path: Path | None = None) -> dict[str, Any]:
    conditions = load_conditions(path)
    validate_conditions(conditions)

    mu_eff = float(conditions["mass_normalization"]["mu_eff"])
    d0_grid = [int(x) for x in conditions["initial_edge_distances"]]
    phase_offsets = [int(x) for x in conditions["phase_offsets"]]
    signal_cfg = conditions["signal_channel"]
    control_cfg = conditions.get("control_channel", {})
    control_enabled = bool(control_cfg.get("enabled", False))

    rows: List[Dict[str, Any]] = []
    all_alpha_em: List[float] = []

    for d0 in d0_grid:
        horizon = depth_horizon_for_distance(conditions, d0)
        phase_rows: List[Dict[str, Any]] = []
        alpha_em_phase_samples: List[float] = []
        replay_hashes: List[str] = []

        for phase_offset in phase_offsets:
            signal = _run_channel(
                channel_id=str(signal_cfg["channel_id"]),
                left_motif_id=str(signal_cfg["left_motif_id"]),
                right_motif_id=str(signal_cfg["right_motif_id"]),
                d0=d0,
                depth_horizon=horizon,
                track_right_side="right",
                left_precommit_ticks=0,
                right_precommit_ticks=phase_offset,
            )
            dist_map_sig = _distance_map(signal["distance"])
            alpha_sig_samples = _alpha_samples_from_events(
                events=signal["phase_events"],
                distance_by_depth=dist_map_sig,
                mu_eff=mu_eff,
                depth_horizon=horizon,
            )
            alpha_signal = _median([float(r["alpha_hat"]) for r in alpha_sig_samples])

            alpha_control: Optional[float] = None
            alpha_control_samples: List[Dict[str, float]] = []
            if control_enabled:
                control = _run_channel(
                    channel_id=str(control_cfg["channel_id"]),
                    left_motif_id=str(control_cfg["left_motif_id"]),
                    right_motif_id=str(control_cfg["right_motif_id"]),
                    d0=d0,
                    depth_horizon=horizon,
                    track_right_side="right",
                    left_precommit_ticks=0,
                    right_precommit_ticks=phase_offset,
                )
                dist_map_ctl = _distance_map(control["distance"])
                alpha_control_samples = _alpha_samples_from_events(
                    events=control["phase_events"],
                    distance_by_depth=dist_map_ctl,
                    mu_eff=mu_eff,
                    depth_horizon=horizon,
                )
                alpha_control = _median([float(r["alpha_hat"]) for r in alpha_control_samples])
            alpha_em: Optional[float]
            if alpha_signal is None:
                alpha_em = None
            elif alpha_control is None:
                alpha_em = alpha_signal
            else:
                alpha_em = alpha_signal - alpha_control

            if alpha_em is not None:
                alpha_em_phase_samples.append(alpha_em)
                all_alpha_em.append(alpha_em)

            replay_hashes.append(str(signal["run_payload"]["replay_hash"]))
            phase_rows.append(
                {
                    "phase_offset": phase_offset,
                    "signal_event_count": len(signal["phase_events"]),
                    "signal_alpha_sample_count": len(alpha_sig_samples),
                    "alpha_signal": alpha_signal,
                    "alpha_control": alpha_control,
                    "alpha_em": alpha_em,
                    "signal_replay_hash": signal["run_payload"]["replay_hash"],
                }
            )

        alpha_em_median = _median(alpha_em_phase_samples)
        alpha_em_mad = _mad(alpha_em_phase_samples, alpha_em_median) if alpha_em_median is not None else None
        rows.append(
            {
                "initial_edge_distance": d0,
                "depth_horizon": horizon,
                "phase_offsets": phase_offsets,
                "phase_results": phase_rows,
                "alpha_em_median": alpha_em_median,
                "alpha_em_mad": alpha_em_mad,
                "phase_valid_count": len(alpha_em_phase_samples),
                "signal_replay_hashes": replay_hashes,
            }
        )

    rows.sort(key=lambda r: int(r["initial_edge_distance"]))
    uv_row = rows[0] if rows else None
    ir_row = rows[-1] if rows else None
    pooled_median = _median(all_alpha_em)
    pooled_mad = _mad(all_alpha_em, pooled_median) if pooled_median is not None else None
    target_alpha = float(conditions["target"]["alpha"])
    pooled_rel_gap = (
        abs(pooled_median - target_alpha) / target_alpha
        if pooled_median is not None and target_alpha != 0
        else None
    )

    deterministic_payload = {
        "schema_version": "alpha_photon_running_v1",
        "conditions_checksum": _sha(conditions),
        "rows": rows,
        "summary": {
            "mu_eff": mu_eff,
            "target_alpha": target_alpha,
            "uv_distance": uv_row["initial_edge_distance"] if uv_row else None,
            "uv_alpha_em": uv_row["alpha_em_median"] if uv_row else None,
            "ir_distance": ir_row["initial_edge_distance"] if ir_row else None,
            "ir_alpha_em": ir_row["alpha_em_median"] if ir_row else None,
            "pooled_alpha_em_median": pooled_median,
            "pooled_alpha_em_mad": pooled_mad,
            "pooled_relative_gap_to_target": pooled_rel_gap,
        },
    }
    replay_hash = _sha(deterministic_payload)

    return {
        "schema_version": "alpha_photon_running_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "conditions_checksum": deterministic_payload["conditions_checksum"],
        "rows": rows,
        "summary": deterministic_payload["summary"],
        "replay_hash": replay_hash,
    }


def write_artifacts(
    payload: dict[str, Any],
    *,
    json_paths: List[Path] | None = None,
    csv_paths: List[Path] | None = None,
    md_paths: List[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [OUT_JSON]
    if csv_paths is None:
        csv_paths = [OUT_CSV]
    if md_paths is None:
        md_paths = [OUT_MD]

    for p in json_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fieldnames = [
        "initial_edge_distance",
        "depth_horizon",
        "phase_valid_count",
        "alpha_em_median",
        "alpha_em_mad",
    ]
    for p in csv_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in payload["rows"]:
                out = {k: row.get(k) for k in fieldnames}
                w.writerow(out)

    md_lines = [
        "# ALPHA Photon Running (Full CxO Lightcone)",
        "",
        f"- Replay hash: `{payload['replay_hash'][:16]}...`",
        f"- Conditions checksum: `{payload['conditions_checksum'][:16]}...`",
        "",
        "| d0 (edges) | depth_horizon | valid phase offsets | alpha_em median | alpha_em MAD |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in payload["rows"]:
        md_lines.append(
            "| {d0} | {h} | {n} | {aem} | {mad} |".format(
                d0=row["initial_edge_distance"],
                h=row["depth_horizon"],
                n=row["phase_valid_count"],
                aem="None" if row["alpha_em_median"] is None else f"{row['alpha_em_median']:.12f}",
                mad="None" if row["alpha_em_mad"] is None else f"{row['alpha_em_mad']:.12f}",
            )
        )
    s = payload["summary"]
    md_lines.extend(
        [
            "",
            "## UV -> IR Summary",
            f"- UV point (smallest d0): d0={s['uv_distance']}, alpha_em={s['uv_alpha_em']}",
            f"- IR point (largest d0): d0={s['ir_distance']}, alpha_em={s['ir_alpha_em']}",
            f"- Pooled median alpha_em: {s['pooled_alpha_em_median']}",
            f"- Pooled MAD: {s['pooled_alpha_em_mad']}",
            f"- Relative gap to CODATA alpha: {s['pooled_relative_gap_to_target']}",
            "",
            "Photon interaction event definition: change in relative e7-phase bucket between tracked motifs.",
        ]
    )
    md = "\n".join(md_lines) + "\n"
    for p in md_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(md, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Derive alpha running from full CxO lightcone photon interactions")
    parser.add_argument("--conditions-file", type=Path, default=DEFAULT_CONDITIONS)
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write sources artifacts")
    args = parser.parse_args()

    payload = run_alpha_photon_running(args.conditions_file)
    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {OUT_JSON}")
        print(f"Wrote {OUT_CSV}")
        print(f"Wrote {OUT_MD}")
        return

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    print(
        f"alpha_photon_running: rows={len(payload['rows'])}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

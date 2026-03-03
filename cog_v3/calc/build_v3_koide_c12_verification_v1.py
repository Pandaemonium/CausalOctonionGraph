"""Verify Koide/Brannen identity over C12-like phase offsets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_koide_c12_verification_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_koide_c12_verification_v1.md"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_koide_c12_verification_v1.csv"
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_koide_c12_verification_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _koide_k_unsigned(masses: List[float]) -> float:
    sm = float(sum(masses))
    sr = float(sum(math.sqrt(max(0.0, m)) for m in masses))
    if sr == 0.0:
        return 0.0
    return float(sm / (sr * sr))


def _koide_k_signed(roots: List[float]) -> float:
    masses = [float(r * r) for r in roots]
    sm = float(sum(masses))
    sr = float(sum(roots))
    if sr == 0.0:
        return 0.0
    return float(sm / (sr * sr))


def _brannen_roots(delta_deg: float, c_scale: float = 1.0) -> List[float]:
    d = math.radians(float(delta_deg))
    out: List[float] = []
    for kk in (0, 1, 2):
        val = 1.0 + math.sqrt(2.0) * math.cos((2.0 * math.pi * kk / 3.0) + d)
        out.append(float(c_scale * val))
    return out


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Koide C12 Verification (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- delta_grid_deg_step: `{payload['params']['delta_step_deg']}`",
        f"- max_abs_error_equilateral_signed: `{payload['equilateral_orbit']['max_abs_error_signed_vs_2over3']:.3e}`",
        f"- max_abs_error_equilateral_unsigned: `{payload['equilateral_orbit']['max_abs_error_unsigned_vs_2over3']:.3e}`",
        "",
        "## Non-equilateral control",
        "",
        f"- K_mean: `{payload['nonequilateral_control']['K_mean']:.6f}`",
        f"- K_min: `{payload['nonequilateral_control']['K_min']:.6f}`",
        f"- K_max: `{payload['nonequilateral_control']['K_max']:.6f}`",
    ]
    return "\n".join(lines)


def build_payload(*, delta_step_deg: float = 10.0) -> Dict[str, Any]:
    deltas = np.arange(0.0, 360.0 + 1e-9, float(delta_step_deg), dtype=np.float64)
    rows: List[Dict[str, Any]] = []
    errs: List[float] = []

    for d in deltas.tolist():
        roots = _brannen_roots(float(d), c_scale=1.0)
        masses = [float(r * r) for r in roots]
        k_unsigned = _koide_k_unsigned(masses)
        k_signed = _koide_k_signed(roots)
        err_unsigned = float(k_unsigned - (2.0 / 3.0))
        err_signed = float(k_signed - (2.0 / 3.0))
        errs.append(abs(err_signed))
        rows.append(
            {
                "delta_deg": float(d),
                "m0": float(masses[0]),
                "m1": float(masses[1]),
                "m2": float(masses[2]),
                "K_unsigned": float(k_unsigned),
                "K_signed": float(k_signed),
                "K_unsigned_minus_2over3": float(err_unsigned),
                "K_signed_minus_2over3": float(err_signed),
            }
        )

    # non-equilateral control orbit (0,1,2) as relative phase offsets
    ctrl_rows: List[float] = []
    for d in deltas.tolist():
        dd = math.radians(float(d))
        phases = [dd + 0.0, dd + 2.0 * math.pi / 12.0, dd + 4.0 * math.pi / 12.0]  # 0,1,2 in C12 ticks
        roots = [float(1.0 + math.sqrt(2.0) * math.cos(ph)) for ph in phases]
        ctrl_rows.append(_koide_k_signed(roots))

    payload: Dict[str, Any] = {
        "schema_version": "v3_koide_c12_verification_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "params": {
            "delta_step_deg": float(delta_step_deg),
            "delta_count": int(len(rows)),
        },
        "equilateral_orbit": {
            "orbit_ticks": [0, 4, 8],
            "target_K": float(2.0 / 3.0),
            "max_abs_error_signed_vs_2over3": float(max(abs(float(r["K_signed_minus_2over3"])) for r in rows) if rows else 0.0),
            "mean_abs_error_signed_vs_2over3": float(
                np.mean(np.asarray([abs(float(r["K_signed_minus_2over3"])) for r in rows], dtype=np.float64)) if rows else 0.0
            ),
            "max_abs_error_unsigned_vs_2over3": float(max(abs(float(r["K_unsigned_minus_2over3"])) for r in rows) if rows else 0.0),
            "mean_abs_error_unsigned_vs_2over3": float(
                np.mean(np.asarray([abs(float(r["K_unsigned_minus_2over3"])) for r in rows], dtype=np.float64)) if rows else 0.0
            ),
        },
        "nonequilateral_control": {
            "orbit_ticks": [0, 1, 2],
            "K_mean": float(np.mean(np.asarray(ctrl_rows, dtype=np.float64))) if ctrl_rows else 0.0,
            "K_min": float(np.min(np.asarray(ctrl_rows, dtype=np.float64))) if ctrl_rows else 0.0,
            "K_max": float(np.max(np.asarray(ctrl_rows, dtype=np.float64))) if ctrl_rows else 0.0,
        },
        "rows": rows,
    }
    payload["replay_hash"] = _sha_payload(payload)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write(_render_md(payload))
        f.write("\n")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "delta_deg",
                "m0",
                "m1",
                "m2",
                "K_unsigned",
                "K_signed",
                "K_unsigned_minus_2over3",
                "K_signed_minus_2over3",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)

    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Build Koide C12 verification artifact.")
    ap.add_argument("--delta-step-deg", type=float, default=10.0)
    args = ap.parse_args()
    payload = build_payload(delta_step_deg=float(args.delta_step_deg))
    print(f"max_abs_error_signed={payload['equilateral_orbit']['max_abs_error_signed_vs_2over3']:.3e}")
    print(f"max_abs_error_unsigned={payload['equilateral_orbit']['max_abs_error_unsigned_vs_2over3']:.3e}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()

"""Search excited electron motifs for relative periodic orbits (RPOs) in 3D.

RPO definition used here (x-axis translation lane):
    S_{t+N} = T_dx(S_t)
on a periodic torus lattice, with exact state equality in the unity alphabet.

This script:
1) starts from a stable electron motif in vacuum background,
2) applies one-shot center perturbation at tick 0,
3) evolves on periodic 3D lattice under canonical projector dynamics,
4) detects exact RPOs in x-shifted co-moving frame,
5) checks robustness across multiple parent-fold orders.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from calc.xor_scenario_loader import canonical_motif_state_map
from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "electron_excited_rpo_scan_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "electron_excited_rpo_scan_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_electron_excited_rpo_scan_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
MOTIF_SOURCE_REPO_PATH = "calc/xor_scenario_loader.py::canonical_motif_state_map"


@dataclass(frozen=True)
class RPOParams:
    ticks: int = 40
    size_xyz: int = 7
    burn_in_ticks: int = 8
    min_period: int = 2
    max_period: int = 16
    kick_ops: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7)
    max_shift_x: int = 3


@dataclass(frozen=True)
class FoldOrderVariant:
    order_id: str
    offsets: Tuple[Tuple[int, int, int], ...]


@dataclass(frozen=True)
class KickCase:
    case_id: str
    center_op_idx: int | None
    neighbor_seed_op_idx: int | None


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_cxo(state_gi: Sequence[Tuple[int, int]]) -> k.CxO:
    vals = [k.GInt(int(re), int(im)) for re, im in state_gi]
    return k.project_cxo_to_unity((vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7]))


def _basis_state(op_idx: int) -> k.CxO:
    vals = [k.ZERO_G] * 8
    vals[int(op_idx)] = k.ONE_G
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _left_mul_projected(op_idx: int, state: k.CxO) -> k.CxO:
    return k.project_cxo_to_unity(k.cxo_mul(_basis_state(int(op_idx)), state))


def _abs2(z: k.GInt) -> int:
    return int(z.re * z.re + z.im * z.im)


def _build_fold_orders() -> List[FoldOrderVariant]:
    base = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
    rev = list(reversed(base))
    axis_cycle = [(0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1), (-1, 0, 0), (1, 0, 0)]
    plus_first = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]
    return [
        FoldOrderVariant("canonical_xyz", tuple(base)),
        FoldOrderVariant("reverse_xyz", tuple(rev)),
        FoldOrderVariant("axis_cycle_yzx", tuple(axis_cycle)),
        FoldOrderVariant("plus_first", tuple(plus_first)),
    ]


def _shift_x(world: Sequence[k.CxO], *, n: int, dx: int) -> List[k.CxO]:
    """Return world shifted by +dx along x under torus boundary."""
    out = [k.cxo_one() for _ in world]
    dxm = int(dx) % int(n)
    for x in range(n):
        for y in range(n):
            for z in range(n):
                src_idx = (x * n + y) * n + z
                dst_x = (x + dxm) % n
                dst_idx = (dst_x * n + y) * n + z
                out[dst_idx] = world[src_idx]
    return out


def _equal_world(a: Sequence[k.CxO], b: Sequence[k.CxO]) -> bool:
    if len(a) != len(b):
        return False
    return all(sa == sb for sa, sb in zip(a, b))


def _detect_rpo_x(
    *,
    history: Sequence[List[k.CxO]],
    n: int,
    burn_in: int,
    min_period: int,
    max_period: int,
    max_shift_x: int,
) -> Dict[str, Any]:
    t_max = len(history) - 1
    if t_max <= 0:
        return {"found": False}
    period_hi = max(1, int(max_period))
    period_lo = max(1, int(min_period))
    shift_choices: List[int] = []
    for s in range(1, max(1, int(max_shift_x)) + 1):
        shift_choices.extend([s, -s])
    shift_choices.append(0)

    for t1 in range(max(int(burn_in), period_lo), t_max + 1):
        for N in range(period_lo, period_hi + 1):
            t0 = t1 - N
            if t0 < 0:
                continue
            base = history[t0]
            now = history[t1]
            for dx in shift_choices:
                shifted = _shift_x(base, n=n, dx=dx)
                if _equal_world(shifted, now):
                    speed = float(abs(dx) / float(N))
                    return {
                        "found": True,
                        "t0": int(t0),
                        "t1": int(t1),
                        "period_N": int(N),
                        "shift_dx": int(dx),
                        "speed_abs_dx_over_N": float(speed),
                    }
    return {"found": False}


def _simulate_case_variant(
    *,
    params: RPOParams,
    case: KickCase,
    fold_variant: FoldOrderVariant,
    electron_state: k.CxO,
) -> Dict[str, Any]:
    n = int(params.size_xyz)
    if n < 5:
        raise ValueError("size_xyz must be >= 5")
    center = (n // 2, n // 2, n // 2)

    # Lexicographic (x,y,z) linearization.
    def idx(x: int, y: int, z: int) -> int:
        return (x * n + y) * n + z

    world: List[k.CxO] = [k.cxo_one() for _ in range(n * n * n)]
    world[idx(*center)] = electron_state
    if case.center_op_idx is not None:
        world[idx(*center)] = _left_mul_projected(int(case.center_op_idx), world[idx(*center)])
    if case.neighbor_seed_op_idx is not None:
        neighbor_px = ((center[0] + 1) % n, center[1], center[2])
        world[idx(*neighbor_px)] = _basis_state(int(case.neighbor_seed_op_idx))

    history: List[List[k.CxO]] = [list(world)]
    centroid_rows: List[Dict[str, float]] = []

    for tick in range(int(params.ticks)):
        old = world
        nxt: List[k.CxO] = [k.cxo_one() for _ in range(n * n * n)]
        for x in range(n):
            for y in range(n):
                for z in range(n):
                    i = idx(x, y, z)
                    msgs: List[k.CxO] = []
                    for dx, dy, dz in fold_variant.offsets:
                        qx = (x + int(dx)) % n
                        qy = (y + int(dy)) % n
                        qz = (z + int(dz)) % n
                        msgs.append(old[idx(qx, qy, qz)])
                    nxt[i] = k.update_rule(old[i], msgs)
        world = nxt
        history.append(list(world))

        # Track non-e000 centroid for diagnostics.
        rho = []
        for s in world:
            rho.append(float(sum(_abs2(s[j]) for j in range(1, 8))))
        den = float(sum(rho))
        if den > 0.0:
            cx = float(sum(float(x) * rho[idx(x, y, z)] for x in range(n) for y in range(n) for z in range(n)) / den)
            cy = float(sum(float(y) * rho[idx(x, y, z)] for x in range(n) for y in range(n) for z in range(n)) / den)
            cz = float(sum(float(z) * rho[idx(x, y, z)] for x in range(n) for y in range(n) for z in range(n)) / den)
        else:
            cx = cy = cz = 0.0
        centroid_rows.append({"tick": float(tick + 1), "cx": cx, "cy": cy, "cz": cz})

    rpo = _detect_rpo_x(
        history=history,
        n=n,
        burn_in=int(params.burn_in_ticks),
        min_period=int(params.min_period),
        max_period=int(params.max_period),
        max_shift_x=int(params.max_shift_x),
    )
    rpo["fold_order_id"] = fold_variant.order_id
    rpo["case_id"] = case.case_id
    rpo["center_op_idx"] = case.center_op_idx
    rpo["neighbor_seed_op_idx"] = case.neighbor_seed_op_idx
    rpo["centroid_rows"] = centroid_rows
    return rpo


def build_payload(params: RPOParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else RPOParams()
    if int(p.ticks) < 8:
        raise ValueError("ticks must be >= 8")
    if int(p.burn_in_ticks) >= int(p.ticks):
        raise ValueError("burn_in_ticks must be < ticks")
    if int(p.min_period) < 1 or int(p.max_period) < int(p.min_period):
        raise ValueError("invalid period range")

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    motifs = canonical_motif_state_map()
    electron = _to_cxo(motifs["left_spinor_electron_ideal"])
    fold_orders = _build_fold_orders()

    kick_cases: List[KickCase] = [KickCase("control_none", None, None)]
    for op in p.kick_ops:
        kick_cases.append(KickCase(f"center_left_e{int(op):03b}", int(op), None))
    for op in p.kick_ops:
        kick_cases.append(KickCase(f"center_neighbor_px_left_e{int(op):03b}", int(op), int(op)))
    for op in p.kick_ops:
        kick_cases.append(KickCase(f"neighbor_px_only_e{int(op):03b}", None, int(op)))

    case_rows: List[Dict[str, Any]] = []
    for kc in kick_cases:
        variant_rows: List[Dict[str, Any]] = []
        for fv in fold_orders:
            variant_rows.append(
                _simulate_case_variant(params=p, case=kc, fold_variant=fv, electron_state=electron)
            )
        found_rows = [r for r in variant_rows if bool(r.get("found", False))]
        robust = bool(len(found_rows) == len(variant_rows) and len(found_rows) > 0)
        same_period_shift = False
        if robust:
            pairs = {(int(r["period_N"]), int(r["shift_dx"])) for r in found_rows}
            same_period_shift = bool(len(pairs) == 1)
        case_rows.append(
            {
                "case_id": kc.case_id,
                "center_op_idx": kc.center_op_idx,
                "neighbor_seed_op_idx": kc.neighbor_seed_op_idx,
                "variant_results": variant_rows,
                "summary": {
                    "all_variants_found_rpo": robust,
                    "all_variants_same_period_shift": same_period_shift,
                    "variants_with_rpo": int(len(found_rows)),
                    "variant_count": int(len(variant_rows)),
                    "representative_period_shift": (
                        [int(found_rows[0]["period_N"]), int(found_rows[0]["shift_dx"])] if found_rows else None
                    ),
                    "representative_speed": (float(found_rows[0]["speed_abs_dx_over_N"]) if found_rows else None),
                },
            }
        )

    robust_cases = [
        c["case_id"]
        for c in case_rows
        if bool(c["summary"]["all_variants_found_rpo"]) and bool(c["summary"]["all_variants_same_period_shift"])
    ]
    robust_nonzero_shift_cases = [
        c["case_id"]
        for c in case_rows
        if bool(c["summary"]["all_variants_found_rpo"])
        and bool(c["summary"]["all_variants_same_period_shift"])
        and c["summary"]["representative_period_shift"] is not None
        and int(c["summary"]["representative_period_shift"][1]) != 0
    ]
    payload: Dict[str, Any] = {
        "schema_version": "electron_excited_rpo_scan_v1",
        "claim_id": "ELECTRON-RPO-001",
        "mode": "simulation_first_structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "projector_id": k.PROJECTOR_ID,
        "motif_source": MOTIF_SOURCE_REPO_PATH,
        "motif_id": "left_spinor_electron_ideal",
        "params": {
            "ticks": int(p.ticks),
            "size_xyz": int(p.size_xyz),
            "burn_in_ticks": int(p.burn_in_ticks),
            "min_period": int(p.min_period),
            "max_period": int(p.max_period),
            "kick_ops": [int(x) for x in p.kick_ops],
            "max_shift_x": int(p.max_shift_x),
            "boundary_mode": "periodic_torus",
        },
        "fold_order_variants": [fo.order_id for fo in fold_orders],
        "kick_cases": [
            {
                "case_id": kc.case_id,
                "center_op_idx": kc.center_op_idx,
                "neighbor_seed_op_idx": kc.neighbor_seed_op_idx,
            }
            for kc in kick_cases
        ],
        "cases": case_rows,
        "robust_rpo_case_ids": robust_cases,
        "robust_nonzero_shift_case_ids": robust_nonzero_shift_cases,
        "checks": {
            "has_any_rpo": bool(any(c["summary"]["variants_with_rpo"] > 0 for c in case_rows)),
            "has_robust_rpo": bool(len(robust_cases) > 0),
            "has_robust_nonzero_shift_rpo": bool(len(robust_nonzero_shift_cases) > 0),
            "rpo_requires_order_robustness_gate": True,
        },
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    lines = [
        "# Electron Excited RPO Scan (v1)",
        "",
        "Searches exact relative periodic orbits under x-shift translation on a 3D torus.",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- size_xyz: `{p['size_xyz']}`",
        f"- burn_in_ticks: `{p['burn_in_ticks']}`",
        f"- min_period..max_period: `{p['min_period']}..{p['max_period']}`",
        f"- kick_ops: `{p['kick_ops']}`",
        f"- max_shift_x: `{p['max_shift_x']}`",
        f"- fold_order_variants: `{payload['fold_order_variants']}`",
        "",
        "## Cases",
        "",
        "| case_id | variants_with_rpo | all_variants_found_rpo | all_variants_same_period_shift | representative_period_shift | representative_speed |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for c in payload["cases"]:
        s = c["summary"]
        lines.append(
            f"| `{c['case_id']}` | {s['variants_with_rpo']} | {s['all_variants_found_rpo']} | "
            f"{s['all_variants_same_period_shift']} | `{s['representative_period_shift']}` | `{s['representative_speed']}` |"
        )
    lines.extend(["", "## Robust RPO Cases", ""])
    robust_ids = list(payload["robust_rpo_case_ids"])
    if robust_ids:
        lines.extend([f"- `{cid}`" for cid in robust_ids])
    else:
        lines.append("- none")
    lines.extend(["", "## Robust Nonzero-Shift RPO Cases", ""])
    nz_ids = list(payload.get("robust_nonzero_shift_case_ids", []))
    if nz_ids:
        lines.extend([f"- `{cid}`" for cid in nz_ids])
    else:
        lines.append("- none")
    lines.extend(["", "## Checks", ""])
    lines.extend([f"- {k}: `{v}`" for k, v in payload["checks"].items()])
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: Dict[str, Any],
    json_paths: Sequence[Path] = (OUT_JSON,),
    md_paths: Sequence[Path] = (OUT_MD,),
) -> None:
    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = _render_md(payload)
    for path in md_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticks", type=int, default=RPOParams.ticks)
    parser.add_argument("--size", type=int, default=RPOParams.size_xyz)
    parser.add_argument("--burn-in", type=int, default=RPOParams.burn_in_ticks)
    parser.add_argument("--min-period", type=int, default=RPOParams.min_period)
    parser.add_argument("--max-period", type=int, default=RPOParams.max_period)
    parser.add_argument("--max-shift-x", type=int, default=RPOParams.max_shift_x)
    parser.add_argument("--kick-ops", type=int, nargs="*", default=list(RPOParams.kick_ops))
    args = parser.parse_args()

    kicks = tuple(int(x) for x in args.kick_ops)
    if not kicks:
        raise ValueError("kick-ops must be non-empty")
    params = RPOParams(
        ticks=int(args.ticks),
        size_xyz=int(args.size),
        burn_in_ticks=int(args.burn_in),
        min_period=int(args.min_period),
        max_period=int(args.max_period),
        kick_ops=kicks,
        max_shift_x=int(args.max_shift_x),
    )
    payload = build_payload(params)
    write_artifacts(payload)
    print(
        "electron_excited_rpo_scan_v1: "
        f"has_any_rpo={payload['checks']['has_any_rpo']}, "
        f"has_robust_rpo={payload['checks']['has_robust_rpo']}, "
        f"robust_count={len(payload['robust_rpo_case_ids'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Build excited propagation cycle library for multiple particle motifs (v1).

Outputs exact post-transient relative-periodic propagation cycles on a 3D torus.
Each selected case includes:
1) perturbation contract,
2) transient lock timing,
3) exact cycle states in lab frame.
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
OUT_JSON = ROOT / "cog_v2" / "sources" / "particle_excited_propagation_cycle_library_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "particle_excited_propagation_cycle_library_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_particle_excited_propagation_cycle_library_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
MOTIF_SOURCE_REPO_PATH = "calc/xor_scenario_loader.py::canonical_motif_state_map"


@dataclass(frozen=True)
class LibraryParams:
    ticks: int = 48
    size_xyz: int = 7
    burn_in_ticks: int = 8
    min_period: int = 2
    max_period: int = 20
    max_shift_x: int = 3
    kick_ops: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7)
    particle_ids: Tuple[str, ...] = (
        "left_spinor_electron_ideal",
        "left_spinor_muon_motif",
        "left_spinor_tau_motif",
        "right_spinor_electron_ideal",
        "vector_proton_proto_t124",
    )


@dataclass(frozen=True)
class FoldOrderVariant:
    order_id: str
    offsets: Tuple[Tuple[int, int, int], ...]


@dataclass(frozen=True)
class EnergyBand:
    energy_id: str
    center_kick: bool
    shell1_vacuum_coherent: bool
    shell2_vacuum_coherent: bool
    description: str


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


def _serialize_state(state: k.CxO) -> List[List[int]]:
    return [[int(z.re), int(z.im)] for z in state]


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


def _energy_bands() -> Tuple[EnergyBand, ...]:
    return (
        EnergyBand(
            "E1_center_kick",
            center_kick=True,
            shell1_vacuum_coherent=False,
            shell2_vacuum_coherent=False,
            description="Low excitation: center motif left-multiplied by eXYZ basis kick at tick 0.",
        ),
        EnergyBand(
            "E2_center_plus_shell1",
            center_kick=True,
            shell1_vacuum_coherent=True,
            shell2_vacuum_coherent=False,
            description=(
                "Medium excitation: center kick plus coherent +x nearest-neighbor vacuum phase seed "
                "(photon-like directional perturbation lane)."
            ),
        ),
        EnergyBand(
            "E3_center_plus_shell2",
            center_kick=True,
            shell1_vacuum_coherent=True,
            shell2_vacuum_coherent=True,
            description="Higher excitation: center kick plus coherent +x first and second shell vacuum phase seeds.",
        ),
    )


def _shift_x(world: Sequence[k.CxO], *, n: int, dx: int) -> List[k.CxO]:
    out = [k.cxo_one() for _ in world]
    dxm = int(dx) % int(n)
    for x, y, z in itertools.product(range(n), repeat=3):
        src = (x * n + y) * n + z
        dst_x = (x + dxm) % n
        dst = (dst_x * n + y) * n + z
        out[dst] = world[src]
    return out


def _equal_world(a: Sequence[k.CxO], b: Sequence[k.CxO]) -> bool:
    return len(a) == len(b) and all(sa == sb for sa, sb in zip(a, b))


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
    shifts: List[int] = []
    for s in range(1, max(1, int(max_shift_x)) + 1):
        shifts.extend([s, -s])
    shifts.append(0)
    for t1 in range(max(int(burn_in), int(min_period)), t_max + 1):
        for period in range(int(min_period), int(max_period) + 1):
            t0 = int(t1 - period)
            if t0 < 0:
                continue
            s0 = history[t0]
            s1 = history[t1]
            for dx in shifts:
                if _equal_world(_shift_x(s0, n=n, dx=dx), s1):
                    return {
                        "found": True,
                        "t0": int(t0),
                        "t1": int(t1),
                        "period_N": int(period),
                        "shift_dx": int(dx),
                        "speed_abs_dx_over_N": float(abs(dx) / float(period)),
                    }
    return {"found": False}


def _run_variant(
    *,
    params: LibraryParams,
    particle_state: k.CxO,
    vacuum_state: k.CxO,
    op_idx: int,
    band: EnergyBand,
    fold: FoldOrderVariant,
) -> Dict[str, Any]:
    n = int(params.size_xyz)
    center = (n // 2, n // 2, n // 2)
    shell1 = ((center[0] + 1) % n, center[1], center[2])
    shell2 = ((center[0] + 2) % n, center[1], center[2])

    def idx(x: int, y: int, z: int) -> int:
        return (x * n + y) * n + z

    world: List[k.CxO] = [k.cxo_one() for _ in range(n * n * n)]
    seed_center = _left_mul_projected(int(op_idx), particle_state) if band.center_kick else particle_state
    world[idx(*center)] = seed_center
    vac_phase = _left_mul_projected(int(op_idx), vacuum_state)
    if band.shell1_vacuum_coherent:
        world[idx(*shell1)] = vac_phase
    if band.shell2_vacuum_coherent:
        world[idx(*shell2)] = vac_phase

    history: List[List[k.CxO]] = [list(world)]
    for _ in range(int(params.ticks)):
        old = world
        nxt: List[k.CxO] = [k.cxo_one() for _ in range(n * n * n)]
        for x, y, z in itertools.product(range(n), repeat=3):
            msgs: List[k.CxO] = []
            for dx, dy, dz in fold.offsets:
                qx = (x + int(dx)) % n
                qy = (y + int(dy)) % n
                qz = (z + int(dz)) % n
                msgs.append(old[idx(qx, qy, qz)])
            nxt[idx(x, y, z)] = k.update_rule(old[idx(x, y, z)], msgs)
        world = nxt
        history.append(list(world))

    rpo = _detect_rpo_x(
        history=history,
        n=n,
        burn_in=int(params.burn_in_ticks),
        min_period=int(params.min_period),
        max_period=int(params.max_period),
        max_shift_x=int(params.max_shift_x),
    )
    rpo["history"] = history
    rpo["fold_order_id"] = fold.order_id
    return rpo


def _extract_cycle_rows(history: Sequence[List[k.CxO]], t0: int, period: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for k_idx in range(int(period)):
        t = int(t0 + k_idx)
        world = history[t]
        rows.append(
            {
                "cycle_step": int(k_idx),
                "tick": int(t),
                "world_state_dense": [_serialize_state(s) for s in world],
            }
        )
    return rows


def build_payload(params: LibraryParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else LibraryParams()
    if int(p.ticks) < 12:
        raise ValueError("ticks must be >= 12")
    if int(p.size_xyz) < 5:
        raise ValueError("size_xyz must be >= 5")
    if int(p.burn_in_ticks) >= int(p.ticks):
        raise ValueError("burn_in_ticks must be < ticks")

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    motifs = canonical_motif_state_map()
    vacuum = _to_cxo(motifs["su_vacuum_omega"])
    fold_orders = _build_fold_orders()
    bands = _energy_bands()

    particle_rows: List[Dict[str, Any]] = []
    for pid in p.particle_ids:
        if pid not in motifs:
            continue
        particle_state = _to_cxo(motifs[pid])
        selected_cases: List[Dict[str, Any]] = []
        for band in bands:
            winner: Dict[str, Any] | None = None
            for op_idx in p.kick_ops:
                variant_results = [
                    _run_variant(
                        params=p,
                        particle_state=particle_state,
                        vacuum_state=vacuum,
                        op_idx=int(op_idx),
                        band=band,
                        fold=fold,
                    )
                    for fold in fold_orders
                ]
                found = [r for r in variant_results if bool(r.get("found", False))]
                robust = bool(len(found) == len(variant_results) and len(found) > 0)
                if not robust:
                    continue
                signature = {(int(r["period_N"]), int(r["shift_dx"])) for r in found}
                if len(signature) != 1:
                    continue
                period, dx = next(iter(signature))
                if int(dx) == 0:
                    continue
                # Choose earliest lock tick among robust options for this band.
                t0_med = sorted(int(r["t0"]) for r in found)[len(found) // 2]
                if winner is None or t0_med < int(winner["transient_lock_tick"]):
                    canonical = next(r for r in variant_results if str(r["fold_order_id"]) == "canonical_xyz")
                    cycle_rows = _extract_cycle_rows(canonical["history"], int(canonical["t0"]), int(canonical["period_N"]))
                    closure_ok = _equal_world(
                        _shift_x(canonical["history"][int(canonical["t0"])], n=int(p.size_xyz), dx=int(canonical["shift_dx"])),
                        canonical["history"][int(canonical["t1"])],
                    )
                    winner = {
                        "energy_id": band.energy_id,
                        "energy_description": band.description,
                        "perturbation": {
                            "center_op_idx": int(op_idx),
                            "center_kick": bool(band.center_kick),
                            "shell1_vacuum_coherent": bool(band.shell1_vacuum_coherent),
                            "shell2_vacuum_coherent": bool(band.shell2_vacuum_coherent),
                            "vacuum_phase_seed_state": _serialize_state(_left_mul_projected(int(op_idx), vacuum)),
                        },
                        "period_N": int(period),
                        "shift_dx": int(dx),
                        "speed_abs_dx_over_N": float(abs(dx) / float(period)),
                        "transient_lock_tick": int(canonical["t0"]),
                        "transient_confirm_tick": int(canonical["t1"]),
                        "fold_order_robustness": {
                            "variant_count": int(len(variant_results)),
                            "variant_ids": [v.order_id for v in fold_orders],
                            "all_variants_found_rpo": True,
                            "all_variants_same_period_shift": True,
                        },
                        "closure_witness": {
                            "closure_check_passed": bool(closure_ok),
                            "closure_relation": "state(t0 + N) == shift_x(state(t0), dx)",
                        },
                        "cycle_rows_post_transient": cycle_rows,
                    }
            if winner is not None:
                selected_cases.append(winner)

        # ensure at least two cases with distinct energy_id when available
        selected_cases = sorted(selected_cases, key=lambda r: (str(r["energy_id"]), int(r["transient_lock_tick"])))
        if len(selected_cases) > 2:
            # Keep first two distinct energies.
            keep: List[Dict[str, Any]] = []
            seen: set[str] = set()
            for row in selected_cases:
                eid = str(row["energy_id"])
                if eid in seen:
                    continue
                keep.append(row)
                seen.add(eid)
                if len(keep) >= 2:
                    break
            selected_cases = keep

        particle_rows.append(
            {
                "particle_id": pid,
                "selected_case_count": int(len(selected_cases)),
                "selected_cases": selected_cases,
                "has_two_energy_cases": bool(len(selected_cases) >= 2 and selected_cases[0]["energy_id"] != selected_cases[1]["energy_id"]) if len(selected_cases) >= 2 else False,
            }
        )

    payload: Dict[str, Any] = {
        "schema_version": "particle_excited_propagation_cycle_library_v1",
        "claim_id": "EXCITED-CYCLE-LIB-001",
        "mode": "simulation_first_structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "projector_id": k.PROJECTOR_ID,
        "motif_source": MOTIF_SOURCE_REPO_PATH,
        "params": {
            "ticks": int(p.ticks),
            "size_xyz": int(p.size_xyz),
            "burn_in_ticks": int(p.burn_in_ticks),
            "min_period": int(p.min_period),
            "max_period": int(p.max_period),
            "max_shift_x": int(p.max_shift_x),
            "kick_ops": [int(x) for x in p.kick_ops],
            "particle_ids": list(p.particle_ids),
            "boundary_mode": "periodic_torus",
        },
        "energy_bands": [
            {
                "energy_id": b.energy_id,
                "description": b.description,
                "center_kick": b.center_kick,
                "shell1_vacuum_coherent": b.shell1_vacuum_coherent,
                "shell2_vacuum_coherent": b.shell2_vacuum_coherent,
            }
            for b in bands
        ],
        "fold_order_variants": [f.order_id for f in fold_orders],
        "particles": particle_rows,
        "checks": {
            "all_particles_have_at_least_two_energy_cases": bool(all(bool(r["has_two_energy_cases"]) for r in particle_rows)) if particle_rows else False,
            "particle_count_processed": int(len(particle_rows)),
        },
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    lines = [
        "# Particle Excited Propagation Cycle Library (v1)",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- size_xyz: `{p['size_xyz']}`",
        f"- burn_in_ticks: `{p['burn_in_ticks']}`",
        f"- period range: `{p['min_period']}..{p['max_period']}`",
        f"- kick_ops: `{p['kick_ops']}`",
        f"- fold_order_variants: `{payload['fold_order_variants']}`",
        "",
        "## Particle Summary",
        "",
        "| particle_id | selected_case_count | has_two_energy_cases |",
        "|---|---:|---:|",
    ]
    for r in payload["particles"]:
        lines.append(
            f"| `{r['particle_id']}` | {r['selected_case_count']} | {r['has_two_energy_cases']} |"
        )
    lines.extend(["", "## Selected Cases", ""])
    for r in payload["particles"]:
        lines.append(f"### {r['particle_id']}")
        if not r["selected_cases"]:
            lines.append("- no robust nonzero-shift RPO case found")
            lines.append("")
            continue
        for c in r["selected_cases"]:
            lines.append(
                f"- `{c['energy_id']}` op=`{c['perturbation']['center_op_idx']}` "
                f"N=`{c['period_N']}` dx=`{c['shift_dx']}` "
                f"speed=`{c['speed_abs_dx_over_N']}` "
                f"lock=`{c['transient_lock_tick']}` confirm=`{c['transient_confirm_tick']}`"
            )
        lines.append("")
    lines.extend(
        [
            "## Checks",
            "",
            *(f"- {k}: `{v}`" for k, v in payload["checks"].items()),
        ]
    )
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
    parser.add_argument("--ticks", type=int, default=LibraryParams.ticks)
    parser.add_argument("--size", type=int, default=LibraryParams.size_xyz)
    parser.add_argument("--burn-in", type=int, default=LibraryParams.burn_in_ticks)
    parser.add_argument("--min-period", type=int, default=LibraryParams.min_period)
    parser.add_argument("--max-period", type=int, default=LibraryParams.max_period)
    parser.add_argument("--max-shift-x", type=int, default=LibraryParams.max_shift_x)
    parser.add_argument("--kick-ops", type=int, nargs="*", default=list(LibraryParams.kick_ops))
    args = parser.parse_args()

    kicks = tuple(int(x) for x in args.kick_ops)
    if not kicks:
        raise ValueError("kick-ops must be non-empty")
    params = LibraryParams(
        ticks=int(args.ticks),
        size_xyz=int(args.size),
        burn_in_ticks=int(args.burn_in),
        min_period=int(args.min_period),
        max_period=int(args.max_period),
        max_shift_x=int(args.max_shift_x),
        kick_ops=kicks,
    )
    payload = build_payload(params)
    write_artifacts(payload)
    print(
        "particle_excited_propagation_cycle_library_v1: "
        f"particles={payload['checks']['particle_count_processed']}, "
        f"all_have_two_energy_cases={payload['checks']['all_particles_have_at_least_two_energy_cases']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


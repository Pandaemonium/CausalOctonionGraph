from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from cog_v4.python import kernel_s2880_lightcone_coherent_v1 as kv4


OUT_MD = Path("cog_v4/sources/v4_small_system_coherent_sim_with_integer_energy_v1.md")
OUT_JSON = Path("cog_v4/sources/v4_small_system_coherent_sim_with_integer_energy_v1.json")


def _render_md(payload: Dict[str, Any]) -> str:
    s = payload["seed"]
    c = payload["counts"]
    t = payload["triality"]
    ez = payload["energy_z"]
    ms = payload["measurement_summary"]
    lines = [
        "# v4 Small-System Coherent Sim With Integer Energy (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- shape: `{payload['shape']}`",
        f"- stencil_id: `{payload['stencil_id']}`",
        f"- boundary_mode: `{payload['boundary_mode']}`",
        f"- history_depth: `{payload['history_depth']}`",
        f"- decoherence_ticks: `{payload['decoherence_ticks']}`",
        "",
        "## Seed",
        "",
        f"- domain_g (Z3): `{s['domain_g']}`",
        f"- energy_a (Z4): `{s['energy_a']}`",
        f"- q_id (Q240): `{s['q_id']}`",
        f"- seed_sid: `{s['seed_sid']}`",
        f"- seed_z (integer energy): `{s['seed_z']}`",
        f"- vacuum_z: `{s['vacuum_z']}`",
        "",
        "## Volume",
        "",
        f"- total cells: `{c['cells_total']}`",
        f"- start lightcone cells: `{c['start_volume_cells']}`",
        f"- measurement cells: `{c['measurement_cells']}`",
        "",
        "## Triality",
        "",
        f"- gamma_t0: `{t['gamma_t0']}`",
        f"- gamma_t_meas: `{t['gamma_t_meas']}`",
        f"- conserved: `{t['conserved']}`",
        "",
        "## Integer Energy Z",
        "",
        f"- total_t0: `{ez['total_t0']}`",
        f"- total_t_meas: `{ez['total_t_meas']}`",
        f"- conserved: `{ez['conserved']}`",
        f"- nonnegative: `{ez['nonnegative']}`",
        f"- min_t_meas: `{ez['min_t_meas']}`",
        f"- measurement_sum: `{ez['measurement_sum']}`",
        "",
        "## Measurement Summary",
        "",
        f"- phase_hist_12: `{ms['phase_hist_12']}`",
        f"- unique q bins in measurement: `{ms['q_hist_nonzero']}`",
        "",
    ]
    return "\n".join(lines) + "\n"


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    cfg = kv4.CoherentConfig(
        history_depth=int(args.history_depth),
        stencil_id=str(args.stencil_id),
        boundary_mode=str(args.boundary_mode),
        cone_metric=str(args.cone_metric),
    )
    ecfg = kv4.IntegerEnergyConfig(
        seed_z=int(args.seed_z),
        vacuum_z=int(args.vacuum_z),
    )
    volume = kv4.VolumeBox(
        x0=int(args.mx0),
        x1=int(args.mx1),
        y0=int(args.my0),
        y1=int(args.my1),
        z0=int(args.mz0),
        z1=int(args.mz1),
    )
    return kv4.run_coherent_reconstruction_with_integer_energy(
        shape=(int(args.nx), int(args.ny), int(args.nz)),
        measurement_volume=volume,
        decoherence_ticks=int(args.decoherence_ticks),
        domain_g=int(args.domain_g),
        energy_a=int(args.energy_a),
        q_id=int(args.q_id),
        config=cfg,
        energy_cfg=ecfg,
        vacuum_sid=int(args.vacuum_sid),
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build v4 coherent simulation with integer Z-energy.")
    p.add_argument("--nx", type=int, default=21)
    p.add_argument("--ny", type=int, default=21)
    p.add_argument("--nz", type=int, default=21)

    p.add_argument("--mx0", type=int, default=9)
    p.add_argument("--mx1", type=int, default=12)
    p.add_argument("--my0", type=int, default=9)
    p.add_argument("--my1", type=int, default=12)
    p.add_argument("--mz0", type=int, default=9)
    p.add_argument("--mz1", type=int, default=12)

    p.add_argument("--decoherence-ticks", type=int, default=6)
    p.add_argument("--history-depth", type=int, default=4)
    p.add_argument("--stencil-id", type=str, default="axial6", choices=["axial6", "cube26"])
    p.add_argument("--boundary-mode", type=str, default="fixed_vacuum", choices=["fixed_vacuum", "periodic"])
    p.add_argument("--cone-metric", type=str, default="l1", choices=["l1", "linf"])

    p.add_argument("--domain-g", type=int, default=0)
    p.add_argument("--energy-a", type=int, default=1)
    p.add_argument("--q-id", type=int, default=0)
    p.add_argument("--vacuum-sid", type=int, default=0)
    p.add_argument("--seed-z", type=int, default=1)
    p.add_argument("--vacuum-z", type=int, default=0)

    p.add_argument("--out-md", type=Path, default=OUT_MD)
    p.add_argument("--out-json", type=Path, default=OUT_JSON)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.write_text(_render_md(payload), encoding="utf-8")
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from cog_v3.python import kernel_cog_v4_coherence as kc


OUT_JSON = Path("cog_v3/sources/v4_s_rule_coherence_probe_v1.json")
OUT_MD = Path("cog_v3/sources/v4_s_rule_coherence_probe_v1.md")


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v4 s-rule Coherence Probe (v1)",
        "",
        f"- horizon: `{payload['horizon']}`",
        f"- selected_rule_name: `{payload['selected_rule_name']}`",
        f"- selected_rule_physical: `{payload['selected_rule_physical']}`",
        "",
        "## Seed",
        "",
        f"- g: `{payload['seed']['g']}`",
        f"- a: `{payload['seed']['a']}`",
        f"- basis(q): `{payload['seed']['basis']}`",
        f"- e7_energy: `{payload['seed']['e7_energy']}`",
        f"- e0_energy: `{payload['seed']['e0_energy']}`",
        "",
        "## Candidates",
        "",
        "| rule_name | physical | violation_t | violation_coords | n_paths | n_disagreeing |",
        "|---|---:|---:|---|---:|---:|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['rule_name']}` | {row['physical']} | {row['violation_t']} | {row['violation_coords']} | {row['n_paths']} | {row['n_disagreeing']} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    seed = kc.e7_e0_energy_probe_seed(
        g=int(args.g),
        a=int(args.a),
        sign=int(args.sign),
        basis=int(args.basis),
        e7_energy=int(args.e7_energy),
        e0_energy=int(args.e0_energy),
    )
    probe = kc.select_s_rule_by_coherence(seed, horizon=int(args.horizon))
    payload: Dict[str, Any] = {
        **probe,
        "seed": {
            "g": int(args.g) % 3,
            "a": int(args.a) % 4,
            "basis": int(args.basis) % 8,
            "e7_energy": int(args.e7_energy),
            "e0_energy": int(args.e0_energy),
        },
    }
    return payload


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run e7/e0 deterministic s-rule coherence probe.")
    p.add_argument("--g", type=int, default=0)
    p.add_argument("--a", type=int, default=1)
    p.add_argument("--sign", type=int, default=1)
    p.add_argument("--basis", type=int, default=7)
    p.add_argument("--e7-energy", type=int, default=1)
    p.add_argument("--e0-energy", type=int, default=0)
    p.add_argument("--horizon", type=int, default=3)
    p.add_argument("--out-json", type=Path, default=OUT_JSON)
    p.add_argument("--out-md", type=Path, default=OUT_MD)
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


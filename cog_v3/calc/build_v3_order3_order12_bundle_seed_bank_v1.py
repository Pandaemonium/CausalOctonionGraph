"""Build RFC-014 order3<->order12 bundle seed bank on S960 (C4 x Q240)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_order3_order12_bundle_seed_bank_v1.csv"
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_order3_order12_bundle_seed_bank_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_order3_order12_bundle_seed_bank_v1.md"
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_order3_order12_bundle_seed_bank_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Order3-Order12 Bundle Seed Bank (v1)",
        "",
        f"- convention_id: `{payload['convention_id']}`",
        f"- s960_size: `{payload['s960_size']}`",
        f"- order12_subgroup_count: `{payload['order12_subgroup_count']}`",
        f"- unique_order3_core_count: `{payload['unique_order3_core_count']}`",
        f"- bijection_ok: `{payload['bijection_ok']}`",
        "",
        "## Notes",
        "",
        "- `bundle4_ids` encodes `{g^1,g^4,g^7,g^10}` as S960 ids.",
        "- `core_order3_id` is the order-3 core (`g^4`) for the subgroup.",
    ]
    return "\n".join(lines)


def build_payload() -> Dict[str, Any]:
    qmul = c12.build_qmul_table()
    mul = c12.build_mul_table(phase_count=4, qmul=qmul)  # S960
    s960_size = int(mul.shape[0])
    identity = int(c12.s_identity_id())
    clocks = c12.build_clocks(mul, identity=identity)

    rows: List[Dict[str, Any]] = []
    core_set = set()
    bundle_count = 0

    for clk in clocks:
        if int(clk.period) != 12:
            continue
        cyc = list(int(x) for x in clk.canonical_cycle)
        # canonical cycle starts at identity: [e, g, g^2, ..., g^11]
        g1 = int(cyc[1])
        g4 = int(cyc[4])
        g7 = int(cyc[7])
        g10 = int(cyc[10])
        core_set.add(int(g4))
        bundle_count += 1
        rows.append(
            {
                "bundle_id": int(bundle_count - 1),
                "clock_id": int(clk.clock_id),
                "period": int(clk.period),
                "rep_id": int(clk.rep_id),
                "generator_id": int(g1),
                "core_order3_id": int(g4),
                "bundle4_ids": f"{g1}|{g4}|{g7}|{g10}",
                "bundle4_seed_id": f"B4_{g1}_{g4}_{g7}_{g10}",
            }
        )

    rows.sort(key=lambda r: (int(r["core_order3_id"]), int(r["generator_id"])))
    for i, r in enumerate(rows):
        r["bundle_id"] = int(i)

    payload: Dict[str, Any] = {
        "schema_version": "v3_order3_order12_bundle_seed_bank_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "phase_count": 4,
        "s960_size": int(s960_size),
        "order12_subgroup_count": int(len(rows)),
        "unique_order3_core_count": int(len(core_set)),
        "bijection_ok": bool(len(rows) == 56 and len(core_set) == 56),
    }
    payload["replay_hash"] = _sha_payload(payload)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "bundle_id",
                "clock_id",
                "period",
                "rep_id",
                "generator_id",
                "core_order3_id",
                "bundle4_ids",
                "bundle4_seed_id",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write(_render_md(payload))
        f.write("\n")

    return payload


def main() -> None:
    _ = argparse.ArgumentParser(description="Build v3 order3/order12 bundle seed bank.")
    payload = build_payload()
    print(f"order12_subgroup_count={payload['order12_subgroup_count']}")
    print(f"unique_order3_core_count={payload['unique_order3_core_count']}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()


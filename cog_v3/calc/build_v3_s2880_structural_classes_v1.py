"""Derive structural classes from S2880 invariants + action fingerprints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from cog_v3.calc import v3_s2880_utils as u
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = u.repo_root()
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_s2880_structural_classes_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"

INVARIANT_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_invariants_v1.csv"
FINGERPRINT_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_action_fingerprints_v1.csv"

OUT_CLASS_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_structural_classes_v1.csv"
OUT_MAP_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_element_class_map_v1.csv"
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_s2880_structural_classes_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_s2880_structural_classes_v1.md"


def _qbin(x: float, step: float = 0.05) -> float:
    if step <= 0:
        return float(x)
    return float(round(float(x) / float(step)) * float(step))


def _render_md(payload: Dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# v3 S2880 Structural Classes (v1)",
        "",
        f"- element_count: `{s['element_count']}`",
        f"- class_count: `{s['class_count']}`",
        f"- largest_class_size: `{s['largest_class_size']}`",
        "",
        "## Top classes",
        "",
        "| class_id | count | order | family | phase_mod3 | dominant_dp | dominant_dg |",
        "|---|---:|---:|---|---:|---:|---:|",
    ]
    for row in payload["top_classes"]:
        lines.append(
            f"| `{row['class_id']}` | {row['count']} | {row['order']} | "
            f"`{row['q_family_tag']}` | {row['phase_sector_mod3']} | {row['dominant_dp_left']} | {row['dominant_dg_left']} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_payload() -> Dict[str, Any]:
    if not INVARIANT_CSV.exists():
        raise FileNotFoundError(f"Missing invariants CSV: {INVARIANT_CSV}")
    if not FINGERPRINT_CSV.exists():
        raise FileNotFoundError(f"Missing fingerprint CSV: {FINGERPRINT_CSV}")

    inv_rows = u.read_csv_rows(INVARIANT_CSV)
    fp_rows = u.read_csv_rows(FINGERPRINT_CSV)
    fp_by_sid = {int(r["s_id"]): r for r in fp_rows}

    class_key_to_rows: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = {}
    merged_rows: List[Dict[str, Any]] = []
    for inv in inv_rows:
        sid = int(inv["s_id"])
        fp = fp_by_sid.get(int(sid))
        if fp is None:
            continue
        key = (
            int(inv["order"]),
            str(inv["q_family_tag"]),
            str(inv["q_g2_proxy_tag"]),
            int(inv["phase_sector_mod3"]),
            int(inv["phase_sector_mod4"]),
            int(inv["inner_conj_l_orbit_size"]),
            int(inv["inner_conj_r_orbit_size"]),
            int(inv["q_centralizer_size"]),
            int(fp["dominant_dp_left"]),
            int(fp["dominant_dg_left"]),
            _qbin(float(fp["commute_rate_probe"]), step=0.05),
            _qbin(float(fp["assoc_nonzero_rate"]), step=0.05),
            _qbin(float(fp["probe_order_preserve_rate"]), step=0.05),
            _qbin(float(fp["family_transition_entropy"]), step=0.10),
        )
        row = {
            "s_id": int(sid),
            "label": str(inv["label"]),
            "order": int(inv["order"]),
            "q_family_tag": str(inv["q_family_tag"]),
            "q_g2_proxy_tag": str(inv["q_g2_proxy_tag"]),
            "phase_sector_mod3": int(inv["phase_sector_mod3"]),
            "phase_sector_mod4": int(inv["phase_sector_mod4"]),
            "inner_conj_l_orbit_size": int(inv["inner_conj_l_orbit_size"]),
            "inner_conj_r_orbit_size": int(inv["inner_conj_r_orbit_size"]),
            "q_centralizer_size": int(inv["q_centralizer_size"]),
            "dominant_dp_left": int(fp["dominant_dp_left"]),
            "dominant_dg_left": int(fp["dominant_dg_left"]),
            "commute_rate_probe": float(fp["commute_rate_probe"]),
            "assoc_nonzero_rate": float(fp["assoc_nonzero_rate"]),
            "probe_order_preserve_rate": float(fp["probe_order_preserve_rate"]),
            "family_transition_entropy": float(fp["family_transition_entropy"]),
            "_class_key": key,
        }
        merged_rows.append(row)
        class_key_to_rows.setdefault(key, []).append(row)

    # deterministic class ids by (size desc, key)
    class_items = list(class_key_to_rows.items())
    class_items.sort(key=lambda kv: (-len(kv[1]), kv[0]))
    class_id_by_key = {k0: f"SC{idx:04d}" for idx, (k0, _) in enumerate(class_items, start=1)}

    map_rows: List[Dict[str, Any]] = []
    class_rows: List[Dict[str, Any]] = []
    for key, members in class_items:
        cid = class_id_by_key[key]
        count = len(members)
        m0 = members[0]
        class_rows.append(
            {
                "class_id": cid,
                "count": int(count),
                "order": int(m0["order"]),
                "q_family_tag": str(m0["q_family_tag"]),
                "q_g2_proxy_tag": str(m0["q_g2_proxy_tag"]),
                "phase_sector_mod3": int(m0["phase_sector_mod3"]),
                "phase_sector_mod4": int(m0["phase_sector_mod4"]),
                "inner_conj_l_orbit_size": int(m0["inner_conj_l_orbit_size"]),
                "inner_conj_r_orbit_size": int(m0["inner_conj_r_orbit_size"]),
                "q_centralizer_size": int(m0["q_centralizer_size"]),
                "dominant_dp_left": int(m0["dominant_dp_left"]),
                "dominant_dg_left": int(m0["dominant_dg_left"]),
                "commute_rate_probe_mean": float(sum(float(x["commute_rate_probe"]) for x in members) / max(1, count)),
                "assoc_nonzero_rate_mean": float(sum(float(x["assoc_nonzero_rate"]) for x in members) / max(1, count)),
                "probe_order_preserve_rate_mean": float(
                    sum(float(x["probe_order_preserve_rate"]) for x in members) / max(1, count)
                ),
                "family_transition_entropy_mean": float(
                    sum(float(x["family_transition_entropy"]) for x in members) / max(1, count)
                ),
                "member_sids": "|".join(str(int(x["s_id"])) for x in sorted(members, key=lambda r: int(r["s_id"]))),
            }
        )
        for m in members:
            map_rows.append(
                {
                    "s_id": int(m["s_id"]),
                    "label": str(m["label"]),
                    "class_id": cid,
                    "order": int(m["order"]),
                    "q_family_tag": str(m["q_family_tag"]),
                    "phase_sector_mod3": int(m["phase_sector_mod3"]),
                    "dominant_dp_left": int(m["dominant_dp_left"]),
                    "dominant_dg_left": int(m["dominant_dg_left"]),
                    "commute_rate_probe": f"{float(m['commute_rate_probe']):.6f}",
                    "assoc_nonzero_rate": f"{float(m['assoc_nonzero_rate']):.6f}",
                    "probe_order_preserve_rate": f"{float(m['probe_order_preserve_rate']):.6f}",
                    "family_transition_entropy": f"{float(m['family_transition_entropy']):.6f}",
                }
            )

    class_fields = [
        "class_id",
        "count",
        "order",
        "q_family_tag",
        "q_g2_proxy_tag",
        "phase_sector_mod3",
        "phase_sector_mod4",
        "inner_conj_l_orbit_size",
        "inner_conj_r_orbit_size",
        "q_centralizer_size",
        "dominant_dp_left",
        "dominant_dg_left",
        "commute_rate_probe_mean",
        "assoc_nonzero_rate_mean",
        "probe_order_preserve_rate_mean",
        "family_transition_entropy_mean",
        "member_sids",
    ]
    map_fields = [
        "s_id",
        "label",
        "class_id",
        "order",
        "q_family_tag",
        "phase_sector_mod3",
        "dominant_dp_left",
        "dominant_dg_left",
        "commute_rate_probe",
        "assoc_nonzero_rate",
        "probe_order_preserve_rate",
        "family_transition_entropy",
    ]
    u.write_csv_rows(OUT_CLASS_CSV, fieldnames=class_fields, rows=class_rows)
    u.write_csv_rows(OUT_MAP_CSV, fieldnames=map_fields, rows=map_rows)

    top_classes = [
        {
            "class_id": r["class_id"],
            "count": int(r["count"]),
            "order": int(r["order"]),
            "q_family_tag": str(r["q_family_tag"]),
            "phase_sector_mod3": int(r["phase_sector_mod3"]),
            "dominant_dp_left": int(r["dominant_dp_left"]),
            "dominant_dg_left": int(r["dominant_dg_left"]),
        }
        for r in sorted(class_rows, key=lambda rr: int(rr["count"]), reverse=True)[:20]
    ]
    payload: Dict[str, Any] = {
        "schema_version": "v3_s2880_structural_classes_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": u.sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": u.sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "summary": {
            "element_count": int(len(map_rows)),
            "class_count": int(len(class_rows)),
            "largest_class_size": int(max((int(r["count"]) for r in class_rows), default=0)),
        },
        "checks": {
            "map_row_count_ok": bool(len(map_rows) == len(inv_rows)),
            "class_count_positive": bool(len(class_rows) > 0),
        },
        "top_classes": top_classes,
    }
    payload["replay_hash"] = u.sha_payload(payload)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Build S2880 structural classes.")
    _ = ap.parse_args()
    payload = build_payload()
    print(f"class_count={payload['summary']['class_count']}")
    print(f"largest_class_size={payload['summary']['largest_class_size']}")
    print(f"Wrote {OUT_CLASS_CSV}")
    print(f"Wrote {OUT_MAP_CSV}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()


"""Build full S2880 invariant catalog (C12 x Q240)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from cog_v3.calc import v3_s2880_utils as u
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = u.repo_root()
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_s2880_invariants_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"

OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_invariants_v1.csv"
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_s2880_invariants_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_s2880_invariants_v1.md"


def _render_md(payload: Dict[str, Any]) -> str:
    s = payload["summary"]
    return "\n".join(
        [
            "# v3 S2880 Invariants (v1)",
            "",
            f"- kernel_profile: `{payload['kernel_profile']}`",
            f"- convention_id: `{payload['convention_id']}`",
            f"- phase_count: `{payload['params']['phase_count']}`",
            f"- q_alphabet_size: `{payload['params']['q_alphabet_size']}`",
            f"- s2880_size: `{s['s2880_size']}`",
            f"- distinct_orders: `{','.join(str(x) for x in s['distinct_orders'])}`",
            f"- q_family_counts: `{s['q_family_counts']}`",
            f"- phase_sector_mod3_counts: `{s['phase_sector_mod3_counts']}`",
            f"- max_inner_conj_l_orbit_size: `{s['max_inner_conj_l_orbit_size']}`",
            f"- max_inner_conj_r_orbit_size: `{s['max_inner_conj_r_orbit_size']}`",
            "",
            "## Notes",
            "",
            "- Inner-conjugation and centralizer invariants are derived exactly on the Q240 factor",
            "  and lifted to S2880 (phase index is preserved under conjugation).",
            "- This artifact is the structural base table used by fingerprinting and role catalog scripts.",
            "",
        ]
    )


def build_payload(*, phase_count: int = u.PHASE_COUNT) -> Dict[str, Any]:
    qmul = u.qmul_table()
    qn = int(qmul.shape[0])
    s_size = int(phase_count * qn)
    q_orders, q_inv = u.q_orders_and_inverses(qmul=qmul)
    q_meta = u.q_meta(q_orders=q_orders, q_inv=q_inv, qmul=qmul)
    q_meta_by_id = {int(r["q_id"]): r for r in q_meta}
    q_group = u.q_conjugation_and_centralizers(qmul=qmul, q_inv=q_inv)

    rows: List[Dict[str, Any]] = []
    order_hist: Dict[int, int] = {}
    phase3_hist: Dict[int, int] = {0: 0, 1: 0, 2: 0}
    q_family_hist: Dict[str, int] = {}

    for s_id in range(s_size):
        p, q_id = u.phase_q_from_sid(int(s_id), phase_count=phase_count, qn=qn)
        qm = q_meta_by_id[int(q_id)]
        po = u.phase_order(int(p), phase_count=phase_count)
        qo = int(qm["q_order"])
        so = u.s_order(int(p), int(qo), phase_count=phase_count)
        p_inv = int((-int(p)) % int(phase_count))
        q_inv_id = int(qm["q_inverse_id"])
        inv_sid = u.sid(int(p_inv), int(q_inv_id), phase_count=phase_count, qn=qn)
        sq_sid = u.s_mul_sid(int(s_id), int(s_id), qmul=qmul, phase_count=phase_count)
        cube_sid = u.s_mul_sid(int(sq_sid), int(s_id), qmul=qmul, phase_count=phase_count)
        neg_phase_sid = u.sid(int((int(p) + phase_count // 2) % phase_count), int(q_id), phase_count=phase_count, qn=qn)
        s_centralizer_size = int(phase_count) * int(q_group["q_centralizer_size"][int(q_id)])

        row = {
            "s_id": int(s_id),
            "label": u.label_sid(int(s_id), phase_count=phase_count, qn=qn),
            "phase_idx": int(p),
            "phase_label": u.PHASE_LABELS[int(p)],
            "phase_angle_deg": f"{u.phase_angle_deg(int(p), phase_count=phase_count):.1f}",
            "phase_order": int(po),
            "phase_sector_mod3": int(p % 3),
            "phase_sector_mod4": int(p % 4),
            "q_id": int(q_id),
            "q_label": str(qm["q_label"]),
            "q_order": int(qo),
            "q_inverse_id": int(q_inv_id),
            "q_family_tag": str(qm["q_family_tag"]),
            "q_g2_proxy_tag": str(qm["q_g2_proxy_tag"]),
            "q_support_size": int(qm["q_support_size"]),
            "q_support_mask_bin": str(qm["q_support_mask_bin"]),
            "q_has_e000": str(bool(qm["q_has_e000"])).lower(),
            "q_has_e111": str(bool(qm["q_has_e111"])).lower(),
            "order": int(so),
            "inverse_sid": int(inv_sid),
            "square_sid": int(sq_sid),
            "cube_sid": int(cube_sid),
            "neg_phase_sid": int(neg_phase_sid),
            "is_self_inverse": str(bool(int(sq_sid) == u.sid(0, int(k.IDENTITY_ID), phase_count=phase_count, qn=qn))).lower(),
            "inner_conj_l_orbit_size": int(q_group["left_orbit_size"][int(q_id)]),
            "inner_conj_r_orbit_size": int(q_group["right_orbit_size"][int(q_id)]),
            "q_conj_l_rep": int(q_group["left_rep"][int(q_id)]),
            "q_conj_r_rep": int(q_group["right_rep"][int(q_id)]),
            "q_centralizer_size": int(q_group["q_centralizer_size"][int(q_id)]),
            "s_centralizer_size": int(s_centralizer_size),
            "conj_class_id_l": f"p{int(p)}_ql{int(q_group['left_rep'][int(q_id)])}",
            "conj_class_id_r": f"p{int(p)}_qr{int(q_group['right_rep'][int(q_id)])}",
            **{f"q_{lab}": str(qm["q_coeffs"][i]) for i, lab in enumerate(u.BASIS_LABELS)},
            **{f"c_{lab}": u.frac_to_complex_phase_coeff(qm["q_coeffs"][i], int(p), phase_count=phase_count) for i, lab in enumerate(u.BASIS_LABELS)},
        }
        rows.append(row)

        order_hist[int(so)] = int(order_hist.get(int(so), 0) + 1)
        phase3_hist[int(p % 3)] = int(phase3_hist[int(p % 3)] + 1)
        fam = str(qm["q_family_tag"])
        q_family_hist[fam] = int(q_family_hist.get(fam, 0) + 1)

    fields = [
        "s_id",
        "label",
        "phase_idx",
        "phase_label",
        "phase_angle_deg",
        "phase_order",
        "phase_sector_mod3",
        "phase_sector_mod4",
        "q_id",
        "q_label",
        "q_order",
        "q_inverse_id",
        "q_family_tag",
        "q_g2_proxy_tag",
        "q_support_size",
        "q_support_mask_bin",
        "q_has_e000",
        "q_has_e111",
        "order",
        "inverse_sid",
        "square_sid",
        "cube_sid",
        "neg_phase_sid",
        "is_self_inverse",
        "inner_conj_l_orbit_size",
        "inner_conj_r_orbit_size",
        "q_conj_l_rep",
        "q_conj_r_rep",
        "q_centralizer_size",
        "s_centralizer_size",
        "conj_class_id_l",
        "conj_class_id_r",
        *[f"q_{lab}" for lab in u.BASIS_LABELS],
        *[f"c_{lab}" for lab in u.BASIS_LABELS],
    ]
    u.write_csv_rows(OUT_CSV, fieldnames=fields, rows=rows)

    payload: Dict[str, Any] = {
        "schema_version": "v3_s2880_invariants_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": u.sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": u.sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "params": {
            "phase_count": int(phase_count),
            "q_alphabet_size": int(qn),
        },
        "summary": {
            "s2880_size": int(s_size),
            "distinct_orders": [int(x) for x in sorted(order_hist.keys())],
            "order_hist": {str(int(k0)): int(v0) for k0, v0 in sorted(order_hist.items())},
            "phase_sector_mod3_counts": {str(int(k0)): int(v0) for k0, v0 in sorted(phase3_hist.items())},
            "q_family_counts": {str(k0): int(v0) for k0, v0 in sorted(q_family_hist.items())},
            "max_inner_conj_l_orbit_size": int(max(int(x["inner_conj_l_orbit_size"]) for x in rows)),
            "max_inner_conj_r_orbit_size": int(max(int(x["inner_conj_r_orbit_size"]) for x in rows)),
        },
        "checks": {
            "row_count_ok": bool(len(rows) == int(s_size)),
            "all_orders_positive": bool(all(int(r["order"]) > 0 for r in rows)),
        },
    }
    payload["replay_hash"] = u.sha_payload(payload)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Build S2880 invariants catalog.")
    ap.add_argument("--phase-count", type=int, default=u.PHASE_COUNT)
    args = ap.parse_args()
    payload = build_payload(phase_count=int(args.phase_count))
    print(f"s2880_size={payload['summary']['s2880_size']}")
    print(f"distinct_orders={payload['summary']['distinct_orders']}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()


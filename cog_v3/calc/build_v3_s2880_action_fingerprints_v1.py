"""Build action fingerprints for every S2880 element."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

from cog_v3.calc import v3_s2880_utils as u
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = u.repo_root()
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_s2880_action_fingerprints_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"
INVARIANT_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_invariants_v1.csv"

OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_action_fingerprints_v1.csv"
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_s2880_action_fingerprints_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_s2880_action_fingerprints_v1.md"

FAMILY_CODES = {
    "A16_basis_signed_unit": 0,
    "B112_line_plus_e000_halfsum": 1,
    "C112_complement_halfsum": 2,
    "other": 3,
}
FAMILY_LABELS = ["A16_basis_signed_unit", "B112_line_plus_e000_halfsum", "C112_complement_halfsum", "other"]


def _parse_probe_seed_order3(q_orders: Sequence[int]) -> List[int]:
    return [int(i) for i, o in enumerate(q_orders) if int(o) == 3]


def _parse_probe_seed_order6(q_orders: Sequence[int]) -> List[int]:
    return [int(i) for i, o in enumerate(q_orders) if int(o) == 6]


def _parse_probe_seed_basis(q_meta: Sequence[Dict[str, Any]]) -> List[int]:
    out: List[int] = []
    for row in q_meta:
        if int(row["q_support_size"]) == 1:
            out.append(int(row["q_id"]))
    return out


def _build_probe_sids(
    *,
    phase_count: int,
    qn: int,
    q_orders: Sequence[int],
    q_meta: Sequence[Dict[str, Any]],
    use_phase_set: Sequence[int],
) -> List[int]:
    order3 = _parse_probe_seed_order3(q_orders)
    order6 = _parse_probe_seed_order6(q_orders)
    basis = _parse_probe_seed_basis(q_meta)
    q_ids = sorted(set([int(k.IDENTITY_ID)] + [int(x) for x in order3] + [int(x) for x in order6] + [int(x) for x in basis]))
    out: List[int] = []
    for p in use_phase_set:
        pp = int(p) % int(phase_count)
        for q_id in q_ids:
            out.append(u.sid(int(pp), int(q_id), phase_count=phase_count, qn=qn))
    return sorted(set(out))


def _family_transition_entropy(counts: Sequence[Sequence[int]]) -> float:
    flat: List[int] = []
    for row in counts:
        for v in row:
            flat.append(int(v))
    return u.entropy_from_counts(flat)


def _associator_nonzero_rate(
    *,
    actor_sid: int,
    anchor_sids: Sequence[int],
    qmul,
    phase_count: int,
) -> float:
    total = 0
    nz = 0
    anchors = list(anchor_sids)
    n = len(anchors)
    if n == 0:
        return 0.0
    for i in range(n):
        b = int(anchors[i])
        c = int(anchors[(i + 1) % n])
        lhs = u.s_mul_sid(u.s_mul_sid(int(actor_sid), int(b), qmul=qmul, phase_count=phase_count), int(c), qmul=qmul, phase_count=phase_count)
        rhs = u.s_mul_sid(int(actor_sid), u.s_mul_sid(int(b), int(c), qmul=qmul, phase_count=phase_count), qmul=qmul, phase_count=phase_count)
        total += 1
        if int(lhs) != int(rhs):
            nz += 1
    return float(nz) / float(total) if total > 0 else 0.0


def _render_md(payload: Dict[str, Any]) -> str:
    s = payload["summary"]
    return "\n".join(
        [
            "# v3 S2880 Action Fingerprints (v1)",
            "",
            f"- element_count: `{s['element_count']}`",
            f"- probe_count: `{s['probe_count']}`",
            f"- anchor_count: `{s['anchor_count']}`",
            f"- mean_commute_rate: `{s['mean_commute_rate']:.6f}`",
            f"- mean_assoc_nonzero_rate: `{s['mean_assoc_nonzero_rate']:.6f}`",
            f"- mean_probe_order_preserve_rate: `{s['mean_probe_order_preserve_rate']:.6f}`",
            "",
            "## Notes",
            "",
            "- Fingerprints are actor-level summaries over a fixed probe bank.",
            "- These are used for structural classing and role-prior scoring.",
            "",
        ]
    )


def build_payload(
    *,
    phase_count: int = u.PHASE_COUNT,
    probe_phases: Sequence[int] = (0, 1, 2),
) -> Dict[str, Any]:
    if not INVARIANT_CSV.exists():
        raise FileNotFoundError(f"Missing invariants CSV: {INVARIANT_CSV}")
    inv_rows = u.read_csv_rows(INVARIANT_CSV)
    qmul = u.qmul_table()
    qn = int(qmul.shape[0])
    q_orders, q_inv = u.q_orders_and_inverses(qmul=qmul)
    q_meta = u.q_meta(q_orders=q_orders, q_inv=q_inv, qmul=qmul)
    inv_by_sid = {int(r["s_id"]): r for r in inv_rows}

    probe_sids = _build_probe_sids(
        phase_count=phase_count,
        qn=qn,
        q_orders=q_orders,
        q_meta=q_meta,
        use_phase_set=probe_phases,
    )
    # Anchors for associator checks: identity + first 15 basis/order3 probes at phase 0.
    anchor_q = sorted(
        set([int(k.IDENTITY_ID)] + _parse_probe_seed_basis(q_meta) + _parse_probe_seed_order3(q_orders))
    )[:16]
    anchor_sids = [u.sid(0, int(q_id), phase_count=phase_count, qn=qn) for q_id in anchor_q]

    out_rows: List[Dict[str, Any]] = []
    for s_id in sorted(inv_by_sid.keys()):
        actor = int(s_id)
        dp_hist = [0] * int(phase_count)
        dg_hist = [0, 0, 0]
        commute = 0
        order_pres = 0
        fam_pres = 0
        fam_trans = [[0] * 4 for _ in range(4)]

        for probe in probe_sids:
            left = u.s_mul_sid(int(actor), int(probe), qmul=qmul, phase_count=phase_count)
            right = u.s_mul_sid(int(probe), int(actor), qmul=qmul, phase_count=phase_count)
            if int(left) == int(right):
                commute += 1

            p0, _ = u.phase_q_from_sid(int(probe), phase_count=phase_count, qn=qn)
            p1, _ = u.phase_q_from_sid(int(left), phase_count=phase_count, qn=qn)
            dp = int((int(p1) - int(p0)) % int(phase_count))
            dp_hist[int(dp)] += 1
            dg = int((int(p1 % 3) - int(p0 % 3)) % 3)
            dg_hist[int(dg)] += 1

            ord0 = int(inv_by_sid[int(probe)]["order"])
            ord1 = int(inv_by_sid[int(left)]["order"])
            if int(ord0) == int(ord1):
                order_pres += 1

            f0 = str(inv_by_sid[int(probe)]["q_family_tag"])
            f1 = str(inv_by_sid[int(left)]["q_family_tag"])
            c0 = int(FAMILY_CODES.get(f0, 3))
            c1 = int(FAMILY_CODES.get(f1, 3))
            fam_trans[c0][c1] += 1
            if int(c0) == int(c1):
                fam_pres += 1

        probe_count = int(len(probe_sids))
        assoc_nz = _associator_nonzero_rate(actor_sid=int(actor), anchor_sids=anchor_sids, qmul=qmul, phase_count=phase_count)
        dp_dom = int(max(range(int(phase_count)), key=lambda i: dp_hist[int(i)]))
        dg_dom = int(max(range(3), key=lambda i: dg_hist[int(i)]))
        fam_entropy = _family_transition_entropy(fam_trans)

        row = {
            "s_id": int(actor),
            "phase_idx": int(inv_by_sid[int(actor)]["phase_idx"]),
            "q_id": int(inv_by_sid[int(actor)]["q_id"]),
            "order": int(inv_by_sid[int(actor)]["order"]),
            "q_family_tag": str(inv_by_sid[int(actor)]["q_family_tag"]),
            "probe_count": int(probe_count),
            "anchor_count": int(len(anchor_sids)),
            "commute_rate_probe": float(commute / probe_count if probe_count else 0.0),
            "probe_order_preserve_rate": float(order_pres / probe_count if probe_count else 0.0),
            "probe_family_preserve_rate": float(fam_pres / probe_count if probe_count else 0.0),
            "family_transition_entropy": float(fam_entropy),
            "assoc_nonzero_rate": float(assoc_nz),
            "dominant_dp_left": int(dp_dom),
            "dominant_dg_left": int(dg_dom),
            "dp_hist": "|".join(str(int(x)) for x in dp_hist),
            "dg_hist": "|".join(str(int(x)) for x in dg_hist),
            "family_transition_matrix": "|".join(
                ",".join(str(int(x)) for x in fam_trans[r]) for r in range(4)
            ),
        }
        out_rows.append(row)

    fields = [
        "s_id",
        "phase_idx",
        "q_id",
        "order",
        "q_family_tag",
        "probe_count",
        "anchor_count",
        "commute_rate_probe",
        "probe_order_preserve_rate",
        "probe_family_preserve_rate",
        "family_transition_entropy",
        "assoc_nonzero_rate",
        "dominant_dp_left",
        "dominant_dg_left",
        "dp_hist",
        "dg_hist",
        "family_transition_matrix",
    ]
    u.write_csv_rows(OUT_CSV, fieldnames=fields, rows=out_rows)

    payload: Dict[str, Any] = {
        "schema_version": "v3_s2880_action_fingerprints_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": u.sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": u.sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "params": {
            "phase_count": int(phase_count),
            "probe_phases": [int(x) for x in probe_phases],
        },
        "summary": {
            "element_count": int(len(out_rows)),
            "probe_count": int(len(probe_sids)),
            "anchor_count": int(len(anchor_sids)),
            "mean_commute_rate": float(sum(float(r["commute_rate_probe"]) for r in out_rows) / max(1, len(out_rows))),
            "mean_assoc_nonzero_rate": float(sum(float(r["assoc_nonzero_rate"]) for r in out_rows) / max(1, len(out_rows))),
            "mean_probe_order_preserve_rate": float(
                sum(float(r["probe_order_preserve_rate"]) for r in out_rows) / max(1, len(out_rows))
            ),
            "dominant_dp_hist": {
                str(i): int(sum(1 for r in out_rows if int(r["dominant_dp_left"]) == i))
                for i in range(int(phase_count))
            },
            "dominant_dg_hist": {
                str(i): int(sum(1 for r in out_rows if int(r["dominant_dg_left"]) == i))
                for i in range(3)
            },
        },
        "checks": {
            "row_count_ok": bool(len(out_rows) == int(phase_count * qn)),
            "probe_count_positive": bool(len(probe_sids) > 0),
            "anchor_count_positive": bool(len(anchor_sids) > 0),
        },
    }
    payload["replay_hash"] = u.sha_payload(payload)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Build S2880 action fingerprints.")
    ap.add_argument("--phase-count", type=int, default=u.PHASE_COUNT)
    ap.add_argument("--probe-phases", type=str, default="0,1,2")
    args = ap.parse_args()
    probe_phases = [int(x.strip()) for x in str(args.probe_phases).split(",") if x.strip() != ""]
    payload = build_payload(phase_count=int(args.phase_count), probe_phases=probe_phases)
    print(f"element_count={payload['summary']['element_count']}")
    print(f"probe_count={payload['summary']['probe_count']}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()


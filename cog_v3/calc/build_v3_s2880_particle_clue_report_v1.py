"""S2880 particle-clue report and seed-prior extraction.

This is an analysis layer over existing S2880 artifacts:
- invariants
- action fingerprints
- particle/interaction role catalog

Outputs:
- clue report JSON/MD
- compact seed-prior CSV for search runners
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v3.calc import v3_s2880_utils as u
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = u.repo_root()
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_s2880_particle_clue_report_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"

INVARIANT_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_invariants_v1.csv"
FINGERPRINT_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_action_fingerprints_v1.csv"
CATALOG_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_interaction_catalog_v1.csv"

OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_clue_report_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_clue_report_v1.md"
OUT_PRIOR_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_seed_priors_v1.csv"

ROLE_FIELDS = [
    ("photon_like", "score_photon_like"),
    ("neutrino_like", "score_neutrino_like"),
    ("electron_like", "score_electron_like"),
    ("quark_core_like", "score_quark_core_like"),
    ("mediator_w_like", "score_mediator_w_like"),
    ("unstable_crossmix_like", "score_unstable_crossmix_like"),
]


def _merge_rows() -> List[Dict[str, Any]]:
    inv_rows = u.read_csv_rows(INVARIANT_CSV)
    fp_rows = u.read_csv_rows(FINGERPRINT_CSV)
    cat_rows = u.read_csv_rows(CATALOG_CSV)
    inv_by = {int(r["s_id"]): r for r in inv_rows}
    fp_by = {int(r["s_id"]): r for r in fp_rows}
    out: List[Dict[str, Any]] = []
    for c in cat_rows:
        sid = int(c["s_id"])
        inv = inv_by[int(sid)]
        fp = fp_by[int(sid)]
        row = {
            "s_id": int(sid),
            "label": str(c["label"]),
            "class_id": str(c["class_id"]),
            "phase_idx": int(c["phase_idx"]),
            "phase_sector_mod3": int(inv["phase_sector_mod3"]),
            "q_id": int(c["q_id"]),
            "q_order": int(c["q_order"]),
            "order": int(c["order"]),
            "q_family_tag": str(c["q_family_tag"]),
            "top_role_1": str(c["top_role_1"]),
            "top_role_1_score": float(c["top_role_1_score"]),
            "dominant_dp_left": int(fp["dominant_dp_left"]),
            "dominant_dg_left": int(fp["dominant_dg_left"]),
            "commute_rate_probe": float(fp["commute_rate_probe"]),
            "assoc_nonzero_rate": float(fp["assoc_nonzero_rate"]),
            "probe_order_preserve_rate": float(fp["probe_order_preserve_rate"]),
            "family_transition_entropy": float(fp["family_transition_entropy"]),
        }
        for role_name, field in ROLE_FIELDS:
            row[field] = float(c[field])
        out.append(row)
    return out


def _mean(vals: Sequence[float]) -> float:
    if not vals:
        return 0.0
    return float(sum(float(v) for v in vals) / float(len(vals)))


def _aggregate_by_order_family_g(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets: Dict[Tuple[int, str, int], List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        key = (int(r["order"]), str(r["q_family_tag"]), int(r["phase_sector_mod3"]))
        buckets[key].append(r)
    out: List[Dict[str, Any]] = []
    for key, members in buckets.items():
        order, family, g = key
        rec = {
            "order": int(order),
            "q_family_tag": str(family),
            "phase_sector_mod3": int(g),
            "count": int(len(members)),
        }
        for role_name, field in ROLE_FIELDS:
            rec[f"{role_name}_mean"] = _mean([float(m[field]) for m in members])
        out.append(rec)
    out.sort(key=lambda r: (int(r["order"]), str(r["q_family_tag"]), int(r["phase_sector_mod3"])))
    return out


def _generation_triads(rows: Sequence[Dict[str, Any]], *, role_field: str, top_n: int = 40) -> List[Dict[str, Any]]:
    by_qid_g: Dict[Tuple[int, int], List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_qid_g[(int(r["q_id"]), int(r["phase_sector_mod3"]))].append(r)

    triads: List[Dict[str, Any]] = []
    all_qids = sorted({int(r["q_id"]) for r in rows})
    for q_id in all_qids:
        best: Dict[int, Dict[str, Any]] = {}
        ok = True
        for g in (0, 1, 2):
            cand = by_qid_g.get((int(q_id), int(g)), [])
            if not cand:
                ok = False
                break
            cand_sorted = sorted(cand, key=lambda x: float(x[role_field]), reverse=True)
            best[int(g)] = cand_sorted[0]
        if not ok:
            continue
        s0 = float(best[0][role_field])
        s1 = float(best[1][role_field])
        s2 = float(best[2][role_field])
        mean = (s0 + s1 + s2) / 3.0
        spread = max(s0, s1, s2) - min(s0, s1, s2)
        coherence = 1.0 - spread
        triads.append(
            {
                "q_id": int(q_id),
                "sids": [int(best[g]["s_id"]) for g in (0, 1, 2)],
                "scores": [float(best[g][role_field]) for g in (0, 1, 2)],
                "score_mean": float(mean),
                "score_spread": float(spread),
                "coherence": float(coherence),
                "families": [str(best[g]["q_family_tag"]) for g in (0, 1, 2)],
                "orders": [int(best[g]["order"]) for g in (0, 1, 2)],
            }
        )
    triads.sort(key=lambda r: (float(r["score_mean"]), float(r["coherence"])), reverse=True)
    return triads[: int(top_n)]


def _seed_priors(rows: Sequence[Dict[str, Any]], *, top_per_role: int = 120) -> List[Dict[str, Any]]:
    priors: List[Dict[str, Any]] = []
    role_constraints = {
        "photon_like": lambda r: int(r["q_id"]) == int(k.IDENTITY_ID),
        "neutrino_like": lambda r: int(r["q_id"]) == int(k.IDENTITY_ID) and str(r["q_family_tag"]) == "A16_basis_signed_unit",
        "electron_like": lambda r: str(r["q_family_tag"]) == "B112_line_plus_e000_halfsum",
        "quark_core_like": lambda r: int(r["q_order"]) == 3,
        "mediator_w_like": lambda r: int(r["dominant_dg_left"]) != 0,
        "unstable_crossmix_like": lambda r: float(r["family_transition_entropy"]) >= 0.9,
    }
    role_rationale = {
        "photon_like": "identity-q, high phase transport candidate",
        "neutrino_like": "A-family identity-q with weakly interacting profile",
        "electron_like": "B-family stable nontrivial order candidate",
        "quark_core_like": "order-3 q-core prior",
        "mediator_w_like": "nonzero generation-hop dominant_dg",
        "unstable_crossmix_like": "high family-transition entropy",
    }
    for role_name, field in ROLE_FIELDS:
        filt = [r for r in rows if role_constraints[role_name](r)]
        if not filt:
            filt = list(rows)
        ranked = sorted(filt, key=lambda r: float(r[field]), reverse=True)[: int(top_per_role)]
        for rank, r in enumerate(ranked, start=1):
            priors.append(
                {
                    "role": str(role_name),
                    "priority_rank": int(rank),
                    "s_id": int(r["s_id"]),
                    "class_id": str(r["class_id"]),
                    "phase_idx": int(r["phase_idx"]),
                    "phase_sector_mod3": int(r["phase_sector_mod3"]),
                    "q_id": int(r["q_id"]),
                    "order": int(r["order"]),
                    "q_order": int(r["q_order"]),
                    "q_family_tag": str(r["q_family_tag"]),
                    "dominant_dg_left": int(r["dominant_dg_left"]),
                    "dominant_dp_left": int(r["dominant_dp_left"]),
                    "score": float(r[field]),
                    "rationale": role_rationale[role_name],
                }
            )
    priors.sort(key=lambda r: (str(r["role"]), int(r["priority_rank"])))
    return priors


def _role_top(rows: Sequence[Dict[str, Any]], *, n: int = 30) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for role_name, field in ROLE_FIELDS:
        ranked = sorted(rows, key=lambda r: float(r[field]), reverse=True)[: int(n)]
        out[role_name] = [
            {
                "s_id": int(r["s_id"]),
                "class_id": str(r["class_id"]),
                "phase_idx": int(r["phase_idx"]),
                "q_id": int(r["q_id"]),
                "order": int(r["order"]),
                "q_family_tag": str(r["q_family_tag"]),
                "dominant_dg_left": int(r["dominant_dg_left"]),
                "dominant_dp_left": int(r["dominant_dp_left"]),
                "score": float(r[field]),
            }
            for r in ranked
        ]
    return out


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 S2880 Particle Clue Report (v1)",
        "",
        f"- element_count: `{payload['summary']['element_count']}`",
        f"- seed_prior_rows: `{payload['summary']['seed_prior_rows']}`",
        "",
        "## Top role winners (counts)",
        "",
    ]
    for role, cnt in payload["summary"]["top_role_winner_counts"].items():
        lines.append(f"- {role}: `{cnt}`")
    lines.extend(["", "## Top generation-triads (neutrino_like)", ""])
    tri = payload["generation_triads"]["neutrino_like"][:10]
    lines.append("| q_id | sids(g0,g1,g2) | score_mean | score_spread |")
    lines.append("|---:|---|---:|---:|")
    for t in tri:
        lines.append(
            f"| {t['q_id']} | {','.join(str(x) for x in t['sids'])} | "
            f"{t['score_mean']:.4f} | {t['score_spread']:.4f} |"
        )
    lines.extend(["", "## Notes", "", "- This report is heuristic (role priors), not a claim of particle identification.", ""])
    return "\n".join(lines)


def build_payload(*, top_per_role: int = 120, triad_top_n: int = 40) -> Dict[str, Any]:
    rows = _merge_rows()
    role_top = _role_top(rows, n=30)
    agg = _aggregate_by_order_family_g(rows)
    triads = {
        role_name: _generation_triads(rows, role_field=field, top_n=triad_top_n)
        for role_name, field in ROLE_FIELDS
    }
    seed_priors = _seed_priors(rows, top_per_role=top_per_role)

    prior_fields = [
        "role",
        "priority_rank",
        "s_id",
        "class_id",
        "phase_idx",
        "phase_sector_mod3",
        "q_id",
        "order",
        "q_order",
        "q_family_tag",
        "dominant_dg_left",
        "dominant_dp_left",
        "score",
        "rationale",
    ]
    u.write_csv_rows(OUT_PRIOR_CSV, fieldnames=prior_fields, rows=seed_priors)

    winner_counts: Dict[str, int] = {}
    for r in rows:
        winner_counts[str(r["top_role_1"])] = int(winner_counts.get(str(r["top_role_1"]), 0) + 1)

    payload: Dict[str, Any] = {
        "schema_version": "v3_s2880_particle_clue_report_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": u.sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": u.sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "params": {
            "top_per_role": int(top_per_role),
            "triad_top_n": int(triad_top_n),
        },
        "summary": {
            "element_count": int(len(rows)),
            "seed_prior_rows": int(len(seed_priors)),
            "top_role_winner_counts": {k0: int(v0) for k0, v0 in sorted(winner_counts.items())},
        },
        "role_top": role_top,
        "generation_triads": triads,
        "aggregate_by_order_family_g": agg,
        "checks": {
            "element_count_ok": bool(len(rows) == 2880),
            "seed_prior_nonempty": bool(len(seed_priors) > 0),
        },
    }
    payload["replay_hash"] = u.sha_payload(payload)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Build S2880 particle clue report.")
    ap.add_argument("--top-per-role", type=int, default=120)
    ap.add_argument("--triad-top-n", type=int, default=40)
    args = ap.parse_args()
    payload = build_payload(top_per_role=int(args.top_per_role), triad_top_n=int(args.triad_top_n))
    print(f"element_count={payload['summary']['element_count']}")
    print(f"seed_prior_rows={payload['summary']['seed_prior_rows']}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_PRIOR_CSV}")


if __name__ == "__main__":
    main()


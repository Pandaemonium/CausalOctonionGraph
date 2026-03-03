"""Build heuristic particle/interaction role catalog over S2880."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v3.calc import v3_s2880_utils as u
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = u.repo_root()
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_s2880_particle_interaction_catalog_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"

INVARIANT_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_invariants_v1.csv"
FINGERPRINT_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_action_fingerprints_v1.csv"
CLASS_MAP_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_element_class_map_v1.csv"
CLASS_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_structural_classes_v1.csv"

OUT_ELEM_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_interaction_catalog_v1.csv"
OUT_CLASS_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_interaction_class_catalog_v1.csv"
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_interaction_catalog_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_interaction_catalog_v1.md"

ROLE_NAMES = [
    "photon_like",
    "neutrino_like",
    "electron_like",
    "quark_core_like",
    "mediator_w_like",
    "unstable_crossmix_like",
]


def _clamp01(x: float) -> float:
    return float(max(0.0, min(1.0, float(x))))


def _family_entropy_norm(h: float) -> float:
    # 4x4 matrix entropy upper bound ~4 bits when flattened with uniform occupancy.
    return _clamp01(float(h) / 4.0)


def _assoc_mid(a: float) -> float:
    # peak around 0.5, lower toward 0 or 1
    return _clamp01(1.0 - abs(float(a) - 0.5) / 0.5)


def _score_roles(
    *,
    phase_order: int,
    q_order: int,
    q_id: int,
    q_family_tag: str,
    commute_rate: float,
    assoc_nonzero_rate: float,
    order_preserve_rate: float,
    family_entropy: float,
    dominant_dg: int,
) -> Dict[str, float]:
    is_q_identity = 1.0 if int(q_id) == int(k.IDENTITY_ID) else 0.0
    is_high_phase = 1.0 if int(phase_order) >= 6 else 0.0
    is_phase_gen_changer = 1.0 if int(dominant_dg) != 0 else 0.0
    is_q_order3 = 1.0 if int(q_order) == 3 else 0.0
    fam_a = 1.0 if q_family_tag == "A16_basis_signed_unit" else 0.0
    fam_b = 1.0 if q_family_tag == "B112_line_plus_e000_halfsum" else 0.0
    fam_c = 1.0 if q_family_tag == "C112_complement_halfsum" else 0.0
    fam_non_a = 1.0 if fam_a < 0.5 else 0.0
    ent = _family_entropy_norm(float(family_entropy))
    assoc = _clamp01(float(assoc_nonzero_rate))
    comm = _clamp01(float(commute_rate))
    op = _clamp01(float(order_preserve_rate))

    photon_like = (
        0.45 * is_q_identity
        + 0.20 * is_high_phase
        + 0.20 * comm
        + 0.15 * (1.0 - assoc)
    )
    neutrino_like = (
        0.30 * fam_a
        + 0.20 * is_high_phase
        + 0.25 * (1.0 - assoc)
        + 0.25 * comm
    )
    electron_like = (
        0.25 * fam_b
        + 0.10 * fam_c
        + 0.20 * _assoc_mid(assoc)
        + 0.20 * op
        + 0.15 * (1.0 - is_phase_gen_changer)
        + 0.10 * comm
    )
    quark_core_like = (
        0.35 * is_q_order3
        + 0.20 * fam_non_a
        + 0.25 * assoc
        + 0.20 * (1.0 - comm)
    )
    mediator_w_like = (
        0.40 * is_phase_gen_changer
        + 0.20 * is_high_phase
        + 0.20 * assoc
        + 0.20 * (1.0 - op)
    )
    unstable_crossmix_like = (
        0.30 * assoc
        + 0.25 * (1.0 - comm)
        + 0.25 * ent
        + 0.20 * (1.0 - op)
    )

    return {
        "photon_like": _clamp01(photon_like),
        "neutrino_like": _clamp01(neutrino_like),
        "electron_like": _clamp01(electron_like),
        "quark_core_like": _clamp01(quark_core_like),
        "mediator_w_like": _clamp01(mediator_w_like),
        "unstable_crossmix_like": _clamp01(unstable_crossmix_like),
    }


def _top_roles(scores: Dict[str, float], n: int = 3) -> List[Tuple[str, float]]:
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[: int(n)]


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 S2880 Particle/Interaction Role Catalog (v1)",
        "",
        f"- element_count: `{payload['summary']['element_count']}`",
        f"- class_count: `{payload['summary']['class_count']}`",
        "",
        "## Top element candidates by role",
        "",
    ]
    for role, rows in payload["top_elements_by_role"].items():
        lines.append(f"### {role}")
        lines.append("")
        lines.append("| s_id | class_id | score | label |")
        lines.append("|---:|---|---:|---|")
        for r in rows:
            lines.append(
                f"| {r['s_id']} | `{r['class_id']}` | {r['score']:.4f} | `{r['label']}` |"
            )
        lines.append("")
    return "\n".join(lines)


def build_payload() -> Dict[str, Any]:
    for path in (INVARIANT_CSV, FINGERPRINT_CSV, CLASS_MAP_CSV, CLASS_CSV):
        if not path.exists():
            raise FileNotFoundError(f"Missing required input: {path}")

    inv_rows = u.read_csv_rows(INVARIANT_CSV)
    fp_rows = u.read_csv_rows(FINGERPRINT_CSV)
    map_rows = u.read_csv_rows(CLASS_MAP_CSV)
    cls_rows = u.read_csv_rows(CLASS_CSV)

    inv_by_sid = {int(r["s_id"]): r for r in inv_rows}
    fp_by_sid = {int(r["s_id"]): r for r in fp_rows}
    class_by_sid = {int(r["s_id"]): str(r["class_id"]) for r in map_rows}

    elem_rows: List[Dict[str, Any]] = []
    for s_id in sorted(inv_by_sid.keys()):
        inv = inv_by_sid[int(s_id)]
        fp = fp_by_sid[int(s_id)]
        scores = _score_roles(
            phase_order=int(inv["phase_order"]),
            q_order=int(inv["q_order"]),
            q_id=int(inv["q_id"]),
            q_family_tag=str(inv["q_family_tag"]),
            commute_rate=float(fp["commute_rate_probe"]),
            assoc_nonzero_rate=float(fp["assoc_nonzero_rate"]),
            order_preserve_rate=float(fp["probe_order_preserve_rate"]),
            family_entropy=float(fp["family_transition_entropy"]),
            dominant_dg=int(fp["dominant_dg_left"]),
        )
        top = _top_roles(scores, n=3)
        elem_rows.append(
            {
                "s_id": int(s_id),
                "label": str(inv["label"]),
                "class_id": str(class_by_sid[int(s_id)]),
                "phase_idx": int(inv["phase_idx"]),
                "q_id": int(inv["q_id"]),
                "order": int(inv["order"]),
                "q_order": int(inv["q_order"]),
                "q_family_tag": str(inv["q_family_tag"]),
                "commute_rate_probe": float(fp["commute_rate_probe"]),
                "assoc_nonzero_rate": float(fp["assoc_nonzero_rate"]),
                "probe_order_preserve_rate": float(fp["probe_order_preserve_rate"]),
                "family_transition_entropy": float(fp["family_transition_entropy"]),
                **{f"score_{name}": float(scores[name]) for name in ROLE_NAMES},
                "top_role_1": str(top[0][0]),
                "top_role_1_score": float(top[0][1]),
                "top_role_2": str(top[1][0]),
                "top_role_2_score": float(top[1][1]),
                "top_role_3": str(top[2][0]),
                "top_role_3_score": float(top[2][1]),
            }
        )

    elem_fields = [
        "s_id",
        "label",
        "class_id",
        "phase_idx",
        "q_id",
        "order",
        "q_order",
        "q_family_tag",
        "commute_rate_probe",
        "assoc_nonzero_rate",
        "probe_order_preserve_rate",
        "family_transition_entropy",
        *[f"score_{name}" for name in ROLE_NAMES],
        "top_role_1",
        "top_role_1_score",
        "top_role_2",
        "top_role_2_score",
        "top_role_3",
        "top_role_3_score",
    ]
    u.write_csv_rows(OUT_ELEM_CSV, fieldnames=elem_fields, rows=elem_rows)

    # Class-level aggregation.
    cls_ids = sorted({str(r["class_id"]) for r in cls_rows})
    class_rows: List[Dict[str, Any]] = []
    for cid in cls_ids:
        members = [r for r in elem_rows if str(r["class_id"]) == str(cid)]
        if not members:
            continue
        role_means = {
            role: float(sum(float(m[f"score_{role}"]) for m in members) / max(1, len(members)))
            for role in ROLE_NAMES
        }
        top = _top_roles(role_means, n=3)
        class_rows.append(
            {
                "class_id": str(cid),
                "count": int(len(members)),
                **{f"score_{role}_mean": float(role_means[role]) for role in ROLE_NAMES},
                "top_role_1": str(top[0][0]),
                "top_role_1_score": float(top[0][1]),
                "top_role_2": str(top[1][0]),
                "top_role_2_score": float(top[1][1]),
                "top_role_3": str(top[2][0]),
                "top_role_3_score": float(top[2][1]),
            }
        )
    class_rows.sort(key=lambda r: int(r["count"]), reverse=True)
    class_fields = [
        "class_id",
        "count",
        *[f"score_{role}_mean" for role in ROLE_NAMES],
        "top_role_1",
        "top_role_1_score",
        "top_role_2",
        "top_role_2_score",
        "top_role_3",
        "top_role_3_score",
    ]
    u.write_csv_rows(OUT_CLASS_CSV, fieldnames=class_fields, rows=class_rows)

    top_elements_by_role: Dict[str, List[Dict[str, Any]]] = {}
    for role in ROLE_NAMES:
        key = f"score_{role}"
        top_elements_by_role[role] = [
            {
                "s_id": int(r["s_id"]),
                "class_id": str(r["class_id"]),
                "score": float(r[key]),
                "label": str(r["label"]),
            }
            for r in sorted(elem_rows, key=lambda rr: float(rr[key]), reverse=True)[:20]
        ]

    payload: Dict[str, Any] = {
        "schema_version": "v3_s2880_particle_interaction_catalog_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": u.sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": u.sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "summary": {
            "element_count": int(len(elem_rows)),
            "class_count": int(len(class_rows)),
        },
        "checks": {
            "element_count_ok": bool(len(elem_rows) == len(inv_rows)),
            "class_count_positive": bool(len(class_rows) > 0),
        },
        "top_elements_by_role": top_elements_by_role,
    }
    payload["replay_hash"] = u.sha_payload(payload)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Build S2880 particle/interaction role catalog.")
    _ = ap.parse_args()
    payload = build_payload()
    print(f"element_count={payload['summary']['element_count']}")
    print(f"class_count={payload['summary']['class_count']}")
    print(f"Wrote {OUT_ELEM_CSV}")
    print(f"Wrote {OUT_CLASS_CSV}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()


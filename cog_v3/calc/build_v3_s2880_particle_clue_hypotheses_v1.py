"""Derive actionable particle-hypothesis sets from S2880 clue artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from cog_v3.calc import v3_s2880_utils as u
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = u.repo_root()
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_s2880_particle_clue_hypotheses_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"
CLUE_JSON = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_clue_report_v1.json"
CATALOG_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_interaction_catalog_v1.csv"

OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_clue_hypotheses_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_clue_hypotheses_v1.md"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_hypothesis_seed_sets_v1.csv"


def _load_clue() -> Dict[str, Any]:
    if not CLUE_JSON.exists():
        raise FileNotFoundError(f"Missing clue report: {CLUE_JSON}")
    return json.loads(CLUE_JSON.read_text(encoding="utf-8"))


def _load_catalog() -> List[Dict[str, str]]:
    if not CATALOG_CSV.exists():
        raise FileNotFoundError(f"Missing catalog: {CATALOG_CSV}")
    return u.read_csv_rows(CATALOG_CSV)


def _top_qids_for_role(catalog_rows: List[Dict[str, str]], *, role_field: str, n: int = 24) -> List[Dict[str, Any]]:
    # Keep best instance per q_id to avoid overcounting phase replicas.
    by_qid: Dict[int, Dict[str, str]] = {}
    for r in catalog_rows:
        q_id = int(r["q_id"])
        cur = by_qid.get(q_id)
        if cur is None or float(r[role_field]) > float(cur[role_field]):
            by_qid[q_id] = r
    ranked = sorted(by_qid.values(), key=lambda r: float(r[role_field]), reverse=True)[: int(n)]
    out: List[Dict[str, Any]] = []
    for r in ranked:
        out.append(
            {
                "q_id": int(r["q_id"]),
                "best_s_id": int(r["s_id"]),
                "phase_idx": int(r["phase_idx"]),
                "score": float(r[role_field]),
                "q_family_tag": str(r["q_family_tag"]),
                "class_id": str(r["class_id"]),
                "order": int(r["order"]),
            }
        )
    return out


def _triad_extract(clue: Dict[str, Any], role_name: str, n: int = 16) -> List[Dict[str, Any]]:
    tri = clue.get("generation_triads", {}).get(role_name, [])
    return list(tri[: int(n)])


def _photon_neutrino_separation(catalog_rows: List[Dict[str, str]], n: int = 40) -> Dict[str, Any]:
    # Score deltas at element level to identify where the two hypotheses separate.
    rows = []
    for r in catalog_rows:
        sp = float(r["score_photon_like"])
        sn = float(r["score_neutrino_like"])
        rows.append(
            {
                "s_id": int(r["s_id"]),
                "q_id": int(r["q_id"]),
                "phase_idx": int(r["phase_idx"]),
                "q_family_tag": str(r["q_family_tag"]),
                "order": int(r["order"]),
                "photon_minus_neutrino": float(sp - sn),
                "photon_score": float(sp),
                "neutrino_score": float(sn),
            }
        )
    pos = sorted(rows, key=lambda r: float(r["photon_minus_neutrino"]), reverse=True)[: int(n)]
    neg = sorted(rows, key=lambda r: float(r["photon_minus_neutrino"]))[: int(n)]
    abs_gap_mean = sum(abs(float(r["photon_minus_neutrino"])) for r in rows) / max(1, len(rows))
    exact_tie_count = sum(1 for r in rows if abs(float(r["photon_minus_neutrino"])) < 1e-12)
    return {
        "mean_abs_delta": float(abs_gap_mean),
        "exact_tie_count": int(exact_tie_count),
        "top_photon_favored": pos,
        "top_neutrino_favored": neg,
    }


def _render_md(payload: Dict[str, Any]) -> str:
    sep = payload["photon_neutrino_separation"]
    lines = [
        "# v3 S2880 Particle Clue Hypotheses (v1)",
        "",
        f"- mean_abs(photon-neutrino score delta): `{sep['mean_abs_delta']:.6f}`",
        f"- exact_tie_count: `{sep['exact_tie_count']}`",
        "",
        "## Recommended q-core sets",
        "",
    ]
    for lane in ("photon_lane", "neutrino_lane", "electron_lane", "quark_lane", "mediator_lane", "crossmix_lane"):
        qids = payload["recommended_qcore_sets"][lane]["q_ids"]
        lines.append(f"- {lane}: `{qids}`")
    lines.extend(["", "## Top generation triads", ""])
    for role in ("photon_like", "neutrino_like", "electron_like"):
        lines.append(f"### {role}")
        lines.append("| q_id | sids(g0,g1,g2) | score_mean | spread |")
        lines.append("|---:|---|---:|---:|")
        for t in payload["triads"][role][:8]:
            lines.append(
                f"| {t['q_id']} | {','.join(str(x) for x in t['sids'])} | "
                f"{float(t['score_mean']):.4f} | {float(t['score_spread']):.4f} |"
            )
        lines.append("")
    return "\n".join(lines)


def build_payload(*, top_n_qids: int = 24, triad_top_n: int = 16) -> Dict[str, Any]:
    clue = _load_clue()
    cat = _load_catalog()

    role_field_map = {
        "photon_like": "score_photon_like",
        "neutrino_like": "score_neutrino_like",
        "electron_like": "score_electron_like",
        "quark_core_like": "score_quark_core_like",
        "mediator_w_like": "score_mediator_w_like",
        "unstable_crossmix_like": "score_unstable_crossmix_like",
    }
    top_q = {
        role: _top_qids_for_role(cat, role_field=field, n=top_n_qids)
        for role, field in role_field_map.items()
    }
    triads = {role: _triad_extract(clue, role, n=triad_top_n) for role in ("photon_like", "neutrino_like", "electron_like")}
    sep = _photon_neutrino_separation(cat, n=40)

    # Compact recommended q-core sets.
    rec_sets = {
        "photon_lane": {"q_ids": [int(r["q_id"]) for r in top_q["photon_like"][:12]]},
        "neutrino_lane": {"q_ids": [int(r["q_id"]) for r in top_q["neutrino_like"][:12]]},
        "electron_lane": {"q_ids": [int(r["q_id"]) for r in top_q["electron_like"][:20]]},
        "quark_lane": {"q_ids": [int(r["q_id"]) for r in top_q["quark_core_like"][:24]]},
        "mediator_lane": {"q_ids": [int(r["q_id"]) for r in top_q["mediator_w_like"][:24]]},
        "crossmix_lane": {"q_ids": [int(r["q_id"]) for r in top_q["unstable_crossmix_like"][:24]]},
    }

    # Write compact seed set CSV.
    csv_rows: List[Dict[str, Any]] = []
    for lane, rec in rec_sets.items():
        for rank, q_id in enumerate(rec["q_ids"], start=1):
            csv_rows.append(
                {
                    "lane": str(lane),
                    "priority_rank": int(rank),
                    "q_id": int(q_id),
                }
            )
    u.write_csv_rows(
        OUT_CSV,
        fieldnames=["lane", "priority_rank", "q_id"],
        rows=csv_rows,
    )

    payload: Dict[str, Any] = {
        "schema_version": "v3_s2880_particle_clue_hypotheses_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": u.sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": u.sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "params": {"top_n_qids": int(top_n_qids), "triad_top_n": int(triad_top_n)},
        "photon_neutrino_separation": sep,
        "top_qids_by_role": top_q,
        "triads": triads,
        "recommended_qcore_sets": rec_sets,
        "checks": {
            "catalog_nonempty": bool(len(cat) > 0),
            "csv_rows_nonempty": bool(len(csv_rows) > 0),
        },
    }
    payload["replay_hash"] = u.sha_payload(payload)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Build S2880 particle clue hypotheses artifact.")
    ap.add_argument("--top-n-qids", type=int, default=24)
    ap.add_argument("--triad-top-n", type=int, default=16)
    args = ap.parse_args()
    payload = build_payload(top_n_qids=int(args.top_n_qids), triad_top_n=int(args.triad_top_n))
    print(f"mean_abs_delta={payload['photon_neutrino_separation']['mean_abs_delta']:.6f}")
    print(f"exact_tie_count={payload['photon_neutrino_separation']['exact_tie_count']}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()


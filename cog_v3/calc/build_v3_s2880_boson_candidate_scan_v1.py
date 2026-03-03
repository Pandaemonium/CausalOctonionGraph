"""Scan S2880 for boson-like candidates from existing structural role catalogs.

Inputs:
- cog_v3/sources/v3_s2880_particle_interaction_catalog_v1.csv
- cog_v3/sources/v3_s2880_invariants_v1.csv

Outputs:
- cog_v3/sources/v3_s2880_boson_candidate_scan_v1.json
- cog_v3/sources/v3_s2880_boson_candidate_scan_v1.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]

IN_ROLE = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_interaction_catalog_v1.csv"
IN_INV = ROOT / "cog_v3" / "sources" / "v3_s2880_invariants_v1.csv"

OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_s2880_boson_candidate_scan_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_s2880_boson_candidate_scan_v1.md"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_s2880_boson_candidate_scan_v1.py"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _merge_rows(role_rows: List[Dict[str, str]], inv_rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    inv_by = {str(r["s_id"]): r for r in inv_rows}
    out: List[Dict[str, Any]] = []
    for r in role_rows:
        sid = str(r["s_id"])
        iv = inv_by.get(sid, {})
        out.append(
            {
                "s_id": int(sid),
                "label": str(r["label"]),
                "top_role_1": str(r["top_role_1"]),
                "top_role_1_score": float(r["top_role_1_score"]),
                "phase_idx": int(r["phase_idx"]),
                "phase_sector_mod3": int(iv.get("phase_sector_mod3", r.get("phase_idx", "0"))) % 3,
                "q_id": int(r["q_id"]),
                "order": int(r["order"]),
                "q_order": int(r["q_order"]),
                "q_family_tag": str(r["q_family_tag"]),
                "commute_rate_probe": float(r["commute_rate_probe"]),
                "assoc_nonzero_rate": float(r["assoc_nonzero_rate"]),
                "probe_order_preserve_rate": float(r["probe_order_preserve_rate"]),
                "family_transition_entropy": float(r["family_transition_entropy"]),
                "score_photon_like": float(r["score_photon_like"]),
                "score_mediator_w_like": float(r["score_mediator_w_like"]),
                "score_unstable_crossmix_like": float(r["score_unstable_crossmix_like"]),
                "q_has_e000": str(iv.get("q_has_e000", "")).lower() == "true",
                "q_has_e111": str(iv.get("q_has_e111", "")).lower() == "true",
            }
        )
    return out


def _top(rows: List[Dict[str, Any]], *, role: str, score_key: str, n: int) -> List[Dict[str, Any]]:
    cand = [r for r in rows if str(r["top_role_1"]) == str(role)]
    cand.sort(
        key=lambda x: (
            float(x[score_key]),
            float(x["commute_rate_probe"]),
            -float(x["assoc_nonzero_rate"]),
            float(x["probe_order_preserve_rate"]),
        ),
        reverse=True,
    )
    return cand[: int(n)]


def build_payload(*, top_n: int) -> Dict[str, Any]:
    role_rows = _read_csv(IN_ROLE)
    inv_rows = _read_csv(IN_INV)
    rows = _merge_rows(role_rows, inv_rows)

    role_count = Counter(str(r["top_role_1"]) for r in rows)
    role_by_phase: Dict[str, Dict[str, int]] = defaultdict(lambda: {"0": 0, "1": 0, "2": 0})
    for r in rows:
        role = str(r["top_role_1"])
        g = str(int(r["phase_sector_mod3"]) % 3)
        role_by_phase[role][g] = int(role_by_phase[role][g]) + 1

    photon_top = _top(rows, role="photon_like", score_key="score_photon_like", n=int(top_n))
    weak_top = _top(rows, role="mediator_w_like", score_key="score_mediator_w_like", n=int(top_n))

    # Optional gluon-proxy lane: pure-imaginary A16 basis states (heuristic, not model-closed claim).
    gluon_proxy = [
        r
        for r in rows
        if str(r["q_family_tag"]) == "A16_basis_signed_unit" and not bool(r["q_has_e000"])
    ]
    gluon_proxy.sort(
        key=lambda x: (float(x["commute_rate_probe"]), -float(x["assoc_nonzero_rate"]), float(x["probe_order_preserve_rate"])),
        reverse=True,
    )
    gluon_proxy = gluon_proxy[: int(top_n)]

    payload: Dict[str, Any] = {
        "schema_version": "v3_s2880_boson_candidate_scan_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "inputs": {
            "role_csv": str(IN_ROLE.relative_to(ROOT)).replace("\\", "/"),
            "role_csv_sha256": _sha_file(IN_ROLE),
            "inv_csv": str(IN_INV.relative_to(ROOT)).replace("\\", "/"),
            "inv_csv_sha256": _sha_file(IN_INV),
        },
        "top_n": int(top_n),
        "summary": {
            "total_rows": int(len(rows)),
            "top_role_1_counts": {k: int(v) for k, v in sorted(role_count.items())},
            "top_role_1_counts_by_phase_mod3": {k: role_by_phase[k] for k in sorted(role_by_phase.keys())},
        },
        "candidates": {
            "photon_like_top": photon_top,
            "mediator_w_like_top": weak_top,
            "gluon_proxy_top": gluon_proxy,
        },
        "notes": [
            "This scan ranks candidates from existing heuristic role scores; it is not a proof of particle identity.",
            "gluon_proxy_top is a structural proxy lane (pure-imaginary A16) and should be treated as exploratory.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# v3 S2880 Boson Candidate Scan (v1)",
        "",
        f"- schema_version: `{payload['schema_version']}`",
        f"- top_n: `{payload['top_n']}`",
        f"- total_rows: `{s['total_rows']}`",
        "",
        "## Top Role Counts",
        "",
        "| role | count | g0 | g1 | g2 |",
        "|---|---:|---:|---:|---:|",
    ]
    by_phase = s["top_role_1_counts_by_phase_mod3"]
    for role, cnt in s["top_role_1_counts"].items():
        bp = by_phase.get(role, {"0": 0, "1": 0, "2": 0})
        lines.append(f"| `{role}` | {int(cnt)} | {int(bp['0'])} | {int(bp['1'])} | {int(bp['2'])} |")

    def add_table(title: str, key: str, score_key: str) -> None:
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                "| s_id | phase_idx | q_id | order | q_family_tag | score | commute | assoc | label |",
                "|---:|---:|---:|---:|---|---:|---:|---:|---|",
            ]
        )
        for r in payload["candidates"][key]:
            lines.append(
                f"| {int(r['s_id'])} | {int(r['phase_idx'])} | {int(r['q_id'])} | {int(r['order'])} | "
                f"`{r['q_family_tag']}` | {float(r[score_key]):.6f} | {float(r['commute_rate_probe']):.6f} | "
                f"{float(r['assoc_nonzero_rate']):.6f} | `{str(r['label'])}` |"
            )

    add_table("Photon-Like Candidates", "photon_like_top", "score_photon_like")
    add_table("Weak-Mediator-Like Candidates", "mediator_w_like_top", "score_mediator_w_like")
    add_table("Gluon-Proxy Structural Lane (Exploratory)", "gluon_proxy_top", "commute_rate_probe")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `photon_like_top`: strongest neutral propagation/mode-preserving lane under current role model.",
            "- `mediator_w_like_top`: strongest cross-mixing mediator lane under current role model.",
            "- `gluon_proxy_top`: pure-imaginary basis lane for color-like mediator exploration; not yet calibrated as a closed gluon map.",
        ]
    )
    return "\n".join(lines)


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--top-n", type=int, default=24)
    args = ap.parse_args()
    payload = build_payload(top_n=int(args.top_n))
    write_artifacts(payload)
    print(
        "v3_s2880_boson_candidate_scan_v1: "
        f"rows={payload['summary']['total_rows']}, "
        f"roles={payload['summary']['top_role_1_counts']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


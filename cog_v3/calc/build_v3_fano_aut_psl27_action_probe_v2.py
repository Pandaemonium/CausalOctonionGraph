"""Probe Family-A Fano automorphism action (PSL(2,7)-size lane) on Q240/S960 order-6 sectors."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_fano_aut_psl27_action_probe_v2.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_fano_aut_psl27_action_probe_v2.md"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_fano_aut_psl27_orbits_v2.csv"
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_fano_aut_psl27_action_probe_v2.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _build_third_sign_tables() -> Tuple[Dict[Tuple[int, int], int], Dict[Tuple[int, int], int]]:
    third: Dict[Tuple[int, int], int] = {}
    sign: Dict[Tuple[int, int], int] = {}
    for i in range(1, 8):
        for j in range(1, 8):
            if i == j:
                continue
            a = [Fraction(0, 1)] * 8
            b = [Fraction(0, 1)] * 8
            a[i] = Fraction(1, 1)
            b[j] = Fraction(1, 1)
            p = k.oct_mul(tuple(a), tuple(b))
            nz = [idx for idx, c in enumerate(p) if c != 0]
            if len(nz) != 1:
                raise RuntimeError("basis product not monomial")
            kk = int(nz[0])
            third[(i, j)] = kk
            sign[(i, j)] = 1 if p[kk] > 0 else -1
    return third, sign


def _enumerate_fano_automorphisms(
    third: Dict[Tuple[int, int], int],
    sign: Dict[Tuple[int, int], int],
    *,
    orientation_mode: str,
) -> List[Tuple[int, ...]]:
    out: List[Tuple[int, ...]] = []
    for perm in itertools.permutations(range(1, 8)):
        ok = True
        for i in range(1, 8):
            si = int(perm[i - 1])
            for j in range(1, 8):
                if i == j:
                    continue
                sj = int(perm[j - 1])
                k0 = int(third[(i, j)])
                sk0 = int(perm[k0 - 1])
                if int(third[(si, sj)]) != sk0:
                    ok = False
                    break
                if str(orientation_mode) == "oriented":
                    if int(sign[(si, sj)]) != int(sign[(i, j)]):
                        ok = False
                        break
            if not ok:
                break
        if ok:
            out.append(tuple(int(x) for x in perm))
    return out


def _permute_q240_id(qid: int, perm: Tuple[int, ...]) -> int:
    x = k.ALPHABET[int(qid)]
    y = [x[0]] + [Fraction(0, 1)] * 7
    for i in range(1, 8):
        # new coeff for basis i receives old coeff from perm^-1(i)
        src = int(perm[i - 1])
        y[i] = x[src]
    yy = tuple(y)
    out = k.ALPHABET_INDEX.get(yy)
    if out is None:
        return -1
    return int(out)


def _orbit_partition(perms: Sequence[np.ndarray], n_points: int) -> List[List[int]]:
    unseen = set(range(int(n_points)))
    out: List[List[int]] = []
    while unseen:
        s = int(next(iter(unseen)))
        stack = [s]
        orb = set([s])
        unseen.remove(s)
        while stack:
            x = int(stack.pop())
            for p in perms:
                y = int(p[x])
                if y not in orb:
                    orb.add(y)
                    if y in unseen:
                        unseen.remove(y)
                    stack.append(y)
        out.append(sorted(int(v) for v in orb))
    out.sort(key=lambda g: (len(g), g[0]))
    return out


def _stabilizer_hist(perms: Sequence[np.ndarray], n_points: int) -> Dict[int, int]:
    hist: Dict[int, int] = {}
    for p in range(int(n_points)):
        s = 0
        for a in perms:
            if int(a[p]) == int(p):
                s += 1
        hist[int(s)] = int(hist.get(int(s), 0) + 1)
    return hist


def _closure_ok(perms: Sequence[np.ndarray]) -> bool:
    keys = {tuple(int(v) for v in p.tolist()) for p in perms}
    n = len(perms)
    if n == 0:
        return False
    m = int(perms[0].shape[0])
    for i in range(n):
        pi = perms[i]
        for j in range(n):
            pj = perms[j]
            comp = tuple(int(pi[int(pj[t])]) for t in range(m))
            if comp not in keys:
                return False
    return True


def _domain_order6_sets() -> Tuple[List[int], List[int]]:
    # Q240 order-6
    qmul = c12.build_qmul_table()
    q_order6: List[int] = []
    for qid in range(int(qmul.shape[0])):
        o = int(c12.element_order(int(qid), qmul, int(k.IDENTITY_ID), max_order=4096))
        if o == 6:
            q_order6.append(int(qid))

    # S960 order-6
    smul = c12.build_mul_table(phase_count=4, qmul=qmul)
    s_order6: List[int] = []
    s_identity = int(c12.s_identity_id())
    for sid in range(int(smul.shape[0])):
        o = int(c12.element_order(int(sid), smul, s_identity, max_order=4096))
        if o == 6:
            s_order6.append(int(sid))
    return q_order6, s_order6


def _build_action_on_domain(
    *,
    domain_ids: Sequence[int],
    auts: Sequence[Tuple[int, ...]],
    is_s960: bool,
) -> Tuple[List[np.ndarray], bool]:
    domain = [int(x) for x in domain_ids]
    idx_of = {sid: i for i, sid in enumerate(domain)}
    perms: List[np.ndarray] = []
    dropped = 0
    qn = int(k.ALPHABET_SIZE)
    for perm in auts:
        row = np.full((len(domain),), -1, dtype=np.int32)
        ok = True
        for i, sid in enumerate(domain):
            if bool(is_s960):
                p = int(sid // qn)
                q = int(sid % qn)
                q2 = int(_permute_q240_id(int(q), perm))
                if q2 < 0:
                    ok = False
                    break
                sid2 = int(p * qn + q2)
            else:
                sid2 = int(_permute_q240_id(int(sid), perm))
                if sid2 < 0:
                    ok = False
                    break
            j = idx_of.get(int(sid2))
            if j is None:
                ok = False
                break
            row[i] = np.int32(int(j))
        if ok:
            perms.append(row)
        else:
            dropped += 1
    return perms, dropped


def _analyze_variant(
    *,
    variant_id: str,
    auts: Sequence[Tuple[int, ...]],
    q_order6: Sequence[int],
    s_order6: Sequence[int],
) -> Dict[str, Any]:
    q_perms, q_drop = _build_action_on_domain(domain_ids=q_order6, auts=auts, is_s960=False)
    s_perms, s_drop = _build_action_on_domain(domain_ids=s_order6, auts=auts, is_s960=True)

    q_orbits = _orbit_partition(q_perms, len(q_order6)) if q_perms else []
    s_orbits = _orbit_partition(s_perms, len(s_order6)) if s_perms else []

    q_stab = _stabilizer_hist(q_perms, len(q_order6)) if q_perms else {}
    s_stab = _stabilizer_hist(s_perms, len(s_order6)) if s_perms else {}

    out = {
        "variant_id": str(variant_id),
        "candidate_action_size": int(len(auts)),
        "q240": {
            "order6_set_size": int(len(q_order6)),
            "effective_action_size": int(len(q_perms)),
            "dropped_action_count_embedding_mismatch": int(q_drop),
            "closure_ok": bool(_closure_ok(q_perms)) if q_perms else False,
            "faithful_ok": bool(len(q_perms) == len(auts)),
            "orbit_partition": [int(len(o)) for o in q_orbits],
            "stabilizer_histogram": {str(k0): int(v0) for k0, v0 in sorted(q_stab.items())},
        },
        "s960": {
            "order6_set_size": int(len(s_order6)),
            "effective_action_size": int(len(s_perms)),
            "dropped_action_count_embedding_mismatch": int(s_drop),
            "closure_ok": bool(_closure_ok(s_perms)) if s_perms else False,
            "faithful_ok": bool(len(s_perms) == len(auts)),
            "orbit_partition": [int(len(o)) for o in s_orbits],
            "stabilizer_histogram": {str(k0): int(v0) for k0, v0 in sorted(s_stab.items())},
        },
    }
    return out


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Fano Automorphism PSL(2,7) Action Probe (v2)",
        "",
        f"- convention_id: `{payload['convention_id']}`",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        "",
        "| variant | action_size | q240_order6 | q240_orbits | s960_order6 | s960_orbits |",
        "|---|---:|---:|---|---:|---|",
    ]
    for v in payload["variants"]:
        lines.append(
            f"| `{v['variant_id']}` | {int(v['candidate_action_size'])} | "
            f"{int(v['q240']['order6_set_size'])} | `{v['q240']['orbit_partition']}` | "
            f"{int(v['s960']['order6_set_size'])} | `{v['s960']['orbit_partition']}` |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `unoriented` preserves Fano third-index product map (sign ignored) and yields PSL(2,7)-size lane.",
            "- `oriented` additionally preserves directed sign orientation and is a strict subgroup.",
        ]
    )
    return "\n".join(lines)


def build_payload() -> Dict[str, Any]:
    third, sign = _build_third_sign_tables()
    q_order6, s_order6 = _domain_order6_sets()

    auts_unoriented = _enumerate_fano_automorphisms(third, sign, orientation_mode="unoriented")
    auts_oriented = _enumerate_fano_automorphisms(third, sign, orientation_mode="oriented")

    variants = [
        _analyze_variant(
            variant_id="unoriented_signfree",
            auts=auts_unoriented,
            q_order6=q_order6,
            s_order6=s_order6,
        ),
        _analyze_variant(
            variant_id="oriented_signpreserving",
            auts=auts_oriented,
            q_order6=q_order6,
            s_order6=s_order6,
        ),
    ]

    payload: Dict[str, Any] = {
        "schema_version": "v3_fano_aut_psl27_action_probe_v2",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "variants": variants,
        "meta": {
            "automorphism_count_unoriented": int(len(auts_unoriented)),
            "automorphism_count_oriented": int(len(auts_oriented)),
        },
    }
    payload["replay_hash"] = _sha_payload(payload)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write(_render_md(payload))
        f.write("\n")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "variant_id",
                "candidate_action_size",
                "domain",
                "order6_set_size",
                "effective_action_size",
                "dropped_action_count_embedding_mismatch",
                "closure_ok",
                "faithful_ok",
                "orbit_partition",
                "stabilizer_histogram",
            ]
        )
        for v in variants:
            for domain in ("q240", "s960"):
                d = v[domain]
                w.writerow(
                    [
                        str(v["variant_id"]),
                        int(v["candidate_action_size"]),
                        str(domain),
                        int(d["order6_set_size"]),
                        int(d["effective_action_size"]),
                        int(d["dropped_action_count_embedding_mismatch"]),
                        bool(d["closure_ok"]),
                        bool(d["faithful_ok"]),
                        json.dumps(d["orbit_partition"], sort_keys=True),
                        json.dumps(d["stabilizer_histogram"], sort_keys=True),
                    ]
                )
    return payload


def main() -> None:
    _ = argparse.ArgumentParser(description="Build v3 Fano automorphism action probe v2.")
    payload = build_payload()
    print(f"unoriented_aut_count={payload['meta']['automorphism_count_unoriented']}")
    print(f"oriented_aut_count={payload['meta']['automorphism_count_oriented']}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()

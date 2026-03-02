"""Build norm-1 integer CxO failure ledger with mixed e000 factors (v1).

This artifact records every failing pair in a deterministic catalog where both
e000=1 and e000=0 factor states are present.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from itertools import combinations
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.calc.build_norm1_integer_kernel_probe_v1 import render_failure_cases_md
from cog_v2.python import kernel_norm1_integer_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "norm1_integer_failure_cases_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "norm1_integer_failure_cases_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_norm1_integer_failure_cases_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_norm1_integer_v1.py"

PAIR_ORDER: Tuple[Tuple[int, int], ...] = tuple((i, j) for i, j in combinations(range(1, 8), 2))


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _serialize_g(z: k.GInt) -> List[int]:
    return [int(z.re), int(z.im)]


def _serialize_cxo(x: k.CxO) -> List[List[int]]:
    return [_serialize_g(z) for z in x]


def _family_state(anchor_idx: int, m: int, n: int, i: int, j: int) -> k.CxO:
    # a = m + n*i, b = n - m*i, so a^2 + b^2 = 0 in Z[i].
    a = k.GInt(int(m), int(n))
    b = k.GInt(int(n), int(-m))
    vals = [k.ZERO_G for _ in range(8)]
    vals[int(anchor_idx)] = k.ONE_G
    vals[int(i)] = a
    vals[int(j)] = b
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _build_catalog(range_limit: int, sample_cap: int) -> List[k.CxO]:
    if range_limit < 1:
        raise ValueError("range_limit must be >= 1")
    if sample_cap < 8:
        raise ValueError("sample_cap must be >= 8")

    e000_pool: List[k.CxO] = []
    non_e000_pool: List[k.CxO] = []
    seen: set[Tuple[Tuple[int, int], ...]] = set()

    for m in range(-int(range_limit), int(range_limit) + 1):
        for n in range(-int(range_limit), int(range_limit) + 1):
            if m == 0 and n == 0:
                continue
            for anchor in range(8):
                for i, j in PAIR_ORDER:
                    st = _family_state(anchor, m, n, i, j)
                    if not k.cxo_is_norm_one(st):
                        continue
                    key = tuple((z.re, z.im) for z in st)
                    if key in seen:
                        continue
                    seen.add(key)
                    if st[0] == k.ONE_G:
                        e000_pool.append(st)
                    else:
                        non_e000_pool.append(st)

    # Deterministic balanced merge so both e000=1 and e000=0 are guaranteed.
    target_a = min(len(e000_pool), int(sample_cap) // 2)
    target_b = min(len(non_e000_pool), int(sample_cap) - target_a)
    if target_a == 0 or target_b == 0:
        raise ValueError("Unable to build mixed-e000 catalog with current params.")

    out: List[k.CxO] = []
    ia = 0
    ib = 0
    while len(out) < int(sample_cap) and (ia < target_a or ib < target_b):
        if ia < target_a:
            out.append(e000_pool[ia])
            ia += 1
        if len(out) >= int(sample_cap):
            break
        if ib < target_b:
            out.append(non_e000_pool[ib])
            ib += 1
    return out


def _select_catalog(range_limit: int, sample_cap: int | None) -> List[k.CxO]:
    if sample_cap is None:
        # Full mixed catalog (all deduped states from generator).
        # Use a very large cap; _build_catalog clips to actual size.
        return _build_catalog(range_limit=int(range_limit), sample_cap=10**9)
    return _build_catalog(range_limit=int(range_limit), sample_cap=int(sample_cap))


def build_payload(
    range_limit: int = 2,
    sample_cap: int | None = 36,
    max_failure_records: int = 20000,
) -> Dict[str, Any]:
    if int(max_failure_records) < 1:
        raise ValueError("max_failure_records must be >= 1")
    catalog = _select_catalog(int(range_limit), None if sample_cap is None else int(sample_cap))
    failures: List[Dict[str, Any]] = []
    e000_nonzero_in_failures = 0
    e000_zero_in_failures = 0
    e111_nonzero_in_failures = 0
    scanned_pairs = 0

    for ai, a in enumerate(catalog):
        for bi, b in enumerate(catalog):
            scanned_pairs += 1
            prod = k.cxo_mul(a, b)
            if k.cxo_is_norm_one(prod):
                continue
            if a[0] == k.ONE_G and b[0] == k.ONE_G:
                e000_nonzero_in_failures += 1
            else:
                e000_zero_in_failures += 1
            if a[7] != k.ZERO_G or b[7] != k.ZERO_G:
                e111_nonzero_in_failures += 1
            if len(failures) < int(max_failure_records):
                failures.append(
                    {
                        "a_index": int(ai),
                        "b_index": int(bi),
                        "factor_a": _serialize_cxo(a),
                        "factor_b": _serialize_cxo(b),
                        "product": _serialize_cxo(prod),
                        "product_norm": _serialize_g(k.cxo_composition_norm(prod)),
                        "product_norm_residual_linf": int(k.cxo_norm_residual_linf(prod)),
                        "product_max_coeff_linf": int(k.cxo_max_coeff_linf(prod)),
                    }
                )

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "norm1_integer_failure_cases_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "params": {
            "range_limit": int(range_limit),
            "sample_cap": None if sample_cap is None else int(sample_cap),
            "max_failure_records": int(max_failure_records),
            "pair_order": [list(p) for p in PAIR_ORDER],
        },
        "scanned_pair_count": int(scanned_pairs),
        "state_count": int(len(catalog)),
        "e000_one_state_count": int(sum(1 for s in catalog if s[0] == k.ONE_G)),
        "e000_zero_state_count": int(sum(1 for s in catalog if s[0] != k.ONE_G)),
        "e111_nonzero_state_count": int(sum(1 for s in catalog if s[7] != k.ZERO_G)),
        "failure_count": int(e000_nonzero_in_failures + e000_zero_in_failures),
        "recorded_failure_count": int(len(failures)),
        "failure_mix_counts": {
            "both_factors_e000_one": int(e000_nonzero_in_failures),
            "at_least_one_factor_e000_zero": int(e000_zero_in_failures),
            "at_least_one_factor_e111_nonzero": int(e111_nonzero_in_failures),
        },
        "failures": failures,
        "notes": [
            "Catalog is intentionally mixed across e000=1 and e000=0 seeds.",
            "Each recorded failure includes full factors, product, and product norm.",
            "failure_count counts all failing pairs; recorded_failure_count may be capped.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def write_artifacts(
    payload: Dict[str, Any],
    json_paths: Sequence[Path] = (OUT_JSON,),
    md_paths: Sequence[Path] = (OUT_MD,),
) -> None:
    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_failure_cases_md(payload)
    for path in md_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--range-limit", type=int, default=2)
    parser.add_argument(
        "--sample-cap",
        type=int,
        default=1024,
        help="number of states to include (use -1 for full catalog)",
    )
    parser.add_argument("--max-failure-records", type=int, default=20000)
    args = parser.parse_args()

    sample_cap: int | None = None if int(args.sample_cap) < 0 else int(args.sample_cap)
    payload = build_payload(
        range_limit=int(args.range_limit),
        sample_cap=sample_cap,
        max_failure_records=int(args.max_failure_records),
    )
    write_artifacts(payload)
    print(
        "norm1_integer_failure_cases_v1: "
        f"states={payload['state_count']}, "
        f"e111_nonzero_states={payload['e111_nonzero_state_count']}, "
        f"e000_one={payload['e000_one_state_count']}, "
        f"e000_zero={payload['e000_zero_state_count']}, "
        f"failures={payload['failure_count']}, "
        f"recorded_failures={payload['recorded_failure_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

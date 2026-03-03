"""Smoke test for SparseCausalBackend wiring.

Checks that dense and sparse backends preserve the set of distinct path
products under vacuum-identity assumptions for a single-excitation seed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from cog_v3.python import causal_past_contract_v1 as cp
from cog_v3.python import kernel_cog_v5_coherence as kv5


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v5_sparse_backend_smoke_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v5_sparse_backend_smoke_v1.md"


Coords = Tuple[int, int, int]


def _state_key(st: kv5.State) -> Tuple[int, int, int, int, int]:
    return (int(st.g), int(st.a), int(st.basis), int(st.sign), int(st.e))


def _product_set(
    paths: List[cp.Path],
    seed: Dict[Coords, kv5.State],
) -> List[Tuple[int, int, int, int, int]]:
    s = {_state_key(kv5.path_product(p, seed)) for p in paths}
    return sorted(s)


def main() -> None:
    origin: Coords = (0, 0, 0)
    horizon = 6
    max_paths = 50_000

    vacuum = kv5.State(g=0, a=0, basis=0, sign=1, e=0)
    seed = kv5.vacuum_seed()
    seed[(1, 1, 1)] = kv5.State(g=1, a=1, basis=7, sign=1, e=1)

    dense = cp.F2CubePastProvider()
    active = cp.active_sites_from_seed(seed, vacuum_state=vacuum)
    sparse = cp.SparseCausalBackend(active_sites=active, vacuum_identity_mode=True)

    rows = []
    n_checked = 0
    n_match = 0
    for t in range(1, horizon + 1):
        for target in kv5.F2_SITES:
            if not dense.is_reachable(origin, target, t):
                continue
            dense_paths = dense.paths(origin, target, t, max_paths=max_paths)
            sparse_paths = sparse.paths(origin, target, t, max_paths=max_paths)
            dense_set = _product_set(dense_paths, seed)
            sparse_set = _product_set(sparse_paths, seed)
            ok = dense_set == sparse_set
            n_checked += 1
            n_match += int(ok)
            rows.append(
                {
                    "t": int(t),
                    "target": tuple(target),
                    "n_dense_paths": int(len(dense_paths)),
                    "n_sparse_paths": int(len(sparse_paths)),
                    "n_dense_products": int(len(dense_set)),
                    "n_sparse_products": int(len(sparse_set)),
                    "product_set_match": bool(ok),
                }
            )

    payload = {
        "schema_version": "v5_sparse_backend_smoke_v1",
        "kernel_profile": kv5.KERNEL_PROFILE,
        "horizon": horizon,
        "active_sites": sorted([tuple(s) for s in active]),
        "n_checked_points": n_checked,
        "n_product_set_match": n_match,
        "all_match": bool(n_checked == n_match),
        "rows": rows,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = [
        "# v5 Sparse Backend Smoke (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- horizon: `{horizon}`",
        f"- active_sites: `{payload['active_sites']}`",
        f"- checked points: `{n_checked}`",
        f"- product-set matches: `{n_match}`",
        f"- all_match: `{payload['all_match']}`",
    ]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()

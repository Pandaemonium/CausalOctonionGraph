"""RFC-013 probe: order-6 (168) sector and candidate PSL(2,7)-like action."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_order6_psl27_action_probe_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_order6_psl27_action_probe_v1.md"
OUT_ORBITS = ROOT / "cog_v3" / "sources" / "v3_order6_psl27_orbits_v1.csv"
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_order6_psl27_action_probe_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _orders(mul: np.ndarray, identity: int) -> List[int]:
    out: List[int] = []
    for sid in range(int(mul.shape[0])):
        out.append(int(c12.element_order(int(sid), mul, int(identity), max_order=4096)))
    return out


def _inverse_table(mul: np.ndarray, identity: int) -> np.ndarray:
    n = int(mul.shape[0])
    inv = np.full((n,), -1, dtype=np.int32)
    idc = int(identity)
    for a in range(n):
        row_ok = np.flatnonzero(mul[a, :] == np.uint16(idc))
        col_ok = np.flatnonzero(mul[:, a] == np.uint16(idc))
        cand = sorted(set(int(x) for x in row_ok.tolist()) & set(int(x) for x in col_ok.tolist()))
        if cand:
            inv[a] = np.int32(cand[0])
        elif row_ok.size > 0:
            inv[a] = np.int32(int(row_ok[0]))
    if int(np.count_nonzero(inv < 0)) > 0:
        raise RuntimeError("inverse lookup failed for some elements")
    return inv


def _orbit_partition(perms: Sequence[np.ndarray], n_points: int) -> List[List[int]]:
    unseen = set(range(int(n_points)))
    out: List[List[int]] = []
    while unseen:
        start = int(next(iter(unseen)))
        stack = [start]
        orb = set([start])
        unseen.remove(start)
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


def _random_control(n_points: int, action_size: int, trials: int, seed: int) -> Dict[str, Any]:
    rr = random.Random(int(seed))
    orbit_counts: List[int] = []
    largest_sizes: List[int] = []
    base = list(range(int(n_points)))
    for t in range(int(trials)):
        perms: List[np.ndarray] = []
        for _ in range(int(action_size)):
            x = list(base)
            rr.shuffle(x)
            perms.append(np.asarray(x, dtype=np.int32))
        orbs = _orbit_partition(perms, n_points=int(n_points))
        orbit_counts.append(int(len(orbs)))
        largest_sizes.append(int(max(len(o) for o in orbs)))
    return {
        "trials": int(trials),
        "mean_orbit_count": float(np.mean(np.asarray(orbit_counts, dtype=np.float64))) if orbit_counts else 0.0,
        "mean_largest_orbit": float(np.mean(np.asarray(largest_sizes, dtype=np.float64))) if largest_sizes else 0.0,
        "seed": int(seed),
    }


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Order-6 PSL(2,7) Action Probe (v1)",
        "",
        f"- convention_id: `{payload['convention_id']}`",
        f"- order6_set_size: `{payload['order6_set_size']}`",
        f"- candidate_action_size: `{payload['candidate_action_size']}`",
        f"- closure_ok: `{payload['closure_ok']}`",
        f"- faithful_ok: `{payload['faithful_ok']}`",
        "",
        "## Orbit Summary",
        "",
        f"- orbit_partition: `{payload['orbit_partition']}`",
        f"- stabilizer_histogram: `{payload['stabilizer_histogram']}`",
        "",
        "## Random Control",
        "",
        f"- mean_orbit_count: `{payload['random_control_comparison']['mean_orbit_count']:.4f}`",
        f"- mean_largest_orbit: `{payload['random_control_comparison']['mean_largest_orbit']:.4f}`",
    ]
    return "\n".join(lines)


def build_payload(*, random_trials: int = 24, random_seed: int = 1337) -> Dict[str, Any]:
    qmul = c12.build_qmul_table()
    mul = c12.build_mul_table(phase_count=4, qmul=qmul)  # S960 lane
    identity = int(c12.s_identity_id())
    ords = _orders(mul, identity=identity)
    inv = _inverse_table(mul, identity=identity)

    order6_ids = [i for i, o in enumerate(ords) if int(o) == 6]
    order6_ids.sort()
    order6_set = set(int(x) for x in order6_ids)
    idx_of = {sid: i for i, sid in enumerate(order6_ids)}

    # Candidate action family: left-associated inner conjugation by order-6 elements.
    perm_rows: List[np.ndarray] = []
    rep_g: List[int] = []
    seen: Dict[Tuple[int, ...], int] = {}
    for g in order6_ids:
        gi = int(inv[int(g)])
        row = []
        ok = True
        for x in order6_ids:
            y = int(mul[int(mul[int(g), int(x)]), int(gi)])
            if y not in order6_set:
                ok = False
                break
            row.append(int(idx_of[y]))
        if not ok:
            continue
        key = tuple(int(v) for v in row)
        if key not in seen:
            seen[key] = len(perm_rows)
            perm_rows.append(np.asarray(row, dtype=np.int32))
            rep_g.append(int(g))

    perm_map = {tuple(int(v) for v in p.tolist()): i for i, p in enumerate(perm_rows)}
    n_action = int(len(perm_rows))
    n_pts = int(len(order6_ids))

    closure_ok = True
    for i in range(n_action):
        pi = perm_rows[i]
        for j in range(n_action):
            pj = perm_rows[j]
            comp = tuple(int(pi[int(pj[t])]) for t in range(n_pts))
            if comp not in perm_map:
                closure_ok = False
                break
        if not closure_ok:
            break

    faithful_ok = bool(n_action == n_pts)
    orbits = _orbit_partition(perm_rows, n_points=n_pts) if perm_rows else []
    orbit_partition = [int(len(o)) for o in orbits]

    stab_hist: Dict[int, int] = {}
    orb_id_of_point = np.full((n_pts,), -1, dtype=np.int32)
    for oid, orb in enumerate(orbits):
        for p in orb:
            orb_id_of_point[int(p)] = np.int32(int(oid))
    for p in range(n_pts):
        stab = 0
        for a in range(n_action):
            if int(perm_rows[a][p]) == int(p):
                stab += 1
        stab_hist[int(stab)] = int(stab_hist.get(int(stab), 0) + 1)

    random_ctrl = _random_control(
        n_points=n_pts,
        action_size=max(1, n_action),
        trials=int(random_trials),
        seed=int(random_seed),
    )

    payload: Dict[str, Any] = {
        "schema_version": "v3_order6_psl27_action_probe_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "order6_set_size": int(n_pts),
        "candidate_action_size": int(n_action),
        "closure_ok": bool(closure_ok),
        "faithful_ok": bool(faithful_ok),
        "orbit_partition": orbit_partition,
        "stabilizer_histogram": {str(k0): int(v0) for k0, v0 in sorted(stab_hist.items())},
        "random_control_comparison": random_ctrl,
    }
    payload["replay_hash"] = _sha_payload(payload)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write(_render_md(payload))
        f.write("\n")

    with OUT_ORBITS.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["order6_id", "point_index", "orbit_id", "orbit_size", "stabilizer_size"])
        for p in range(n_pts):
            sid = int(order6_ids[p])
            oid = int(orb_id_of_point[p]) if int(orb_id_of_point[p]) >= 0 else -1
            osz = int(len(orbits[oid])) if oid >= 0 else 0
            stab = 0
            for a in range(n_action):
                if int(perm_rows[a][p]) == int(p):
                    stab += 1
            w.writerow([sid, p, oid, osz, stab])

    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Run v3 order-6 PSL(2,7) action probe.")
    ap.add_argument("--random-trials", type=int, default=24)
    ap.add_argument("--random-seed", type=int, default=1337)
    args = ap.parse_args()

    payload = build_payload(random_trials=int(args.random_trials), random_seed=int(args.random_seed))
    print(f"order6_set_size={payload['order6_set_size']}")
    print(f"candidate_action_size={payload['candidate_action_size']}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_ORBITS}")


if __name__ == "__main__":
    main()


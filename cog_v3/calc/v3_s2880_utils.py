"""Shared utilities for S2880 (C12 x Q240) analysis scripts."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import numpy as np

from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


PHASE_COUNT = 12
PHASE_LABELS: Tuple[str, ...] = tuple("1" if p == 0 else f"zeta12^{p}" for p in range(PHASE_COUNT))
BASIS_LABELS = k.BASIS_LABELS


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def sid(phase_idx: int, q_id: int, *, phase_count: int = PHASE_COUNT, qn: int | None = None) -> int:
    if qn is None:
        qn = int(k.ALPHABET_SIZE)
    return int(phase_idx) * int(qn) + int(q_id)


def phase_q_from_sid(s_id: int, *, phase_count: int = PHASE_COUNT, qn: int | None = None) -> Tuple[int, int]:
    if qn is None:
        qn = int(k.ALPHABET_SIZE)
    return (int(s_id) // int(qn), int(s_id) % int(qn))


def phase_mul(a: int, b: int, *, phase_count: int = PHASE_COUNT) -> int:
    return int((int(a) + int(b)) % int(phase_count))


def phase_order(p: int, *, phase_count: int = PHASE_COUNT) -> int:
    pp = int(p) % int(phase_count)
    if pp == 0:
        return 1
    return int(phase_count // math.gcd(int(phase_count), pp))


def phase_angle_deg(p: int, *, phase_count: int = PHASE_COUNT) -> float:
    return float((360.0 * (int(p) % int(phase_count))) / float(phase_count))


def s_order(p: int, q_order: int, *, phase_count: int = PHASE_COUNT) -> int:
    return int(math.lcm(phase_order(int(p), phase_count=phase_count), int(q_order)))


def qmul_table() -> np.ndarray:
    qn = int(k.ALPHABET_SIZE)
    out = np.empty((qn, qn), dtype=np.uint16)
    for a in range(qn):
        for b in range(qn):
            out[a, b] = np.uint16(int(k.multiply_ids(int(a), int(b))))
    return out


def s_mul_sid(lhs_sid: int, rhs_sid: int, *, qmul: np.ndarray, phase_count: int = PHASE_COUNT) -> int:
    qn = int(qmul.shape[0])
    lp, lq = phase_q_from_sid(int(lhs_sid), phase_count=phase_count, qn=qn)
    rp, rq = phase_q_from_sid(int(rhs_sid), phase_count=phase_count, qn=qn)
    p = phase_mul(int(lp), int(rp), phase_count=phase_count)
    q = int(qmul[int(lq), int(rq)])
    return int(sid(int(p), int(q), phase_count=phase_count, qn=qn))


def q_orders_and_inverses(*, qmul: np.ndarray | None = None) -> Tuple[List[int], List[int]]:
    if qmul is None:
        qmul = qmul_table()
    qn = int(qmul.shape[0])
    identity = int(k.IDENTITY_ID)
    orders = [0] * qn
    inv = [0] * qn
    for q_id in range(qn):
        cur = int(q_id)
        order = 1
        while cur != identity:
            cur = int(qmul[cur, int(q_id)])
            order += 1
            if order > 4096:
                raise RuntimeError(f"Order search exceeded bound for q_id={q_id}")
        orders[int(q_id)] = int(order)
        # q^(order-1) as inverse in power-associative subloop
        acc = int(identity)
        for _ in range(int(order - 1)):
            acc = int(qmul[acc, int(q_id)])
        inv[int(q_id)] = int(acc)
    return orders, inv


def q_support_mask(oct_elem: tuple) -> int:
    mask = 0
    for i, c in enumerate(oct_elem):
        if c != 0:
            mask |= (1 << i)
    return int(mask)


def q_family_tag(support_size: int, has_e000: bool) -> str:
    if int(support_size) == 1:
        return "A16_basis_signed_unit"
    if int(support_size) == 4 and bool(has_e000):
        return "B112_line_plus_e000_halfsum"
    if int(support_size) == 4 and not bool(has_e000):
        return "C112_complement_halfsum"
    return "other"


def q_g2_proxy_tag(support_size: int, has_e000: bool, family_tag: str) -> str:
    if int(support_size) == 1 and bool(has_e000):
        return "G2_proxy_scalar2"
    if int(support_size) == 1 and not bool(has_e000):
        return "G2_proxy_pure_imag14"
    if family_tag == "B112_line_plus_e000_halfsum":
        return "G2_proxy_B112"
    if family_tag == "C112_complement_halfsum":
        return "G2_proxy_C112"
    return "G2_proxy_other"


def q_meta(*, q_orders: Sequence[int], q_inv: Sequence[int], qmul: np.ndarray | None = None) -> List[Dict[str, Any]]:
    if qmul is None:
        qmul = qmul_table()
    qn = int(qmul.shape[0])
    out: List[Dict[str, Any]] = []
    for q_id in range(qn):
        elem = k.ALPHABET[int(q_id)]
        support_size = int(sum(1 for c in elem if c != 0))
        has_e000 = bool(elem[0] != 0)
        has_e111 = bool(elem[7] != 0)
        fam = q_family_tag(int(support_size), bool(has_e000))
        g2 = q_g2_proxy_tag(int(support_size), bool(has_e000), fam)
        out.append(
            {
                "q_id": int(q_id),
                "q_label": k.elem_label(int(q_id)),
                "q_order": int(q_orders[int(q_id)]),
                "q_inverse_id": int(q_inv[int(q_id)]),
                "q_support_size": int(support_size),
                "q_support_mask_bin": format(q_support_mask(elem), "08b"),
                "q_has_e000": bool(has_e000),
                "q_has_e111": bool(has_e111),
                "q_family_tag": fam,
                "q_g2_proxy_tag": g2,
                "q_norm_scalar": str(k.oct_norm_scalar(elem)),
                "q_coeffs": tuple(elem),
            }
        )
    return out


def q_conjugation_and_centralizers(
    *,
    qmul: np.ndarray,
    q_inv: Sequence[int],
) -> Dict[str, Any]:
    qn = int(qmul.shape[0])
    left_orbit_size = [0] * qn
    right_orbit_size = [0] * qn
    left_rep = [0] * qn
    right_rep = [0] * qn
    q_centralizer_size = [0] * qn

    for x in range(qn):
        lset: set[int] = set()
        rset: set[int] = set()
        cz = 0
        for g in range(qn):
            gi = int(q_inv[int(g)])
            # (g*x)*g^-1
            lval = int(qmul[int(qmul[int(g), int(x)]), gi])
            # g*(x*g^-1)
            rval = int(qmul[int(g), int(qmul[int(x), gi])])
            lset.add(int(lval))
            rset.add(int(rval))
            if int(qmul[int(x), int(g)]) == int(qmul[int(g), int(x)]):
                cz += 1
        left_orbit_size[int(x)] = int(len(lset))
        right_orbit_size[int(x)] = int(len(rset))
        left_rep[int(x)] = int(min(lset))
        right_rep[int(x)] = int(min(rset))
        q_centralizer_size[int(x)] = int(cz)

    return {
        "left_orbit_size": left_orbit_size,
        "right_orbit_size": right_orbit_size,
        "left_rep": left_rep,
        "right_rep": right_rep,
        "q_centralizer_size": q_centralizer_size,
    }


def label_sid(s_id: int, *, phase_count: int = PHASE_COUNT, qn: int | None = None) -> str:
    if qn is None:
        qn = int(k.ALPHABET_SIZE)
    p, q_id = phase_q_from_sid(int(s_id), phase_count=phase_count, qn=qn)
    q_label = k.elem_label(int(q_id))
    if int(p) == 0:
        return q_label
    return f"{PHASE_LABELS[int(p)]}*({q_label})"


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, *, fieldnames: Sequence[str], rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fieldnames))
        w.writeheader()
        for r in rows:
            w.writerow(r)


def open_csv_like(path: Path, *, gzip_output: bool) -> Tuple[Any, csv.writer]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if gzip_output:
        fh = gzip.open(path, "wt", newline="", encoding="utf-8")
    else:
        fh = path.open("w", newline="", encoding="utf-8")
    return fh, csv.writer(fh)


def frac_to_complex_phase_coeff(c: Fraction, p: int, *, phase_count: int = PHASE_COUNT) -> str:
    # Human-readable pseudo-complex coefficient c * exp(i*theta)
    if c == 0:
        return "0"
    angle = phase_angle_deg(int(p), phase_count=phase_count)
    return f"{c}*exp(i*{angle:.1f}deg)"


def entropy_from_counts(counts: Iterable[int]) -> float:
    vals = [int(x) for x in counts if int(x) > 0]
    total = int(sum(vals))
    if total <= 0:
        return 0.0
    h = 0.0
    for v in vals:
        p = float(v) / float(total)
        h -= p * math.log(p, 2.0)
    return float(h)


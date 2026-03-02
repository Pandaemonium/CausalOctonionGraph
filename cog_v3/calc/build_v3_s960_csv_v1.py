"""Export the canonical v3 S960 alphabet (C4 x Q240) to CSV."""

from __future__ import annotations

import argparse
import csv
from fractions import Fraction
from pathlib import Path
from typing import Dict, Sequence, Tuple

from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_s960_elements_v1.csv"

PHASE_LABELS: Tuple[str, ...] = ("1", "i", "-1", "-i")
PHASE_ORDER: Tuple[int, ...] = (1, 4, 2, 4)
PHASE_COUNT = 4
S960_SIZE = PHASE_COUNT * int(k.ALPHABET_SIZE)
S960_IDENTITY = 0 * int(k.ALPHABET_SIZE) + int(k.IDENTITY_ID)


def _sid(phase_idx: int, q_id: int) -> int:
    return int(phase_idx) * int(k.ALPHABET_SIZE) + int(q_id)


def _phase_q_from_sid(sid: int) -> Tuple[int, int]:
    qn = int(k.ALPHABET_SIZE)
    return (int(sid) // qn, int(sid) % qn)


def _phase_mul(a: int, b: int) -> int:
    return int((int(a) + int(b)) % PHASE_COUNT)


def _s_mul(lhs_sid: int, rhs_sid: int) -> int:
    lp, lq = _phase_q_from_sid(int(lhs_sid))
    rp, rq = _phase_q_from_sid(int(rhs_sid))
    p = _phase_mul(int(lp), int(rp))
    q = int(k.multiply_ids(int(lq), int(rq)))
    return int(_sid(int(p), int(q)))


def _element_order(sid: int) -> int:
    seed = int(sid)
    cur = seed
    order = 1
    while cur != int(S960_IDENTITY):
        cur = _s_mul(int(cur), int(seed))
        order += 1
        if order > 4096:
            raise RuntimeError(f"Order search exceeded bound for sid={sid}")
    return int(order)


def _power_sid(sid: int, exponent: int) -> int:
    if exponent < 0:
        raise ValueError("Exponent must be non-negative.")
    cur = int(S960_IDENTITY)
    for _ in range(int(exponent)):
        cur = _s_mul(int(cur), int(sid))
    return int(cur)


def _power_orbit_group(sid: int, order: int) -> tuple[int, ...]:
    cur = int(S960_IDENTITY)
    orbit_ids: list[int] = [int(cur)]
    for _ in range(1, int(order)):
        cur = _s_mul(int(cur), int(sid))
        orbit_ids.append(int(cur))
    return tuple(sorted(set(orbit_ids)))


def _support_mask(oct_elem: tuple) -> int:
    mask = 0
    for idx, coeff in enumerate(oct_elem):
        if coeff != 0:
            mask |= (1 << idx)
    return int(mask)


def _q_family_tag(support_size: int, has_e000: bool) -> str:
    if support_size == 1:
        return "A16_basis_signed_unit"
    if support_size == 4 and has_e000:
        return "B112_line_plus_e000_halfsum"
    if support_size == 4 and not has_e000:
        return "C112_complement_halfsum"
    return "other"


def _q_g2_proxy_tag(support_size: int, has_e000: bool, family_tag: str) -> str:
    if support_size == 1 and has_e000:
        return "G2_proxy_scalar2"
    if support_size == 1 and not has_e000:
        return "G2_proxy_pure_imag14"
    if family_tag == "B112_line_plus_e000_halfsum":
        return "G2_proxy_B112"
    if family_tag == "C112_complement_halfsum":
        return "G2_proxy_C112"
    return "G2_proxy_other"


def _phase_apply_coeff(c: Fraction, phase_idx: int) -> str:
    if c == 0:
        return "0"
    p = int(phase_idx)
    if p == 0:
        return str(c)
    if p == 1:
        return f"{c}*i"
    if p == 2:
        return str(-c)
    return f"{-c}*i"


def _rows() -> Sequence[dict[str, str]]:
    # Precompute q-side orders and negation in Q240.
    q_orders: Dict[int, int] = {}
    for q_id in range(int(k.ALPHABET_SIZE)):
        cur = int(q_id)
        order = 1
        while cur != int(k.IDENTITY_ID):
            cur = int(k.multiply_ids(int(cur), int(q_id)))
            order += 1
            if order > 4096:
                raise RuntimeError(f"Q240 order search exceeded bound for q_id={q_id}")
        q_orders[int(q_id)] = int(order)

    q_neg_one = (
        Fraction(-1, 1),
        Fraction(0, 1),
        Fraction(0, 1),
        Fraction(0, 1),
        Fraction(0, 1),
        Fraction(0, 1),
        Fraction(0, 1),
        Fraction(0, 1),
    )
    q_neg_one_id = int(k.ALPHABET_INDEX[q_neg_one])
    q_neg_id: Dict[int, int] = {
        int(q_id): int(k.multiply_ids(int(q_id), int(q_neg_one_id)))
        for q_id in range(int(k.ALPHABET_SIZE))
    }

    records: list[dict[str, object]] = []
    for phase_idx in range(PHASE_COUNT):
        for q_id, oct_elem in enumerate(k.ALPHABET):
            sid = int(_sid(int(phase_idx), int(q_id)))
            order = _element_order(int(sid))
            orbit = _power_orbit_group(int(sid), int(order))
            support_size = sum(1 for c in oct_elem if c != 0)
            mask = _support_mask(oct_elem)
            has_e000 = bool(oct_elem[0] != 0)
            has_e111 = bool(oct_elem[7] != 0)
            nonzero_basis = "|".join(
                k.BASIS_LABELS[idx] for idx, c in enumerate(oct_elem) if c != 0
            )
            pos_count = sum(1 for c in oct_elem if c > 0)
            neg_count = sum(1 for c in oct_elem if c < 0)
            sum_coeff = sum(oct_elem)
            sum_abs_coeff = sum(abs(c) for c in oct_elem)
            norm_scalar = k.oct_norm_scalar(oct_elem)
            q_family = _q_family_tag(int(support_size), bool(has_e000))
            q_g2 = _q_g2_proxy_tag(int(support_size), bool(has_e000), q_family)
            inverse_id = _power_sid(int(sid), int(order - 1))
            square_id = _power_sid(int(sid), 2)
            cube_id = _power_sid(int(sid), 3)
            neg_phase_id = int(_sid(int((phase_idx + 2) % 4), int(q_id)))
            neg_q_sid = int(_sid(int(phase_idx), int(q_neg_id[int(q_id)])))
            is_self_inverse = bool(square_id == int(S960_IDENTITY))
            orbit_rep_id = min(orbit)
            orbit_index = orbit.index(int(sid))
            rec: dict[str, object] = {
                "id": int(sid),
                "label": (
                    k.elem_label(int(q_id))
                    if int(phase_idx) == 0
                    else f"{PHASE_LABELS[int(phase_idx)]}*({k.elem_label(int(q_id))})"
                ),
                "alphabet_id": "s960_shared_phase_v1",
                "convention_id": k.CONVENTION_ID,
                "kernel_profile": k.KERNEL_PROFILE,
                "phase_idx": int(phase_idx),
                "phase_label": PHASE_LABELS[int(phase_idx)],
                "phase_order": int(PHASE_ORDER[int(phase_idx)]),
                "q_id": int(q_id),
                "q_label": k.elem_label(int(q_id)),
                "q_order": int(q_orders[int(q_id)]),
                "q_family_tag": q_family,
                "q_g2_proxy_tag": q_g2,
                "order": int(order),
                "orbit_size": int(len(orbit)),
                "orbit_rep_id": int(orbit_rep_id),
                "orbit_index": int(orbit_index),
                "orbit_group": orbit,
                "support_size": int(support_size),
                "support_mask_bin": format(int(mask), "08b"),
                "support_mask_hex": hex(int(mask)),
                "nonzero_basis": nonzero_basis,
                "has_e000": bool(has_e000),
                "has_e111": bool(has_e111),
                "coeff_pos_count": int(pos_count),
                "coeff_neg_count": int(neg_count),
                "sum_coeff": sum_coeff,
                "sum_abs_coeff": sum_abs_coeff,
                "norm_scalar": norm_scalar,
                "inverse_id": int(inverse_id),
                "square_id": int(square_id),
                "cube_id": int(cube_id),
                "neg_phase_id": int(neg_phase_id),
                "neg_q_id": int(neg_q_sid),
                "is_self_inverse": bool(is_self_inverse),
                "q_coeffs": oct_elem,
            }
            records.append(rec)

    # Class maps for additional orbit notions.
    order_groups: dict[int, list[int]] = {}
    phase_groups: dict[int, list[int]] = {}
    q_groups: dict[int, list[int]] = {}
    q_order_groups: dict[int, list[int]] = {}
    q_family_groups: dict[str, list[int]] = {}
    q_g2_groups: dict[str, list[int]] = {}
    for rec in records:
        sid = int(rec["id"])
        order_groups.setdefault(int(rec["order"]), []).append(sid)
        phase_groups.setdefault(int(rec["phase_idx"]), []).append(sid)
        q_groups.setdefault(int(rec["q_id"]), []).append(sid)
        q_order_groups.setdefault(int(rec["q_order"]), []).append(sid)
        q_family_groups.setdefault(str(rec["q_family_tag"]), []).append(sid)
        q_g2_groups.setdefault(str(rec["q_g2_proxy_tag"]), []).append(sid)

    inverse_ids = {int(rec["id"]): int(rec["inverse_id"]) for rec in records}
    all_ids = [int(rec["id"]) for rec in records]

    # Inner-conjugation orbit sizes in S960.
    inner_conj_l_size: dict[int, int] = {}
    inner_conj_r_size: dict[int, int] = {}
    for x in all_ids:
        lset: set[int] = set()
        rset: set[int] = set()
        for g in all_ids:
            g_inv = inverse_ids[g]
            lval = _s_mul(_s_mul(g, x), g_inv)  # (g*x)*g^-1
            rval = _s_mul(g, _s_mul(x, g_inv))  # g*(x*g^-1)
            lset.add(int(lval))
            rset.add(int(rval))
        inner_conj_l_size[x] = int(len(lset))
        inner_conj_r_size[x] = int(len(rset))

    out: list[dict[str, str]] = []
    for rec in records:
        sid = int(rec["id"])
        q_id = int(rec["q_id"])
        phase_idx = int(rec["phase_idx"])
        orbit = tuple(int(x) for x in rec["orbit_group"])  # type: ignore[assignment]
        order_group = sorted(order_groups[int(rec["order"])])
        phase_group = sorted(phase_groups[int(phase_idx)])
        q_group = sorted(q_groups[int(q_id)])
        q_order_group = sorted(q_order_groups[int(rec["q_order"])])
        q_family_group = sorted(q_family_groups[str(rec["q_family_tag"])])
        q_g2_group = sorted(q_g2_groups[str(rec["q_g2_proxy_tag"])])
        neg_phase_group = sorted({sid, int(rec["neg_phase_id"])})
        neg_q_group = sorted({sid, int(rec["neg_q_id"])})
        inv_group = sorted({sid, int(rec["inverse_id"])})

        row: dict[str, str] = {
            "id": str(int(sid)),
            "label": str(rec["label"]),
            "alphabet_id": str(rec["alphabet_id"]),
            "convention_id": str(rec["convention_id"]),
            "kernel_profile": str(rec["kernel_profile"]),
            "phase_idx": str(int(phase_idx)),
            "phase_label": str(rec["phase_label"]),
            "phase_order": str(int(rec["phase_order"])),
            "q_id": str(int(q_id)),
            "q_label": str(rec["q_label"]),
            "q_order": str(int(rec["q_order"])),
            "q_family_tag": str(rec["q_family_tag"]),
            "q_g2_proxy_tag": str(rec["q_g2_proxy_tag"]),
            "order": str(int(rec["order"])),
            "orbit_size": str(int(rec["orbit_size"])),
            "orbit_rep_id": str(int(rec["orbit_rep_id"])),
            "orbit_index": str(int(rec["orbit_index"])),
            "orbit_group": "|".join(str(int(x)) for x in orbit),
            "orbit_group_negation_phase": "|".join(str(int(x)) for x in neg_phase_group),
            "orbit_group_negation_q": "|".join(str(int(x)) for x in neg_q_group),
            "orbit_group_inverse": "|".join(str(int(x)) for x in inv_group),
            "orbit_group_order_class": "|".join(str(int(x)) for x in order_group),
            "orbit_group_phase_class": "|".join(str(int(x)) for x in phase_group),
            "orbit_group_q_class": "|".join(str(int(x)) for x in q_group),
            "orbit_group_q_order_class": "|".join(str(int(x)) for x in q_order_group),
            "orbit_group_q_family_class": "|".join(str(int(x)) for x in q_family_group),
            "orbit_group_q_g2_proxy_class": "|".join(str(int(x)) for x in q_g2_group),
            "inner_conj_l_orbit_size": str(int(inner_conj_l_size[sid])),
            "inner_conj_r_orbit_size": str(int(inner_conj_r_size[sid])),
            "support_size": str(int(rec["support_size"])),
            "support_mask_bin": str(rec["support_mask_bin"]),
            "support_mask_hex": str(rec["support_mask_hex"]),
            "nonzero_basis": str(rec["nonzero_basis"]),
            "has_e000": str(bool(rec["has_e000"])).lower(),
            "has_e111": str(bool(rec["has_e111"])).lower(),
            "coeff_pos_count": str(int(rec["coeff_pos_count"])),
            "coeff_neg_count": str(int(rec["coeff_neg_count"])),
            "sum_coeff": str(rec["sum_coeff"]),
            "sum_abs_coeff": str(rec["sum_abs_coeff"]),
            "norm_scalar": str(rec["norm_scalar"]),
            "inverse_id": str(int(rec["inverse_id"])),
            "square_id": str(int(rec["square_id"])),
            "cube_id": str(int(rec["cube_id"])),
            "neg_phase_id": str(int(rec["neg_phase_id"])),
            "neg_q_id": str(int(rec["neg_q_id"])),
            "is_self_inverse": str(bool(rec["is_self_inverse"])).lower(),
        }

        q_coeffs = rec["q_coeffs"]  # type: ignore[assignment]
        for basis_idx, basis_label in enumerate(k.BASIS_LABELS):
            coeff = q_coeffs[basis_idx]  # type: ignore[index]
            row[f"q_{basis_label}"] = str(coeff)
            row[f"c_{basis_label}"] = _phase_apply_coeff(coeff, int(phase_idx))
        out.append(row)
    return out


def build_csv(out_csv: Path) -> Path:
    rows = _rows()
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "id",
        "label",
        "alphabet_id",
        "convention_id",
        "kernel_profile",
        "phase_idx",
        "phase_label",
        "phase_order",
        "q_id",
        "q_label",
        "q_order",
        "q_family_tag",
        "q_g2_proxy_tag",
        "order",
        "orbit_size",
        "orbit_rep_id",
        "orbit_index",
        "orbit_group",
        "orbit_group_negation_phase",
        "orbit_group_negation_q",
        "orbit_group_inverse",
        "orbit_group_order_class",
        "orbit_group_phase_class",
        "orbit_group_q_class",
        "orbit_group_q_order_class",
        "orbit_group_q_family_class",
        "orbit_group_q_g2_proxy_class",
        "inner_conj_l_orbit_size",
        "inner_conj_r_orbit_size",
        "support_size",
        "support_mask_bin",
        "support_mask_hex",
        "nonzero_basis",
        "has_e000",
        "has_e111",
        "coeff_pos_count",
        "coeff_neg_count",
        "sum_coeff",
        "sum_abs_coeff",
        "norm_scalar",
        "inverse_id",
        "square_id",
        "cube_id",
        "neg_phase_id",
        "neg_q_id",
        "is_self_inverse",
        *[f"q_{b}" for b in k.BASIS_LABELS],
        *[f"c_{b}" for b in k.BASIS_LABELS],
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return out_csv


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export v3 S960 alphabet to CSV.")
    p.add_argument(
        "--out-csv",
        type=str,
        default=str(OUT_CSV),
        help="Output CSV path.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out_path = Path(args.out_csv).resolve()
    written = build_csv(out_path)
    print(f"Wrote {written}")
    print(f"s960_size={S960_SIZE}")


if __name__ == "__main__":
    main()


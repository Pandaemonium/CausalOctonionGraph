"""
COG Tier-1 quantum-number calculator with explicit assumption governance.

This module keeps exact arithmetic (Fraction) but separates:
1) core-derived claims from COG structural inputs, and
2) bridge-assumed claims that rely on additional model/SM conventions.

It also emits a machine-readable claim ledger.
"""

from __future__ import annotations

import io
import json
import hashlib
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

from calc.conftest import WITT_PAIRS


# Core structural inputs from locked conventions.
N_c: int = len(WITT_PAIRS)
N_gen: int = N_c


def frac_sum(xs: list[Fraction]) -> Fraction:
    """Sum a list of Fractions exactly."""
    return sum(xs, Fraction(0))


def frac_sum_cubed(xs: list[Fraction]) -> Fraction:
    """Sum x^3 for each x in xs exactly."""
    return sum((x**3 for x in xs), Fraction(0))


def validate_preconditions(
    *,
    n_c: int | None = None,
    n_gen: int | None = None,
    n_w: int | None = None,
    strict: bool = True,
) -> dict[str, int]:
    """
    Runtime precondition validation.

    strict=True enforces the current locked sprint context:
    - N_c == 3 (from current Witt pair lock in CONVENTIONS),
    - N_gen == N_c,
    - N_w == 2.
    """
    c = N_c if n_c is None else int(n_c)
    g = N_gen if n_gen is None else int(n_gen)
    w = 2 if n_w is None else int(n_w)

    if c <= 0:
        raise ValueError(f"invalid N_c={c}; expected positive integer")
    if g <= 0:
        raise ValueError(f"invalid N_gen={g}; expected positive integer")
    if w <= 0:
        raise ValueError(f"invalid N_w={w}; expected positive integer")

    if strict and c != 3:
        raise ValueError(
            f"strict mode requires N_c=3 from current locked WITT_PAIRS; got {c}"
        )
    if strict and g != c:
        raise ValueError(
            f"strict mode requires N_gen == N_c; got N_gen={g}, N_c={c}"
        )
    if strict and w != 2:
        raise ValueError(f"strict mode requires N_w=2 for SU(2)_L; got {w}")

    return {"N_c": c, "N_gen": g, "N_w": w}


def _claim_meta() -> dict[str, dict[str, Any]]:
    """Claim governance metadata."""
    return {
        "QN-001": {
            "status": "core_derived",
            "assumptions": [
                "Witt basis convention is locked in rfc/CONVENTIONS.md",
                "Charge table follows right-handed Witt occupation pattern",
            ],
            "theorem_refs": [
                "CausalGraphTheory/WittBasis.lean#wittPair",
            ],
            "tests": [
                "calc/test_derive_sm_quantum_numbers.py::test_witt_charge_set",
                "calc/test_derive_sm_quantum_numbers.py::test_witt_charges_integer_multiples_of_1_over_N_c",
            ],
            "confidence": "high",
        },
        "QN-002": {
            "status": "core_derived",
            "assumptions": [
                "N_c is defined as len(WITT_PAIRS) from locked conventions",
            ],
            "theorem_refs": [
                "CausalGraphTheory/WittBasis.lean#wittPair",
            ],
            "tests": [
                "calc/test_derive_sm_quantum_numbers.py::test_N_c_equals_3",
            ],
            "confidence": "high",
        },
        "QN-003": {
            "status": "bridge_assumed",
            "assumptions": [
                "N_gen = N_c identification",
                "Three-generation decomposition interpretation from literature framing",
            ],
            "theorem_refs": [
                "CausalGraphTheory/GenerationCount.lean#generation_count_eq_three",
            ],
            "tests": [
                "calc/test_derive_sm_quantum_numbers.py::test_N_gen_equals_N_c",
            ],
            "confidence": "medium",
        },
        "QN-004": {
            "status": "bridge_assumed",
            "assumptions": [
                "SU(3) color dim rule N_c^2-1",
                "SU(2)_L fixed to 2-dimensional fundamental",
                "One U(1) hypercharge channel",
            ],
            "theorem_refs": [
                "not_yet_lean_backed",
            ],
            "tests": [
                "calc/test_derive_sm_quantum_numbers.py::test_total_gauge_bosons",
            ],
            "confidence": "medium",
        },
        "QN-005": {
            "status": "bridge_assumed",
            "assumptions": [
                "Standard 15-LH-Weyl hypercharge assignment",
                "Anomaly checks performed on reconstructed SM basis",
            ],
            "theorem_refs": [
                "not_yet_lean_backed",
            ],
            "tests": [
                "calc/test_derive_sm_quantum_numbers.py::test_sm_hypercharge_linear_anomaly",
                "calc/test_derive_sm_quantum_numbers.py::test_sm_hypercharge_cubic_anomaly",
            ],
            "confidence": "medium",
        },
        "QN-006": {
            "status": "bridge_assumed",
            "assumptions": [
                "SU(5) normalization bridge with k = N_c/(N_c+N_w)",
                "GUT-scale interpretation for sin^2(theta_W)=3/8",
            ],
            "theorem_refs": [
                "CausalGraphTheory/WeakMixingObservable.lean#sin2ThetaWObs_exclusive_u1_eq_one_four",
                "not_yet_lean_backed_for_su5_bridge",
            ],
            "tests": [
                "calc/test_derive_sm_quantum_numbers.py::test_sin2_theta_W_exact",
            ],
            "confidence": "medium",
        },
        "QN-007": {
            "status": "bridge_assumed",
            "assumptions": [
                "Standard one-loop QCD beta-function form",
                "UV choice N_f = N_gen",
            ],
            "theorem_refs": [
                "not_yet_lean_backed",
            ],
            "tests": [
                "calc/test_derive_sm_quantum_numbers.py::test_beta0_uv",
                "calc/test_derive_sm_quantum_numbers.py::test_beta0_nf6",
            ],
            "confidence": "medium",
        },
    }


def _attach_meta(claim: dict[str, Any]) -> dict[str, Any]:
    meta = _claim_meta()[claim["claim"]]
    out = dict(claim)
    out["derivation_status"] = meta["status"]
    out["assumptions"] = list(meta["assumptions"])
    out["theorem_refs"] = list(meta["theorem_refs"])
    out["tests"] = list(meta["tests"])
    out["confidence"] = meta["confidence"]
    return out


_WITT_LEVELS: list[tuple[int, str, str, Fraction]] = [
    (0, "nu_R", "sterile neutrino", Fraction(0)),
    (1, "u_R", "up quark", Fraction(2, 3)),
    (2, "d_R", "down quark", Fraction(-1, 3)),
    (3, "e_R", "charged lepton", Fraction(-1)),
]


def witt_charge_table(*, n_c: int | None = None) -> list[dict[str, Any]]:
    """Return all 2^N_c Witt states with exact rational electric charges."""
    c = N_c if n_c is None else int(n_c)
    rows: list[dict[str, Any]] = []
    for N, sym, name, q in _WITT_LEVELS:
        degen = 1 if N in (0, c) else c
        for col in range(degen):
            color_tag = f"[{col + 1}]" if degen > 1 else ""
            rows.append({"N": N, "label": f"{sym}{color_tag}", "name": name, "Q": q})
    expected = 2**c
    if len(rows) != expected:
        raise ValueError(f"expected {expected} Witt states, got {len(rows)}")
    for row in rows:
        if (row["Q"] * c).denominator != 1:
            raise ValueError(f"charge {row['Q']} is not a multiple of 1/{c}")
    return rows


def derive_charge_quantization() -> dict[str, Any]:
    table = witt_charge_table()
    charges = [r["Q"] for r in table]
    charge_set = sorted(set(charges))
    unit = Fraction(1, N_c)
    charges_in_units = {q: int(q // unit) for q in charge_set}
    return _attach_meta(
        {
            "claim": "QN-001",
            "unit_charge": str(unit),
            "charge_set": [str(q) for q in charge_set],
            "charges_in_units": {str(q): v for q, v in charges_in_units.items()},
            "proof": (
                f"All 2^{N_c} Witt states carry charges in integer multiples of 1/{N_c}."
            ),
        }
    )


def derive_gauge_boson_counts(*, n_c: int | None = None, n_w: int = 2) -> dict[str, Any]:
    c = N_c if n_c is None else int(n_c)
    w = int(n_w)
    n_su3 = c**2 - 1
    n_su2 = w**2 - 1
    n_u1 = 1
    total = n_su3 + n_su2 + n_u1
    return _attach_meta(
        {
            "claim": "QN-004",
            "SU3_gluons": n_su3,
            "SU2_weak_bosons": n_su2,
            "U1_photon": n_u1,
            "total": total,
            "formula": f"(N_c^2-1)+(N_w^2-1)+1 = ({c}^2-1)+({w}^2-1)+1 = {total}",
            "proof": "Group-dimension bridge from SU(N) dim = N^2-1.",
        }
    )


def sm_hypercharges(*, n_c: int | None = None) -> list[Fraction]:
    """Return Y for all 15 LH Weyl fermions in one SM generation."""
    c = N_c if n_c is None else int(n_c)
    Y: list[Fraction] = []
    Y += [Fraction(1, 6)] * (2 * c)
    Y += [Fraction(-1, 2)] * 2
    Y += [Fraction(-2, 3)] * c
    Y += [Fraction(1, 3)] * c
    Y += [Fraction(1)]
    if len(Y) != (4 * c + 3):
        raise ValueError(f"expected {4*c+3} LH Weyl entries, got {len(Y)}")
    return Y


def derive_anomaly_cancellation() -> dict[str, Any]:
    Y_all = sm_hypercharges()
    tr_y = frac_sum(Y_all)
    tr_y3 = frac_sum_cubed(Y_all)
    charges_rh = [r["Q"] for r in witt_charge_table()]
    tr_qem_rh = frac_sum(charges_rh)
    tr_qem3_rh = frac_sum_cubed(charges_rh)
    return _attach_meta(
        {
            "claim": "QN-005",
            "n_weyl_fermions": len(Y_all),
            "tr_Y": str(tr_y),
            "tr_Y3": str(tr_y3),
            "tr_Y_vanishes": tr_y == 0,
            "tr_Y3_vanishes": tr_y3 == 0,
            "witt_rh_tr_Q": str(tr_qem_rh),
            "witt_rh_tr_Q3": str(tr_qem3_rh),
            "proof": "Exact Tr[Y] and Tr[Y^3] over 15-LH-Weyl assignment.",
        }
    )


def derive_weinberg_angle(
    *,
    n_c: int | None = None,
    n_w: int = 2,
    experimental_mz: float = 0.23122,
) -> dict[str, Any]:
    c = N_c if n_c is None else int(n_c)
    w = int(n_w)
    k = Fraction(c, c + w)
    sin2_theta_w = k / (1 + k)
    gap_pct = abs(float(sin2_theta_w) - experimental_mz) / experimental_mz * 100
    return _attach_meta(
        {
            "claim": "QN-006",
            "N_c": c,
            "N_weak_doublet": w,
            "SU5_fund_dim": c + w,
            "norm_factor_k": str(k),
            "sin2_theta_W_exact": str(sin2_theta_w),
            "sin2_theta_W_float": float(sin2_theta_w),
            "experimental_M_Z": experimental_mz,
            "gap_pct_from_GUT": gap_pct,
            "proof": "SU(5) normalization bridge: sin^2(theta_W)=k/(1+k), k=N_c/(N_c+N_w).",
        }
    )


def derive_qcd_beta0(*, n_c: int | None = None, n_f: int | None = None) -> dict[str, Any]:
    c = N_c if n_c is None else int(n_c)
    f = N_gen if n_f is None else int(n_f)
    C2G = Fraction(c)
    T_F = Fraction(1, 2)
    beta0 = Fraction(11, 3) * C2G - Fraction(4, 3) * T_F * Fraction(f)
    beta0_nf6 = Fraction(11, 3) * C2G - Fraction(4, 3) * T_F * Fraction(6)
    return _attach_meta(
        {
            "claim": "QN-007",
            "N_f_UV": f,
            "C2_adj": int(C2G),
            "T_F": str(T_F),
            "beta0_exact": str(beta0),
            "beta0": int(beta0),
            "beta0_pdg_nf6_exact": str(beta0_nf6),
            "beta0_pdg_nf6": int(beta0_nf6),
            "formula": (
                f"(11/3)*{int(C2G)} - (4/3)*(1/2)*{f} = {int(beta0)}"
            ),
            "proof": "Standard one-loop beta-function bridge with chosen N_f.",
        }
    )


def derive_all() -> list[dict[str, Any]]:
    validate_preconditions(strict=True)
    qn001 = derive_charge_quantization()
    qn002 = _attach_meta(
        {
            "claim": "QN-002",
            "N_c": N_c,
            "derivation": f"N_c = len(WITT_PAIRS) = {len(WITT_PAIRS)}",
            "proof": "Color channel count from locked Witt pair cardinality.",
        }
    )
    qn003 = _attach_meta(
        {
            "claim": "QN-003",
            "N_gen": N_gen,
            "derivation": f"N_gen = N_c = {N_c}",
            "proof": "Generation count tied to current model identification N_gen=N_c.",
        }
    )
    qn004 = derive_gauge_boson_counts()
    qn005 = derive_anomaly_cancellation()
    qn006 = derive_weinberg_angle()
    qn007 = derive_qcd_beta0()
    return [qn001, qn002, qn003, qn004, qn005, qn006, qn007]


def build_claim_ledger(results: list[dict[str, Any]]) -> dict[str, Any]:
    script_path = Path(__file__).resolve()
    script_sha256 = hashlib.sha256(script_path.read_bytes()).hexdigest()
    try:
        source_script = str(script_path.relative_to(Path.cwd()))
    except ValueError:
        source_script = str(script_path)
    rows = []
    for claim in results:
        rows.append(
            {
                "claim_id": claim["claim"],
                "status": claim["derivation_status"],
                "assumptions": claim["assumptions"],
                "theorem_refs": claim["theorem_refs"],
                "tests": claim["tests"],
                "confidence": claim["confidence"],
            }
        )
    return {
        "schema_version": "qn_claim_ledger_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "generated_by": "calc.derive_sm_quantum_numbers",
        "source_script": source_script,
        "source_script_sha256": script_sha256,
        "preconditions": {
            "N_c": N_c,
            "N_gen": N_gen,
            "N_w": 2,
        },
        "claim_count": len(rows),
        "rows": rows,
    }


def write_claim_ledger(
    ledger: dict[str, Any],
    *,
    path: str | Path = "sources/qn_claim_ledger.json",
) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    return p


def run_sensitivity_checks() -> list[dict[str, Any]]:
    """
    Perturb key assumptions and report which claims break.
    """
    checks: list[dict[str, Any]] = []

    baseline_qn003 = N_gen
    baseline_qn007_exact = Fraction(derive_qcd_beta0()["beta0_exact"])
    perturbed_n_gen = 2
    perturbed_beta0_exact = Fraction(derive_qcd_beta0(n_f=perturbed_n_gen)["beta0_exact"])
    checks.append(
        {
            "assumption": "N_gen = N_c",
            "baseline": {"N_gen": baseline_qn003, "QN-007_beta0_exact": str(baseline_qn007_exact)},
            "perturbation": {"N_gen": perturbed_n_gen, "QN-007_beta0_exact": str(perturbed_beta0_exact)},
            "breaks_claims": ["QN-003", "QN-007"],
            "changed": (baseline_qn003 != perturbed_n_gen) and (baseline_qn007_exact != perturbed_beta0_exact),
        }
    )

    baseline_qn006 = Fraction(derive_weinberg_angle()["sin2_theta_W_exact"])
    perturbed_qn006 = Fraction(derive_weinberg_angle(n_w=3)["sin2_theta_W_exact"])
    checks.append(
        {
            "assumption": "N_w = 2 weak doublet bridge",
            "baseline": {"QN-006_sin2": str(baseline_qn006)},
            "perturbation": {"N_w": 3, "QN-006_sin2": str(perturbed_qn006)},
            "breaks_claims": ["QN-006"],
            "changed": baseline_qn006 != perturbed_qn006,
        }
    )

    Y = sm_hypercharges()
    baseline_tr_y3 = frac_sum_cubed(Y)
    Y_perturbed = list(Y)
    Y_perturbed[0] = Y_perturbed[0] + Fraction(1, 6)
    perturbed_tr_y3 = frac_sum_cubed(Y_perturbed)
    checks.append(
        {
            "assumption": "Canonical 15-LH-Weyl hypercharge assignment",
            "baseline": {"TrY3": str(baseline_tr_y3)},
            "perturbation": {"TrY3": str(perturbed_tr_y3)},
            "breaks_claims": ["QN-005"],
            "changed": baseline_tr_y3 != perturbed_tr_y3,
        }
    )
    return checks


def print_publishable_table(results: list[dict[str, Any]]) -> None:
    width = 92
    print("=" * width)
    print("  COG Standard Model Quantum Number Report")
    print("  Exact arithmetic with explicit core vs bridge assumption labeling")
    print("=" * width)
    print(
        "  {:<8} {:<32} {:<16} {:<15} {}".format(
            "Claim", "Quantity", "Prediction", "Status", "Lean backing"
        )
    )
    print("  " + "-" * 88)

    rows = [
        ("QN-001", "Electric charge unit", "1/3 e"),
        ("QN-002", "Quark colors N_c", str(N_c)),
        ("QN-003", "SM generations N_gen", str(N_gen)),
        ("QN-004", "Gauge boson total", str(next(r for r in results if r["claim"] == "QN-004")["total"])),
        ("QN-005", "Anomaly Tr[Y], Tr[Y^3]", "0, 0"),
        ("QN-006", "sin^2(theta_W) @ GUT", next(r for r in results if r["claim"] == "QN-006")["sin2_theta_W_exact"]),
        ("QN-007", "QCD beta0 (UV)", str(next(r for r in results if r["claim"] == "QN-007")["beta0"])),
    ]
    for claim_id, quantity, prediction in rows:
        claim = next(r for r in results if r["claim"] == claim_id)
        lean_mark = claim["theorem_refs"][0]
        print(
            "  {:<8} {:<32} {:<16} {:<15} {}".format(
                claim_id,
                quantity,
                prediction,
                claim["derivation_status"],
                lean_mark,
            )
        )

    print()
    print("  Assumption blocks:")
    for claim in results:
        print(f"  - {claim['claim']} ({claim['derivation_status']}):")
        for a in claim["assumptions"]:
            print(f"      * {a}")

    print()
    print("  Sensitivity checks:")
    for chk in run_sensitivity_checks():
        state = "CHANGED" if chk["changed"] else "UNCHANGED"
        print(f"  - {chk['assumption']}: {state}; impacts {', '.join(chk['breaks_claims'])}")

    print()
    print("  Framing:")
    print("  Results are from COG core plus declared bridge assumptions.")
    print("=" * width)


def main() -> None:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    results = derive_all()
    ledger = build_claim_ledger(results)
    out_path = write_claim_ledger(ledger)

    print_publishable_table(results)

    qn5 = next(r for r in results if r["claim"] == "QN-005")
    qn6 = next(r for r in results if r["claim"] == "QN-006")
    qn7 = next(r for r in results if r["claim"] == "QN-007")

    assert qn5["tr_Y_vanishes"], "FAIL: Tr[Y] != 0"
    assert qn5["tr_Y3_vanishes"], "FAIL: Tr[Y^3] != 0"
    assert Fraction(qn6["sin2_theta_W_exact"]) == Fraction(3, 8), "FAIL: sin^2(theta_W) != 3/8"
    assert qn7["beta0"] == 9, "FAIL: beta0 != 9"

    print(f"\n  Wrote claim ledger: {out_path}")
    print("  All assertions passed.")


if __name__ == "__main__":
    main()

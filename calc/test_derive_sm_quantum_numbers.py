"""Tests for calc/derive_sm_quantum_numbers.py."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from calc.derive_sm_quantum_numbers import (
    N_c,
    N_gen,
    build_claim_ledger,
    derive_all,
    derive_anomaly_cancellation,
    derive_charge_quantization,
    derive_gauge_boson_counts,
    derive_qcd_beta0,
    derive_weinberg_angle,
    frac_sum,
    frac_sum_cubed,
    run_sensitivity_checks,
    sm_hypercharges,
    validate_preconditions,
    write_claim_ledger,
    witt_charge_table,
)


def test_N_c_equals_3() -> None:
    assert N_c == 3


def test_N_gen_equals_N_c() -> None:
    assert N_gen == N_c == 3


def test_validate_preconditions_strict_ok() -> None:
    ctx = validate_preconditions(strict=True)
    assert ctx["N_c"] == 3
    assert ctx["N_gen"] == 3
    assert ctx["N_w"] == 2


def test_validate_preconditions_strict_rejects_noncanonical_nc() -> None:
    with pytest.raises(ValueError, match="requires N_c=3"):
        validate_preconditions(n_c=4, strict=True)


def test_validate_preconditions_non_strict_allows_perturbation() -> None:
    ctx = validate_preconditions(n_c=4, n_gen=4, n_w=3, strict=False)
    assert ctx == {"N_c": 4, "N_gen": 4, "N_w": 3}


def test_witt_table_has_eight_states() -> None:
    assert len(witt_charge_table()) == 8


def test_witt_charge_set() -> None:
    charges = {r["Q"] for r in witt_charge_table()}
    assert charges == {Fraction(0), Fraction(2, 3), Fraction(-1, 3), Fraction(-1)}


def test_witt_charges_integer_multiples_of_1_over_N_c() -> None:
    unit = Fraction(1, N_c)
    for row in witt_charge_table():
        assert (row["Q"] / unit).denominator == 1


def test_charge_quantization_result() -> None:
    out = derive_charge_quantization()
    assert out["claim"] == "QN-001"
    assert out["unit_charge"] == "1/3"
    assert out["derivation_status"] == "core_derived"
    assert out["assumptions"]


def test_su3_gluon_count() -> None:
    out = derive_gauge_boson_counts()
    assert out["SU3_gluons"] == 8
    assert out["derivation_status"] == "bridge_assumed"


def test_su2_weak_boson_count() -> None:
    out = derive_gauge_boson_counts()
    assert out["SU2_weak_bosons"] == 3


def test_u1_count() -> None:
    out = derive_gauge_boson_counts()
    assert out["U1_photon"] == 1


def test_total_gauge_bosons() -> None:
    out = derive_gauge_boson_counts()
    assert out["total"] == 12


def test_sm_hypercharges_count() -> None:
    assert len(sm_hypercharges()) == 15


def test_sm_hypercharge_linear_anomaly() -> None:
    assert frac_sum(sm_hypercharges()) == 0


def test_sm_hypercharge_cubic_anomaly() -> None:
    assert frac_sum_cubed(sm_hypercharges()) == 0


def test_anomaly_dict_flags() -> None:
    out = derive_anomaly_cancellation()
    assert out["tr_Y_vanishes"]
    assert out["tr_Y3_vanishes"]
    assert out["derivation_status"] == "bridge_assumed"


def test_sin2_theta_W_exact() -> None:
    out = derive_weinberg_angle()
    assert Fraction(out["sin2_theta_W_exact"]) == Fraction(3, 8)


def test_sin2_theta_W_normalization_factor() -> None:
    out = derive_weinberg_angle()
    assert Fraction(out["norm_factor_k"]) == Fraction(3, 5)


def test_weinberg_angle_su5_fund_dim() -> None:
    out = derive_weinberg_angle()
    assert out["SU5_fund_dim"] == 5


def test_beta0_uv() -> None:
    out = derive_qcd_beta0()
    assert out["beta0"] == 9
    assert out["derivation_status"] == "bridge_assumed"


def test_beta0_positive_asymptotic_freedom() -> None:
    out = derive_qcd_beta0()
    assert out["beta0"] > 0


def test_beta0_nf6() -> None:
    out = derive_qcd_beta0()
    assert out["beta0_pdg_nf6"] == 7


def test_derive_all_returns_all_claims() -> None:
    out = derive_all()
    ids = [row["claim"] for row in out]
    assert ids == ["QN-001", "QN-002", "QN-003", "QN-004", "QN-005", "QN-006", "QN-007"]


def test_claim_status_split_core_vs_bridge() -> None:
    out = derive_all()
    by_id = {r["claim"]: r for r in out}
    assert by_id["QN-001"]["derivation_status"] == "core_derived"
    assert by_id["QN-002"]["derivation_status"] == "core_derived"
    assert by_id["QN-003"]["derivation_status"] == "bridge_assumed"
    assert by_id["QN-004"]["derivation_status"] == "bridge_assumed"
    assert by_id["QN-005"]["derivation_status"] == "bridge_assumed"
    assert by_id["QN-006"]["derivation_status"] == "bridge_assumed"
    assert by_id["QN-007"]["derivation_status"] == "bridge_assumed"


def test_claims_include_assumptions_and_theorem_refs() -> None:
    out = derive_all()
    for row in out:
        assert isinstance(row["assumptions"], list)
        assert len(row["assumptions"]) >= 1
        assert isinstance(row["theorem_refs"], list)
        assert len(row["theorem_refs"]) >= 1


def test_sensitivity_checks_detect_expected_breakage() -> None:
    checks = run_sensitivity_checks()
    assert len(checks) == 3
    by_assumption = {c["assumption"]: c for c in checks}

    c1 = by_assumption["N_gen = N_c"]
    assert c1["changed"] is True
    assert set(c1["breaks_claims"]) == {"QN-003", "QN-007"}

    c2 = by_assumption["N_w = 2 weak doublet bridge"]
    assert c2["changed"] is True
    assert c2["breaks_claims"] == ["QN-006"]

    c3 = by_assumption["Canonical 15-LH-Weyl hypercharge assignment"]
    assert c3["changed"] is True
    assert c3["breaks_claims"] == ["QN-005"]


def test_claim_ledger_schema_and_fields(tmp_path: Path) -> None:
    results = derive_all()
    ledger = build_claim_ledger(results)
    assert ledger["schema_version"] == "qn_claim_ledger_v1"
    assert ledger["generated_by"] == "calc.derive_sm_quantum_numbers"
    assert isinstance(ledger["generated_at_utc"], str) and ledger["generated_at_utc"]
    assert isinstance(ledger["source_script"], str) and ledger["source_script"]
    assert isinstance(ledger["source_script_sha256"], str) and len(ledger["source_script_sha256"]) == 64
    assert ledger["preconditions"] == {"N_c": 3, "N_gen": 3, "N_w": 2}
    assert ledger["claim_count"] == 7
    for row in ledger["rows"]:
        assert set(row.keys()) == {
            "claim_id",
            "status",
            "assumptions",
            "theorem_refs",
            "tests",
            "confidence",
        }

    out_path = write_claim_ledger(ledger, path=tmp_path / "qn_claim_ledger.json")
    loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "qn_claim_ledger_v1"
    assert loaded["claim_count"] == 7

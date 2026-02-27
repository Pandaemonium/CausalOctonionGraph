from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from calc.derive_sm_quantum_numbers import build_claim_ledger, derive_all
from scripts.validate_qn_claim_ledger import validate


def _write(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def test_validate_qn_claim_ledger_happy_path(tmp_path: Path) -> None:
    ledger = build_claim_ledger(derive_all())
    path = _write(tmp_path / "qn_claim_ledger.json", ledger)
    errors = validate(path, require_lean_backed_statuses={"core_derived"})
    assert errors == []


def test_validate_qn_claim_ledger_rejects_placeholder_for_core(tmp_path: Path) -> None:
    ledger = build_claim_ledger(derive_all())
    mutated = deepcopy(ledger)
    row = next(r for r in mutated["rows"] if r["claim_id"] == "QN-001")
    row["theorem_refs"] = ["not_yet_lean_backed"]
    path = _write(tmp_path / "qn_claim_ledger.json", mutated)
    errors = validate(path, require_lean_backed_statuses={"core_derived"})
    assert any("QN-001" in e and "forbids placeholder" in e for e in errors)


def test_validate_qn_claim_ledger_rejects_missing_top_level_field(tmp_path: Path) -> None:
    ledger = build_claim_ledger(derive_all())
    mutated = deepcopy(ledger)
    mutated.pop("claim_count")
    path = _write(tmp_path / "qn_claim_ledger.json", mutated)
    errors = validate(path, require_lean_backed_statuses={"core_derived"})
    assert any("missing top-level fields" in e for e in errors)


def test_validate_qn_claim_ledger_rejects_missing_test_artifact(tmp_path: Path) -> None:
    ledger = build_claim_ledger(derive_all())
    mutated = deepcopy(ledger)
    row = next(r for r in mutated["rows"] if r["claim_id"] == "QN-004")
    row["tests"] = ["calc/does_not_exist.py::test_missing"]
    path = _write(tmp_path / "qn_claim_ledger.json", mutated)
    errors = validate(path, require_lean_backed_statuses={"core_derived"})
    assert any("test ref path does not exist" in e for e in errors)


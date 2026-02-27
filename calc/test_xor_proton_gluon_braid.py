"""
Tests for calc/xor_proton_gluon_braid.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from calc.xor_proton_gluon_braid import (
    EXCHANGE_CYCLE,
    build_proton_gluon_braid_dataset,
    build_proton_gluon_braid_initial_state,
    select_gluon_operator,
    write_proton_gluon_braid_artifacts,
)


def test_gluon_operator_selection_expected_cycle():
    # Deterministic "smallest valid routing gluon" policy.
    expected = {
        (0, 1): 3,  # zero-index g=2
        (1, 2): 1,  # zero-index g=0
        (2, 0): 2,  # zero-index g=1
    }
    got = {(a, b): select_gluon_operator(a, b) for (a, b) in EXCHANGE_CYCLE}
    assert got == expected


def test_initial_state_has_three_nodes_and_three_cycle_edges():
    s0 = build_proton_gluon_braid_initial_state()
    assert len(s0.nodes) == 3
    assert len(s0.edges) == 3
    ordered = sorted(s0.edges, key=lambda e: e.order)
    assert [(e.src_node_id, e.dst_node_id) for e in ordered] == list(EXCHANGE_CYCLE)
    assert all(e.hand == "left" for e in ordered)
    assert all(e.payload_mode == "src_state" for e in ordered)


def test_braid_detected_with_period_three_default_run():
    ds = build_proton_gluon_braid_dataset(steps=12)
    assert ds["schema_version"] == "xor_proton_gluon_braid_v1"
    assert ds["braid_detected"] is True
    assert ds["dominant_channel_period"] == 3
    assert len(ds["trace"]) == 13


def test_replay_hash_stable():
    a = build_proton_gluon_braid_dataset(steps=18)
    b = build_proton_gluon_braid_dataset(steps=18)
    assert a["dominant_sequence_hash"] == b["dominant_sequence_hash"]
    assert [r["dominant_channels"] for r in a["trace"]] == [r["dominant_channels"] for r in b["trace"]]


def test_write_artifacts(tmp_path: Path):
    ds = build_proton_gluon_braid_dataset(steps=10)
    json_path = tmp_path / "xor_proton_gluon_braid.json"
    csv_path = tmp_path / "xor_proton_gluon_braid.csv"
    write_proton_gluon_braid_artifacts(ds, json_paths=[json_path], csv_paths=[csv_path])

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_proton_gluon_braid_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(ds["trace"])
    assert "dominant_q0" in rows[0]
    assert "dominant_q1" in rows[0]
    assert "dominant_q2" in rows[0]


"""
Tests for calc/xor_scenario_loader.py
"""

from __future__ import annotations

from pathlib import Path

from calc.xor_scenario_loader import (
    build_event_state_from_spec,
    canonical_motif_state_map,
    load_scenario_specs,
    run_loaded_scenario,
)


def test_canonical_motif_state_map_has_required_ids():
    m = canonical_motif_state_map()
    assert "vector_electron_favored" in m
    assert "left_spinor_electron_ideal" in m
    assert "right_spinor_electron_ideal" in m
    assert "vector_proton_proto_t124" in m


def test_load_single_yaml_spec(tmp_path: Path):
    p = tmp_path / "sc.yml"
    p.write_text(
        "\n".join(
            [
                "scenario_id: s1",
                "title: test",
                "steps: 3",
                "nodes:",
                "  - node_id: 0",
                "    motif_id: left_spinor_electron_ideal",
                "  - node_id: 1",
                "    motif_id: right_spinor_electron_ideal",
                "edges:",
                "  - src_node_id: 0",
                "    dst_node_id: 1",
                "    op_idx: 7",
                "    hand: left",
                "  - src_node_id: 1",
                "    dst_node_id: 0",
                "    op_idx: 7",
                "    hand: left",
            ]
        ),
        encoding="utf-8",
    )
    specs = load_scenario_specs(p)
    assert len(specs) == 1
    assert specs[0].scenario_id == "s1"
    assert specs[0].steps == 3


def test_build_event_state_from_spec_and_run(tmp_path: Path):
    p = tmp_path / "sc.yml"
    p.write_text(
        "\n".join(
            [
                "scenario_id: s2",
                "steps: 2",
                "nodes:",
                "  - node_id: 0",
                "    motif_id: vector_electron_favored",
                "edges: []",
            ]
        ),
        encoding="utf-8",
    )
    spec = load_scenario_specs(p)[0]
    state = build_event_state_from_spec(spec)
    assert len(state.nodes) == 1
    trace = run_loaded_scenario(spec)
    assert len(trace) == 3  # steps+1
    assert trace[0].step_index == 0
    assert trace[-1].step_index == 2


def test_custom_base8_state_node(tmp_path: Path):
    p = tmp_path / "sc.yml"
    p.write_text(
        "\n".join(
            [
                "scenario_id: s3",
                "steps: 1",
                "nodes:",
                "  - node_id: 0",
                "    state_base8:",
                "      - ['1', '0']",
                "      - ['0', '0']",
                "      - ['0', '0']",
                "      - ['0', '0']",
                "      - ['0', '0']",
                "      - ['0', '0']",
                "      - ['0', '0']",
                "      - ['0', '0']",
                "edges: []",
            ]
        ),
        encoding="utf-8",
    )
    spec = load_scenario_specs(p)[0]
    state = build_event_state_from_spec(spec)
    assert state.nodes[0].state[0] == (1, 0)


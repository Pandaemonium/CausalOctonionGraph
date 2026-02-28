from __future__ import annotations

import json
from pathlib import Path

import pytest

import minimal_world_kernel_preregistered_unity as k


HERE = Path(__file__).resolve().parent
EXAMPLE = HERE / "lightcone_example_preregistered_unity.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_preregistered_example_loads_and_runs() -> None:
    world = k.load_world(str(EXAMPLE))
    out = k.run(world, 2)
    assert out.tick == 2
    assert set(out.states.keys()) == set(world.node_ids)


def test_invalid_parent_order_rejected(tmp_path: Path) -> None:
    payload = _load_json(EXAMPLE)
    payload["eval_plan"]["parent_order"]["n2"] = ["n0"]  # Missing n1
    bad = tmp_path / "bad_parent_order.json"
    _write_json(bad, payload)
    with pytest.raises(ValueError, match="parent_order\\['n2'\\]"):
        k.load_world(str(bad))


def test_round_order_must_cover_all_nodes(tmp_path: Path) -> None:
    payload = _load_json(EXAMPLE)
    payload["eval_plan"]["round_order"] = ["n0", "n1"]  # Missing n2
    bad = tmp_path / "bad_round_order.json"
    _write_json(bad, payload)
    with pytest.raises(ValueError, match="round_order"):
        k.load_world(str(bad))


def test_replay_is_deterministic() -> None:
    world_a = k.load_world(str(EXAMPLE))
    world_b = k.load_world(str(EXAMPLE))
    out_a = k.run(world_a, 4)
    out_b = k.run(world_b, 4)
    assert out_a.states == out_b.states
    assert out_a.tick == out_b.tick


def test_coefficients_remain_in_unity_set_after_run() -> None:
    allowed = {(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)}
    world = k.load_world(str(EXAMPLE))
    out = k.run(world, 5)
    for nid in out.node_ids:
        for z in out.states[nid]:
            assert (z.re, z.im) in allowed


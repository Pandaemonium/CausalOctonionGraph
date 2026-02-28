from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kernel_projective_unity as k  # noqa: E402


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _base_world_json() -> dict:
    return {
        "node_ids": ["n0", "n1", "n2"],
        "event_order": ["n1", "n0", "n2"],
        "parents": {
            "n0": [],
            "n1": [],
            "n2": ["n0", "n1"],
        },
        "init_state": {
            "n0": [[1, 0], [0, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            "n1": [[1, 0], [0, -1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            "n2": [[1, 0], [0, 0], [1, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
        },
    }


def test_projector_idempotence_scalar_and_state() -> None:
    coeffs = [
        k.GInt(0, 0),
        k.GInt(2, 0),
        k.GInt(-7, 1),
        k.GInt(3, 3),
        k.GInt(1, -9),
    ]
    for z in coeffs:
        once = k.project_g_to_unity(z)
        twice = k.project_g_to_unity(once)
        assert once == twice

    state = (
        k.GInt(5, 0),
        k.GInt(-2, 9),
        k.GInt(0, -4),
        k.GInt(1, 1),
        k.GInt(0, 0),
        k.GInt(-8, -1),
        k.GInt(2, -2),
        k.GInt(0, 3),
    )
    once_state = k.project_cxo_to_unity(state)
    twice_state = k.project_cxo_to_unity(once_state)
    assert once_state == twice_state


def test_strict_input_rejects_nonunity(tmp_path: Path) -> None:
    payload = _base_world_json()
    payload["init_state"]["n2"][0] = [2, 0]
    in_path = tmp_path / "nonunity.json"
    _write_json(in_path, payload)
    with pytest.raises(ValueError, match="not in unity alphabet"):
        k.load_world(str(in_path), enforce_unity_input=True)


def test_allow_nonunity_projects_input_and_runs(tmp_path: Path) -> None:
    payload = _base_world_json()
    payload["init_state"]["n2"][0] = [2, 0]
    in_path = tmp_path / "project_nonunity.json"
    _write_json(in_path, payload)

    world = k.load_world(str(in_path), enforce_unity_input=False)
    assert k.cxo_is_unity(world.states["n2"])

    out = k.run(world, 3)
    assert out.tick == 3
    for nid in out.node_ids:
        assert k.cxo_is_unity(out.states[nid])


def test_event_order_validation(tmp_path: Path) -> None:
    payload = _base_world_json()
    payload["event_order"] = ["n0", "n2"]  # missing n1
    path = tmp_path / "bad_order.json"
    _write_json(path, payload)
    with pytest.raises(ValueError, match="event_order must be a permutation"):
        k.load_world(str(path))


def test_replay_determinism_and_metadata(tmp_path: Path) -> None:
    payload = _base_world_json()
    in_path = tmp_path / "in.json"
    out_a = tmp_path / "out_a.json"
    out_b = tmp_path / "out_b.json"
    _write_json(in_path, payload)

    world_a = k.load_world(str(in_path))
    world_b = k.load_world(str(in_path))
    run_a = k.run(world_a, 4)
    run_b = k.run(world_b, 4)

    assert run_a.tick == run_b.tick
    assert run_a.states == run_b.states

    k.save_world(str(out_a), run_a)
    k.save_world(str(out_b), run_b)
    raw_a = json.loads(out_a.read_text(encoding="utf-8"))
    raw_b = json.loads(out_b.read_text(encoding="utf-8"))

    assert raw_a == raw_b
    assert raw_a["kernel_profile"] == k.KERNEL_PROFILE
    assert raw_a["projector_id"] == k.PROJECTOR_ID
    assert raw_a["basis_labels"] == list(k.BASIS_LABELS)
    assert raw_a["index_channel"] == "xor"
    assert raw_a["sign_table_profile"] == "fano_oriented_triples_xor_v1"
    assert raw_a["event_order"] == ["n1", "n0", "n2"]

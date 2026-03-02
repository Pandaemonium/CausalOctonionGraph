from __future__ import annotations

from cog_v3.calc import build_v3_kernel_selection_matrix_v1 as mod


def test_build_payload_contract() -> None:
    payload = mod.build_payload(batches=1, global_seed=1337, backend="numba_cpu")
    assert payload["schema_version"] == "v3_kernel_selection_matrix_v1"
    assert payload["kernel_profile"]
    assert payload["convention_id"]
    assert payload["event_order_policy"] == "synchronous_parallel_v1"
    assert payload["params"]["batches"] == 1
    assert payload["last_batch"] is not None
    last = payload["last_batch"]
    assert "kernel_selection_matrix" in last
    assert len(last["kernel_selection_matrix"]) >= 1

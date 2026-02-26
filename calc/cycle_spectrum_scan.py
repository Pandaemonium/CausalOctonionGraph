"""
calc/cycle_spectrum_scan.py
RFC-023 section 8.2 / H6: Composite subsystem cycle-spectrum scan

Purpose:
  - Confirm the single-node e7 period-4 baseline.
  - Test H6: composite dynamics can realize periods greater than 4.

This version adds deterministic cross-coupled update rules inspired by RFC-021:
  1) local temporal commit (left multiplication by e7),
  2) causal-local neighbor messages (left/right nearest neighbors),
  3) bounded one-step memory term (finite process-memory proxy),
  4) deterministic projection to a finite phase-basis state space.
"""

from __future__ import annotations

from calc.complex_octonion import ComplexOctonion
from calc.conftest import VACUUM_AXIS
import numpy as np

# e7 is the temporal-commit operator (0-indexed: point 6 -> basis e7).
E7_OP = ComplexOctonion.basis(VACUUM_AXIS)

# Non-collinear interaction operators used for neighbor message coupling.
INTERACTION_OPS = [
    ComplexOctonion.basis(1),  # e1
    ComplexOctonion.basis(2),  # e2
    ComplexOctonion.basis(4),  # e4
]

# Discrete quarter-turn phases used by the projection map.
PHASE_QUARTER_TURNS = (1 + 0j, -1 + 0j, 0 + 1j, 0 - 1j)


def _as_complex_octonion(x) -> ComplexOctonion:
    """Normalize an Octonion/ComplexOctonion-like value to ComplexOctonion."""
    if isinstance(x, ComplexOctonion):
        return x
    return ComplexOctonion(np.asarray(x.c, dtype=complex))


def e7_left(x: ComplexOctonion) -> ComplexOctonion:
    """Left multiplication by e7: temporal commit T(x) = e7 * x."""
    return _as_complex_octonion(E7_OP * x)


def orbit_period(x: ComplexOctonion, op, max_period: int = 64) -> int:
    """Return period of x under op, or -1 when > max_period."""
    current = op(x)
    for n in range(1, max_period + 1):
        if np.allclose(current.c, x.c, atol=1e-9):
            return n
        current = op(current)
    return -1


def _quantize_quarter_turn(c: complex) -> complex:
    """Map any complex number to one of {+1, -1, +i, -i}."""
    if abs(c.real) >= abs(c.imag):
        return 1 + 0j if c.real >= 0 else -1 + 0j
    return 0 + 1j if c.imag >= 0 else 0 - 1j


def project_to_phase_basis(x: ComplexOctonion) -> ComplexOctonion:
    """
    Deterministic projection map:
      - choose dominant basis component by absolute magnitude,
      - quantize its phase to a quarter turn,
      - collapse to that single basis component.

    This keeps the composite system in a finite state space, so cycle spectra
    are well-defined and reproducible.
    """
    coeffs = np.asarray(x.c, dtype=complex)
    mags = np.abs(coeffs)
    idx = int(np.argmax(mags))
    if mags[idx] < 1e-12:
        return ComplexOctonion.basis(0)
    phase = _quantize_quarter_turn(coeffs[idx])
    return _as_complex_octonion(ComplexOctonion.basis(idx) * phase)


def _state_key(x: ComplexOctonion) -> tuple[tuple[int, int], ...]:
    """Stable hashable key for a projected state."""
    coeffs = np.asarray(x.c, dtype=complex)
    return tuple((int(np.rint(z.real)), int(np.rint(z.imag))) for z in coeffs)


def _joint_key(states: list[ComplexOctonion]) -> tuple[tuple[tuple[int, int], ...], ...]:
    return tuple(_state_key(s) for s in states)


def random_phase_basis_state(rng: np.random.Generator) -> ComplexOctonion:
    """Sample a random one-hot basis state with quarter-turn phase."""
    idx = int(rng.integers(0, 8))
    phase = PHASE_QUARTER_TURNS[int(rng.integers(0, 4))]
    return _as_complex_octonion(ComplexOctonion.basis(idx) * phase)


def independent_joint_update(states: list[ComplexOctonion]) -> list[ComplexOctonion]:
    """Independent update: T(x1,...,xk) = (e7*x1,...,e7*xk)."""
    return [project_to_phase_basis(e7_left(s)) for s in states]


def coupled_joint_update(
    states: list[ComplexOctonion],
    prev_states: list[ComplexOctonion] | None = None,
    coupling: float = 1.0,
    memory_weight: float = 0.5,
) -> list[ComplexOctonion]:
    """
    RFC-021-inspired deterministic local interaction update.

    For node i (ring topology):
      local_i  = e7 * state_i
      msg_i    = opL_i * state_{i-1} + opR_i * state_{i+1}
      memory_i = prev_state_i
      next_i   = Proj(local_i + coupling*msg_i + memory_weight*memory_i)

    Inputs are strictly nearest-neighbor plus bounded one-step memory.
    """
    n = len(states)
    if prev_states is None:
        prev_states = states

    out: list[ComplexOctonion] = []
    for i, s in enumerate(states):
        left = states[(i - 1) % n]
        right = states[(i + 1) % n]
        prev = prev_states[i]

        op_l = INTERACTION_OPS[i % len(INTERACTION_OPS)]
        op_r = INTERACTION_OPS[(i + 1) % len(INTERACTION_OPS)]

        local = e7_left(s)
        msg = _as_complex_octonion(op_l * left + op_r * right)
        mem = _as_complex_octonion(prev)

        combined = _as_complex_octonion(local + (coupling * msg) + (memory_weight * mem))
        out.append(project_to_phase_basis(combined))
    return out


def detect_joint_cycle(
    initial_states: list[ComplexOctonion],
    mode: str = "coupled",
    max_steps: int = 512,
    coupling: float = 1.0,
    memory_weight: float = 0.5,
) -> dict:
    """
    Detect attractor-cycle length for a joint system.

    Returns:
      {
        "period": int,
        "transient": int,
        "steps_checked": int
      }
    """
    states = [project_to_phase_basis(s) for s in initial_states]
    prev_states = [project_to_phase_basis(s) for s in initial_states]

    if mode == "independent":
        key = _joint_key(states)
    else:
        key = (_joint_key(states), _joint_key(prev_states))

    seen = {key: 0}

    for step in range(1, max_steps + 1):
        if mode == "independent":
            states = independent_joint_update(states)
            key = _joint_key(states)
        elif mode == "coupled":
            next_states = coupled_joint_update(
                states,
                prev_states=prev_states,
                coupling=coupling,
                memory_weight=memory_weight,
            )
            prev_states, states = states, next_states
            key = (_joint_key(states), _joint_key(prev_states))
        else:
            raise ValueError(f"Unknown mode: {mode}")

        if key in seen:
            return {
                "period": step - seen[key],
                "transient": seen[key],
                "steps_checked": step,
            }
        seen[key] = step

    return {"period": -1, "transient": -1, "steps_checked": max_steps}


def scan_single_node_periods(n_samples: int = 20) -> dict:
    """
    Scan periods for single nodes under e7 left multiplication.
    Expected baseline: period 4 for nonzero states.
    """
    results = {}
    rng = np.random.default_rng(42)

    for basis_idx in range(8):
        x = ComplexOctonion.basis(basis_idx)
        results[f"e{basis_idx}"] = orbit_period(x, e7_left)

    periods = []
    for _ in range(n_samples):
        x = random_phase_basis_state(rng)
        periods.append(orbit_period(x, e7_left))
    results["random_sample_periods"] = sorted(set(periods))
    return results


def scan_composite_joint_period(
    n_nodes: int = 2,
    n_samples: int = 20,
    mode: str = "coupled",
    coupling: float = 1.0,
    memory_weight: float = 0.5,
    max_steps: int = 512,
    seed: int = 99,
) -> dict:
    """
    Scan attractor-cycle periods for n-node systems.

    mode:
      - independent: no cross-coupling (baseline, usually period 4)
      - coupled: local cross-coupled + bounded-memory update (RFC-021 style)
    """
    rng = np.random.default_rng(seed)
    periods: list[int] = []
    witnesses_gt4: list[dict] = []

    for sample_idx in range(n_samples):
        initial_states = [random_phase_basis_state(rng) for _ in range(n_nodes)]
        cycle = detect_joint_cycle(
            initial_states,
            mode=mode,
            max_steps=max_steps,
            coupling=coupling,
            memory_weight=memory_weight,
        )
        periods.append(cycle["period"])
        if cycle["period"] > 4:
            witnesses_gt4.append(
                {
                    "sample": sample_idx,
                    "period": cycle["period"],
                    "transient": cycle["transient"],
                }
            )

    return {
        "mode": mode,
        "n_nodes": n_nodes,
        "n_samples": n_samples,
        "unique_periods": sorted(set(periods)),
        "periods_gt4_count": sum(1 for p in periods if p > 4),
        "witnesses_gt4": witnesses_gt4[:5],  # keep compact
        "coupling": coupling,
        "memory_weight": memory_weight,
    }


def scan_h6_composite_periods(
    node_counts: tuple[int, ...] = (2, 3, 4),
    n_samples: int = 20,
    coupling: float = 1.0,
    memory_weight: float = 0.5,
) -> dict:
    """Run H6 scans across multiple composite sizes."""
    return {
        f"nodes_{n}": scan_composite_joint_period(
            n_nodes=n,
            n_samples=n_samples,
            mode="coupled",
            coupling=coupling,
            memory_weight=memory_weight,
        )
        for n in node_counts
    }


if __name__ == "__main__":
    print("=== Single-node e7 periods (baseline) ===")
    single = scan_single_node_periods()
    for k, v in single.items():
        print(f"  {k}: {v}")

    print("\n=== Composite baseline (independent) ===")
    baseline = scan_composite_joint_period(n_nodes=2, n_samples=20, mode="independent")
    print(f"  unique periods: {baseline['unique_periods']}")
    print(f"  periods > 4:    {baseline['periods_gt4_count']}")

    print("\n=== Composite coupled (RFC-021 style) ===")
    coupled = scan_composite_joint_period(
        n_nodes=2,
        n_samples=20,
        mode="coupled",
        coupling=1.0,
        memory_weight=0.5,
    )
    print(f"  unique periods: {coupled['unique_periods']}")
    print(f"  periods > 4:    {coupled['periods_gt4_count']}")
    if coupled["witnesses_gt4"]:
        print(f"  witness examples (>4): {coupled['witnesses_gt4']}")

    print("\n=== H6 scan across node counts ===")
    h6 = scan_h6_composite_periods(node_counts=(2, 3, 4), n_samples=20)
    for k, v in h6.items():
        print(
            f"  {k}: periods={v['unique_periods']}, "
            f"gt4={v['periods_gt4_count']}/{v['n_samples']}"
        )


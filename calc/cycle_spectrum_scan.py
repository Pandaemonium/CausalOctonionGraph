"""
calc/cycle_spectrum_scan.py
RFC-023 §8.2 / H6: Composite subsystem cycle-spectrum scan

Tests H6 (RFC-023): composite dynamics can realize periods greater than 4.

Single-node baseline: e7 left-mult has period 4 for all nonzero states.
Composite scan: for k-node systems with cross-coupling, measure joint period.

TODO (delegate): implement cross-coupled update rules per RFC-021/022 and
scan for periods > 4 in composite motifs.
"""
from calc.complex_octonion import ComplexOctonion, E0, E1, E2, E3, E4, E5, E6, E7
from calc.conftest import VACUUM_AXIS
import numpy as np

# e7 is the temporal-commit operator (0-indexed: point 6 = e7 in physics)
E7_OP = ComplexOctonion.basis(VACUUM_AXIS)  # = E7


def e7_left(x: ComplexOctonion) -> ComplexOctonion:
    """Left-multiplication by e7: temporal commit T(x) = e7 * x."""
    return E7_OP * x


def orbit_period(x: ComplexOctonion, op, max_period: int = 64) -> int:
    """Return the period of x under repeated application of op, or -1 if > max_period."""
    current = op(x)
    for n in range(1, max_period + 1):
        if np.allclose(current.c, x.c, atol=1e-9):
            return n
        current = op(current)
    return -1


def scan_single_node_periods(n_samples: int = 20) -> dict:
    """
    Scan orbit periods for single nodes under e7 left-mult.
    Expected: all nonzero states have period 4 (proved in Spinors.lean).
    """
    results = {}
    rng = np.random.default_rng(42)

    for basis_idx in range(8):
        x = ComplexOctonion.basis(basis_idx)
        p = orbit_period(x, e7_left)
        results[f"e{basis_idx+1}"] = p

    # Random states
    periods = []
    for _ in range(n_samples):
        coeffs = rng.integers(-3, 4, size=8).astype(complex)
        if np.all(coeffs == 0):
            coeffs[0] = 1
        x = ComplexOctonion(coeffs)
        periods.append(orbit_period(x, e7_left))

    results["random_sample_periods"] = sorted(set(periods))
    return results


def scan_all_basis_operators(basis_indices=(0, 1, 2, 3, 4, 5, 6)) -> dict:
    """
    Scan orbit periods under left-mult by each imaginary basis element.
    Establishes which operators have period 4 vs longer.
    """
    results = {}
    test_states = [ComplexOctonion.basis(i) for i in range(8)]

    for op_idx in basis_indices:
        op_elem = ComplexOctonion.basis(op_idx)

        def make_op(e):
            return lambda x: e * x

        op = make_op(op_elem)
        periods = [orbit_period(s, op) for s in test_states if not np.allclose(s.c, 0)]
        results[f"left_e{op_idx+1}"] = sorted(set(periods))

    return results


def scan_composite_joint_period(n_nodes: int = 2, n_samples: int = 10) -> dict:
    """
    Scan joint orbit period for n_nodes-node systems under simultaneous e7 application.
    Independent nodes: joint period = lcm of individual periods = 4.

    TODO: implement cross-coupled update rules for genuine H6 testing.
    """
    rng = np.random.default_rng(99)
    joint_periods = []

    for _ in range(n_samples):
        states = []
        for _ in range(n_nodes):
            coeffs = rng.integers(-2, 3, size=8).astype(complex)
            if np.all(coeffs == 0):
                coeffs[0] = 1
            states.append(ComplexOctonion(coeffs))

        # Independent joint update: T(x1,...,xk) = (T(x1),...,T(xk))
        def joint_op(ss):
            return [e7_left(s) for s in ss]

        current = joint_op(states)
        for n in range(1, 65):
            if all(np.allclose(current[i].c, states[i].c, atol=1e-9) for i in range(n_nodes)):
                joint_periods.append(n)
                break
        else:
            joint_periods.append(-1)

    return {
        "n_nodes": n_nodes,
        "joint_periods_independent": sorted(set(joint_periods)),
        "note": "TODO: add cross-coupled update rules to test H6 (periods > 4)",
    }


if __name__ == "__main__":
    print("=== Single-node e7 periods (expect all 4) ===")
    single = scan_single_node_periods()
    for k, v in single.items():
        print(f"  {k}: period {v}")

    print("\n=== All-basis operator periods ===")
    basis_scan = scan_all_basis_operators()
    for k, v in basis_scan.items():
        print(f"  {k}: periods {v}")

    print("\n=== 2-node composite joint period (independent) ===")
    comp = scan_composite_joint_period(n_nodes=2)
    print(f"  Joint periods: {comp['joint_periods_independent']}")
    print(f"  Note: {comp['note']}")

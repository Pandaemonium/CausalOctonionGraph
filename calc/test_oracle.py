"""
Tests comparing Python implementation against Lean oracle data.
"""

import pytest
import numpy as np
from calc.conftest import LEAN_DATA
from calc.complex_octonion import witt_operator

def parse_complex_octonion(json_data):
    """
    Parse generic JSON list of [re, im] strings into numpy array of complex.
    Input: [[re0, im0], [re1, im1], ...]
    """
    coeffs = []
    for pair in json_data:
        re_str, im_str = pair
        re = float(re_str)
        im = float(im_str)
        coeffs.append(complex(re, im))
    return np.array(coeffs)

@pytest.mark.skipif(not LEAN_DATA, reason="Lean oracle data not found")
def test_witt_operator_consistency():
    """Verify Python witt_operator(0) matches Lean wittLowerDoubled(0)."""
    # Lean exports "doubled" operators (integer coefficients).
    # Python witt_operator returns 0.5 * (...).
    # So we must multiply Python result by 2 (or compare doubled vs doubled).
    
    # Get Lean data
    witt_json = LEAN_DATA.get("witt", {})
    if "alpha0" not in witt_json:
        pytest.skip("alpha0 not in oracle data")
        
    lean_alpha0_coeffs = parse_complex_octonion(witt_json["alpha0"])
    
    # Get Python data (doubled)
    # witt_operator(0) is alpha0.
    # Python alpha0 = 0.5 * (e6 + i e1).
    # Doubled = e6 + i e1.
    py_alpha0 = witt_operator(0, dag=False)
    py_alpha0_doubled = py_alpha0 * 2
    
    # Compare coefficients
    # Python uses complex128, Lean exported strings of integers.
    # We allow small float tolerance.
    assert np.allclose(py_alpha0_doubled.c, lean_alpha0_coeffs)

@pytest.mark.skipif(not LEAN_DATA, reason="Lean oracle data not found")
def test_witt_operator_dag_consistency():
    """Verify Python witt_operator(0, dag=True) matches Lean wittRaiseDoubled(0)."""
    witt_json = LEAN_DATA.get("witt", {})
    if "alpha0_dag" not in witt_json:
        pytest.skip("alpha0_dag not in oracle data")

    lean_alpha0_dag_coeffs = parse_complex_octonion(witt_json["alpha0_dag"])
    
    # Python alpha0_dag = -0.5 * (e6 - i e1). (My corrected definition)
    # Doubled = -(e6 - i e1) = -e6 + i e1.
    py_alpha0_dag = witt_operator(0, dag=True)
    py_alpha0_dag_doubled = py_alpha0_dag * 2
    
    assert np.allclose(py_alpha0_dag_doubled.c, lean_alpha0_dag_coeffs)

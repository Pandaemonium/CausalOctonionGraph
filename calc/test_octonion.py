"""
Tests for calc/octonion.py
"""

import numpy as np
import pytest
from calc.octonion import Octonion

def test_octonion_init():
    o = Octonion([1, 2, 3, 4, 5, 6, 7, 8])
    assert o.c.shape == (8,)
    assert o.re == 1
    assert np.array_equal(o.im, [2, 3, 4, 5, 6, 7, 8])

def test_add_sub():
    o1 = Octonion(np.arange(8))
    o2 = Octonion(np.ones(8))
    o3 = o1 + o2
    assert np.array_equal(o3.c, np.arange(8) + 1)
    o4 = o1 - o2
    assert np.array_equal(o4.c, np.arange(8) - 1)

def test_mul_scalar():
    o = Octonion(np.ones(8))
    o2 = o * 2
    assert np.array_equal(o2.c, np.ones(8) * 2)
    o3 = 3 * o
    assert np.array_equal(o3.c, np.ones(8) * 3)

def test_mul_basis():
    # e1 * e2 = e3
    e1 = Octonion([0, 1, 0, 0, 0, 0, 0, 0])
    e2 = Octonion([0, 0, 1, 0, 0, 0, 0, 0])
    e3 = Octonion([0, 0, 0, 1, 0, 0, 0, 0])
    
    assert (e1 * e2) == e3
    assert (e2 * e1) == -e3

    # e1 * e1 = -1
    e0 = Octonion([1, 0, 0, 0, 0, 0, 0, 0])
    assert (e1 * e1) == -e0

def test_associativity_fail():
    # (e1 e2) e4 = e3 e4 = e7
    e1 = Octonion([0, 1, 0, 0, 0, 0, 0, 0])
    e2 = Octonion([0, 0, 1, 0, 0, 0, 0, 0])
    e4 = Octonion([0, 0, 0, 0, 1, 0, 0, 0])
    e3 = Octonion([0, 0, 0, 1, 0, 0, 0, 0])
    e7 = Octonion([0, 0, 0, 0, 0, 0, 0, 1])
    
    lhs = (e1 * e2) * e4
    assert lhs == e7
    
    # e1 (e2 e4) = e1 e6 = -e7
    # L4: (2,4,6) -> e2e4 = e6
    # L3: (1,7,6) -> e1e7 = e6 => e1e6 = -e7
    e6 = Octonion([0, 0, 0, 0, 0, 0, 1, 0])
    rhs = e1 * (e2 * e4)
    assert rhs == -e7
    
    assert lhs != rhs

def test_alternativity():
    # x(xy) = (xx)y
    # Test with random integers to avoid float precision issues for now
    x = Octonion(np.random.randint(-5, 5, 8))
    y = Octonion(np.random.randint(-5, 5, 8))
    
    lhs = x * (x * y)
    rhs = (x * x) * y
    assert lhs == rhs

def test_norm_multiplicative():
    # N(xy) = N(x)N(y)
    x = Octonion(np.random.randint(-5, 5, 8))
    y = Octonion(np.random.randint(-5, 5, 8))
    
    nx = x.norm_sq()
    ny = y.norm_sq()
    nxy = (x * y).norm_sq()
    
    assert nxy == nx * ny

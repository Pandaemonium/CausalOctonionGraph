"""
calc/octonion.py
Phase 1.2: Octonion algebra

Mirrors CausalGraphTheory/Octonion.lean.
Implements Octonion arithmetic using numpy arrays and Fano plane structure constants.
"""

import numpy as np
from calc.fano import basis_mul

class Octonion:
    """
    Octonion with coefficients in R (float or int).
    c[0] is real part (e0).
    c[1]..c[7] are imaginary parts (e1..e7).
    """
    def __init__(self, coeffs):
        self.c = np.array(coeffs)
        if self.c.shape != (8,):
            raise ValueError("Octonion must have exactly 8 coefficients")

    @classmethod
    def basis(cls, i):
        """Construct basis element e_i (0..7)."""
        c = np.zeros(8, dtype=int)
        c[i] = 1
        return cls(c)

    def __repr__(self):
        return f"Octonion({self.c})"

    def __eq__(self, other):
        if isinstance(other, Octonion):
            return np.array_equal(self.c, other.c)
        return False

    def __add__(self, other):
        if isinstance(other, Octonion):
            return Octonion(self.c + other.c)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Octonion):
            return Octonion(self.c - other.c)
        return NotImplemented

    def __neg__(self):
        return Octonion(-self.c)

    def __mul__(self, other):
        if isinstance(other, (int, float, complex, np.number)):
            return Octonion(self.c * other)
        
        if not isinstance(other, Octonion):
            return NotImplemented

        # Result accumulator
        res = np.zeros(8, dtype=self.c.dtype)

        # Real part * Real part
        res[0] += self.c[0] * other.c[0]

        # Real * Imaginary
        for k in range(1, 8):
            res[k] += self.c[0] * other.c[k]
            res[k] += self.c[k] * other.c[0]

        # Imaginary * Imaginary
        for i in range(1, 8):
            for j in range(1, 8):
                if i == j:
                    # e_i * e_i = -1
                    res[0] -= self.c[i] * other.c[j]
                else:
                    # e_i * e_j = sign * e_k
                    # basis_mul takes 0-indexed imaginary parts (0..6)
                    # so we pass i-1, j-1
                    k_idx, sign = basis_mul(i - 1, j - 1)
                    # Result is e_{k+1}
                    k = k_idx + 1
                    res[k] += sign * self.c[i] * other.c[j]

        return Octonion(res)

    def __rmul__(self, other):
        if isinstance(other, (int, float, complex, np.number)):
            return Octonion(other * self.c)
        return NotImplemented

    @property
    def re(self):
        return self.c[0]

    @property
    def im(self):
        return self.c[1:]

    def conj(self):
        """Conjugate: a0 - sum(ai ei)"""
        res = -self.c
        res[0] = self.c[0]
        return Octonion(res)

    def norm_sq(self):
        """Norm squared: sum(ci^2)"""
        return np.sum(self.c ** 2)

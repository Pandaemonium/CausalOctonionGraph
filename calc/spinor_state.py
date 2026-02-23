"""
calc/spinor_state.py
Phase B1-B2: Muon (gen-2) state vector construction in C⊗O.

Mirrors CausalGraphTheory/Spinors.lean.

Convention:
  s  = (1/2)(e₀ + i·e₇)   left projector  (gen1 sector = s·_·S*)
  s* = (1/2)(e₀ - i·e₇)   left conjugate  (gen2/3 sector = s*·_·S*)
  S* = (1/2)(e₀ - i·e₇)   right conjugate (same formula, applied from the RIGHT)

We work at 4× scale to stay in integer arithmetic (mirrors the Lean proofs):
  leftVacConjDoubled  = 2s* = e₀ - i·e₇
  rightVacConjDoubled = 2S* = e₀ - i·e₇   (same formula)

Furey (2019) arXiv:1910.08395, Eq. 21 — second charged lepton (muon):
  ψ_μ = s*·S* · (−i·e₂ + e₆ + e₁₂₃ − i·e₁₃₆) · s*·S*

Triple products (Furey convention, rfc/CONVENTIONS.md §2):
  e₁₂₃ = (e₁·e₂)·e₃ = e₃·e₃ = −e₀
  e₁₃₆ = (e₁·e₃)·e₆ = (−e₂)·e₆ = −(e₂·e₆) = −(−e₄) = +e₄

So the inner expression is:
  inner_μ = −i·e₂ + e₆ + (−e₀) − i·(+e₄)
           = −e₀ − i·e₂ − i·e₄ + e₆

At 4× scale:
  4·ψ_μ = (2s*) · (inner_μ · (2S*))
"""

import numpy as np
from calc.complex_octonion import ComplexOctonion, E0, E1, E2, E3, E4, E5, E6, E7

# ================================================================
# Projector elements (at 2× scale to stay integer)
# ================================================================

# 2s* = e₀ − i·e₇
leftVacConjDoubled: ComplexOctonion = ComplexOctonion(
    np.array([1, 0, 0, 0, 0, 0, 0, -1j], dtype=complex)
)

# 2S* = e₀ − i·e₇  (same formula, applied from the RIGHT)
rightVacConjDoubled: ComplexOctonion = leftVacConjDoubled


# ================================================================
# Muon inner expression
# inner_μ = −e₀ − i·e₂ − i·e₄ + e₆
# ================================================================

muonInner: ComplexOctonion = ComplexOctonion(
    np.array([-1, 0, -1j, 0, -1j, 0, 1, 0], dtype=complex)
)


# ================================================================
# Gen-2 (muon) state at 4× scale
# 4·ψ_μ = (2s*) · (inner_μ · (2S*))
# ================================================================

def compute_gen2_state() -> ComplexOctonion:
    """
    Compute gen2StateQuadruple = leftVacConjDoubled * (muonInner * rightVacConjDoubled).

    This mirrors the Lean definition:
        def gen2StateQuadruple : ComplexOctonion ℤ :=
          leftVacConjDoubled * (muonInner * rightVacConjDoubled)
    """
    inner_right = muonInner * rightVacConjDoubled
    return leftVacConjDoubled * inner_right


gen2StateQuadruple: ComplexOctonion = compute_gen2_state()


# ================================================================
# Proportional idempotency check
# If ψ_μ = (1/4)·gen2, then ψ_μ is idempotent iff gen2² = 4·gen2.
# Compute the actual scalar c such that gen2² = c·gen2.
# ================================================================

def check_proportional_idempotency() -> tuple[bool, complex | None]:
    """
    Check whether gen2StateQuadruple² = c·gen2StateQuadruple for some scalar c.

    Returns (is_proportional, c) where c is the proportionality constant,
    or (False, None) if not proportional.

    The Lean theorem `gen2State_proportional_idempotent` claims c = 4.
    This function determines the actual value of c.
    """
    sq = gen2StateQuadruple * gen2StateQuadruple
    gen2 = gen2StateQuadruple

    # Find first non-zero component of gen2 to compute ratio
    c_ratio = None
    for k in range(8):
        if abs(gen2.c[k]) > 1e-10:
            if abs(sq.c[k]) < 1e-10:
                # gen2[k] != 0 but sq[k] = 0 → can't be proportional with any c
                return False, None
            ratio = sq.c[k] / gen2.c[k]
            if c_ratio is None:
                c_ratio = ratio
            elif abs(ratio - c_ratio) > 1e-10:
                return False, None

    if c_ratio is None:
        # gen2 is zero → trivially proportional (c undefined)
        return True, None

    # Verify all components satisfy sq = c_ratio * gen2
    expected = ComplexOctonion(c_ratio * gen2.c)
    if np.allclose(sq.c, expected.c):
        return True, c_ratio
    return False, None


# ================================================================
# Fano triple product helpers (for verification)
# ================================================================

def fano_triple(a: int, b: int, c_idx: int) -> ComplexOctonion:
    """
    Compute (eₐ · e_b) · e_c using real octonion basis elements.
    Indices are 0..7 (Lean/physics convention: 0=e₀, 1=e₁, ..., 7=e₇).
    """
    from calc.complex_octonion import BASIS
    ea = ComplexOctonion(BASIS[a].c.astype(complex))
    eb = ComplexOctonion(BASIS[b].c.astype(complex))
    ec = ComplexOctonion(BASIS[c_idx].c.astype(complex))
    return (ea * eb) * ec


# ================================================================
# Main: print computed values
# ================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Spinor state: gen-2 (muon) at 4x scale")
    print("=" * 60)

    print("\nTriple product check (Furey convention):")
    e123 = fano_triple(1, 2, 3)  # (e1*e2)*e3
    e136 = fano_triple(1, 3, 6)  # (e1*e3)*e6
    print(f"  e1*e2*e3 = {e123.c}  (expect -e0 = [-1,0,...,0])")
    print(f"  e1*e3*e6 = {e136.c}  (expect +e4 = [0,0,0,0,1,0,0,0])")

    print("\nmuonInner components:")
    for k in range(8):
        v = muonInner.c[k]
        if abs(v) > 1e-10:
            print(f"  c[{k}] = {v}")

    print("\ngen2StateQuadruple (= 4*psi_mu) components:")
    for k in range(8):
        v = gen2StateQuadruple.c[k]
        if abs(v) > 1e-10:
            print(f"  c[{k}] = {v}")

    sq = gen2StateQuadruple * gen2StateQuadruple
    print("\ngen2StateQuadruple^2 components:")
    for k in range(8):
        v = sq.c[k]
        if abs(v) > 1e-10:
            print(f"  c[{k}] = {v}")

    is_prop, c_val = check_proportional_idempotency()
    print(f"\ngen2^2 = c*gen2?  {is_prop},  c = {c_val}")
    if is_prop and c_val is not None:
        if abs(c_val - 4) < 1e-10:
            print("  -> Lean theorem as written is CORRECT (c = +4)")
        elif abs(c_val + 4) < 1e-10:
            print("  -> Lean theorem needs sign correction: RHS should use -4, not +4")
        else:
            print(f"  -> Unexpected proportionality constant: {c_val}")

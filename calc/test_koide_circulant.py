"""
calc/test_koide_circulant.py

Tests for the circulant matrix derivation of the Koide formula.

Background (from claims/koide_exactness.yml Notes):
    The Brannen parametrization sqrt(m_n) = A + B*cos(theta + 2*pi*n/3)
    is exactly the eigenvalue formula for a 3x3 circulant Hermitian matrix
    C in J_3(C).  The three generation masses are eigenvalues of such a
    matrix.  The B/A = sqrt(2) constraint is the condition that the matrix
    norm in the off-democratic sector equals the democratic sector norm.

    The circulant matrix with first row [c0, c1, c2] (c2 = conj(c1)) has
    eigenvalues:
        lambda_k = A + B*cos(theta + 2*pi*k/3)  for k = 0, 1, 2
    where A = c0 (real), B/2 = |c1|, theta = -arg(c1).

    The Koide ratio Q = 2/3 requires B/A = sqrt(2), i.e. b = a/sqrt(2)
    for the real-symmetric case.

References:
    - claims/koide_exactness.yml (Notes section)
    - calc/koide.py (PDG mass values and core Koide functions)
    - Brannen (2006): Discrete Fourier Transform and the Koide Formula
"""

import math
import cmath
import numpy as np
import pytest

# ---------------------------------------------------------------------------
# PDG 2023 charged lepton masses (MeV/c^2)
# ---------------------------------------------------------------------------
M_ELECTRON = 0.51099895000
M_MUON = 105.6583755
M_TAU = 1776.86

LEPTON_MASSES = (M_ELECTRON, M_MUON, M_TAU)


# ---------------------------------------------------------------------------
# Circulant matrix construction
# ---------------------------------------------------------------------------

def build_real_circulant_3x3(a, b):
    """
    Build a 3x3 real symmetric circulant matrix:
        C = [[a, b, b],
             [b, a, b],
             [b, b, a]]

    Analytic eigenvalues: a+2b (once), a-b (twice).
    """
    return np.array([[a, b, b],
                     [b, a, b],
                     [b, b, a]], dtype=float)


def build_brannen_circulant_3x3(A, B, theta=0.0):
    """
    Build a 3x3 Hermitian circulant whose eigenvalues are:
        lambda_k = A + B*cos(theta + 2*pi*k/3)  for k = 0, 1, 2.

    First row: [A, (B/2)*exp(-i*theta), (B/2)*exp(+i*theta)]
    C[i,j] = first_row[(j - i) % 3]
    """
    c0 = complex(A, 0.0)
    c1 = (B / 2.0) * cmath.exp(-1j * theta)
    c2 = (B / 2.0) * cmath.exp(+1j * theta)
    coeffs = [c0, c1, c2]
    C = np.zeros((3, 3), dtype=complex)
    for i in range(3):
        for j in range(3):
            C[i, j] = coeffs[(j - i) % 3]
    return C


def circulant_eigenvalues_analytic(A, B, theta=0.0):
    """Analytic eigenvalues: lambda_k = A + B*cos(theta + 2*pi*k/3)."""
    return [A + B * math.cos(theta + 2 * math.pi * k / 3) for k in range(3)]


def koide_ratio_from_sqrt_masses(sqrt_masses):
    """Q = sum(f_k^2) / (sum(f_k))^2 where f_k = sqrt(m_k)."""
    f = list(sqrt_masses)
    return sum(x ** 2 for x in f) / (sum(f) ** 2)


def fit_brannen_params_from_lepton_masses(masses=LEPTON_MASSES):
    """
    Fit Brannen parameters A, B, theta to the observed lepton sqrt-masses.

    The Brannen eigenvalue vector for (k=0,1,2) is:
        lambda_k = A + B*cos(theta + 2*pi*k/3)

    The cosine vector c(theta) = (cos(theta), cos(theta+2pi/3), cos(theta+4pi/3))
    lies in the plane perpendicular to (1,1,1) and has norm sqrt(3/2).

    So delta = f - A*(1,1,1) = B * c(theta), giving:
        B = ||delta|| / ||c(theta)|| = ||delta|| * sqrt(2/3)
        theta = atan2(-dot(delta, u2)/|c(theta)|, dot(delta, u1)/|c(theta)|)

    where u1, u2 are an ONB of the perp plane and c(0) expressed in that basis
    has components (sqrt(1/2), sqrt(1/6)*... ) — worked out via direct projection.

    Direct approach: project delta onto the unit cosine vector at theta=0,
    then extract amplitude and phase.

    Parameters: the sqrt-masses are matched to k=0,1,2 in the ORDER they appear
    after sorting (ascending), which corresponds to theta chosen so that
    lambda_0 < lambda_1 < lambda_2.
    """
    # Sort sqrt-masses ascending: f[0]=sqrt(m_e), f[1]=sqrt(m_mu), f[2]=sqrt(m_tau)
    sqrt_masses = sorted(math.sqrt(m) for m in masses)
    f = np.array(sqrt_masses, dtype=float)
    A = float(f.mean())
    delta = f - A  # lies in perp plane to (1,1,1)

    # The Brannen cosine basis vectors in R^3 (for theta=0 and theta=pi/2):
    # c_cos = (cos(0), cos(2pi/3), cos(4pi/3)) = (1, -1/2, -1/2)  -- norm sqrt(3/2)
    # c_sin = (sin(0), sin(2pi/3), sin(4pi/3)) = (0, sqrt(3)/2, -sqrt(3)/2) -- norm sqrt(3/2)
    # Normalize them to unit vectors:
    c_cos = np.array([1.0, -0.5, -0.5])           # norm = sqrt(3/2)
    c_sin = np.array([0.0, math.sqrt(3)/2, -math.sqrt(3)/2])  # norm = sqrt(3/2)
    norm_c = math.sqrt(1.5)  # = sqrt(3/2)

    # Project delta onto these (unnormalized) basis vectors
    p_cos = float(np.dot(delta, c_cos)) / (norm_c ** 2)  # coefficient of c_cos
    p_sin = float(np.dot(delta, c_sin)) / (norm_c ** 2)  # coefficient of c_sin

    # delta = B*(cos(theta)*c_cos + sin(theta)*(-c_sin))... wait, let's be careful.
    # lambda_k = A + B*cos(theta + 2pi*k/3)
    #          = A + B*cos(theta)*cos(2pi*k/3) - B*sin(theta)*sin(2pi*k/3)
    # So delta_k = B*cos(theta)*cos(2pi*k/3) - B*sin(theta)*sin(2pi*k/3)
    # delta = B*cos(theta)*c_cos - B*sin(theta)*c_sin
    # Therefore:
    #   dot(delta, c_cos) = B*cos(theta)*||c_cos||^2 - B*sin(theta)*dot(c_sin,c_cos)
    # Note: dot(c_cos, c_sin) = 0 (orthogonal), so:
    #   dot(delta, c_cos) = B*cos(theta) * (3/2)  =>  B*cos(theta) = dot(delta,c_cos)/(3/2)
    #   dot(delta, c_sin) = -B*sin(theta) * (3/2) =>  B*sin(theta) = -dot(delta,c_sin)/(3/2)

    B_cos_theta = float(np.dot(delta, c_cos)) / 1.5
    B_sin_theta = -float(np.dot(delta, c_sin)) / 1.5

    B = math.sqrt(B_cos_theta ** 2 + B_sin_theta ** 2)
    theta = math.atan2(B_sin_theta, B_cos_theta)
    return A, B, theta


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_real_symmetric_circulant_eigenvalues():
    """Eigenvalues of [[a,b,b],[b,a,b],[b,b,a]] are a+2b (x1) and a-b (x2)."""
    a, b = 5.0, 2.0
    C = build_real_circulant_3x3(a, b)
    eigs = sorted(np.linalg.eigvalsh(C).tolist())
    expected = sorted([a + 2 * b, a - b, a - b])
    for num, ana in zip(eigs, expected):
        assert abs(num - ana) < 1e-10, f"Eigenvalue mismatch: {num} vs {ana}"


def test_circulant_eigenvalues_match_analytic():
    """Numeric eigenvalues of build_brannen_circulant_3x3 match analytic formula."""
    A = 2.0
    B = math.sqrt(2) * A
    theta = 0.3
    C = build_brannen_circulant_3x3(A, B, theta)
    numeric_eigs = sorted(np.linalg.eigvalsh(C).tolist())
    analytic_eigs = sorted(circulant_eigenvalues_analytic(A, B, theta))
    for num, ana in zip(numeric_eigs, analytic_eigs):
        assert abs(num - ana) < 1e-10, f"Eigenvalue mismatch: numeric={num}, analytic={ana}"


def test_koide_condition_B_equals_A_sqrt2():
    """When B/A = sqrt(2), Q = 2/3 exactly (for various theta)."""
    A = 3.0
    B = A * math.sqrt(2)
    for theta in [0.0, 0.1, 0.5, math.pi / 4, math.pi / 3]:
        sqrt_masses = circulant_eigenvalues_analytic(A, B, theta)
        if all(f > 0 for f in sqrt_masses):
            Q = koide_ratio_from_sqrt_masses(sqrt_masses)
            assert abs(Q - 2.0 / 3.0) < 1e-12, (
                f"Q={Q} != 2/3 for B/A=sqrt(2), theta={theta}"
            )


def test_koide_formula_Q_from_brannen_ratio():
    """Q = 1/3 + B^2/(6*A^2) from the Brannen parametrization."""
    A = 3.0
    theta = 0.2
    for ratio in [0.5, 0.8, 1.0, math.sqrt(2), 1.5, 2.0]:
        B = A * ratio
        sqrt_masses = circulant_eigenvalues_analytic(A, B, theta)
        if all(f > 0 for f in sqrt_masses):
            Q = koide_ratio_from_sqrt_masses(sqrt_masses)
            expected_Q = 1.0 / 3.0 + ratio ** 2 / 6.0
            assert abs(Q - expected_Q) < 1e-12, (
                f"Q={Q} does not match 1/3+B^2/(6A^2)={expected_Q} for B/A={ratio}"
            )


def test_brannen_params_from_lepton_masses():
    """Fit Brannen params to PDG masses; recovered sqrt-masses match originals."""
    A, B, theta = fit_brannen_params_from_lepton_masses(LEPTON_MASSES)
    assert A > 0, f"A={A} should be positive"
    assert B > 0, f"B={B} should be positive"
    recovered = sorted(circulant_eigenvalues_analytic(A, B, theta))
    original = sorted(math.sqrt(m) for m in LEPTON_MASSES)
    for rec, orig in zip(recovered, original):
        assert abs(rec - orig) < 1e-6, (
            f"Recovered sqrt-mass {rec:.8f} does not match original {orig:.8f}"
        )


def test_lepton_b_over_a_ratio():
    """B/A from PDG masses is close to sqrt(2), consistent with Q ~ 2/3."""
    A, B, theta = fit_brannen_params_from_lepton_masses(LEPTON_MASSES)
    ratio = B / A
    Q_pdg = sum(LEPTON_MASSES) / (sum(math.sqrt(m) for m in LEPTON_MASSES)) ** 2
    Q_brannen = 1.0 / 3.0 + ratio ** 2 / 6.0
    assert abs(Q_pdg - Q_brannen) < 1e-6, (
        f"Q_pdg={Q_pdg} != Q_brannen={Q_brannen}"
    )
    assert abs(Q_pdg - 2.0 / 3.0) < 2e-4, (
        f"PDG Koide ratio Q={Q_pdg:.8f} deviates from 2/3 by more than 2e-4"
    )
    assert abs(ratio - math.sqrt(2)) < 0.01, (
        f"B/A={ratio:.8f} is not close to sqrt(2)={math.sqrt(2):.8f}"
    )


def test_circulant_koide_match():
    """
    Main test: construct 3x3 Hermitian circulant from Brannen params fitted
    to PDG lepton masses, compute eigenvalues, and verify:
      (a) eigenvalues reproduce lepton mass ratios within 1e-4 relative error,
      (b) Koide ratio Q is within 1e-3 of 2/3.

    See claims/koide_exactness.yml (Notes: CIRCULANT MATRIX ORIGIN section).
    """
    # Step 1: fit Brannen parameters to PDG lepton masses
    A, B, theta = fit_brannen_params_from_lepton_masses(LEPTON_MASSES)

    # Step 2: construct 3x3 Hermitian circulant
    C = build_brannen_circulant_3x3(A, B, theta)
    assert np.allclose(C, C.conj().T, atol=1e-12), "Matrix is not Hermitian"

    # Step 3: compute eigenvalues numerically
    eigs_numeric = np.linalg.eigvalsh(C)  # sorted ascending
    sqrt_masses_numeric = sorted(eigs_numeric.tolist())
    assert all(f > 0 for f in sqrt_masses_numeric), (
        f"Non-positive eigenvalues: {sqrt_masses_numeric}"
    )

    # Step 4: check mass ratios vs PDG
    masses_numeric = [f ** 2 for f in sqrt_masses_numeric]
    masses_pdg = sorted(LEPTON_MASSES)
    ratios_numeric = [m / masses_numeric[0] for m in masses_numeric]
    ratios_pdg = [m / masses_pdg[0] for m in masses_pdg]
    for rn, rp in zip(ratios_numeric, ratios_pdg):
        rel_err = abs(rn - rp) / max(abs(rp), 1.0)
        assert rel_err < 1e-4, (
            f"Mass ratio mismatch: circulant={rn:.6f}, PDG={rp:.6f}, rel_err={rel_err:.2e}"
        )

    # Step 5: Koide ratio from numeric eigenvalues
    Q_numeric = koide_ratio_from_sqrt_masses(sqrt_masses_numeric)
    Q_pdg = sum(LEPTON_MASSES) / (sum(math.sqrt(m) for m in LEPTON_MASSES)) ** 2
    assert abs(Q_numeric - Q_pdg) < 1e-8, (
        f"Q from circulant ({Q_numeric:.10f}) differs from PDG ({Q_pdg:.10f})"
    )
    assert abs(Q_numeric - 2.0 / 3.0) < 1e-3, (
        f"Koide ratio Q={Q_numeric:.8f} not within 1e-3 of 2/3"
    )
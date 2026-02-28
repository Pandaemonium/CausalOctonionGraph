"""
microstate_experiments.py
Five minimal COG simulation systems where SM constants emerge as measurable outputs.
Each experiment fits in < 20 lines of active code.

Convention: FANO_CYCLES is 0-indexed (0=e1..6=e7); 8-vectors have a[0]=scalar, a[1..7]=imaginary.
Run: python calc/microstate_experiments.py
"""

import numpy as np
from calc.conftest import FANO_CYCLES, FANO_SIGN, FANO_THIRD, WITT_PAIRS, VACUUM_AXIS


# ─── shared: octonionic multiplication ──────────────────────────────────────
# FANO_SIGN has all 42 ordered pairs (7 triples × 6 cyclic/anti-cyclic).
# Must iterate FANO_SIGN.items() — NOT just the 7 FANO_CYCLES — to get all products.

def octo_mul(a, b):
    r = np.zeros(8)
    r[0] = a[0]*b[0] - np.dot(a[1:], b[1:])
    r[1:] = a[0]*b[1:] + b[0]*a[1:]
    for (i, j), s in FANO_SIGN.items():
        k = FANO_THIRD[(i, j)]
        r[k+1] += s * a[i+1] * b[j+1]
    return r


def basis(idx):
    """8-vector for basis element: idx=0 -> scalar 1; idx=1..7 -> e1..e7."""
    v = np.zeros(8); v[idx] = 1.0; return v


# ── Experiment 1: Witt-pair vacuum couplings → lepton mass matrix ────────────
#
# Physical picture: each lepton generation = one Witt pair.  The lepton mass
# comes from how strongly the Witt pair couples to the vacuum axis e7 via
# the Fano product.  Coupling_i = fano product of Witt pair i through e7.
# Mass matrix M_ij = coupling_i × coupling_j.
# Eigenvalues of M = m_e, m_mu, m_tau (up to an overall scale).

def experiment_lepton_mass_matrix():
    vac = VACUUM_AXIS  # 0-indexed imaginary unit index (= 6 for e7)
    vac_vec = basis(vac + 1)  # +1 because a[0] = scalar

    # For each Witt pair (p, q), compute the coupling to the vacuum axis:
    #   e_p × e_vac = ±e_q  (if (p, vac, q) is a Fano triple, returns sign)
    #   coupling_i = fano sign of (pair_left × vacuum → pair_right)
    couplings = []
    for (p, q) in WITT_PAIRS:
        # e_p × e_vac = c × e_q ?  Check all Fano triples.
        c = 0.0
        for (i, j, k) in FANO_CYCLES:
            s = FANO_SIGN[(i, j)]
            if i == p and j == vac and k == q:
                c = s; break
            if i == p and j == vac and k != q:
                pass  # different result
            # also check reversed directions via sign flip
            if j == p and i == vac and k == q:
                c = -s; break
        # If no direct triple found, compute via octo_mul
        if c == 0.0:
            ep = basis(p + 1)
            ev = basis(vac + 1)
            prod = octo_mul(ep, ev)
            eq = basis(q + 1)
            c = float(np.dot(prod, eq))
        couplings.append(c)

    # Outer-product mass matrix: M_ij = c_i * c_j + delta_ij * epsilon
    # (pure outer product is rank-1; add small epsilon for full spectrum)
    c = np.array(couplings)
    M = np.outer(c, c)

    # Off-diagonal Witt-pair cross-coupling: e_p1 × e_p2 via Fano
    # M_ij += coupling of Witt pair i to Witt pair j (inter-generation mixing)
    for a_idx, (pa, qa) in enumerate(WITT_PAIRS):
        for b_idx, (pb, qb) in enumerate(WITT_PAIRS):
            if a_idx == b_idx: continue
            # compute e_pa × e_pb
            epa = basis(pa + 1); epb = basis(pb + 1)
            cross = octo_mul(epa, epb)
            # project onto vacuum direction
            M[a_idx, b_idx] += float(cross[vac + 1])

    evals = np.sort(np.abs(np.linalg.eigvalsh(M)))
    sqrt_evals = np.sqrt(evals)
    print("\n=== Experiment 1: Lepton mass matrix from Witt-pair vacuum couplings ===")
    print(f"  Couplings to vacuum axis (e{vac+1}): {couplings}")
    print(f"  Mass matrix eigenvalues:    {evals.tolist()}")
    print(f"  sqrt(eigenvalue) ratios:    ", end="")
    if sqrt_evals[0] > 1e-8:
        print([round(v/sqrt_evals[0], 4) for v in sqrt_evals])
    else:
        print([round(v, 6) for v in sqrt_evals], " (one zero mode)")
    print(f"  Koide target ratios:        1 : 14.42 : 82.82")
    print(f"  S3 symmetry broken?         {len(set(round(e,4) for e in evals)) > 1}")


# ── Experiment 2: Higgs sector triality parity split ─────────────────────────
#
# Physical picture: in triality (V, S+, S-), each of the 7 Fano triples belongs
# to one sector.  The Higgs = V sector (even parity).  The ratio w(V)/7 ≈ m_H/m_top.

def experiment_higgs_parity():
    wV = wSp = wSm = 0
    for (i, j, k) in FANO_CYCLES:
        si = FANO_SIGN[(i, j)]
        sj = FANO_SIGN[(j, k)]
        if si == sj:     wV  += 1   # even parity → Higgs (V) sector
        elif si == +1:   wSp += 1   # S+ sector
        else:            wSm += 1   # S- sector

    ratio = wV / 7
    print("\n=== Experiment 2: Higgs sector parity split ===")
    print(f"  Fano triples per sector: V={wV}, S+={wSp}, S-={wSm}  (total=7)")
    print(f"  m_H / m_top  =  w(V) / 7  =  {wV}/7  =  {ratio:.4f}")
    print(f"  Experimental:                          0.7240")
    print(f"  Deviation:                             {abs(ratio-0.724)/0.724*100:.2f}%")


# ── Experiment 3: CP-odd phase of quark mixing matrix ────────────────────────
#
# Physical picture: the CKM matrix = mis-alignment between up-type and down-type
# Yukawa matrices built from Fano signs.  If Fano signs are real (±1), det(CKM)
# is real → delta_CP = 0 or pi at tree level.  Deviation from 0 = radiative CP.

def experiment_cp_phase():
    # Build 6×6 quark Yukawa matrix (e1..e6, not e7 = vacuum axis)
    M_q = np.zeros((6, 6))
    for (i, j, k) in FANO_CYCLES:
        s = FANO_SIGN[(i, j)]
        for (a, b, c) in [(i,j,k),(j,k,i),(k,i,j)]:
            if a <= 5 and b <= 5:       # only quark nodes (not e7)
                M_q[a, b] = s

    # Split into up-quark and down-quark sectors
    M_up   = M_q[:3, :3]   # e1, e2, e3
    M_down = M_q[3:, 3:]   # e4, e5, e6

    _, U_up   = np.linalg.eigh(M_up   @ M_up.T)
    _, U_down = np.linalg.eigh(M_down @ M_down.T)
    CKM = U_up.T @ U_down
    delta_CP = float(np.angle(np.linalg.det(CKM)))

    print("\n=== Experiment 3: Tree-level CKM CP phase ===")
    print(f"  Quark Yukawa (up-sector):  \n{np.round(M_up,1)}")
    print(f"  Quark Yukawa (down-sector):\n{np.round(M_down,1)}")
    print(f"  det(CKM) phase:            {delta_CP:.6f} rad")
    print(f"  Experimental delta_CP:     1.3600 rad")
    print(f"  Tree-level prediction:     0 (Fano signs are real → no complex phase)")
    print(f"  Needed correction:         C⊗O complex extension (non-zero associator)")


# ── Experiment 4: Witt-pair orbit periods → lepton mass ladder ───────────────
#
# Physical picture: under repeated application of the Fano cyclic operator T
# (apply each of the 7 generators in sequence), a state traces an orbit.
# The electron is confined to its Witt pair (period = 3).
# A "muon-like" state uses all 3 Witt pairs (period = ?).
# The ratio of orbit periods ≈ mass ratio.

def experiment_lepton_orbit():
    def apply_fano_cycle(state):
        """Apply all 7 Fano generators in order: state -> e1*state -> e2*(e1*state) -> ..."""
        for i in range(7):
            ei = basis(i + 1)
            state = octo_mul(ei, state)
        return state

    def orbit_period(start, max_steps=500):
        """Count ticks until return to ±start (up to sign)."""
        state = start.copy()
        for t in range(1, max_steps + 1):
            state = apply_fano_cycle(state)
            norm = np.dot(state, start)
            if abs(abs(norm) - 1.0) < 1e-6 and np.linalg.norm(state - start * norm) < 1e-6:
                return t
        return None  # did not return

    # Electron state: e6 (one Witt-pair component)
    e_electron = basis(WITT_PAIRS[0][0] + 1)   # e6 (0-indexed 5 → array idx 6)
    # Muon state: e6 + e2 (two Witt-pair components combined)
    e_muon = (basis(WITT_PAIRS[0][0] + 1) + basis(WITT_PAIRS[1][0] + 1))
    e_muon /= np.linalg.norm(e_muon)
    # Tau state: all three Witt-pair components
    e_tau = sum(basis(p + 1) for p, q in WITT_PAIRS)
    e_tau /= np.linalg.norm(e_tau)

    T_e   = orbit_period(e_electron)
    T_mu  = orbit_period(e_muon)
    T_tau = orbit_period(e_tau)

    print("\n=== Experiment 4: Lepton orbit periods under Fano cycle operator ===")
    print(f"  Electron (e6 only):           period = {T_e}")
    print(f"  Muon-like (e6+e2 combined):   period = {T_mu}")
    print(f"  Tau-like  (e6+e2+e3 sum):     period = {T_tau}")
    if T_e and T_mu:
        print(f"  Period ratio T_mu/T_e  =  {T_mu}/{T_e}  =  {T_mu/T_e:.2f}")
        print(f"  Experimental m_mu/m_e  =  206.77")
    if T_e and T_tau:
        print(f"  Period ratio T_tau/T_e =  {T_tau}/{T_e}  =  {T_tau/T_e:.2f}")
        print(f"  Experimental m_tau/m_e =  3477.15")


# ── Experiment 5: Associator cost per basis state → top quark outlier ────────
#
# Physical picture: mass = associator drag.  Count |A(ek, ei, ej)|^2 summed over
# all (i,j) pairs for each basis direction ek.  The maximum-cost direction is
# the heaviest fermion.

def experiment_associator_costs():
    def assoc_cost(k):
        """Total A(ek, ei, ej)^2 summed over imaginary (i,j) pairs."""
        ek = basis(k + 1)
        total = 0.0
        for i in range(7):
            for j in range(7):
                if i == j: continue
                ei = basis(i + 1); ej = basis(j + 1)
                A = octo_mul(octo_mul(ek, ei), ej) - octo_mul(ek, octo_mul(ei, ej))
                total += float(np.dot(A, A))
        return total

    costs = {k: round(assoc_cost(k), 4) for k in range(7)}
    min_c = min(costs.values())
    max_c = max(costs.values())
    ranked = sorted(costs.items(), key=lambda x: x[1])

    print("\n=== Experiment 5: Associator cost per imaginary unit ===")
    for k, c in ranked:
        witt_label = next((f"Witt-pair {n}" for n,(p,q) in enumerate(WITT_PAIRS) if k in (p,q)), "")
        vac_label  = " ← VACUUM AXIS" if k == VACUUM_AXIS else ""
        print(f"  e{k+1} (idx {k}):  cost = {c:8.4f}  {witt_label}{vac_label}")

    print(f"\n  Min cost: {min_c}  Max cost: {max_c}  Ratio: {max_c/min_c:.4f}")
    print(f"  Prediction: all equal (Fano symmetry) → top outlier from S3, not assoc asymmetry")
    print(f"  If NOT all equal: the vacuum axis (e{VACUUM_AXIS+1}) should be the maximum")


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("=" * 60)
    print("COG Microstate Experiments: SM constants from Fano dynamics")
    print("=" * 60)

    experiment_lepton_mass_matrix()
    experiment_higgs_parity()
    experiment_cp_phase()
    experiment_lepton_orbit()
    experiment_associator_costs()

# RFC-015: Photon Energy in the Causal Octonion Graph

**Status:** Active — Architecture Draft (2026-02-24)
**Depends on:**
  - `rfc/CONVENTIONS.md` (locked Fano/Furey convention)
  - `rfc/RFC-013_Algebraic_Vacuum_and_Causal_Spawning.md` (e7 as photon operator)
  - `rfc/RFC-004_Particle_Motifs.md` (vertex costs V_e=1, V_mu=15)
**Claims addressed:**
  - `PHOTON-001` (stub — photon energy as emergent quantity)
**Literature:**
  - `sources/photon_energy_discrete_models.md`

---

## 1. Executive Summary

RFC-013 established that e7 is the photon operator (L_{e7} is photon absorption)
and that each e7 hop through vacuum costs zero drag (c = 1 tick/hop). This RFC
addresses the next question: **what determines photon energy?**

**Red-team finding:** The proposal "E = ΔS/Δt with Δt = vertex tick cost" has the
wrong direction. It predicts E_mu_photon < E_e_photon, while experiment requires
E_mu_photon >> E_e_photon (muonic hydrogen transitions are ~200× more energetic than
ordinary hydrogen). This RFC identifies the correct directional formula and defers
the full quantitative derivation to the orbital energy level program.

**Three locked decisions from this RFC:**

1. **P1 — Action Quantization:** Each e7 graph edge carries exactly one quantum of
   causal action: ΔS = ℏ per edge. This is local and operator-level.

2. **P2 — Energy is Relational, Not Local:** Photon energy is NOT a property of
   a single e7 edge. It is the difference in orbital binding depth between the
   initial and final states of the emitting/absorbing particle:
   E_photon = |E_initial_level - E_final_level|.

3. **P3 — Directional Proportionality:** Orbital binding depth scales with vertex
   cost V_particle, not inversely. Therefore E_mu_photon ~ 15 × E_e_photon at
   the level of vertex-cost counting. The full ~207× ratio requires the complete
   orbital energy derivation (deferred to post-mass-ratio milestone).

---

## 2. Background: The Photon Energy Gap

### 2.1 What RFC-013 Established

RFC-013 locked the following architectural decisions:
- L_{e7} is the universal photon operator: State_next = e7 · State_current
- e7 · omega = -i omega (vacuum phase rotation, zero drag, proved in Lean)
- Vacuum orbit period = 4 (all states satisfy L_{e7}^4 = id — Universal C_e=4 theorem)
- Photon traversal of a vacuum node: 1 tick/hop, no decoherence

### 2.2 What Was Not Established

RFC-013 did not address:
- What determines the energy of a photon
- Why different atomic transitions produce photons of different energies
- How the COG reproduces the Balmer series, Lyman series, etc.

### 2.3 Why This Matters (and Why It Can Be Deferred)

Photon energy quantization is required for:
- Spectroscopy derivation (Balmer/Lyman series for hydrogen)
- Compton scattering kinematics
- Photoelectric effect threshold

Photon energy quantization is NOT required for:
- Mass ratio derivation (m_mu/m_e, m_p/m_e) — the immediate program goal
- Koide formula derivation
- Generation structure
- Gauge symmetry proofs

Therefore: **spectroscopy is explicitly deferred.** This RFC establishes the
conceptual framework for future derivation without blocking current priorities.

---

## 3. Principle P1: Action Quantization

### 3.1 Statement

Each causal edge labeled by e7 carries exactly one quantum of causal action:

```
ΔS = ℏ  (per e7 graph edge)
```

This is a local, per-edge property. It does not imply a photon energy.

### 3.2 Literature Support

This principle is well-grounded in the literature (see sources/photon_energy_discrete_models.md §2):

- **Feynman checkerboard (Earle 2010, arXiv:1012.1564):** Each direction reversal
  contributes amplitude iε ~ iℏ. The mass parameter m = ε/(lattice step) = density
  of reversals. Action per step = ℏ by construction.

- **Johnston causal set QFT (2010, arXiv:1010.5514):** The causal set Feynman
  propagator is a sum over causal paths. Each causal link contributes one transition
  matrix factor. Energy is an eigenvalue of the discrete propagator matrix — a
  combinatorial quantity.

- **Sorkin (2009, arXiv:0910.0673):** The EM field from a moving charge is
  reconstructed by summing over past causal links. Photon energy is carried on
  causal links. This is the causal set grounding of ΔS = ℏ per link.

- **D'Ariano QCA (2014, arXiv:1406.1021):** In the 1D Dirac QCA path integral,
  each lattice step contributes a transition matrix. The checkerboard amplitude
  iε generalizes to iΔS/ℏ = i per step.

### 3.3 What P1 Does Not Imply

P1 assigns ℏ of action to each edge but does NOT assign an energy to the photon.
Energy requires a time interval: E = ΔS/Δt. The controversy is in what Δt means.

---

## 4. The Direction Problem: Critique of E = ℏ/Δt_vertex

### 4.1 The Proposed Formula

The natural first guess for photon energy in COG is:

```
E = ΔS / Δt = ℏ / V_particle
```

where V_particle is the vertex tick cost (V_e = 1, V_mu = 15).

### 4.2 Why It Fails

This formula predicts:

| Particle | V | E_photon (formula) | E_photon (experiment) |
|---|---|---|---|
| Electron | 1 | ℏ / 1 = ℏ | ~10 eV (Lyman-alpha) |
| Muon | 15 | ℏ / 15 = ℏ/15 | ~2 keV (muonic Lyman-alpha) |
| Ratio | — | 1/15 (mu < e) | ~200 (mu >> e) |

The formula gives the **wrong direction.** Muon-photon interactions must involve
higher-energy photons (muonic hydrogen is 200× more tightly bound), but the
formula predicts 15× lower energy for muons.

### 4.3 The Root Cause

The formula E = ℏ/V_particle treats V_particle as a characteristic time interval —
a rate at which interactions occur. But photon energy is not determined by interaction
rate; it is determined by **transition energy** — the depth of the orbital potential
well. Deeper wells → higher energy transitions → higher energy photons.

In the COG, deeper orbital binding corresponds to **more ticks accumulated per
orbit**, not fewer. Particles with higher vertex cost accumulate more ticks per
orbit and are therefore more tightly bound, not less.

---

## 5. Principle P2 and P3: Correct Directional Formula

### 5.1 Transition Energy

In any quantum theory, the energy of an emitted photon equals the transition energy:

```
E_photon = E_upper_level - E_lower_level
```

In COG terms, the orbital energy levels are functions of the tick-count accumulated
per orbit. The relevant quantity is:

```
Ticks per orbit = C_particle × V_particle
```

where C_particle = 4 (Universal C_e=4 theorem, proved in Lean for all states) and
V_particle is the vertex cost per hop.

| Particle | C | V | Ticks per orbit |
|---|---|---|---|
| Electron | 4 | 1 | 4 |
| Muon | 4 | 15 | 60 |

The muon's orbit costs 60 ticks vs the electron's 4 ticks. A higher tick-cost orbit
corresponds to a deeper binding — the particle "works harder" per cycle. The photon
emitted in a transition must carry the full orbital energy gap.

### 5.2 Directional Proportionality (P3)

At the level of vertex-cost counting:

```
E_photon ~ (C × V) × ℏ_unit / r²
```

where r is the principal quantum number and ℏ_unit is the fundamental action quantum.
This gives:

```
E_mu_photon / E_e_photon ~ (4 × 15) / (4 × 1) = 15
```

This is the RIGHT direction (muon photons are higher energy than electron photons),
but the factor is 15 rather than the experimental ~200. The remaining factor of ~14
must come from the complete orbital energy derivation, which depends on the radial
structure of the COG orbital levels (not yet computed).

### 5.3 Summary

P2: E_photon = orbital transition energy (difference between COG orbital levels).

P3: Orbital depth scales with ticks-per-orbit = C × V. Therefore E_photon ∝ V_particle
    in the correct direction. The exact coefficient requires the orbital level derivation.

---

## 6. Photon Field Structure: The Nurowski Alignment

A key structural alignment from the literature (Nurowski 2009, arXiv:0906.2060):

In the split-octonionic formulation, the vacuum Maxwell equations take the form:

```
∂F = 0
```

where ∂ = e1∂x + e2∂y + e4∂z + **e7∂t** and F is a split-octonionic
electromagnetic field with components in {e1,e2,e3,e4,e5,e6}.

**The photon field F lives in the 6D space perpendicular to e7.** The e7 direction
acts as the time operator.

This is consistent with COG conventions (CONVENTIONS.md §5.1):
- e7 is the vacuum axis (time direction)
- {e1,...,e6} is the color/charge sector

**Implication:** In COG, the photon is a state in the 6D color sector {e1,...,e6},
not in the e7 direction. The L_{e7} operator acts on these states as the time
evolution / photon absorption operator. This gives a consistent picture:
- e7 = time direction, photon operator
- photon field = excitation in {e1,...,e6} sector

Note: Nurowski's result uses split octonions; COG uses ordinary octonions (C⊗O).
The structural analogy is suggestive but not a direct import. The sign tensor
differs between split and ordinary octonion conventions.

**Photon masslessness from algebra (Furey alignment):** The photon has zero
computational drag because U(1)_EM is generated by Q = N/3 = (1/3)Σαᵢ†αᵢ,
which commutes with all SU(3)_c generators. The photon carries no color charge,
so it creates no octonionic non-associativity and forces no evaluation ticks.
In COG terms: V_photon = 0 because [Q, SU(3)] = 0. This is the algebraic
derivation of photon masslessness from the locked conventions, requiring no
additional postulate. (Source: Furey 1603.04078, Furey-Hughes 2209.13016)

---

## 7. D'Ariano-Perinotti Alignment

The strongest literature support for photon energy emerging from a discrete graph
is the D'Ariano-Perinotti QCA programme (arXiv:1407.6928):

**The photon is a composite boson built from two correlated massless Weyl fermions,
each on a quantum walk graph. Photon energy emerges from bosonic statistics when
the Fermi-pair density is low — it is NOT input.**

For COG, this suggests an open research direction:

**Question:** Can the COG photon (L_{e7} operator) be derived as a composite of two
Weyl-type states in C⊗O, analogous to the D'Ariano construction?

If so, photon energy would emerge from the bosonic statistics of the C⊗O state
algebra, without any additional postulate. This is a medium-term research goal,
not required for near-term mass-ratio proofs.

---

## 8. Spectroscopy Deferral

The full derivation of spectral line energies requires:

1. **COG orbital energy levels:** The analog of E_n = -m_e α²/(2n²) in COG terms.
   This requires computing the "binding energy" of each orbital level as a function
   of tick count, not yet done.

2. **The COG Bohr radius:** The analog of a_0 = ℏ/(m_e α c) as a graph-theoretic
   quantity (path length in the causal DAG between the electron orbit center and
   the boundary of the Coulomb region).

3. **Coulomb interaction in COG:** How the proton (a V_p >> 1 vertex) modifies the
   tick costs of the orbiting electron. This is the bound-state problem, addressed
   by the hydrogen atom program (deferred to after mass-ratio derivation).

**Until these are derived, the COG cannot predict absolute photon energies.**
It can predict energy ratios (E_mu_photon / E_e_photon ~ 15 from vertex costs),
and it can confirm the correct directional ordering. This is sufficient for the
current program goals.

---

## 9. Open Problems

| # | Problem | Severity | Blocker for |
|---|---|---|---|
| OP-1 | Full derivation of COG orbital energy levels | High | Spectroscopy |
| OP-2 | Photon as composite Fermi-pair in C⊗O (D'Ariano alignment) | Medium | Photon completeness |
| OP-3 | Ordinary vs split octonion reconciliation for Maxwell ∂F=0 | Medium | EM from COG |
| OP-4 | Why V_mu/V_e = 15 but m_mu/m_e = 207 (the 14× gap) | High | Full mass ratio |
| OP-5 | Photon emission (not just absorption) mechanism | Medium | Spectroscopy |
| OP-6 | Connection L_{e7} operator to U(1) gauge boson from Furey algebra | Low | Formal completeness |

OP-4 is the critical gap: the vertex cost ratio 15 gives the direction correct but
not the magnitude. The factor of ~14 must emerge from the orbital energy level
structure, and deriving it is equivalent to deriving the full muon mass.

---

## 10. Locked Decisions

The following are locked and should not be revisited without explicit human approval:

**LOCKED:** e7 is the photon operator (L_{e7} is photon absorption). From RFC-013.

**LOCKED:** Each e7 edge carries ΔS = ℏ of causal action. From P1 above.

**LOCKED:** E_photon is not a local property of a single e7 edge. It is a relational
property (transition energy) of the emitting/absorbing orbital structure. From P2.

**LOCKED:** E_photon ∝ V_particle in the correct direction (not inversely). From P3.

**DEFERRED (not locked):** The exact coefficient relating E_photon to V_particle
and orbital quantum numbers. This requires the orbital energy level derivation.

---

## 11. Action Items

| # | Action | Target File | Priority |
|---|---|---|---|
| A1 | Create claims/PHOTON-001.yml with status=partial | claims/ | Immediate |
| A2 | Verify Lean: Nurowski split-oct ∂F=0 analogue in C⊗O is consistent | CausalGraphTheory/ | Medium |
| A3 | Python: compute E_mu/E_e ratio from V counts, compare to muonic H data | calc/ | Medium |
| A4 | Literature: investigate D'Ariano photon-as-Fermi-pair in C⊗O language | sources/ | Low |
| A5 | After mass-ratio proof: derive COG Bohr energy formula | calc/ | Deferred |

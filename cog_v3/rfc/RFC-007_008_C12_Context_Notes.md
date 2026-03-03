# RFC-007 + RFC-008: C12 Context and Connections

Status: Notes
Date: 2026-03-03
Author: COG Core (Claude lane)
Applies to:
- `RFC-007_Motif_First_Chirality_Emergence_and_Parity_Test_Contract.md`
- `RFC-008_Mesoscale_Lorentz_Pseudosymmetry_and_RG_Selection_Contract.md`

## 1. RFC-007 in C12 Context

### 1.1 Scope extension

RFC-007 §2 is scoped to "S960 alphabet (C4 × Q240)". The analysis should be extended to
S2880 = C12 × Q240. The C12 migration adds new chirality channels not present in C4.

### 1.2 C12 chirality = Δp sign asymmetry

In S2880, the natural parity transform for the C12 phase sector is:
```
P(p, q) = (-p mod 12, q_parity)
```
where q_parity is the parity-conjugate of q in Q240.

The parity-transform maps:
- p=1 ↔ p=11 (Gen2 ↔ Gen2, 30° ↔ 330°)
- p=4 ↔ p=8 (Gen2 ↔ Gen3, 120° ↔ 240°)
- p=0 ↔ p=0 (self-conjugate)

Key observation: under P, Gen2 and Gen3 SWAP (p=4 ↔ p=8), but Gen1 (p=0,3,6,9)
maps to Gen1. This is the discrete analog of weak isospin: left-handed doublets
(Gen1/Gen2) vs right-handed singlet (Gen3 decoupled).

### 1.3 RFC-007 observable mapping to RFC-010

RFC-007 chirality observables map to RFC-010 metrics:
| RFC-007 | RFC-010 / RFC-016 | Notes |
|---------|------------------|-------|
| winding_sign | A₁ = P(Δp=+3) - P(Δp=-3) | Signed hop asymmetry |
| symmetry_score | |A₁(M)| - |A₁(P(M))| | Asymmetry reversal test |
| triad_sign | Sign convention of dominant Z₄ orbit direction | RFC-010 orientation |

Current RFC-010 data: A₂ = -0.0290 (small non-zero asymmetry in even channels).
After RFC-015 fix: A₁ expected to become non-zero for odd-phase motifs (d3 channel).

### 1.4 Parity violation in C12

In C12, the parity transform P sends p → -p mod 12. The Brannen delta (RFC-016 §5.2)
breaks this symmetry: delta ≠ 0 means the mass eigenstates at {0°+δ, 120°+δ, 240°+δ}
are NOT symmetric under p → -p (unless δ = 0 or δ = π/2).

This is the C12 analog of CP violation — the delta offset = discrete CP phase.
Physical prediction: stable motifs at non-zero delta will show measurable A₁ ≠ 0
(matching RFC-007 H1: parity-neutral kernel + chiral motif → asymmetric dynamics).

### 1.5 Updated RFC-007 test protocol for C12

When testing RFC-007 in S2880:
1. Use odd-phase seeds at p=1 (Gen2 representative, as assigned in RFC-015).
2. Construct parity partner: seed at p=-1 mod 12 = 11 (also Gen2).
3. Run both; compare A₁ values.
4. H1 confirmed if: A₁(p=1 motif) ≠ 0 AND sign of A₁ is opposite for p=11 motif.

---

## 2. RFC-008 in C12 Context

### 2.1 Phase diagram constraint on kernel selection

RFC-008 defines an RG-based kernel selection criterion: anisotropy must decrease under
coarse-graining. This is a necessary but not sufficient condition for physical kernels.

RFC-017 adds a NECESSARY ADDITIONAL CONDITION:
> The physical kernel must be in Phase M (mesophase), not Phase D (disordered).

Combined selection criterion:
```
Physical kernel passes iff:
  1. anisotropy_block4 < anisotropy_block2 < anisotropy_micro  (RFC-008 RG gate)
  AND
  2. R3 ≥ 2 in odd-phase seeds                                 (RFC-017 Phase M gate)
```

### 2.2 Mesophase = RG IR fixed point

The RFC-008 anisotropy decay corresponds to RG flow toward a fixed point. In the
C12 clock model:
- Phase D: the disordered fixed point (all coupling flows to zero)
- Phase M: the ordered fixed point (within-gen coupling flows to large value)
- Phase boundary: the critical fixed point (scale-invariant, conformally symmetric)

The K0 kernel (near-critical, seed-sensitive) may BE at or near the critical point.
This would explain why K0 passes more gates than K1/K2 (which are in Phase D):
K0 is near-critical → it has the LONGEST correlation length → best Lorentz approximation
at mesoscales (largest correlation length ≈ largest Lorentz-invariant region).

Physical prediction: the physical kernel is at or just below the critical point,
in the Phase M side where R3 just exceeds 2.

### 2.3 K1/K2/K3 candidates in Phase M context

RFC-008 evaluates K1 (cube26 uniform), K2 (cube26 shell-scheduled), K3 (cube26 split-step).
Gate-5-v2 shows all three are in Phase D (diffusive) for current seeding.
After RFC-015 fix + Phase M search (RFC-017 sweep), the evaluation should use:
- Not K0/K1/K2 labels from previous gate evaluations
- The w3-biased family {w3=1, 2, 4, 8, ...} as the new kernel candidates
- RFC-008 metrics (anisotropy decay) applied to the w3-biased kernels

If w3_crit > 1: the minimum physical kernel has w3 > 1 (K0 is not physical; biased kernel required).
If w3_crit ≈ 1: K0 is the critical kernel and is physical (near-critical mesophase).

### 2.4 Updated kernel shortlist

Based on RFC-017 and RFC-008 combined, the new kernel evaluation family should be:
- K_w3_1: S2880 uniform (w3=1) = K0 in S2880 encoding
- K_w3_2: S2880 with w3=2 (mild within-gen bias)
- K_w3_4: S2880 with w3=4 (moderate bias)
- K_w3_8: S2880 with w3=8 (strong bias)

Each candidate is evaluated on BOTH gates:
1. RFC-008 anisotropy decay (Lorentz-like gate)
2. RFC-017 R3 and Kuramoto r (Phase M gate)

---

## 3. Combined Picture

The three RFC series connect as follows:

```
RFC-007 (chirality)
  ↕ connects via A₁ parity observable
RFC-010 (C12 phase channels, R3, A₁)
  ↕ connects via odd-phase seeding
RFC-015 (trial bank fix — enables R3 > 0)
  ↕ connects via R3 > 1 condition
RFC-017 (phase boundary — identifies mesophase)
  ↕ connects via w3 parameter sweep
RFC-008 (RG/Lorentz kernel selection)
  ↕ connects via mesophase = RG fixed point
RFC-016 (Koide formula — mass eigenstates in mesophase)
```

The execution dependency order is:
1. RFC-015 fix (kick-phase-0 in trial bank) — unblocks all downstream
2. RFC-017 sweep (find mesophase) — identifies physical kernel
3. RFC-007 chirality probe (at mesophase, with odd-phase seeds) — tests parity violation
4. RFC-008 anisotropy decay (for w3 > w3_crit kernel) — confirms Lorentz criterion
5. RFC-016 Phase B (measure Brannen delta in mesophase) — predicts lepton masses

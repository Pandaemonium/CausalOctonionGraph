# Koide Proof (v1)

Status: partial formal proof, assumption-explicit.
Date: 2026-03-03

Superseded for external sharing by:
- `sources/koide_proof_v2_kernel_v5_for_external_review.md`

This note gives the cleanest currently defensible proof chain for Koide in this repo.

## 1) Target statement

Let `f_e, f_mu, f_tau > 0` be square-root masses:

- `f_e = sqrt(m_e)`
- `f_mu = sqrt(m_mu)`
- `f_tau = sqrt(m_tau)`

Define

`K := (f_e^2 + f_mu^2 + f_tau^2) / (f_e + f_mu + f_tau)^2`.

Koide exactness is `K = 2/3`.

## 2) Algebraic core (fully proved)

Set:

- `S2 := f_e^2 + f_mu^2 + f_tau^2`
- `P2 := f_e f_mu + f_mu f_tau + f_tau f_e`

Then:

`K = 2/3` is equivalent to

`3*S2 = 2*(f_e + f_mu + f_tau)^2`.

Expand:

`2*(f_e + f_mu + f_tau)^2 = 2*S2 + 4*P2`.

So:

`3*S2 = 2*S2 + 4*P2` iff `S2 = 4*P2`.

Therefore:

`K = 2/3  <->  S2 = 4*P2`.

This is formalized in Lean:

- `CausalGraphTheory/Koide.lean`
- theorem `koide_algebraic_iff`

## 3) Z3 Brannen ansatz reduction (fully proved, assumption-explicit)

Assume

`f_k = A * (1 + B*c_k)` for `k in {0,1,2}`

with Z3 constraints

- `c_0 + c_1 + c_2 = 0`
- `c_0 c_1 + c_1 c_2 + c_2 c_0 = -3/4`.

From these constraints:

`c_0^2 + c_1^2 + c_2^2 = 3/2`.

Then:

- `sum f_k = 3A`
- `sum f_k^2 = A^2 * (3 + (3/2) B^2)`

Hence

`K = [A^2 * (3 + (3/2)B^2)] / (3A)^2 = 1/3 + B^2/6`.

So:

`K = 2/3` iff `B^2 = 2`.

This bridge is formalized in Lean:

- `CausalGraphTheory/Koide.lean`
- theorem `brannen_b_squared`

and pipeline form:

- `CausalGraphTheory/KoideGroupBridge.lean`
- theorem `brannen_koide_from_z3_and_b2`

## 4) C12/Z3 phase geometry fact (proved as group identity)

On C12, choose Z3 orbit `{0,4,8}`:

- `z_0 = exp(2*pi*i*0/12) = 1`
- `z_1 = exp(2*pi*i*4/12) = omega`
- `z_2 = exp(2*pi*i*8/12) = omega^2`
- with `omega^3 = 1`, `omega != 1`.

Then:

`1 + omega + omega^2 = 0`.

This proves exact 120-degree phase balancing in the generation sector.

Important: this identity alone does **not** force `B^2 = 2`; it supports the Z3-equispaced ansatz.

## 5) Exact current conclusion

What is proved:

1. `K = 2/3 <-> S2 = 4*P2` (exact algebra).
2. Under Z3 Brannen ansatz, `K = 2/3 <-> B^2 = 2` (exact algebra).
3. Z3 orbit `{0,4,8}` has exact phase-sum cancellation.

What remains to close full "Koide-from-kernel":

1. Derive the Z3 ansatz constraints from the active kernel dynamics (not impose them).
2. Derive why kernel dynamics select `B^2 = 2` (or equivalent) without fitting.

So this is a rigorous partial proof with a clear remaining kernel-closure gap.

## 6) Practical use in claims

Safe claim wording today:

- "Koide exactness is algebraically equivalent to `S2=4*P2`, and in the Z3 Brannen class this is equivalent to `B^2=2`; full kernel derivation of these constraints is pending."

Unsafe wording today:

- "Kernel already proves Koide with no remaining assumptions."

## 7) How to tie Koide to the algebra (must-use structure)

To make Koide a consequence of the algebra (not a fitted overlay), use only these
model-internal structures as inputs:

1. **State algebra factorization**
   - `S = Z3 (domain) x Q240 (octavian) x Z (energy) x Z4 (energy phase)`.
2. **C12 embedding**
   - `phase_idx = 4*domain + 3*energy_phase (mod 12)`.
   - Domain is a 120-degree rotor; energy phase is a 90-degree rotor.
3. **Coherent-lightcone kernel**
   - Physical states are exactly path-independent fold products.
4. **No-fit invariants**
   - Triality symmetry (`Z3`) and energy-phase symmetry (`Z4`) are exact.
   - Any derived mass relation must be invariant under allowed relabelings.

If Koide is real in this model, it must be derivable from those four items alone.

## 8) Concrete "algebra must be used" proof plan

Define a lepton mass proxy from the kernel:

- For a stable motif class `M_k` (k in {0,1,2}), define frequency
  `f_k := 1 / period(M_k)` or an equivalent invariant tick-rate functional.

Then prove this chain:

1. **Z3-equivariant generation orbit**
   - The three charged-lepton motifs form one `Z3` orbit:
     `M_{k+1} = T(M_k)` with `T^3 = id`.
2. **Mode decomposition forced by Z3**
   - Any generation-indexed scalar observable decomposes in basis
     `{1, omega^k, omega^{2k}}`, `omega = exp(2*pi*i/3)`.
   - So `f_k` must take Brannen/circulant form:
     `f_k = A * (1 + B*c_k)` with fixed `Z3` geometry for `c_k`.
3. **Kernel-derived quadratic constraint**
   - Show kernel conservation/equivariance implies the SOS identity
     `S2 = 4*P2`, or equivalently `B^2 = 2`.
4. **Apply existing algebraic theorem**
   - From Section 2, conclude `K = 2/3`.

This is the exact point where current work is blocked: Step 3.

## 9) What to prove next in Lean (minimal set)

Add these theorem targets (names suggested):

1. `z3_orbit_of_lepton_motifs`
   - Lepton candidates are one orbit under a `Z3` action induced by kernel symmetry.
2. `observable_z3_fourier_form`
   - Any generation observable pulled from kernel is in the 3-mode Fourier basis.
3. `kernel_implies_sos_condition`
   - From kernel axioms/invariants, derive `f_e^2+f_mu^2+f_tau^2 = 4*(...)`.
4. `koide_from_kernel`
   - Immediate corollary via `koide_ratio_is_two_thirds_of_sos`.

Until (3) is formalized, "Koide from kernel" remains a partial result.

## 10) Engineering constraints to prevent hidden fitting

To keep the result legitimate:

1. Do not choose `A,B,c_k` by fitting masses.
2. Derive `f_k` only from motif dynamics and invariant functionals.
3. Freeze convention choices before evaluation.
4. Require replay hash reproducibility for every proof-supporting artifact.
5. Reject any derivation that introduces continuous free parameters not already
   present in the discrete algebra.

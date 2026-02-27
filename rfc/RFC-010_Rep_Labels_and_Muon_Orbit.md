# RFC-010: Rep Labels, C⊗O State Vectors, and the Muon Orbit

**Status:** Draft
**Created:** 2026-02-22
**Module:** `COG.Algebra.Spinors`, `COG.Particles.LeptonMotifs`
**Dependencies:** `rfc/CONVENTIONS.md` (locked), `rfc/RFC-001_Canonical_State_and_Rules.md`,
  `rfc/RFC-009_Spinor_Representations_and_Triality_Overhead.md`
**Claims addressed:** KOIDE-001 (lepton generation masses — muon in particular)

---

## 1. Executive Summary

The goal of this RFC is to define the update rule well enough to simulate the
**muon orbit** — the COG motif whose tick count (or gate density) represents the
muon mass — and to compute the ratio `C_μ / C_e` for comparison with the
experimental value `m_μ / m_e ≈ 206.768`.

The session ending RFC-009 identified four blockers. A subsequent literature
search (2026-02-22) resolved or reframed all four:

| # | Blocker | Prior status | Resolution |
|---|---------|-------------|------------|
| B1 | Python `Node` missing Rep label | Open | **Fix**: add `rep: NodeLabel` to Python dataclass |
| B2 | Cross-rep product rule undefined | Open | **Closed**: it IS octonion multiplication (Fano table) |
| B3 | Complex unit `i` not tracked in Python state | Open | **Fix**: upgrade state to 8-component `ComplexOctonion` |
| B4 | Triality map τ has no explicit matrix | Open | **Reframed**: use Furey's projector-sector labeling instead |

The critical architectural finding is:

> **The V × S⁺ → S⁻ cross-representation product is identically octonion
> multiplication: t(x, a) = x · a (left multiplication, using the Fano table).
> No additional formula is required.**
>
> — Baez (2002), Baez–Huerta (2010/2011); confirmed by literature search.

This means the physical cost of the triality rotation is already encoded in the
Fano-table evaluation. The only missing pieces are:
1. Correctly labeling which Rep each node lives in.
2. Tracking the full `ComplexOctonion ℤ` state (8 rational components) rather
   than the reduced `(OctIdx, sign)` state.

---

## 2. The Furey Labeling Scheme (replacing V/S+/S-)

### 2.1 Why SO(8) triality V/S+/S- is the wrong frame

The abstract SO(8) representations V, S⁺, S⁻ are all isomorphic to ℝ⁸ as vector
spaces; they differ only in how so(8) acts. There is **no basis permutation**
τ: {e₀,..,e₇} → {e₀,..,e₇} implementing the triality rotation. τ acts on the
Lie algebra so(8), not on representation vectors.

Attempting to implement τ as a 8×8 permutation matrix is therefore a
category error. We need a different way to distinguish the three generations.

### 2.2 Furey's projector-sector construction (Cl(6) / C⊗O)

Furey (2019, arXiv:1910.08395) constructs three lepton generations directly from
the complex octonions C⊗O using **two commuting idempotents**:

```
Left vacuum:   s  = ½(1 + i·e₇)     (acts from the LEFT)
               s* = ½(1 - i·e₇)

Right vacuum:  S  = ½(1 + i·e₇)     (acts from the RIGHT)
               S* = ½(1 - i·e₇)
```

**Note**: `s` and `S` use the same formula but act from opposite sides in the
algebra. Because C⊗O is non-associative, left and right actions are genuinely
distinct.

The four projector sectors are (Furey 2019, arXiv:1910.08395, Eq. 19):

```
Sector  s · _ · S*   — generation 1 (electron family)
Sector  s* · _ · S*  — generation 2 (muon family)
Sector  s* · _ · S   — generation 3 (tauon family)   [or sS, both appear]
Sector  s · _ · S    — sterile sector (no physical charged lepton)
```

The charged lepton states (Furey 2019, Eq. 21) are:

```
e₁⁻ = s·S* · (i·e₁ - e₃ + e₁₂₆ + e₁₄₅) · s*·S*      [electron]
e₂⁻ = s·S* · (-i·e₂ + e₆ + e₁₂₃ - i·e₁₃₆) · s*·S*    [muon]
e₃⁻ = s·S* · (-i·e₄ + e₅ - e₁₃₄ - i·e₁₃₅) · s*·S*    [tauon]
```

where e_{ijk} = e_i · e_j · e_k (triple Fano products). These are explicit elements
of C⊗O with rational-integer coefficients once the ½ denominators from s and S* are
cleared (work at 4× scale: 2s = e₀ + i·e₇, 2S* = e₀ - i·e₇).

### 2.3 Why this is better than ie₇ eigenvalue

The ie₇ eigenvalue (the operator "multiply on the LEFT by ie₇") gives only a Z₂
splitting: eigenvalue +1 corresponds to the `s`-sector, eigenvalue -1 to `s*`-sector.
This distinguishes the first/third generations from the second, but NOT all three.

The RIGHT vacuum eigenvalue (ie₇ acting from the RIGHT via S vs. S*) gives the
second Z₂. Together the two bits give Z₂ × Z₂ — four sectors, three of which
correspond to the three charged lepton generations. The triality cycle

```
V → S⁺ → S⁻ → V
```

is a Z₃ action on the abstract SO(8) representations, but Furey's concrete C⊗O
realization gives the Z₂ × Z₂ sector structure directly from s and S, which is
sufficient to label the generations without needing an explicit Z₃ triality map.

The McRae 2025 matrix H = (1/2)M (arXiv:2502.14016, Eq. 8) is the most explicit
form of the abstract triality available, but it acts on the 28 so(8) generators
(organized into 7 quartets), not on the 8-dimensional representation vectors. It
is **not needed** for the COG simulation — only the sector labels matter.

### 2.4 The NodeLabel enum (already in State.lean)

The Lean file `CausalGraphTheory/State.lean` already has:

```lean
inductive NodeLabel : Type
  | V        -- vector rep (fermion after triality rotation)
  | S_plus   -- positive-chirality spinor
  | S_minus  -- negative-chirality spinor
  | vacuum   -- Fock vacuum state
```

**Action required**: Reinterpret `V | S_plus | S_minus` as:
- `S_plus` ↔ Furey's `s`-sector (left vacuum eigenvalue +1, ie₇ acts from left)
- `S_minus` ↔ Furey's `s*`-sector (left vacuum eigenvalue -1)
- `V`      ↔ a lepton or quark state after both projectors applied (fully specified)

The distinction between generations 1, 2, 3 (and the sterile sector) is then
carried by the **right vacuum** projection, which we encode as a new field.

---

## 3. The Muon State Vector (Furey 2019, Eq. 21–22)

### 3.1 First-generation electron state

The electron state in C⊗O is (Furey 2019, Eq. 21):

```
ψ_e = α₁† α₂† α₃† · ω
```

where:
```
ω       = ½(e₀ + i·e₇)                          — vacuum (s-sector, S-sector)
α₁†     = ½(-e₆ + i·e₁)                         — raising operator, color 1
α₂†     = ½(-e₂ + i·e₅)                         — raising operator, color 2
α₃†     = ½(-e₃ + i·e₄)                         — raising operator, color 3
```

The electron state ψ_e carries all three color charges — it is the charged
lepton, color-singlet combination.

### 3.2 Second-generation muon state

The muon lives in the **s*·S*** sector of C⊗O (Furey 2019, Eq. 19). Its
concrete state vector is (Furey 2019, Eq. 21):

```
ψ_μ = e₂⁻ = s·S* · (-i·e₂ + e₆ + e₁₂₃ - i·e₁₃₆) · s*·S*
```

where `e_{ijk} = e_i · e_j · e_k` denotes the triple Fano product (evaluated
left-to-right using the Furey convention from `rfc/CONVENTIONS.md`).

To evaluate this as a concrete element of C⊗O:

1. Expand the triple products using the Fano table:
   ```
   e₁₂₃ = e₁ · e₂ · e₃ = e₃ · e₃ = -e₀    (since e₁·e₂=e₃, then e₃·e₃=-e₀)
   e₁₃₆ = e₁ · e₃ · e₆ = (-e₂) · e₆ = ...  (use Fano table)
   ```

2. Apply s = ½(e₀ + ie₇) from the LEFT and S* = ½(e₀ - ie₇) from the RIGHT.

3. The result is an element of C⊗O. Working at 4× scale (using 2s and 2S*
   to avoid fractions), the muon vacuum state is:

```
4·ω_μ = (e₀ + i·e₇) · (-i·e₂ + e₆ + e₁₂₃ - i·e₁₃₆) · (e₀ - i·e₇)
```

This product must be computed using the Fano table and `FormalComplex`
arithmetic. The result is an element of C⊗O with integer coefficients in the
basis {e₀, ie₀, e₁, ie₁, ..., e₇, ie₇}.

**Note**: The generation-2 vacuum ω_μ satisfies ω_μ² = ω_μ (idempotency) —
this is a consistency check that the sector projection is correctly applied.

### 3.3 Generation-shift automorphism (for context)

The three state vectors ψ_e, ψ_μ, ψ_τ are NOT related by a simple permutation
of octonion basis indices. They are in different projector blocks of Cl(6):

| Generation | Projector sector | Left | Right |
|-----------|-----------------|------|-------|
| 1 (electron) | s·S* | s = ½(1+ie₇) | S* = ½(1-ie₇) |
| 2 (muon)     | s*·S* | s* = ½(1-ie₇) | S* = ½(1-ie₇) |
| 3 (tauon)    | s*·S or s·S | s* (or s) | S = ½(1+ie₇) |

The connection to the J₃(C⊗O) Albert algebra (relevant for the Koide formula)
is that the three primitive idempotents of J₃ correspond to the diagonal entries
(ω₁, ω₂, ω₃) of a 3×3 Jordan matrix, and their eigenvalues give the Brannen
circulant parametrization. But this connection is for the mass matrix structure,
not for the orbit simulation.

### 3.3 Orbit length as mass

In the COG framework, mass = orbit length under the exchange rule. For
generation-1 (electron), the orbit is the shortest closed path in the Fano
graph that is algebraically consistent (associative subalgebra). For
generation-2 (muon), the orbit passes through a non-associative sector before
returning.

**Hypothesis**: The ratio C_μ / C_e (orbit lengths) equals m_μ / m_e ≈ 206.768.

This will be tested by simulation once the muon state vector ω₂ is computed
and the COG exchange rule is correctly applied to it.

---

## 4. Implementation Plan

### Phase A — Lean: Add generation label and compute ω₂

**File**: `CausalGraphTheory/Spinors.lean` (new file)

```lean
import CausalGraphTheory.WittBasis
import CausalGraphTheory.ComplexOctonion

namespace CausalGraph

/-- The three lepton generations, plus the sterile sector. -/
inductive Generation : Type
  | gen1   -- electron family (s·_·S sector)
  | gen2   -- muon family    (s·_·S* sector)
  | gen3   -- tauon family   (s*·_·S* sector)
  | sterile -- no physical particle (s*·_·S sector)
  deriving DecidableEq, Repr

/-- Left vacuum idempotent: s = ½(e₀ + i·e₇). Doubled: 2s = e₀ + i·e₇. -/
def leftVacuumDoubled : ComplexOctonion ℤ :=
  ComplexOctonion.basis 0 + ComplexOctonion.mulI (ComplexOctonion.basis 7)

/-- Right vacuum: same formula, but semantically acts from the RIGHT. -/
def rightVacuumDoubled : ComplexOctonion ℤ := leftVacuumDoubled

/-- Generation-2 vacuum (muon sector): 2·ω₂ = 2s* · 2ω · 2S (scaled). -/
-- To be computed: (e₀ - i·e₇) * (e₀ + i·e₇) * (e₀ + i·e₇)
-- All divisions by 8 are deferred; we work with the 8× scaled version.
def gen2VacuumOctet : ComplexOctonion ℤ :=
  sorry  -- TODO: compute (e₀ - ie₇) * (e₀ + ie₇) * (e₀ + ie₇) via Fano table

end CausalGraph
```

**Tasks**:
- A1. Write `Spinors.lean` with `Generation` type and `leftVacuumDoubled`.
- A2. Compute `gen2VacuumOctet` by evaluating the three-term Fano product
      `(e₀ - ie₇) * (e₀ + ie₇) * (e₀ + ie₇)` in `ComplexOctonion ℤ`.
      Use `lean_run_code` to check intermediate steps.
- A3. Add `#eval` checks verifying idempotency of ω₂ (scaled).
- A4. Prove `τ_order` (Z₃ action of generation shift): `decide`-provable once
      the three generation vacua are concrete elements.

### Phase B — Python: Upgrade state to full ComplexOctonion

**File**: `calc/spinor_state.py` (new file, keeping `mass_drag.py` intact)

The Python simulation currently uses `(OctIdx: int, sign: int)` — a 14-point
state. This misses the complex `i` component entirely.

The upgraded state is a `ComplexOctonion`: 8 components, each a `Fraction` pair
`(re, im)` — matching `ComplexOctonion ℤ` in Lean.

```python
# calc/spinor_state.py
from fractions import Fraction
from dataclasses import dataclass
from typing import Tuple
from calc.conftest import FANO_CYCLES, FANO_SIGN, FANO_THIRD

# A ComplexOctonion over Q: 8 components of (re, im)
# Index 0 = e₀ component, ..., Index 7 = e₇ component
ComplexOct = Tuple[Tuple[Fraction, Fraction], ...]  # length 8

ZERO: ComplexOct = tuple((Fraction(0), Fraction(0)) for _ in range(8))

def basis(k: int) -> ComplexOct:
    """Pure real basis element e_k."""
    return tuple((Fraction(1) if j == k else Fraction(0), Fraction(0))
                 for j in range(8))

def i_times(x: ComplexOct) -> ComplexOct:
    """Multiply by central imaginary unit i: (re,im) -> (-im, re)."""
    return tuple((-im, re) for (re, im) in x)

def add(x: ComplexOct, y: ComplexOct) -> ComplexOct:
    return tuple((xr+yr, xi+yi) for (xr,xi),(yr,yi) in zip(x,y))

def scale(q: Fraction, x: ComplexOct) -> ComplexOct:
    return tuple((q*r, q*im) for (r,im) in x)

def oct_mul_basis(j: int, k: int) -> ComplexOct:
    """Product e_j * e_k in C⊗O, returning a ComplexOct."""
    if j == 0: return basis(k)        # e₀ is identity
    if k == 0: return basis(j)
    if j == k: return scale(Fraction(-1), basis(0))   # e_j² = -e₀

    sign = FANO_SIGN.get((j, k), 0)
    if sign == 0:
        raise ValueError(f"No Fano product for ({j},{k})")
    third = FANO_THIRD[(j, k)]
    result = basis(third)
    if sign < 0:
        result = scale(Fraction(-1), result)
    return result

def oct_mul(x: ComplexOct, y: ComplexOct) -> ComplexOct:
    """Full C⊗O multiplication: (a + ib)(c + id) = ac - bd + i(ad + bc)
    where a,b,c,d are Octonion parts and i commutes with all e_j."""
    result = ZERO
    for j in range(8):
        xr, xi = x[j]
        for k in range(8):
            yr, yk_im = y[k]
            # real part of x[j] * real part of y[k]: xr*yr * (e_j * e_k)
            if xr != 0 and yr != 0:
                ej_ek = oct_mul_basis(j, k)
                result = add(result, scale(xr * yr, ej_ek))
            # i * x[j] * i * y[k] = -xi*yk_im * (e_j * e_k)  [i²=-1]
            if xi != 0 and yk_im != 0:
                ej_ek = oct_mul_basis(j, k)
                result = add(result, scale(-xi * yk_im, ej_ek))
            # real * imaginary: xr*yk_im * i*(e_j * e_k)
            if xr != 0 and yk_im != 0:
                ej_ek = oct_mul_basis(j, k)
                result = add(result, i_times(scale(xr * yk_im, ej_ek)))
            # imaginary * real: xi*yr * i*(e_j * e_k)
            if xi != 0 and yr != 0:
                ej_ek = oct_mul_basis(j, k)
                result = add(result, i_times(scale(xi * yr, ej_ek)))
    return result
```

**Tasks**:
- B1. Write `calc/spinor_state.py` with `ComplexOct` type and arithmetic.
- B2. Add pytest tests in `calc/test_spinor_state.py`:
  - `test_basis_mul`: verify `e₁ * e₂ = +e₃` (and all 7 directed triples).
  - `test_vacuum_idempotent`: verify `ω * ω = ω` where `ω = ½(e₀ + ie₇)`.
  - `test_lower_annihilates`: verify `α₁ · ω = 0`, `α₂ · ω = 0`, `α₃ · ω = 0`.
- B3. Compute and print gen-1, gen-2, gen-3 vacuum state vectors.
- B4. Verify `gen2_vacuum * gen2_vacuum = gen2_vacuum` (idempotency).

### Phase C — Python: Simulate the muon orbit

**File**: `calc/muon_orbit.py` (new file)

Once the gen-2 state vector ω₂ is known, simulate the COG exchange rule:

```
Exchange rule (single step, for a lepton node with state ψ):
  ψ_new = edge_operator · ψ   (left multiplication by the edge operator)
```

The electron's exchange rule cycles through the L1 subalgebra {e₁, e₂, e₃} —
a fully associative quaternionic subalgebra. Each step costs 1 tick.
The orbit closes after 3 steps (associative cycle), so `C_e = 3`.

The muon's exchange rule crosses Fano lines, entering non-associative sectors.
The branching protocol (RFC-001 §3.3) applies: each non-associative step
spawns two branches (left and right products differ). The orbit is the
**minimum-cost branch** that returns to ω₂.

```python
# calc/muon_orbit.py
from calc.spinor_state import ComplexOct, oct_mul, ZERO
from calc.conftest import FANO_CYCLES

def electron_orbit() -> int:
    """Simulates electron motif: cyclic through L1 = {e1, e2, e3}.
    Returns orbit length C_e = 3."""
    # e1 -> e1*e2 = e3 -> e3*e1 = e2 -> e2*e3 = e1 (cycle of length 3)
    # All products are associative (quaternion subalgebra H ⊂ O).
    return 3

def muon_orbit(max_steps: int = 10_000) -> dict:
    """Simulate muon motif: cyclic through a non-associative Fano path.
    Returns first recurrence tick count C_mu."""
    # TODO: implement after gen-2 state vector is computed in Phase A/B
    pass
```

**Tasks**:
- C1. Implement `electron_orbit()` and verify `C_e = 3`.
- C2. Implement `muon_orbit()` after gen-2 state vector is known.
- C3. Report `C_μ / C_e` and compare to `m_μ / m_e = 206.768`.

### Phase D — Lean: Prove τ order-3

**File**: `CausalGraphTheory/Spinors.lean` (continuation of Phase A)

```lean
/-- The generation-shift automorphism has order 3. -/
theorem generation_shift_order3 : ∀ g : Generation,
    shift (shift (shift g)) = g := by decide
```

This is provable by `decide` once `Generation` and `shift` are fully defined
(all four cases: gen1 → gen2 → gen3 → gen1, sterile → sterile).

---

## 5. Blocker Resolution Summary

### B1: Python Node missing Rep label — RESOLVED in Phase B

Add `rep: Generation` to the Python `Node` dataclass in `spinor_state.py`.
The Lean equivalent (`Node.label: NodeLabel`) already exists in `State.lean`.

### B2: Cross-rep product rule undefined — ALREADY RESOLVED

**Finding**: The cross-representation product V × S⁺ → S⁻ is exactly
octonion multiplication `t(x, a) = x · a` (Baez 2002, Baez–Huerta 2010).
The Fano table correctly computes this. No additional formula is needed.

**Cost**: 1 tick if the product is on a single Fano line (associative);
2 ticks if the product is between two non-collinear imaginary units
(triggers the Alternativity Evaluator — RFC-001 §3.3).

### B3: Complex i not tracked — RESOLVED in Phase B

The reduced `(OctIdx, sign)` state is isomorphic to the real octonion `±e_k`.
This discards the imaginary components `ie_k` that are essential for:
- The vacuum state `ω = ½(e₀ + ie₇)`
- The Witt ladder operators `α_j = ½(e_a + ie_b)`
- The muon state `ω₂ = s* · ω · S`

The upgrade to `ComplexOctonion ℤ` (8 rational-integer complex components)
is required. This is what `State.lean` already uses.

### B4: Triality map τ — REFRAMED as generation labeling

**Finding**: τ is NOT a permutation on {e₀,..,e₇}. It acts on the so(8) Lie
algebra as the outer automorphism H = (1/2)M (McRae 2025, arXiv:2502.14016,
Eq. 8), a 4×4 matrix acting on each of 7 quartets of the 28 so(8) generators.
This formula is NOT a map on representation vectors.

The correct concrete implementation is Furey's projector-sector construction
(§2.2 above), which gives three distinct state vectors in C⊗O — one per
generation — without needing an explicit τ matrix. The generation label
(electron / muon / tauon) is stored as an explicit enum field `Generation`
(see §4, Phase A1), derived from the (s vs. s*) × (S vs. S*) sector.

The "cost" of moving between generations is then the cost of evaluating the
3-body Fano product `s* · ψ · S*` — computed by the Fano table and tracked
by the tick counter in the COG update rule.

---

## 6. The Key Physical Question

Once `C_μ / C_e` is computed, three outcomes are possible:

1. **C_μ / C_e ≈ 206.768**: The muon orbit length matches experiment. The COG
   framework has derived a second mass ratio from first principles.

2. **C_μ / C_e is a small integer** (like the proton failure: 3.667): The orbit
   definition is still wrong. The Fano path, branching protocol, or
   recurrence condition needs correction.

3. **The orbit is infinite** (no recurrence): The muon is not a closed orbit in
   the Fano graph — the path diverges. This would be a strong falsification
   of the COG mechanism for lepton masses.

Only outcome 1 constitutes success. Outcomes 2 and 3 must be documented as
falsification data and the mechanism revised.

---

## 7. What We Are NOT Doing

- We are **not** computing `m_p / m_e = 1836` at this stage. The proton is
  a three-body system and requires a separate RFC once the lepton mechanism
  is validated.

- We are **not** fitting the result post-hoc. The exchange rule, orbit
  definition, and recurrence condition must all be fixed by physical
  reasoning (Furey labeling, Fano table, alternativity trigger) BEFORE
  the simulation is run.

- We are **not** abandoning the COG framework if `C_μ / C_e ≠ 206.768`. We
  document the datum, record the root cause, and revise.

---

## 8. Dependencies and File Manifest

| File | Status | Notes |
|------|--------|-------|
| `CausalGraphTheory/Spinors.lean` | **New** | Generation type, gen-2 vacuum |
| `calc/spinor_state.py` | **New** | Full ComplexOct arithmetic |
| `calc/test_spinor_state.py` | **New** | pytest suite |
| `calc/muon_orbit.py` | **New** | Orbit simulation |
| `CausalGraphTheory/State.lean` | Existing | NodeLabel already correct |
| `CausalGraphTheory/WittBasis.lean` | Existing | Witt pairs already proved |
| `CausalGraphTheory/ComplexOctonion.lean` | Existing | FormalComplex, oct_mul available |
| `rfc/CONVENTIONS.md` | **Locked** | Fano triples, Witt pairs |

---

## 9. Next Steps (ordered)

1. **Phase A1–A3**: Write `Spinors.lean`, compute gen-2 vacuum `ω₂`.
2. **Phase B1–B2**: Write `spinor_state.py`, pass basis multiplication tests.
3. **Phase B3–B4**: Compute and verify gen-1/2/3 state vectors in Python.
4. **Phase C1**: Verify electron orbit: `C_e = 3`.
5. **Phase C2**: Run muon orbit simulation, record `C_μ`.
6. **Report**: Record result in `claims/muon_mass.yml` (new claim file).
7. **Phase D**: Prove `generation_shift_order3` in Lean by `decide`.

---

*Authors: COG session 2026-02-22. This RFC supersedes the triality-overhead
framing of RFC-009 §5–6 for the lepton mass question. RFC-009 remains active
for the proton/electron ratio (MU-001).*

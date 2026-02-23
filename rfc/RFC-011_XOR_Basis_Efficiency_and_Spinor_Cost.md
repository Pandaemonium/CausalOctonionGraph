# RFC-011: XOR Basis Primacy and Spinor Representation Overhead

**Status:** Open — Hypothesis with partial literature grounding
**Created:** 2026-02-22
**Module:** `COG.Algebra.XOR`, `COG.Particles.RepCost`
**Dependencies:** `rfc/CONVENTIONS.md` (locked), `rfc/RFC-009_Spinor_Representations_and_Triality_Overhead.md`
**Claims addressed:** KOIDE-001 (mechanism for lepton generation mass hierarchy)
**Upstream hypothesis:** Gemini synthesis, 2026-02-22

---

## 1. Executive Summary

This RFC investigates whether the 3-bit XOR structure of the octonion
multiplication table — which is already implicit in the locked Furey convention
of this project — provides a computational basis for the mass hierarchy of the
three lepton generations.

**The core hypothesis:**
> If the discrete causal graph universe operates natively using XOR-indexed
> octonion multiplication (the most efficient possible algebraic instruction),
> then any interaction that requires a triality-representation translation
> before and after the XOR step incurs computational overhead. That overhead,
> measured in elementary operations, is the origin of the muon and tau masses.

**What the literature establishes (grounded):**

1. The Furey convention used in this project IS the XOR basis
   (proved in §3, verified against `calc/conftest.py`).
2. The Fano plane lines under XOR labeling reproduce the Hamming (7,4)
   error-correcting code (Gunaydin et al. 2020, arXiv:2008.01494).
3. Octonions define the largest continuous family of equiangular projections
   and thereby a universal quantum computational scheme
   (Freedman, Shokrian-Zini, Wang 2018, arXiv:1811.08580).
4. The triality automorphism of SO(8) has a manifest $S_3 \times SO(8)$
   structure when written octionically (Schray & Manogue 1994,
   arXiv:hep-th/9407179). It is NOT a simple index permutation.

**What the literature does NOT establish:**

5. That the vector representation V is computationally "cheaper" than S+ or S-
   in a quantum computer. The universality result of Freedman et al. applies
   equally to all three triality representations.
6. That the triality translation costs exactly 206 or 3477 elementary
   operations. This is an open COG-specific claim.

The RFC closes by defining the specific computation needed to test the
hypothesis: decompose the triality automorphism into elementary XOR+sign
steps and count them.

---

## 2. Background: The XOR Structure of Octonions

### 2.1 The Standard Result

Label the 7 imaginary units $e_1, \ldots, e_7$ by their 3-bit binary
representations $001, 010, 011, 100, 101, 110, 111$. Then:

$$e_i \cdot e_j = \pm e_{i \oplus j} \quad \text{for } i \neq j$$

where $\oplus$ denotes bitwise XOR. The index of the product is simply the
XOR of the indices; only the sign requires additional information (a 7x7
lookup table with 42 non-zero entries, or equivalently 3 bits per pair).

This is a standard observation about the octonions under the
"binary basis" labeling. See e.g. Borsten et al. (2008, arXiv:0809.4685),
who use exactly this 3-bit labeling to map the 7 Fano vertices to
7-qubit quantum states with E_7 symmetry.

The most precise formalization appears in Rausch de Traubenberg & Slupinski
(2022, arXiv:2207.13946), who define a "composition factor" on the Fano
plane as a map $\phi: F \times F \to \{-1, +1\}$ subject to constraints
derived from the Fano incidence geometry. This map encodes EXACTLY the sign
table of the octonion multiplication: the index is the XOR, and $\phi(i,j)$
gives the sign. They prove that the composition factors are in bijection with
Fano-plane multiplication conventions (up to G_2 automorphisms), providing
the most direct mathematical grounding for "XOR + sign = complete octonion
product."

Dixon (1995, arXiv:hep-th/9503053) introduced the related X-product for
octonions, defined by $e_i \cdot e_j = \epsilon_{ijk} e_k$ where the index
triples $\{i,j,k\}$ are exactly the 7 lines of the Fano plane. The XY-product
variant extends this to include identity-permuting automorphisms.

Saniga (2015, arXiv:1509.06009) classifies all 30 labelings of the Fano
plane on a 7-element set, distinguishing "ordinary" lines (where the sum of
two smaller labels equals the third — the XOR-compatible labelings) from
"defective" ones. The Furey convention used in this project is an "ordinary"
labeling, confirming its XOR compatibility is not accidental.

### 2.2 Efficient Classical Implementation

Under XOR labeling, one octonion multiplication requires:
- **Index computation:** 1 XOR instruction (single clock cycle on any CPU)
- **Sign determination:** 1 table lookup (from a precomputed 7x7 bit array)
- **Coefficient accumulation:** standard scalar arithmetic

This is provably minimal: the index cannot be computed in fewer than 1
instruction, and the sign cannot be determined without at least 1 bit of
information per ordered pair. The XOR basis achieves both lower bounds
simultaneously.

**Comparison with matrix representation:** Representing the 7 imaginary
units as $8 \times 8$ real matrices requires 64 multiply-accumulate
operations per basis product — a factor of ~64 overhead versus XOR+lookup.

### 2.3 The Furey/COG Convention IS the XOR Basis

The locked Fano cycles in `rfc/CONVENTIONS.md` and `calc/conftest.py` are:

```
(1,2,3), (1,4,5), (1,7,6), (2,4,6), (2,5,7), (3,4,7), (3,6,5)
```

(physics indices, 1-indexed). Checking each triple against XOR:

| Triple (a,b,c)  | Binary a   | Binary b   | a XOR b  | c (expected) | Match |
|-----------------|-----------|-----------|---------|-------------|-------|
| (1, 2, 3)       | 001       | 010       | 011 = 3 | 3           | YES   |
| (1, 4, 5)       | 001       | 100       | 101 = 5 | 5           | YES   |
| (1, 7, 6)       | 001       | 111       | 110 = 6 | 6           | YES   |
| (2, 4, 6)       | 010       | 100       | 110 = 6 | 6           | YES   |
| (2, 5, 7)       | 010       | 101       | 111 = 7 | 7           | YES   |
| (3, 4, 7)       | 011       | 100       | 111 = 7 | 7           | YES   |
| (3, 6, 5)       | 011       | 110       | 101 = 5 | 5           | YES   |

**All 7 lines match XOR exactly.** The existing `calc/fano.py` implements
"XOR hardware" via a precomputed dictionary. There is no new code to write
here; the project already uses the optimal basis.

---

## 3. The Hamming (7,4) Code Identity

Gunaydin, Kallosh, Linde, Yamada (2020, arXiv:2008.01494) show that:

> "We propose octonion, Fano plane based superpotentials, codifying the
> error correcting Hamming (7,4) code."

The connection is exact and well-known in coding theory:

- The 7 imaginary units $e_1, \ldots, e_7$ correspond to the 7 bit positions
  of the Hamming (7,4) code.
- The 7 Fano lines correspond to the 7 parity-check equations.
- The XOR structure $e_i \cdot e_j = e_{i \oplus j}$ is precisely the
  syndrome computation for the Hamming code.

**Physical interpretation for COG:** Octonion multiplication under the XOR
basis is equivalent to Hamming parity checking. A single octonion product
is literally a parity check in the Hamming sense. This has two implications:

1. **Error detection:** The Hamming code detects all 1-bit errors and corrects
   all 1-bit errors. In COG, a single-hop interaction that changes one Fano
   index is maximally efficiently checked and corrected by the algebra itself.

2. **Efficient implementation:** Hardware Hamming encoders are single-clock-cycle
   XOR trees. If the COG graph engine uses Hamming arithmetic for its
   octonion multiplication step, each multiplication costs exactly 1 tick
   (the parity check). This is the formal grounding of the "1 tick per
   interaction in V" claim in RFC-009 §5.3.

---

## 4. Octonionic Quantum Computing (Freedman et al. 2018)

Freedman, Shokrian-Zini, and Wang (arXiv:1811.08580) construct a universal
quantum computational scheme from the octonions. Their key result:

> "The largest continuous family [of equiangular projections], in a sense
> made precise in Corollary 4.2, is associated with the octonions and this
> example leads to a universal computational scheme."

**What this establishes:** The octonion algebra supports a maximally rich
universal quantum computer. The V, S+, S- representations of SO(8) are all
present in this construction — they are NOT distinguished computationally
within the Freedman framework.

**What this does NOT establish:** That V is computationally cheaper than S+
or S-. The universality argument is symmetric under triality.

**COG interpretation:** The Freedman result grounds the claim that a
COG-style octonionic causal graph can in principle perform universal
quantum computation. It does not by itself explain why different
representations should cost different numbers of ticks.

---

## 5. Triality: Structure vs. Cost

### 5.1 The S_3 x SO(8) Structure (Schray & Manogue 1994)

Schray and Manogue (arXiv:hep-th/9407179) show that the triality automorphism
$\tau$ of SO(8) has a manifest $S_3 \times SO(8)$ structure when expressed
octionically. The three representations V, S+, S- are related by the order-3
outer automorphism $\tau: V \to S_+ \to S_- \to V$.

Crucially, $\tau$ is an **outer** automorphism — it cannot be implemented
by an inner conjugation (i.e., by any element of the octonion algebra itself).
This means:

1. Translating a V state to an S+ state is NOT just multiplication by some
   fixed octonion $a$. It requires a non-trivial structural transformation.
2. The transformation involves a permutation of the 8 basis elements
   **combined with sign changes** — it is not a pure XOR operation.

### 5.2 Explicit Form of Triality on the Octonions

Following McRae (2025, arXiv:2502.14016, Table 1), the triality automorphism
$\tau$ maps octonion basis elements as follows (one consistent choice):

```
tau(e0) = e0   (identity acts on real unit)
tau(e1) = ?    (permutes imaginary units non-trivially)
...
```

**Status:** The explicit matrix for $\tau$ on the 7 imaginary units requires
checking McRae Table 1 against our locked Fano convention
(see `rfc/CONVENTIONS.md §9` checklist). This has NOT been verified in COG
yet (RFC-010 Phase D is open).

### 5.3 What the COG Hypothesis Claims

RFC-009 §5.3 proposes:

> Moving within the same representation costs 0 extra ticks.
> Applying tau once (V -> S+, S+ -> S-, S- -> V) costs 1 extra tick.
> Applying tau twice costs 2 extra ticks.

This is a postulate, not a derivation. The testable version is:

> **Claim (COG-QC-01):** The triality automorphism tau, when decomposed
> into elementary XOR+sign operations on the 3-bit basis, requires exactly
> N_tau elementary steps. The mass ratio m_mu / m_e equals N_tau (or a
> simple function of it).

For this claim to explain the experimental ratio m_mu/m_e = 206.768, we
need N_tau ~ 207 (or a combination that gives 206.768 with C_e = 3 as a
multiplier).

---

## 6. The Sign Computation: A Candidate Mechanism

### 6.1 The XOR+Parity Split

Under XOR labeling, the full multiplication rule decomposes as:

```
e_i * e_j = sgn(i, j) * e_{i XOR j}

where sgn(i, j) = +1 or -1 depending on the ordered pair (i, j).
```

The index computation is free (XOR). The sign computation requires
a binary function on ordered pairs of 3-bit numbers. This binary function
is NOT a simple XOR of the indices; it is a non-linear parity function.

One way to compute the sign uses the concept of a "G2 structure" on the
7 imaginary units: the sign of $e_i \cdot e_j$ is determined by whether
the ordered triple $(i, j, i \oplus j)$ is a "positively oriented" or
"negatively oriented" Fano line.

### 6.2 Sign Computation Cost

In classical digital hardware, the sign of one product requires:
1. Look up the parity of the triple $(i, j, i \oplus j)$: 1 table access
2. Determine orientation from cyclic order: 1 comparison

This is 2 operations beyond the XOR index computation. Total cost of one
octonion basis product in XOR hardware: **1 XOR + 2 sign ops = 3 elementary
operations.**

Note: C_e = 3. This may not be coincidental. The electron orbit length of
3 might be the minimum cost for one complete basis-element interaction in
the V representation (1 XOR + 2 sign).

### 6.3 The Spinor Sign Table is Permuted

The triality automorphism tau acts on the sign table as a non-trivial
permutation. This means that when working in the S+ representation, the
sign table has different entries from the V sign table — it is a
"rotated" parity function.

**Consequence:** An S+ state cannot use the native XOR + sign-table lookup.
It must first apply tau to convert the indices, then look up in the V sign
table, then apply tau^{-1} to convert back. This is exactly the emulation
overhead of RFC-009 §5.3.

**The question becomes:** How many elementary XOR+sign operations does
applying tau once require?

### 6.4 The ±1/2 Entries as Native Bit-Shifts (Gemini note, 2026-02-22)

The true SO(8) outer triality matrix has entries of magnitude $1/2$, not
$\{0, \pm 1\}$ as a permutation matrix would. At first glance this seems to
require floating-point arithmetic — expensive and unnatural for a discrete
XOR-based universe.

**The resolution:** Division by 2 is a single bit-shift right (`>> 1`) on
binary hardware. Half-integer coordinates are natively computable as integer
shifts — no floating-point unit required.

This is not accidental. The $E_8$ lattice and $D_4$ root system, which
underlie the SO(8) spinor representations, always have their spinor roots at
half-integer coordinates — shifted by $\frac{1}{2}$ relative to the vector
representation roots. A universe that operates on integer bit-shift hardware
naturally represents spinors as one-bit-right-shifted integers.

**Revised cost table (Gemini, 2026-02-22):**

| Entry magnitude | Operations | Total |
|----------------|-----------|-------|
| $\pm 1$        | 1 XOR + 1 sign + 0 shift | 2 ops |
| $\pm 1/2$      | 1 XOR + 1 sign + 1 bit-shift | $C_e = 3$ ops |

If the true $\tau$ matrix has all entries of magnitude $1/2$ (consistent with
$D_4/E_8$ spinor structure), then $C_e = 3$ applies uniformly to every
non-zero entry. The constant $C_e = 3$ thus has a direct physical
interpretation: **it counts the three primitive hardware operations needed to
compute one spinor basis-element interaction.**

---

## 7. Testable Claim and Action Items

### 7.1 Claim COG-QC-01 (Open)

**Statement:** The triality automorphism $\tau$, decomposed into elementary
XOR+sign operations on the 3-bit octonion basis, requires exactly $N_\tau$
steps. The muon-to-electron mass ratio satisfies:

$$\frac{m_\mu}{m_e} = \frac{C_e + N_\tau \cdot C_e}{C_e} = 1 + N_\tau$$

or some analogous formula involving $C_e = 3$ and $N_\tau$.

**Why this matters:** If $N_\tau = 206$, the muon mass ratio is explained
purely by the overhead of one triality translation. If $N_\tau$ is a small
number (e.g., 7 or 21), the claim fails and an alternative mechanism is needed.

### 7.2 Action Item A: Implement Triality Explicitly

Write `calc/triality_map.py`:

1. Load the locked Fano convention from `calc/conftest.py`.
2. Implement the triality automorphism $\tau$ as a function
   `tau(state: np.ndarray) -> np.ndarray` on the 8-dimensional state space.
   **Tau is an $8 \times 8$ real orthogonal matrix, NOT a simple index
   permutation.** Applying $\tau$ to a unit basis vector yields a
   superposition of basis vectors, typically with $\pm 1/2$ coefficients
   arising from the D4/E8 lattice structure (Gemini feedback, 2026-02-22).
3. Verify $\tau^3 = I_8$ using `np.allclose(T @ T @ T, np.eye(8))`.
4. Count the minimum number of elementary XOR+sign operations needed to
   compute one application of $\tau \cdot x$ for an 8-component state $x$.
   Each row of $\tau$ with $k$ non-zero entries of magnitude $1/2$ requires
   at minimum $k$ XOR+sign+shift operations. The total is $N_\tau$.

**Correction from Gemini (2026-02-22):** The original draft specified
`tau(state: int) -> int`, which is mathematically incorrect. Tau is a
_linear map_ on $\mathbb{R}^8$, not an index permutation. The $\pm 1/2$
entries arise from the intertwining operator between the V and S+
representations of SO(8). A permutation-only tau would give entries in
$\{0, \pm 1\}$ and correspond to an inner automorphism (G2 element), not
the outer triality automorphism of SO(8).

**Reference for the explicit matrix:** McRae (2025, arXiv:2502.14016),
Section 2.3 (Euclidean) or Section 4.3 (Lorentzian, equation 23). The
matrix acts on _quartets of Lie algebra generators_, not directly on the
8-dimensional state space. The state-space intertwiner must be derived from
the Clifford algebra generators in McRae §2.2 via the constraint
$T \cdot V_{ij} \cdot T^{-1} = L_{H(ij)}$ for all 28 generator pairs.
Must be checked against `rfc/CONVENTIONS.md §9` before use.

### 7.3 Action Item B: Verify N_tau Numerically (CSE-optimized)

Once `tau` is implemented, the naive count `count_xor_sign_ops(T)` is only an
**upper bound**: it counts $C_e$ per non-zero entry independently. The true
$N_\tau$ must use **common sub-expression elimination (CSE)** (Gemini note,
2026-02-22).

**Why CSE matters:** If $\tau[i_1, j]$ and $\tau[i_2, j]$ both draw from the
same source column $j$ with the same magnitude, the hardware computes the
scaled value once and deposits it into two output rows. Sign flips are free
(a single bit complement). This is the *straight-line program* (SLP)
optimization for fixed-matrix vector multiplication — a standard technique
in computer algebra and circuit synthesis.

**Algorithm for `count_circuit_depth_cse(T)`:**

```python
def count_circuit_depth_cse(T: np.ndarray) -> tuple[int, dict]:
    """
    Group non-zero entries by (source_column, magnitude).
    Each unique (col, mag) pair is ONE hardware computation, shared across
    all output rows that use it (with free sign flips).
    CSE cost = C_e * (number of unique (col, mag) groups).
    """
    unique_sources = {(j, round_to_half(abs(T[i,j])))
                      for i, j in nonzero_indices(T)}
    return C_e * len(unique_sources), ...
```

For the G2 permutation (each column has exactly 1 non-zero entry):
`unique_sources` has 8 elements → CSE cost = 24 (same as naive, no savings).

For the true τ with 4 non-zero entries per column at magnitude 1/2:
`unique_sources` has 8 elements → CSE cost = 24.  But 8 rows × 4 entries
= 32 non-zero entries → naive cost = 96.  **CSE reduces 96 → 24.**  The
true $N_\tau$ may be much smaller than the naive count suggests.

**Implementation in `calc/triality_map.py`** provides three levels:

| Function | Method | Model |
|----------|--------|-------|
| `count_xor_sign_ops(T)` | $C_e \times$ n_nonzero | **Upper bound** |
| `count_circuit_depth_cse(T)` | $C_e \times$ unique (col, mag) groups | **Intermediate** |
| `count_circuit_depth_greedy(T)` | Greedy pair CSE + bit-shifts | **Tightest arithmetic lower bound** |

The greedy algorithm (Gemini, 2026-02-22) does two things the column CSE does not:
1. **Row-level bit-shift**: if every non-zero entry in a row has magnitude $1/2$,
   the entire row shares one `>> 1` tick (not one per entry).
2. **Cross-row pair sharing**: if $x_i + x_j$ appears in multiple rows, it is
   computed once as an intermediate register, like a Walsh-Hadamard butterfly
   stage.

`report_ntau(T)` reports all three counts. The **greedy N_tau is the figure to
check against $m_\mu/m_e - 1 = 205.768$** once the true SO(8) tau matrix is
available.

### 7.4 Action Item C: Update RFC-009 Based on Result

- If $N_\tau$ gives the muon mass: promote COG-QC-01 to a proved claim,
  update `claims/muon_mass.yml` (LEPTON-001) to `status: proved`.
- If $N_\tau$ does not give the muon mass: document as falsification,
  update the claims file to `status: blocked` with notes.

---

## 7b. Prior Work: The Furey Programme (COG Foundations)

The following papers define the algebraic foundations that RFC-001 and
RFC-010 of this project build on. They are listed here for completeness
and to connect RFC-011 to the broader literature stream.

| Citation | arXiv ID | Content |
|----------|----------|---------|
| Furey (2016) — thesis | 1611.09182 | Derives one SM generation from left ideals of C⊗O. Origin of the s, S* projector construction used in Spinors.lean. |
| Furey & Hughes (2022a) | 2209.13016 | Single copy of R⊗C⊗H⊗O encodes all Weyl representations of one generation without fermion doubling. |
| Furey & Hughes (2022b) | 2210.10126 | Division algebraic symmetry breaking Spin(10) → SM. Derives L-R symmetric Higgs from octonionic triality. |
| Furey (2025) | 2505.07923 | SM gauge bosons + three fermion generations form a $Z_2^5$-graded superalgebra isomorphic to $H_{16}(\mathbb{C})$. Most recent. |
| Todorov (2022) | 2206.06912 | Octonion internal space algebra for SM. Derives $m_H/m_W$ from the theoretical Weinberg angle. |

Note: RFC-010 (Gen labels and muon state) cites Furey (2019) arXiv:1910.08395
for the specific charged lepton state vectors. The 2025 Furey paper
(2505.07923) extends this to all three generations simultaneously; it should
be read before attempting Phase C of RFC-010.

---

## 8. Literature Summary Table

| Citation | arXiv ID | Relevance to COG-QC-01 | Status |
|----------|----------|------------------------|--------|
| Freedman, Shokrian-Zini, Wang (2018) | 1811.08580 | Octonions = universal QC via equiangular projections. Grounds octonionic computation as a valid model. | Grounded |
| Gunaydin, Kallosh, Linde, Yamada (2020) | 2008.01494 | Fano plane = Hamming (7,4) code. XOR multiplication = Hamming parity check. | Grounded |
| Schray & Manogue (1994) | hep-th/9407179 | Triality is S3 x SO(8) structure in octonionic language. NOT a simple permutation. | Grounded |
| Borsten et al. (2008) | 0809.4685 | 7 Fano vertices = 7-qubit system with 3-bit labels. E7 structure. | Grounded |
| Rausch de Traubenberg & Slupinski (2022) | 2207.13946 | "Composition factor" = signed XOR table. Most direct formalization of XOR+sign as complete octonion product. All g_2 brackets derived from Fano incidence. | Grounded |
| Dixon (1995) | hep-th/9503053 | X-product: e_i * e_j = eps_{ijk} e_k with Fano indices. Earliest explicit XOR-structure reference. | Grounded |
| Saniga (2015) | 1509.06009 | All 30 Fano labelings. "Ordinary" (XOR-compatible) vs. "defective." Furey convention is ordinary. | Grounded |
| Gunaydin et al. (2020) | 2008.01494 | Fano plane = Hamming (7,4) code. XOR multiplication = Hamming parity check. | Grounded |
| da Rocha & Vaz (2006) | math-ph/0603053 | Cl(0,7)-parametrized octonion products; triality maps and G2 actions as computational outputs. | Context |
| McRae (2025) | 2502.14016 | Explicit H=(1/2)M triality matrix in C⊗O. Needed for Action Item A. | Not yet verified vs. CONVENTIONS.md |
| Liu Yu-Fen (2001) | math-ph/0109008 | Vector representation of Dirac equation via triality. | Context |
| RFC-009 §5.3 (this project) | — | Triality overhead = 0/1/2 ticks by postulate. COG-QC-01 is the derived version. | Open |

---

## 9. Open Questions

| # | Question | Blocking |
|---|----------|---------|
| 9.1 | What is $N_\tau$ for the locked Furey convention? | COG-QC-01 |
| 9.2 | Does $1 + N_\tau \approx m_\mu / m_e$? | LEPTON-001 |
| 9.3 | Does $\tau^2$ cost $2 N_\tau$ or $N_\tau$? Since $\tau$ is orthogonal, $\tau^2 = \tau^{-1} = \tau^T$. Transposing exchanges rows ↔ columns; the CSE structure may differ. Compute $N_\tau^{\text{CSE}}$ for both $\tau$ and $\tau^T$ explicitly. If symmetric: $V \to S_-$ costs the same as $V \to S_+$ (unlikely to match tau lepton 3477). If asymmetric: the Fano sign conventions may break CSE symmetry, giving $\tau^T$ a different depth — a natural mechanism for the tau/muon mass ratio. | Tau mass |
| 9.4 | Is the Freedman universality result specific to V, or equally valid for S+/S-? | QC model |
| 9.5 | Does the COG graph engine need to explicitly implement tau, or does it emerge from the exchange schedule? | Architecture |

---

## 10. Dependency Graph

```
RFC-001 (Fano algebra, locked)
    |
    +--> RFC-009 §5 (Triality overhead postulate)
    |        |
    |        +--> RFC-011 (this: grounds XOR efficiency, defines N_tau test)
    |                 |
    |                 +--> calc/triality_map.py  [Action Item A]
    |                 |        |
    |                 |        +--> claims/muon_mass.yml (LEPTON-001) [update]
    |                 |
    |                 +--> RFC-010 Phase D (tau order-3 Lean proof)
    |
    +--> RFC-010 (Rep labels, Spinors.lean)
```

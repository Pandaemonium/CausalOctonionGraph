# RFC-061: The Fine Structure Constant from Fano Automorphism Counting

Status: Stub — Exploratory / High-Risk (2026-02-26)
Module:
- `COG.Core.AlphaDerivation`
Depends on:
- `rfc/RFC-039_Charge_as_Discrete_Z4_Cycle.md`
- `rfc/RFC-041_Charge_Operator_Reconciliation.md`
- `rfc/RFC-052_Scale_Calibration_from_Graph_Units.md`
Literature basis:
- Wyler (1969): α from symmetric spaces
- Gillaspy and Schwob (1999): most precise experimental value of α
- Atiyah (2018): Todd function derivation of α (controversial)

---

## 1. Executive Summary

The fine structure constant $lpha pprox 1/137.036$ is the most famous
unexplained constant in physics. It sets the strength of the electromagnetic
interaction. Feynman called it “one of the greatest damn mysteries of physics.”

In COG, the electromagnetic interaction strength is determined by the update
rule D3 gate when two charged nodes exchange energy. The question is whether
$lpha$ can be expressed as a pure ratio of integer quantities arising from
the octonion/Fano algebra — with no free parameters.

This is **high-risk**: multiple attempts by serious mathematicians have
produced numerically close results that turned out to be coincidences.
The RFC documents the approaches, their status, and the COG-specific search.

---

## 2. The Known Attempts

### 2.1 Wyler’s formula (1969)

Wyler derived:

$$lpha_W = rac{9}{8\pi^4} \left(rac{\pi^5}{2^4 \cdot 5!}ight)^{1/4}
= rac{1}{137.0360...}$$

from the ratio of volumes of symmetric spaces $D_5/D_4 	imes D_1$ in
5-dimensional anti-de Sitter space. The derivation uses:
- $D_5 = SO(10)/U(5)$: the 5D ball (spin-1/2 electrons live here)
- $D_4 = SO(8)/U(4)$: the 4D ball (photons live here)

The numerical agreement is remarkable (matches experiment to 6 decimal places
at the time). However, the physical interpretation was unclear and Wyler’s
approach fell out of favor.

**COG connection:** $D_5$ and $D_4$ are real forms of exceptional spaces
related to the octonion structure. $SO(8)$ has an exceptional triality
symmetry related to $G_2 = 	ext{Aut}(\mathbb{O})$.

### 2.2 Atiyah’s attempt (2018)

Atiyah proposed deriving $lpha$ from the “Todd function” $T$, a power series
arising from the $\hat{A}$-genus in algebraic topology. The claim was that
the “inverse fine structure constant” $j(T) = 137.035...$. This was not
accepted by the community as a valid derivation.

### 2.3 Group-theoretic counting

Order of $GL(3,2) = 	ext{Aut}(	ext{Fano plane}) \cong PSL(2,7)$: **168**

Note: $168 = 8 	imes 21 = 168$. And $137 = 168 - 31 = ?$ No obvious connection.

Other potentially relevant numbers:
- $|G_2(\mathbb{F}_2)| = 12096 = 168 	imes 72$
- Number of octonion units: 8 (or 7 imaginary)
- Number of Fano lines: 7
- $7 	imes 137 = 959 = ?$ No obvious connection.
- $8 	imes 17 = 136$, $8 	imes 17 + 1 = 137$. Coincidence?

**COG hypothesis:** $lpha^{-1}$ may involve the ratio of orbit sizes
under the $G_2$ or $GL(3,2)$ action on the Fano plane, combined with
the Z4 cycle period (RFC-039).

---

## 3. COG Search Strategy

### 3.1 Phase 1: Enumerate plausible expressions

Search the space of rational functions of:
- $\pi$ (from continuous Lie group volumes)
- 7, 8, 21, 168, 336 (Fano/G2 group orders)
- 4 (Z4 cycle period)
- The Clifford algebra dimension: 64 (= $2^6$)

Target: $f(\pi, 7, 8, ...) = 137.036...$

### 3.2 Phase 2: Wyler revisited in COG language

Wyler’s formula uses $SO(8)$ and $SO(10)$, which are related to octonion
triality ($SO(8)$ has an exceptional triality automorphism of order 3, see
Furey-Hughes 2024 and triality in Baez 2002).

Map Wyler’s spaces to COG structures:
- $D_4 = SO(8)/U(4)$: related to the 4-fold Witt structure in C⊗O?
- $D_5 = SO(10)/U(5)$: related to C⊗H⊗O (32-dim, one generation)?

### 3.3 Falsification criterion

Any candidate expression $f$ must:
1. Match $lpha^{-1}$ to at least 6 significant figures.
2. Have a physical interpretation (not be a numerical coincidence).
3. Predict how $lpha$ runs with energy scale (the running coupling
   $lpha(Q)$ in QED), even if only qualitatively.

If no such expression is found after exhaustive search, document this as
a **negative result**: $lpha$ may not have a simple algebraic origin
in the Fano/octonion structure.

---

## 4. Implementation Targets

### Python
- `calc/alpha_search.py`: systematic search over rational functions
  of COG group-theoretic quantities
- `calc/wyler_revisited.py`: compute Wyler formula, identify each factor
  in COG/octonion terms
- `calc/test_alpha_search.py`: verify search correctness, reproducibility

### Lean (long-term, only if a candidate formula is found)
- `CausalGraphTheory/AlphaDerivation.lean`
- If a formula is found: formalize the derivation

---

## 5. Risk Assessment

| Risk | Likelihood | Impact |
|------|-----------|--------|
| No algebraic expression found | Medium | Negative result (still valuable) |
| Expression found but numerically fortuitous | High | Must pass running-alpha test |
| Expression found with physical interpretation | Low | Would be major result |
| Wyler-like formula derived in COG language | Medium | High — would revive Wyler program |

---

## 6. Sources

1. Wyler (1969), *L’espace symétrique du groupe des équations de Maxwell*,
   C.R. Acad. Sci. Paris A269, 743-745
2. Gillaspy and Schwob (1999), experimental value of $lpha$,
   Phys. Rev. Lett. 82, 4960
3. Atiyah (2018), *The fine structure constant*, preprint
4. Feynman (1985), *QED: The Strange Theory of Light and Matter*, Ch. 4
5. Baez (2002), *The Octonions*, §4.1 (triality and $SO(8)$)
   https://arxiv.org/abs/math/0105155
6. Furey and Hughes (2024), *Three generations from triality*
   https://arxiv.org/abs/2409.17948

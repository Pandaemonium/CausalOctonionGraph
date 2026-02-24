# Causal Octonion Graph (COG)

> **Deterministic Physics at the Planck Scale.** 
> 
> 
> 
> 
> What if the universe is not an infinitely divisible continuum of spacetime, but a discrete, self-computing algorithm driven by the pure symmetries of the normed division algebras?

The **Causal Octonion Graph (COG)** project is a rigorous, machine-verified framework aimed at deriving the structure of the Standard Model directly from discrete, non-associative algebra over causal graphs.

By abandoning continuous real numbers (ℝ) and probabilistic wave functions, we replace quantum field theory with a computable engine where fundamental particles are algebraic state vectors in ℂ⊗𝕆, and "time" emerges strictly from the forced sequential ticking of non-associative octonionic operations.

---

## The Core Hypothesis

Our work builds heavily on the algebraic constructions of Cohl Furey and others, restricting physics purely to the division algebras acting on themselves. There are no arbitrary matrices or column vectors here. We are proving that gauge symmetries, particle generations, and even mass (as algorithmic computational drag) fall out inevitably from the discrete combinatorics of the Fano plane.

## Current State: The Lean 4 Kernel

We are currently building the foundational mathematical kernel. Our `CausalGraphTheory/` library is **completely sorry-free and fully verified** in Lean 4.

### Key Verified Theorems 

We have successfully formalized the following physical and mathematical foundations:

* **The Fano Plane Axioms:** Verified projective geometry (7 points, 7 lines, precise incidence axioms).
* **Octonion Alternativity:** Proved left/right alternativity and flexibility over any commutative ring.
* **Octonion Non-Associativity:** Explicit witness formalized showing (e₁e₂)e₄ ≠ e₁(e₂e₄). *(The engine of emergent time).*
* **The Sterile Vacuum:** Verified the idempotent vacuum state ω = ½(1+ie₇) where ω² = ω.
* **Vacuum Annihilation:** Proved that all three Witt lowering operators annihilate the vacuum: αⱼ·ω = 0 for j = 0, 1, 2.

### Repository Structure

| Module | Core Function |
| --- | --- |
| `Fano.lean` | Fano plane geometry and strict incidence axioms. |
| `FanoMul.lean` | Octonion basis multiplication derived directly from the Fano sign table. |
| `Octonion.lean` | Octonion algebra formalized over any CommRing. |
| `OctonionAlt.lean` | Left/right alternativity and flexibility proofs. |
| `ComplexOctonion.lean` | Formalization of the ℂ⊗𝕆 sector (avoiding `Mathlib`'s continuous Reals). |
| `WittBasis.lean` | Witt ladder operators, the vacuum idempotent, and annihilation proofs. |

---

## Getting Started

We use `lake` to build the project and `elan` for toolchain management.

```bash
# 1. Install elan (Lean version manager)
curl https://elan-init.org/ -sSf | sh

# 2. Clone the repository
git clone https://github.com/YOUR-USERNAME/CausalGraphTheory.git
cd CausalGraphTheory

# 3. Fetch the Mathlib cache (Saves hours of local compilation!)
lake exe cache get

# 4. Build the formalizations
lake build

# 5. Run Python checks (recommended)
python -m pip install -e .[dev]
python -m pytest -q

```

---

## Call for Contributors

We are actively looking for collaborators to help expand the graph! Whether you are a Lean 4 tactician, a Python simulation hacker, or a theoretical physicist, there are massive open problems to tackle:

* **Lean 4 Formalizers:** We need help formalizing the SO(8) Triality automorphism mapping and proving that the subgroup stabilizing the vacuum axis has exactly order 24 (the SL(2,3) generation symmetry group).
* **Python/NumPy Developers:** We are building adjacent causal graph simulators in Python to calculate the exact algorithmic drag (mass ratios) of the Muon and Tau generation translations.
* **Physicists:** Help us construct the algebraic proofs for charge quantization and anomaly cancellation using strictly discrete topology.

**Read before contributing:** All sign conventions, directed Fano triples, Witt pairings, and the chosen vacuum axis are strictly locked in our source of truth document: [`rfc/CONVENTIONS.md`](rfc/CONVENTIONS.md).

---

*License: MIT*

---

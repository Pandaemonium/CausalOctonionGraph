# RFC-007: Derivation of Fundamental Constants

**Status:** Draft
**Created:** 2026-02-22
**Module:** `COG.Constants.Derivation`
**Dependencies:** `COG.Core.State`, `COG.Core.Dynamics`, `COG.Algebra.ComplexOctonions` (DEF-001)

## 1. Executive Summary
If the Causal Octonion Graph (COG) hypothesis is correct, the universe is a purely algebraic graph computing itself without any free parameters. Standard quantum field theory requires manually plugging $\approx 26$ arbitrary constants into equations to match reality. In our framework, these values must emerge naturally.

The goal of this RFC is to map out the theoretical and computational pathways to derive the empirical constants of the Standard Model directly from the geometric and topological properties of the $\mathbb{C} \otimes \mathbb{O}$ algebra and the Fano plane. Instead of inputs, constants like the fine-structure constant and particle masses must be derived as dimensionless geometric ratios, topological phase-shift penalties, or algorithmic computational drag coefficients.

---

## 2. The Dimensionless Couplings (Graph Topology)
Coupling constants dictate the probability of causal edges successfully routing through specific subalgebras.



### 2.1 The Fine-Structure Constant ($\alpha$)
* **Empirical Value:** $\alpha \approx 1/137.035999$ (CODATA 2022)
* **COG Interpretation:** Represents the fundamental topological phase-shift penalty of the $U(1)$ electromagnetic interaction. 
* **Derivation Goal:** Compute $\alpha$ purely from the volume of the gauge group's discrete mathematical shadow within the $\mathbb{C} \otimes \mathbb{O}$ graph. 

### 2.2 The Strong Coupling Constant ($\alpha_s$)
* **COG Interpretation:** The statistical ratio of operations trapped within the 24-element vacuum stabilizer (the discrete $SU(3)$ color-cycle) versus operations escaping into the broader 168-element $GL(3,2)$ graph.
* **Derivation Goal:** Formally prove the exact combinatorial limit of this ratio as the causal graph size approaches infinity.

### 2.3 The Weinberg Angle ($\theta_W$)
* **Empirical Value:** $\sin^2 \theta_W \approx 0.23122$ (at the $Z$-pole)
* **COG Interpretation:** The precise geometric projection ratio between the quaternionic subalgebra ($\mathbb{H}$, handling $SU(2)$) and the complex subalgebra ($\mathbb{C}$, handling $U(1)$).

---

## 3. Algorithmic Drag Ratios (Masses)
In COG, mass is not an inherent object property but rather the computational frequency of forced sequential ticks (the Alternativity Trigger). Mass ratios are exactly the algorithmic overheads of maintaining specific repeating subgraphs (motifs).

### 3.1 Proton-to-Electron Mass Ratio ($\mu$)
* **Empirical Value:** $\mu \approx 1836.152673$ (CODATA 2022)
* **COG Interpretation:** An electron is a single node cycling through a cleanly associative subalgebra. A proton is a highly complex, 3-node color-singlet cycle constantly exchanging $SU(3)$ edges. 
* **Derivation Goal:** Prove that maintaining a stable octonionic tri-state cycle requires exactly $\sim 1836$ extra evaluation ticks compared to a single propagating lepton state.



### 3.2 Fermion Generation Ratios (The Koide Limit)
* **Empirical Values:** $m_e \approx 0.511$ MeV, $m_\mu \approx 105.658$ MeV, $m_\tau \approx 1776.93$ MeV. The Koide formula yields exactly $\frac{m_e + m_\mu + m_\tau}{(\sqrt{m_e} + \sqrt{m_\mu} + \sqrt{m_\tau})^2} = \frac{2}{3}$.
* **COG Interpretation:** The computational penalty of shifting representations via $SO(8)$ Triality ($V \to S_+ \to S_-$). The exact 2/3 ratio suggests an underlying rigid geometry governing generation mixing.
* **Derivation Goal:** Simulate the algorithmic drag of generation translations and match the observed Muon/Electron and Tau/Electron ratios.

---

## 4. Dimensional Artifacts (Emergent Limits)
These constants are human artifacts based on arbitrary macroscopic units (meters, seconds, kilograms). We cannot derive their numerical values, but we *can* derive their roles as the absolute bounds of the computing engine.

### 4.1 The Speed of Light ($c$)
* **COG Interpretation:** The hardware limit of the universe. $c \equiv 1$ node-hop per 1 algorithmic tick. It is the absolute maximum propagation speed of causality through the Directed Acyclic Graph.

### 4.2 Planck's Constant ($h$)
* **COG Interpretation:** The minimum data packet. Represents exactly one discrete algebraic state transition in the $\mathbb{C} \otimes \mathbb{O}$ algebra.



### 4.3 The Gravitational Constant ($G$)
* **COG Interpretation:** An emergent thermodynamic limit. If dense particle motifs are "hot spots" of computation (high node-update frequency), $G$ is the statistical proportionality constant dictating how these clusters warp the routing of surrounding vacuum edges.

---

## 5. Agent Implementation Tasks

### Task 5.1: The Lean Formalizer (`lean/COG/Constants/Coupling.lean`)
* Formalize the geometric ratio between the 24-element $SU(3)$ stabilizer and the 168-element $GL(3,2)$ Fano automorphism group.
* Define the exact topological phase shift in $\mathbb{C} \otimes \mathbb{O}$ to bound the value of $\alpha$.

### Task 5.2: The Python Simulator (`calc/mass_drag.py`)
* Build a Monte Carlo simulation tracking the update ticks of the $V$, $S_+$, and $S_-$ representations. 
* Write an automated test `test_koide_limit()` that asserts the simulated drag ratio of the three states approaches the Koide equation limit of $2/3$.

### Task 5.3: The Skeptic / Red Team (`rfc/RFC-005_Objections.md`)
* **Attack Vector 1:** The "Running" of Constants. If $\alpha$ and $\sin^2 \theta_W$ are fixed geometric ratios in the Fano plane, how does the DAG account for the fact that these constants change ("run") depending on the energy scale of the interaction?
* **Attack Vector 2:** Prove that the derived $\mu \approx 1836$ is mathematically robust and not just a numerical coincidence mined by over-parameterizing the Python simulation's graph update rules.

---
**Author Notes / Scratchpad:**
*(Energy scale in a causal graph is just inverse topological distance/graph density. High energy = short graph paths. The constants shouldn't fundamentally "run" in the continuum sense—rather, the discrete granular effects of the Fano cycles become visible at short distances, breaking the macroscopic continuum approximation.)*
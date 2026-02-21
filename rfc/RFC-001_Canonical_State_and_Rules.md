# RFC-001: The Canonical State and Algorithmic Update Rules (Phase I)

**Status:** Draft  
**Module:** `COG.Core.State` & `COG.Core.Dynamics`  
**Dependencies:** `COG.Algebra.ComplexOctonions` (DEF-001)  

## 1. Executive Summary
To replace the continuous wave function of standard quantum mechanics, the Causal Octonion Graph (COG) requires a discrete, computable data structure. This RFC defines the canonical representation of the universe's total information (the State) and the strict topological triggers that force that state to evaluate forward (the Update Rules). 

The goal of this RFC is to define the exact mathematical signatures needed by the Lean formalizer and the Python graph simulator.

---

## 2. The Canonical State ($G$)
The universe is not a manifold of points; it is a Directed Acyclic Graph (DAG) of algebraic events. We must define the state without reference to a global background time parameter $t$.



### 2.1 Nodes (The Fermionic States)
A node $N$ represents a discrete fermionic state. It possesses no spatial $(x, y, z)$ coordinates.
* **Data Type:** An element of the $\mathbb{C} \otimes \mathbb{O}$ algebra (e.g., $V$, $S_+$, or $S_-$ representation).
* **Properties:** A node is entirely defined by the sequence of octonionic ladder operators (the Witt basis) that have been applied to the sterile vacuum $v$.

### 2.2 Edges (The Gauge Operators)
An edge $E$ represents a causal interaction (a gauge boson) transferring algebraic instructions between nodes.
* **Data Type:** A directed edge carrying a specific algebraic operator ($U(1)$ phase shift, $SU(3)$ color rotation, etc.).
* **Properties:** Edges establish the topological distance between nodes. Distance $d(A, B)$ is exactly the minimum number of sequential edge-hops required to route a signal from $A$ to $B$.

### 2.3 The Global Graph
The total state $G$ is the set of all Nodes and Edges. 
* **Open Question for Formalizer:** Should $G$ be represented as a massive, sparse adjacency matrix, or purely as a list of localized parent-child node relationships to enforce strict locality?

---

## 3. The Algorithmic Update Rules (The Engine of Time)
Time does not tick universally. "Time" is the local, forced evaluation of a node when it encounters a computational bottleneck.



### 3.1 Associative Batch Processing (Timelessness)
If a node receives multiple incoming edges (e.g., $U(1)$ virtual photons) that lie within a common associative subalgebra (like $\mathbb{C}$ or $\mathbb{H}$), the order of evaluation does not matter.
* **Rule:** The simulator batch-processes these interactions as a single topological event. No sequential "ticks" are generated. Macroscopically, this manifests as quantum superposition.

### 3.2 The Alternativity Trigger (The Origin of the Tick)
The fundamental engine of time is non-associativity. 
* **Rule:** If a node receives incoming edges that span independent, non-associative axes of the Fano plane (e.g., a 3-body QCD color interaction), the Alternativity Theorem states the operations cannot be batched.
* **Action:** The universe is forced to execute a binary evaluation tree. This sequential ordering of operations generates the localized "ticks" of time.

---

## 4. Agent Implementation Tasks

### Task 4.1: The Lean Formalizer (`lean/COG/Core/State.lean`)
* Define the `inductive GraphState` type.
* Write the formal definition for topological distance $d(A, B)$ relying purely on edge-counting, strictly avoiding $\mathbb{R}$.

### Task 4.2: The Python Coder (`calc/graph_updater.py`)
* Build a toy model using `NetworkX`.
* Initialize a graph with 5 nodes in the $V$ representation.
* Write an `update_step()` function that scans the graph, identifies associative vs. non-associative edge overlaps, and accurately increments a "local tick counter" only for the non-associative nodes.

### Task 4.3: The Skeptic / Red Team (`rfc/RFC-001_Objections.md`)
* **Attack Vector 1:** If time is purely local, how do macroscopic regions of the graph maintain the illusion of synchronized Lorentz covariance without a global clock? 
* **Attack Vector 2:** Look for race conditions in the DAG. If Node A and Node B are spacelike separated but both route edges to Node C, how does Node C resolve the order of arrival without a background metric?

---
**Author Notes / Scratchpad:**
*(Write your initial thoughts on resolving the Red Team's Attack Vector 2 here before assigning to agents.)*
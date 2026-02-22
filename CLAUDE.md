# GEMINI.md: The Causal Octonion Graph (COG) Workspace

## 1. Project Orientation & The Prime Directive
Welcome to the COG repository. Our objective is to rigorously derive the Standard Model and the bound state of hydrogen without relying on continuous spacetime, infinite divisibility, or the real number line ($\mathbb{R}$). 

**The Prime Directive: The Continuum is an Illusion.**
In this workspace, you must abandon continuous fields, differential equations, and probabilistic wave functions. You are building a deterministic universe where:
* **Reality is a directed, acyclic graph (a causal graph).**
* **Nodes** are discrete state vectors built on the normed division algebras (specifically the complex-octonionic sector $\mathbb{C} \otimes \mathbb{O}$).
* **Edges** are causal interactions carrying rigid algebraic operators.
* **Time** is not a background dimension; it is the forced sequential ticking that emerges explicitly from the non-associativity of the octonions (the Alternativity Theorem).
* **Mass** is equivalent to computational drag/frequency of forced evaluation ticks.

## 2. Gemini Tool Usage Strategy & Code Modification Rules
As an AI agent operating in this codebase, your highest risk to the project is "edit drift"—the accidental deletion of nuanced logic, imports, or established proofs through careless overwriting.

**CRITICAL: You are strictly forbidden from executing whole-file rewrites.**
When modifying files, you must adhere to the following protocols:
1.  **Targeted Edits Only:** Use surgical diffs, AST-level modifications, or precise search-and-replace blocks. Never overwrite the entire contents of a file just to change a few lines.
2.  **Preserve Context:** Before altering a Lean proof or Python script, read the existing imports and helper functions. Do not orphan existing code.
3.  **One Concept Per File:** Keep Lean files and test scripts extremely short. If a file is growing too large, split the lemmas or tests into smaller, modular files.
4.  **Halt on Confusion:** If a Lean tactic fails or a mathematical derivation reaches a paradox, do not endlessly guess or rewrite the file. Stop, document the failure in the `notes` section of the corresponding YAML claim, and flag it as `blocked` for human review.

## 2b. Algebraic Convention Lock
All Lean and Python code MUST use the Furey convention as defined in `rfc/CONVENTIONS.md`. This document is **locked** — do not modify its directed triples, sign tensor, Witt basis pairings, or vacuum axis without explicit human approval.

**Non-negotiable rules:**
* The 7 directed cyclic triples are defined in `rfc/CONVENTIONS.md` §2. Do not invent, reorder, or "fix" them.
* The Witt basis pairs $(e_6, e_1)$, $(e_2, e_5)$, $(e_3, e_4)$ with vacuum axis $e_7$ are locked.
* Python code must import convention constants from `calc/conftest.py` (`FANO_CYCLES`, `FANO_SIGN`, `FANO_THIRD`, `WITT_PAIRS`, `VACUUM_AXIS`), never redefine them locally.
* Lean code must define `fanoCycles` to match the same 7 triples and derive all sign/multiplication tables from them programmatically.
* Before merging any code that touches octonion multiplication, verify against the checklist in `rfc/CONVENTIONS.md` §9.

## 3. Directory Boundaries & Scoped Responsibilities
You must respect the architectural separation of concerns. Do not mix narrative text with formal proofs, and do not mix symbolic logic with numerical approximations.

* `claims/` **(The Source of Truth):** This directory contains YAML files representing the knowledge graph. You may read these to understand dependencies and update their `status` or `provenance` metadata. Do not alter the core `statement` without explicit human permission.
* `CausalGraphTheory/` **(Formal Verification — Lean 4):** This is the strict mathematical kernel.
    * **Mathlib is allowed** for discrete algebra, tactics, and combinatorics. Use surgical imports of the deepest leaf module (e.g., `import Mathlib.Tactic.Ring`, not `import Mathlib`).
    * **Forbidden Mathlib imports (hard gate — CI will reject):**
      - `Mathlib.Analysis.*` (real analysis, normed spaces, calculus)
      - `Mathlib.Topology.*` (topological spaces, continuity, limits)
      - `Mathlib.MeasureTheory.*` (measures, integrals, probability)
      - `Mathlib.Geometry.Manifold.*` (smooth manifolds, bundles)
      - `Mathlib.Data.Real.*` (the real number line $\mathbb{R}$)
      - `Mathlib.Data.Complex.Basic` (Mathlib's Complex type — it transitively imports $\mathbb{R}$; use our `FormalComplex` instead)
    * **Allowed Mathlib imports (non-exhaustive):**
      - `Mathlib.Tactic.*` (`ring`, `ext`, `fin_cases`, `norm_num`, `decide`, `omega`, `simp`, `linarith`)
      - `Mathlib.Data.Fin.*`, `Mathlib.Data.Finset.*`, `Mathlib.Data.Fintype.*`
      - `Mathlib.Data.Int.*`, `Mathlib.Data.Rat.*`, `Mathlib.Data.ZMod.*`
      - `Mathlib.Data.Matrix.*`
      - `Mathlib.Algebra.*` (rings, groups, modules — discrete algebra)
      - `Mathlib.GroupTheory.*` (finite groups, subgroups, actions)
      - `Mathlib.RingTheory.*`
      - `Mathlib.LinearAlgebra.CliffordAlgebra.*`, `Mathlib.LinearAlgebra.QuadraticForm.*`
      - `Mathlib.Combinatorics.*` (including `SimpleGraph`)
      - `Mathlib.Order.*` (partial orders, lattices)
    * **When in doubt:** Run `lake exe graph` after adding a new import. If `Mathlib.Topology`, `Mathlib.Analysis`, or `Mathlib.Data.Real` appears in the transitive dependency graph, the import is forbidden.
    * Rely purely on discrete mathematics, finite group theory, algebra, and combinatorics.
* `calc/` **(Computational Drag & Numerics):** This is the Python/NumPy environment used to calculate algorithmic overhead (e.g., the $V \to S_+$ Triality translation). 
    * Use this for 2D grid/matrix generation, eigenvalue limits, and fast iterative testing of the Fano Penalty or mass ratios.
    * All numeric claims must be backed by a passing `pytest` suite.
* `manuscript/` **(Pedagogical Output):** This contains the LaTeX source for the textbook. You may only write to this directory to explain claims that have a status of `cited` or `proved`. The narrative must translate the discrete graph combinatorics into accessible, intuitive concepts.

## 3b. Editing Markdown Files with LaTeX

When editing `.md` files in `rfc/` or `sources/`, AI-generated text has a known failure mode: LaTeX escape sequences get corrupted into control characters.

**Known corruptions (written by an AI, stored as literal control chars):**

| Intended LaTeX | What got written | Symptom in Read output |
|---|---|---|
| `\to` | TAB + `o` | `	o` (tab before `o`) |
| `\tau` | TAB + `au` | `	au` |
| `\nu` | LF + `u` | line break before `u` |
| `\nu_R` | LF + `u_R` | heading split across two lines |
| `\times` | TAB + `imes` | `	imes` |

**The fix is always the same:** Use the `Edit` tool directly. Read the file, see the corruption, and replace the broken span with the correct LaTeX string. **Do not write Python scripts to manipulate bytes.** The `Read` tool normalizes line endings, and the `Edit` tool matches the normalized content exactly — this is sufficient to fix any control-character corruption.

## 4. The Workflow Loop
When assigned a task, execute the following loop:
1.  **Read the Claim:** Understand the specific algebraic or combinatorial mechanism proposed in the `claims/` YAML file.
2.  **Ground the Claim:** If it requires external grounding, search `sources/` or query the literature to find supporting/falsifying contexts.
3.  **Formalize or Compute:** * If it is a structural mechanism (e.g., anomaly cancellation), write the Lean proof in `lean/`.
    * If it is a quantitative prediction (e.g., the Koide formula limit), write the Python/NumPy derivation in `calc/`.
4.  **Update State:** Modify the YAML file's status to `proved` or `blocked`.
5.  **Draft the Prose:** If `proved`, update the relevant `manuscript/` section with clear, pedagogical LaTeX.

Remember: A physical theory must be fragile to be true. Actively search for failure modes, associative graph noise, and combinatorial dead ends. If the non-associative math breaks down, document the exact point of failure.
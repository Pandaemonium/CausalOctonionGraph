# Contributing to the Causal Octonion Graph (COG) Theory

Welcome to the COG project! We are thrilled you are here.

This repository is not just a standard software project; it is a foundational physics laboratory. We are building a mathematically rigorous, fully verified framework to derive the Standard Model of particle physics from discrete, non-associative algebra.

To ensure our proofs remain mathematically pristine and our sub-quantum models remain logically consistent, all contributors must strictly adhere to the guidelines below.

---

## The Prime Directive: No Continua Allowed

Before writing a single line of Lean or Python, you must understand the core hypothesis of this project: **The continuum is an illusion.** We model reality as a discrete, directed acyclic causal graph. Therefore, we enforce a strict "firewall" against continuous mathematics.

* **Forbidden:** You must never import `Mathlib.Data.Real`, `Mathlib.Topology.ContinuousFunction`, or rely on any axioms of infinite divisibility or smooth manifolds.
* **Required:** All proofs and simulations must rely strictly on discrete mathematics, finite group theory, the C⊗O (complex-octonion) algebra, and graph combinatorics.

---

## Repository Architecture

To prevent cross-contamination of logic, the repository is strictly divided:

1. **`claims/`**: The Knowledge Graph (YAML). The absolute source of truth for the physical theory.
2. **`CausalGraphTheory/`**: The Lean 4 formal verification kernel. All algebraic symmetries and graph kinematics are proven here.
3. **`calc/`**: The Python/NumPy sandbox. Used strictly for calculating algorithmic computational drag (particle mass) and statistical limits.
4. **`rfc/`**: The Request for Comments directory. Where new physical mechanisms are debated before being coded.

---

## How to Contribute

Whether you are a mathematician, a physicist, or a software engineer, there is a place for you here.

### 1. The RFC Process (For New Physics/Math Concepts)

Do not open a massive Pull Request with a brand-new physical theory or a 1,000-line Lean file. All structural additions must go through the Request for Comments (RFC) process.

1. Copy an existing RFC (e.g. `rfc/RFC-001_Canonical_State_and_Rules.md`) as a template and draft your proposal with a new `RFC-NNN_` prefix.
2. Open a PR adding your draft to the `rfc/` folder.
3. The community (and our automated Red Team agents) will review it, hunt for hidden assumptions, and test its combinatorics.
4. Once the RFC is merged, you may begin formalizing it in Lean or Python.

### 2. Lean 4 Formalization (`lean/`)

If you are contributing to the verified math kernel:

* **Check the Conventions:** All sign conventions, directed Fano triples, and Witt pairings are locked in [`rfc/CONVENTIONS.md`](rfc/CONVENTIONS.md). Do not invent your own basis alignments.
* **Keep Files Tiny:** One lemma/theorem per file is highly encouraged. This prevents edit drift and keeps the LSP fast.


### 3. Python Algorithmic Simulation (`calc/`)

If you are simulating generation masses or the Koide limit:

* **Test-Driven Derivations:** Every numerical derivation must be backed by a pytest suite in `calc/` (test files are named `calc/test_*.py`). Run tests with `python -m pytest` to avoid environment/PATH mismatches.
* **Algorithmic Honesty:** You may not hardcode arbitrary constants to make the math fit empirical data. All operations must represent literal execution steps of the graph (e.g., shifting across independent complex color planes).

---

## File Encoding: UTF-8 is Mandatory

Lean 4 is a Unicode-first language. All `.lean` files in this project use
Unicode characters (`→`, `ℤ`, `⟨`, `⟩`, `·`, `⊗`, etc.) for readability
and mathematical accuracy. **Do not replace these with ASCII substitutes.**

### Rules

1. **All `.lean` and `.py` files must be encoded as UTF-8.** Never rely on
   system defaults (Windows defaults to `cp1252`, which corrupts 3-byte UTF-8
   sequences starting with 0xE2).

2. **AI agents writing `.lean` files must use explicit `encoding='utf-8'`.**
   The recommended pattern is a one-time helper script:

   ```python
   # Build the Lean string with \u escapes to keep the Python source ASCII-safe,
   # then write it explicitly as UTF-8.
   LEAN_CODE = "def f : Nat \u2192 Nat\n  | 0 => 1\n  | n+1 => n\n"
   with open('CausalGraphTheory/MyFile.lean', 'w', encoding='utf-8') as f:
       f.write(LEAN_CODE)
   ```

3. **If you see `â`, `â†'`, or `âŸ` in error messages**, it means a UTF-8
   multi-byte sequence was decoded as cp1252. Fix the encoding; do not
   rewrite the Lean code.

4. **Verify after writing** with `lake build`:

   ```bash
   lake build CausalGraphTheory.MyModule 2>&1 | tail -20
   ```

See `LESSONS_AND_TIPS.md §Lean LSP / Tooling Issues` for the full diagnosis
and key `\u` escape reference table.

---

## Pull Request Workflow

1. **Fork the repository** and create your branch from `main`.
2. **Sync the cache:** Always run `lake exe cache get` before building to avoid recompiling Mathlib.
3. **Run the test suites:**
* Lean: Ensure `lake build` passes with zero errors or `sorry` states in your modified files.
* Python: Ensure `python -m pytest -q` passes.


4. **Targeted Diffs:** Ensure your PR is surgically focused. Do not include random formatting changes in unrelated files.
5. **Update the Knowledge Graph:** If your PR successfully proves a blocked theorem or derivation, update the corresponding YAML file in `claims/` to `status: proved` and link your PR.

---

## Getting Help

If you get stuck on a Lean tactic (e.g. an induction hypothesis has the wrong shape, or `simp` auto-expands something unexpectedly), check [`LESSONS_AND_TIPS.md`](LESSONS_AND_TIPS.md) first — it documents known pitfalls and their fixes. If you are still stuck, open a "Draft" PR and ask for help. We highly encourage collaborative debugging.

Thank you for helping us rewrite the foundations of physics!


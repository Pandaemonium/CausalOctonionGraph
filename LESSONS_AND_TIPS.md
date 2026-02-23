# LESSONS_AND_TIPS.md

A running log of tricky issues encountered in this project and how they were resolved.
Add new entries at the **top** of each section so the most recent fixes are easy to find.

---

## Lean 4 Proof Issues

### Induction with a Hypothesis Depending on the Induction Variable

**Symptom:** When doing `induction n generalizing a` and there is a hypothesis
`h1 : f a b n = true` already in context, the generated IH has the **wrong shape** —
it does NOT include `h1` as a premise. Instead `ih` has type `conclusion_with_n=k`
with no mention of `h1`, making `ih h_reach` fail with "Function expected".

**Root cause:** Lean 4's `induction` only generalizes the listed variables in the IH.
Hypotheses already in context that depend on the induction variable are **not** automatically
moved into the IH; they stay as fixed hypotheses specialized to each case.

**Fix:** Extract a separate private auxiliary lemma that does NOT have `h1` in scope,
so the induction hypothesis is correctly universally quantified. Pattern:

```lean
-- Wrong: h1 in scope corrupts IH
lemma my_lemma (h1 : reach G a b n) (h2 : reach G b c m) : reach G a c (n+m) := by
  induction n generalizing a  -- IH is wrong!

-- Correct: auxiliary lemma keeps h2 fixed, quantifies over n and a
private lemma my_lemma_aux (h2 : reach G b c m) :
    ∀ (n a : Nat), reach G a b n → reach G a c (n + m) := by
  intro n
  induction n with   -- IH is: ∀ a, reach G a b k → reach G a c (k+m)  ✓
  ...

lemma my_lemma (h1 : reach G a b n) (h2 : reach G b c m) : reach G a c (n+m) :=
  my_lemma_aux h2 n a h1
```

---

### `split_ifs at h` Puts the NEGATIVE Case First

**Symptom:** Writing `split_ifs at h with hcond; · tactic_for_true; · tactic_for_false`
results in strange errors: the first bullet applies to the `¬ cond` case, and the second
to the `cond` case — the opposite of what you'd expect.

**Root cause:** Lean 4's `split_ifs` generates the `neg` subgoal **before** the `pos`
subgoal, so the first `·` is always the negative (false) branch.

**Fix:** Use `by_cases` instead of `split_ifs` when case order matters:

```lean
-- Fragile with split_ifs (neg case comes first):
split_ifs at h with hgt
· simp at h          -- accidentally handles neg case
· exact some_lemma h -- accidentally handles pos case

-- Robust with by_cases:
by_cases hgt : s > t
· -- pos case: guaranteed
  unfold dist at h; rw [if_pos hgt] at h; exact absurd h (by simp)
· -- neg case: guaranteed
  unfold dist at h; rw [if_neg hgt] at h; exact List.find?_some h
```

---

### `simp at h` May Auto-Expand `List.find?` Results

**Symptom:** After `split_ifs at h` in the negative branch where
`h : (List.range n).find? p = some d`, calling `simp at h` transforms `h` into
a conjunction `p d = true ∧ d < n ∧ ∀ j < d, p j = false` via an `@[simp]` lemma.
This leaves the goal **unsolved** (simp doesn't automatically apply `h.1`).

**Fix:** Avoid `simp` on `find?` hypotheses. Use `rw [if_pos/if_neg]` to selectively
reduce the `if`, then call `List.find?_some h` directly:

```lean
unfold dist at h
rw [if_neg hgt] at h      -- rw does NOT trigger @[simp] auto-rewriting
exact List.find?_some h   -- h is still the raw find? = some d form
```

If you do end up with the conjunction form, extract with `h.1`.

---

### `List.find?_append` Leaves an `Option.or` Goal Requiring `rfl`

**Symptom:** After `rw [List.find?_append, h_pre]` where `h_pre : l1.find? p = some k`,
the remaining goal is `(some k).or (l2.find? p) = some k`, which is NOT automatically
closed.

**Root cause:** `List.find?_append : (xs ++ ys).find? p = (xs.find? p).or (ys.find? p)`.
After substituting `h_pre`, you get `(some k).or _ = some k`, which is `rfl` by definition
of `Option.or`, but Lean doesn't close it automatically.

**Fix:** Add `rfl` after the rewrites:

```lean
have hfull : (l1 ++ l2).find? p = some k := by
  rw [List.find?_append, h_pre]
  rfl   -- closes (some k).or _ = some k
```

---

### `(0 : Octonion R).c k` Not Reduced by `dsimp only [...]`

**Symptom:** When proving `O * (0 : ComplexOctonion Z) = 0` via `Octonion.ext`,
the components of the zero octonion `(0 : Octonion R).c k` remain opaque after
`dsimp only [HMul.hMul, Mul.mul, Zero.zero]`. Subsequent `simp` or `ring` fails
because the zero components aren't substituted.

**Fix:** Add a private `rfl`-based helper lemma so `simp` can substitute:

```lean
private lemma zero_c_eq {R : Type*} [CommRing R] (k : Fin 8) :
    (0 : Octonion R).c k = 0 := rfl

-- Then use:
simp only [HMul.hMul, Mul.mul, zero_c_eq, FormalComplex.zero_re, FormalComplex.zero_im]
simp [FormalComplex.ext_iff]
```

---

### Nonexistent Lemma Names in Lean 4 / Mathlib

These Lean 3 / wrong-version lemma names have been confirmed **not to exist** in the current
Lean 4 / Mathlib version used by this project. Use the alternatives:

| Nonexistent name | Correct alternative |
|---|---|
| `List.indexOf` | Use `List.find?_eq_none` + contradiction approach instead |
| `List.find?_eq_none_of_lt_findIdx` | Use `List.find?_eq_none` + `List.find?_append` |
| `List.find?_isSome_iff_exists` | Use `rcases h : l.find? p with _ \| d'` to case-split |
| `List.find?_isSome_of_mem` | Use the `none`-branch contradiction pattern |
| `Option.noConfusion` (as a term) | Use `simp` or `absurd h (by simp)` |

**Key Lean 4 `List.find?` API** (confirmed working):
```lean
List.find?_some    : l.find? p = some a → p a = true
List.find?_eq_none : l.find? p = none ↔ ∀ x ∈ l, ¬(p x = true)
List.find?_append  : (xs ++ ys).find? p = (xs.find? p).or (ys.find? p)
List.take_range    : List.take i (List.range n) = List.range (min i n)
List.mem_of_find?_eq_some : l.find? p = some a → a ∈ l
```

---

### `Bool.and_eq_true` Is a `PropEq`, Not an `Iff`

**Symptom:** `Bool.and_eq_true` says `(a && b = true) = (a = true ∧ b = true)`.
It is a `Prop` equality (`=`), not an `Iff` (`↔`). This matters if you try to use it
with `exact` or `apply` — use `simp only [Bool.and_eq_true]` instead.

---

## Lean LSP / Tooling Issues

### `Write` Tool on Windows Corrupts Unicode in Lean Files (cp1252 vs UTF-8)

**Symptom:** A Lean file written by the AI `Write` tool compiles fine in existing
files (e.g. `WittBasis.lean`) but the newly written file produces errors like:
- `expected token` at column positions of `→`, `ℤ`, `⟨`, or `⟩`
- `Function expected at Generation but applied to â`
- `failed to synthesize CommRing â`

Hover info shows `generationShift : sorry` instead of `Generation → Generation`.

**Root cause:** On Windows, Python's default file encoding is `cp1252` (Windows
code page). The AI `Write` tool writes files without specifying `encoding='utf-8'`.
Multi-byte UTF-8 sequences for `→` (E2 86 92), `ℤ` (E2 84 A4), `⟨` (E2 9F A8),
and `⟩` (E2 9F A9) all start with byte 0xE2, which is the Latin-1 character `â`.
The cp1252 decoder corrupts the remaining bytes, producing garbage that Lean's
tokenizer rejects.

Importantly: the **existing** `.lean` files in the repo work fine because they
were created before this encoding issue was introduced. The corruption only
affects files created by the `Write` tool in the affected session.

**Do NOT work around by using ASCII substitutes** (`->` for `→`, `Int` for `ℤ`,
`{re :=}` for `⟨⟩`). Lean 4 is designed around Unicode; stripping it out makes
the math kernel unreadable and non-idiomatic.

**Correct fix:** Write a short Python script that uses `\u` escape sequences
(pure ASCII) to build the Lean source string, then writes it with `encoding='utf-8'`:

```python
# write_spinors.py  (ASCII-safe Python source; Unicode only in the string)
import pathlib

LEAN_CODE = """\
def generationShift : Generation \u2192 Generation
  ...
def leftVacConjDoubled : ComplexOctonion \u2124 :=
  \u27e8fun k => if k == 0 then \u27e81, 0\u27e9 else \u27e80, 0\u27e9\u27e9
"""
with open('CausalGraphTheory/Spinors.lean', 'w', encoding='utf-8') as f:
    f.write(LEAN_CODE)
```

Run it via Bash, then verify with `lake build`:

```bash
cd /c/Projects/CausalGraphTheory
python write_spinors.py
lake build CausalGraphTheory.Spinors 2>&1 | tail -20
```

**Key characters and their `\u` escapes:**

| Character | U+ code | Python escape | Meaning |
|-----------|---------|--------------|---------|
| `→` | U+2192 | `\u2192` | Lean type arrow |
| `ℤ` | U+2124 | `\u2124` | Integer type |
| `⟨` | U+27E8 | `\u27e8` | Anonymous constructor open |
| `⟩` | U+27E9 | `\u27e9` | Anonymous constructor close |
| `·` | U+00B7 | `\u00b7` | Middle dot (in comments) |
| `⊗` | U+2297 | `\u2297` | Tensor product (in comments) |

**After verifying with `lake build`:** delete the helper script (it is a
one-time fix, not a project artifact).

---

### `lean_diagnostic_messages` Tool Gives `charmap` Codec Errors

**Symptom:** The `lean_diagnostic_messages` MCP tool fails with
`'charmap' codec can't decode byte 0x90` or similar, especially after writing files
with Unicode content (arrow characters `→`, angle brackets `⟨⟩`, etc.).

**Fix:** Fall back to `lake build` via the Bash tool for reliable diagnostics:

```bash
cd /c/Projects/CausalGraphTheory && lake build CausalGraphTheory.Distance 2>&1 | tail -30
```

The build output shows accurate file:line:col error messages and is not affected
by codec issues.

---

### `lean_run_code` Tool Has UTF-8 Angle Bracket Issues

**Symptom:** `lean_run_code` fails with `expected token` errors at column positions
corresponding to `⟨` or `⟩` characters (U+27E8/U+27E9, 3-byte UTF-8). The `obtain`
tactic pattern `obtain ⟨a, b, c⟩ := h` reliably triggers this.

**Root cause:** The `lean_run_code` tool processes code through a codec that
mishandles multi-byte UTF-8 characters at specific positions.

**Workaround:** For testing proofs that use `obtain ⟨...⟩`, write the proof directly
into the Lean file and use `lake build` to check it. For `lean_run_code`, use
`rcases` or `match` if possible, but know that the `obtain` failure is a tool issue,
not a proof issue.

---

### Cascading "expected token" / "Function expected" Errors in Diagnostics

**Symptom:** The LSP diagnostic tool reports bizarre errors like
"Function expected at ℕ, applied to â" at positions inside valid-looking definitions
(e.g., inside `def reachableIn : Nat → Nat → Nat → Bool`).

**Root cause:** These are cascading errors from real problems later in the file
(e.g., unknown constants, wrong lemma names). The `â` is the first byte (0xE2)
of the UTF-8 arrow `→`, reported with wrong encoding in the error message.

**Fix:** Look for the REAL errors reported further down the file (unknown identifier,
unsolved goals, etc.) and fix those first. The cascading "expected token" errors
will disappear once the real errors are resolved.

---

## Markdown / LaTeX Issues

### AI-Generated LaTeX Escape Sequences Corrupted to Control Characters

**Symptom:** When reading `.md` files edited by an AI, sequences like `\to` appear
as a TAB character followed by `o` (shown as `	o` in the Read output). Similarly:
`\tau` → `	au`, `\nu` → newline + `u`, `\times` → `	imes`.

**Root cause:** AI text generation sometimes emits the escape character (0x09 for TAB,
0x0A for newline) instead of the backslash when writing LaTeX commands.

**Fix:** Use the `Edit` tool directly to replace the corrupted span with the correct
LaTeX string. The `Read` tool normalizes line endings, and `Edit` matches the normalized
content exactly. Do NOT use Python scripts to manipulate bytes.

```
Read the file → see the corruption → Edit to replace corrupted span with correct LaTeX
```

---

## Python / pytest Issues

*(none yet)*

---

## General Development Tips

- **One concept per file**: keep Lean files short. If a file is growing beyond ~200 lines
  of proof code, consider splitting lemmas into separate files.
- **Surgical edits only**: never rewrite a whole file to fix a few lines. Use targeted
  `Edit` operations to preserve surrounding context.
- **Halt on confusion**: if a Lean tactic fails and you've tried 3+ approaches, stop and
  mark the claim as `blocked` rather than guessing indefinitely.
- **Check API before using**: use `#check @Lemma.name` via `lean_run_code` to verify
  the exact signature before writing a proof that depends on it.
- **Avoid `Mathlib.Data.List.Defs` import**: `Mathlib.Data.List.Basic` covers nearly all
  list lemmas needed. The `Defs` import may be redundant or cause issues.

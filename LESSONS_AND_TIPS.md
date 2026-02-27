# LESSONS_AND_TIPS.md

A running log of tricky issues encountered in this project and how they were resolved.
Add new entries at the **top** of each section so the most recent fixes are easy to find.

## Quick-Find Index

| Symptom keyword | Section |
|----------------|---------|
| `pytest`, `No module named pytest`, test runner | [Python / pytest Issues](#python--pytest-issues) |
| `crucible`, `docker exec`, container not running | [Docker / Crucible Issues](#docker--crucible-issues) |
| `charmap`, `cp1252`, Unicode corruption, `→` broken | [UTF-8 / Encoding Issues](#utf-8--encoding-issues) |
| `\to`, `\tau`, `\nu` corrupted in Markdown | [Markdown / LaTeX Issues](#markdown--latex-issues) |
| `split_ifs`, `induction` IH wrong shape, `simp` | [Lean 4 Proof Issues](#lean-4-proof-issues) |
| `lean_diagnostic_messages` codec error | [UTF-8 / Encoding Issues](#utf-8--encoding-issues) |
| `python3` not found on Windows | [Python / pytest Issues](#python--pytest-issues) |
| `status after pi`, YAML metadata backfill, claim schema | [YAML / Claim Metadata Issues](#yaml--claim-metadata-issues) |
| `unacceptable character #x0081`, YAML parse error | [YAML / Claim Metadata Issues](#yaml--claim-metadata-issues) |

---

## YAML / Claim Metadata Issues

### Regex Backfill Can Accidentally Delete `status:` Lines

**Symptom:** After automated metadata insertion, claims have only:
`pi_obs_profile`, `projection_sensitivity`, etc., and top-level `status:` is missing.
This silently breaks claim governance and any status-dependent tooling.

**Root cause:** PowerShell regex replacement used a replacement string like
`"$1`n$ins"` where `$1` is interpreted as a PowerShell variable (empty), not
a regex capture-group reference.

**Fix:** Use `Regex.Replace` with an explicit match evaluator or construct the
new line with the captured group value, e.g.:

```powershell
$new = [regex]::Replace($raw, '(?m)^(status:\s*.*)$', { param($m) $m.Value + "`n" + $ins }, 1)
```

Then run a validation pass:
1. every claim must still have `^status:`,
2. `status:` must appear before `pi_obs_profile:`.

---

### Untracked Claim Files Cannot Be Recovered from `HEAD`

**Symptom:** Recovery script uses `git show HEAD:claims/<file>.yml` and fails with:
`path exists on disk, but not in 'HEAD'`.

**Root cause:** File is untracked (`??`) and has no committed baseline in `HEAD`.
Any "restore from git" logic will fail for these files.

**Fix:**
1. Detect tracked/untracked before recovery.
2. For tracked files, restore from `HEAD`.
3. For untracked files, treat as standalone and reconstruct from alternate artifacts
   (manager briefs, notes, copies), or quarantine/remove until canonical source exists.

Quick check:

```powershell
git status --short claims
```

---

### Strict YAML Parsing Fails on Hidden Control Characters

**Symptom:** YAML loader errors like:
`unacceptable character #x0081` or `#x008f`.

**Root cause:** Corrupted control bytes (often from encoding/tool-chain issues)
inside text blocks; YAML parsers reject them.

**Fix:** Sanitize control characters before parse validation:
1. remove `[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]`,
2. rewrite file UTF-8 with normalized newlines,
3. rerun YAML parser over all claims.

Minimal Python sanitizer pattern:

```python
import re, glob
pat = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]')
for p in glob.glob('claims/*.yml'):
    s = open(p, 'r', encoding='utf-8').read()
    ns = pat.sub('', s)
    if ns != s:
        open(p, 'w', encoding='utf-8', newline='\n').write(ns)
```

Always follow with parser validation (`yaml.safe_load`) across all claim files.

---

### List-Style YAML Files Need Entry-Scoped Backfills

**Symptom:** Multi-entry files (e.g., list of `- id: ...`) lose list markers or
become malformed after global replace.

**Root cause:** Line-oriented replacement scripts assume one top-level map per file.
That assumption fails for list-style claim registries.

**Fix:**
1. Detect list-style files first (`^- id:`).
2. Apply metadata insertion per entry with two-space indentation.
3. Validate counts (`entries == status == pi_obs_profile`) after patch.

Never run one-map backfill logic on list files.

---

## Docker / Crucible Issues

### `pytest` Not Available in Crucible Container

**Symptom:** `docker exec crucible python3 -m pytest calc/ ...` returns
`No module named pytest`. Post-task verification in the orchestrator silently
reports unverified for all Python tasks.

**Root cause:** The crucible container's startup command is `tail -f /dev/null`
with no pip install step. The `orchestrator` and `dashboard` containers install
their `requirements.txt` (which includes pytest) at startup, but the crucible
does not.

**Fix:** `pytest` was added to the Dockerfile's base pip install line (2026-02-26).
Rebuild the crucible container to pick it up:
```bash
docker compose up -d --build crucible
```
After rebuilding, `python3 -m pytest calc/ -x --tb=short -q` works inside the
crucible container as expected.

**Note for agents:** If `python3 -m pytest` fails inside the crucible with
"No module named pytest", the container has not been rebuilt yet. Log the
verification result as `unverified` and continue — do NOT try to `pip install`
at runtime (will fail with "externally-managed-environment" on Ubuntu 24.04).

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
`\tau` → TAB+`au`, `\nu` → newline+`u`, `\times` → TAB+`imes`.

**Root cause:** AI text generation sometimes emits the escape character (0x09 for TAB,
0x0A for newline) instead of the backslash when writing LaTeX commands.

**How to scan for it** (run from repo root):

```python
import glob
TAB = chr(9)
for path in sorted(glob.glob('**/*.md', recursive=True)):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    hits = [(i, repr(content[max(0,i-12):i+12])) for i, c in enumerate(content) if c == TAB]
    for pos, ctx in hits:
        print(f'{path}  byte {pos}: {ctx}')
```

**Fix — small number of corruptions (1–3):** Use the `Edit` tool directly.
The `Read` tool normalizes line endings, and `Edit` matches the normalized content
exactly, so a targeted find-and-replace is fastest:

```
Read the file → identify the exact corrupted span → Edit to replace with correct LaTeX
```

**Fix — bulk corruption (4+ occurrences in a file):** Do NOT try to fix with a
`python -c "..."` bash one-liner. The bash escaping of TAB characters in the replacement
strings silently fails and leaves the corruption in place. Instead, **write a Python
script to disk** using the `Write` tool, then run it:

```python
# fix_tabs.py  (write this file, then: python fix_tabs.py, then delete it)
TAB = chr(9)
with open('sources/comprehensive_literature_notes.md', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    (TAB + 'o ', '\\to '),    # \to followed by space
    (TAB + 'o}', '\\to}'),    # \to followed by }
    (TAB + 'imes', '\\times'),
    (TAB + 'au', '\\tau'),
    ('\nu', '\\nu'),           # newline + u (if present)
]
for bad, good in replacements:
    content = content.replace(bad, good)

with open('sources/comprehensive_literature_notes.md', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
remaining = [i for i, c in enumerate(content) if c == TAB]
print(f'Remaining tabs: {len(remaining)}')
```

Run with `python fix_tabs.py`, verify output is `Remaining tabs: 0`, then delete the
helper script.

**Why `python -c` fails:** When you pass replacement strings containing `\t` through
`bash -c "python -c '...'"`, the two layers of shell quoting interact unpredictably
and the backslash is either consumed by bash or Python's string parser before the
`str.replace()` call sees it. Writing to a file entirely sidesteps this.

---

## Python / pytest Issues

### `python3` Not Found on Windows — Use `python`

**Symptom:** `python3 fix_tabs.py` fails with `'python3' is not recognized as an
internal or external command`.

**Root cause:** On Windows, the Python binary is always `python`, not `python3`.
The `python3` alias only exists by default on Linux/macOS.

**Fix:** Use `python` (no `3`) for all Bash commands in this repo:

```bash
python fix_tabs.py       # correct on Windows
python -m pytest -q      # correct on Windows
```

---

### Checking Which `pytest` / Package Is Active

**Symptom:** `pytest` command works but picks up a system-level pytest that can't
find the repo's `calc/` modules (import errors on `from calc.conftest import ...`).

**Fix:** Always run via the module flag to ensure the right environment:

```bash
python -m pytest -q
```

This guarantees pytest uses the same `sys.path` as the `python` executable you
just confirmed is working.

---

## General Development Tips

- **Consult this file first**: before spending time fighting a tooling or encoding
  problem, search `LESSONS_AND_TIPS.md` for a prior solution. If you solve a new
  annoyance, document it here immediately so the next session benefits.
- **`lean_verify` is the gold-standard axiom check**: use `lean_verify` (not
  `lean_diagnostic_messages`) to confirm a theorem is axiom-clean. It returns the
  exact set `{propext, Classical.choice, Quot.sound}` for `sorry`-free proofs and
  is not affected by the Windows charmap codec errors.
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
- **Delete temporary fix scripts**: after running any one-off Python helper (encoding
  fix, data migration, etc.), delete it immediately. These files are not project
  artifacts and will pollute `git status`.

# Formatting and Text Integrity Guardrails

## Goal
Stop spending time on avoidable formatting and encoding cleanup by enforcing automated checks locally and in CI.

## Scope
This plan covers:
- line endings, whitespace, and final newlines
- UTF-8 encoding and mojibake detection
- YAML/JSON sanity checks
- consistent local + CI behavior

This plan does not change project math, proofs, or physics claims.

## Guardrail Stack

### 1. Editor-level defaults (first line of defense)
Add `.editorconfig` and require editors/IDEs to respect it.

Recommended baseline:
```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.py]
indent_size = 4

[*.lean]
indent_size = 2
```

VS Code workspace defaults (`.vscode/settings.json`):
- `"files.encoding": "utf8"`
- `"files.eol": "\n"`
- `"editor.formatOnSave": true`

### 2. Git-level normalization (second line of defense)
Add `.gitattributes`:
```gitattributes
* text=auto eol=lf

*.lean text eol=lf
*.yml text eol=lf
*.md text eol=lf
*.py text eol=lf
*.toml text eol=lf
*.json text eol=lf

*.png binary
*.jpg binary
*.jpeg binary
*.pdf binary
```

This prevents OS-specific EOL churn and accidental binary rewrites.

### 3. Local pre-commit hooks (hard local gate)
Add `.pre-commit-config.yaml` and require contributors to install hooks.

Hook set:
- `trailing-whitespace`
- `end-of-file-fixer`
- `mixed-line-ending` (force LF)
- `check-yaml`
- `check-json`
- `check-merge-conflict`
- `check-lean-sorry` (grep gate)
- custom `scripts/check_text_integrity.py`

`check_text_integrity.py` should fail on:
- UTF-8 BOM (`b'\xef\xbb\xbf'`)
- control chars (except tab/newline/carriage return)
- cp1252 corruption sequences for common math/doc Unicode:
- `b'\xe2\x80\x94'` decoded as cp1252 (em-dash corruption signature)
- `b'\xc2\xa7'` decoded as cp1252 (section-sign corruption signature)
- `b'\xe2\x80\x9c'` decoded as cp1252 (smart-quote corruption signature)
- replacement character bytes `b'\xef\xbf\xbd'` (`\ufffd`)
- generic suspicious high-byte pairs matching `r'[\xc3\xc2][\x80-\xbf]'` in byte-level scans

Note: the primary root cause in this repo is AI tooling on Windows writing cp1252 instead of UTF-8 (especially for Lean/doc files). See `CLAUDE.md` §2 for the required prevention pattern (`encoding='utf-8'` in write helpers). The hook is a safety net, not a substitute.

### 4. CI gate (must match local)
In GitHub Actions, run:
```bash
python -m pip install pre-commit
pre-commit run --all-files

# hard gate for incomplete Lean proofs
if grep -r '\bsorry\b' CausalGraphTheory/ --include='*.lean'; then
  echo "ERROR: sorry found in Lean files"
  exit 1
fi
```

This ensures local checks and CI checks are identical.

## Required Contributor Workflow

### One-time setup
```bash
python -m pip install pre-commit
pre-commit install
```

### Before pushing
```bash
pre-commit run --all-files
lake build
python -m pytest -q
```

If any formatting/encoding check fails, fix it before commit.

## Suggested Repository Commands
Adopt `make check` as the canonical pre-push target. It should run:
1. `pre-commit run --all-files`
2. YAML parse sanity check for all `claims/*.yml`
3. `lake build`
4. `python -m pytest -q`

Keep this command as the canonical pre-push gate.

## Rollout Plan
1. Add `.editorconfig`.
2. Add `.vscode/settings.json` with UTF-8 + LF defaults.
3. Add `.gitattributes`.
4. Run `git add --renormalize .` and commit the normalization delta.
5. Add `.pre-commit-config.yaml` (including `check-lean-sorry`).
6. Add `scripts/check_text_integrity.py`.
7. Update CI workflow to run pre-commit + `sorry` gate.
8. Update existing `CONTRIBUTING.md` with setup instructions (do not recreate it).
9. Enforce: no PR merge unless formatting gate is green.

## Acceptance Criteria
- Formatting-only churn in PRs drops to near zero.
- No new mojibake/control-character regressions.
- Local and CI formatting results are consistent.
- Contributors can run one command and know if a branch is merge-ready.

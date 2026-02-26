"""
Smoke test: call all three frontier models simultaneously with the manager brief.
Each model is asked to assess the project state and recommend short/medium/long-term goals.

Usage:
    python calc/smoke_test_frontiers.py
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Load .env from repo root
# ---------------------------------------------------------------------------
REPO = Path(__file__).parent.parent
ENV_FILE = REPO / ".env"

def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val

_load_env(ENV_FILE)

# ---------------------------------------------------------------------------
# Collect repo context
# ---------------------------------------------------------------------------
def _read(path, limit=5000):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception as e:
        return f"(could not read: {e})"

def build_context() -> str:
    brief = _read(REPO / "rfc/MANAGER_BRIEF_FRONTIER.md", 8000)

    # Claim statuses
    import yaml  # type: ignore
    claims_lines = []
    claims_dir = REPO / "claims"
    for f in sorted(claims_dir.glob("*.yml")):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            cid   = data.get("id", f.stem)
            stat  = data.get("status", "?")
            stmt  = str(data.get("statement", ""))[:120]
            claims_lines.append(f"  {cid:12s} [{stat:12s}]  {stmt}")
        except Exception:
            pass
    claims_block = "\n".join(claims_lines) if claims_lines else "(none found)"

    # Recent Lean files (outline)
    lean_files = sorted((REPO / "CausalGraphTheory").glob("*.lean"))
    lean_outline = "\n".join(f.name for f in lean_files[:25])

    return f"""
# COG Lab — Project State Brief (2026-02-25)

{brief}

---

## Full Claim Registry (id, status, statement excerpt)

{claims_block}

---

## Lean Source Files Present

{lean_outline}
""".strip()


def run_charge_sign_regression_smoke() -> dict:
    """
    Local kernel regression smoke.

    Validates expected charge-sign interaction polarity outcomes from
    calc/charge_sign_interaction_matrix.py and records results even when
    frontier model API calls fail.
    """
    try:
        from calc.charge_sign_interaction_matrix import summarize

        summary = summarize()
        matrix = summary["matrix"]
        checks = {
            "ee_repulsive": matrix["electron"]["electron"] == "repulsive",
            "e_positron_attractive": matrix["electron"]["positron_like"] == "attractive",
            "e_vacuum_neutral": matrix["electron"]["vacuum"] == "neutral",
            "vacuum_vacuum_neutral": matrix["vacuum"]["vacuum"] == "neutral",
        }
        return {
            "ok": all(checks.values()),
            "checks": checks,
            "charges": summary["charges"],
            "error": "",
        }
    except Exception as e:
        return {
            "ok": False,
            "checks": {},
            "charges": {},
            "error": str(e),
        }


SYSTEM = (
    "You are an expert in discrete mathematics, Lean 4 formal proofs, "
    "theoretical physics, and mathematical physics research methodology. "
    "You give rigorous, honest, and constructive technical assessments. "
    "Be direct about gaps and risks — do not hype. Be specific about "
    "which mathematical steps are needed."
)

TASK = """
Based on the project brief above, please write a structured assessment covering:

1. **Current State Summary** — What has genuinely been proven vs what is still hand-waving?
   Which claims are robust, which are partial, which are speculative?

2. **Short-Term Goals (1–2 weeks)** — Specific, achievable tasks:
   name exact claims, exact files, and exact techniques.

3. **Medium-Term Goals (1–3 months)** — What theoretical milestones to target next?
   What would constitute a publishable result?

4. **Long-Term Vision (6–12 months)** — What does success look like?
   What is the highest-risk assumption that could invalidate the whole approach?

5. **Highest-Priority Next Task** — If you were the manager, what single task
   would you assign right now, to which worker model, and why?

Be specific and technical. This is a serious research project.
"""


# ---------------------------------------------------------------------------
# API callers
# ---------------------------------------------------------------------------

async def call_claude(context: str) -> tuple[str, float]:
    t0 = time.time()
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        response = client.messages.create(
            model="claude-sonnet-4-6",
            system=SYSTEM,
            messages=[{"role": "user", "content": context + "\n\n" + TASK}],
            max_tokens=3000,
        )
        return response.content[0].text, time.time() - t0
    except Exception as e:
        return f"[ERROR calling claude-sonnet-4-6]: {e}", time.time() - t0


async def call_gemini(context: str) -> tuple[str, float]:
    t0 = time.time()
    # Try gemini-3-pro-preview first, fall back to gemini-2.5-pro
    models_to_try = ["gemini-3-pro-preview", "gemini-2.5-pro", "gemini-2.5-flash"]
    for model in models_to_try:
        try:
            # Try new google-genai SDK first
            try:
                from google import genai  # type: ignore
                from google.genai import types  # type: ignore
                client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
                response = client.models.generate_content(
                    model=model,
                    contents=[{"role": "user", "parts": [{"text": context + "\n\n" + TASK}]}],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM,
                        max_output_tokens=3000,
                    ),
                )
                return f"[Model: {model} via google-genai SDK]\n\n{response.text}", time.time() - t0
            except ImportError:
                # Fall back to old SDK
                import google.generativeai as genai_old  # type: ignore
                genai_old.configure(api_key=os.environ["GOOGLE_API_KEY"])
                gmodel = genai_old.GenerativeModel(
                    model_name=model,
                    system_instruction=SYSTEM,
                )
                response = gmodel.generate_content(
                    contents=[{"role": "user", "parts": [{"text": context + "\n\n" + TASK}]}],
                    generation_config=genai_old.types.GenerationConfig(max_output_tokens=3000),
                )
                return f"[Model: {model} via google-generativeai SDK]\n\n{response.text}", time.time() - t0
        except Exception as e:
            err = str(e)
            if "not found" in err.lower() or "invalid" in err.lower() or "404" in err:
                # Model not available, try next
                continue
            return f"[ERROR calling {model}]: {e}", time.time() - t0
    return f"[ERROR: no Gemini models available. Tried: {models_to_try}]", time.time() - t0


async def call_codex(context: str) -> tuple[str, float]:
    t0 = time.time()
    models_to_try = ["codex-mini-latest", "gpt-5.2-codex", "o3-mini", "gpt-4o"]
    for model in models_to_try:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

            # Determine if this model uses Responses API or Chat Completions
            use_responses = any(p in model.lower() for p in ("codex",))

            if use_responses:
                response = client.responses.create(
                    model=model,
                    instructions=SYSTEM,
                    input=[{
                        "role": "user",
                        "content": [{"type": "input_text", "text": context + "\n\n" + TASK}],
                    }],
                    max_output_tokens=3000,
                )
                # Extract text
                text = ""
                for item in (getattr(response, "output", None) or []):
                    for part in (getattr(item, "content", None) or []):
                        if getattr(part, "type", "") in ("output_text", "text"):
                            t = getattr(part, "text", "")
                            if isinstance(t, str):
                                text += t
                if not text:
                    text = getattr(response, "output_text", "") or "(no output text)"
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM},
                        {"role": "user", "content": context + "\n\n" + TASK},
                    ],
                    max_tokens=3000,
                )
                text = response.choices[0].message.content or ""

            return f"[Model: {model}]\n\n{text}", time.time() - t0

        except Exception as e:
            err = str(e).lower()
            if any(x in err for x in ("not found", "no such model", "invalid model", "404", "does not exist")):
                continue
            return f"[ERROR calling {model}]: {e}", time.time() - t0

    return f"[ERROR: no OpenAI/Codex models available. Tried: {models_to_try}]", time.time() - t0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    # Force UTF-8 output to avoid Windows cp1252 encoding crashes
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    out_file = REPO / "calc" / "smoke_test_results.md"

    def emit(text: str) -> None:
        """Write to both stdout and the output file."""
        sys.stdout.write(text + "\n")
        sys.stdout.flush()

    emit("Building repo context...")
    try:
        context = build_context()
    except Exception as e:
        emit(f"Failed to build context: {e}")
        sys.exit(1)
    emit(f"Context length: {len(context):,} chars\n")

    emit("Running local kernel regression smoke...")
    charge_smoke = run_charge_sign_regression_smoke()
    if charge_smoke["error"]:
        emit(f"  [FAIL] charge-sign matrix smoke error: {charge_smoke['error']}")
    else:
        emit(f"  [OK={charge_smoke['ok']}] charges={charge_smoke['charges']}")
        for name, ok in charge_smoke["checks"].items():
            emit(f"    - {name}: {ok}")
    emit("")

    emit("Calling all three frontier models in parallel...")
    emit("=" * 70)

    results = await asyncio.gather(
        call_claude(context),
        call_gemini(context),
        call_codex(context),
        return_exceptions=False,
    )

    labels = [
        "CLAUDE SONNET 4.6",
        "GEMINI (3-PRO-PREVIEW or fallback)",
        "CODEX / OPENAI (codex-mini-latest or fallback)",
    ]

    output_sections = []
    for label, (response, elapsed) in zip(labels, results):
        section = f"\n{'=' * 70}\n### {label}  ({elapsed:.1f}s)\n{'=' * 70}\n{response}\n"
        output_sections.append(section)
        emit(section)

    emit("=" * 70)
    emit("Smoke test complete.")

    # Write full results to UTF-8 markdown file
    md_content = "# COG Lab — Frontier Model Smoke Test Results\n\n"
    md_content += f"*Generated: 2026-02-25*\n\n"
    md_content += "## Local Kernel Regression Smoke\n\n"
    if charge_smoke["error"]:
        md_content += f"- status: FAIL\n- error: `{charge_smoke['error']}`\n\n"
    else:
        md_content += f"- status: {'PASS' if charge_smoke['ok'] else 'FAIL'}\n"
        md_content += f"- charges: `{charge_smoke['charges']}`\n"
        md_content += "- checks:\n"
        for name, ok in charge_smoke["checks"].items():
            md_content += f"  - {name}: {ok}\n"
        md_content += "\n"
    md_content += "\n".join(output_sections)
    out_file.write_text(md_content, encoding="utf-8")
    emit(f"\nFull results written to: {out_file}")


if __name__ == "__main__":
    asyncio.run(main())

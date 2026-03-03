"""Smoke test for build_v3_structural_visualizer_v1."""

from __future__ import annotations

from pathlib import Path

from cog_v3.calc import build_v3_structural_visualizer_v1 as mod


ROOT = Path(__file__).resolve().parents[2]
OUT_HTML = ROOT / "cog_v3" / "sources" / "v3_structural_visualizer_v1.html"


def main() -> None:
    payload = mod.build_payload()
    ds = payload.get("datasets", [])
    ids = [d.get("dataset_id") for d in ds]
    if ids != ["Q240", "S960", "S2880"]:
        raise AssertionError(f"unexpected datasets: {ids}")
    mod.main()
    if not OUT_HTML.exists():
        raise AssertionError(f"missing html: {OUT_HTML}")
    html = OUT_HTML.read_text(encoding="utf-8")
    if "v3 Structural Visualizer" not in html:
        raise AssertionError("title marker missing")
    if "schema_version" not in html:
        raise AssertionError("payload marker missing")
    print("ok: test_v3_structural_visualizer_v1")


if __name__ == "__main__":
    main()


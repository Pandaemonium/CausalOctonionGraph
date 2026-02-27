from __future__ import annotations

from scripts.build_manager_context_package import build_package


def test_manager_context_package_schema() -> None:
    pkg = build_package(top_n=5)
    assert pkg["schema_version"] == "manager_context_package_v2"
    assert isinstance(pkg["summary"], dict)
    assert isinstance(pkg["top_open_claims"], list)
    assert isinstance(pkg["oracle"], dict)
    assert isinstance(pkg["semantic_digest"], list)


def test_manager_context_semantic_digest_nonempty() -> None:
    pkg = build_package(top_n=3)
    digest = pkg["semantic_digest"]
    assert isinstance(digest, list)
    assert all(isinstance(line, str) and line.strip() for line in digest)

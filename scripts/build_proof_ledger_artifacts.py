#!/usr/bin/env python3
"""
Build static JSON artifacts for the public Proof Ledger page.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CLAIMS_DIR = ROOT / "claims"
MATRIX_PATH = CLAIMS_DIR / "CLAIM_STATUS_MATRIX.yml"
EVENTS_PATH = ROOT / "website" / "claim_events.yml"
ACCOMPLISH_PATH = ROOT / "website" / "accomplishments.yml"
OUT_DIR = ROOT / "website" / "data"

STATUS_LABEL = {
    "supported": "Proved",
    "partial": "In Progress",
    "active_hypothesis": "Hypothesis",
    "stub": "Queued",
    "falsified": "Falsified",
    "superseded": "Superseded",
}
STATUS_COLOR = {
    "supported": "proved",
    "partial": "progress",
    "active_hypothesis": "hypothesis",
    "stub": "queued",
    "falsified": "falsified",
    "superseded": "superseded",
}


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        # Some historical claim files may contain malformed YAML fragments.
        # Artifact generation should degrade gracefully rather than fail hard.
        return {}
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _parse_utc(ts: str) -> datetime | None:
    if not isinstance(ts, str):
        return None
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None


def _extract_claim_id(path: Path, data: dict[str, Any]) -> str:
    for key in ("id", "claim_id", "name"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return path.stem.upper()


def _load_claim_dependencies(valid_claim_ids: set[str]) -> list[dict[str, str]]:
    edges: set[tuple[str, str]] = set()
    for path in sorted(CLAIMS_DIR.glob("*.yml")):
        if path.name == "CLAIM_STATUS_MATRIX.yml":
            continue
        data = _read_yaml(path)
        claim_id = _extract_claim_id(path, data)
        deps = data.get("depends_on", [])
        if not isinstance(deps, list):
            continue
        for dep in deps:
            if not isinstance(dep, str):
                continue
            dep = dep.strip()
            if dep in valid_claim_ids and claim_id in valid_claim_ids:
                edges.add((dep, claim_id))
    return [{"from": a, "to": b} for (a, b) in sorted(edges)]


def _derive_topics(event: dict[str, Any]) -> list[str]:
    topics = event.get("tags", [])
    if isinstance(topics, list):
        tags = [str(x).strip() for x in topics if isinstance(x, str) and x.strip()]
        if tags:
            return tags
    evidence = event.get("evidence", {})
    if isinstance(evidence, dict):
        owner = str(evidence.get("owner_rfc", "")).lower()
        if "weinberg" in owner:
            return ["electroweak"]
        if "gauge" in owner:
            return ["gauge-structure"]
        if "photon" in owner:
            return ["photon"]
        if "mass" in owner:
            return ["mass"]
    return ["general"]


def main() -> int:
    matrix = _read_yaml(MATRIX_PATH)
    events_doc = _read_yaml(EVENTS_PATH)
    accom_doc = _read_yaml(ACCOMPLISH_PATH)

    rows = matrix.get("rows", {})
    events = events_doc.get("events", [])
    cards = accom_doc.get("cards", [])

    if not isinstance(rows, dict):
        raise SystemExit("Invalid matrix rows")
    if not isinstance(events, list):
        raise SystemExit("Invalid claim events")
    if not isinstance(cards, list):
        cards = []

    now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Latest event per claim.
    latest_event_by_claim: dict[str, dict[str, Any]] = {}
    events_norm: list[dict[str, Any]] = []
    for ev in events:
        if not isinstance(ev, dict):
            continue
        claim_id = str(ev.get("claim_id", "")).strip()
        to_status = str(ev.get("to_status", "")).strip()
        promoted_at_utc = str(ev.get("promoted_at_utc", "")).strip()
        ts = _parse_utc(promoted_at_utc)
        if not claim_id or ts is None:
            continue

        normalized = dict(ev)
        normalized["public_status_label"] = STATUS_LABEL.get(to_status, to_status)
        normalized["status_color_token"] = STATUS_COLOR.get(to_status, "queued")
        normalized["topics"] = _derive_topics(ev)
        events_norm.append(normalized)

        current = latest_event_by_claim.get(claim_id)
        if current is None:
            latest_event_by_claim[claim_id] = normalized
        else:
            old_ts = _parse_utc(str(current.get("promoted_at_utc", "")))
            if old_ts is None or ts > old_ts:
                latest_event_by_claim[claim_id] = normalized

    events_norm.sort(
        key=lambda e: _parse_utc(str(e.get("promoted_at_utc", ""))) or datetime.min,
        reverse=True,
    )

    card_by_claim: dict[str, dict[str, Any]] = {}
    for card in cards:
        if isinstance(card, dict):
            claim_id = str(card.get("claim_id", "")).strip()
            if claim_id:
                card_by_claim[claim_id] = card

    claims_index: list[dict[str, Any]] = []
    for claim_id, row in sorted(rows.items()):
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", "stub"))
        latest_event = latest_event_by_claim.get(claim_id)
        card = card_by_claim.get(claim_id, {})
        claims_index.append(
            {
                "claim_id": claim_id,
                "status": status,
                "public_status_label": STATUS_LABEL.get(status, status),
                "status_color_token": STATUS_COLOR.get(status, "queued"),
                "owner_rfc": str(row.get("owner_rfc", "")).strip(),
                "last_verified_at": str(row.get("last_verified_at", "")).strip(),
                "spotlight_headline": str(card.get("public_headline", "")).strip(),
                "why_it_matters": str(card.get("why_it_matters", "")).strip(),
                "latest_event_id": str(latest_event.get("event_id", "")).strip() if latest_event else "",
                "latest_event_time_utc": str(latest_event.get("promoted_at_utc", "")).strip() if latest_event else "",
                "latest_headline_layman": (
                    str(latest_event.get("headlines", {}).get("layman", "")).strip() if latest_event else ""
                ),
            }
        )

    claim_ids = set(rows.keys())
    edges = _load_claim_dependencies(claim_ids)
    children_counter: Counter[str] = Counter(edge["from"] for edge in edges)

    tech_tree = {
        "generated_at_utc": now_utc,
        "node_count": len(rows),
        "edge_count": len(edges),
        "nodes": [
            {
                "id": ci["claim_id"],
                "status": ci["status"],
                "public_status_label": ci["public_status_label"],
                "status_color_token": ci["status_color_token"],
                "latest_event_id": ci["latest_event_id"],
                "unlocks_count": int(children_counter.get(ci["claim_id"], 0)),
            }
            for ci in claims_index
        ],
        "edges": edges,
    }

    counts = Counter(ci["status"] for ci in claims_index)
    claims_summary = {
        "generated_at_utc": now_utc,
        "counts_by_status": dict(sorted(counts.items())),
        "total_claims": len(claims_index),
        "latest_event_utc": events_norm[0]["promoted_at_utc"] if events_norm else "",
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "claim_events.json").write_text(
        json.dumps({"generated_at_utc": now_utc, "events": events_norm}, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "claims_index.json").write_text(
        json.dumps(
            {
                "generated_at_utc": now_utc,
                "summary": claims_summary,
                "claims": claims_index,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "tech_tree.json").write_text(json.dumps(tech_tree, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_DIR / 'claim_events.json'}")
    print(f"Wrote {OUT_DIR / 'claims_index.json'}")
    print(f"Wrote {OUT_DIR / 'tech_tree.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

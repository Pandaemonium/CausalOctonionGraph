#!/usr/bin/env python3
"""
Validate website/accomplishments.yml against claims/CLAIM_STATUS_MATRIX.yml.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "claims" / "CLAIM_STATUS_MATRIX.yml"
ACCOMPLISH_PATH = ROOT / "website" / "accomplishments.yml"
EVENTS_PATH = ROOT / "website" / "claim_events.yml"


def _canonical_status(status: str) -> str:
    return "supported_bridge" if status == "supported" else status


def _read_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _parse_utc(ts: str) -> datetime | None:
    if not isinstance(ts, str):
        return None
    ts = ts.strip()
    if not ts:
        return None
    try:
        # Supports both second and fractional-second UTC formats.
        # Example: 2026-02-27T00:26:10Z or 2026-02-27T00:26:10.282011Z
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def _looks_like_path(ref: str) -> bool:
    if "://" in ref:
        return False
    return "/" in ref or ref.endswith((".py", ".lean", ".md", ".yml", ".yaml", ".json"))


def _extract_file_ref(ref: str) -> str:
    # Keep the path prefix for values like "calc/test_x.py::test_case".
    if "::" in ref:
        return ref.split("::", 1)[0]
    return ref


def main() -> int:
    errors: list[str] = []
    if not MATRIX_PATH.exists():
        print(f"ERROR: missing {MATRIX_PATH}")
        return 1
    if not ACCOMPLISH_PATH.exists():
        print(f"ERROR: missing {ACCOMPLISH_PATH}")
        return 1

    matrix = _read_yaml(MATRIX_PATH)
    accom = _read_yaml(ACCOMPLISH_PATH)
    events_doc = _read_yaml(EVENTS_PATH) if EVENTS_PATH.exists() else {}
    rows = matrix.get("rows", {})
    cards = accom.get("cards", [])
    events = events_doc.get("events", [])

    if not isinstance(rows, dict):
        print("ERROR: matrix rows missing/invalid")
        return 1
    if not isinstance(cards, list):
        print("ERROR: accomplishments cards missing/invalid")
        return 1
    if EVENTS_PATH.exists() and not isinstance(events, list):
        print("ERROR: website/claim_events.yml events missing/invalid")
        return 1

    events_by_id: dict[str, dict[str, Any]] = {}
    latest_event_by_claim: dict[str, dict[str, Any]] = {}
    for ev in events if isinstance(events, list) else []:
        if not isinstance(ev, dict):
            continue
        event_id = str(ev.get("event_id", "")).strip()
        claim_id = str(ev.get("claim_id", "")).strip()
        promoted_at_utc = str(ev.get("promoted_at_utc", "")).strip()
        if event_id:
            events_by_id[event_id] = ev
        if claim_id:
            current = latest_event_by_claim.get(claim_id)
            if current is None:
                latest_event_by_claim[claim_id] = ev
            else:
                old_ts = _parse_utc(str(current.get("promoted_at_utc", "")))
                new_ts = _parse_utc(promoted_at_utc)
                if old_ts is None or (new_ts is not None and new_ts > old_ts):
                    latest_event_by_claim[claim_id] = ev

    seen_card_ids: set[str] = set()
    for idx, card in enumerate(cards):
        if not isinstance(card, dict):
            errors.append(f"card[{idx}] is not a mapping")
            continue
        card_id = str(card.get("card_id", "")).strip()
        claim_id = str(card.get("claim_id", "")).strip()
        status_raw = str(card.get("status", "")).strip()
        status = _canonical_status(status_raw)
        evidence = card.get("evidence", {})
        last_event_id = str(card.get("last_promotion_event_id", "")).strip()
        if not card_id:
            errors.append(f"card[{idx}] missing card_id")
        elif card_id in seen_card_ids:
            errors.append(f"duplicate card_id: {card_id}")
        else:
            seen_card_ids.add(card_id)
        if not claim_id:
            errors.append(f"{card_id or f'card[{idx}]'} missing claim_id")
            continue
        if claim_id not in rows:
            errors.append(f"{card_id}: unknown claim_id {claim_id}")
            continue
        matrix_status = _canonical_status(str(rows[claim_id].get("status", "")))
        if status != matrix_status:
            errors.append(f"{card_id}: status mismatch for {claim_id}: card={status_raw}, matrix={matrix_status}")
        if matrix_status not in {"supported_bridge", "proved_core"} and not card.get("gap_metric"):
            errors.append(f"{card_id}: non-supported claim must include gap_metric")
        if not isinstance(evidence, dict) or not evidence.get("claim_file"):
            errors.append(f"{card_id}: evidence.claim_file required")
            continue

        claim_file = str(evidence.get("claim_file", "")).strip()
        if claim_file and not (ROOT / claim_file).exists():
            errors.append(f"{card_id}: evidence.claim_file does not exist: {claim_file}")

        owner_rfc = str(evidence.get("owner_rfc", "")).strip()
        if owner_rfc and _looks_like_path(owner_rfc):
            owner_path = ROOT / _extract_file_ref(owner_rfc)
            if not owner_path.exists():
                errors.append(f"{card_id}: evidence.owner_rfc path missing: {owner_rfc}")

        for key in ("lean_artifacts", "battery_artifacts"):
            refs = evidence.get(key, [])
            if not isinstance(refs, list):
                continue
            for ref in refs:
                if not isinstance(ref, str):
                    continue
                ref = ref.strip()
                if not ref or not _looks_like_path(ref):
                    continue
                artifact_path = ROOT / _extract_file_ref(ref)
                if not artifact_path.exists():
                    errors.append(f"{card_id}: missing artifact path in {key}: {ref}")

        latest_event = latest_event_by_claim.get(claim_id)
        if status in {"supported_bridge", "proved_core"}:
            if latest_event is None:
                errors.append(f"{card_id}: supported claim must have a promotion event")
            elif _canonical_status(str(latest_event.get("to_status", "")).strip()) not in {
                "supported_bridge",
                "proved_core",
            }:
                errors.append(f"{card_id}: latest promotion event is not to a promoted status")

        if last_event_id:
            event = events_by_id.get(last_event_id)
            if event is None:
                errors.append(f"{card_id}: unknown last_promotion_event_id {last_event_id}")
            else:
                event_claim_id = str(event.get("claim_id", "")).strip()
                event_to_status = _canonical_status(str(event.get("to_status", "")).strip())
                if event_claim_id != claim_id:
                    errors.append(
                        f"{card_id}: last_promotion_event_id claim mismatch "
                        f"(event claim={event_claim_id}, card claim={claim_id})"
                    )
                if event_to_status != status:
                    errors.append(
                        f"{card_id}: last_promotion_event_id status mismatch "
                        f"(event to_status={event_to_status}, card status={status_raw})"
                    )

                last_verified_at = str(card.get("last_verified_at", "")).strip()
                event_time = _parse_utc(str(event.get("promoted_at_utc", "")).strip())
                verified_time = _parse_utc(last_verified_at)
                if last_verified_at and verified_time is None:
                    errors.append(f"{card_id}: invalid last_verified_at timestamp: {last_verified_at}")
                if event_time is not None and verified_time is not None and verified_time < event_time:
                    errors.append(
                        f"{card_id}: last_verified_at must be >= promotion time "
                        f"({last_verified_at} < {event.get('promoted_at_utc')})"
                    )

    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"OK: validated {len(cards)} accomplishment cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

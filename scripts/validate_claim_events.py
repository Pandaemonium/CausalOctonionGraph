#!/usr/bin/env python3
"""
Validate website/claim_events.yml against claims/CLAIM_STATUS_MATRIX.yml.

The claim-event ledger is append-only and promotion-oriented.
This validator enforces:
1. schema integrity,
2. allowed transitions,
3. event ordering and uniqueness,
4. matrix alignment for latest status per claim,
5. evidence path sanity checks.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "claims" / "CLAIM_STATUS_MATRIX.yml"
EVENTS_PATH = ROOT / "website" / "claim_events.yml"

TIERS = ("layman", "student", "physicist")
ALLOWED_STATUS = {
    "stub",
    "active_hypothesis",
    "partial",
    "supported_bridge",
    "proved_core",
    # Legacy alias still accepted in event history.
    "supported",
    "falsified",
    "superseded",
}
ALLOWED_TRANSITIONS = {
    "stub": {"active_hypothesis", "partial", "falsified", "superseded"},
    "active_hypothesis": {"partial", "supported_bridge", "proved_core", "falsified", "superseded"},
    "partial": {"supported_bridge", "proved_core", "falsified", "superseded"},
    "supported_bridge": {"proved_core", "falsified", "superseded"},
    "proved_core": {"falsified", "superseded"},
    # Legacy alias resolves to supported_bridge.
    "supported": {"proved_core", "falsified", "superseded"},
    "falsified": set(),
    "superseded": set(),
}


def _read_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
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


def _is_nonempty_str(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _canonical_status(s: str) -> str:
    return "supported_bridge" if s == "supported" else s


def _extract_file_ref(ref: str) -> str:
    if "::" in ref:
        return ref.split("::", 1)[0]
    return ref


def _path_like(ref: str) -> bool:
    return "/" in ref or ref.endswith((".py", ".lean", ".md", ".yml", ".yaml", ".json"))


def main() -> int:
    errors: list[str] = []

    if not MATRIX_PATH.exists():
        print(f"ERROR: missing {MATRIX_PATH}")
        return 1
    if not EVENTS_PATH.exists():
        print(f"ERROR: missing {EVENTS_PATH}")
        return 1

    matrix = _read_yaml(MATRIX_PATH)
    rows = matrix.get("rows", {})
    if not isinstance(rows, dict):
        print("ERROR: invalid claims/CLAIM_STATUS_MATRIX.yml rows")
        return 1

    doc = _read_yaml(EVENTS_PATH)
    events = doc.get("events", [])
    if not isinstance(events, list):
        print("ERROR: website/claim_events.yml events must be a list")
        return 1

    seen_ids: set[str] = set()
    last_global_ts: datetime | None = None
    claim_histories: dict[str, list[dict[str, Any]]] = {}

    required_top = [
        "event_id",
        "claim_id",
        "from_status",
        "to_status",
        "promoted_at_utc",
        "headlines",
        "significance_summaries",
        "not_claimed",
        "evidence",
        "verified_by",
        "verification_run_id",
    ]

    for idx, ev in enumerate(events):
        ctx = f"event[{idx}]"
        if not isinstance(ev, dict):
            errors.append(f"{ctx}: must be a mapping")
            continue

        for key in required_top:
            if key not in ev:
                errors.append(f"{ctx}: missing required field '{key}'")

        event_id = str(ev.get("event_id", "")).strip()
        claim_id = str(ev.get("claim_id", "")).strip()
        from_status_raw = str(ev.get("from_status", "")).strip()
        to_status_raw = str(ev.get("to_status", "")).strip()
        from_status = _canonical_status(from_status_raw)
        to_status = _canonical_status(to_status_raw)
        promoted_at_utc = str(ev.get("promoted_at_utc", "")).strip()

        if not event_id:
            errors.append(f"{ctx}: empty event_id")
        elif event_id in seen_ids:
            errors.append(f"{ctx}: duplicate event_id '{event_id}'")
        else:
            seen_ids.add(event_id)

        if not claim_id:
            errors.append(f"{ctx}: empty claim_id")
        elif claim_id not in rows:
            errors.append(f"{ctx}: unknown claim_id '{claim_id}'")

        if from_status_raw not in ALLOWED_STATUS:
            errors.append(f"{ctx}: invalid from_status '{from_status_raw}'")
        if to_status_raw not in ALLOWED_STATUS:
            errors.append(f"{ctx}: invalid to_status '{to_status_raw}'")
        if from_status in ALLOWED_TRANSITIONS and to_status not in ALLOWED_TRANSITIONS[from_status]:
            errors.append(f"{ctx}: disallowed transition '{from_status_raw}' -> '{to_status_raw}'")

        ts = _parse_utc(promoted_at_utc)
        if ts is None:
            errors.append(f"{ctx}: invalid promoted_at_utc '{promoted_at_utc}'")
        else:
            if last_global_ts is not None and ts < last_global_ts:
                errors.append(f"{ctx}: timestamps must be monotonic non-decreasing")
            last_global_ts = ts

        for section_name in ("headlines", "significance_summaries"):
            section = ev.get(section_name)
            if not isinstance(section, dict):
                errors.append(f"{ctx}: {section_name} must be a mapping")
                continue
            for tier in TIERS:
                if not _is_nonempty_str(section.get(tier)):
                    errors.append(f"{ctx}: {section_name}.{tier} is required")

        not_claimed = ev.get("not_claimed")
        if not isinstance(not_claimed, list) or not not_claimed:
            errors.append(f"{ctx}: not_claimed must be a non-empty list")
        else:
            for i, line in enumerate(not_claimed):
                if not _is_nonempty_str(line):
                    errors.append(f"{ctx}: not_claimed[{i}] must be a non-empty string")

        evidence = ev.get("evidence")
        if not isinstance(evidence, dict):
            errors.append(f"{ctx}: evidence must be a mapping")
        else:
            claim_file = str(evidence.get("claim_file", "")).strip()
            if not claim_file:
                errors.append(f"{ctx}: evidence.claim_file required")
            else:
                claim_path = ROOT / claim_file
                if not claim_path.exists():
                    errors.append(f"{ctx}: evidence.claim_file not found: {claim_file}")

            owner_rfc = str(evidence.get("owner_rfc", "")).strip()
            if owner_rfc:
                owner_path = ROOT / _extract_file_ref(owner_rfc)
                if _path_like(owner_rfc) and not owner_path.exists():
                    errors.append(f"{ctx}: evidence.owner_rfc path missing: {owner_rfc}")

            evidence_artifact_count = 0
            for key in ("lean_artifacts", "battery_artifacts", "python_artifacts"):
                refs = evidence.get(key, [])
                if not isinstance(refs, list):
                    errors.append(f"{ctx}: evidence.{key} must be a list")
                    continue
                evidence_artifact_count += len([r for r in refs if isinstance(r, str) and r.strip()])
                for ref in refs:
                    if not isinstance(ref, str):
                        continue
                    ref = ref.strip()
                    if not ref or not _path_like(ref):
                        continue
                    path = ROOT / _extract_file_ref(ref)
                    if not path.exists():
                        errors.append(f"{ctx}: missing artifact path in evidence.{key}: {ref}")

            if evidence_artifact_count == 0:
                errors.append(f"{ctx}: at least one verification artifact is required")

        if claim_id:
            claim_histories.setdefault(claim_id, []).append(ev)

    # Per-claim chain consistency and matrix alignment.
    for claim_id, history in claim_histories.items():
        ordered = sorted(
            history,
            key=lambda e: _parse_utc(str(e.get("promoted_at_utc", ""))) or datetime.min,
        )
        prev_to: str | None = None
        for i, ev in enumerate(ordered):
            event_id = str(ev.get("event_id", ""))
            from_status = _canonical_status(str(ev.get("from_status", "")))
            to_status = _canonical_status(str(ev.get("to_status", "")))
            if i > 0 and prev_to is not None and from_status != prev_to:
                errors.append(
                    f"{event_id}: chain mismatch for {claim_id} "
                    f"(from_status={from_status}, expected {prev_to})"
                )
            prev_to = to_status

        latest_to_status = _canonical_status(str(ordered[-1].get("to_status", "")))
        matrix_status = _canonical_status(str(rows.get(claim_id, {}).get("status", "")))
        if matrix_status and latest_to_status != matrix_status:
            errors.append(
                f"{claim_id}: latest event to_status={latest_to_status} "
                f"does not match matrix status={matrix_status}"
            )

    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"OK: validated {len(events)} claim events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

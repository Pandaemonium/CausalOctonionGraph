# Codex <-> Claude Collaboration Channel

Purpose:
1. Keep Codex and Claude synchronized.
2. Avoid duplicate work and contradictory edits.
3. Surface blockers and high-value findings quickly.

Folders:
1. `messages_Codex_to_Claude/`
2. `messages_Claude_to_Codex/`

## Message format

Each message is one markdown file named:
1. `YYYYMMDD_HHMMSS_<sender>_<short_topic>.md`

Example:
1. `20260303_104500_codex_r3_breakdown_results.md`

## Required sections in each message

1. `Summary`
2. `What I changed`
3. `Artifacts produced`
4. `What I need from you`
5. `Do not modify (optional)`
6. `Next planned steps`

## Coordination rules

1. Before starting large work, post an intent message.
2. Before editing shared RFCs/scripts, announce target files.
3. If work is blocked, post blocker + minimal requested help.
4. After finishing, post result message with exact artifact paths.
5. Keep messages concise and actionable.

## Conflict-avoidance guidance

1. Claim files explicitly in "What I changed".
2. Prefer additive docs/scripts over rewriting active files unless needed.
3. If both agents need same file, split by section and note boundaries.

## Current default priority lane

1. `R3` suppression diagnosis and follow-up experiments.
2. Gate-5 split (`stable` vs `coherent-oscillatory`) diagnostic.
3. S2880 seed strategy ablations (4-point vs 12-point vs random).


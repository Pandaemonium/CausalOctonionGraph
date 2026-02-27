# Skeptic Claim-by-Claim Review Template

Use this file as `skeptic_claim_review.md` in each reviewable task context pack.

## Metadata
- task_id:
- producer_worker:
- skeptic_worker:
- producer_model:
- skeptic_model:
- reviewed_at_utc:

## Verdict Summary
- overall_status: PASS | PASS_WITH_LIMITS | FAIL | MIXED
- claims_reviewed_count:
- claims_pass_count:
- claims_pass_with_limits_count:
- claims_fail_count:

## Claim-by-Claim Table
| claim_id | verdict | replay_check | defect_or_limit | evidence_paths |
|---|---|---|---|---|
| CLAIM-XXX | PASS/PASS_WITH_LIMITS/FAIL | what was rerun/rechecked | limits or defects | file paths, theorem ids, test ids |

## Salvage Section (Required)
List valid sub-results even if parent task failed.

| salvaged_item_id | source_claim_id | why_valid | reusable_artifact | proposed_followup_task |
|---|---|---|---|---|
| SALVAGE-001 | CLAIM-XXX | brief rationale | file/theorem/test path | one sentence |

## Required Defects for Failed Claims
For each failed claim, include:
1. exact defect,
2. minimal reproducer,
3. repair instruction.

## Promotion Recommendation
- promote_now_claims:
- hold_claims:
- reroute_tasks:

# Public Proof Ledger Implementation Plan

Status: Draft  
Owner: Research Director + Clerk Team  
Audience: Public watchers, professional physicists, internal reviewers  
Last Updated: 2026-02-27

## 1. Goal

Build a public-facing "Proof Ledger" experience that is:
1. Engaging for general audiences,
2. Informative for technical readers,
3. Rigorous enough for scientific scrutiny,
4. Maintained safely by clerks with low operational burden.

Core user promise:
1. "Show me what was upgraded."
2. "Tell me when it happened."
3. "Show me exactly why I should trust it."

## 2. Product Success Criteria

1. Every status upgrade is visible with relative time (`10 minutes ago`) and exact UTC.
2. Every public claim card has evidence links and an explicit "not claimed" boundary.
3. No claim can appear as upgraded without passing validation gates.
4. Clerk publish flow takes less than 10 minutes for a normal promotion event.
5. Public users can filter by status, topic, and recency window.
6. The UI successfully communicates the *connected nature* of the research, showing how early proofs unlock later hypotheses.

## 3. Public Experience Vision

To make the research journey captivating and accessible, the ledger must go beyond a simple changelog. It should feel like tracking a live, monumental expedition.

### 3.1 Hero Section: "The Discovery Tech Tree"

Instead of a standard list, the primary visualization is an interactive **Knowledge Graph** (or "Tech Tree").
1. **Visual Metaphor:** Claims are nodes connected by prerequisite edges.
2. **Engagement Loop:** When a foundational claim is upgraded to `proved` (deep green), users visually see the "energy" or "unlock" status flow down the edges to dependent active hypotheses.
3. **Context at a Glance:** This instantly answers *why* an abstract mathematical proof matters (e.g., "Proving this topological lemma just unlocked the pathway to proving the Muon Mass").
4. **Live Counters:**
   - `proved`
   - `supported`
   - `open / in-progress`
5. **"Newest Upgrade" Spotlight Card:** Overlaid on the tree, showing the latest headline, relative time, and primary evidence link.

### 3.2 The "Complexity Toggle" (ELI5 to PhD)

To serve multiple audiences simultaneously without cluttering the UI, a global toggle controls the text density and vocabulary of the ledger.
- **`[ Layman ] -- [ Student ] -- [ Physicist ]`**
- Changing the toggle dynamically rewrites headlines and summaries in the feed.
  - *Layman:* "We proved that particles can have a built-in clock."
  - *Student:* "We verified the topological depth acts as an interaction clock."
  - *Physicist:* "Verified `tau_int` monotonicity and deterministic `kMultiplicity` in Kernel v2."
- *Clerk Role:* Local Qwen-3 models automatically generate these three tiers of summaries for every promotion event during the publish flow.

### 3.3 Upgrade Feed (Primary Feed Surface)

1. Reverse-chronological feed of status transitions (append-only history) sitting below or beside the Tech Tree.
2. Each feed row shows:
   - Claim ID and dynamically toggled headline.
   - Transition (`partial -> supported`, `supported -> proved`).
   - Relative time and exact UTC.
   - Verification bundle links.
3. **Gamification & Clerk Persona:** The UI should note which autonomous agent made the update (e.g., *"Ledger updated by System Clerk Qwen-3"*). Include "Streak" counters for sustained progress (e.g., *"3 consecutive weeks with a topological proof upgrade!"*).

### 3.4 Claim Detail Pages & "Proof Path" Breadcrumbs

When a user clicks into a specific claim:
1. Dynamic summaries (respecting the Complexity Toggle).
2. **"How we got here" (Proof Path):** An auto-generated visual breadcrumb trail showing the 3-4 prerequisite claims that had to be proven first to make this specific upgrade possible.
3. Evidence bundle with direct file/test/theorem references.
4. Full status timeline.
5. "Not claimed" section to prevent overstatement.

### 3.5 Automated Social "Hype" Cards (OpenGraph)

To encourage public sharing and program hype:
1. The CI pipeline auto-generates a striking OpenGraph image for every `claim_events.yml` entry.
2. When a link is shared on social media, the preview card prominently displays: **"🔓 PROVED: [Layman Headline]. [Read the Proof]"** with strong project branding.

## 4. Clerk-Maintained Data Model

Design requirement: no database needed, no manual "relative time" maintenance.

## 4.1 Source files

1. `claims/CLAIM_STATUS_MATRIX.yml` remains authoritative for current status.
2. New append-only file: `website/claim_events.yml` stores promotion history.
3. Existing `website/accomplishments.yml` remains curated highlight content.
4. **NEW:** `claims/dependencies.yml` (or added to existing claim files) to explicitly map prerequisite edges for the Tech Tree.

## 4.2 Proposed `website/claim_events.yml` schema

```yaml
schema_version: "1.1.0"
events:
  - event_id: "EVT-20260227-0001"
    claim_id: "WEINBERG-UV-001"
    from_status: "partial"
    to_status: "supported"
    promoted_at_utc: "2026-02-27T01:18:42Z"
    headlines:
      layman: "We confirmed the underlying structure that determines how forces mix."
      student: "We verified the exclusive-U1 invariant for weak-mixing."
      physicist: "Exclusive-U1 weak-mixing invariant promoted to supported."
    significance_summaries:
      layman: "This is a major step toward proving exactly why the Weak force behaves the way it does."
      student: "This locks in a key structural value needed to derive the Weinberg angle."
      physicist: "Locks a machine-checked electroweak UV structural value required for macroscopic coupling limits."
    evidence:
      claim_file: "claims/WEINBERG-UV-001.yml"
      owner_rfc: "rfc/RFC-029_Weinberg_Angle_Gap_Closure.md"
      lean_artifacts:
        - "CausalGraph.sin2ThetaWObs_exclusive_u1_eq_one_four"
      battery_artifacts:
        - "calc/test_weinberg_h2_governance.py::test_expected_baseline_values"
    verified_by: "Clerk Qwen-3"
    verification_run_id: "battery_v2_20260227_0112Z"
```

## 4.3 Time display contract

1. Store only canonical UTC timestamps in data (`promoted_at_utc`).
2. Render relative time in browser or render step.
3. Always show exact UTC on click/expand.
4. Never hand-write strings like "5 hours ago."

## 5. Governance and Validation

## 5.1 New validator script

Create `scripts/validate_claim_events.py` with gates:
1. Required fields exist for every event (including all 3 complexity tiers for headlines/summaries).
2. Timestamp format is strict ISO-8601 UTC (`Z`).
3. Status transitions are allowed by policy.
4. Latest event status for each claim matches `CLAIM_STATUS_MATRIX.yml`.
5. Every event has at least one verification artifact.
6. `event_id` uniqueness and monotonic timestamp ordering.

## 5.2 Existing validator alignment

Extend `scripts/validate_public_accomplishments.py` checks:
1. If a card says status `supported` or `proved`, there must be a corresponding promotion event.
2. Evidence references must resolve to existing files/tests/theorems.
3. `last_verified_at` must be greater than or equal to last promotion timestamp.

## 5.3 CI policy

Add CI job stages:
1. `validate_claim_matrix`
2. `validate_claim_events`
3. `validate_public_accomplishments`
4. `build_proof_ledger_artifacts`
5. `generate_social_cards` (New step for OpenGraph images)

Fail closed on schema or transition violations.

## 6. Build Pipeline (Static-Site Friendly)

## 6.1 Generator script

Create `scripts/build_proof_ledger_artifacts.py`:
1. Read matrix + events + accomplishments + dependencies.
2. Emit `website/data/claim_events.json`.
3. Emit `website/data/claims_index.json`.
4. Emit `website/data/tech_tree.json` (for the Knowledge Graph visualization).
5. Emit optional `website/pages/results_live.md` fragment from templates.

## 6.2 Frontend rendering targets

1. Keep current `website/pages/accomplishments.md` as curated narrative.
2. Add new page `website/pages/proof_ledger.md` as the live status/timeline surface.
3. Build the interactive Tech Tree component (e.g., using D3.js or similar React visualization library).
4. Optionally route `/web/results` to `proof_ledger` once parity is reached.

## 7. Content and Copy Rules for Clerks

1. **Complexity Tiering is Mandatory:** Clerks *must* generate the `layman`, `student`, and `physicist` summaries for every event.
2. Public headline max 110 characters per tier.
3. Public significance must answer "why this matters" in one sentence.
4. No superlatives without explicit evidence links.
5. Every event must include one "not claimed" boundary sentence in claim card context.

## 8. Visual Direction (Captivating but Serious)

1. Tone: "Scientific newsroom meets interactive discovery."
2. Color semantics:
   - `proved`: deep green
   - `supported`: vibrant blue
   - `partial`: amber
   - `active_hypothesis`: violet-gray
   - `superseded`: neutral gray with strike badge
3. Motion:
   - Smooth pan/zoom on the Tech Tree.
   - Satisfying "pulse" or "flow" animation along tree edges when a node upgrades to `proved`.
   - Soft entry animation for new feed rows.
4. Typography:
   - Large, high-contrast status labels.
   - Clean sans-serif for readability across complexity toggles.

## 9. File-by-File Implementation Plan

## 9.1 Create

1. `website/claim_events.yml`
2. `website/pages/proof_ledger.md`
3. `scripts/validate_claim_events.py`
4. `scripts/build_proof_ledger_artifacts.py`
5. `scripts/generate_social_cards.py`
6. `website/data/claim_events.json` (generated)
7. `website/data/claims_index.json` (generated)
8. `website/data/tech_tree.json` (generated)

## 9.2 Update

1. `website/pages/accomplishments.md`
   - add pointer to live Proof Ledger page.
2. `website/accomplishments.yml`
   - add optional field `last_promotion_event_id` for each card.
3. `scripts/validate_public_accomplishments.py`
   - cross-check with promotion events.
4. `website/intro.md`
   - update "Results" link copy to highlight live upgrade timestamps.
5. `claims/*.yml` (Iterative update to include `depends_on` lists for the Tech Tree).

## 10. Rollout Plan

## Phase 1 (Data & Backend MVP, 2-3 days)

1. Add `claim_events.yml` (with complexity tiers).
2. Add event validator.
3. Build simple feed page with relative times and complexity toggle.

## Phase 2 (The Tech Tree & Visuals, 4-7 days)

1. Map dependencies between claims.
2. Build and integrate the interactive Tech Tree visualization.
3. Add "Proof Path" breadcrumbs to detail pages.
4. Implement Social Card (OpenGraph) auto-generation in CI.

## Phase 3 (Public launch)

1. Switch `/web/results` primary content to Proof Ledger.
2. Keep accomplishments page as editorial highlight layer.
3. Publish governance note describing validation criteria.

## 11. Clerk Operating Checklist

For each promotion:
1. Update claim status in `claims/*.yml` and matrix.
2. **Generate Layman, Student, and Physicist summaries.**
3. Append event to `website/claim_events.yml`.
4. Update affected highlight card if needed.
5. Run:
   - `python scripts/validate_claim_events.py`
   - `python scripts/validate_public_accomplishments.py`
   - `python scripts/build_proof_ledger_artifacts.py`
6. Open PR with promotion summary and evidence links.

## 12. Definition of Done

This project is complete when:
1. Public page features an interactive Discovery Tech Tree showing claim relationships.
2. Users can dynamically toggle the complexity of the ledger (Layman/Student/Physicist).
3. Promotion history is append-only, visible, and shows relative + absolute times.
4. Every displayed claim is backed by linked evidence and "How we got here" breadcrumbs.
5. Automated social cards are generated for every upgrade.
6. Clerks can reliably maintain the multi-tiered system using local models during routine operation.
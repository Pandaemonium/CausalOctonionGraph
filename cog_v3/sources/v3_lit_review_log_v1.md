# v3 Literature Review Log (v1)

Date started: 2026-03-02  
Owner: Codex (overnight autonomous run)  
Scope: Immediate blockers + long-horizon enablers

## 1. Purpose

Capture concise, high-signal literature findings in a format that is:

1. fast to append during active runs,
2. easy to convert into code/RFC decisions,
3. auditable for preregistered claims.

## 2. Entry Template

Use one block per literature cycle:

1. `timestamp`:
2. `focus_type`: `blocker` or `long_horizon`
3. `question`:
4. `sources_checked`:
5. `key_finding`:
6. `confidence`: `low`, `medium`, `high`
7. `immediate_action`: `apply`, `defer`, or `reject`
8. `reason`:
9. `linked_artifacts`:
10. `follow_up_test`:

## 3. Initial Seed Topics

1. Wave-layer two-front transport vs detector-layer exclusivity criteria.
2. Chiral gating constructions in discrete/lattice systems.
3. Active-search methods for sparse attractor discovery.
4. Coarse-graining motifs into stable mesoscopic descriptors.
5. Symmetry-based pruning for multiplicative finite alphabets.

## 4. Running Entries

### Entry 2026-03-02T00:00:00-08:00

1. `focus_type`: `long_horizon`
2. `question`: What search-policy frameworks can reduce expensive brute-force scans?
3. `key_finding`: Maintain a dual track:
   - exploitation around top candidates,
   - exploration with novelty/diversity pressure.
4. `confidence`: `medium`
5. `immediate_action`: `apply`
6. `reason`: Fits current finite-compute constraints and complements fail-fast.
7. `follow_up_test`: Add novelty score to candidate ranking and measure top-k yield.

### Entry 2026-03-02T00:00:00-08:00-B

1. `focus_type`: `blocker`
2. `question`: Should two-front wave occupancy automatically reject photon candidates?
3. `key_finding`: No. Require detector-layer exclusivity tests before rejection.
4. `confidence`: `high`
5. `immediate_action`: `apply`
6. `reason`: Avoids conflating wave support geometry with event outcomes.
7. `linked_artifacts`:
   - `cog_v3/rfc/RFC-002_Seeded_Event_Order_FailFast_and_Photon_Chirality_Hypotheses.md`
   - `cog_v3/rfc/RFC-003_e000_Anchor_Chirality_and_C_Asymmetry_Test_Contract.md`
8. `follow_up_test`: Implement twin-detector panels in photon finalist workflow.

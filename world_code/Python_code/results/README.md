# results

Campaign outputs from `run_world_code_campaign.py` are written here.

Per campaign:
1. `manifest.json`
2. `campaign_summary.json`
3. one subfolder per example, each with:
   - `step_XXXX.json` final world state at that step count,
   - `summary.json` metrics trace.

These are raw-state artifacts for later representation-layer extraction:
1. edge-count distance observables,
2. axis-weight observables (e0/e7 and related),
3. motif-interaction recurrence and scale scans.


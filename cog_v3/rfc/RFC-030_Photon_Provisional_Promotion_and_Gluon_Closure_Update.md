# RFC-030: Photon Provisional Promotion and Gluon Closure Update

Status: Draft
Date: 2026-03-03
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-025_Gauge_Boson_Identification_in_S2880.md`
- `cog_v3/rfc/RFC-029_Photon_Z4_Phase_Excitation_Wave_Emergence_and_EM_Identification.md`
- `cog_v3/python/kernel_s2880_pair_conservative_v1.py`
- `cog_v3/calc/build_v3_s2880_boson_closure_probe_v1.py`

---

## 1. Purpose

This RFC executes two immediate actions:

1. Promote the photon lane from "candidate" to "provisionally promoted" in the current
   S2880 process-lane framework.
2. Run extended closure on the gluon-proxy lane and report geometry sensitivity.

This is an additive operational update. It does not rewrite RFC-025/RFC-029.

---

## 2. Run Configuration

Tool:
- `python -m cog_v3.calc.build_v3_s2880_boson_closure_probe_v1`

Common parameters:
- `top_n=24`
- `ticks=48`
- `grid=9x9x9`
- `boundary_mode=fixed_vacuum`
- `global_seed=20260303`
- `vacuum_phase=0`
- kernel: `cog_v3_s2880_pair_conservative_v1`

Stencils tested:
- `axial6`
- `cube26`

Artifacts:
- `cog_v3/sources/v3_s2880_boson_closure_probe_v1_axial6_t48.json`
- `cog_v3/sources/v3_s2880_boson_closure_probe_v1_axial6_t48.md`
- `cog_v3/sources/v3_s2880_boson_closure_probe_v1_cube26_t48.json`
- `cog_v3/sources/v3_s2880_boson_closure_probe_v1_cube26_t48.md`

---

## 3. Results Summary

### 3.1 Photon lane

Observed:
- axial6: closure `0.8978`, lane fraction `0.9167`, survival `0.9167`
- cube26: closure `0.8983`, lane fraction `0.9167`, survival `0.9167`

Top seeds remain the phase-lifted `(+e000)` family, e.g.:
- `s_id 2879 = zeta12^11*(1*e000)` (closure ~0.9833 in cube26 run)
- `s_id 959 = zeta12^3*(1*e000)` (closure ~0.9825 in cube26 run)

Interpretation:
- Photon lane is stable across both tested geometries with near-identical statistics.
- This supports immediate provisional promotion.

### 3.2 Gluon-proxy lane

Observed:
- axial6: closure `0.5559`, lane fraction `0.3727`, survival `1.0000`
- cube26: closure `0.6853`, lane fraction `0.5865`, survival `1.0000`

Top seeds are consistent pure-imaginary A16 `e001` phase-lifts, e.g.:
- `s_id 1017 = zeta12^4*(-1*e001)`
- `s_id 2457 = zeta12^10*(-1*e001)`
- `s_id 57 = -1*e001`

Interpretation:
- The gluon-proxy lane survives strongly as a process lane in both stencils.
- Closure quality improves materially under cube26.
- Lane remains "proxy" (not yet a finalized gluon identity contract).

---

## 4. Promotion Decision

### 4.1 Photon

Decision: **Provisional Promote**

New status:
- `PHOTON_PROVISIONAL_V1`

Meaning:
- The photon lane is now treated as a promoted working channel for downstream search and
  interaction tests.
- Promotion is based on repeated closure under current kernel semantics and geometry
  robustness across axial6 and cube26 at 48 ticks.

Not implied by this promotion:
- Final detector-model semantics are solved.
- Final edge-vs-site architecture is solved.
- Full QED-equivalent reconstruction is solved.

### 4.2 Gluon-proxy

Decision: **Continue as Active Proxy Lane**

New status:
- `GLUON_PROXY_ACTIVE_V1`

Meaning:
- Keep as a prioritized channel for additional closure and interaction stress tests.
- Do not yet declare finalized gluon mapping.

---

## 5. Immediate Next Steps

1. Run same closure battery at `ticks=96` for both stencils.
2. Add packet-seed tests (multi-voxel) for gluon-proxy interaction behavior.
3. Add interaction panels:
   - photon-lane with charged motif candidates,
   - gluon-proxy lane with quark-core lane candidates.
4. Add one concise gate report that separates:
   - process-lane closure,
   - detector-level hypotheses,
   - architecture assumptions.

---

## 6. Notes

This RFC is intentionally operational: it records what was run and what was promoted now.
It avoids rewriting the older theoretical RFC text in this commit.


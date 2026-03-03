"""Canonical COG engine (single-source runtime semantics).

This module enforces one engine definition:
1) fully coherent lightcone,
2) path-product update via deterministic fold-order multiplication.

All new analysis lanes should route through this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from cog_v3.python import kernel_cog_v4_coherence as kc


ENGINE_PROFILE = "cog_v4_coherent_lightcone_fold_v1"


@dataclass(frozen=True)
class SiteSeed:
    """Per-site canonical seed tuple in the requested factorization."""

    domain: int  # Z3
    oct_basis: int  # 0..7 basis index for current coherence engine state
    energy_n: int  # Z>=0
    energy_phase: int  # Z4
    sign: int = 1  # {-1,+1}


def _state_from_seed(seed: SiteSeed) -> kc.State:
    return kc.State(
        g=int(seed.domain) % 3,
        a=int(seed.energy_phase) % 4,
        e=int(seed.energy_n),
        sign=int(seed.sign),
        basis=int(seed.oct_basis) % 8,
    )


def uniform_seed(seed: SiteSeed) -> kc.SeedConfig:
    """Assign same canonical seed tuple to every F2^3 site."""
    st = _state_from_seed(seed)
    return {s: st for s in kc.F2_SITES}


def seed_from_site_map(
    default_seed: SiteSeed,
    overrides: Dict[Tuple[int, int, int], SiteSeed],
) -> kc.SeedConfig:
    """Build SeedConfig from canonical tuples with per-site overrides."""
    cfg = uniform_seed(default_seed)
    for s, sd in overrides.items():
        cfg[s] = _state_from_seed(sd)
    return cfg


def lightcone_trace(
    *,
    seed_cfg: kc.SeedConfig,
    horizon: int,
    origin: Tuple[int, int, int] = (0, 0, 0),
    s_rule: Optional[kc.SRule] = None,
) -> Dict[str, object]:
    """Run canonical engine trace and return coherence summary + details."""
    kernel = kc.COGKernel(cfg=seed_cfg, origin=origin, s_rule=s_rule)
    ok, viol = kernel.physical(horizon=int(horizon))
    points: List[Dict[str, object]] = []
    for t in range(1, int(horizon) + 1):
        for s in kc.F2_SITES:
            pt = kernel.future_state_detailed(s, int(t))
            points.append(
                {
                    "coords": tuple(s),
                    "t": int(t),
                    "status": str(pt.status),
                    "state": None
                    if pt.state is None
                    else {
                        "g": int(pt.state.g),
                        "a": int(pt.state.a),
                        "e": int(pt.state.e),
                        "sign": int(pt.state.sign),
                        "basis": int(pt.state.basis),
                    },
                    "n_paths": int(pt.n_paths),
                    "n_disagreeing": int(pt.n_disagreeing),
                }
            )
    return {
        "engine_profile": ENGINE_PROFILE,
        "physical": bool(ok),
        "violation": None
        if viol is None
        else {
            "coords": tuple(viol.coords),
            "t": int(viol.t),
            "status": str(viol.status),
            "n_paths": int(viol.n_paths),
            "n_disagreeing": int(viol.n_disagreeing),
        },
        "points": points,
    }


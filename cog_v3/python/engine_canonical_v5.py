"""Canonical COG v5 engine.

Single execution lane:
  - coherent lightcone semantics (no Markov stepping),
  - path-product update on F2^3,
  - explicit profile tag for replay and citation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from cog_v3.python import kernel_cog_v5_coherence as kv5


ENGINE_PROFILE = kv5.KERNEL_PROFILE


@dataclass(frozen=True)
class SiteSeed:
    """Per-site seed in Z3 x O x Z x Z4."""

    domain: int       # Z3
    oct_basis: int    # 0..7
    energy_n: int     # Z>=0
    energy_phase: int # Z4
    sign: int = 1     # {-1,+1}


def _state_from_seed(seed: SiteSeed) -> kv5.State:
    return kv5.State(
        g=int(seed.domain) % 3,
        a=int(seed.energy_phase) % 4,
        e=int(seed.energy_n),
        sign=int(seed.sign),
        basis=int(seed.oct_basis) % 8,
    )


def uniform_seed(seed: SiteSeed) -> kv5.SeedConfig:
    st = _state_from_seed(seed)
    return {s: st for s in kv5.F2_SITES}


def seed_from_site_map(
    default_seed: SiteSeed,
    overrides: Dict[Tuple[int, int, int], SiteSeed],
) -> kv5.SeedConfig:
    cfg = uniform_seed(default_seed)
    for s, sd in overrides.items():
        cfg[s] = _state_from_seed(sd)
    return cfg


def lightcone_trace(
    *,
    seed_cfg: kv5.SeedConfig,
    horizon: int,
    origin: Tuple[int, int, int] = (0, 0, 0),
    s_rule: Optional[kv5.SRule] = None,
) -> Dict[str, object]:
    spec = kv5.KernelV5Spec(origin=origin, s_rule=s_rule)
    kernel = kv5.make_kernel(seed_cfg, spec=spec)
    ok, viol = kernel.physical(horizon=int(horizon))
    points: List[Dict[str, object]] = []
    for t in range(1, int(horizon) + 1):
        for s in kv5.F2_SITES:
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

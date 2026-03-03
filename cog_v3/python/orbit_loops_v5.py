"""Orbit/loop analysis tools for v5 coherent-lightcone kernel.

Goal:
- find coherent periodic loops in a closed "single excitation in vacuum-like"
  system without assuming periodicity by construction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from cog_v3.python import kernel_cog_v5_coherence as kv5


Coords = Tuple[int, int, int]


@dataclass(frozen=True)
class LoopResult:
    seed_g: int
    seed_a: int
    seed_basis: int
    seed_sign: int
    seed_e: int
    excite_site: Coords
    target: Coords
    horizon: int
    physical: bool
    period: Optional[int]
    first_repeat_at: Optional[int]
    coherent_samples: int
    incoherent_samples: int


def state_key(st: kv5.State) -> Tuple[int, int, int, int, int]:
    return (int(st.g), int(st.a), int(st.basis), int(st.sign), int(st.e))


def single_excitation_seed(
    *,
    g: int,
    a: int,
    basis: int,
    sign: int,
    e: int,
    excite_site: Coords = (1, 1, 1),
) -> kv5.SeedConfig:
    cfg = kv5.vacuum_seed()
    cfg[excite_site] = kv5.State(g=g, a=a, basis=basis, sign=sign, e=e)
    return cfg


def detect_period(keys: List[Tuple[int, int, int, int, int]]) -> Tuple[Optional[int], Optional[int]]:
    """Return (period, first_repeat_index) if a stable period is detected."""
    seen: Dict[Tuple[int, int, int, int, int], int] = {}
    for i, k in enumerate(keys):
        if k in seen:
            j = seen[k]
            p = i - j
            if p <= 0:
                continue
            ok = True
            for t in range(i, len(keys)):
                if keys[t] != keys[j + ((t - j) % p)]:
                    ok = False
                    break
            if ok:
                return p, i
        else:
            seen[k] = i
    return None, None


def analyze_single_excitation_loop(
    *,
    g: int,
    a: int,
    basis: int,
    sign: int,
    e: int,
    excite_site: Coords = (1, 1, 1),
    target: Coords = (1, 1, 1),
    horizon: int = 48,
    origin: Coords = (0, 0, 0),
    s_rule: Optional[kv5.SRule] = None,
) -> LoopResult:
    cfg = single_excitation_seed(
        g=g,
        a=a,
        basis=basis,
        sign=sign,
        e=e,
        excite_site=excite_site,
    )
    kernel = kv5.make_kernel(cfg, spec=kv5.KernelV5Spec(origin=origin, s_rule=s_rule))
    physical, _viol = kernel.physical(horizon=int(horizon))

    keys: List[Tuple[int, int, int, int, int]] = []
    coherent_samples = 0
    incoherent_samples = 0

    for t in range(1, int(horizon) + 1):
        if not kernel.is_reachable(target, t):
            continue
        pt = kernel.future_state_detailed(target, t)
        if pt.status == kv5.COHERENT and pt.state is not None:
            coherent_samples += 1
            keys.append(state_key(pt.state))
        elif pt.status == kv5.INCOHERENT:
            incoherent_samples += 1

    period, first_repeat = detect_period(keys) if keys else (None, None)

    return LoopResult(
        seed_g=int(g) % 3,
        seed_a=int(a) % 4,
        seed_basis=int(basis) % 8,
        seed_sign=1 if int(sign) >= 0 else -1,
        seed_e=int(e),
        excite_site=tuple(excite_site),
        target=tuple(target),
        horizon=int(horizon),
        physical=bool(physical),
        period=period,
        first_repeat_at=first_repeat,
        coherent_samples=coherent_samples,
        incoherent_samples=incoherent_samples,
    )


def scan_single_excitation_loops(
    *,
    g_values: List[int],
    a_values: List[int],
    basis_values: List[int],
    sign_values: List[int],
    e_values: List[int],
    excite_site: Coords = (1, 1, 1),
    target: Coords = (1, 1, 1),
    horizon: int = 48,
    origin: Coords = (0, 0, 0),
    s_rule: Optional[kv5.SRule] = None,
) -> List[LoopResult]:
    out: List[LoopResult] = []
    for g in g_values:
        for a in a_values:
            for basis in basis_values:
                for sign in sign_values:
                    for e in e_values:
                        out.append(
                            analyze_single_excitation_loop(
                                g=g,
                                a=a,
                                basis=basis,
                                sign=sign,
                                e=e,
                                excite_site=excite_site,
                                target=target,
                                horizon=horizon,
                                origin=origin,
                                s_rule=s_rule,
                            )
                        )
    return out

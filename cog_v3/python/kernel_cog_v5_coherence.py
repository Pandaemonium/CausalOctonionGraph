"""COG v5 Kernel -- canonical coherent-lightcone profile.

v5 is a clean profile freeze of the v4 coherence kernel:
  - same non-Markov semantics (global lightcone coherence),
  - same state algebra (Z3 x Z4 x O with E in Z>=0),
  - same coherence rule (deterministic fold over complete causal past),
  - explicit profile/version contract for reproducibility.

Design choice:
  We intentionally reuse the proven v4 implementation as the execution core
  and lock a profile string for externally reproducible runs.

Architecture boundary:
  - Core kernel contract assumes complete causal past is available.
  - The concrete F2^3/cube retrieval mechanism is a supplementary backend
    (see `cog_v3/python/causal_past_contract_v1.py`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from cog_v3.python import kernel_cog_v4_coherence as v4


KERNEL_PROFILE = "cog_v5_coherent_lightcone_fold_v1"


# Re-export core algebra/geometry symbols for a stable public surface.
State = v4.State
MeasurementTarget = v4.MeasurementTarget
MeasurementVolume = v4.MeasurementVolume
MeasurementResult = v4.MeasurementResult
LightconePoint = v4.LightconePoint
SeedConfig = v4.SeedConfig
SRule = v4.SRule
F2_SITES = v4.F2_SITES
FANO_TRIPLES = v4.FANO_TRIPLES
COHERENT = v4.COHERENT
INCOHERENT = v4.INCOHERENT
NOT_IN_LIGHTCONE = v4.NOT_IN_LIGHTCONE

site_to_basis = v4.site_to_basis
basis_to_site = v4.basis_to_site
causal_neighbors = v4.causal_neighbors
hamming_distance = v4.hamming_distance
oct_mul = v4.oct_mul
all_paths = v4.all_paths
path_product = v4.path_product
backproject_to_start = v4.backproject_to_start

vacuum_seed = v4.vacuum_seed
basis_identity_seed = v4.basis_identity_seed
uniform_seed = v4.uniform_seed
generation_seed = v4.generation_seed
e7_e0_energy_probe_seed = v4.e7_e0_energy_probe_seed

s_rule_zero = v4.s_rule_zero
s_rule_fano_sign = v4.s_rule_fano_sign
s_rule_energy_gradient = v4.s_rule_energy_gradient
s_rule_basis_order = v4.s_rule_basis_order
select_s_rule_by_coherence = v4.select_s_rule_by_coherence


@dataclass(frozen=True)
class KernelV5Spec:
    """Runtime configuration for the v5 coherence kernel."""

    origin: Tuple[int, int, int] = (0, 0, 0)
    s_rule: Optional[SRule] = None


class COGKernelV5(v4.COGKernel):
    """v5 runtime kernel with a fixed profile identity."""

    profile: str = KERNEL_PROFILE


@dataclass
class COGv5Sim(v4.COGv4Sim):
    """v5 simulation wrapper over the coherence kernel core."""

    @property
    def profile(self) -> str:
        return KERNEL_PROFILE

    def __post_init__(self) -> None:
        self._kernel = COGKernelV5(cfg=self.seed, origin=self.origin)


def make_kernel(
    seed: SeedConfig,
    *,
    spec: KernelV5Spec = KernelV5Spec(),
) -> COGKernelV5:
    """Construct a v5 kernel instance from seed + spec."""
    return COGKernelV5(cfg=seed, origin=spec.origin, s_rule=spec.s_rule)


def coherence_certificate(
    seed: SeedConfig,
    *,
    horizon: int,
    spec: KernelV5Spec = KernelV5Spec(),
) -> Dict[str, object]:
    """Deterministic coherence report for reproducibility contracts."""
    kernel = make_kernel(seed, spec=spec)
    ok, viol = kernel.physical(horizon=int(horizon))
    return {
        "kernel_profile": KERNEL_PROFILE,
        "origin": tuple(spec.origin),
        "horizon": int(horizon),
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
    }

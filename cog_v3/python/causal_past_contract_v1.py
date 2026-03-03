"""Causal past contract (backend-agnostic) for COG kernels.

This module defines the abstraction boundary requested in v5:

- Core kernel axiom: updates are computed from the COMPLETE causal past.
- Backend mechanism: how that past is collected is a supplementary concern.

Current bundled backend:
- F2-cube (`F2^3`) retrieval, implemented via kernel_cog_v4_coherence helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, List, Protocol, Tuple

from cog_v3.python import kernel_cog_v4_coherence as v4


Coords = Tuple[int, int, int]
Path = Tuple[Coords, ...]


@dataclass(frozen=True)
class CausalTarget:
    """A spacetime target where a state is evaluated."""

    coords: Coords
    t_obs: int


class CausalPastProvider(Protocol):
    """Backend contract for collecting complete causal past data."""

    def is_reachable(self, origin: Coords, target: Coords, t: int) -> bool:
        """Return True iff target is causally reachable from origin at time t."""
        ...

    def paths(
        self,
        origin: Coords,
        target: Coords,
        t: int,
        *,
        max_paths: int,
    ) -> List[Path]:
        """Return complete causal paths contributing to (target, t)."""
        ...

    def backproject_support(
        self,
        targets: Iterable[CausalTarget],
        *,
        origin: Coords,
    ) -> FrozenSet[Coords]:
        """Return minimal initial-support set that can influence given targets."""
        ...


class F2CubePastProvider:
    """Supplementary backend: causal-past retrieval on F2^3 cube geometry."""

    def is_reachable(self, origin: Coords, target: Coords, t: int) -> bool:
        d = v4.hamming_distance(origin, target)
        return d <= t and (d % 2) == (t % 2)

    def paths(
        self,
        origin: Coords,
        target: Coords,
        t: int,
        *,
        max_paths: int = 50_000,
    ) -> List[Path]:
        return v4.all_paths(origin, target, t, max_paths=max_paths)

    def backproject_support(
        self,
        targets: Iterable[CausalTarget],
        *,
        origin: Coords = (0, 0, 0),
    ) -> FrozenSet[Coords]:
        mv = v4.MeasurementVolume(
            targets=[
                v4.MeasurementTarget(coords=t.coords, t_obs=int(t.t_obs))
                for t in targets
            ]
        )
        return v4.backproject_to_start(mv, origin=origin)


def active_sites_from_seed(
    seed: Dict[Coords, v4.State],
    *,
    vacuum_state: v4.State,
) -> FrozenSet[Coords]:
    """Return sites that deviate from a declared vacuum state."""
    return frozenset(s for s, st in seed.items() if st != vacuum_state)


class SparseCausalBackend:
    """Sparse retrieval backend on top of F2^3.

    Exactness contract (vacuum_identity_mode=True):
    1. non-active sites are exactly in the declared vacuum identity state,
    2. vacuum-only paths are product-equivalent (single representative is enough),
    3. all active-touching paths are retained.
    """

    def __init__(
        self,
        *,
        active_sites: FrozenSet[Coords],
        vacuum_identity_mode: bool = True,
    ) -> None:
        self.active_sites: FrozenSet[Coords] = frozenset(active_sites)
        self.vacuum_identity_mode: bool = bool(vacuum_identity_mode)
        self._dense = F2CubePastProvider()

    def is_reachable(self, origin: Coords, target: Coords, t: int) -> bool:
        return self._dense.is_reachable(origin, target, t)

    def _path_hits_active(self, path: Path) -> bool:
        return any(s in self.active_sites for s in path)

    def paths(
        self,
        origin: Coords,
        target: Coords,
        t: int,
        *,
        max_paths: int = 50_000,
    ) -> List[Path]:
        dense_paths = self._dense.paths(origin, target, t, max_paths=max_paths)
        if not self.vacuum_identity_mode:
            return dense_paths

        active_paths: List[Path] = []
        vacuum_rep: List[Path] = []
        for p in dense_paths:
            if self._path_hits_active(p):
                active_paths.append(p)
            elif not vacuum_rep:
                # One representative preserves the unique vacuum-only product class.
                vacuum_rep.append(p)
        return active_paths + vacuum_rep

    def backproject_support(
        self,
        targets: Iterable[CausalTarget],
        *,
        origin: Coords = (0, 0, 0),
    ) -> FrozenSet[Coords]:
        dense = self._dense.backproject_support(targets, origin=origin)
        if not self.vacuum_identity_mode:
            return dense
        # Keep only non-vacuum support that can influence targets.
        return frozenset(s for s in dense if s in self.active_sites)

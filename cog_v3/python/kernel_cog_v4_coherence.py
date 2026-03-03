"""COG v4 Kernel -- Coherence Axiom Form.

Foundational axiom:  A configuration on Z3 x Z4 x O is PHYSICAL iff the
state at every future lightcone point is uniquely determined (path-independent)
from initial data on F2^3.

This is NOT a state machine. There is NO Markov step. The whole lightcone is
either perfectly coherent from the seed -- or the configuration does not exist.

===========================================================================
State space (per F2^3 site):

  g     : int in {0,1,2}    -- Z3 generation  (0=electron, 1=muon, 2=tau)
  a     : int in {0,1,2,3}  -- Z4 EM phase    (0=vacuum, 1=helicity+,
                                                 2=longitudinal, 3=helicity-)
  e     : int in Z>=0       -- integer energy quantum inventory
  sign  : int in {-1, +1}   -- octonionic accumulation sign
  basis : int in {0,...,7}  -- octonionic basis index e0...e7 (Furey convention)

===========================================================================
Octonion multiplication -- Furey convention (CONVENTIONS.md Section 2):

  Seven directed cyclic triples (i,j,k): e_i * e_j = +e_k.
  (1,2,3), (1,4,5), (1,7,6), (2,4,6), (2,5,7), (3,4,7), (3,6,5)

===========================================================================
F2^3 geometry:

  8 sites = vertices of a 3-cube, labeled (x,y,z) in {0,1}^3.
  Site (x,y,z)  <-->  octonionic basis e_{4x + 2y + z}:
    (0,0,0) = e0 = real unit (causal origin)
    (1,1,1) = e7 = vacuum axis (symmetry-breaking direction)

  Causal adjacency: XOR-flip exactly one bit.
    neighbors(x,y,z) = {(x^1,y,z), (x,y^1,z), (x,y,z^1)}

===========================================================================
Path product (the kernel):

  A causal path of length t is a sequence [s_0, s_1, ..., s_t] where
  consecutive sites are XOR-adjacent.  The path product is:

      cfg[s_0] * cfg[s_1] * ... * cfg[s_t]     (State multiplication)

  where State multiplication composes Z3, Z4, and octonion factors.

===========================================================================
Coherence axiom (physical filter):

  state(target, t) is PHYSICAL iff ALL paths of length t from origin (0,0,0)
  to target give the SAME path product.

  If any two paths disagree: INCOHERENT -- non-physical, does not exist.

===========================================================================
v4 additions:

  - Explicit Seed datatype (g, a, basis, sign per site)
  - MeasurementVolume = list of (coords, t_obs) observation targets
  - backproject_to_start(): minimal F2^3 sites in the past lightcone of
    every measurement target -- the sites that "matter" for the given
    measurements
  - COGv4Sim: orchestrates  seed -> propagate -> measure  pipeline

===========================================================================
Design note on the measurement protocol:

  The user specifies a MeasurementVolume (what they want to know) and a
  Seed (the initial state at t=0 on F2^3).  The simulation propagates
  forward under the coherence axiom and returns the unique state at each
  measurement target, or INCOHERENT if the configuration is non-physical
  at that point.  Non-physical configurations are not evolved -- they simply
  do not exist in COG.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Furey convention  (CONVENTIONS.md Section 2)
# ---------------------------------------------------------------------------

#: Seven directed cyclic triples (i,j,k): e_i * e_j = +e_k.
FANO_TRIPLES: Tuple[Tuple[int, int, int], ...] = (
    (1, 2, 3),
    (1, 4, 5),
    (1, 7, 6),
    (2, 4, 6),
    (2, 5, 7),
    (3, 4, 7),
    (3, 6, 5),
)

# ---------------------------------------------------------------------------
# F2^3 geometry
# ---------------------------------------------------------------------------

#: All 8 vertices of the 3-cube, in canonical binary order.
F2_SITES: Tuple[Tuple[int, int, int], ...] = tuple(
    (x, y, z) for x in range(2) for y in range(2) for z in range(2)
)


def site_to_basis(coords: Tuple[int, int, int]) -> int:
    """Map (x,y,z) -> octonionic basis index  4x + 2y + z  in {0,...,7}."""
    return 4 * coords[0] + 2 * coords[1] + coords[2]


def basis_to_site(basis: int) -> Tuple[int, int, int]:
    """Map octonionic basis index -> (x,y,z) in {0,1}^3."""
    b = int(basis)
    return ((b >> 2) & 1, (b >> 1) & 1, b & 1)


def causal_neighbors(coords: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
    """Return the 3 XOR-adjacent sites (causal neighbors in F2^3)."""
    x, y, z = int(coords[0]), int(coords[1]), int(coords[2])
    return [(x ^ 1, y, z), (x, y ^ 1, z), (x, y, z ^ 1)]


def hamming_distance(
    a: Tuple[int, ...], b: Tuple[int, ...]
) -> int:
    """Hamming distance between two binary tuples."""
    return sum(int(ai) != int(bi) for ai, bi in zip(a, b))


# ---------------------------------------------------------------------------
# Octonion multiplication -- Furey convention
# ---------------------------------------------------------------------------


def oct_mul(i: int, j: int) -> Tuple[int, int]:
    """Return (sign, k) such that e_i * e_j = sign * e_k.

    Uses the Furey convention: the seven directed cyclic triples in
    FANO_TRIPLES define which products are +1 and which are -1.

    Special cases:
      e_0 * e_j = e_j  (e_0 = real unit / identity)
      e_i * e_0 = e_i
      e_i * e_i = -e_0  for i != 0
    """
    ii, jj = int(i), int(j)
    if ii == 0:
        return (1, jj)
    if jj == 0:
        return (1, ii)
    if ii == jj:
        return (-1, 0)
    for a, b, c in FANO_TRIPLES:
        for p, q, r in ((a, b, c), (b, c, a), (c, a, b)):
            if (ii, jj) == (p, q):
                return (1, r)
            if (ii, jj) == (q, p):
                return (-1, r)
    raise ValueError(f"No Fano line contains both e{i} and e{j}")


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class State:
    """A single site state in Z3 x Z4 x O.

    Attributes
    ----------
    g     : Z3 generation index   (0 = electron, 1 = muon, 2 = tau)
    a     : Z4 EM phase           (0 = vacuum,   1 = helicity+,
                                   2 = longitudinal/unphysical,
                                   3 = helicity-)
    e     : integer energy        (Z>=0)
    sign  : octonionic sign       (+1 or -1)
    basis : octonionic basis index  e_{basis}  in {0,...,7}
    """

    g: int
    a: int
    sign: int
    basis: int
    e: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "g", int(self.g) % 3)
        object.__setattr__(self, "a", int(self.a) % 4)
        if int(self.e) < 0:
            raise ValueError(f"e must be >= 0, got {self.e}")
        object.__setattr__(self, "e", int(self.e))
        if int(self.sign) not in (-1, 1):
            raise ValueError(f"sign must be -1 or +1, got {self.sign}")
        if not (0 <= int(self.basis) <= 7):
            raise ValueError(f"basis must be in 0..7, got {self.basis}")

    def __mul__(self, other: "State") -> "State":
        """Compose two states: Z3 x Z4 group product, octonionic product."""
        s, k = oct_mul(self.basis, other.basis)
        return State(
            g=(self.g + other.g) % 3,
            a=(self.a + other.a) % 4,
            e=self.e + other.e,
            sign=self.sign * other.sign * s,
            basis=k,
        )

    def __repr__(self) -> str:
        sgn = "+" if self.sign > 0 else "-"
        return f"State(g={self.g}, a={self.a}, E={self.e}, sign={sgn}1, e{self.basis})"


# ---------------------------------------------------------------------------
# Path enumeration
# ---------------------------------------------------------------------------

#: Maximum paths before raising RuntimeError.  Safe cap for t <= 10 on F2^3.
_MAX_PATHS_DEFAULT: int = 50_000


class _PathLimitReached(Exception):
    pass


def all_paths(
    start: Tuple[int, int, int],
    end: Tuple[int, int, int],
    steps: int,
    *,
    max_paths: int = _MAX_PATHS_DEFAULT,
) -> List[Tuple[Tuple[int, int, int], ...]]:
    """Enumerate all causal paths of EXACTLY `steps` steps from start to end.

    Each step moves to a XOR-adjacent neighbor.  Paths may revisit sites.
    Returns a list of (steps+1)-tuples of site coordinates.

    Pruning: branches where remaining steps < hamming_distance(cur, end), or
    where the parity of remaining steps does not match hamming_distance, are
    cut immediately.

    Raises RuntimeError if more than max_paths paths are found (protects
    against exponential blowup for large t).
    """
    if steps < 0:
        return []

    results: List[Tuple[Tuple[int, int, int], ...]] = []

    def _walk(
        cur: Tuple[int, int, int],
        remaining: int,
        path: List[Tuple[int, int, int]],
    ) -> None:
        if remaining == 0:
            if cur == end:
                results.append(tuple(path))
                if len(results) >= max_paths:
                    raise _PathLimitReached()
            return
        d = hamming_distance(cur, end)
        # Parity/distance pruning.
        if d > remaining or (d % 2) != (remaining % 2):
            return
        for nb in causal_neighbors(cur):
            path.append(nb)
            _walk(nb, remaining - 1, path)
            path.pop()

    try:
        _walk(start, steps, [start])
    except _PathLimitReached:
        raise RuntimeError(
            f"all_paths exceeded max_paths={max_paths}: "
            f"t={steps}, start={start}, end={end}.  "
            f"Reduce horizon or increase max_paths."
        )

    return results


SRule = Callable[[State, State], int]


def _normalize_s(x: int) -> int:
    v = int(x)
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


def _mul_with_s_rule(lhs: State, rhs: State, s_rule: SRule) -> State:
    """Deterministic composition with optional C4 phase lift s in {-1,0,+1}.

    Interpretation in this path-product kernel:
    - `s` is a deterministic phase-lift increment added to the Z4 channel.
    - Energy non-negativity is a hard gate on whether a requested signed lift
      can fire:
        s=+1 requires rhs.e > 0
        s=-1 requires lhs.e > 0
      otherwise s is forced to 0.
    - Integer energy remains additive and nonnegative.
    """
    s_req = _normalize_s(s_rule(lhs, rhs))
    s_eff = s_req
    if s_req > 0 and int(rhs.e) <= 0:
        s_eff = 0
    elif s_req < 0 and int(lhs.e) <= 0:
        s_eff = 0

    oct_s, oct_k = oct_mul(lhs.basis, rhs.basis)
    return State(
        g=(lhs.g + rhs.g) % 3,
        a=(lhs.a + rhs.a + int(s_eff)) % 4,
        sign=lhs.sign * rhs.sign * oct_s,
        basis=oct_k,
        e=lhs.e + rhs.e,
    )


def path_product(
    path: Tuple[Tuple[int, int, int], ...],
    cfg: "SeedConfig",
    *,
    s_rule: Optional[SRule] = None,
) -> State:
    """Compute the ordered product  cfg[s0] * cfg[s1] * ... * cfg[s_t]."""
    state = cfg[path[0]]
    for coords in path[1:]:
        rhs = cfg[coords]
        if s_rule is None:
            state = state * rhs
        else:
            state = _mul_with_s_rule(state, rhs, s_rule)
    return state


# ---------------------------------------------------------------------------
# Measurement types
# ---------------------------------------------------------------------------

#: A dict mapping each F2^3 site to its initial State.
SeedConfig = Dict[Tuple[int, int, int], State]


@dataclass(frozen=True)
class MeasurementTarget:
    """One observation point: site coords at time t_obs."""

    coords: Tuple[int, int, int]
    t_obs: int


@dataclass
class MeasurementVolume:
    """A collection of (coords, t_obs) observation targets."""

    targets: List[MeasurementTarget] = field(default_factory=list)

    def add(self, coords: Tuple[int, int, int], t_obs: int) -> None:
        self.targets.append(MeasurementTarget(coords=coords, t_obs=t_obs))

    def __len__(self) -> int:
        return len(self.targets)


# ---------------------------------------------------------------------------
# Seed-volume back-projection
# ---------------------------------------------------------------------------


def backproject_to_start(
    measurement_vol: MeasurementVolume,
    *,
    origin: Tuple[int, int, int] = (0, 0, 0),
) -> FrozenSet[Tuple[int, int, int]]:
    """Minimal F2^3 sites that influence at least one measurement target.

    A site x is relevant for (target, t_obs) iff x appears in some causal
    path of length t_obs from origin to target.  This holds exactly when:

        d(origin, x) + d(x, target) <= t_obs
        d(origin, x) + d(x, target) ≡ t_obs  (mod 2)

    where d is the Hamming distance on {0,1}^3.

    Sites NOT in this set have zero influence on any measurement in the
    given volume and do not need to be seeded.
    """
    relevant: Set[Tuple[int, int, int]] = set()
    for mt in measurement_vol.targets:
        for site in F2_SITES:
            d1 = hamming_distance(origin, site)
            d2 = hamming_distance(site, mt.coords)
            total = d1 + d2
            if total <= mt.t_obs and (total % 2) == (mt.t_obs % 2):
                relevant.add(site)
    return frozenset(relevant)


# ---------------------------------------------------------------------------
# Coherence results
# ---------------------------------------------------------------------------

COHERENT = "COHERENT"
INCOHERENT = "INCOHERENT"
NOT_IN_LIGHTCONE = "NOT_IN_LIGHTCONE"


@dataclass
class LightconePoint:
    """Coherence result at a single (coords, t) point.

    status values:
      COHERENT         -- unique path product; site is physical at this time.
      INCOHERENT       -- paths disagree; configuration does not exist.
      NOT_IN_LIGHTCONE -- no paths of length t reach this site from origin
                          (parity or distance mismatch).  Not a violation.
    """

    coords: Tuple[int, int, int]
    t: int
    status: str                   # COHERENT / INCOHERENT / NOT_IN_LIGHTCONE
    state: Optional[State]        # unique state if COHERENT, else None
    n_paths: int                  # total paths evaluated
    n_disagreeing: int            # paths that disagreed with the first

    @property
    def physical(self) -> bool:
        """True iff the status is COHERENT or NOT_IN_LIGHTCONE (no violation)."""
        return self.status in (COHERENT, NOT_IN_LIGHTCONE)


@dataclass
class MeasurementResult:
    """Coherence result for one MeasurementTarget."""

    target: MeasurementTarget
    status: str
    state: Optional[State]
    n_paths: int
    n_disagreeing: int

    @property
    def physical(self) -> bool:
        return self.status in (COHERENT, NOT_IN_LIGHTCONE)


# ---------------------------------------------------------------------------
# Coherence kernel
# ---------------------------------------------------------------------------


@dataclass
class COGKernel:
    """Coherence axiom kernel over F2^3 x T.

    Physical iff state(target, t) is path-independent for every (target, t).

    Parameters
    ----------
    cfg    : SeedConfig -- initial State at each of the 8 F2^3 sites.
    origin : Tuple     -- the causal origin (default (0,0,0) = e0).
    """

    cfg: SeedConfig
    origin: Tuple[int, int, int] = (0, 0, 0)
    s_rule: Optional[SRule] = None

    def future_state(
        self, target: Tuple[int, int, int], t: int
    ) -> Optional[State]:
        """Return the unique future state if coherent, else None."""
        return self.future_state_detailed(target, t).state

    def is_reachable(self, target: Tuple[int, int, int], t: int) -> bool:
        """True iff target is in the causal future of origin at time t.

        Requires d(origin, target) <= t  AND  d(origin, target) ≡ t (mod 2).
        """
        d = hamming_distance(self.origin, target)
        return d <= t and (d % 2) == (t % 2)

    def future_state_detailed(
        self, target: Tuple[int, int, int], t: int
    ) -> LightconePoint:
        """Compute state(target, t) with full coherence diagnostics."""
        if not self.is_reachable(target, t):
            return LightconePoint(
                coords=target,
                t=t,
                status=NOT_IN_LIGHTCONE,
                state=None,
                n_paths=0,
                n_disagreeing=0,
            )

        paths = all_paths(self.origin, target, t)
        if not paths:
            # Should not happen after is_reachable check, but guard anyway.
            return LightconePoint(
                coords=target,
                t=t,
                status=NOT_IN_LIGHTCONE,
                state=None,
                n_paths=0,
                n_disagreeing=0,
            )

        products = [path_product(p, self.cfg, s_rule=self.s_rule) for p in paths]
        first = products[0]
        n_disagree = sum(1 for pr in products[1:] if pr != first)

        if n_disagree == 0:
            return LightconePoint(
                coords=target,
                t=t,
                status=COHERENT,
                state=first,
                n_paths=len(products),
                n_disagreeing=0,
            )
        return LightconePoint(
            coords=target,
            t=t,
            status=INCOHERENT,
            state=None,
            n_paths=len(products),
            n_disagreeing=n_disagree,
        )

    def physical(
        self, horizon: int = 3
    ) -> Tuple[bool, Optional[LightconePoint]]:
        """Test if the configuration is physical up to time horizon.

        Returns (True, None) if all (coords, t) up to horizon are coherent.
        Returns (False, first_violation) at the first INCOHERENT point.
        """
        for t in range(1, horizon + 1):
            for coords in F2_SITES:
                pt = self.future_state_detailed(coords, t)
                if not pt.physical:
                    return False, pt
        return True, None

    def lightcone(
        self, horizon: int = 3
    ) -> Dict[Tuple[Tuple[int, int, int], int], LightconePoint]:
        """Compute all lightcone points for every (site, t) up to horizon."""
        return {
            (coords, t): self.future_state_detailed(coords, t)
            for t in range(1, horizon + 1)
            for coords in F2_SITES
        }


# ---------------------------------------------------------------------------
# v4 Simulation: seed -> coherence filter -> measure
# ---------------------------------------------------------------------------


@dataclass
class COGv4Sim:
    """COG v4 simulation under the coherence axiom.

    Protocol
    --------
    1. Define MeasurementVolume  (what you want to observe).
    2. backproject_to_start()    (find minimal seed sites that matter).
    3. Provide a Seed            (State for each F2^3 site -- or the minimal
                                  set returned by step 2).
    4. run()                     (propagate forward; apply coherence filter).
    5. Inspect results           (COHERENT -> unique state; INCOHERENT ->
                                  configuration does not exist in COG).

    Non-physical configurations are not evolved.  They simply do not exist.
    """

    seed: SeedConfig
    measurement_vol: MeasurementVolume
    origin: Tuple[int, int, int] = (0, 0, 0)

    def __post_init__(self) -> None:
        self._kernel = COGKernel(cfg=self.seed, origin=self.origin)

    def seed_volume(self) -> FrozenSet[Tuple[int, int, int]]:
        """F2^3 sites that influence at least one measurement target."""
        return backproject_to_start(self.measurement_vol, origin=self.origin)

    def run(self) -> List[MeasurementResult]:
        """Propagate forward and collect measurement results."""
        results: List[MeasurementResult] = []
        for mt in self.measurement_vol.targets:
            pt = self._kernel.future_state_detailed(mt.coords, mt.t_obs)
            results.append(
                MeasurementResult(
                    target=mt,
                    status=pt.status,
                    state=pt.state,
                    n_paths=pt.n_paths,
                    n_disagreeing=pt.n_disagreeing,
                )
            )
        return results

    def physical(self) -> bool:
        """True iff every measurement target is coherent."""
        return all(r.physical for r in self.run())

    def summary(self) -> str:
        """Human-readable summary of measurement results."""
        lines = [
            f"COGv4Sim  origin={self.origin}  "
            f"targets={len(self.measurement_vol)}",
            "-" * 60,
        ]
        for r in self.run():
            mt = r.target
            label = f"({mt.coords}, t={mt.t_obs})"
            if r.physical:
                lines.append(
                    f"  {label:35s}  COHERENT    {r.state!r}  "
                    f"[{r.n_paths} paths]"
                )
            else:
                lines.append(
                    f"  {label:35s}  INCOHERENT  "
                    f"[{r.n_paths} paths, {r.n_disagreeing} disagree]"
                )
        lines.append("-" * 60)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Standard seed constructors
# ---------------------------------------------------------------------------


def vacuum_seed() -> SeedConfig:
    """Trivial vacuum: every site is e0 (real unit), g=0, a=0, sign=+1.

    All path products equal e0 at all times -> trivially physical.
    """
    return {s: State(g=0, a=0, sign=1, basis=0) for s in F2_SITES}


def basis_identity_seed() -> SeedConfig:
    """Each site carries its own octonionic basis element.

    Site (x,y,z) -> State(g=0, a=0, sign=+1, basis=4x+2y+z).

    This seed is generically INCOHERENT: different paths to the same target
    traverse different basis elements and produce different octonionic products.
    Useful as a non-trivial 'incoherent reference' in tests.
    """
    return {
        s: State(g=0, a=0, sign=1, basis=site_to_basis(s))
        for s in F2_SITES
    }


def uniform_seed(g: int, a: int, sign: int, basis: int) -> SeedConfig:
    """Every site identical: trivially coherent (any path gives the same product)."""
    st = State(g=g, a=a, sign=sign, basis=basis)
    return {s: st for s in F2_SITES}


def generation_seed(
    g_map: Dict[Tuple[int, int, int], int],
    *,
    a: int = 0,
    sign: int = 1,
    basis: int = 0,
) -> SeedConfig:
    """Seed with site-specific Z3 generation, uniform in all other channels.

    g_map : dict from F2^3 coords to g value (0,1,2).
    Useful for constructing generation-domain walls.
    """
    cfg: SeedConfig = {}
    for s in F2_SITES:
        g_val = int(g_map.get(s, 0)) % 3
        cfg[s] = State(g=g_val, a=a, sign=sign, basis=basis)
    return cfg


def e7_e0_energy_probe_seed(
    *,
    g: int = 0,
    a: int = 1,
    sign: int = 1,
    basis: int = 7,
    e7_energy: int = 1,
    e0_energy: int = 0,
) -> SeedConfig:
    """Small coherence probe seed requested for s-rule selection.

    Construction:
    - All sites start as vacuum-like (g=0, a=0, e=0, +e0).
    - Site e7 = (1,1,1): (g, basis, a, E=e7_energy).
    - Site e0 = (0,0,0): (g, basis, a, E=e0_energy).
    """
    if int(e7_energy) < 0 or int(e0_energy) < 0:
        raise ValueError("Probe energies must be >= 0.")

    cfg = vacuum_seed()
    cfg[(1, 1, 1)] = State(
        g=int(g) % 3,
        a=int(a) % 4,
        sign=int(sign),
        basis=int(basis) % 8,
        e=int(e7_energy),
    )
    cfg[(0, 0, 0)] = State(
        g=int(g) % 3,
        a=int(a) % 4,
        sign=int(sign),
        basis=int(basis) % 8,
        e=int(e0_energy),
    )
    return cfg


def s_rule_zero(lhs: State, rhs: State) -> int:
    return 0


def s_rule_fano_sign(lhs: State, rhs: State) -> int:
    s, _k = oct_mul(lhs.basis, rhs.basis)
    return int(s)


def s_rule_energy_gradient(lhs: State, rhs: State) -> int:
    if int(rhs.e) > int(lhs.e):
        return 1
    if int(rhs.e) < int(lhs.e):
        return -1
    return 0


def s_rule_basis_order(lhs: State, rhs: State) -> int:
    if int(rhs.basis) > int(lhs.basis):
        return 1
    if int(rhs.basis) < int(lhs.basis):
        return -1
    return 0


def select_s_rule_by_coherence(
    seed_cfg: SeedConfig,
    *,
    origin: Tuple[int, int, int] = (0, 0, 0),
    horizon: int = 3,
    candidates: Optional[Dict[str, Optional[SRule]]] = None,
) -> Dict[str, object]:
    """Evaluate deterministic s-rule candidates by coherence.

    Returns:
    - per-rule physical() result,
    - selected rule (best coherence, then deterministic name tie-break).
    """
    cand = candidates or {
        "no_s_rule_baseline": None,
        "s_rule_zero": s_rule_zero,
        "s_rule_fano_sign": s_rule_fano_sign,
        "s_rule_energy_gradient": s_rule_energy_gradient,
        "s_rule_basis_order": s_rule_basis_order,
    }

    rows: List[Dict[str, object]] = []
    for name in sorted(cand.keys()):
        rule = cand[name]
        kernel = COGKernel(cfg=seed_cfg, origin=origin, s_rule=rule)
        ok, viol = kernel.physical(horizon=int(horizon))
        rows.append(
            {
                "rule_name": str(name),
                "physical": bool(ok),
                "violation_t": None if viol is None else int(viol.t),
                "violation_coords": None if viol is None else tuple(viol.coords),
                "n_paths": None if viol is None else int(viol.n_paths),
                "n_disagreeing": None if viol is None else int(viol.n_disagreeing),
            }
        )

    # Coherence-first selection:
    # 1) physical=True beats False
    # 2) later first-violation time beats earlier
    # 3) deterministic lexical tie-break by rule_name
    def _score(r: Dict[str, object]) -> Tuple[int, int, str]:
        phys = 1 if bool(r["physical"]) else 0
        vt = int(horizon) + 1 if r["violation_t"] is None else int(r["violation_t"])
        return (phys, vt, str(r["rule_name"]))

    best = sorted(rows, key=_score, reverse=True)[0]
    return {
        "horizon": int(horizon),
        "rows": rows,
        "selected_rule_name": str(best["rule_name"]),
        "selected_rule_physical": bool(best["physical"]),
    }

"""Accelerated stepping backends for the v3 Octavian-240 multiplicative kernel.

This module preserves canonical update semantics:
  out[node] = (Π neighbors msg) * old[node]
with fixed-vacuum boundaries encoded as neighbor index `-1`.

Backends:
  - python: reference implementation (slow, exact)
  - numba_cpu: JIT compiled CPU backend (default accelerator)
  - numba_cuda: optional GPU backend (available only if CUDA runtime is usable)

The accelerated lane is intentionally separate from the canonical kernel module
so governance artifacts can still pin the exact reference implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
from numba import njit, prange

from cog_v3.python import kernel_octavian240_multiplicative_v1 as k

try:
    from numba import cuda
except Exception:  # pragma: no cover - environment dependent
    cuda = None  # type: ignore[assignment]


AccelWorld = np.ndarray  # uint16, flattened [nx * ny * nz]
NeighborTable = np.ndarray  # int32, shape [n_cells, n_neighbors], -1 => fixed vacuum
MulTable = np.ndarray  # uint16, shape [240, 240]

THREADS_PER_BLOCK = 256


@dataclass(frozen=True)
class BackendInfo:
    backend_id: str
    available: bool
    reason: str


def _basis_id(i: int, sign: int = 1) -> int:
    v = [Fraction(0, 1) for _ in range(8)]
    v[int(i)] = Fraction(int(sign), 1)
    return int(k.ALPHABET_INDEX[tuple(v)])  # type: ignore[index]


def default_probe_state_id() -> int:
    """Default non-vacuum probe state (`+e111`) used in benchmark seeding."""
    return _basis_id(7, +1)


def offsets_for_stencil(stencil_id: str) -> List[Tuple[int, int, int]]:
    sid = str(stencil_id)
    if sid == "axial6":
        return [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
    if sid == "cube26":
        out: List[Tuple[int, int, int]] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    out.append((dx, dy, dz))
        return out
    if sid == "cube124":
        out = []
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                for dz in (-2, -1, 0, 1, 2):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    out.append((dx, dy, dz))
        return out
    raise ValueError(f"Unknown stencil_id: {sid}")


def _index(x: int, y: int, z: int, ny: int, nz: int) -> int:
    return (x * ny + y) * nz + z


def build_neighbor_table(
    nx: int, ny: int, nz: int, offsets: Sequence[Tuple[int, int, int]]
) -> NeighborTable:
    n = int(nx) * int(ny) * int(nz)
    m = len(offsets)
    tab = np.full((n, m), -1, dtype=np.int32)
    row = 0
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                for j, (dx, dy, dz) in enumerate(offsets):
                    qx, qy, qz = x + int(dx), y + int(dy), z + int(dz)
                    if 0 <= qx < nx and 0 <= qy < ny and 0 <= qz < nz:
                        tab[row, j] = _index(qx, qy, qz, ny, nz)
                row += 1
    return tab


def build_mul_table() -> MulTable:
    t = np.zeros((k.ALPHABET_SIZE, k.ALPHABET_SIZE), dtype=np.uint16)
    for a in range(k.ALPHABET_SIZE):
        for b in range(k.ALPHABET_SIZE):
            t[a, b] = np.uint16(k.multiply_ids(int(a), int(b)))
    return t


def make_world(nx: int, ny: int, nz: int, seed_state_id: int | None = None) -> AccelWorld:
    n = int(nx) * int(ny) * int(nz)
    world = np.full(n, np.uint16(k.IDENTITY_ID), dtype=np.uint16)
    if seed_state_id is not None:
        cx, cy, cz = nx // 2, ny // 2, nz // 2
        idx = _index(cx, cy, cz, ny, nz)
        world[idx] = np.uint16(int(seed_state_id))
    return world


def step_python(
    world: AccelWorld,
    neighbors: NeighborTable,
    mul_table: MulTable,
    vac_id: int = k.IDENTITY_ID,
    identity_id: int = k.IDENTITY_ID,
) -> AccelWorld:
    n, m = neighbors.shape
    out = np.empty_like(world)
    vac = int(vac_id)
    ident = int(identity_id)
    for i in range(n):
        acc = ident
        for j in range(m):
            q = int(neighbors[i, j])
            msg = vac if q < 0 else int(world[q])
            acc = int(mul_table[acc, msg])
        out[i] = np.uint16(mul_table[acc, int(world[i])])
    return out


@njit(cache=True, parallel=True)
def _step_numba_cpu(
    world: AccelWorld,
    neighbors: NeighborTable,
    mul_table: MulTable,
    vac_id: np.uint16,
    identity_id: np.uint16,
) -> AccelWorld:
    n = neighbors.shape[0]
    m = neighbors.shape[1]
    out = np.empty_like(world)
    for i in prange(n):
        acc = identity_id
        for j in range(m):
            q = neighbors[i, j]
            msg = vac_id if q < 0 else world[q]
            acc = mul_table[acc, msg]
        out[i] = mul_table[acc, world[i]]
    return out


@njit(cache=True, parallel=True)
def _run_ticks_numba_cpu(
    world: AccelWorld,
    neighbors: NeighborTable,
    mul_table: MulTable,
    ticks: int,
    vac_id: np.uint16,
    identity_id: np.uint16,
) -> AccelWorld:
    n = neighbors.shape[0]
    m = neighbors.shape[1]
    cur = world.copy()
    nxt = np.empty_like(cur)
    for _ in range(ticks):
        for i in prange(n):
            acc = identity_id
            for j in range(m):
                q = neighbors[i, j]
                msg = vac_id if q < 0 else cur[q]
                acc = mul_table[acc, msg]
            nxt[i] = mul_table[acc, cur[i]]
        tmp = cur
        cur = nxt
        nxt = tmp
    return cur


def step_numba_cpu(
    world: AccelWorld,
    neighbors: NeighborTable,
    mul_table: MulTable,
    vac_id: int = k.IDENTITY_ID,
    identity_id: int = k.IDENTITY_ID,
) -> AccelWorld:
    return _step_numba_cpu(
        world,
        neighbors,
        mul_table,
        np.uint16(int(vac_id)),
        np.uint16(int(identity_id)),
    )


if cuda is not None:  # pragma: no branch
    @cuda.jit
    def _step_numba_cuda(
        world_in: AccelWorld,
        world_out: AccelWorld,
        neighbors: NeighborTable,
        mul_table: MulTable,
        vac_id: np.uint16,
        identity_id: np.uint16,
    ) -> None:
        i = cuda.grid(1)
        n = world_in.shape[0]
        if i >= n:
            return
        m = neighbors.shape[1]
        acc = identity_id
        for j in range(m):
            q = neighbors[i, j]
            msg = vac_id if q < 0 else world_in[q]
            acc = mul_table[acc, msg]
        world_out[i] = mul_table[acc, world_in[i]]


def numba_cuda_available() -> BackendInfo:
    if cuda is None:
        return BackendInfo("numba_cuda", False, "numba.cuda import failed")
    try:
        ok = bool(cuda.is_available())
    except Exception as exc:  # pragma: no cover - environment dependent
        return BackendInfo("numba_cuda", False, f"cuda availability check failed: {exc}")
    if not ok:
        # Numba commonly reports False when NVVM (ptx compiler) is missing even
        # if a CUDA device is visible to the driver.
        try:
            from numba.cuda.cudadrv import nvvm

            _ = nvvm.NVVM()
        except Exception as exc:  # pragma: no cover - environment dependent
            return BackendInfo("numba_cuda", False, f"CUDA device found but NVVM unavailable: {exc}")
        return BackendInfo("numba_cuda", False, "CUDA runtime unavailable for numba")
    return BackendInfo("numba_cuda", True, "ok")


def step_numba_cuda(
    world: AccelWorld,
    neighbors: NeighborTable,
    mul_table: MulTable,
    vac_id: int = k.IDENTITY_ID,
    identity_id: int = k.IDENTITY_ID,
    threads_per_block: int = THREADS_PER_BLOCK,
) -> AccelWorld:
    info = numba_cuda_available()
    if not info.available:
        raise RuntimeError(info.reason)
    assert cuda is not None  # for type checker
    n = world.shape[0]
    blocks = (n + int(threads_per_block) - 1) // int(threads_per_block)
    d_world = cuda.to_device(world)
    d_out = cuda.device_array_like(d_world)
    d_neighbors = cuda.to_device(neighbors)
    d_mul = cuda.to_device(mul_table)
    _step_numba_cuda[blocks, int(threads_per_block)](
        d_world,
        d_out,
        d_neighbors,
        d_mul,
        np.uint16(int(vac_id)),
        np.uint16(int(identity_id)),
    )
    cuda.synchronize()
    return d_out.copy_to_host()


def run_ticks(
    world: AccelWorld,
    neighbors: NeighborTable,
    mul_table: MulTable,
    ticks: int,
    backend: str,
    vac_id: int = k.IDENTITY_ID,
    identity_id: int = k.IDENTITY_ID,
    threads_per_block: int = THREADS_PER_BLOCK,
) -> AccelWorld:
    cur = np.asarray(world, dtype=np.uint16)
    t = int(ticks)
    if t < 0:
        raise ValueError("ticks must be >= 0")
    b = str(backend)
    if b == "python":
        for _ in range(t):
            cur = step_python(cur, neighbors, mul_table, vac_id=vac_id, identity_id=identity_id)
        return cur
    if b == "numba_cpu":
        return _run_ticks_numba_cpu(
            cur,
            neighbors,
            mul_table,
            int(t),
            np.uint16(int(vac_id)),
            np.uint16(int(identity_id)),
        )
    if b == "numba_cuda":
        info = numba_cuda_available()
        if not info.available:
            raise RuntimeError(info.reason)
        assert cuda is not None
        n = cur.shape[0]
        blocks = (n + int(threads_per_block) - 1) // int(threads_per_block)
        d_world = cuda.to_device(cur)
        d_out = cuda.device_array_like(d_world)
        d_neighbors = cuda.to_device(neighbors)
        d_mul = cuda.to_device(mul_table)
        for _ in range(t):
            _step_numba_cuda[blocks, int(threads_per_block)](
                d_world,
                d_out,
                d_neighbors,
                d_mul,
                np.uint16(int(vac_id)),
                np.uint16(int(identity_id)),
            )
            d_world, d_out = d_out, d_world
        cuda.synchronize()
        return d_world.copy_to_host()
    raise ValueError(f"Unknown backend: {backend}")


def backend_matrix() -> Dict[str, BackendInfo]:
    info: Dict[str, BackendInfo] = {}
    info["python"] = BackendInfo("python", True, "reference")
    info["numba_cpu"] = BackendInfo("numba_cpu", True, "available")
    info["numba_cuda"] = numba_cuda_available()
    return info

#!/usr/bin/env python3
"""
Target: S3 Witt-Pair Covariance Test
Claim: GEN-002 / MU-001 / LEPTON-001 (Generation Fork)
Description: Tests if the deterministic COG update rule is covariant under the
S3 cyclic permutation of the three color planes (Witt pairs).

Binary Outcome:
- TRUE: The generation hierarchy is Kinematic (driven by orbit geometries).
- FALSE: The generation hierarchy is Dynamical (update rule breaks the symmetry).
"""

from __future__ import annotations

import random
from typing import Dict, List, Tuple

# Assuming minimal_world_kernel is accessible in the python path
from minimal_world_kernel_calc_copy import (
    CxO,
    GInt,
    World,
    cxo_mul,
    step,
)

# ---------------------------------------------------------------------------
# 1. S3 Permutation Definition (The Fano Sigma Map)
# ---------------------------------------------------------------------------

def apply_sigma(state: CxO) -> CxO:
    """
    Applies the S3 cyclic permutation to the three Witt pairs (Color Planes).
    Cycle: P1(e6, e1) -> P2(e2, e5) -> P3(e3, e4) -> P1(e6, e1)
    e0 and e7 (Vacuum) remain fixed.
    """
    out = [GInt(0, 0) for _ in range(8)]
    
    # Fixed axes
    out[0] = state[0]  # e0 -> e0
    out[7] = state[7]  # e7 -> e7
    
    # e1(P1) -> e5(P2) -> e4(P3) -> e1(P1)
    out[5] = state[1]  
    out[4] = state[5]
    out[1] = state[4]
    
    # e6(P1) -> e2(P2) -> e3(P3) -> e6(P1)
    out[2] = state[6]
    out[3] = state[2]
    out[6] = state[3]
    
    return tuple(out)

def apply_sigma_to_world(world: World) -> World:
    """Returns a new World with sigma applied to all node states."""
    new_states = {nid: apply_sigma(state) for nid, state in world.states.items()}
    return World(
        node_ids=world.node_ids,
        parents=world.parents,
        states=new_states,
        tick=world.tick
    )

# ---------------------------------------------------------------------------
# 2. Test Generators
# ---------------------------------------------------------------------------

def _random_gint() -> GInt:
    """Generate a random Gaussian integer to avoid trivial zero-state passes."""
    return GInt(random.randint(-3, 3), random.randint(-3, 3))

def _random_cxo() -> CxO:
    return tuple(_random_gint() for _ in range(8))

def build_test_cone(depth: int) -> World:
    """Builds a dense 1D causal cone populated with dense random noise."""
    node_ids = []
    parents: Dict[str, List[str]] = {}
    states: Dict[str, CxO] = {}
    
    for d in range(depth + 1):
        for k in range(d + 1):
            nid = f"d{d}_n{k}"
            node_ids.append(nid)
            states[nid] = _random_cxo()
            
            if d == 0:
                parents[nid] = []
            else:
                p_list = []
                if k > 0:
                    p_list.append(f"d{d-1}_n{k-1}")
                if k < d:
                    p_list.append(f"d{d-1}_n{k}")
                parents[nid] = p_list
                
    return World(node_ids=node_ids, parents=parents, states=states, tick=0)

# ---------------------------------------------------------------------------
# 3. Falsification Gates
# ---------------------------------------------------------------------------

def gate_1_algebra_covariance() -> bool:
    """
    Test if sigma is a true automorphism of the underlying C x O algebra.
    sigma(A * B) == sigma(A) * sigma(B)
    """
    A = _random_cxo()
    B = _random_cxo()
    
    left = apply_sigma(cxo_mul(A, B))
    right = cxo_mul(apply_sigma(A), apply_sigma(B))
    
    return left == right

def gate_2_dynamical_covariance(steps: int = 10) -> bool:
    """
    Test if the macroscopic left-fold graph update preserves the S3 symmetry.
    sigma(step^N(World)) == step^N(sigma(World))
    """
    # 1. Initialize identical dense universes
    world_base = build_test_cone(depth=15)
    
    # 2. Universe A: Update then Sigma
    world_A = world_base
    for _ in range(steps):
        world_A = step(world_A)
    world_A_final = apply_sigma_to_world(world_A)
    
    # 3. Universe B: Sigma then Update
    world_B = apply_sigma_to_world(world_base)
    for _ in range(steps):
        world_B = step(world_B)
        
    # 4. Compare resulting microstates exactly
    for nid in world_A_final.node_ids:
        if world_A_final.states[nid] != world_B.states[nid]:
            return False
            
    return True

# ---------------------------------------------------------------------------
# 4. Execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== S3 WITT-PAIR COVARIANCE TEST ===")
    
    # Run 100 random algebra checks
    alg_passes = sum(1 for _ in range(100) if gate_1_algebra_covariance())
    print(f"Gate 1 (Algebra Automorphism): {alg_passes}/100 passes")
    
    if alg_passes < 100:
        print("\nFATAL: Sigma is not an automorphism of the hardcoded Fano orientation!")
        print("Outcome: DYNAMICAL (Symmetry is broken at the lowest algebraic level).")
        exit(1)
        
    # Run dynamical graph update check
    graph_pass = gate_2_dynamical_covariance(steps=5)
    print(f"Gate 2 (N-Step Graph Update): {'PASS' if graph_pass else 'FAIL'}")
    
    print("\n--- CONCLUSION ---")
    if graph_pass:
        print("Result: TRUE (Covariant)")
        print("Meaning: The generation mass hierarchy is purely KINEMATIC.")
        print("Next Action: Proceed with orbit length extraction for Muon/Tau masses.")
    else:
        print("Result: FALSE (Symmetry Broken)")
        print("Meaning: The generation mass hierarchy is DYNAMICAL.")
        print("Next Action: The left-fold update rule natively splits the generations. Extract the mass splitting directly from the interactionFold overhead.")
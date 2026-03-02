# Round 05 Work - Motif-First Chirality Model
Date: 2026-03-02
## Position
Primary hypothesis: chirality is encoded by motif geometry/dynamics, not hard-coded in the kernel.
Kernel should remain as parity-neutral as feasible; motifs should break symmetry via structure and history.
## Operational chirality observables
1. **Phase winding sign**:
   - Track oriented loop of phase progression around motif centroid.
   - Positive/negative winding defines candidate handedness.
2. **Triad orientation sign**:
   - Build local triad from principal transport direction + two transverse structure vectors.
   - Determinant sign gives geometric handedness.
3. **Interaction asymmetry score**:
   - Compare motif response to mirror-transformed perturbation.
## Harness design
1. Construct motif M and mirrored motif P(M).
2. Evolve both in identical vacuum and seeded event-order stream.
3. Compare:
   - survival duration,
   - propagation velocity,
   - coupling rates into designated weak-like channels.
4. Flag chirality signal if mirrored pair diverges beyond threshold while control motifs do not.
## Speculative mechanism candidates
1. Chiral commit from non-commuting product order along closed motif path.
2. Chiral locking via asymmetric occupancy of B/C families under repeated local products.
3. e000/e111 occupancy timing asymmetry as an emergent chiral marker.
## Deliverable for implementation
- Add a chirality_probe module that returns (winding_sign, triad_sign, asymmetry_score) per motif-run.

# Round 04 Literature - Lattice Chirality Constraints
Date: 2026-03-02
## Sources reviewed
1. Nielsen-Ninomiya no-go theorem (fermion doubling on translationally invariant local lattices).
2. Kaplan domain-wall fermions (extra-dimension chirality localization).
3. Narayanan-Neuberger overlap fermions.
4. Ginsparg-Wilson relation literature.
## Core constraints
1. Naive local symmetric discretizations generically produce doubled chiral species.
2. To recover realistic chirality, one typically needs:
   - modified symmetry relation (Ginsparg-Wilson), or
   - extra structural dimension/defect (domain wall), or
   - explicit asymmetry in how modes are selected.
## Relevance to COG v3
1. If chirality is motif-first, motif topology must include a chiral selector that survives coarse graining.
2. If kernel contributes, it should do so minimally and auditable (e.g., ordering channel, not full bias field).
3. We should explicitly test for doubling analogs in candidate kernels/motifs.
## Round output
- Add a chirality gate to motif validation:
  - stable handedness observable,
  - anti-handed partner behavior,
  - no immediate doubling artifact in same energy class.

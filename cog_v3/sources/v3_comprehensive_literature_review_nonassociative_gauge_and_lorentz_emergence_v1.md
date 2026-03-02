# v3 Comprehensive Literature Review: Nonassociative Gauge Leads and Lorentz Emergence

Date: 2026-03-02  
Owner: COG Core  
Scope: Identify high-value prior art relevant to:

1. octonion/nonassociative gauge constructions,
2. emergent Lorentz behavior in discrete dynamics,
3. candidate mathematical constraints for v3 kernel design.

## 1. Executive Summary

Strongest conclusions from the literature:

1. There is meaningful prior art for nonassociative/octonionic gauge formulations, especially via
   cochain twists and Moufang-loop structures, but no dominant standard framework.
2. Emergent Lorentz behavior in discrete models is best established in quantum automata/walk
   settings under explicit locality + homogeneity + isotropy constraints.
3. Discreteness does not force Lorentz breaking in principle, but fixed finite-valency regular
   structures can induce preferred-frame artifacts if not carefully designed.
4. No mature literature appears to match the exact `S960` CA construction currently used in v3,
   which likely makes this lane novel.

## 2. Method

Search lanes:

1. nonassociative gauge + octonions,
2. octonion-to-particle-algebra programs,
3. QCA/quantum-walk emergent relativity,
4. causal-set Lorentz compatibility,
5. lattice-gas isotropy design principles,
6. direct octonion CA / multiplicative automata.

Primary-source preference:

1. arXiv preprints from known groups,
2. APS/JHEP/Annals/PR journals,
3. foundational theorems and high-citation baseline papers.

## 3. Nonassociative Gauge Theory and Octonions

## 3.1 Majid cochain-twist framework (high relevance)

1. S. Majid, "Gauge theory on nonassociative spaces" (2005), `arXiv:math/0506453`.
2. Key result:
   - gives a concrete method to do gauge theory on octonions and related quasialgebras by
     cochain twist.
   - includes explicit flat-connection moduli for `Z_2^3` cube and octonion-related structures.
3. Relevance to v3:
   - provides a principled way to encode nonassociativity via associator data rather than ad hoc rules.
   - suggests a route to structured kernel constraints rather than purely empirical stencil tuning.

## 3.2 Moufang-loop gauge construction (medium-high relevance)

1. Ootsuka, Tanaka, Loginov, "Non-associative Gauge Theory" (2005), `arXiv:hep-th/0512349`.
2. Key result:
   - constructs gauge models where structure object is a Moufang loop (unit octonions).
   - presents octonionic analogs of Maxwell/Yang-Mills and instanton-like solutions.
3. Relevance to v3:
   - supports using multiplicative nonassociative state updates with loop structure.
   - indicates how to separate group-like and nonassociative effects in observables.

## 3.3 G2 and octonion automorphism viewpoint (background relevance)

1. `Aut(O) = G2` is a standard structural fact used repeatedly in octonion physics proposals.
2. Practical takeaway:
   - if v3 wants a gauge-like interpretation, deciding whether gauge variables live in
     `G2`-type automorphisms versus raw octonion elements is critical.

## 4. Octonion-to-Particle-Algebra Programs

## 4.1 Furey line (high conceptual relevance)

1. C. Furey, "Standard model physics from an algebra?" (2016), `arXiv:1611.09182`.
2. C. Furey, "Three generations, two unbroken gauge symmetries, and one eight-dimensional algebra"
   (2019), `arXiv:1910.08395`.
3. Core contribution:
   - SM-like representation structure from complex octonions / Clifford algebras,
     including chirality-selective weak behavior in algebraic form.
4. Relevance to v3:
   - strong inspiration for algebraic state taxonomy and chirality handling.
   - does not directly provide a CA kernel, but provides candidate state-organization constraints.

## 4.2 Related Clifford/exceptional extensions (medium relevance)

1. Gresnigt and others (e.g., `arXiv:2003.08814`) provide full-gauge-content algebraic embeddings.
2. Relevance:
   - useful for classification and interpretation layers once kernel dynamics are reliable.

## 5. Emergent Lorentz in Discrete Dynamics

## 5.1 Foundational QCA/QW results (high relevance)

1. D. Meyer, "From quantum cellular automata to quantum lattice gases" (1996),
   `arXiv:quant-ph/9604003`, DOI `10.1007/BF02199356`.
2. I. Bialynicki-Birula, "Weyl, Dirac, and Maxwell equations on a lattice as unitary cellular automata"
   (1994), DOI `10.1103/PhysRevD.49.6920`.
3. D'Ariano, Perinotti, Bisio et al.:
   - "Quantum cellular automata and free quantum field theory" (2016), `arXiv:1608.02004`.
   - related works deriving Weyl/Dirac/Maxwell in small-wavevector regimes.
4. Arrighi, Facchini, Forets:
   - "Discrete Lorentz covariance for quantum walks and quantum cellular automata" (2014),
     DOI `10.1088/1367-2630/16/9/093007`.

Key pattern:

1. emergent relativistic behavior requires explicit structural constraints,
2. continuum/mesoscale limits are where closure appears,
3. isotropy design and graph/lattice geometry are decisive.

## 5.2 Causal-set discreteness and Lorentz compatibility (high relevance)

1. Dowker, Henson, Sorkin (2003), "Quantum Gravity Phenomenology, Lorentz Invariance and Discreteness",
   `arXiv:gr-qc/0311055`.
2. Bombelli, Henson, Sorkin (2006), "Discreteness without symmetry breaking: a theorem",
   `arXiv:gr-qc/0605006`.

Key result:

1. discreteness need not break Lorentz invariance,
2. but finite-valency graph assignment constraints matter strongly.

Relevance:

1. supports v3 strategy of mesoscale closure tests over microscale invariance assumptions.

## 6. Classical CA Isotropy Engineering

## 6.1 Lattice-gas precedent (medium-high engineering relevance)

1. Frisch, Hasslacher, Pomeau (1986), DOI `10.1103/PhysRevLett.56.1505`.
2. Subsequent lattice-gas and lattice-Boltzmann work shows:
   - isotropy and Galilean-like behavior emerge only when velocity-set symmetry and
     moment constraints are engineered.

Relevance:

1. suggests kernel schedules in v3 should satisfy moment-balance constraints, even in multiplicative form.

## 7. Direct Octonion CA / Multiplicative Automata

1. McKinley (2025), "Elementary Cellular Automata as Multiplicative Automata",
   `arXiv:2502.13360`.
2. Status:
   - interesting direct precedent for multiplicative reinterpretation and octonion-table pointers,
   - currently early-stage and not a settled physics framework.

Conclusion:

1. direct CA-over-octonion-structured alphabets is lightly explored; v3 remains largely novel.

## 8. What This Means for v3 Kernel Strategy

High-confidence implications:

1. prioritize mesoscale Lorentz battery over tick-scale isotropy metrics,
2. treat isotropy as engineered constraint (not only observed metric),
3. use multiple direction classes and unsaturated detector distances,
4. separate wave occupancy and detector outcomes in all transport claims,
5. incorporate nonassociative structure systematically (associator/cocycle-inspired design)
   if current heuristic channel policies plateau.

## 9. Recommended Next Work Items

1. Build `v3_lorentz_closure_battery_v1` with:
   - multi-distance linearity fits,
   - multi-direction slope spread,
   - front-tensor isotropy,
   - scale persistence.
2. Add kernel synthesis constraints inspired by lattice-moment balancing:
   - zero first moment drift,
   - isotropic second moment target,
   - bounded higher-moment anisotropy.
3. Start a "nonassociative structured kernel" branch:
   - compare heuristic policies (`K0-K2`) against one cocycle/associator-informed policy.
4. Keep Furey-like algebraic taxonomy as interpretation layer until transport closure is validated.

## 10. Reference List (Primary)

1. Majid (2005): `https://arxiv.org/abs/math/0506453`
2. Ootsuka, Tanaka, Loginov (2005): `https://arxiv.org/abs/hep-th/0512349`
3. Meyer (1996): `https://arxiv.org/abs/quant-ph/9604003`
4. Meyer journal DOI: `https://doi.org/10.1007/BF02199356`
5. Bialynicki-Birula (1994): `https://doi.org/10.1103/PhysRevD.49.6920`
6. D'Ariano, Perinotti (2016): `https://arxiv.org/abs/1608.02004`
7. Arrighi, Facchini, Forets (2014): `https://doi.org/10.1088/1367-2630/16/9/093007`
8. Dowker, Henson, Sorkin (2003): `https://arxiv.org/abs/gr-qc/0311055`
9. Bombelli, Henson, Sorkin (2006): `https://arxiv.org/abs/gr-qc/0605006`
10. Frisch, Hasslacher, Pomeau (1986): `https://doi.org/10.1103/PhysRevLett.56.1505`
11. Furey thesis (2016): `https://arxiv.org/abs/1611.09182`
12. Furey three generations (2019): `https://arxiv.org/abs/1910.08395`
13. Kleinschmidt, Nicolai, Palmkvist (2010): `https://arxiv.org/abs/1010.2212`
14. McKinley (2025): `https://arxiv.org/abs/2502.13360`

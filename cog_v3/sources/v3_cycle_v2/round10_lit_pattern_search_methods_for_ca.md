# Round 10 Literature - Pattern Search Methods for Cellular Automata
Date: 2026-03-02
## Sources reviewed
1. Game-of-Life search ecosystem (e.g., Catagolue-style census methods).
2. Hashlife/accelerated temporal stepping ideas for sparse regions.
3. Evolutionary and novelty-search methods for glider-like structure discovery.
4. SAT/SMT and symbolic constraint methods for periodic orbit finding.
## Transferable methods
1. **Census-first pipeline**:
   - aggressively deduplicate by invariant signatures,
   - retain only novel survivors.
2. **Novelty over objective-only**:
   - search does better when reward includes behavioral novelty.
3. **Two-phase search**:
   - cheap broad scan,
   - expensive confirmatory reruns.
4. **Canonical signatures**:
   - hash motif modulo translation and phase/global sign equivalence.
## v3 adaptation
1. Add motif hash key for deduplication before long confirm runs.
2. Maintain novelty archive keyed by (period class, drift class, chirality class).
3. Allocate GPU budget with bandit-like scheduling to top novelty bins.
## Round output
- Search framework should combine exploitation (best scores) + exploration (novel bins).

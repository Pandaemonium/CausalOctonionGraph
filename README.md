# Causal Octonion Graph (COG)

A Lean 4 formalization of octonionic algebra and the Witt basis construction
for the complex octonions C ⊗ O, aimed at deriving Standard Model structure
from discrete, non-associative algebra over causal graphs.

## What's here

**Lean 4 library** (`CausalGraphTheory/`) — sorry-free, fully verified:

| File | Content |
|------|---------|
| `Fano.lean` | Fano plane PG(2,2): 7 points, 7 lines, incidence axioms |
| `FanoMul.lean` | Octonion basis multiplication from Fano sign table |
| `Algebra.lean` | Mathlib imports (CommRing, tactics) |
| `Octonion.lean` | Octonion algebra over any CommRing, explicit Fano-driven multiplication |
| `OctonionAlt.lean` | Left/right alternativity and flexibility (proved for general elements) |
| `OctonionNonAssoc.lean` | Non-associativity witness |
| `ComplexOctonion.lean` | FormalComplex R (avoids Mathlib's R-dependent Complex), C ⊗ O |
| `WittBasis.lean` | Witt ladder operators, vacuum idempotent, annihilation proof |

**Key results proved:**
- Fano plane axioms (each line has 3 points, each point on 3 lines, two points determine a line, two lines meet in one point)
- Octonion alternativity: `x * (x * y) = (x * x) * y` over any CommRing
- Octonion non-associativity: explicit witness `(e1 * e2) * e4 != e1 * (e2 * e4)`
- Vacuum idempotent: `(2w)^2 = 2*(2w)` where `w = 1/2(1 + i*e7)`
- Vacuum annihilation: `alpha_j * w = 0` for all three lowering operators

## Building

```bash
# Install elan (Lean version manager) if you haven't
curl https://elan-init.org/ -sSf | sh

# Get Mathlib cache (avoids hours of compilation)
lake exe cache get

# Build
lake build
```

## Convention source of truth

All sign conventions, directed Fano triples, Witt pairings, and vacuum axis
are locked in [`rfc/CONVENTIONS.md`](rfc/CONVENTIONS.md).

## License

MIT

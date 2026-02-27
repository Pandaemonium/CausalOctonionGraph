# The Causal Octonion Graph: Short Physical Primer
*Draft for onboarding and intuition building (short version).*
*Updated: 2026-02-27*

---

## 1. One-line picture

COG models reality as a growing directed acyclic graph (DAG) whose nodes carry
discrete algebraic states and whose edges carry algebraic interactions.

No continuum fields are assumed in the kernel. No real-number differential
equations are used in the core update rule.

---

## 2. What is fundamental in COG

The model has three primitive ingredients:

1. A DAG (causal order).
2. Node states in complex octonions over integers.
3. A local update rule that combines incoming messages multiplicatively.

Everything else (distance, clocks, mass proxies, observable projections) is
derived from those ingredients.

---

## 3. Node state: corrected representation (16 integers)

This is the key correction.

A node state is not "just eight integers." The canonical kernel state is a
complex octonion with integer coefficients:

`psi in C x O over Z`.

Write it as:

```text
psi = sum_{k=0..7} (a_k + i b_k) e_k,   with a_k, b_k in Z
```

So each node has:

1. 8 octonion basis directions `e_0 ... e_7`
2. each direction has a real and imaginary integer coefficient

That is **16 integers total** at the coefficient level (`a_0..a_7, b_0..b_7`).

Why people sometimes say "8-component state":

1. There are 8 basis axes.
2. Each axis carries one complex-integer coefficient.

So "8 components" and "16 integers" are both true, but they describe different
views of the same object.

---

## 4. Why octonions matter here

Octonions are non-associative. That means:

```text
(x*y)*z is not always equal to x*(y*z)
```

In COG, this is interpreted as a structural reason that update order matters.
That gives a natural place for directional "tick" semantics in a discrete model.

Status note:

1. Algebraic alternativity/non-associativity foundations are formalized.
2. Full phenomenology mapping is still ongoing.

---

## 5. The Fano plane as multiplication map

The seven imaginary octonion units are organized by the directed Fano triples.
Those triples lock which basis multiplications produce which outputs and signs.

In practice, this gives:

1. a finite combinatorial multiplication skeleton,
2. a fixed convention for signs/orientation,
3. a compact way to encode allowed local interaction structure.

This is one of the main structural reasons COG can stay fully discrete.

---

## 6. Two clocks in the model

COG currently uses two different counters:

1. `topoDepth`: graph-depth style causal layering.
2. `tickCount`: local update progression for a node.

These are related but not identical. The distinction is important for mass/drag
proxies and for separating "graph growth" from "local internal progression."

---

## 7. What "distance" means here

At kernel level, distance is graph-theoretic, not metric-tensor based.

Typical operational forms:

1. shortest-path style edge count along allowed causal paths,
2. or nearest-next-interaction gap in the local causal neighborhood (RFC-035 track).

Macroscopic geometric recovery is still an open bridge, but the discrete distance
foundation is explicit.

---

## 8. What is already solid vs what is still open

### Solid foundation (infrastructure level)

1. Core octonion/Fano algebra stack in Lean is substantial.
2. Deterministic DAG-first update framework is active.
3. Claim governance and test-gated status workflow are in place.

### Open frontier (physics closure level)

1. Full D4/D5 closure and downstream stabilization.
2. Constant-derivation gaps (for example Weinberg IR closure, strong running bridge).
3. Many-body and bound-state closures (hydrogen-first priority).

---

## 9. How to read status claims safely

Use this interpretation rule:

1. "Proved": machine-checked statement in the current formal stack.
2. "Supported/partial": strong artifacts exist, but not final closure.
3. "Hypothesis/open": intuition and test scaffolding, not final derivation.

For public communication, this lets us keep excitement while staying rigorous.

---

## 10. Minimal mental model for newcomers

If you only keep one picture, keep this:

1. The universe is a causal graph, not a background stage.
2. Each node carries a 16-integer complex-octonion state.
3. Local interactions are finite algebraic updates.
4. Non-associativity makes update order physically meaningful.
5. Observables are what survive projection and governance gates.

That is the COG kernel worldview in one page.

---

## 11. Optional notation quick reference

1. `psi`: node state in `C x O` over `Z`.
2. `e_0..e_7`: octonion basis directions.
3. `topoDepth`: causal depth counter.
4. `tickCount`: local step counter.
5. `combine`: multiplicative interaction combiner in update semantics.

---

*Short-primer objective: intuition first, no overclaiming, no mojibake, and
kernel-level correctness on the state representation.*

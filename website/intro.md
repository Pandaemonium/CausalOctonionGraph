# The Causal Octonion Graph (COG) Lab

> *Can the Standard Model and hydrogen's bound state be derived from pure
> combinatorics, without ever invoking the real-number continuum?*

We believe the answer is **yes** — and this project is building the formal proof.

---

## What We Are Doing

The COG Lab is a discrete-mathematics research project with a single,
audacious goal: to show that the particle spectrum, gauge symmetries, and
bound-state energies of physics emerge inevitably from the algebraic structure
of the **octonions** $\mathbb{O}$ and the combinatorics of a directed causal graph.

No continuous spacetime. No differential equations. No probability amplitudes.
Just a finite graph whose nodes carry octonion-valued state vectors and whose
edges carry rigid algebraic operators.

### The Prime Directive: The Continuum is an Illusion

In this framework:

- **Reality is a directed acyclic graph** (a causal graph).
- **Nodes** are discrete state vectors built from the normed division algebra
  $\mathbb{C} \otimes \mathbb{O}$.
- **Edges** are causal interactions labelled by algebraic operators.
- **Time** is not a background dimension; it is the forced sequential ticking
  that emerges from the *non-associativity* of octonion multiplication.
- **Mass** is computational drag: the frequency at which a state must be
  forcibly re-evaluated.

---

## Target Physical Systems

We are working outward from simplest to hardest:

| System | Status |
|---|---|
| Hydrogen (1s ground state) | Primary target |
| Proton (quark confinement) | In scope |
| Electron-electron interaction | In scope |
| Electron-muon interaction | In scope |
| Proton-proton interaction | In scope |
| Tritium | Longer term |

---

## What Has Been Proved So Far

Our formal proofs are written in **Lean 4** and verified by Mathlib.
Only discrete algebra is used; continuous analysis is forbidden.

Key milestones:

- **Octonion non-associativity** — the failure of $(e_i e_j) e_k = e_i (e_j e_k)$
  is proved for all Fano triples. This is the tick-forcing mechanism.
- **Furey algebra embedding** — the 64-dimensional $\mathbb{C} \otimes \mathbb{O}$
  algebra is constructed and its grade structure verified.
- **$S_3$ symmetry** — the symmetric group $S_3$ of three generations emerges
  from stabilisers of the vacuum axis $e_7$ in the Fano plane.
- **Koide formula (search)** — an ongoing Diophantine search for the integer
  triplet $(f_0, f_1, f_2)$ that minimises the Koide residual under the
  constraint that the triplet encodes the charged lepton mass ratios
  $(1 : 207 : 3477)$.

See the [Results](/web/results) page for the live claim registry.

---

## How We Work

The lab runs **autonomously around the clock**. A frontier-model manager
(Gemini) assigns tasks to worker models (Claude Sonnet, GPT-codex). Workers
write Lean proofs, run Python tests, search the literature, and commit
results directly to the GitHub repository.

Progress is monitored on the [Dashboard](/).

---

## The Mathematics in Brief

The octonions form the largest normed division algebra:
$$
\mathbb{O} \cong \mathbb{R}^8, \quad \|xy\| = \|x\|\|y\|, \quad
x(yz) \neq (xy)z \text{ in general.}
$$

Their multiplication table is encoded in the **Fano plane** $PG(2,2)$:
seven points $\{e_1, \ldots, e_7\}$ and seven lines, each line giving one
directed cyclic triple $(e_i, e_j, e_k)$ with $e_i e_j = e_k$.

The non-associator
$$
[x,y,z] = (xy)z - x(yz)
$$
is completely antisymmetric in $x,y,z$ and vanishes iff at least two of the
three arguments are equal — this *alternativity* is the algebraic engine
behind the discrete time tick.

---

## Follow Along

- **Primer** — the full mathematical primer, from first principles to open frontier: [/web/pages/cog_primer](/web/pages/cog_primer)
- **Cycle Atlas** — interactive motif rhythm explorer (single + coupled periods): [/web/pages/cycle_atlas](/web/pages/cycle_atlas)
- **Proof Ledger** — live upgrades in plain language (with timestamps): [/web/proof_ledger](/web/proof_ledger)
- **Results** — live proof registry: [/web/results](/web/results)
- **Leaderboard** — team standings and kudos: [/web/leaderboard](/web/leaderboard)
- **Pedagogy** — accessible explanations: [/web/pedagogy](/web/pedagogy)
- **Dashboard** — lab status and agent activity: [Dashboard](/)
- **GitHub** — source code and Lean proofs: the `CausalGraphTheory` repository

*This project is open science. All proofs are machine-checked and publicly visible.*

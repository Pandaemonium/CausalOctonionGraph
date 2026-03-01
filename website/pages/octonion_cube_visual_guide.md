# How To Visualize The Octonion Cube, Phase Clocks, and Fano Orientation

This is a public-facing visual guide for the COG v2 geometry.

ASCII companion:

1. [Octonion Cube Visual Guide (ASCII Companion)](/web/pages/octonion_cube_visual_guide_ascii)
2. [Particle Motif GIF Atlas](/web/pages/particle_motif_cycle_gif_atlas)

Use this page when you want a concrete picture in your head of:

1. the 8-channel octonion index cube (`e000..e111`),
2. the 4-cycle phase clock inside each channel,
3. the oriented Fano interaction triples.

---

## One-Sentence Picture

Think of the model as:

1. an 8-vertex binary cube of channel addresses,
2. with a tiny phase clock in each vertex (`+1 -> +i -> -1 -> -i -> +1`),
3. and interaction arrows that follow oriented 3-point Fano triples on the 7 nonzero vertices.

---

## Step 1: Draw The 8-Vertex Index Cube

Draw a cube and label each corner by a 3-bit string:

1. `e000`
2. `e001`
3. `e010`
4. `e011`
5. `e100`
6. `e101`
7. `e110`
8. `e111`

You can use this coordinate convention:

1. first bit = x
2. second bit = y
3. third bit = z

So each channel is literally a binary coordinate `(x,y,z)` with bits in `{0,1}`.

---

## Step 2: Understand What The Cube Means (and what it does not mean)

The cube is the **index geometry** only.

It tells you:

1. which channel is which,
2. how channel destinations are computed (XOR).

It does **not** by itself tell you multiplication sign/chirality.

XOR routing rule:

1. destination index = `i xor j`
2. example: `001 xor 010 = 011`
3. example: `101 xor 011 = 110`

So XOR gives "where the interaction lands."

---

## Step 3: Put A 4-Cycle Clock Inside Each Vertex

Each channel carries a local phase value from:

1. `0` (null / unoccupied),
2. `+1`,
3. `+i`,
4. `-1`,
5. `-i`.

For the active phase states, imagine a 4-step clock:

1. `+1 -> +i -> -1 -> -i -> +1` (repeat)

Interpretation:

1. each cube vertex is an address,
2. each address has its own tiny phase clock,
3. the full node state is all 8 clocks at once (with some entries possibly `0`).

So a node state is:

1. `psi : {000..111} -> {0, +1, +i, -1, -i}`.

---

## Step 4: Remove `e000` And Build The Fano Interaction Layer

Now ignore `e000` for interaction triads and focus on the 7 nonzero channels:

1. `001, 010, 011, 100, 101, 110, 111`

These 7 points form the Fano incidence structure.

A Fano line is a 3-point set `{a, b, c}` with:

1. `a xor b xor c = 0`
2. equivalently `c = a xor b`.

Important:

1. Fano lines are interaction triads (hyperedges),
2. they are not ordinary cube edges.

---

## Step 5: Add Orientation (the arrows that create sign)

For each Fano triad, choose the canonical directed cycle.

If `(a,b,c)` is oriented, then:

1. `a * b = +c`
2. `b * c = +a`
3. `c * a = +b`

Reversing order flips sign:

1. `b * a = -c`, etc.

This orientation is the missing sign/chirality data that XOR alone cannot provide.

XOR says "destination channel."  
Fano orientation says "plus or minus, and handedness."

---

## Canonical Oriented Triads In Binary Labels

Using the current v2 mapping (`e001..e111` as indices 1..7), one canonical oriented set is:

1. `(001, 010, 011)`
2. `(001, 100, 101)`
3. `(001, 111, 110)`
4. `(010, 100, 110)`
5. `(010, 101, 111)`
6. `(011, 100, 111)`
7. `(011, 110, 101)`

You do not need these memorized to reason visually.  
You can regenerate each triad by XOR closure and then apply the chosen orientation table.

---

## Practical Visual Method (Most Clear For Humans)

Do this as two linked drawings:

1. **Left panel:** cube with `e000..e111` labels and tiny 4-cycle clocks.
2. **Right panel:** Fano 7-point graph (exclude `e000`) with oriented arrows on each line.

Then connect panels by label identity (`001` is the same channel in both panels).

Why this is best:

1. cube panel makes addressing and phase fibers obvious,
2. Fano panel makes interaction chirality/sign obvious,
3. trying to force both into one picture usually causes confusion.

---

## What This Geometry Implies For COG

1. finite exact channel addressing (`F2^3`),
2. finite exact local phase alphabet (`0, +/-1, +/-i`),
3. deterministic routing (XOR),
4. deterministic chirality/sign selection (Fano orientation),
5. layered causal time (from strict DAG depth).

So the model is not "just a cube."  
It is:

1. a layered causal graph in time,
2. with cube-indexed channel fibers,
3. and oriented Fano interaction structure.

---

## Quick Sanity Checks You Can Do By Hand

1. XOR closure:
   - pick two nonzero labels `a,b`; verify `a xor b` is also in `001..111`.
2. Triad closure:
   - pick a line `(a,b,c)` and check `a xor b xor c = 0`.
3. Orientation sign:
   - verify forward order is positive and reverse is negative by table convention.
4. Clock update:
   - verify one channel can cycle `+1,+i,-1,-i` while others remain fixed or null.

If all four checks hold, your sketch is consistent with the v2 geometric contract.

# Octonion Cube Visual Guide (ASCII Companion)

Use this page when you want a plain-text, copy-paste diagram for notes, slides, or chat.

See also:
- [How To Visualize The Octonion Cube, Phase Clocks, and Fano Orientation](/web/pages/octonion_cube_visual_guide)
- [Particle Motif GIF Atlas](/web/pages/particle_motif_cycle_gif_atlas)

---

## 1) Two-Panel Mental Model

Panel A (left): channel index cube (`e000..e111`) with local 4-cycle phase clocks.  
Panel B (right): oriented Fano triads on the 7 nonzero channels.

---

## 2) Panel A: 3-Bit Cube (Channel Addresses)

```text
                 e111 -------- e110
                 / |            / |
               /   |          /   |
            e101 -------- e100    |
              |     |       |     |
              |   e011 -----|--- e010
              |   /         |   /
              | /           | /
            e001 -------- e000
```

Coordinate meaning:

1. `eabc` means `(x,y,z) = (a,b,c)` with bits in `{0,1}`
2. XOR routing is index arithmetic:
   - `001 xor 010 = 011`
   - `101 xor 011 = 110`

---

## 3) Per-Channel Clock (inside each cube cell)

```text
active phase cycle:  +1 -> +i -> -1 -> -i -> +1 -> ...
null state:          0  (unoccupied channel)
```

So each channel stores one of:

```text
{0, +1, +i, -1, -i}
```

---

## 4) Panel B: Oriented Fano Triads (nonzero channels only)

Nonzero set:

```text
001, 010, 011, 100, 101, 110, 111
```

Canonical oriented triads (binary labels):

```text
(001,010,011)
(001,100,101)
(001,111,110)
(010,100,110)
(010,101,111)
(011,100,111)
(011,110,101)
```

Orientation rule:

```text
if (a,b,c) is oriented:
  a*b = +c
  b*c = +a
  c*a = +b

reverse order flips sign:
  b*a = -c
```

Triad closure check:

```text
a xor b xor c = 0
```

---

## 5) One-Line Synthesis

```text
XOR tells you destination channel.
Fano orientation tells you sign/handedness.
4-cycle phase tells you local clock state.
```

---

## 6) Quick Hand Checks

1. Pick any two nonzero labels `a,b`; verify `a xor b` is nonzero and in the set.
2. Pick any listed triad `(a,b,c)`; verify `a xor b xor c = 0`.
3. Reverse a product order and confirm sign flips by orientation convention.
4. Advance a channel phase 4 steps and confirm it returns to start.

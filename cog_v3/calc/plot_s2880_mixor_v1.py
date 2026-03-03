"""S2880 Left/Right Multiplication Covariance Matrix.

Renders a 2880x2880 interaction matrix for the group S2880 = C12 x Q240,
showing how every element mixes with every other under left and right multiplication.

Panels:
  LEFT  : color(s_i * s_j)
  RIGHT : color(s_j * s_i)   [same hue/phase; differs in Q saturation]
  NC    : non-commutativity mask  (s_i*s_j != s_j*s_i in Q)

Color encoding per cell:
  Hue        = Z12 phase index of product (12-step color wheel, 30 deg each)
  Saturation = Q family of product  A16=0.12 (pale) | B112=0.70 | C112=1.00 (vivid)
  Value      = 1.0 always

Sort order (rows AND cols):
  1. q_family_tag   A16 (192) | B112 (1344) | C112 (1344)
  2. phase_sector_mod3  Z3 generation: 0,1,2
  3. phase_sector_mod4  Z4 EM phase: 0,1,2,3
  4. q_id           within-sector Q index

Group boundaries drawn at each level (thick white = family, medium gray = mod3,
thin dark = mod4).

"Massless" channels = product lands on A16 family AND phase_idx=0 (real scalar unit).
These are highlighted in the NC panel as bright yellow dots on the diagonal and as
white pixels elsewhere.
"""

import csv
import os
import sys
import numpy as np
from fractions import Fraction

sys.path.insert(0, 'c:/Projects/CausalGraphTheory')
from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12

# Optional matplotlib -- only used for text/labels overlay
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

# ─────────────────────────────────────────────────────────────────────────────
BASE   = 'c:/Projects/CausalGraphTheory/cog_v3/sources'
OUT    = os.path.join(BASE, 'v3_s2880_mixor_matrix_v1.png')

# ─────────────────────────────────────────────────────────────────────────────
# Load invariants CSV
# ─────────────────────────────────────────────────────────────────────────────
print("Loading invariants CSV...", flush=True)

rows = []
with open(os.path.join(BASE, 'v3_s2880_invariants_v1.csv')) as f:
    for r in csv.DictReader(f):
        rows.append(r)
rows.sort(key=lambda r: int(r['s_id']))
N = len(rows)
print(f"  {N} elements loaded", flush=True)

FAM_MAP = {
    'A16_basis_signed_unit':       0,
    'B112_line_plus_e000_halfsum': 1,
    'C112_complement_halfsum':     2,
}

s_phase   = np.array([int(r['phase_idx'])           for r in rows], dtype=np.int32)
s_qid     = np.array([int(r['q_id'])                for r in rows], dtype=np.int32)
s_mod3    = np.array([int(r['phase_sector_mod3'])    for r in rows], dtype=np.int32)
s_mod4    = np.array([int(r['phase_sector_mod4'])    for r in rows], dtype=np.int32)
s_order   = np.array([int(r['order'])                for r in rows], dtype=np.int32)
s_fam     = np.array([FAM_MAP[r['q_family_tag']]     for r in rows], dtype=np.int32)

# Q family for each q_id (0..239)
q_fam_map = {}
for r in rows:
    qid = int(r['q_id'])
    if qid not in q_fam_map:
        q_fam_map[qid] = FAM_MAP[r['q_family_tag']]
q_fam = np.array([q_fam_map[k] for k in range(240)], dtype=np.int32)
print(f"  q_fam: A16={np.sum(q_fam==0)} B112={np.sum(q_fam==1)} C112={np.sum(q_fam==2)}", flush=True)

# ─────────────────────────────────────────────────────────────────────────────
# Q240 multiplication table  — use the authoritative c12 kernel table
# ─────────────────────────────────────────────────────────────────────────────
print("Loading Q multiplication table from c12 module...", flush=True)
QMT = c12.build_qmul_table().astype(np.int32)   # (240, 240)
print(f"  QMT: {QMT.shape}, q_id range: {QMT.min()}..{QMT.max()}", flush=True)

# Sanity: q_id=239 is the identity
assert list(QMT[239, :]) == list(range(240)), "Identity row broken"
assert list(QMT[:, 239]) == list(range(240)), "Identity col broken"
print("  Identity checks passed", flush=True)

# ─────────────────────────────────────────────────────────────────────────────
# Phase helpers
# ─────────────────────────────────────────────────────────────────────────────
P2M3 = np.zeros(12, dtype=np.int32)
P2M4 = np.zeros(12, dtype=np.int32)
for r in rows:
    k = int(r['phase_idx'])
    P2M3[k] = int(r['phase_sector_mod3'])
    P2M4[k] = int(r['phase_sector_mod4'])

# ─────────────────────────────────────────────────────────────────────────────
# Sort order
# ─────────────────────────────────────────────────────────────────────────────
sort_keys = [(s_fam[i], s_mod3[i], s_mod4[i], s_qid[i], i) for i in range(N)]
sort_keys.sort()
sidx = np.array([k[4] for k in sort_keys], dtype=np.int32)   # display-order s_ids

# Reordered property arrays (in display order)
sp  = s_phase[sidx]   # (2880,) Z12 phase
sq  = s_qid[sidx]     # (2880,) q_id
sfm = s_fam[sidx]     # (2880,) family

# ─────────────────────────────────────────────────────────────────────────────
# 2880 x 2880 product matrices
# ─────────────────────────────────────────────────────────────────────────────
print("Building 2880x2880 product tables...", flush=True)

# Phase:  (Z12 is abelian — same for L and R)
PH = (sp[:, None].astype(np.int32) + sp[None, :].astype(np.int32)) % 12   # (2880, 2880)

# Q family of L product:  Q[sq[i]] * Q[sq[j]]
QL_qid = QMT[np.ix_(sq, sq)].astype(np.int32)   # (2880, 2880)
QR_qid = QL_qid.T                                # Q[sq[j]] * Q[sq[i]]  [R is just the transpose]

fam_L = q_fam[QL_qid]   # (2880, 2880)  family of L product
fam_R = q_fam[QR_qid]   # (2880, 2880)  family of R product

# Non-commutativity mask
NC_mask = (QL_qid != QR_qid).astype(np.uint8)   # 1 where L != R in Q

# Massless indicator: product = A16 family AND phase_idx = 0 (real scalar)
massless_L = ((fam_L == 0) & (PH == 0)).astype(np.uint8)
massless_R = ((fam_R == 0) & (PH == 0)).astype(np.uint8)

print(f"  NC fraction: {NC_mask.mean():.3f}  massless-L fraction: {massless_L.mean():.4f}", flush=True)

# ─────────────────────────────────────────────────────────────────────────────
# Color lookup table  (12 phases x 3 families = 36 entries)
# ─────────────────────────────────────────────────────────────────────────────
SAT_VAL = np.array([0.12, 0.70, 1.00])   # A16, B112, C112

CLR = np.zeros((12, 3, 3), dtype=np.uint8)   # [phase_idx, family, RGB]
for pi in range(12):
    for fi in range(3):
        hue = pi / 12.0
        sat = float(SAT_VAL[fi])
        rgb_f = mcolors.hsv_to_rgb(np.array([[[hue, sat, 1.0]]]))
        CLR[pi, fi] = (rgb_f[0, 0] * 255).astype(np.uint8)

# Build RGB arrays for L and R  (2880, 2880, 3)
print("Building RGB matrices...", flush=True)
RGB_L  = CLR[PH, fam_L]                          # (2880, 2880, 3)
RGB_R  = CLR[PH, fam_R]                          # (2880, 2880, 3)

# NC panel: bright red = non-commutative, dark = commutative
# overlay massless_L in bright yellow
RGB_NC = np.zeros((N, N, 3), dtype=np.uint8)
RGB_NC[NC_mask == 1]  = [200,  40,  20]    # non-commutative = red
RGB_NC[NC_mask == 0]  = [ 20,  20,  80]    # commutative     = dark blue
RGB_NC[massless_L == 1] = [255, 230,   0]  # massless L = yellow

# ─────────────────────────────────────────────────────────────────────────────
# Group boundary indices  (in display-sorted order)
# ─────────────────────────────────────────────────────────────────────────────
sfm_s  = np.array([sort_keys[k][0] for k in range(N)])  # family
sm3_s  = np.array([sort_keys[k][1] for k in range(N)])  # mod3
sm4_s  = np.array([sort_keys[k][2] for k in range(N)])  # mod4

def bounds(keys):
    return list(np.where(np.diff(keys) != 0)[0] + 1)

fb   = bounds(sfm_s)                                          # family boundaries
mb3  = bounds(sfm_s * 3 + sm3_s)                            # mod3 boundaries
mb4  = bounds(sfm_s * 12 + sm3_s * 4 + sm4_s)              # mod4 boundaries

# Family midpoints (for labels)
fb_full = [0] + fb + [N]
fam_mids = [(fb_full[i] + fb_full[i+1]) // 2 for i in range(len(fb_full)-1)]

# ─────────────────────────────────────────────────────────────────────────────
# Draw boundary lines directly into numpy arrays
# ─────────────────────────────────────────────────────────────────────────────
def draw_lines(rgb, fb, mb3, mb4):
    img = rgb.copy()
    # mod4: thin dark separator
    for b in mb4:
        b = min(b, N-1)
        img[b, :] = [45, 45, 45]
        img[:, b] = [45, 45, 45]
    # mod3: medium gray
    for b in mb3:
        b = min(b, N-1)
        img[max(0,b-1):b+1, :] = [130, 130, 130]
        img[:, max(0,b-1):b+1] = [130, 130, 130]
    # family: thick white
    for b in fb:
        b = min(b, N-1)
        img[max(0,b-2):b+2, :] = [255, 255, 255]
        img[:, max(0,b-2):b+2] = [255, 255, 255]
    return img

print("Drawing boundaries...", flush=True)
RGB_L  = draw_lines(RGB_L,  fb, mb3, mb4)
RGB_R  = draw_lines(RGB_R,  fb, mb3, mb4)
RGB_NC = draw_lines(RGB_NC, fb, mb3, mb4)

# ─────────────────────────────────────────────────────────────────────────────
# Colorbar legend strip (2880 x 120 px)
# ─────────────────────────────────────────────────────────────────────────────
LEG_H = N          # same height as panels
LEG_W = 120        # pixels wide

leg = np.zeros((LEG_H, LEG_W, 3), dtype=np.uint8)
row_h = LEG_H // 12
col_w = LEG_W // 3
for pi in range(12):
    for fi in range(3):
        r0 = pi * row_h;  r1 = min((pi+1)*row_h, LEG_H)
        c0 = fi * col_w;  c1 = min((fi+1)*col_w, LEG_W)
        leg[r0:r1, c0:c1] = CLR[pi, fi]
# Draw horizontal lines between phase bands
for pi in range(1, 12):
    leg[pi * row_h, :] = [60, 60, 60]

# ─────────────────────────────────────────────────────────────────────────────
# Assemble raw pixel mosaic
# ─────────────────────────────────────────────────────────────────────────────
SEP = 12
sep = np.full((N, SEP, 3), 18, dtype=np.uint8)

mosaic = np.concatenate([RGB_L, sep, RGB_R, sep, RGB_NC, sep, leg], axis=1)
# Total width: 2880 + 12 + 2880 + 12 + 2880 + 12 + 120 = 8796  height: 2880

# ─────────────────────────────────────────────────────────────────────────────
# Annotated figure (matplotlib adds labels and title)
# ─────────────────────────────────────────────────────────────────────────────
print("Rendering annotated figure...", flush=True)

# Downsample 4x for matplotlib rendering (720x720 per panel)
SCALE = 4
def ds(a):
    return a[::SCALE, ::SCALE]

H_s = N // SCALE          # 720
W_total_s = mosaic.shape[1] // SCALE

# Per-panel downsampled images
L_s   = ds(RGB_L)
R_s   = ds(RGB_R)
NC_s  = ds(RGB_NC)
leg_s = ds(leg)

# Build axes widths proportional to data width
panel_w   = H_s                              # 720 px
sep_w     = SEP // SCALE                     # 3 px
leg_w_s   = LEG_W // SCALE                  # 30 px
total_w   = 3 * panel_w + 2 * sep_w + leg_w_s + 60   # extra for annotations

DPI = 150
FIG_H = (H_s + 180) / DPI                   # ~5.4 inches
FIG_W = total_w / DPI                       # ~15.3 inches

fig = plt.figure(figsize=(FIG_W + 2, FIG_H + 1.5), dpi=DPI, facecolor='#0c0c0c')

# Three data axes + one legend axis, manually placed
margin_l = 0.06
margin_r = 0.01
margin_t = 0.12
margin_b = 0.12
usable_w = 1.0 - margin_l - margin_r
usable_h = 1.0 - margin_t - margin_b

# Width fractions (relative to usable_w)
# 3 panels + 2 separators + legend
panel_frac = (3 * panel_w) / total_w
sep_frac   = sep_w / total_w
leg_frac   = (leg_w_s + 40) / total_w

pw  = usable_w * panel_frac / 3      # width of one data panel
sw  = usable_w * sep_frac             # separator fraction (tiny)
lw  = usable_w * leg_frac             # legend axis width

def make_ax(left, width):
    return fig.add_axes([margin_l + left, margin_b, width, usable_h])

x0 = 0
ax_L  = make_ax(x0,           pw);    x0 += pw + sw
ax_R  = make_ax(x0,           pw);    x0 += pw + sw
ax_NC = make_ax(x0,           pw);    x0 += pw + sw
ax_LG = make_ax(x0,           lw)

# ── Plot panels
for ax, img, title in [
    (ax_L,  L_s,   f"LEFT   s\u1D62 \u00D7 s\u2C7C"),
    (ax_R,  R_s,   f"RIGHT  s\u2C7C \u00D7 s\u1D62"),
    (ax_NC, NC_s,  "Non-commutativity  (red=mixed, yellow=massless)"),
]:
    ax.imshow(img, interpolation='nearest', aspect='equal', origin='upper')
    ax.set_facecolor('#0c0c0c')
    ax.set_title(title, color='#e0e0e0', fontsize=9, pad=4)
    ax.tick_params(colors='#888888', length=0, labelsize=7)

    # Draw family boundary lines (rescaled)
    for b in fb:
        bs = b / SCALE
        ax.axhline(bs, color='white',   lw=0.8, alpha=0.9)
        ax.axvline(bs, color='white',   lw=0.8, alpha=0.9)
    for b in mb3:
        bs = b / SCALE
        ax.axhline(bs, color='#aaaaaa', lw=0.35, alpha=0.65)
        ax.axvline(bs, color='#aaaaaa', lw=0.35, alpha=0.65)

    # Family tick labels on x and y
    ax.set_xticks([m / SCALE for m in fam_mids])
    ax.set_xticklabels(['A16\n(192)', 'B112\n(1344)', 'C112\n(1344)'],
                        color='#cccccc', fontsize=7)
    ax.set_yticks([m / SCALE for m in fam_mids])
    ax.set_yticklabels(['A16', 'B112', 'C112'], color='#cccccc', fontsize=7, rotation=90, va='center')
    for spine in ax.spines.values():
        spine.set_color('#444444')

# ── Legend axis
PHASE_LBLS = ['1 (real)', 'ζ¹','ζ²','ζ³','ζ⁴','ζ⁵','ζ⁶','ζ⁷','ζ⁸','ζ⁹','ζ¹⁰','ζ¹¹']
ax_LG.imshow(leg_s, interpolation='nearest', aspect='auto', origin='upper')
ax_LG.set_facecolor('#0c0c0c')
ax_LG.set_xticks([leg_w_s // 6, leg_w_s // 2, 5 * leg_w_s // 6])
ax_LG.set_xticklabels(['A16', 'B112', 'C112'], color='#cccccc', fontsize=6)
row_h_s = H_s // 12
ax_LG.set_yticks([(i + 0.5) * row_h_s for i in range(12)])
ax_LG.set_yticklabels(PHASE_LBLS, color='#cccccc', fontsize=6)
ax_LG.set_title('Phase × Family', color='#aaaaaa', fontsize=7, pad=3)
for spine in ax_LG.spines.values():
    spine.set_color('#444444')

# ── Family count annotation under each panel
FAM_NAMES = ['A16 (192 scalar units)', 'B112 (1344 line+e000)', 'C112 (1344 complement)']
fb_full2 = [0] + fb + [N]
for fi, fname in enumerate(FAM_NAMES):
    mid = (fb_full2[fi] + fb_full2[fi+1]) / 2 / SCALE
    for ax in [ax_L, ax_R, ax_NC]:
        ax.annotate(fname, xy=(mid, H_s + 2), xycoords='data',
                    color='#888888', fontsize=5, ha='center', va='top',
                    clip_on=False)

# ── Statistics block
n_nc   = int(NC_mask.sum())
n_c    = N*N - n_nc
n_ml   = int(massless_L.sum())
pct_nc = 100 * n_nc / (N*N)
pct_ml = 100 * n_ml / (N*N)
stats  = (f"S2880 = C12 \u00D7 Q240   |   2880 elements, 336 conj. classes\n"
          f"Non-commutative pairs: {n_nc:,} / {N*N:,}  ({pct_nc:.1f}%)    "
          f"Massless channels (A16+\u03B6\u2070): {n_ml:,}  ({pct_ml:.3f}%)\n"
          f"Family split: A16=192  B112=1344  C112=1344  |  "
          f"Z12 phases: {','.join(PHASE_LBLS[:6])}...")
fig.text(0.5, 0.98, stats,
         ha='center', va='top', color='#d0d0d0', fontsize=7.5,
         fontfamily='monospace',
         transform=fig.transFigure)

print(f"Saving {OUT}  ...", flush=True)
plt.savefig(OUT, dpi=DPI, bbox_inches='tight', facecolor='#0c0c0c')
plt.close()
print(f"Saved: {OUT}", flush=True)

# Also save the full-res raw mosaic
import importlib.util
if importlib.util.find_spec('PIL') is not None:
    from PIL import Image
    raw_path = OUT.replace('.png', '_fullres.png')
    Image.fromarray(mosaic).save(raw_path)
    print(f"Full-res saved: {raw_path}", flush=True)
else:
    # fallback: use matplotlib imsave
    raw_path = OUT.replace('.png', '_fullres.png')
    plt.imsave(raw_path, mosaic)
    print(f"Full-res saved (imsave): {raw_path}", flush=True)

print("Done.", flush=True)

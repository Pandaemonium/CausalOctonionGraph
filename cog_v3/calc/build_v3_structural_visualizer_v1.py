"""Build offline interactive structural visualizer for Q240/S960/S2880.

Features:
- Dataset switch: Q240, S960, S2880
- Group mode: pull points into per-group boxes by selected column
- Color mode: color points by selected column
- Hover tooltip with key structural fields

Output:
- `cog_v3/sources/v3_structural_visualizer_v1.html`
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

from cog_v3.calc import v3_s2880_utils as u


ROOT = u.repo_root()
OUT_HTML = ROOT / "cog_v3" / "sources" / "v3_structural_visualizer_v1.html"

Q240_CSV = ROOT / "cog_v3" / "sources" / "v3_octavian240_elements_v1.csv"
S960_CSV = ROOT / "cog_v3" / "sources" / "v3_s960_elements_v1.csv"
S2880_INV_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_invariants_v1.csv"
S2880_FP_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_action_fingerprints_v1.csv"
S2880_MAP_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_element_class_map_v1.csv"
S2880_ROLE_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_interaction_catalog_v1.csv"


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _index(rows: Sequence[Dict[str, str]], key: str) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for r in rows:
        out[str(r[key])] = r
    return out


def _trim_label(label: str, max_len: int = 120) -> str:
    s = str(label)
    if len(s) <= int(max_len):
        return s
    return s[: int(max_len - 3)] + "..."


def _bucket01(v: float, *, step: float = 0.1) -> str:
    x = max(0.0, min(1.0, float(v)))
    b = int(round(x / float(step)))
    return f"{b * step:.1f}"


def _unique_count(rows: Sequence[Dict[str, Any]], col: str) -> int:
    vals = set()
    for r in rows:
        vals.add(str(r.get(col, "")))
    return int(len(vals))


def _recommend_columns(
    rows: Sequence[Dict[str, Any]],
    *,
    exclude: Sequence[str],
    force_group: Sequence[str] = (),
    force_color: Sequence[str] = (),
    max_unique_group: int = 24,
    max_unique_color: int = 48,
) -> Dict[str, List[str]]:
    if not rows:
        return {"group": [], "color": []}
    cols = [c for c in rows[0].keys() if c not in set(exclude)]
    group_cols: List[str] = []
    color_cols: List[str] = []
    for c in cols:
        ucnt = _unique_count(rows, c)
        if 1 < ucnt <= int(max_unique_group):
            group_cols.append(str(c))
        if 1 < ucnt <= int(max_unique_color):
            color_cols.append(str(c))
    group_cols.sort()
    color_cols.sort()
    force_g = [str(c) for c in force_group if str(c) in cols]
    force_c = [str(c) for c in force_color if str(c) in cols]
    group_cols = sorted(set(group_cols).union(force_g))
    color_cols = sorted(set(color_cols).union(force_c))
    return {"group": group_cols, "color": color_cols}


def _build_q240_dataset() -> Dict[str, Any]:
    rows_in = _read_csv(Q240_CSV)
    rows: List[Dict[str, Any]] = []
    for r in rows_in:
        rows.append(
            {
                "id": int(r["id"]),
                "label": _trim_label(r["label"]),
                "order": int(r["order"]),
                "orbit_rep_id": int(r["orbit_rep_id"]),
                "orbit_family": str(r["orbit_group"]),
                "orbit_family_order_class": str(r["orbit_group_order_class"]),
                "orbit_family_q_family_class": str(r["orbit_group_family_class"]),
                "family_tag": str(r["family_tag"]),
                "g2_proxy_tag": str(r["g2_proxy_tag"]),
                "support_size": int(r["support_size"]),
                "has_e000": str(r["has_e000"]),
                "has_e111": str(r["has_e111"]),
                "inner_conj_l_orbit_size": int(r["inner_conj_l_orbit_size"]),
                "inner_conj_r_orbit_size": int(r["inner_conj_r_orbit_size"]),
                "q_order_class_size": len(str(r["orbit_group_order_class"]).split("|")),
                "q_family_class_size": len(str(r["orbit_group_family_class"]).split("|")),
                "loop_template_id": (
                    f"ord={int(r['order'])}|fam={str(r['family_tag'])}|supp={int(r['support_size'])}|"
                    f"ol={int(r['inner_conj_l_orbit_size'])}|or={int(r['inner_conj_r_orbit_size'])}"
                ),
                "loop_anchor_id": str(r["orbit_rep_id"]),
            }
        )
    rec = _recommend_columns(
        rows,
        exclude=("id", "label"),
        force_group=("orbit_family", "orbit_rep_id", "orbit_size"),
    )
    return {
        "dataset_id": "Q240",
        "title": "Q240",
        "id_field": "id",
        "label_field": "label",
        "rows": rows,
        "group_columns": rec["group"],
        "color_columns": rec["color"],
        "default_group_column": "orbit_family" if "orbit_family" in rec["group"] else ("family_tag" if "family_tag" in rec["group"] else (rec["group"][0] if rec["group"] else "")),
        "default_color_column": "order" if "order" in rec["color"] else (rec["color"][0] if rec["color"] else ""),
        "template_columns": ["loop_template_id"],
        "anchor_columns": ["loop_anchor_id", "orbit_family", "family_tag"],
        "default_template_column": "loop_template_id",
        "default_anchor_column": "loop_anchor_id",
    }


def _build_s960_dataset() -> Dict[str, Any]:
    rows_in = _read_csv(S960_CSV)
    rows: List[Dict[str, Any]] = []
    for r in rows_in:
        rows.append(
            {
                "id": int(r["id"]),
                "label": _trim_label(r["label"]),
                "phase_idx": int(r["phase_idx"]),
                "phase_label": str(r["phase_label"]),
                "phase_order": int(r["phase_order"]),
                "q_id": int(r["q_id"]),
                "q_order": int(r["q_order"]),
                "q_family_tag": str(r["q_family_tag"]),
                "q_g2_proxy_tag": str(r["q_g2_proxy_tag"]),
                "order": int(r["order"]),
                "support_size": int(r["support_size"]),
                "orbit_rep_id": int(r["orbit_rep_id"]),
                "orbit_family": str(r["orbit_group"]),
                "orbit_family_phase_class": str(r["orbit_group_phase_class"]),
                "orbit_family_q_class": str(r["orbit_group_q_class"]),
                "inner_conj_l_orbit_size": int(r["inner_conj_l_orbit_size"]),
                "inner_conj_r_orbit_size": int(r["inner_conj_r_orbit_size"]),
                "orbit_size": int(r["orbit_size"]),
                "loop_template_id": (
                    f"ord={int(r['order'])}|phord={int(r['phase_order'])}|qord={int(r['q_order'])}|"
                    f"qfam={str(r['q_family_tag'])}|ol={int(r['inner_conj_l_orbit_size'])}|or={int(r['inner_conj_r_orbit_size'])}"
                ),
                "loop_anchor_id": str(r["orbit_rep_id"]),
            }
        )
    rec = _recommend_columns(
        rows,
        exclude=("id", "label"),
        force_group=("orbit_family", "orbit_rep_id", "orbit_size"),
    )
    return {
        "dataset_id": "S960",
        "title": "S960 (C4 x Q240)",
        "id_field": "id",
        "label_field": "label",
        "rows": rows,
        "group_columns": rec["group"],
        "color_columns": rec["color"],
        "default_group_column": "orbit_family" if "orbit_family" in rec["group"] else ("q_family_tag" if "q_family_tag" in rec["group"] else (rec["group"][0] if rec["group"] else "")),
        "default_color_column": "phase_label" if "phase_label" in rec["color"] else (rec["color"][0] if rec["color"] else ""),
        "template_columns": ["loop_template_id"],
        "anchor_columns": ["loop_anchor_id", "orbit_family", "q_family_tag", "phase_label"],
        "default_template_column": "loop_template_id",
        "default_anchor_column": "loop_anchor_id",
    }


def _build_s2880_dataset() -> Dict[str, Any]:
    inv_rows = _read_csv(S2880_INV_CSV)
    fp_rows = _read_csv(S2880_FP_CSV) if S2880_FP_CSV.exists() else []
    map_rows = _read_csv(S2880_MAP_CSV) if S2880_MAP_CSV.exists() else []
    role_rows = _read_csv(S2880_ROLE_CSV) if S2880_ROLE_CSV.exists() else []

    fp_by = _index(fp_rows, "s_id") if fp_rows else {}
    map_by = _index(map_rows, "s_id") if map_rows else {}
    role_by = _index(role_rows, "s_id") if role_rows else {}

    rows: List[Dict[str, Any]] = []
    for r in inv_rows:
        sid = str(r["s_id"])
        fpr = fp_by.get(sid, {})
        cmr = map_by.get(sid, {})
        rlr = role_by.get(sid, {})
        rows.append(
            {
                "id": int(r["s_id"]),
                "label": _trim_label(r["label"]),
                "phase_idx": int(r["phase_idx"]),
                "phase_label": str(r["phase_label"]),
                "phase_sector_mod3": int(r["phase_sector_mod3"]),
                "phase_sector_mod4": int(r["phase_sector_mod4"]),
                "order": int(r["order"]),
                "q_id": int(r["q_id"]),
                "q_order": int(r["q_order"]),
                "q_family_tag": str(r["q_family_tag"]),
                "q_g2_proxy_tag": str(r["q_g2_proxy_tag"]),
                "orbit_family_l": str(r.get("conj_class_id_l", "")),
                "orbit_family_r": str(r.get("conj_class_id_r", "")),
                "inner_conj_l_orbit_size": int(r["inner_conj_l_orbit_size"]),
                "inner_conj_r_orbit_size": int(r["inner_conj_r_orbit_size"]),
                "q_centralizer_size": int(r["q_centralizer_size"]),
                "class_id": str(cmr.get("class_id", "")),
                "dominant_dp_left": int(fpr["dominant_dp_left"]) if str(fpr.get("dominant_dp_left", "")).strip() != "" else -1,
                "dominant_dg_left": int(fpr["dominant_dg_left"]) if str(fpr.get("dominant_dg_left", "")).strip() != "" else -1,
                "commute_rate_probe": float(fpr["commute_rate_probe"]) if str(fpr.get("commute_rate_probe", "")).strip() != "" else 0.0,
                "assoc_nonzero_rate": float(fpr["assoc_nonzero_rate"]) if str(fpr.get("assoc_nonzero_rate", "")).strip() != "" else 0.0,
                "probe_order_preserve_rate": float(fpr["probe_order_preserve_rate"]) if str(fpr.get("probe_order_preserve_rate", "")).strip() != "" else 0.0,
                "top_role_1": str(rlr.get("top_role_1", "")),
                "top_role_1_score": float(rlr["top_role_1_score"]) if str(rlr.get("top_role_1_score", "")).strip() != "" else 0.0,
                "top_role_2": str(rlr.get("top_role_2", "")),
                "top_role_3": str(rlr.get("top_role_3", "")),
                "loop_template_id": (
                    f"ord={int(r['order'])}|dp={int(fpr.get('dominant_dp_left', -1))}|dg={int(fpr.get('dominant_dg_left', -1))}|"
                    f"qfam={str(r['q_family_tag'])}|ol={int(r['inner_conj_l_orbit_size'])}|or={int(r['inner_conj_r_orbit_size'])}|"
                    f"assoc={_bucket01(float(fpr.get('assoc_nonzero_rate', 0.0)))}|"
                    f"comm={_bucket01(float(fpr.get('commute_rate_probe', 0.0)))}"
                ),
                "loop_anchor_id": str(r["q_id"]),
            }
        )

    rec = _recommend_columns(
        rows,
        exclude=("id", "label"),
        force_group=("class_id", "orbit_family_l", "orbit_family_r", "q_family_tag", "phase_sector_mod3", "loop_template_id"),
    )
    return {
        "dataset_id": "S2880",
        "title": "S2880 (C12 x Q240)",
        "id_field": "id",
        "label_field": "label",
        "rows": rows,
        "group_columns": rec["group"],
        "color_columns": rec["color"],
        "default_group_column": "orbit_family_l" if "orbit_family_l" in rec["group"] else ("class_id" if "class_id" in rec["group"] else ("q_family_tag" if "q_family_tag" in rec["group"] else (rec["group"][0] if rec["group"] else ""))),
        "default_color_column": "top_role_1" if "top_role_1" in rec["color"] else ("phase_label" if "phase_label" in rec["color"] else (rec["color"][0] if rec["color"] else "")),
        "template_columns": ["loop_template_id", "class_id"],
        "anchor_columns": ["loop_anchor_id", "orbit_family_l", "orbit_family_r", "q_family_tag", "phase_sector_mod3"],
        "default_template_column": "loop_template_id",
        "default_anchor_column": "orbit_family_l",
    }


def _build_html(payload: Dict[str, Any]) -> str:
    data_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>v3 Structural Visualizer</title>
  <style>
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
      background: #0b1020;
      color: #e5e7eb;
    }}
    .wrap {{
      display: grid;
      grid-template-columns: 340px 1fr;
      height: 100vh;
    }}
    .panel {{
      border-right: 1px solid #1f2937;
      padding: 14px 12px;
      overflow: auto;
      background: #0a1329;
    }}
    .panel h1 {{
      margin: 0 0 8px;
      font-size: 16px;
    }}
    .panel p {{
      margin: 0 0 10px;
      color: #9ca3af;
      font-size: 13px;
    }}
    label {{
      display: block;
      margin-top: 10px;
      margin-bottom: 4px;
      font-size: 12px;
      color: #cbd5e1;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    select, input[type="range"] {{
      width: 100%;
      background: #0f172a;
      color: #e5e7eb;
      border: 1px solid #334155;
      border-radius: 6px;
      padding: 7px 8px;
      font-size: 13px;
      box-sizing: border-box;
    }}
    .row {{
      display: flex;
      gap: 8px;
      align-items: center;
      margin-top: 10px;
    }}
    .stats {{
      margin-top: 14px;
      font-size: 12px;
      color: #cbd5e1;
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 6px;
      padding: 8px;
      line-height: 1.5;
      white-space: pre-wrap;
    }}
    .hint {{
      margin-top: 8px;
      font-size: 12px;
      color: #94a3b8;
    }}
    .canvas-wrap {{
      position: relative;
      overflow: hidden;
      background: radial-gradient(circle at 20% 20%, #112449, #0b1020 55%);
    }}
    #viz {{
      display: block;
      width: 100%;
      height: 100%;
    }}
    .tooltip {{
      position: absolute;
      pointer-events: none;
      min-width: 220px;
      max-width: 420px;
      background: rgba(2, 8, 23, 0.95);
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 8px 10px;
      color: #e2e8f0;
      font-size: 12px;
      line-height: 1.4;
      transform: translate(12px, 12px);
      display: none;
      z-index: 10;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="panel">
      <h1>v3 Structural Visualizer</h1>
      <p>Select dataset, then choose structural columns for grouping and color.</p>
      <label>Dataset</label>
      <select id="datasetSel"></select>
      <label>Group (box clustering)</label>
      <select id="groupSel"></select>
      <label>Color</label>
      <select id="colorSel"></select>
      <label>View Mode</label>
      <select id="viewSel">
        <option value="points">Point Cloud</option>
        <option value="atlas">Orbit Atlas</option>
      </select>
      <label>Template Column (Atlas)</label>
      <select id="templateSel"></select>
      <label>Anchor Column (Atlas)</label>
      <select id="anchorSel"></select>
      <label>Atlas Top-N (per axis)</label>
      <input id="atlasTopN" type="range" min="8" max="40" value="24" />
      <div class="row">
        <input id="groupToggle" type="checkbox" checked />
        <span style="font-size:13px;color:#cbd5e1;">Enable Group Boxes</span>
      </div>
      <label>Point Size</label>
      <input id="sizeRange" type="range" min="1" max="7" value="3" />
      <div id="stats" class="stats"></div>
      <div class="hint">
        Point Cloud: structural grouping and coloring. Orbit Atlas: template x anchor heatmap
        to show repeated loop structure across different octonion anchors.
      </div>
    </div>
    <div class="canvas-wrap">
      <canvas id="viz"></canvas>
      <div id="tip" class="tooltip"></div>
    </div>
  </div>
  <script>
  const payload = {data_json};
  const datasets = payload.datasets;
  const datasetSel = document.getElementById('datasetSel');
  const groupSel = document.getElementById('groupSel');
  const colorSel = document.getElementById('colorSel');
  const viewSel = document.getElementById('viewSel');
  const templateSel = document.getElementById('templateSel');
  const anchorSel = document.getElementById('anchorSel');
  const atlasTopN = document.getElementById('atlasTopN');
  const groupToggle = document.getElementById('groupToggle');
  const sizeRange = document.getElementById('sizeRange');
  const statsEl = document.getElementById('stats');
  const canvas = document.getElementById('viz');
  const tip = document.getElementById('tip');
  const ctx = canvas.getContext('2d');

  const palette = [
    '#38bdf8','#f97316','#22c55e','#f43f5e','#a78bfa','#facc15',
    '#14b8a6','#fb7185','#84cc16','#60a5fa','#f59e0b','#34d399',
    '#e879f9','#c084fc','#ef4444','#10b981','#8b5cf6','#d946ef'
  ];

  let current = {{
    datasetId: datasets[0].dataset_id,
    groupCol: '',
    colorCol: '',
    viewMode: 'points',
    templateCol: '',
    anchorCol: '',
    atlasTopN: 24,
    groupEnabled: true,
    pointSize: 3
  }};
  let world = {{ points: [], boxes: [] }};

  function seededUnit(seed) {{
    let x = Number(seed) || 0;
    x = (x ^ 0x9e3779b9) >>> 0;
    x = (x * 1664525 + 1013904223) >>> 0;
    return (x & 0xffffff) / 0x1000000;
  }}

  function hashString(s) {{
    let h = 2166136261 >>> 0;
    const str = String(s);
    for (let i=0; i<str.length; i++) {{
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }}
    return h >>> 0;
  }}

  function resize() {{
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.max(200, Math.floor(rect.width));
    canvas.height = Math.max(200, Math.floor(rect.height));
    layoutAndRender();
  }}

  function getDataset() {{
    return datasets.find(d => d.dataset_id === current.datasetId) || datasets[0];
  }}

  function fillSelect(sel, values, preferred) {{
    sel.innerHTML = '';
    const noneOpt = document.createElement('option');
    noneOpt.value = '';
    noneOpt.textContent = '(none)';
    sel.appendChild(noneOpt);
    values.forEach(v => {{
      const opt = document.createElement('option');
      opt.value = v;
      opt.textContent = v;
      sel.appendChild(opt);
    }});
    const pick = preferred && values.includes(preferred) ? preferred : '';
    sel.value = pick;
  }}

  function updateSelectors() {{
    const ds = getDataset();
    fillSelect(groupSel, ds.group_columns || [], ds.default_group_column || '');
    fillSelect(colorSel, ds.color_columns || [], ds.default_color_column || '');
    fillSelect(templateSel, ds.template_columns || [], ds.default_template_column || '');
    fillSelect(anchorSel, ds.anchor_columns || [], ds.default_anchor_column || '');
    current.groupCol = groupSel.value;
    current.colorCol = colorSel.value;
    current.templateCol = templateSel.value;
    current.anchorCol = anchorSel.value;
  }}

  function colorFor(value, idx) {{
    const s = String(value);
    if (!s) return '#9ca3af';
    if (idx < palette.length) return palette[idx];
    const h = hashString(s) % 360;
    return `hsl(${{h}},75%,58%)`;
  }}

  function layoutPoints(ds) {{
    const W = canvas.width, H = canvas.height;
    const margin = 36;
    const rows = ds.rows || [];
    const idField = ds.id_field || 'id';
    const labelField = ds.label_field || 'label';
    const groupCol = current.groupEnabled ? current.groupCol : '';
    const colorCol = current.colorCol;

    const groupVals = [];
    const groupMap = new Map();
    rows.forEach(r => {{
      const g = groupCol ? String(r[groupCol] ?? '') : '__all__';
      if (!groupMap.has(g)) {{
        groupMap.set(g, []);
        groupVals.push(g);
      }}
      groupMap.get(g).push(r);
    }});

    const G = groupVals.length || 1;
    const cols = Math.ceil(Math.sqrt(G));
    const gridRows = Math.ceil(G / cols);
    const boxW = (W - margin*2) / cols;
    const boxH = (H - margin*2) / gridRows;

    const boxes = [];
    const points = [];

    const colorValues = [];
    const colorIdx = new Map();
    rows.forEach(r => {{
      const c = colorCol ? String(r[colorCol] ?? '') : '';
      if (c && !colorIdx.has(c)) {{
        colorIdx.set(c, colorValues.length);
        colorValues.push(c);
      }}
    }});

    groupVals.forEach((gv, gi) => {{
      const cx = gi % cols;
      const cy = Math.floor(gi / cols);
      const x0 = margin + cx * boxW;
      const y0 = margin + cy * boxH;
      const x1 = x0 + boxW;
      const y1 = y0 + boxH;
      boxes.push({{group: gv, x0, y0, x1, y1, count: groupMap.get(gv).length}});
      const members = groupMap.get(gv);
      for (let i=0; i<members.length; i++) {{
        const r = members[i];
        const sid = Number(r[idField]);
        const seedA = hashString(String(sid) + '|A');
        const seedB = hashString(String(sid) + '|B');
        const ux = seededUnit(seedA);
        const uy = seededUnit(seedB);
        const px = x0 + 10 + ux * Math.max(1, (boxW - 20));
        const py = y0 + 18 + uy * Math.max(1, (boxH - 28));
        const cv = colorCol ? String(r[colorCol] ?? '') : '';
        const cidx = cv ? (colorIdx.get(cv) ?? 0) : 0;
        points.push({{
          x: px, y: py,
          id: sid,
          label: String(r[labelField] ?? ''),
          row: r,
          group: gv,
          colorValue: cv,
          color: cv ? colorFor(cv, cidx) : '#38bdf8'
        }});
      }}
    }});

    return {{points, boxes, colorValues, colorIdx}};
  }}

  function layoutAtlas(ds) {{
    const rows = ds.rows || [];
    const tplCol = current.templateCol;
    const ancCol = current.anchorCol;
    const W = canvas.width, H = canvas.height;
    const leftPad = 210, topPad = 120, rightPad = 30, bottomPad = 30;
    const maxN = Math.max(8, Number(current.atlasTopN) || 24);

    const tplCounts = new Map();
    const ancCounts = new Map();
    const pairCounts = new Map();

    rows.forEach(r => {{
      const t = tplCol ? String(r[tplCol] ?? '') : '';
      const a = ancCol ? String(r[ancCol] ?? '') : '';
      if (!t || !a) return;
      tplCounts.set(t, (tplCounts.get(t) || 0) + 1);
      ancCounts.set(a, (ancCounts.get(a) || 0) + 1);
      const k = t + '\\t' + a;
      pairCounts.set(k, (pairCounts.get(k) || 0) + 1);
    }});

    const tplVals = Array.from(tplCounts.entries()).sort((x, y) => y[1] - x[1]).slice(0, maxN).map(x => x[0]);
    const ancVals = Array.from(ancCounts.entries()).sort((x, y) => y[1] - x[1]).slice(0, maxN).map(x => x[0]);
    const tplIdx = new Map(tplVals.map((v, i) => [v, i]));
    const ancIdx = new Map(ancVals.map((v, i) => [v, i]));

    const R = tplVals.length || 1;
    const C = ancVals.length || 1;
    const gridW = Math.max(120, W - leftPad - rightPad);
    const gridH = Math.max(120, H - topPad - bottomPad);
    const cw = gridW / C;
    const ch = gridH / R;

    let maxCount = 0;
    pairCounts.forEach((v, k) => {{
      const parts = k.split('\\t');
      if (parts.length !== 2) return;
      if (!tplIdx.has(parts[0]) || !ancIdx.has(parts[1])) return;
      if (v > maxCount) maxCount = v;
    }});
    maxCount = Math.max(1, maxCount);

    const cells = [];
    pairCounts.forEach((v, k) => {{
      const parts = k.split('\\t');
      if (parts.length !== 2) return;
      const t = parts[0], a = parts[1];
      const ri = tplIdx.get(t), ci = ancIdx.get(a);
      if (ri === undefined || ci === undefined) return;
      const x = leftPad + ci * cw;
      const y = topPad + ri * ch;
      const inten = Math.log1p(v) / Math.log1p(maxCount);
      const hue = 210 - Math.round(180 * inten);
      const col = `hsl(${{hue}},85%,${{22 + Math.round(38 * inten)}}%)`;
      cells.push({{
        x, y, w: cw, h: ch, count: v, template: t, anchor: a, color: col
      }});
    }});

    return {{
      tplVals, ancVals, cells, maxCount,
      leftPad, topPad, rightPad, bottomPad, cw, ch,
      totalRows: rows.length
    }};
  }}


  function renderPoints(ds) {{
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    world.boxes.forEach((b) => {{
      ctx.save();
      ctx.strokeStyle = 'rgba(148,163,184,0.35)';
      ctx.lineWidth = 1;
      ctx.strokeRect(b.x0 + 0.5, b.y0 + 0.5, (b.x1 - b.x0) - 1, (b.y1 - b.y0) - 1);
      ctx.fillStyle = 'rgba(148,163,184,0.06)';
      ctx.fillRect(b.x0 + 1, b.y0 + 1, (b.x1 - b.x0) - 2, 18);
      ctx.fillStyle = '#cbd5e1';
      ctx.font = '11px ui-sans-serif,system-ui';
      const gname = b.group === '__all__' ? '(all)' : b.group;
      const txt = `${{gname}} [${{b.count}}]`;
      ctx.fillText(txt.length > 42 ? txt.slice(0, 42) + '?' : txt, b.x0 + 4, b.y0 + 13);
      ctx.restore();
    }});

    const pr = Number(current.pointSize) || 3;
    world.points.forEach(p => {{
      ctx.beginPath();
      ctx.arc(p.x, p.y, pr, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = 0.90;
      ctx.fill();
    }});
    ctx.globalAlpha = 1.0;

    const gcol = current.groupCol || '(none)';
    const ccol = current.colorCol || '(none)';
    statsEl.textContent =
`dataset: ${{ds.title}}
view: Point Cloud
rows: ${{(ds.rows || []).length}}
group column: ${{gcol}}
group count: ${{world.boxes.length}}
color column: ${{ccol}}
color values: ${{world.colorValues.length}}
point size: ${{current.pointSize}}`;
  }}

  function renderAtlas(ds) {{
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);
    const A = world.atlas;
    if (!A) return;

    A.cells.forEach(c => {{
      ctx.fillStyle = c.color;
      ctx.fillRect(c.x + 0.5, c.y + 0.5, Math.max(1, c.w - 1), Math.max(1, c.h - 1));
    }});

    ctx.strokeStyle = 'rgba(148,163,184,0.35)';
    ctx.lineWidth = 1;
    ctx.strokeRect(
      A.leftPad + 0.5,
      A.topPad + 0.5,
      Math.max(1, A.cw * Math.max(1, A.ancVals.length) - 1),
      Math.max(1, A.ch * Math.max(1, A.tplVals.length) - 1)
    );

    ctx.fillStyle = '#cbd5e1';
    ctx.font = '11px ui-sans-serif,system-ui';
    A.ancVals.forEach((v, i) => {{
      const x = A.leftPad + (i + 0.5) * A.cw;
      const txt = String(v);
      ctx.save();
      ctx.translate(x, A.topPad - 6);
      ctx.rotate(-0.6);
      ctx.fillText(txt.length > 26 ? txt.slice(0, 26) + '...' : txt, 0, 0);
      ctx.restore();
    }});
    A.tplVals.forEach((v, i) => {{
      const y = A.topPad + (i + 0.5) * A.ch + 4;
      const txt = String(v);
      ctx.fillText(txt.length > 32 ? txt.slice(0, 32) + '...' : txt, 6, y);
    }});

    ctx.fillStyle = '#93c5fd';
    ctx.font = '12px ui-sans-serif,system-ui';
    ctx.fillText(`template: ${{current.templateCol || '(none)'}}`, A.leftPad, 18);
    ctx.fillText(`anchor: ${{current.anchorCol || '(none)'}}`, A.leftPad, 34);
    ctx.fillText(`max cell count: ${{A.maxCount}}`, A.leftPad, 50);

    statsEl.textContent =
`dataset: ${{ds.title}}
view: Orbit Atlas
rows: ${{A.totalRows}}
template column: ${{current.templateCol || '(none)'}}
template values shown: ${{A.tplVals.length}}
anchor column: ${{current.anchorCol || '(none)'}}
anchor values shown: ${{A.ancVals.length}}
filled cells: ${{A.cells.length}}
atlas top-N: ${{current.atlasTopN}}`;
  }}

  function render() {{
    const ds = getDataset();
    if (current.viewMode === 'atlas') {{
      renderAtlas(ds);
    }} else {{
      renderPoints(ds);
    }}
  }}

  function layoutAndRender() {{
    const ds = getDataset();
    world = layoutPoints(ds);
    world.atlas = layoutAtlas(ds);
    render();
  }}

  function updateDataset() {{
    current.datasetId = datasetSel.value;
    updateSelectors();
    layoutAndRender();
  }}

  function setup() {{
    datasets.forEach(d => {{
      const opt = document.createElement('option');
      opt.value = d.dataset_id;
      opt.textContent = d.title;
      datasetSel.appendChild(opt);
    }});
    datasetSel.value = current.datasetId;
    viewSel.value = current.viewMode;
    atlasTopN.value = String(current.atlasTopN);
    updateSelectors();

    datasetSel.addEventListener('change', updateDataset);
    groupSel.addEventListener('change', () => {{
      current.groupCol = groupSel.value;
      layoutAndRender();
    }});
    colorSel.addEventListener('change', () => {{
      current.colorCol = colorSel.value;
      layoutAndRender();
    }});
    viewSel.addEventListener('change', () => {{
      current.viewMode = viewSel.value || 'points';
      layoutAndRender();
    }});
    templateSel.addEventListener('change', () => {{
      current.templateCol = templateSel.value;
      layoutAndRender();
    }});
    anchorSel.addEventListener('change', () => {{
      current.anchorCol = anchorSel.value;
      layoutAndRender();
    }});
    atlasTopN.addEventListener('input', () => {{
      current.atlasTopN = Number(atlasTopN.value) || 24;
      layoutAndRender();
    }});
    groupToggle.addEventListener('change', () => {{
      current.groupEnabled = !!groupToggle.checked;
      layoutAndRender();
    }});
    sizeRange.addEventListener('input', () => {{
      current.pointSize = Number(sizeRange.value) || 3;
      render();
    }});

    canvas.addEventListener('mousemove', (ev) => {{
      const rect = canvas.getBoundingClientRect();
      const mx = ev.clientX - rect.left;
      const my = ev.clientY - rect.top;
      if (current.viewMode === 'atlas') {{
        const A = world.atlas;
        if (!A) {{
          tip.style.display = 'none';
          return;
        }}
        let hit = null;
        for (const c of A.cells) {{
          if (mx >= c.x && mx <= (c.x + c.w) && my >= c.y && my <= (c.y + c.h)) {{
            hit = c;
            break;
          }}
        }}
        if (!hit) {{
          tip.style.display = 'none';
          return;
        }}
        tip.textContent =
`template: ${{hit.template}}
anchor: ${{hit.anchor}}
count: ${{hit.count}}`;
        tip.style.left = `${{mx}}px`;
        tip.style.top = `${{my}}px`;
        tip.style.display = 'block';
        return;
      }}
      let best = null;
      let bestD2 = 80;
      for (const p of world.points) {{
        const dx = p.x - mx, dy = p.y - my;
        const d2 = dx*dx + dy*dy;
        if (d2 < bestD2) {{
          bestD2 = d2;
          best = p;
        }}
      }}
      if (!best) {{
        tip.style.display = 'none';
        return;
      }}
      const keys = Object.keys(best.row).slice(0, 16);
      const body = keys.map(k => `${{k}}: ${{best.row[k]}}`).join('\\n');
      tip.textContent = `id: ${{best.id}}\\nlabel: ${{best.label}}\\n\\n${{body}}`;
      tip.style.left = `${{mx}}px`;
      tip.style.top = `${{my}}px`;
      tip.style.display = 'block';
    }});
    canvas.addEventListener('mouseleave', () => {{
      tip.style.display = 'none';
    }});

    window.addEventListener('resize', resize);
    resize();
  }}

  setup();
  </script>
</body>
</html>
"""


def build_payload() -> Dict[str, Any]:
    if not Q240_CSV.exists():
        raise FileNotFoundError(f"Missing {Q240_CSV}")
    if not S960_CSV.exists():
        raise FileNotFoundError(f"Missing {S960_CSV}")
    if not S2880_INV_CSV.exists():
        raise FileNotFoundError(f"Missing {S2880_INV_CSV}")

    datasets = [
        _build_q240_dataset(),
        _build_s960_dataset(),
        _build_s2880_dataset(),
    ]
    return {
        "schema_version": "v3_structural_visualizer_v1",
        "datasets": datasets,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Build v3 structural visualizer HTML.")
    ap.add_argument("--out-html", type=str, default=str(OUT_HTML))
    args = ap.parse_args()
    payload = build_payload()
    html = _build_html(payload)
    out = Path(args.out_html).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}")
    print(f"datasets={','.join(d['dataset_id'] for d in payload['datasets'])}")


if __name__ == "__main__":
    main()

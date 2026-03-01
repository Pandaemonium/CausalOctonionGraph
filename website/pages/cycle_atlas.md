# Cycle Atlas

This page tracks repeating time patterns ("cycles") in XOR-octonion motif dynamics.

See also: [Standard Model Free Parameters: First-Principles Derivation Table](/web/pages/sm_parameter_derivation_table)
See also: [Particle Motif GIF Atlas](/web/pages/particle_motif_cycle_gif_atlas)

Default view is **Layman**. Switch to **Physicist** for raw policy/trace details.

<div id="cycle-atlas-app" class="atlas-shell">
  <section class="atlas-hero">
    <div class="atlas-kicker">Motif Time Structure</div>
    <h1>Cycle Atlas</h1>
    <p>
      Stable motifs tend to lock into fast periodic rhythms. Coupled motifs can
      generate longer periods. This atlas makes those rhythms visible.
    </p>
    <div id="atlas-metrics" class="atlas-metrics"></div>
  </section>

  <section class="atlas-controls">
    <div class="control-card">
      <label>Complexity</label>
      <div id="mode-toggle" class="mode-toggle">
        <button data-mode="layman" class="is-active">Layman</button>
        <button data-mode="student">Student</button>
        <button data-mode="physicist">Physicist</button>
      </div>
    </div>

    <div class="control-card">
      <label>Coupled Filter</label>
      <div class="row">
        <select id="min-period">
          <option value="2">Period >= 2</option>
          <option value="4">Period >= 4</option>
          <option value="8">Period >= 8</option>
          <option value="16">Period >= 16</option>
        </select>
      </div>
      <div class="row">
        <label class="inline-check">
          <input id="gt4-only" type="checkbox" checked />
          Show only periods > 4
        </label>
      </div>
    </div>
  </section>

  <section class="atlas-grid">
    <article class="panel">
      <h2>Single Motifs</h2>
      <p class="subtle">
        One motif evolving under internal and vacuum-driven policies.
      </p>
      <div id="single-motifs"></div>
    </article>

    <article class="panel">
      <h2>Coupled Motif Pairs</h2>
      <p class="subtle">
        Two motifs exchanging deterministic cross-messages can produce longer cycles.
      </p>
      <div id="coupled-hist" class="hist-wrap"></div>
      <div id="coupled-pairs"></div>
    </article>

    <article class="panel">
      <h2>Furey Left-Ideal Motifs (XOR)</h2>
      <p class="subtle">
        Minimal left-ideal particle motifs from the Furey ladder construction,
        simulated with XOR-index octonion multiplication.
      </p>
      <div id="furey-ideals"></div>
    </article>
  </section>
</div>

<style>
  :root {
    --atlas-bg-a: #f4efe3;
    --atlas-bg-b: #deeff6;
    --atlas-ink: #13262f;
    --atlas-muted: #50646f;
    --atlas-card: rgba(255, 255, 255, 0.8);
    --atlas-border: rgba(19, 38, 47, 0.16);
    --atlas-accent: #005f89;
    --atlas-hot: #b24a1f;
    --atlas-cold: #2a6e45;
  }

  .atlas-shell {
    font-family: "Space Grotesk", "IBM Plex Sans", "Segoe UI", sans-serif;
    color: var(--atlas-ink);
    border: 1px solid var(--atlas-border);
    border-radius: 20px;
    padding: 1rem;
    background:
      radial-gradient(circle at 8% 15%, #f8d7b4 0, transparent 30%),
      radial-gradient(circle at 92% 16%, #cde8fb 0, transparent 34%),
      linear-gradient(145deg, var(--atlas-bg-a), var(--atlas-bg-b));
  }

  .atlas-kicker {
    display: inline-block;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 800;
    background: rgba(0, 95, 137, 0.14);
    color: #0a4b6a;
    border-radius: 999px;
    padding: 0.22rem 0.55rem;
  }

  .atlas-hero h1 {
    margin: 0.2rem 0 0.3rem;
    line-height: 1.05;
    font-size: clamp(1.7rem, 4vw, 2.6rem);
  }

  .atlas-metrics {
    margin-top: 0.8rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.55rem;
  }

  .metric {
    background: var(--atlas-card);
    border: 1px solid var(--atlas-border);
    border-radius: 12px;
    padding: 0.6rem 0.75rem;
  }

  .metric strong {
    display: block;
    font-size: 1.12rem;
  }

  .atlas-controls {
    margin-top: 0.9rem;
    display: grid;
    gap: 0.6rem;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }

  .control-card {
    background: var(--atlas-card);
    border: 1px solid var(--atlas-border);
    border-radius: 12px;
    padding: 0.6rem 0.75rem;
  }

  .control-card label {
    display: block;
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 0.42rem;
    color: var(--atlas-muted);
  }

  .row { margin-bottom: 0.45rem; }
  .row:last-child { margin-bottom: 0; }

  .mode-toggle {
    display: flex;
    gap: 0.35rem;
    flex-wrap: wrap;
  }

  .mode-toggle button {
    border: 1px solid var(--atlas-border);
    border-radius: 999px;
    background: #fff;
    color: var(--atlas-ink);
    font-weight: 700;
    padding: 0.32rem 0.65rem;
    cursor: pointer;
  }

  .mode-toggle button.is-active {
    background: var(--atlas-ink);
    color: #fff;
  }

  select {
    width: 100%;
    border-radius: 8px;
    border: 1px solid var(--atlas-border);
    background: #fff;
    color: var(--atlas-ink);
    padding: 0.38rem 0.5rem;
  }

  .inline-check {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    text-transform: none;
    letter-spacing: 0;
    font-size: 0.93rem;
    color: var(--atlas-ink);
  }

  .atlas-grid {
    margin-top: 0.9rem;
    display: grid;
    gap: 0.8rem;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  }

  .panel {
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid var(--atlas-border);
    border-radius: 14px;
    padding: 0.75rem;
  }

  .subtle {
    margin-top: 0;
    color: var(--atlas-muted);
    font-size: 0.92rem;
  }

  .motif-card, .pair-card {
    background: #fff;
    border: 1px solid var(--atlas-border);
    border-left: 6px solid var(--atlas-cold);
    border-radius: 10px;
    padding: 0.58rem 0.65rem;
    margin-bottom: 0.52rem;
  }

  .pair-card.hot { border-left-color: var(--atlas-hot); }

  .card-head {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 0.4rem;
    align-items: baseline;
  }

  .chip {
    border: 1px solid var(--atlas-border);
    border-radius: 999px;
    padding: 0.12rem 0.45rem;
    font-size: 0.75rem;
    background: rgba(0, 95, 137, 0.08);
  }

  .chip.hot {
    background: rgba(178, 74, 31, 0.13);
    border-color: rgba(178, 74, 31, 0.28);
  }

  .period {
    font-weight: 800;
  }

  .trace {
    margin-top: 0.35rem;
    border: 1px solid var(--atlas-border);
    border-radius: 8px;
    padding: 0.34rem 0.45rem;
    background: #f9fbfc;
    font-family: "IBM Plex Mono", "Consolas", monospace;
    font-size: 0.76rem;
    overflow-x: auto;
    white-space: pre;
  }

  .hist-wrap {
    margin-bottom: 0.6rem;
  }

  .hist-row {
    display: grid;
    grid-template-columns: 44px 1fr 36px;
    gap: 0.4rem;
    align-items: center;
    margin-bottom: 0.25rem;
  }

  .bar {
    height: 0.68rem;
    background: #e6eef2;
    border-radius: 999px;
    overflow: hidden;
    border: 1px solid var(--atlas-border);
  }

  .bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #2f7ea7, #65b6da);
  }

  .empty {
    border: 1px dashed var(--atlas-border);
    border-radius: 10px;
    padding: 0.75rem;
    color: var(--atlas-muted);
    background: rgba(255, 255, 255, 0.55);
  }

  @media (max-width: 640px) {
    .atlas-shell {
      padding: 0.8rem;
      border-radius: 14px;
    }
  }
</style>

<script>
(() => {
  const state = {
    mode: "layman",
    minPeriod: 2,
    gt4Only: true,
    single: null,
    coupled: null,
    furey: null,
  };

  const singleSources = [
    "../data/xor_particle_motif_cycles.json",
    "./data/xor_particle_motif_cycles.json",
    "/web/data/xor_particle_motif_cycles.json",
    "/website/data/xor_particle_motif_cycles.json",
    "website/data/xor_particle_motif_cycles.json"
  ];

  const coupledSources = [
    "../data/xor_coupled_motif_cycles.json",
    "./data/xor_coupled_motif_cycles.json",
    "/web/data/xor_coupled_motif_cycles.json",
    "/website/data/xor_coupled_motif_cycles.json",
    "website/data/xor_coupled_motif_cycles.json"
  ];

  const fureySources = [
    "../data/xor_furey_ideal_cycles.json",
    "./data/xor_furey_ideal_cycles.json",
    "/web/data/xor_furey_ideal_cycles.json",
    "/website/data/xor_furey_ideal_cycles.json",
    "website/data/xor_furey_ideal_cycles.json"
  ];

  async function fetchJson(paths) {
    for (const path of paths) {
      try {
        const res = await fetch(path, { cache: "no-store" });
        if (res.ok) return await res.json();
      } catch (err) {
        // try next path
      }
    }
    return null;
  }

  function relTime(ts) {
    const d = new Date(ts);
    if (Number.isNaN(d.getTime())) return "unknown";
    const sec = Math.max(0, Math.floor((Date.now() - d.getTime()) / 1000));
    if (sec >= 86400) return `${Math.floor(sec / 86400)}d ago`;
    if (sec >= 3600) return `${Math.floor(sec / 3600)}h ago`;
    if (sec >= 60) return `${Math.floor(sec / 60)}m ago`;
    return `${sec}s ago`;
  }

  function formatVector(vec) {
    const parts = [];
    for (let i = 0; i < vec.length; i += 1) {
      const c = vec[i];
      if (c !== 0) parts.push(`${c > 0 ? "+" : ""}${c}e${i}`);
    }
    return parts.length ? parts.join(" ") : "0";
  }

  function renderMetrics() {
    const root = document.getElementById("atlas-metrics");
    if (!state.single || !state.coupled) {
      root.innerHTML = `<div class="empty">Cycle data is not available yet.</div>`;
      return;
    }
    const motifs = state.single.motifs || [];
    const stableUnique = new Set(
      motifs
        .filter((m) => m.is_stable_candidate)
        .map((m) => JSON.stringify(m.triad_support_sorted || []))
    ).size;
    const pairCount = state.coupled.pair_count || 0;
    const gt4 = (state.coupled.pairs || []).filter((p) => Number(p.period || 0) > 4).length;
    const fureyCount = state.furey?.motif_count || 0;
    const fureyStable = state.furey?.stable_period4_count || 0;

    root.innerHTML = `
      <div class="metric"><small>Single Motifs Tracked</small><strong>${motifs.length}</strong></div>
      <div class="metric"><small>Stable Supports</small><strong>${stableUnique}</strong></div>
      <div class="metric"><small>Coupled Pairs</small><strong>${pairCount}</strong></div>
      <div class="metric"><small>Pairs With Period > 4</small><strong>${gt4}</strong></div>
      <div class="metric"><small>Furey Ideal Motifs</small><strong>${fureyCount}</strong></div>
      <div class="metric"><small>Furey Stable (P4)</small><strong>${fureyStable}</strong></div>
      <div class="metric"><small>Data Refreshed</small><strong>${relTime(state.coupled.generated_at_utc)}</strong></div>
    `;
  }

  function modeIsPhysicist() {
    return state.mode === "physicist";
  }

  function renderSingleMotifs() {
    const mount = document.getElementById("single-motifs");
    if (!state.single || !Array.isArray(state.single.motifs)) {
      mount.innerHTML = `<div class="empty">Single motif data unavailable.</div>`;
      return;
    }

    const motifs = [...state.single.motifs].sort((a, b) => {
      const aStable = a.is_stable_candidate ? 1 : 0;
      const bStable = b.is_stable_candidate ? 1 : 0;
      if (aStable !== bStable) return bStable - aStable;
      return String(a.motif_id).localeCompare(String(b.motif_id));
    });

    mount.innerHTML = motifs.map((m) => {
      const pInt = m.policies?.internal_oriented_alternating || {};
      const pVac = m.policies?.vacuum_left_e7 || {};
      const tags = (m.tags || []).map((t) => `<span class="chip">${t}</span>`).join(" ");
      const closure = pInt.support_closure_within_motif_plus_e0 ? "closed" : "open";
      const trace = (pInt.trace || []).slice(0, 8).map((row) =>
        `t=${row.step}: ${formatVector(row.vector || [])}`
      ).join("\n");

      let phys = "";
      if (modeIsPhysicist()) {
        const rows = Object.entries(m.policies || {}).map(([k, v]) =>
          `<tr><td><code>${k}</code></td><td>${v.period ?? "n/a"}</td><td>${v.support_closure_within_motif_plus_e0 ? "yes" : "no"}</td></tr>`
        ).join("");
        phys = `
          <details>
            <summary>Policy table + trace sample</summary>
            <table>
              <thead><tr><th>Policy</th><th>Period</th><th>Support closure</th></tr></thead>
              <tbody>${rows}</tbody>
            </table>
            <div class="trace">${trace}</div>
          </details>
        `;
      } else {
        phys = `
          <div class="subtle">
            Internal period: <strong>${pInt.period ?? "n/a"}</strong>,
            vacuum-driven period: <strong>${pVac.period ?? "n/a"}</strong>,
            support closure: <strong>${closure}</strong>.
          </div>
        `;
      }

      return `
        <article class="motif-card">
          <div class="card-head">
            <strong>${m.motif_id}</strong>
            <span class="chip">${m.is_stable_candidate ? "stable candidate" : "contrast motif"}</span>
          </div>
          <div class="subtle">support triad: [${(m.triad_support_sorted || []).join(", ")}]</div>
          <div>${tags}</div>
          ${phys}
        </article>
      `;
    }).join("");
  }

  function renderHistogram() {
    const mount = document.getElementById("coupled-hist");
    const hist = state.coupled?.period_histogram || {};
    const keys = Object.keys(hist).filter((k) => k !== "None").map((k) => Number(k)).sort((a, b) => a - b);
    if (!keys.length) {
      mount.innerHTML = `<div class="empty">No coupled period histogram available.</div>`;
      return;
    }
    const maxCount = Math.max(...keys.map((k) => Number(hist[String(k)] || 0)));
    mount.innerHTML = keys.map((k) => {
      const c = Number(hist[String(k)] || 0);
      const w = Math.round((c / maxCount) * 100);
      return `
        <div class="hist-row">
          <div>P=${k}</div>
          <div class="bar"><div class="bar-fill" style="width:${w}%"></div></div>
          <div>${c}</div>
        </div>
      `;
    }).join("");
  }

  function renderCoupledPairs() {
    const mount = document.getElementById("coupled-pairs");
    if (!state.coupled || !Array.isArray(state.coupled.pairs)) {
      mount.innerHTML = `<div class="empty">Coupled motif data unavailable.</div>`;
      return;
    }

    let rows = state.coupled.pairs.filter((p) => {
      const period = Number(p.period || 0);
      if (period < state.minPeriod) return false;
      if (state.gt4Only && period <= 4) return false;
      return true;
    });

    rows = rows.sort((a, b) => Number(b.period || 0) - Number(a.period || 0));

    if (!rows.length) {
      mount.innerHTML = `<div class="empty">No pairs match this filter.</div>`;
      return;
    }

    mount.innerHTML = rows.map((p) => {
      const period = Number(p.period || 0);
      const hot = period > 4;
      const trace = (p.trace || []).slice(0, 10).map((row) =>
        `t=${row.step}: A=${formatVector(row.a_vector || [])} | B=${formatVector(row.b_vector || [])}`
      ).join("\n");

      const laymanLine = hot
        ? `This pair returns to the same pattern every ${period} rounds.`
        : `This pair stays in a fast cycle (period ${period}).`;

      return `
        <article class="pair-card ${hot ? "hot" : ""}">
          <div class="card-head">
            <strong>[${(p.triad_a || []).join(", ")}] x [${(p.triad_b || []).join(", ")}]</strong>
            <span class="chip ${hot ? "hot" : ""} period">period ${period}</span>
          </div>
          <div class="subtle">${laymanLine}</div>
          ${
            modeIsPhysicist()
              ? `<details><summary>Trace sample (first 10 steps)</summary><div class="trace">${trace}</div></details>`
              : ""
          }
        </article>
      `;
    }).join("");
  }

  function renderFureyIdeals() {
    const mount = document.getElementById("furey-ideals");
    if (!state.furey || !Array.isArray(state.furey.motifs)) {
      mount.innerHTML = `<div class="empty">Furey ideal data unavailable.</div>`;
      return;
    }

    const motifs = [...state.furey.motifs].sort((a, b) =>
      String(a.motif_id).localeCompare(String(b.motif_id))
    );

    mount.innerHTML = motifs.map((m) => {
      const supportBits = (m.support_bits || []).join(", ");
      const sparse = m.state_sparse || {};
      const sparseLine = Object.entries(sparse).map(([k, v]) => {
        const re = v.re || 0;
        const im = v.im || 0;
        return `${k}:(${re},${im})`;
      }).join("  ");

      const lay = `
        <div class="subtle">
          family: <strong>${m.family}</strong>,
          support bits: <strong>[${supportBits}]</strong>,
          e7-left period: <strong>${m.period_left_e7 ?? "n/a"}</strong>,
          e7-right period: <strong>${m.period_right_e7 ?? "n/a"}</strong>
        </div>
      `;
      const phys = `
        <details>
          <summary>Sparse Gaussian-integer state</summary>
          <div class="trace">${sparseLine || "0"}</div>
        </details>
      `;

      return `
        <article class="motif-card">
          <div class="card-head">
            <strong>${m.motif_id}</strong>
            <span class="chip">${m.stable_period4 ? "stable period-4" : "non-period-4"}</span>
          </div>
          ${lay}
          ${modeIsPhysicist() ? phys : ""}
        </article>
      `;
    }).join("");
  }

  function renderAll() {
    renderMetrics();
    renderSingleMotifs();
    renderHistogram();
    renderCoupledPairs();
    renderFureyIdeals();
  }

  function wireControls() {
    document.querySelectorAll("#mode-toggle button").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.mode = btn.dataset.mode || "layman";
        document.querySelectorAll("#mode-toggle button").forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
        renderAll();
      });
    });

    document.getElementById("min-period").addEventListener("change", (e) => {
      state.minPeriod = Number(e.target.value || 2);
      renderCoupledPairs();
    });

    document.getElementById("gt4-only").addEventListener("change", (e) => {
      state.gt4Only = Boolean(e.target.checked);
      renderCoupledPairs();
    });
  }

  async function init() {
    const [single, coupled, furey] = await Promise.all([
      fetchJson(singleSources),
      fetchJson(coupledSources),
      fetchJson(fureySources),
    ]);
    state.single = single;
    state.coupled = coupled;
    state.furey = furey;
    renderAll();
    wireControls();
  }

  init();
})();
</script>

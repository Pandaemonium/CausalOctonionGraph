# Proof Ledger

This is the live public ledger of claim upgrades in COG Lab.

Default mode is **Layman**.

Want to contribute runs? See:
- `/web/pages/how_do_i_help`

<div id="proof-ledger-app" class="ledger-shell">
  <section class="ledger-hero">
    <div class="hero-kicker">Live Discovery Feed</div>
    <h1>What Just Got Stronger?</h1>
    <p>
      Track each upgrade with plain-language summaries first, and switch to deeper
      technical detail only when you want it.
    </p>
    <div class="hero-metrics" id="hero-metrics"></div>
  </section>

  <section class="ledger-controls">
    <div class="control-group">
      <label>Complexity</label>
      <div class="toggle-row" id="mode-toggle">
        <button data-mode="layman" class="is-active">Layman</button>
        <button data-mode="student">Student</button>
        <button data-mode="physicist">Physicist</button>
      </div>
    </div>

    <div class="control-group">
      <label>Status</label>
      <select id="status-filter">
        <option value="all">All statuses</option>
        <option value="supported">Proved</option>
        <option value="partial">In Progress</option>
        <option value="active_hypothesis">Hypothesis</option>
        <option value="stub">Queued</option>
        <option value="falsified">Falsified</option>
        <option value="superseded">Superseded</option>
      </select>
    </div>

    <div class="control-group">
      <label>Recency</label>
      <select id="time-filter">
        <option value="all">All time</option>
        <option value="24h">Last 24 hours</option>
        <option value="7d">Last 7 days</option>
        <option value="30d">Last 30 days</option>
      </select>
    </div>

    <div class="control-group">
      <label>Topic</label>
      <select id="topic-filter">
        <option value="all">All topics</option>
      </select>
    </div>
  </section>

  <section class="ledger-feed">
    <h2>Upgrade Timeline</h2>
    <p class="subtle">
      Each row shows relative time first, with exact UTC available on expand.
    </p>
    <div id="events-feed"></div>
  </section>

  <section class="ledger-map">
    <h2>Discovery Map (What Unlocks What)</h2>
    <p class="subtle">
      Foundational claims unlock downstream results. This shows the most connected claims right now.
    </p>
    <div id="unlock-map"></div>
  </section>
</div>

<style>
  :root {
    --bg-a: #f3efe7;
    --bg-b: #e2f0ec;
    --ink: #132025;
    --muted: #4e5a5f;
    --card: rgba(255, 255, 255, 0.78);
    --border: rgba(19, 32, 37, 0.18);
    --proved: #156c41;
    --progress: #005d88;
    --hypothesis: #6a4ca1;
    --queued: #9f7a2f;
    --falsified: #ad2e2e;
    --superseded: #6b6b6b;
  }

  .ledger-shell {
    font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif;
    color: var(--ink);
    padding: 1.25rem;
    background:
      radial-gradient(circle at 15% 15%, #f6dcbc 0, transparent 33%),
      radial-gradient(circle at 85% 20%, #cde7ff 0, transparent 29%),
      linear-gradient(135deg, var(--bg-a), var(--bg-b));
    border-radius: 18px;
    border: 1px solid var(--border);
  }

  .ledger-hero h1 {
    margin: 0.15rem 0 0.25rem;
    font-size: clamp(1.75rem, 4.2vw, 2.7rem);
    line-height: 1.05;
  }

  .hero-kicker {
    display: inline-block;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 700;
    font-size: 0.78rem;
    color: #113f52;
    background: rgba(17, 63, 82, 0.12);
    padding: 0.25rem 0.55rem;
    border-radius: 999px;
  }

  .hero-metrics {
    margin-top: 1rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.55rem;
  }

  .metric {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.65rem 0.8rem;
  }

  .metric strong {
    display: block;
    font-size: 1.2rem;
  }

  .ledger-controls {
    margin-top: 1rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.65rem;
  }

  .control-group {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.6rem 0.75rem;
  }

  .control-group label {
    display: block;
    font-size: 0.79rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.45rem;
    color: var(--muted);
  }

  .control-group select {
    width: 100%;
    border-radius: 8px;
    border: 1px solid var(--border);
    padding: 0.42rem 0.52rem;
    background: #fff;
    color: var(--ink);
    font-size: 0.94rem;
  }

  .toggle-row {
    display: flex;
    gap: 0.4rem;
  }

  .toggle-row button {
    border: 1px solid var(--border);
    background: #fff;
    color: var(--ink);
    border-radius: 999px;
    padding: 0.35rem 0.68rem;
    font-weight: 700;
    cursor: pointer;
    transition: transform 120ms ease, box-shadow 120ms ease;
  }

  .toggle-row button:hover {
    transform: translateY(-1px);
  }

  .toggle-row button.is-active {
    background: #132025;
    color: #fff;
    box-shadow: 0 4px 14px rgba(19, 32, 37, 0.25);
  }

  .ledger-feed {
    margin-top: 1rem;
  }

  .ledger-map {
    margin-top: 1rem;
  }

  #unlock-map {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 0.6rem;
  }

  .unlock-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.66rem 0.78rem;
  }

  .unlock-card strong {
    display: inline-block;
    margin-right: 0.35rem;
  }

  .unlock-card .status {
    font-size: 0.78rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 700;
  }

  .unlock-card .count {
    margin-top: 0.32rem;
    font-size: 0.92rem;
  }

  .subtle {
    color: var(--muted);
    margin-top: 0;
  }

  .event-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 8px solid var(--progress);
    border-radius: 12px;
    padding: 0.72rem 0.86rem;
    margin-bottom: 0.7rem;
  }

  .event-card.supported { border-left-color: var(--proved); }
  .event-card.partial { border-left-color: var(--progress); }
  .event-card.active_hypothesis { border-left-color: var(--hypothesis); }
  .event-card.stub { border-left-color: var(--queued); }
  .event-card.falsified { border-left-color: var(--falsified); }
  .event-card.superseded { border-left-color: var(--superseded); }

  .event-head {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    align-items: baseline;
    flex-wrap: wrap;
  }

  .event-status {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 800;
    color: var(--muted);
  }

  .event-time {
    font-size: 0.83rem;
    color: var(--muted);
  }

  .event-headline {
    margin: 0.32rem 0 0.24rem;
    font-size: 1.05rem;
    font-weight: 800;
  }

  .event-why {
    margin: 0 0 0.42rem;
  }

  .event-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.28rem;
    margin-bottom: 0.4rem;
  }

  .chip {
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 0.18rem 0.5rem;
    font-size: 0.77rem;
    background: #fff;
    color: #2c383e;
  }

  details {
    background: rgba(255, 255, 255, 0.68);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.4rem 0.55rem;
  }

  details > summary {
    cursor: pointer;
    font-weight: 700;
  }

  .empty {
    border: 1px dashed var(--border);
    border-radius: 12px;
    padding: 1rem;
    color: var(--muted);
    background: rgba(255, 255, 255, 0.6);
  }
</style>

<script>
(() => {
  const MODES = ["layman", "student", "physicist"];
  const state = {
    mode: "layman",
    status: "all",
    time: "all",
    topic: "all",
    events: [],
    claims: [],
    tree: null,
  };

  const eventsSources = [
    "../data/claim_events.json",
    "./data/claim_events.json",
    "/web/data/claim_events.json",
    "/website/data/claim_events.json",
    "website/data/claim_events.json"
  ];

  const claimsSources = [
    "../data/claims_index.json",
    "./data/claims_index.json",
    "/web/data/claims_index.json",
    "/website/data/claims_index.json",
    "website/data/claims_index.json"
  ];

  const treeSources = [
    "../data/tech_tree.json",
    "./data/tech_tree.json",
    "/web/data/tech_tree.json",
    "/website/data/tech_tree.json",
    "website/data/tech_tree.json"
  ];

  async function fetchJson(paths) {
    for (const path of paths) {
      try {
        const res = await fetch(path, { cache: "no-store" });
        if (res.ok) return await res.json();
      } catch (err) {
        // Try next source path.
      }
    }
    return null;
  }

  function parseUtc(ts) {
    const d = new Date(ts);
    return Number.isNaN(d.getTime()) ? null : d;
  }

  function relTime(ts) {
    const d = parseUtc(ts);
    if (!d) return "unknown";
    const diffMs = Date.now() - d.getTime();
    const absSec = Math.max(0, Math.floor(diffMs / 1000));
    const units = [
      { n: 86400, name: "day" },
      { n: 3600, name: "hour" },
      { n: 60, name: "minute" },
      { n: 1, name: "second" }
    ];
    for (const unit of units) {
      const v = Math.floor(absSec / unit.n);
      if (v >= 1) return `${v} ${unit.name}${v > 1 ? "s" : ""} ago`;
    }
    return "just now";
  }

  function statusDisplay(status) {
    const map = {
      supported: "Proved",
      partial: "In Progress",
      active_hypothesis: "Hypothesis",
      stub: "Queued",
      falsified: "Falsified",
      superseded: "Superseded"
    };
    return map[status] || status;
  }

  function statusCount(status) {
    return state.claims.filter((c) => c.status === status).length;
  }

  function withinTimeFilter(eventUtc, filterValue) {
    if (filterValue === "all") return true;
    const d = parseUtc(eventUtc);
    if (!d) return false;
    const ageMs = Date.now() - d.getTime();
    const limits = { "24h": 24 * 3600e3, "7d": 7 * 24 * 3600e3, "30d": 30 * 24 * 3600e3 };
    return ageMs <= (limits[filterValue] || Number.MAX_SAFE_INTEGER);
  }

  function filteredEvents() {
    return state.events.filter((e) => {
      if (state.status !== "all" && e.to_status !== state.status) return false;
      if (!withinTimeFilter(e.promoted_at_utc, state.time)) return false;
      if (state.topic !== "all") {
        const topics = Array.isArray(e.topics) ? e.topics : [];
        if (!topics.includes(state.topic)) return false;
      }
      return true;
    });
  }

  function renderMetrics() {
    const el = document.getElementById("hero-metrics");
    const latest = state.events[0];
    const latestText = latest ? relTime(latest.promoted_at_utc) : "n/a";
    el.innerHTML = `
      <div class="metric"><small>Proved</small><strong>${statusCount("supported")}</strong></div>
      <div class="metric"><small>In Progress</small><strong>${statusCount("partial")}</strong></div>
      <div class="metric"><small>Hypotheses</small><strong>${statusCount("active_hypothesis")}</strong></div>
      <div class="metric"><small>Latest Upgrade</small><strong>${latestText}</strong></div>
    `;
  }

  function renderTopics() {
    const select = document.getElementById("topic-filter");
    const topics = new Set();
    for (const e of state.events) {
      const tagList = Array.isArray(e.topics) ? e.topics : [];
      for (const t of tagList) topics.add(t);
    }
    const opts = [`<option value="all">All topics</option>`];
    Array.from(topics).sort().forEach((t) => opts.push(`<option value="${t}">${t}</option>`));
    select.innerHTML = opts.join("");
    select.value = state.topic;
  }

  function renderFeed() {
    const feed = document.getElementById("events-feed");
    const items = filteredEvents();
    if (!items.length) {
      feed.innerHTML = `<div class="empty">No events match this filter set yet.</div>`;
      return;
    }

    feed.innerHTML = items.map((e) => {
      const mode = MODES.includes(state.mode) ? state.mode : "layman";
      const headline = e.headlines?.[mode] || e.headlines?.layman || "Untitled upgrade";
      const why = e.significance_summaries?.[mode] || "";
      const topics = (Array.isArray(e.topics) ? e.topics : []).map((t) => `<span class="chip">${t}</span>`).join("");
      const notClaimed = Array.isArray(e.not_claimed) ? e.not_claimed.map((line) => `<li>${line}</li>`).join("") : "";
      const claimFile = e.evidence?.claim_file || "";
      const ownerRfc = e.evidence?.owner_rfc || "";

      const transitionLabel = `${statusDisplay(e.from_status)} -> ${statusDisplay(e.to_status)}`;
      const trustBlock = mode === "physicist"
        ? `
            <ul>
              <li><strong>Transition:</strong> ${transitionLabel}</li>
              <li><strong>Claim file:</strong> <code>${claimFile}</code></li>
              <li><strong>Owner RFC:</strong> <code>${ownerRfc}</code></li>
              <li><strong>Verified by:</strong> ${e.verified_by || "unknown"} (${e.verification_run_id || "no run id"})</li>
            </ul>
          `
        : `
            <ul>
              <li><strong>Transition:</strong> ${transitionLabel}</li>
              <li><strong>Checked by:</strong> ${e.verified_by || "lab clerk"}</li>
              <li><strong>Validation run:</strong> ${e.verification_run_id || "recorded"}</li>
            </ul>
            <p class="subtle">Switch to <strong>Physicist</strong> mode to view technical evidence paths.</p>
          `;

      return `
        <article class="event-card ${e.to_status}">
          <div class="event-head">
            <span class="event-status">${statusDisplay(e.to_status)} | ${e.claim_id}</span>
            <span class="event-time">${relTime(e.promoted_at_utc)} (${e.promoted_at_utc})</span>
          </div>
          <h3 class="event-headline">${headline}</h3>
          <p class="event-why">${why}</p>
          <div class="event-meta">${topics}</div>
          <details>
            <summary>Why trust this upgrade?</summary>
            ${trustBlock}
            <p><strong>Not claimed:</strong></p>
            <ul>${notClaimed}</ul>
          </details>
        </article>
      `;
    }).join("");
  }

  function renderUnlockMap() {
    const mount = document.getElementById("unlock-map");
    const nodes = state.tree?.nodes || [];
    if (!nodes.length) {
      mount.innerHTML = `<div class="empty">Discovery-map data is not available yet.</div>`;
      return;
    }

    const top = [...nodes]
      .filter((n) => Number(n.unlocks_count || 0) > 0)
      .sort((a, b) => (b.unlocks_count || 0) - (a.unlocks_count || 0))
      .slice(0, 8);

    if (!top.length) {
      mount.innerHTML = `<div class="empty">No unlock relationships have been recorded yet.</div>`;
      return;
    }

    mount.innerHTML = top.map((n) => `
      <article class="unlock-card">
        <div><strong>${n.id}</strong> <span class="status">${statusDisplay(n.status)}</span></div>
        <div class="count">Unlocks ${n.unlocks_count} downstream claim${n.unlocks_count === 1 ? "" : "s"}</div>
      </article>
    `).join("");
  }

  function wireControls() {
    document.querySelectorAll("#mode-toggle button").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.mode = btn.dataset.mode || "layman";
        document.querySelectorAll("#mode-toggle button").forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
        renderFeed();
      });
    });

    document.getElementById("status-filter").addEventListener("change", (e) => {
      state.status = e.target.value;
      renderFeed();
    });
    document.getElementById("time-filter").addEventListener("change", (e) => {
      state.time = e.target.value;
      renderFeed();
    });
    document.getElementById("topic-filter").addEventListener("change", (e) => {
      state.topic = e.target.value;
      renderFeed();
    });
  }

  async function init() {
    const [eventsDoc, claimsDoc, treeDoc] = await Promise.all([
      fetchJson(eventsSources),
      fetchJson(claimsSources),
      fetchJson(treeSources),
    ]);

    state.events = eventsDoc?.events || [];
    state.claims = claimsDoc?.claims || [];
    state.tree = treeDoc || null;
    renderMetrics();
    renderTopics();
    renderFeed();
    renderUnlockMap();
    wireControls();
  }

  init();
})();
</script>

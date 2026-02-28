"""
Interactive visualizer for deterministic CxO lightcone evolution.

Features:
1. Load a microstate JSON (`init_state`) or a saved world JSON (`state`).
2. Show full graph (all nodes + parent edges).
3. Hover any graph node to highlight its past/future lightcone.
4. Show hovered-node lightcone metrics across cached tick history.
5. Show each node's full 16-int representation (8 basis slots x [re, im]).
6. Step forward/backward in time with deterministic replay.

Run:
    python world_code/Python_code/lightcone_state_visualizer.py
    python world_code/Python_code/lightcone_state_visualizer.py --input <path>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Set, Tuple

from minimal_world_kernel import GInt, World, step


def _parse_int_coeff(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer literal (no decimal), got {value!r}")
    return value


def _parse_cxo(raw: object) -> tuple[GInt, GInt, GInt, GInt, GInt, GInt, GInt, GInt]:
    if not isinstance(raw, list) or len(raw) != 8:
        raise ValueError("Each node state must be a length-8 list of [re, im] pairs.")
    vals: List[GInt] = []
    for i, pair in enumerate(raw):
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError(f"basis[{i}] must be [re, im].")
        re_part = _parse_int_coeff(pair[0], f"basis[{i}].re")
        im_part = _parse_int_coeff(pair[1], f"basis[{i}].im")
        vals.append(GInt(re_part, im_part))
    return (
        vals[0],
        vals[1],
        vals[2],
        vals[3],
        vals[4],
        vals[5],
        vals[6],
        vals[7],
    )


def load_world_any(path: str) -> World:
    """
    Load either:
    1) input schema with `init_state`, or
    2) saved output schema with `state`.
    """
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    node_ids = [str(x) for x in raw["node_ids"]]
    parents = {str(k): [str(x) for x in v] for k, v in raw["parents"].items()}

    state_key = "init_state" if "init_state" in raw else "state"
    if state_key not in raw:
        raise ValueError("Input JSON must contain either `init_state` or `state`.")

    states = {str(k): _parse_cxo(v) for k, v in raw[state_key].items()}
    missing = [nid for nid in node_ids if nid not in states]
    if missing:
        raise ValueError(f"Missing state entries for node_ids: {missing}")

    tick = int(raw.get("tick", 0))
    return World(node_ids=node_ids, parents=parents, states=states, tick=tick)


def _state_to_16_ints(state: tuple[GInt, GInt, GInt, GInt, GInt, GInt, GInt, GInt]) -> List[int]:
    out: List[int] = []
    for z in state:
        out.append(z.re)
        out.append(z.im)
    return out


def _node_l1(state: tuple[GInt, GInt, GInt, GInt, GInt, GInt, GInt, GInt]) -> int:
    return sum(abs(z.re) + abs(z.im) for z in state)


def _int_to_base8(n: int) -> str:
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    return f"{sign}{oct(abs(n))[2:]}"


def _format_int(n: int, mode: str, compact_keep: int) -> str:
    if mode == "base8":
        return _int_to_base8(n)

    s = str(n)
    if mode == "compact":
        if len(s) <= compact_keep:
            return s
        head = max(3, compact_keep // 2 - 1)
        tail = max(2, compact_keep - head - 2)
        return f"{s[:head]}..{s[-tail:]} ({len(s)}d)"

    return s


def _build_children(node_ids: List[str], parents: Dict[str, List[str]]) -> Dict[str, List[str]]:
    children: Dict[str, List[str]] = {nid: [] for nid in node_ids}
    for nid in node_ids:
        for p in parents.get(nid, []):
            if p in children:
                children[p].append(nid)
    for nid in children:
        children[nid] = sorted(children[nid])
    return children


def _compute_depths(node_ids: List[str], parents: Dict[str, List[str]]) -> Dict[str, int]:
    memo: Dict[str, int] = {}

    def depth_of(nid: str) -> int:
        if nid in memo:
            return memo[nid]
        ps = [p for p in parents.get(nid, []) if p in node_ids]
        if not ps:
            memo[nid] = 0
            return 0
        d = 1 + max(depth_of(p) for p in ps)
        memo[nid] = d
        return d

    for nid in node_ids:
        depth_of(nid)
    return memo


def _ancestors(node: str, parents: Dict[str, List[str]]) -> Set[str]:
    seen: Set[str] = set()
    stack = list(parents.get(node, []))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(parents.get(cur, []))
    return seen


def _descendants(node: str, children: Dict[str, List[str]]) -> Set[str]:
    seen: Set[str] = set()
    stack = list(children.get(node, []))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(children.get(cur, []))
    return seen


class LightconeVisualizer:
    def __init__(self, root: tk.Tk, initial_path: str | None = None):
        self.root = root
        self.root.title("COG Lightcone State Visualizer")
        self.root.geometry("1850x920")

        self.world_history: List[World] = []
        self.cursor: int = 0
        self.current_path: str | None = None

        self.children_map: Dict[str, List[str]] = {}
        self.depth_map: Dict[str, int] = {}
        self.node_positions: Dict[str, Tuple[float, float]] = {}
        self.hover_node: str | None = None
        self.past_cone: Set[str] = set()
        self.future_cone: Set[str] = set()

        self.status_var = tk.StringVar(value="Load a world JSON to begin.")
        self.tick_var = tk.StringVar(value="Tick: -")
        self.advance_var = tk.StringVar(value="1")
        self.file_var = tk.StringVar(value="File: (none)")
        self.display_mode_var = tk.StringVar(value="decimal")
        self.compact_keep_var = tk.StringVar(value="18")
        self.hover_var = tk.StringVar(value="Hover node: (none)")
        self.cone_nodes_var = tk.StringVar(value="Past/Future cone nodes: -")

        self._build_ui()

        if initial_path is not None:
            self.load_path(initial_path)

    def _build_ui(self) -> None:
        controls = ttk.Frame(self.root, padding=8)
        controls.pack(fill=tk.X)

        ttk.Button(controls, text="Load JSON", command=self.load_dialog).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Reset To Start", command=self.reset_to_start).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Prev Tick", command=self.prev_tick).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Next Tick", command=self.next_tick).pack(side=tk.LEFT, padx=4)

        ttk.Label(controls, text="Advance N:").pack(side=tk.LEFT, padx=(12, 4))
        ttk.Entry(controls, textvariable=self.advance_var, width=6).pack(side=tk.LEFT)
        ttk.Button(controls, text="Advance", command=self.advance_n).pack(side=tk.LEFT, padx=4)

        ttk.Label(controls, text="Display:").pack(side=tk.LEFT, padx=(12, 4))
        mode_combo = ttk.Combobox(
            controls,
            textvariable=self.display_mode_var,
            values=("decimal", "compact", "base8"),
            width=10,
            state="readonly",
        )
        mode_combo.pack(side=tk.LEFT)
        mode_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh_table())

        ttk.Label(controls, text="Compact chars:").pack(side=tk.LEFT, padx=(8, 4))
        compact_entry = ttk.Entry(controls, textvariable=self.compact_keep_var, width=5)
        compact_entry.pack(side=tk.LEFT)
        compact_entry.bind("<Return>", lambda _e: self.refresh_table())

        ttk.Label(controls, textvariable=self.tick_var).pack(side=tk.LEFT, padx=(20, 8))

        header = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        header.pack(fill=tk.X)
        ttk.Label(header, textvariable=self.file_var).pack(anchor=tk.W)
        ttk.Label(header, textvariable=self.hover_var).pack(anchor=tk.W)
        ttk.Label(header, textvariable=self.cone_nodes_var).pack(anchor=tk.W)

        main = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        left = ttk.Frame(main)
        right = ttk.Frame(main)
        main.add(left, weight=2)
        main.add(right, weight=3)

        # Left: graph + hover history
        graph_box = ttk.Labelframe(left, text="Full Graph (hover a node)", padding=6)
        graph_box.pack(fill=tk.BOTH, expand=True)
        self.graph_canvas = tk.Canvas(graph_box, bg="#111827", highlightthickness=0)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        self.graph_canvas.bind("<Motion>", self.on_canvas_motion)
        self.graph_canvas.bind("<Leave>", lambda _e: self.set_hover_node(None))
        self.graph_canvas.bind("<Configure>", lambda _e: self.draw_graph())

        hist_box = ttk.Labelframe(left, text="Lightcone In History", padding=6)
        hist_box.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        h_cols = ["tick", "self_l1", "past_l1", "future_l1", "past_nodes", "future_nodes"]
        self.history_tree = ttk.Treeview(hist_box, columns=h_cols, show="headings", height=10)
        for c in h_cols:
            self.history_tree.heading(c, text=c)
            self.history_tree.column(c, width=90, anchor=tk.CENTER, stretch=True)
        self.history_tree.tag_configure("current_tick", background="#ecfccb")
        self.history_tree.pack(fill=tk.BOTH, expand=True)

        # Right: full 16-int table
        table_box = ttk.Labelframe(right, text="Node States (Full 16-int)", padding=6)
        table_box.pack(fill=tk.BOTH, expand=True)

        self.columns = ["node_id"] + [f"e{i}_{part}" for i in range(8) for part in ("re", "im")]
        self.tree = ttk.Treeview(table_box, columns=self.columns, show="headings", height=26)
        for col in self.columns:
            self.tree.heading(col, text=col)
            width = 120 if col == "node_id" else 76
            self.tree.column(col, width=width, anchor=tk.CENTER, stretch=False)

        self.tree.tag_configure("hover", background="#fde68a")
        self.tree.tag_configure("past", background="#dbeafe")
        self.tree.tag_configure("future", background="#fee2e2")
        self.tree.tag_configure("both", background="#ede9fe")

        xscroll = ttk.Scrollbar(table_box, orient=tk.HORIZONTAL, command=self.tree.xview)
        yscroll = ttk.Scrollbar(table_box, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        table_box.rowconfigure(0, weight=1)
        table_box.columnconfigure(0, weight=1)

        status = ttk.Frame(self.root, padding=8)
        status.pack(fill=tk.X)
        ttk.Label(status, textvariable=self.status_var).pack(anchor=tk.W)

    def set_status(self, msg: str) -> None:
        self.status_var.set(msg)

    def load_dialog(self) -> None:
        initial_dir = str(Path("world_code/Python_code/lightcone_microstate_examples").resolve())
        path = filedialog.askopenfilename(
            title="Select lightcone JSON",
            initialdir=initial_dir if Path(initial_dir).exists() else None,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            self.load_path(path)

    def load_path(self, path: str) -> None:
        try:
            world0 = load_world_any(path)
        except Exception as exc:
            messagebox.showerror("Load error", f"Failed to load world JSON:\n{exc}")
            self.set_status(f"Load failed: {exc}")
            return

        self.world_history = [world0]
        self.cursor = 0
        self.current_path = path
        self.file_var.set(f"File: {path}")

        self.children_map = _build_children(world0.node_ids, world0.parents)
        self.depth_map = _compute_depths(world0.node_ids, world0.parents)
        self.hover_node = None
        self.past_cone = set()
        self.future_cone = set()
        self.hover_var.set("Hover node: (none)")
        self.cone_nodes_var.set("Past/Future cone nodes: -")

        self.draw_graph()
        self.refresh_table()
        self.refresh_history_panel()
        self.set_status(
            f"Loaded {len(world0.node_ids)} nodes at tick {world0.tick}. "
            f"Hover a graph node to highlight its lightcone."
        )

    def _current_world(self) -> World | None:
        if not self.world_history:
            return None
        return self.world_history[self.cursor]

    def _layout_positions(self, width: int, height: int) -> Dict[str, Tuple[float, float]]:
        world = self._current_world()
        if world is None:
            return {}

        depths = self.depth_map
        by_depth: Dict[int, List[str]] = {}
        for nid in world.node_ids:
            d = depths.get(nid, 0)
            by_depth.setdefault(d, []).append(nid)
        for d in by_depth:
            by_depth[d] = sorted(by_depth[d])

        max_depth = max(by_depth.keys(), default=0)
        y_pad = 40
        x_pad = 40
        usable_w = max(200, width - 2 * x_pad)
        usable_h = max(120, height - 2 * y_pad)
        y_step = usable_h / max(1, max_depth)

        pos: Dict[str, Tuple[float, float]] = {}
        for d in sorted(by_depth.keys()):
            row = by_depth[d]
            n = len(row)
            for i, nid in enumerate(row):
                x = x_pad + (i + 1) * usable_w / (n + 1)
                y = y_pad + d * y_step
                pos[nid] = (x, y)
        return pos

    def draw_graph(self) -> None:
        self.graph_canvas.delete("all")
        world = self._current_world()
        if world is None:
            return

        width = max(800, self.graph_canvas.winfo_width())
        height = max(420, self.graph_canvas.winfo_height())
        self.node_positions = self._layout_positions(width, height)

        # Edges first
        for child in sorted(world.node_ids):
            cxy = self.node_positions.get(child)
            if cxy is None:
                continue
            cx, cy = cxy
            for p in world.parents.get(child, []):
                pxy = self.node_positions.get(p)
                if pxy is None:
                    continue
                px, py = pxy
                color = "#4b5563"
                if self.hover_node is not None:
                    if (p in self.past_cone and child in self.past_cone) or (
                        p in self.future_cone and child in self.future_cone
                    ):
                        color = "#f59e0b"
                self.graph_canvas.create_line(px, py + 14, cx, cy - 14, fill=color, width=2)

        # Nodes
        r = 14
        for nid in sorted(world.node_ids):
            x, y = self.node_positions[nid]
            fill = "#94a3b8"
            outline = "#0f172a"
            if self.hover_node == nid:
                fill = "#fde68a"
                outline = "#a16207"
            elif nid in self.past_cone and nid in self.future_cone:
                fill = "#c4b5fd"
                outline = "#5b21b6"
            elif nid in self.past_cone:
                fill = "#93c5fd"
                outline = "#1d4ed8"
            elif nid in self.future_cone:
                fill = "#fca5a5"
                outline = "#b91c1c"

            self.graph_canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=outline, width=2, tags=(f"node::{nid}", "node"))
            self.graph_canvas.create_text(x, y - 24, text=nid, fill="#e5e7eb", font=("Segoe UI", 9), tags=(f"node::{nid}", "node"))

    def on_canvas_motion(self, _event: tk.Event) -> None:
        current = self.graph_canvas.find_withtag("current")
        nid: str | None = None
        if current:
            tags = self.graph_canvas.gettags(current[0])
            for t in tags:
                if t.startswith("node::"):
                    nid = t.split("::", 1)[1]
                    break
        self.set_hover_node(nid)

    def set_hover_node(self, nid: str | None) -> None:
        if nid == self.hover_node:
            return
        self.hover_node = nid
        world = self._current_world()
        if world is None or nid is None:
            self.past_cone = set()
            self.future_cone = set()
            self.hover_var.set("Hover node: (none)")
            self.cone_nodes_var.set("Past/Future cone nodes: -")
        else:
            self.past_cone = _ancestors(nid, world.parents) | {nid}
            self.future_cone = _descendants(nid, self.children_map) | {nid}
            past = ",".join(sorted(self.past_cone))
            fut = ",".join(sorted(self.future_cone))
            self.hover_var.set(f"Hover node: {nid}")
            self.cone_nodes_var.set(f"Past({len(self.past_cone)}): {past} | Future({len(self.future_cone)}): {fut}")

        self.draw_graph()
        self.refresh_table()
        self.refresh_history_panel()

    def refresh_history_panel(self) -> None:
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        if not self.world_history or self.hover_node is None:
            return

        for idx, world in enumerate(self.world_history):
            if self.hover_node not in world.states:
                continue
            self_l1 = _node_l1(world.states[self.hover_node])
            past_l1 = sum(_node_l1(world.states[n]) for n in self.past_cone if n in world.states)
            future_l1 = sum(_node_l1(world.states[n]) for n in self.future_cone if n in world.states)
            tags: Tuple[str, ...] = ("current_tick",) if idx == self.cursor else ()
            self.history_tree.insert(
                "",
                tk.END,
                values=(world.tick, self_l1, past_l1, future_l1, len(self.past_cone), len(self.future_cone)),
                tags=tags,
            )

    def refresh_table(self) -> None:
        world = self._current_world()
        if world is None:
            self.tick_var.set("Tick: -")
            return

        mode = self.display_mode_var.get().strip().lower()
        if mode not in {"decimal", "compact", "base8"}:
            mode = "decimal"
        try:
            compact_keep = int(self.compact_keep_var.get())
        except ValueError:
            compact_keep = 18
        compact_keep = max(6, compact_keep)

        self.tick_var.set(f"Tick: {world.tick} (history index {self.cursor + 1}/{len(self.world_history)})")

        for item in self.tree.get_children():
            self.tree.delete(item)

        max_digits = 1
        for nid in sorted(world.node_ids):
            state = world.states[nid]
            ints16 = _state_to_16_ints(state)
            for v in ints16:
                max_digits = max(max_digits, len(str(abs(v))))

            tags: Tuple[str, ...] = ()
            if self.hover_node is not None:
                if nid == self.hover_node:
                    tags = ("hover",)
                elif nid in self.past_cone and nid in self.future_cone:
                    tags = ("both",)
                elif nid in self.past_cone:
                    tags = ("past",)
                elif nid in self.future_cone:
                    tags = ("future",)

            row = [nid] + [_format_int(v, mode=mode, compact_keep=compact_keep) for v in ints16]
            self.tree.insert("", tk.END, values=row, tags=tags)

        self.set_status(
            f"Rendered {len(world.node_ids)} nodes at tick {world.tick}. "
            f"display={mode}, max_digits={max_digits}"
        )

    def reset_to_start(self) -> None:
        if not self.world_history:
            self.set_status("No world loaded.")
            return
        self.cursor = 0
        self.refresh_table()
        self.refresh_history_panel()
        self.set_status("Reset to initial loaded state.")

    def prev_tick(self) -> None:
        if not self.world_history:
            self.set_status("No world loaded.")
            return
        if self.cursor == 0:
            self.set_status("Already at earliest cached tick.")
            return
        self.cursor -= 1
        self.refresh_table()
        self.refresh_history_panel()
        self.set_status("Moved back by one cached tick.")

    def _ensure_history_index(self, idx: int) -> None:
        while len(self.world_history) <= idx:
            self.world_history.append(step(self.world_history[-1]))

    def next_tick(self) -> None:
        if not self.world_history:
            self.set_status("No world loaded.")
            return
        target = self.cursor + 1
        self._ensure_history_index(target)
        self.cursor = target
        self.refresh_table()
        self.refresh_history_panel()
        self.set_status("Advanced by one deterministic tick.")

    def advance_n(self) -> None:
        if not self.world_history:
            self.set_status("No world loaded.")
            return
        try:
            n = int(self.advance_var.get())
        except ValueError:
            self.set_status("Advance N must be an integer.")
            return
        if n <= 0:
            self.set_status("Advance N must be >= 1.")
            return
        target = self.cursor + n
        self._ensure_history_index(target)
        self.cursor = target
        self.refresh_table()
        self.refresh_history_panel()
        self.set_status(f"Advanced by {n} deterministic ticks.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive lightcone state visualizer.")
    parser.add_argument("--input", default=None, help="Optional path to input JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = tk.Tk()
    app = LightconeVisualizer(root, initial_path=args.input)
    root.mainloop()
    _ = app


if __name__ == "__main__":
    main()


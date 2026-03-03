"""Goal-aligned autonomous launcher + status broadcaster for Mark.

This loop is designed to run continuously in the background and:
1) keep a core set of goal-aligned jobs running (no duplicate launches),
2) emit periodic status notes to `cog_v3/collab/messages_Codex_to_Mark`,
3) persist launcher state for resumability.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
MESSAGES_DIR = ROOT / "cog_v3" / "collab" / "messages_Codex_to_Mark"
STATE_JSON = ROOT / "cog_v3" / "sources" / "v3_mark_autopilot_state_v1.json"
STDOUT_LOG = ROOT / "cog_v3" / "sources" / "v3_mark_autopilot_stdout.log"
STDERR_LOG = ROOT / "cog_v3" / "sources" / "v3_mark_autopilot_stderr.log"


@dataclass(frozen=True)
class Task:
    task_id: str
    module: str
    args: List[str]
    priority: int
    max_parallel: int = 1


TASKS: List[Task] = [
    Task(
        task_id="kernel_phase_boundary_ext",
        module="cog_v3.calc.build_v3_phase_boundary_kernel_sweep_v1",
        args=[
            "--global-seed", "1337",
            "--seed-count", "12",
            "--ticks", "160",
            "--warmup-ticks", "24",
            "--size-x", "27",
            "--size-y", "11",
            "--size-z", "11",
            "--stencil-id", "cube26",
            "--boundary-mode", "fixed_vacuum",
            "--channel-policy-id", "uniform_all",
            "--w3-values", "4,8,12,16,24,32",
            "--p-mem-values", "0,0.125,0.25,0.375,0.5,0.625,0.75,0.875,1.0",
        ],
        priority=1,
    ),
    Task(
        task_id="kernel_gate_stack_seed_sweep_ext",
        module="cog_v3.calc.build_v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1",
        args=["--backend", "numba_cpu", "--seed-count", "256", "--global-seed", "1337"],
        priority=2,
    ),
    Task(
        task_id="generation_equivalence_full",
        module="cog_v3.calc.build_v3_generation_aligned_equivalence_panel_v1",
        args=["--global-seed", "1337"],
        priority=3,
    ),
    Task(
        task_id="stable_motif_scan_cube26_long",
        module="cog_v3.calc.build_v3_stable_motif_scan_v1",
        args=[
            "--ticks", "192",
            "--size-x", "39",
            "--size-y", "11",
            "--size-z", "11",
            "--stencil-id", "cube26",
            "--warmup", "32",
            "--boundary", "fixed_vacuum",
            "--thin-output-step", "6",
        ],
        priority=4,
    ),
    Task(
        task_id="s2880_clue_report_refresh",
        module="cog_v3.calc.build_v3_s2880_particle_clue_report_v1",
        args=[],
        priority=5,
    ),
    Task(
        task_id="s2880_clue_hypotheses_refresh",
        module="cog_v3.calc.build_v3_s2880_particle_clue_hypotheses_v1",
        args=[],
        priority=6,
    ),
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _load_state() -> Dict[str, Any]:
    if not STATE_JSON.exists():
        return {
            "schema_version": "v3_mark_autopilot_state_v1",
            "updated_utc": _utc_now(),
            "ticks": 0,
            "launch_counts": {},
            "last_launch_utc": {},
            "last_message_utc": "",
        }
    try:
        return json.loads(STATE_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {
            "schema_version": "v3_mark_autopilot_state_v1",
            "updated_utc": _utc_now(),
            "ticks": 0,
            "launch_counts": {},
            "last_launch_utc": {},
            "last_message_utc": "",
        }


def _save_state(state: Dict[str, Any]) -> None:
    STATE_JSON.parent.mkdir(parents=True, exist_ok=True)
    state["updated_utc"] = _utc_now()
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _python_processes() -> List[Dict[str, Any]]:
    # Use powershell json output for robust parsing.
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        (
            "Get-CimInstance Win32_Process | "
            "Where-Object { $_.Name -eq 'python.exe' } | "
            "Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"
        ),
    ]
    out = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False)
    txt = (out.stdout or "").strip()
    if txt == "":
        return []
    try:
        parsed = json.loads(txt)
    except Exception:
        return []
    if isinstance(parsed, dict):
        parsed = [parsed]
    rows: List[Dict[str, Any]] = []
    for r in parsed:
        rows.append(
            {
                "pid": int(r.get("ProcessId", 0)),
                "command_line": str(r.get("CommandLine", "")),
            }
        )
    return rows


def _active_count_for_module(procs: List[Dict[str, Any]], module: str) -> int:
    needle = f"-m {module}"
    return sum(1 for p in procs if needle in p.get("command_line", ""))


def _launch_task(task: Task) -> None:
    out_log = ROOT / "cog_v3" / "sources" / f"v3_{task.task_id}_stdout.log"
    err_log = ROOT / "cog_v3" / "sources" / f"v3_{task.task_id}_stderr.log"
    out_log.parent.mkdir(parents=True, exist_ok=True)

    with out_log.open("a", encoding="utf-8") as out_f, err_log.open("a", encoding="utf-8") as err_f:
        # Detached subprocess; keep running after parent exits.
        subprocess.Popen(
            ["python", "-m", task.module, *task.args],
            cwd=str(ROOT),
            stdout=out_f,
            stderr=err_f,
            creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS),  # type: ignore[attr-defined]
        )


def _write_message(state: Dict[str, Any], procs: List[Dict[str, Any]], launched: List[str]) -> Path:
    MESSAGES_DIR.mkdir(parents=True, exist_ok=True)
    path = MESSAGES_DIR / f"{_stamp()}_codex_autopilot_tick.md"

    tracked = []
    for t in sorted(TASKS, key=lambda x: x.priority):
        tracked.append(
            {
                "task_id": t.task_id,
                "module": t.module,
                "active_count": _active_count_for_module(procs, t.module),
                "launch_count": int(state.get("launch_counts", {}).get(t.task_id, 0)),
            }
        )

    lines = [
        "# Codex -> Mark: Autopilot Tick",
        "",
        f"Date: {_utc_now()}",
        "",
        "## Goal alignment",
        "",
        "- Following `cog_v3/collab/messages_Mark_to_Codex/Goals.md` priority order.",
        "",
        "## Launched this tick",
        "",
    ]
    if launched:
        for x in launched:
            lines.append(f"- `{x}`")
    else:
        lines.append("- (none; all tracked tasks already active)")

    lines.extend(
        [
            "",
            "## Tracked task status",
            "",
            "| task_id | active_count | launch_count | module |",
            "|---|---:|---:|---|",
        ]
    )
    for r in tracked:
        lines.append(
            f"| `{r['task_id']}` | {r['active_count']} | {r['launch_count']} | `{r['module']}` |"
        )

    lines.extend(
        [
            "",
            "## Runner notes",
            "",
            f"- state_file: `{STATE_JSON.relative_to(ROOT).as_posix()}`",
            f"- stdout_log: `{STDOUT_LOG.relative_to(ROOT).as_posix()}`",
            f"- stderr_log: `{STDERR_LOG.relative_to(ROOT).as_posix()}`",
            "",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_loop(*, sleep_sec: float, message_every_ticks: int, once: bool, no_launch: bool) -> int:
    state = _load_state()
    tick = int(state.get("ticks", 0))

    while True:
        tick += 1
        state["ticks"] = int(tick)
        launched: List[str] = []
        procs = _python_processes()

        for task in sorted(TASKS, key=lambda t: t.priority):
            active = _active_count_for_module(procs, task.module)
            if active < int(task.max_parallel):
                if not no_launch:
                    _launch_task(task)
                    launched.append(task.task_id)
                    state.setdefault("launch_counts", {})
                    state.setdefault("last_launch_utc", {})
                    state["launch_counts"][task.task_id] = int(state["launch_counts"].get(task.task_id, 0)) + 1
                    state["last_launch_utc"][task.task_id] = _utc_now()
                    # refresh process list after launch to avoid immediate duplicate
                    procs = _python_processes()

        wrote_msg = False
        if int(message_every_ticks) <= 1 or (tick % int(message_every_ticks) == 0) or launched:
            msg_path = _write_message(state, procs, launched)
            state["last_message_utc"] = _utc_now()
            wrote_msg = True
        _save_state(state)

        with STDOUT_LOG.open("a", encoding="utf-8") as f:
            f.write(
                f"{_utc_now()} tick={tick} launched={launched} wrote_msg={wrote_msg} "
                f"active_python={len(procs)}\n"
            )

        if once:
            break
        time.sleep(max(1.0, float(sleep_sec)))

    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sleep-sec", type=float, default=300.0, help="Loop sleep duration in seconds.")
    ap.add_argument("--message-every-ticks", type=int, default=1, help="Emit Mark message every N ticks.")
    ap.add_argument("--once", action="store_true", help="Run one tick and exit.")
    ap.add_argument("--no-launch", action="store_true", help="Do not launch tasks, only report.")
    args = ap.parse_args()
    try:
        return run_loop(
            sleep_sec=float(args.sleep_sec),
            message_every_ticks=int(args.message_every_ticks),
            once=bool(args.once),
            no_launch=bool(args.no_launch),
        )
    except Exception as exc:
        STDERR_LOG.parent.mkdir(parents=True, exist_ok=True)
        with STDERR_LOG.open("a", encoding="utf-8") as f:
            f.write(f"{_utc_now()} ERROR {type(exc).__name__}: {exc}\n")
        raise


if __name__ == "__main__":
    raise SystemExit(main())


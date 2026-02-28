"""Compatibility wrapper for parallel Weinberg-angle case generation."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from generate_weinberg_20_cases import RESULTS_ROOT, execute_cases_incremental


def main() -> None:
    parser = argparse.ArgumentParser(description="Parallel runner for 20 Weinberg-angle COG cases.")
    parser.add_argument(
        "--output-dir",
        default=str(RESULTS_ROOT),
        help="Output directory for JSON/CSV artifacts.",
    )
    parser.add_argument("--preconditioning-ticks", type=int, default=0)
    parser.add_argument("--include-cold-baseline", action="store_true")
    parser.add_argument("--case-limit", type=int, default=20)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--kernel-profile", choices=["integer", "unity"], default="integer")
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, (os.cpu_count() or 2) - 1),
        help="Process count (default: cpu_count-1).",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--disable-fast-step", action="store_true")
    parser.add_argument("--verify-fast-step", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    if args.verify_fast_step and args.disable_fast_step:
        raise ValueError("--verify-fast-step requires fast-step enabled.")

    if not args.execute:
        raise SystemExit(
            "Dry-run safety: add --execute. Example: "
            "python world_code/Python_code/generate_weinberg_20_cases_parallel.py "
            "--execute --workers 8 --resume"
        )

    payload = execute_cases_incremental(
        out_dir=Path(args.output_dir),
        preconditioning_ticks=args.preconditioning_ticks,
        include_cold_baseline=args.include_cold_baseline,
        case_limit=args.case_limit,
        max_steps=args.max_steps,
        kernel_profile=args.kernel_profile,
        workers=args.workers,
        use_fast_step=not args.disable_fast_step,
        verify_fast_step=args.verify_fast_step,
        resume=args.resume,
    )
    print(f"Generated {payload['case_count']} cases")
    print(f"Wrote {Path(args.output_dir) / 'weinberg_20_cases.json'}")
    print(f"Wrote {Path(args.output_dir) / 'weinberg_20_cases.csv'}")


if __name__ == "__main__":
    main()

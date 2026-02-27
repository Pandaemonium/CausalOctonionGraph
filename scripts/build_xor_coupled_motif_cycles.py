#!/usr/bin/env python3
"""
Build coupled XOR motif cycle artifacts (pair motifs with deterministic coupling).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calc.xor_coupled_motif_cycles import main


if __name__ == "__main__":
    raise SystemExit(main())

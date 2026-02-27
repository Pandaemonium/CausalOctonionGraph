#!/usr/bin/env python3
"""
Build XOR Furey ideal cycle artifacts.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calc.xor_furey_ideals import main


if __name__ == "__main__":
    raise SystemExit(main())


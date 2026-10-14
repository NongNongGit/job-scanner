"""Compatibility entry point for checkout users and existing direct imports."""

import sys
from pathlib import Path

_source_dir = str(Path(__file__).resolve().parent / "src")
if _source_dir not in sys.path:
    sys.path.insert(0, _source_dir)

from job_scanner import main as _main

if __name__ == "__main__":
    _main.cli()
else:
    # Keep existing ``import main`` callers and monkeypatches on the canonical module.
    sys.modules[__name__] = _main

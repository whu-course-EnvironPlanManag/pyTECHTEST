#!/usr/bin/env python3
"""
Command Line Interface for US DOE TECHTEST 1.0 Python Suite.
Provides run, convert, labor-estimate, and grid-mix queries.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path for direct execution without installation
_BASE_DIR = Path(__file__).resolve().parent
if str(_BASE_DIR) not in sys.path:
    sys.path.insert(0, str(_BASE_DIR))

from pytechtest.cli import main

if __name__ == "__main__":
    main()

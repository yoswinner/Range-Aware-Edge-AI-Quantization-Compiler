"""Root-level evaluation entry point.

Executes the evaluation runner over benchmark programs, displaying safety and
quantization metrics.

Usage:
    python evaluate.py
    python -m tests.evaluation
"""

import sys
from tests.evaluation import main

if __name__ == "__main__":
    sys.exit(main())

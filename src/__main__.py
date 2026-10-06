"""Allow ``python -m src <file>`` as a shorthand for ``python -m src.main <file>``."""

import sys

from src.main import main

if __name__ == "__main__":
    sys.exit(main())

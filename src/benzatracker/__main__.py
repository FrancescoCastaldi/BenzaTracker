"""Entry point: ``python -m benzatracker`` dispatches to CLI, GUI or Web."""
from __future__ import annotations

import os
import sys


def main() -> None:
    args = [a.lower() for a in sys.argv[1:]]

    if "--web" in args or os.environ.get("BENZA_WEB"):
        from .web import run

        run()
    elif "--gui" in args:
        from .gui import run

        run()
    else:
        from .cli import run

        run()


if __name__ == "__main__":
    main()

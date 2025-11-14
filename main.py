"""Entry point for BenzaTracker allowing GUI or CLI selection."""

from __future__ import annotations

import sys


def main() -> None:
    """Launch the GUI by default or the CLI when ``--cli`` is provided."""

    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        from benzatracker.cli import run as run_cli

        run_cli()
    else:
        from benzatracker.gui import run as run_gui

        run_gui()


if __name__ == "__main__":
    main()

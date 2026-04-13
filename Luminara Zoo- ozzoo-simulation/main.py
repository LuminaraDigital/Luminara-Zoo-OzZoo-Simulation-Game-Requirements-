"""Entry point: Luminara Zoo simulation (NIT2112 OzZoo-style brief).

Run (interactive terminal recommended):

    python main.py

After ``pip install -e .`` you may use console scripts ``luminara`` or ``ozzoo``
(see ``pyproject.toml``). On Windows, ``$env:PYTHONUTF8 = "1"`` can improve
Unicode output in some consoles. Closed stdin exits cleanly after startup
(see ``ui.cli.run_game_loop``).
"""

from __future__ import annotations

from ui.cli import run_game_loop


def main() -> None:
    """Console entry point for setuptools / ``python -m`` style launches."""
    run_game_loop()


if __name__ == "__main__":
    main()

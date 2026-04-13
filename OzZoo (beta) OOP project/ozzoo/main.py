"""
main.py — Entry point for the OzZoo Simulation Game.

Run with:
    python main.py

Dependencies (install via pip):
    pip install rich

Author : Babatundji Williams-Fulwood (s8138393)
Unit   : NIT2112 Object Oriented Programming — Victoria University
"""

import sys
import os

# Ensure project root is on the Python path regardless of working directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.cli import run_game

if __name__ == "__main__":
    try:
        run_game()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. G'bye! 🦘")
        sys.exit(0)

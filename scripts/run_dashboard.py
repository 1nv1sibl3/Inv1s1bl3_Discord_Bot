#!/usr/bin/env python3
"""Run the Inv1s1bl3 Web Management Dashboard."""
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.__main__ import setup_logging, run_web

if __name__ == "__main__":
    setup_logging()
    run_web()

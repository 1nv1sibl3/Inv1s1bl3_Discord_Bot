#!/usr/bin/env python3
"""Run the Inv1s1bl3 Discord Bot."""
import asyncio
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.__main__ import setup_logging, run_bot

if __name__ == "__main__":
    setup_logging()
    asyncio.run(run_bot())

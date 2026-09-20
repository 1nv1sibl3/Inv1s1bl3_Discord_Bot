#!/usr/bin/env python3
"""Initialize the Inv1s1bl3 database schema."""
import asyncio
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database.session import init_db

if __name__ == "__main__":
    print("Creating all database tables...")
    asyncio.run(init_db())
    print("Database tables initialized successfully.")

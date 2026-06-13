# -*- coding: utf-8 -*-
"""Domain-specific (OPTIONAL) store loader for the buddhist KG — chokepoint demo only.

The engine core never needs this. It exists for two adapter-level checks:
  · a single read entry-point (chokepoint), so new readers are a recordable event;
  · a place to assert label-preservation (every returned record carries its tier).

Wraps the KG's own v0_3 loader. Adjust paths to your checkout.
"""
from __future__ import annotations
import sys
from pathlib import Path

DB_ROOT = Path(__file__).resolve().parents[3]   # adjust to your DB checkout
LOADER_DIR = DB_ROOT / "buddhist-corpus" / "_scripts" / "v0_3"
STORE_DIR = DB_ROOT / "buddhist-corpus" / "_indexes" / "v0_3"


def open_store(include_candidates: bool = True):
    if str(LOADER_DIR) not in sys.path:
        sys.path.insert(0, str(LOADER_DIR))
    import loader  # type: ignore
    return loader.load_indexes(STORE_DIR, include_candidates=include_candidates)

# -*- coding: utf-8 -*-
"""live_accessors — enumerate files that reference the store, per the versioned predicate.

This is the whole 'reads the store' surface of the engine: it greps the project tree.
It never opens the store itself. File types are driven by predicate.include_globs, so the
engine is not Python-specific.
"""
from __future__ import annotations
import re
from pathlib import Path


def live_accessors(project_root, predicate) -> set:
    if not predicate:
        return set()
    pat = re.compile(predicate.get("access_pattern", ""))
    excl = predicate.get("exclude_substrings", [])
    globs = predicate.get("include_globs", ["**/*.py"])
    root = Path(project_root)
    hits = set()
    for g in globs:
        for p in root.glob(g):
            if not p.is_file():
                continue
            rel = p.relative_to(root).as_posix()
            if any(x in rel for x in excl):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if pat.search(text):
                hits.add(rel)
    return hits

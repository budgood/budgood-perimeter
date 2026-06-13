# -*- coding: utf-8 -*-
"""Append-only manifest loader. Zero domain knowledge.

Record types (by "type" field): store | predicate | channel | unowned.
A correction is a new line with the SAME id (old line kept). The active view is
"latest-by-id where status == active" — mirrors any append-only + rebuildable view.
"""
from __future__ import annotations
import json
from pathlib import Path


def read_jsonl(path: Path):
    rows = []
    try:
        if not path.exists() or path.stat().st_size == 0:
            return rows
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                ln = line.strip()
                if not ln or ln.startswith("//"):
                    continue
                try:
                    rows.append(json.loads(ln))
                except Exception:
                    continue   # one bad line never sinks the rest
    except Exception:
        return rows
    return rows


def load(manifest_path: Path) -> dict:
    """Return {type: [active records]} after latest-by-id-active collapse."""
    rows = read_jsonl(manifest_path)
    latest = {}
    for r in rows:
        if r.get("id"):
            latest[r["id"]] = r
    by_type: dict = {}
    for r in latest.values():
        if r.get("status") == "active":
            by_type.setdefault(r.get("type"), []).append(r)
    return by_type


def active_predicate(by_type: dict):
    preds = by_type.get("predicate", [])
    return preds[-1] if preds else None


def registered_channel_paths(by_type: dict):
    return {r.get("path") for r in by_type.get("channel", [])}


def append(path: Path, record: dict):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

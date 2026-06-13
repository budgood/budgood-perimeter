# -*- coding: utf-8 -*-
"""Reflexive staleness signal — illuminate-only, wire-anywhere.

check() returns a salience string when the last survey is older than the threshold,
else None. It states a process fact ("N days since last survey"); it NEVER prescribes a
deadline (a deadline on judgement = legislating one's own scope = forbidden).

Its object-of-attention is system time, not any input — so wire it to a non-content event
surface: CI, cron, a git pre-commit hook, or an agent SessionStart. See examples/.
"""
from __future__ import annotations
import datetime as _dt
from . import manifest as M


def check(cfg):
    rows = M.read_jsonl(cfg.attest_path)
    if not rows:
        return ("[perimeter] no attestation on record: the channel perimeter has never been "
                "surveyed. Not a command — but you can no longer pretend not to see it. "
                "Run: budgood-perimeter scan")
    last = rows[-1]
    d0 = last.get("date", "")
    try:
        age = (_dt.date.today() - _dt.date.fromisoformat(d0)).days
    except Exception:
        return None
    if age <= cfg.stale_days:
        return None
    thin = "  (and the last survey was thin)" if last.get("thin") else ""
    return (f"[perimeter] {age} days since last survey{thin}; over the {cfg.stale_days}-day "
            f"threshold. A process fact, not a deadline — whether you recount the doors is your "
            f"live act. Run: budgood-perimeter scan, then attest.")

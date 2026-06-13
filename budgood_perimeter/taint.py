# -*- coding: utf-8 -*-
"""Reference remediation for a label leak (SPEC §9).

A leaking channel returns store content stripped of its epistemic grade. The fix is to make
the value arrive at the boundary SELF-LABELLED: pair each returned value with the grade
extracted from its source record. This is the minimal reusable primitive.

It enforces nothing (illuminate, not control) — it is a tool an adapter applies at a channel
it has DECIDED to fix. Applying it flips that channel's manifest `label_preserving` to true.
"""
from __future__ import annotations
from dataclasses import dataclass
import functools

GRADE_FIELDS = ("tier", "confidence", "status", "lifecycle_state",
                "coverage_status", "provenance")


@dataclass(frozen=True)
class Labeled:
    value: object
    grade: dict     # the epistemic grade carried across the boundary

    def __repr__(self):
        return f"Labeled({self.value!r}, grade={self.grade})"


def grade_of(record, fields=GRADE_FIELDS) -> dict:
    """Extract the epistemic grade from a store record."""
    if not isinstance(record, dict):
        return {}
    return {k: record[k] for k in fields if k in record}


def attach(value, source_record, fields=GRADE_FIELDS) -> Labeled:
    """Pair a value with its source record's grade, so the grade crosses the boundary with it."""
    return Labeled(value, grade_of(source_record, fields))


def preserve(reader, fields=GRADE_FIELDS):
    """Wrap a reader that yields (value, source_record) pairs so it returns Labeled values.

    Apply at a leaking channel:
        get_hits = preserve(bm25_pairs)   # was: returned bare values
    Now every hit arrives carrying its tier/confidence — no consumer can mistake candidate-grade
    content for gold without seeing it.
    """
    @functools.wraps(reader)
    def wrapped(*a, **k):
        return [attach(v, src, fields) for (v, src) in reader(*a, **k)]
    return wrapped

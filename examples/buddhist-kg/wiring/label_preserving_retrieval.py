# -*- coding: utf-8 -*-
"""Illustrative remediation for the BM25 leak (PRM-CH-002 build_index).

A leaking retrieval reader returns bare hits — text/score, no tier. Wrapping it with
budgood_perimeter.taint makes each hit arrive carrying its source record's grade, so a
downstream actor cannot treat candidate-grade text as gold without seeing it. This is the
reference shape; adapt to your real retrieval call. Applying it flips PRM-CH-002's
label_preserving to true (then re-attest the survey).
"""
from budgood_perimeter.taint import preserve


# BEFORE (leak): grade stripped at the boundary.
def bm25_hits_leaky(query):
    rows = _search(query)                 # rows joined to concept_nodes carry tier/confidence
    return [r["text"] for r in rows]      # <-- grade dropped here


# AFTER (preserving): yield (value, source_record); preserve() attaches the grade.
def _bm25_pairs(query):
    return [(r["text"], r) for r in _search(query)]

bm25_hits = preserve(_bm25_pairs)         # each hit -> Labeled(text, {tier, confidence, ...})


def _search(query):
    # stand-in for the real BM25 search joined to the store
    return [{"text": "…", "score": 0.9, "tier": "T5", "confidence": "low"}]

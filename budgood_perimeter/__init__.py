"""budgood_perimeter — perimeter governance engine (缘起工程 / Condition Engineering).

Governs ONE locus: the perimeter — the set of channels that touch a knowledge store.
It never reads store *contents*; it only enumerates what references the store, diffs that
against an append-only manifest, and makes the act of re-surveying impossible to forget.

Three invariants (the constitution):
  1. append-only + provenance  — records immutable; a fix is a new same-id version.
  2. illuminate, not control   — the engine diffs/lists/records; it never auto-fixes,
                                 auto-promotes, or co-opts a channel. Judgement stays live.
  3. contributory not primary  — (增上缘非亲因) the apex survey is never forced; a system
                                 that could force its own perimeter recount would be
                                 legislating its own scope.
"""
__version__ = "0.1.0"

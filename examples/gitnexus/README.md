# examples/gitnexus — second adapter (a deliberately different store)

This adapter exists to **test the engine's generality**, not to ship a polished GitNexus integration.
GitNexus is a TypeScript code-intelligence tool whose store is a **graph database** (graphology +
a custom LadybugDB) under `.gitnexus/` — nothing like the jsonl knowledge graph of `buddhist-kg`.
Pointing the *unchanged* engine at it surfaced three findings:

1. **A non-file store works — because the engine never opens the store.** GitNexus keeps its index
   in a graph DB, not files. The engine governs its perimeter anyway: it only enumerates the `.ts`
   modules that read the graph, and never touches the graph itself. The "engine never reads the
   store" design is exactly what makes it store-shape-agnostic.

2. **For a store behind an access layer, the predicate targets the layer.** No module greps
   `.gitnexus/` directly; readers go through the `lbug` / LadybugDB layer. So the predicate's
   `access_pattern` is `LadybugDB|lbug`, not a store path. The versioned-predicate model absorbs
   this with zero engine change (and `/i18n/` is excluded as false positives — translation strings
   that merely mention "lbug").

3. **Label-preservation generalizes, with a different grade vocabulary.** A KG record's grade is
   `tier` / `confidence` / `candidate`. A code-intelligence record's grade is **resolution
   `confidence` / `unresolved` / `isAmbiguous`** (410 / 95 / 2 occurrences in src). A reader that
   returns a resolved call edge *without* its confidence is the same leak. `taint.GRADE_FIELDS`
   would just be configured with `("confidence", "unresolved", "isAmbiguous")` here.

This is a seed, not a finished survey — a real survey would de-noise the predicate hits (the i18n
false positives) and judge each reader's label-preservation. Set `project_root` in `perimeter.toml`
to a GitNexus checkout, then `budgood-perimeter scan`.

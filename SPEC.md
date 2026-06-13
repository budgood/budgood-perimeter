# budgood-perimeter — Specification (v0.1)

Normative spec for the perimeter governance engine. A conforming implementation MAY be
written in any language. Keywords MUST / MUST NOT / SHOULD per RFC 2119.

## 1. Scope & non-goals
This spec governs **one locus: the perimeter** — the set of channels that read a knowledge
store. An implementation MUST NOT, as part of this spec, perform retrieval, evaluation,
routing, judgement, promotion, or any agent loop. It enumerates, diffs, records, illuminates.

## 2. Constitution (invariants)
A conforming implementation MUST uphold all three:
1. **Append-only + provenance.** Manifest and attestation records are immutable. A correction
   is a new record with the same `id`; the active view is latest-by-id where `status==active`.
2. **Illuminate, not control.** The engine MUST NOT modify scanned files, auto-register
   channels, auto-promote, or take any side-effecting action on the store. Output is
   information only.
3. **Contributory, not primary (增上缘非亲因).** The engine MUST NOT force, schedule-as-deadline,
   or self-trigger the survey. The decision to survey is a live act outside the engine.

## 3. Data model
Records are JSON objects on lines of an append-only file. `type` ∈ {store, predicate, channel,
unowned, perimeter_attestation}. Common: `id` (except attestations), `status`
∈ {active, superseded, dormant}.

- **store** — descriptive: `canonical_dir`, `canonical_files`, `derivatives`, `source_anchor`.
- **predicate** — `version`, `include_globs` (list), `access_pattern` (regex),
  `exclude_substrings` (list). The rule that decides what counts as a channel.
- **channel** — `path`, `role` ∈ {reader, writer, auditor}, `ownership` ∈ {owned, unowned},
  `label_preserving` (bool | string), `found_under_predicate` (version), `last_confirmed`.
- **unowned** — `boundary`, `crosses`, `hazard`, `last_judged`. A boundary that cannot be
  instrumented.
- **perimeter_attestation** — `date`, `by`, `channel_diff` {born, died, changed},
  `predicate_review`, `predicate_version_after`, `unowned_judgments`,
  `checklist_version_after`, `thin` (bool), `note`.

## 4. The predicate (versioned, falsifiable)
The active predicate is the latest-by-id `predicate` record with `status==active`. A conforming
survey MUST re-examine the predicate by attempting to falsify it (find an access shape it would
miss), and MUST bump its `version` (append a new predicate, supersede the old) when reality
outgrows it. Implementations SHOULD surface the categories: new path, indirection, new
language/runtime, store-referent drift, ownership crossing, false positives.

## 5. Survey protocol
A survey has three segments:
- **mechanical** — compute `live = {files under include_globs matching access_pattern, minus
  exclude_substrings}`; diff against registered channel paths → born / died / changed
  (changed = registered & live but `found_under_predicate` != active version). A channel with
  `found_under_predicate == "manual"` (a predicate-blind channel carried by hand) MUST be excluded
  from `died`.
- **judgement** — re-examine the predicate (§4) and judge each `unowned` boundary. NOT
  automatable; scaffolded by a checklist.
- **attestation** — append one `perimeter_attestation`. An attestation with empty
  `channel_diff` AND empty `predicate_review` AND empty `unowned_judgments` MUST be marked
  `thin: true`.

## 6. Staleness signal
A conforming implementation MUST provide a reflexive signal that compares the latest
attestation date to a threshold and emits a process-fact string when overdue (or when no
attestation exists). It MUST NOT emit a deadline or imperative. Its trigger surface MUST be a
non-content system event (CI, cron, VCS hook, agent session start), never user input.

## 7. Honest dashboard
A status view MUST NOT claim or display completeness of the perimeter. It MAY report:
last-attested date, age, predicate version, owned/unowned counts, last-thin. Freshness, never
completeness.

## 8. Conformance
A conforming **engine** implements §3–§7 and upholds §2. A conforming **adapter** provides a
config locating `project_root` + manifest + attestations, and a manifest seeded with a `store`
record and an active `predicate`. An adapter MAY provide a store loader for an optional
chokepoint/label-preservation check; the engine core MUST function without it.

## 9. Label-preservation (optional capability)
The perimeter engine governs the *channel set*; the **value-at-boundary** locus — whether a
channel carries the store's epistemic grade (tier/confidence/candidate-status) across its
boundary — is governed by an optional capability built on the same manifest.

A `channel` record MAY declare `label_preserving`:
- `true` — returns store records carrying their grade.
- `false` — a **leak**: returns store content stripped of its grade.
- `"<transform>"` (string, e.g. `"flatten-D"`) — returns content with the grade replaced by a
  single fixed grade.
- absent — **undeclared**; a reader not yet judged.

A conforming implementation that offers this capability MUST be able to enumerate channels by
these classes and MUST surface `false` (leak) and undeclared readers as the hazard. It MUST
NOT auto-remediate (illuminate, not control); remediation — attaching the grade to the value
at that channel (a signature/taint) so it arrives self-labelled — is a live act outside the
engine. This converts a label leak from a comment into a thing the engine can list.

**Reference remediation.** To fix a leak, the channel SHOULD make each returned value arrive
self-labelled: pair it with the epistemic grade extracted from its source record (a `Labeled`
value). An implementation offering this capability SHOULD provide such a primitive —
`attach(value, source_record)` and a `preserve(reader)` wrapper. Applying it at a channel
flips that channel's `label_preserving` to `true`.

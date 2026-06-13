# budgood-perimeter

**English** · [中文](README.zh.md)

> Keep an auditable list of **everything that reads your knowledge base**, get told when that list changes, and never let it quietly rot. Zero dependencies, ~600 lines, Apache-2.0.

[![tests](https://img.shields.io/badge/tests-12%20passing-brightgreen)](docs/validation.md) [![python](https://img.shields.io/badge/python-%E2%89%A53.8-blue)]() [![dependencies](https://img.shields.io/badge/dependencies-0-lightgrey)]() [![license](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

---

## The 60-second picture

You maintain a **knowledge base** — a JSONL knowledge graph, a vector index your RAG app
queries, an agent's long-term memory, a code-intelligence graph. Pick whichever you have.

On day one, two scripts read it. Six months later — after a dozen commits, a few teammates,
and maybe an agent or two — **how many things read that knowledge base now?**

You don't know. Nobody does. There is no list. And three things are quietly going wrong:

- **New readers appear and nobody notices.** A nightly job, a new endpoint, a vendored copy —
  each one now depends on your data, untracked.
- **Some readers silently drop the metadata.** Your records carry a grade — `confidence: low`,
  `status: candidate`, `tier: T5` ("unverified guess"). A faithful reader passes that through.
  A careless one returns just the text, so downstream code treats a guess as established fact.
- **The dashboard lies by omission.** "Coverage: 95%" stays green, because nobody is checking
  whether the *map of who-touches-what* is still correct. It rots in silence.

**budgood-perimeter** is a small tool that fixes the *not knowing*. It keeps an auditable,
append-only list of every **channel** (script/service/export) that reads your store, and:

| command | what it tells you |
|---|---|
| `scan` | which readers are **new**, **gone**, or **changed** since you last looked |
| `labels` | which readers **drop the metadata** (a "leak") vs. carry it through |
| `staleness` | nags you — once — when it's been too long since anyone re-checked |
| `status` | an honest dashboard that reports *freshness*, and refuses to ever say "complete" |
| `attest` | records each check, so "when did we last actually look, and what did we find?" has an answer |

**It never reads your data.** It only watches the *doors* — the files that reference the store.
Think of it as a smoke detector for the blind spot every knowledge base has: the doors you
forgot exist.

## A 2-minute walkthrough

Say your knowledge base is `kb.jsonl` and readers call a helper `open_kb()`.

**1. Tell it where to look** (`perimeter.toml`):

```toml
project_root = "."
[paths]
manifest = "channels.jsonl"
attestations = "attestations.jsonl"
```

**2. Seed the list** (`channels.jsonl`) — the store, how to *spot* a reader (the "predicate"),
and the readers you already know about:

```jsonl
{"id":"STORE","type":"store","status":"active","canonical_files":["kb.jsonl"]}
{"id":"PRED-1","type":"predicate","status":"active","version":"v1","include_globs":["**/*.py"],"access_pattern":"open_kb|kb\\.jsonl"}
{"id":"CH-1","type":"channel","status":"active","path":"api/search.py","role":"reader","label_preserving":true,"found_under_predicate":"v1"}
```

**3. Scan — and it catches a reader nobody tracked:**

```text
$ budgood-perimeter scan --config perimeter.toml
=== perimeter survey · mechanical (predicate v1) ===
live 2 · registered 1
[born  unregistered] 1
  + jobs/nightly_export.py      <- a new reader of your KB that no one was tracking
[died  registered-but-gone] 0
[changed] 0
--- judgement segment (not automatable; the live act) ---
Part I  re-examine the predicate ...   Part II  judge each unowned boundary ...
```

**4. You open `nightly_export.py`, decide it's a real reader that strips the grade, register it,
and record the survey** (this is the human step — the tool never decides for you):

```text
$ budgood-perimeter attest --config perimeter.toml --by alice \
    --predicate-review "nightly_export is a real channel; it returns bare rows -> register as a leak"
```

**5. Now `labels` shows the leak you just found:**

```text
$ budgood-perimeter labels --config perimeter.toml
[LEAK  drops the grade] 1
  jobs/nightly_export.py  (reader) -> False
```

That's the whole loop: *the tool finds the change and lists the leak; you make the call; the
record remembers it.*

## Who is this for

- You maintain a **knowledge graph / RAG index / agent memory / code graph** that more than one
  thing reads, and the list of readers has outgrown your head.
- You care that **low-confidence / candidate / unverified** records don't get laundered into
  "fact" as they pass through readers.
- You want an **audit trail** of "who reads our data, and when did we last verify that list."

**Not for you if:** you want an eval harness, a retriever, a router, or an agent loop.
budgood-perimeter governs exactly one thing — *the set of readers* — and deliberately stops there.

## What it does *not* do (on purpose)

- It **never modifies** your code or data — it lists and records, it does not fix.
- It **never auto-registers** a new reader or auto-classifies a leak — you do, as a judgement call.
- It **never forces** you to survey on a schedule. It can *nag* (staleness), but a deadline on
  judgement is exactly what it refuses to impose. (The why is in the philosophy section.)

---

## Install

Zero dependencies; **Python ≥ 3.8**. (TOML parsing uses stdlib `tomllib` on 3.11+, `tomli` if
installed, else a built-in fallback — so it runs anywhere with nothing to install.)

```bash
git clone https://github.com/budgood/budgood-perimeter && cd budgood-perimeter
pip install -e .            # gives you the `budgood-perimeter` command
# (PyPI release pending: pip install budgood-perimeter)
```

No install needed to try it: `python -m budgood_perimeter scan --config perimeter.toml`.

## Command reference

```bash
budgood-perimeter scan      --config perimeter.toml   # new / gone / drifted readers vs the list
budgood-perimeter status    --config perimeter.toml   # honest dashboard (freshness, never "complete")
budgood-perimeter staleness --config perimeter.toml   # one line iff the survey is overdue
budgood-perimeter labels    --config perimeter.toml   # which readers strip the store's metadata
budgood-perimeter attest    --config perimeter.toml --predicate-review "..." --by you
```

## How a survey works (the model)

Three pieces, by design:

1. **Mechanical (free, automatic).** The engine scans your tree for files matching the
   **predicate** (a versioned rule like "imports `open_kb` or mentions `kb.jsonl`"), and diffs
   that live set against your registered list → **born / died / changed**.
2. **Judgement (yours, not automatable).** You look at what changed and decide: is this a real
   channel? Does the predicate need to catch a new pattern? Does it leak the grade? The tool
   scaffolds the questions ([`docs/checklist.md`](docs/checklist.md)) but never answers them.
3. **Attestation (recorded).** Your survey is appended as one immutable record. A survey that
   found and judged *nothing* is auto-flagged `thin` — a suspiciously cheap look.

Everything is **append-only**: you never edit a record, you append a new same-id version; the
active view is "latest-by-id where status == active", always rebuildable. The **predicate is
itself a versioned record** you bump when reality outgrows it. The **dashboard never claims
completeness** — only how fresh the last survey is.

## Write an adapter (use it on your own store)

An adapter is just: a `perimeter.toml` (project root + file paths) and a `channels.jsonl` seeded
with one `store` record and one active `predicate`. That's it — the engine core contains **zero
domain code**. A complete, real, high-stakes adapter (a scholarly knowledge graph) lives in
[`examples/buddhist-kg/`](examples/buddhist-kg/) and was used to validate the engine on live data.

## Validated on real data

The generic engine was validated against **two structurally different real stores with zero core
changes**: a live jsonl **knowledge graph** (`examples/buddhist-kg`, where it reproduced the
project's hand-written audit number-for-number) and a TypeScript **code-intelligence graph DB**
(`examples/gitnexus`, GitNexus). The same engine governs both; `labels` surfaced real metadata
leaks in each. 12 unit tests pass with zero dependencies. Full brief: [`docs/validation.md`](docs/validation.md).

---

## The thinking behind it (optional reading)

**Origin — this was not built to optimize "Loop Engineering" or any agent framework.** It was extracted from a real system its author built to govern the **Xunsizhe Research-grade Knowledge Graph** (寻思者研究型知识图谱) — a knowledge graph of their own making, its design informed by the Yogācāra (Consciousness-Only) model of the ālaya-vijñāna (the "store-consciousness", where latent seeds and their active manifestations continually condition — "perfume" — one another), and built around a distinctive anti-hallucination mechanism. Its design applies the same idea to the system's own operative *identity* — which mode is in force at a given moment: not a fixed persona, and not a choice outsourced to a lookup table, but a live act of discernment *aided by conditions yet ultimately arising from within*. A small append-only table of "object-feature → what to watch for" only **illuminates** the risks of the current input so they can't be ignored; it never routes, decides, or acts for the model. Two practical questions kept biting. First: *how many things actually read this knowledge base now?* — over time, scripts, services, and agents pile up until the list of readers outgrows anyone's memory. Second, and subtler: every record carries a **grade**, a marker like "unverified", "low-confidence", or "candidate" that says *how much to trust it*. When a reader pulls that record and passes it downstream, does it **carry the marker along, or quietly drop it?** A reader that drops it turns a flagged guess into apparent fact. The tool exists because both problems were real, recurring, and unowned — not because of any trend in agent tooling.

budgood-perimeter is the first tool from a small design discipline its author calls **缘起工程 /
Condition Engineering** — itself rooted in classical categories (亲因 *primary cause* vs 增上缘
*contributory condition*), not in agent frameworks. One idea drives the whole thing:

> **Never let the substrate become the *primary cause* of a decision.** Data, tables, code, and
> even this tool can *inform* a judgement; they must not *make* it. The judgement stays in the
> live act of whoever (human or agent) is looking right now.

Three invariants fall out of that, and the tool enforces them on itself:

1. **Append-only + provenance** — the record of "who reads what" is immutable and rebuildable, so
   it can't drift into a confident-but-wrong state. (This is also why it resists a knowledge-layer
   version of *model collapse*: real, attested facts stay anchored against self-generated drift.)
2. **Illuminate, not control** — the engine makes problems *visible*; it never acts on them. The
   moment a tool starts auto-fixing what it finds, its rule table becomes a thing that rots.
3. **Contributory, not primary** *(增上缘 not 亲因)* — the engine never forces its own re-survey.
   A system that could compel you to re-check its own perimeter would be defining its own scope —
   and then it could quietly decide it's complete. So the apex act stays unforced; the tool only
   guarantees you can never *quietly believe* your list is correct.

**On agentic loops — a contrast worth drawing (though not the motivation).** It wasn't built to fix agentic *loop engineering*, but holding the two side by side is genuinely clarifying, because they make opposite bets about *where judgement lives*. Loop engineering pushes judgement *out* of the model and into the scaffold — evals, routers, verifiers that decide and converge automatically. This keeps judgement *in* the live act and uses data only to make risks impossible to miss.

The useful part is that the two bets fail differently. Hardened scaffolds fail **silently and systematically**: when the world shifts, a stale eval or router keeps deciding — confidently wrong, and the error is institutionalized into a rule (the real incident where a drifting verifier quietly escalated ~90% of traffic to the most expensive model, nothing erroring). Live judgement fails **locally and stochastically**: someone misjudges once, but it isn't frozen into a rule. So loop-closure is one *setting of a dial* — the right one with a hard, cheap oracle and a reversible action, and malpractice without them. budgood-perimeter is what the other end of that dial looks like, made concrete. The full calibration theory — and how the lineage runs prompt engineering → context engineering → governed perimeter — is in [`docs/framework.md`](docs/framework.md).

## Concepts

| term | plain meaning |
|---|---|
| store | your knowledge base; the engine never opens it |
| channel | a file/service that reads the store |
| predicate | the versioned rule for "what counts as a reader" |
| born / died / changed | readers new since / gone since / drifted since the last survey |
| owned / unowned | a boundary you can instrument vs one you can't (a human, an external tool, an LLM's context) |
| attestation | an immutable record that a survey happened: the diff, your review, the date |
| thin | an attestation that engaged nothing — itself flagged for attention |
| label-preserving | whether a reader carries the store's metadata (grade) across its boundary |
| leak | a reader that returns store content with the grade stripped off |

## Contact

Questions, ideas, or want to compare notes on governing knowledge bases — Buddhist text
corpora and code-intelligence governance especially welcome? Reach the author
(**释则生 / Shi Zesheng**):

- **Email**: budgood@163.com
- **WeChat**:

<img src="docs/assets/wechat-shizesheng.png" alt="WeChat: 释则生" width="240">

## License

[Apache-2.0](LICENSE).

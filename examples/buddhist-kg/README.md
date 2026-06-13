# examples/buddhist-kg — reference adapter (hardest corner)

Wires `budgood-perimeter` to a canonical-text scholarship knowledge graph: **no hard oracle**
(does a passage "discuss" a concept? interpretive), **high irreversibility** (a false node wears
structured authority). This is the corner where the engine matters most and where loop-closure
is malpractice — you govern the perimeter and keep judgement live.

What this adapter provides (all an adapter ever needs):
- `perimeter.toml` — points at the KG checkout + paths.
- `channels.jsonl` — seeded store/predicate/channel/unowned records (real readers of the KG).
- `attestations.jsonl` — survey log.
- `open_store_adapter.py` — OPTIONAL: the chokepoint/label-preservation hook into the KG's loader.
- `wiring/claude_code/` — routes the staleness signal to a Claude Code SessionStart hook.

Note the channels seed records a real leak: a BM25 retrieval reader returns hits with
`label_preserving: false` — it strips the epistemic tier. The engine cannot fix that; it makes
the leaking channel a thing you can list with `budgood-perimeter scan`.

# Contributing

Thanks for looking. budgood-perimeter is deliberately small and has a few hard rules that keep
it honest. Please respect them in any PR.

## Run it locally
```bash
python -m unittest discover -s tests -p "test_*.py" -v   # 12 tests, zero dependencies
python -m budgood_perimeter scan --config examples/buddhist-kg/perimeter.toml
```

## Non-negotiable invariants (see SPEC.md §2)
1. **Append-only + provenance.** Never mutate a record; append a new same-id version.
2. **Illuminate, not control.** The engine lists and records — it MUST NOT auto-fix, auto-promote,
   auto-register a channel, or modify any scanned file. If a PR makes the engine *act* on what it
   finds, it will be declined.
3. **Contributory, not primary.** The engine MUST NOT force or schedule-as-deadline its own
   survey. Staleness illuminates; it never commands.

## Scope
This project governs exactly one locus — the perimeter (the set of channels reading a store).
It is not an eval harness, retriever, router, or agent loop. Features outside that locus belong
in a different project.

## Adding an adapter
An adapter is a `perimeter.toml` + a seed `channels.jsonl`. Put real-world adapters under
`examples/`. The engine core must stay domain-free (zero imports of any specific store).

# Roadmap / backlog

Convert each item into a GitHub Issue and add it to the project board.

## Release
- **chore: tag & release v0.1.0** — after the first push, `git tag v0.1.0 && git push --tags`, draft a GitHub Release.
- **ci: confirm Actions green on 3.8–3.12** — workflow is committed (`.github/workflows/ci.yml`); verify the run.
- **packaging: publish to PyPI** — reserve the name `budgood-perimeter`; `python -m build` + `twine upload`.

## Generality (proves the core is domain-free)
- **feat: a second, non-KG adapter** — e.g. a code-intelligence graph or a RAG/vector index, to show the engine needs zero domain code beyond `perimeter.toml` + a seed manifest.
- **spec: conformance test vectors** — fixtures a third-party implementation can run to self-check against SPEC.md.

## Label-preservation follow-through (from the buddhist-kg validation)
- **fix(buddhist-kg): remediate the 3 leaks with `taint`** — `build_index`, `build_vec_index`, `encode`; flip each channel's `label_preserving` to `true` and re-attest.
- **task: resolve the "pending deeper read" classifications** — verify `detect_text` (preserving?) and `encode` (leak?) by reading their actual return paths.
- **feat: `attest` embeds the label_report summary** — each survey record also snapshots leak/undeclared counts, so the audit trail captures the value-at-boundary state over time.

## Polish
- **docs: CODE_OF_CONDUCT + issue/PR templates.**
- **docs: a short "quickstart on your own store" tutorial** building on the README walkthrough.

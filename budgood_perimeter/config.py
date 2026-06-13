# -*- coding: utf-8 -*-
"""Load perimeter.toml -> Config. Domain-agnostic; needs only paths + a project root.

TOML parsing: stdlib tomllib (py>=3.11) -> tomli (if installed) -> a minimal built-in
fallback covering this config's flat schema (string/int/bool + one-level tables), so the
engine runs zero-dependency on any Python >= 3.8.

The predicate (what counts as a channel) lives IN the manifest as a versioned record,
not here — so it stays append-only and falsifiable. This file only resolves locations.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib as _toml          # py >= 3.11
    _HAVE = "tomllib"
except ModuleNotFoundError:          # py < 3.11
    try:
        import tomli as _toml        # optional dep
        _HAVE = "tomli"
    except ModuleNotFoundError:
        _toml = None
        _HAVE = "minimal"


def _minimal_loads(text: str) -> dict:
    """Tiny TOML subset: comments, [table], key = "str" | int | float | true/false."""
    data: dict = {}
    cur = data
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()   # NOTE: '#' inside a value is not supported (fallback only)
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            cur = data.setdefault(line[1:-1].strip(), {})
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        if v[:1] in ("\"", "'"):
            v = v[1:-1]
        elif v.lower() in ("true", "false"):
            v = (v.lower() == "true")
        else:
            try:
                v = int(v)
            except ValueError:
                try:
                    v = float(v)
                except ValueError:
                    pass
        cur[k] = v
    return data


def _loads(text: str) -> dict:
    return _toml.loads(text) if _toml is not None else _minimal_loads(text)


@dataclass
class Config:
    project_root: Path
    manifest_path: Path
    attest_path: Path
    stale_days: int = 14


def load(config_path) -> Config:
    p = Path(config_path).resolve()
    data = _loads(p.read_text(encoding="utf-8"))
    base = p.parent
    pr = (base / data.get("project_root", ".")).resolve()
    paths = data.get("paths", {})
    manifest = (base / paths.get("manifest", "channels.jsonl")).resolve()
    attest = (base / paths.get("attestations", "attestations.jsonl")).resolve()
    stale = int(data.get("staleness", {}).get("threshold_days", 14))
    return Config(pr, manifest, attest, stale)

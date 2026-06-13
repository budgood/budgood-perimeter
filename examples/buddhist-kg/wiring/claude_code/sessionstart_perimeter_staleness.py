# -*- coding: utf-8 -*-
"""Claude Code SessionStart wiring: route the engine's staleness signal to session start.

Illuminate-only; fail-safe (SessionStart must never block startup). Register in
.claude/settings.json under hooks.SessionStart. Set CONFIG to this adapter's perimeter.toml.
"""
import sys, json
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / "perimeter.toml"  # adjust if needed


def _emit(ctx):
    print(json.dumps({"hookSpecificOutput": {"additionalContext": ctx}, "continue": True},
                     ensure_ascii=False))


def main():
    try:
        sys.stdin.buffer.read()
    except Exception:
        pass
    msg = ""
    try:
        import budgood_perimeter.config as C
        import budgood_perimeter.staleness as St
        msg = St.check(C.load(CONFIG)) or ""
    except Exception:
        msg = ""   # fail-safe: never block startup
    _emit(msg)
    sys.exit(0)


if __name__ == "__main__":
    main()

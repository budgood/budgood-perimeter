# -*- coding: utf-8 -*-
"""budgood-perimeter CLI:  scan | attest | status | staleness  (--config perimeter.toml)."""
from __future__ import annotations
import argparse
import json
import sys
from . import config as C
from . import survey as V
from . import staleness as St


def _p_scan(d):
    out = [f"=== perimeter survey · mechanical (predicate {d['predicate_version']}) ===",
           f"live {d['live_count']} · registered {d['registered_count']}",
           f"[born  unregistered] {len(d['born'])}"]
    out += [f"  + {f}" for f in d["born"]]
    out.append(f"[died  registered-but-gone] {len(d['died'])}")
    out += [f"  - {f}" for f in d["died"]]
    out.append(f"[changed  predicate-version-mismatch] {len(d['changed'])}")
    out += [f"  ~ {f}" for f in d["changed"]]
    out += ["", "--- judgement segment (not automatable; the live act) ---",
            "Part I  re-examine the predicate by trying to FALSIFY it (new path / indirection /",
            "        new language / store-referent drift / ownership crossing / false positives).",
            "Part II judge each unowned boundary (still unowned? value arrives self-labelled?",
            "        blast radius? has anything been built on it — exposure?).",
            "Then:   budgood-perimeter attest --predicate-review \"...\" [--unowned-judged \"...\"]"]
    return "\n".join(out)


def _p_status(s):
    lines = ["=== perimeter dashboard (never claims 'complete' — freshness only) ==="]
    if s["last_attested"]:
        warn = "  STALE" if s["stale"] else ""
        lines.append(f"last attested : {s['last_attested']}  ({s['age_days']} days ago{warn})")
        lines.append(f"predicate     : {s['predicate_version']}")
        lines.append(f"last thin?    : {s['last_thin']}")
    else:
        lines.append("last attested : none — never surveyed")
        lines.append(f"predicate     : {s['predicate_version']}")
    lines.append(f"owned channels: {s['owned']}")
    lines.append(f"unowned-watched: {s['unowned_watched']}")
    return "\n".join(lines)


def _p_labels(r):
    lines = ["=== label-preservation (value-at-boundary locus) ==="]
    def block(title, items):
        lines.append(f"[{title}] {len(items)}")
        for c in items:
            lines.append(f"  {c.get('path')}  ({c.get('role')})  -> {c.get('label_preserving')!r}"
                         f"   {c.get('notes','')}")
    block("LEAK  drops the grade", r["leak"])
    block("TRANSFORM  flattens the grade", r["transform"])
    block("UNDECLARED  reader not yet judged", r["undeclared"])
    block("preserving", r["preserving"])
    if r["leak"] or r["undeclared"]:
        lines.append("\n(leaks/undeclared are listed, not fixed. Fix = taint/signature at the "
                     "channel so the value arrives self-labelled. A live act.)")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="budgood-perimeter",
                                 description="perimeter governance engine (缘起工程)")
    ap.add_argument("command", choices=["scan", "attest", "status", "staleness", "labels"])
    ap.add_argument("--config", default="perimeter.toml")
    ap.add_argument("--predicate-review", dest="predicate_review", default="")
    ap.add_argument("--unowned-judged", dest="unowned_judged", default="")
    ap.add_argument("--predicate-bump", dest="predicate_bump", default="")
    ap.add_argument("--checklist-version", dest="checklist_version", default="v1")
    ap.add_argument("--by", default="")
    ap.add_argument("--note", default="")
    a = ap.parse_args(argv)
    try:
        cfg = C.load(a.config)
    except Exception as e:
        print(f"[config] cannot load {a.config}: {e}", file=sys.stderr)
        return 2
    if a.command == "scan":
        print(_p_scan(V.scan(cfg)))
    elif a.command == "status":
        print(_p_status(V.status(cfg)))
    elif a.command == "staleness":
        msg = St.check(cfg)
        if msg:
            print(msg)
    elif a.command == "labels":
        from . import survey as V2
        print(_p_labels(V2.label_report(cfg)))
    elif a.command == "attest":
        rec = V.attest(cfg, predicate_review=a.predicate_review,
                       unowned_judged=a.unowned_judged, predicate_bump=a.predicate_bump,
                       checklist_version=a.checklist_version, by=a.by, note=a.note)
        print("appended:", json.dumps(rec, ensure_ascii=False))
        if rec["thin"]:
            print("\n[!] thin=true: no diff, no predicate review, no unowned judgement — "
                  "suspiciously cheap. A real survey almost always touches one of these. "
                  "This attestation is itself an object worth illuminating.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

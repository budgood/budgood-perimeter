# -*- coding: utf-8 -*-
"""Survey: the mechanical scaffold under the one irreducible live act.

scan()   -> mechanical diff (born/died/changed) of live channels vs manifest
attest() -> append an attestation; flags `thin` when nothing was found AND nothing judged
status() -> honest dashboard data; NEVER claims completeness, only freshness

The judgement segment (re-examine the predicate; judge each unowned boundary) is NOT here.
It is the human/agent live act the checklist scaffolds. This module only makes that act
cheap, recorded, and impossible to forget.
"""
from __future__ import annotations
import datetime as _dt
from . import manifest as M
from . import scan as S


def _today():
    return _dt.date.today().isoformat()


def scan(cfg) -> dict:
    by_type = M.load(cfg.manifest_path)
    pred = M.active_predicate(by_type)
    registered = {r.get("path"): r for r in by_type.get("channel", [])}
    live = S.live_accessors(cfg.project_root, pred) if pred else set()
    pred_v = pred.get("version") if pred else None
    born = sorted(f for f in live if f not in registered)
    died = sorted(p for p, r in registered.items()
                  if p not in live and r.get("found_under_predicate") != "manual")
    changed = sorted(p for p, r in registered.items()
                     if p in live and r.get("found_under_predicate") != pred_v)
    return {"predicate_version": pred_v, "born": born, "died": died, "changed": changed,
            "live_count": len(live), "registered_count": len(registered)}


def attest(cfg, predicate_review="", unowned_judged="", predicate_bump="",
           checklist_version="v1", by="", note="") -> dict:
    d = scan(cfg)
    diff_empty = not (d["born"] or d["died"] or d["changed"])
    pr = (predicate_review or "").strip()
    uj = (unowned_judged or "").strip()
    thin = diff_empty and not pr and not uj          # integrity guard: an empty survey is suspect
    rec = {
        "type": "perimeter_attestation",
        "date": _today(),
        "by": by or "unspecified-actor",
        "channel_diff": {"born": d["born"], "died": d["died"], "changed": d["changed"]},
        "predicate_review": pr or ("falsification attempted; no gap" if not diff_empty else ""),
        "predicate_version_after": predicate_bump or d["predicate_version"],
        "unowned_judgments": uj,
        "checklist_version_after": checklist_version,
        "thin": thin,
        "note": note or "",
    }
    M.append(cfg.attest_path, rec)
    return rec


def status(cfg) -> dict:
    by_type = M.load(cfg.manifest_path)
    atts = M.read_jsonl(cfg.attest_path)
    last = atts[-1] if atts else None
    pred = M.active_predicate(by_type)
    age = None
    if last and last.get("date"):
        try:
            age = max((_dt.date.today() - _dt.date.fromisoformat(last["date"])).days, 0)
        except Exception:
            age = None
    return {
        "last_attested": last.get("date") if last else None,
        "age_days": age,
        "stale": (age is not None and age > cfg.stale_days),
        "predicate_version": (last.get("predicate_version_after") if last
                              else (pred.get("version") if pred else None)),
        "last_thin": last.get("thin") if last else None,
        "owned": sum(1 for r in by_type.get("channel", []) if r.get("ownership") == "owned"),
        "unowned_watched": len(by_type.get("unowned", [])),
    }


def label_report(cfg) -> dict:
    """Label-preservation view of the value-at-boundary locus.

    Partitions registered channels by how they carry the store's epistemic grade:
      leak       — label_preserving is False  (returns store records WITHOUT their grade)
      transform  — label_preserving is a str  (e.g. "flatten-D": stamps one grade on all)
      preserving — label_preserving is True
      undeclared — field missing/None  (a reader that has not been judged)

    Readers that leak or are undeclared are the hazard: the engine only LISTS them
    (illuminate, not control); fixing = taint/signature at that channel, a live act.
    """
    bt = M.load(cfg.manifest_path)
    out = {"leak": [], "transform": [], "preserving": [], "undeclared": []}
    for c in bt.get("channel", []):
        lp = c.get("label_preserving")
        is_reader = c.get("role") in ("reader", None)
        if lp is True:
            out["preserving"].append(c)
        elif lp is False:
            out["leak"].append(c)
        elif isinstance(lp, str) and lp:
            out["transform"].append(c)
        elif is_reader:
            out["undeclared"].append(c)
    return out

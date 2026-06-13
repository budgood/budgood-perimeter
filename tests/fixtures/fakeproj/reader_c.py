# a registered reader that returns store rows WITHOUT their grade -> a label leak
def get():
    rows = open_store()       # matches predicate
    return [r["label"] for r in rows]   # drops everything except the bare value

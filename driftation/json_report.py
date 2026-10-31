"""Step 7 (machine-readable): write the findings as JSON for scripts and evaluation."""
import json

VERSION = "0.1.0"


def make_json(findings, changes, meta):
    """Build the JSON report. `meta` has "model", "base" and "head" (any may be None)."""
    ids = {id(c): f"C{n}" for n, c in enumerate(changes, start=1)}
    shown = [f for f in findings if f["review"]["verdict"] != "still_correct"]
    dismissed = [f for f in findings if f["review"]["verdict"] == "still_correct"]
    report = {
        "tool": "driftation",
        "version": VERSION,
        **meta,
        "summary": {
            "code_changes": len(changes),
            "findings": len(shown),
            "dismissed_by_gemma": len(dismissed),
        },
        "code_changes": [_change(c, ids[id(c)]) for c in changes],
        "findings": [_finding(f, ids) for f in shown],
        "dismissed": [_finding(f, ids) for f in dismissed],
    }
    return json.dumps(report, indent=2, ensure_ascii=False)


def _change(c, change_id):
    return {
        "id": change_id,
        "type": c["type"],
        "kind": c["kind"],
        "old": {"name": c["old_name"], "value": c["old_value"], "file": c["file"], "line": c["old_line"]},
        "new": None if c["type"] == "removed" else {
            "name": c["new_name"] or c["old_name"], "value": c["new_value"], "file": c["file"], "line": c["new_line"],
        },
        "commit": c["commit"],
    }


def _finding(f, ids):
    return {
        "doc": {"file": f["doc"], "line": f["line"], "sentence": f["sentence"]},
        "cause": ids[id(f["change"])],
        "matched": f["matched"],
        "link": "direct" if f["direct"] else "indirect",
        "evidence": f["evidence"],
        "verdict": f["review"]["verdict"],
        "explanation": f["review"]["explanation"],
        "suggested_fix": f["review"]["suggested_fix"],
    }

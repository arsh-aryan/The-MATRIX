import json

from driftation.json_report import make_json

CHANGE = {
    "type": "renamed", "kind": "flag", "file": "cli.py",
    "old_name": "--max-retries", "new_name": "--retries",
    "old_value": "3", "new_value": "3", "old_line": 4, "new_line": 4, "commit": "abc1234",
}


def finding(verdict):
    return {
        "doc": "README.md", "line": 3, "sentence": "Use --max-retries.", "matched": "--max-retries",
        "direct": True, "evidence": ["flag:--max-retries", "doc:README.md:3"], "change": CHANGE,
        "review": {"verdict": verdict, "explanation": "why", "suggested_fix": "Use --retries."},
    }


def test_json_report_shape():
    data = json.loads(make_json([finding("outdated"), finding("still_correct")], [CHANGE],
                                {"model": "gemma4:e4b", "base": "main", "head": "HEAD"}))
    assert data["summary"] == {"code_changes": 1, "findings": 1, "dismissed_by_gemma": 1}
    [change] = data["code_changes"]
    assert change["id"] == "C1"
    assert change["old"] == {"name": "--max-retries", "value": "3", "file": "cli.py", "line": 4}
    assert change["new"]["name"] == "--retries"
    [f] = data["findings"]
    assert f["doc"] == {"file": "README.md", "line": 3, "sentence": "Use --max-retries."}
    assert (f["cause"], f["link"], f["verdict"]) == ("C1", "direct", "outdated")
    assert len(data["dismissed"]) == 1


def test_removed_change_has_no_new_side():
    removed = dict(CHANGE, type="removed", new_name=None, new_value=None, new_line=None)
    data = json.loads(make_json([], [removed], {"model": None, "base": None, "head": None}))
    assert data["code_changes"][0]["new"] is None

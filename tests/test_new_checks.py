"""Signature changes, behaviour changes, docstrings and config tables."""
from pathlib import Path

from driftation.__main__ import main
from driftation.changes import behavior_changes, compare, signature_changes
from driftation.code_graph import extract
from driftation.docs import docstring_sentences
from driftation.drift import _shows_old_call

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "config-and-api"


def symbols(code):
    return extract(code)[0]


def test_new_required_argument_is_a_signature_change():
    old, new = symbols("def create_note(title):\n    pass\n"), symbols("def create_note(title, owner):\n    pass\n")
    [change] = signature_changes("app.py", old, new)
    assert (change["old_value"], change["new_value"]) == ("create_note(title)", "create_note(title, owner)")


def test_new_optional_argument_is_not_a_signature_change():
    old, new = symbols("def f(a):\n    pass\n"), symbols("def f(a, b=1):\n    pass\n")
    assert signature_changes("app.py", old, new) == []


def test_only_calls_with_too_few_arguments_count():
    assert _shows_old_call("Call create_note(title) to add.", "create_note", "create_note(title, owner)")
    assert not _shows_old_call("Call create_note(title, owner).", "create_note", "create_note(title, owner)")


def test_behaviour_change_ignores_docstring_edits():
    old = symbols('def f(x):\n    """Old text."""\n    return x\n')
    new = symbols('def f(x):\n    """New text."""\n    return x\n')
    assert behavior_changes("a.py", old, new, []) == []
    changed = symbols('def f(x):\n    return -x\n')
    [change] = behavior_changes("a.py", old, changed, compare("a.py", old, changed))
    assert change["type"] == "behavior_changed" and "return -x" in change["new_code"]


def test_docstring_sentences_have_real_line_numbers():
    code = 'def f():\n    """First line.\n\n    Returns 20 items.\n    """\n'
    assert list(docstring_sentences(code)) == [(2, "First line."), (4, "Returns 20 items.")]


def test_config_and_api_example(tmp_path):
    out = tmp_path / "report.md"
    main(["--old", str(EXAMPLE / "before"), "--repo", str(EXAMPLE / "after"), "--no-llm", "--output", str(out)])
    report = out.read_text()
    for sentence in [
        "| `server.port` | 8080 | Port the server listens on |",   # config table, changed value
        "| `storage.path` | ./notes.db | Where notes are stored |",  # renamed config key
        "Call create_note(title) to add a note.",                   # new required argument
        "`search(notes, query)` returns up to 20 notes per page.",  # changed default, via the graph
        "Returns at most `page_size` notes (default 20).",          # docstring
    ]:
        assert sentence in report
        assert sentence in (EXAMPLE / "report.md").read_text()  # the saved Gemma report agrees
    assert "server.debug" not in report.split("## 1.")[1]  # unchanged setting not reported
    # The behaviour change needs Gemma, so it is only in the saved Gemma report
    assert "list_notes(notes) returns notes" in (EXAMPLE / "report.md").read_text()

from driftation.changes import compare, find_changes
from driftation.code_graph import extract
from driftation.diff_parser import parse_diff_with_lines


def changes_between(old_code, new_code):
    return compare("app.py", extract(old_code)[0], extract(new_code)[0])


def test_value_changed():
    [change] = changes_between("TIMEOUT = 30\n", "TIMEOUT = 60\n")
    assert change["type"] == "value_changed"
    assert (change["old_value"], change["new_value"]) == ("30", "60")


def test_renamed_flag():
    old = 'p.add_argument("--max-retries", default=3)\n'
    new = 'p.add_argument("--retries", default=3)\n'
    [change] = changes_between(old, new)
    assert change["type"] == "renamed"
    assert (change["old_name"], change["new_name"]) == ("--max-retries", "--retries")


def test_removed_function_reports_function_only():
    [change] = changes_between("def legacy(a, b=1):\n    pass\n", "")
    assert (change["type"], change["kind"], change["old_name"]) == ("removed", "function", "legacy")


def test_renamed_function_does_not_report_its_params():
    [change] = changes_between("def fetch(timeout=5):\n    pass\n", "def fetch_data(timeout=5):\n    pass\n")
    assert (change["type"], change["new_name"]) == ("renamed", "fetch_data")


def test_new_items_are_ignored():
    assert changes_between("", "NEW_SETTING = 1\n") == []


def test_saved_diff_without_git():
    diff = parse_diff_with_lines("""--- a/cli.py
+++ b/cli.py
@@ -4 +4 @@
-parser.add_argument("--max-retries", default=3,
+parser.add_argument("--retries", default=3,
""")
    [change] = find_changes(diff)
    assert (change["old_name"], change["new_name"], change["old_line"]) == ("--max-retries", "--retries", 4)

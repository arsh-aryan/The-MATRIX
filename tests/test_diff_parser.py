from driftation.diff_parser import parse_diff

SAMPLE = """--- a/app.py
+++ b/app.py
@@ -1,2 +1,2 @@
-TIMEOUT = 30
+TIMEOUT = 60
 print("hi")
"""


def test_parse_diff_finds_changed_lines():
    result = parse_diff(SAMPLE)
    assert result["app.py"]["removed"] == ["TIMEOUT = 30"]
    assert result["app.py"]["added"] == ["TIMEOUT = 60"]


def test_two_files():
    diff = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-RETRIES = 3
+RETRIES = 5
diff --git a/cli.py b/cli.py
--- a/cli.py
+++ b/cli.py
@@ -1 +1 @@
-parser.add_argument("--max-retries")
+parser.add_argument("--retries")
"""
    result = parse_diff(diff)
    assert result["app.py"] == {"removed": ["RETRIES = 3"], "added": ["RETRIES = 5"]}
    assert result["cli.py"]["added"] == ['parser.add_argument("--retries")']


def test_deleted_file_keeps_its_name():
    diff = """diff --git a/old.py b/old.py
deleted file mode 100644
--- a/old.py
+++ /dev/null
@@ -1,2 +0,0 @@
-def legacy():
-    pass
"""
    result = parse_diff(diff)
    assert "/dev/null" not in result
    assert result["old.py"]["removed"] == ["def legacy():", "    pass"]


def test_removed_line_that_looks_like_a_header():
    # Removing "-- note" shows up as "--- note" inside the hunk
    diff = """diff --git a/schema.sql b/schema.sql
--- a/schema.sql
+++ b/schema.sql
@@ -1,2 +1,1 @@
--- note
 SELECT 1;
"""
    result = parse_diff(diff)
    assert result["schema.sql"]["removed"] == ["-- note"]


def test_no_newline_marker_is_ignored():
    diff = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-DEBUG = False
\\ No newline at end of file
+DEBUG = True
\\ No newline at end of file
"""
    result = parse_diff(diff)
    assert result["app.py"] == {"removed": ["DEBUG = False"], "added": ["DEBUG = True"]}


def test_line_numbers():
    from driftation.diff_parser import parse_diff_with_lines

    result = parse_diff_with_lines(SAMPLE)
    assert result["app.py"]["removed"] == [(1, "TIMEOUT = 30")]
    assert result["app.py"]["added"] == [(1, "TIMEOUT = 60")]

"""Unusual input: wrong names, missing files, empty changes, odd file types."""
import subprocess

from driftation.__main__ import main
from driftation.diff_parser import parse_diff_with_lines
from driftation.changes import find_changes


def git(repo, *args):
    subprocess.run(["git", "-c", "user.name=T", "-c", "user.email=t@example.com", *args],
                   cwd=repo, check=True, capture_output=True)


def make_repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "app.py").write_text("TIMEOUT = 30\n")
    (tmp_path / "README.md").write_text("Timeout is 30.\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "first")
    return tmp_path


def test_wrong_branch_name_gives_one_clear_line(tmp_path, capsys):
    repo = make_repo(tmp_path)
    assert main(["--repo", str(repo), "--base", "mian", "--no-llm"]) == 2
    assert "branch or commit 'mian' not found. Check --base." in capsys.readouterr().err


def test_not_a_git_repo(tmp_path, capsys):
    assert main(["--repo", str(tmp_path), "--no-llm"]) == 2
    assert "is not a git repository" in capsys.readouterr().err


def test_missing_folder_and_diff_file(tmp_path, capsys):
    assert main(["--repo", str(tmp_path / "nope"), "--no-llm"]) == 2
    assert main(["--repo", str(tmp_path), "--diff", str(tmp_path / "x.diff"), "--no-llm"]) == 2
    assert main(["--repo", str(tmp_path), "--old", str(tmp_path / "old"), "--no-llm"]) == 2
    err = capsys.readouterr().err
    assert "folder not found" in err and "diff file not found" in err


def test_no_changes_at_all(tmp_path):
    repo = make_repo(tmp_path)
    out = tmp_path / "r.md"
    assert main(["--repo", str(repo), "--base", "main", "--head", "main", "--no-llm", "--output", str(out)]) == 0
    assert "No outdated documentation found" in out.read_text()


def test_only_non_code_files_changed():
    diff = parse_diff_with_lines("""diff --git a/logo.png b/logo.png
Binary files a/logo.png and b/logo.png differ
diff --git a/notes.txt b/notes.txt
--- a/notes.txt
+++ b/notes.txt
@@ -1 +1 @@
-old
+new
""")
    assert find_changes(diff) == []


def test_empty_diff_text():
    assert parse_diff_with_lines("") == {}

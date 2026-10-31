"""Runs the whole tool on a tiny git repo with a real pull-request-like branch."""
import subprocess

from driftation.__main__ import main

CLI_BEFORE = '''import argparse

DEFAULT_TIMEOUT = 30

parser = argparse.ArgumentParser()
parser.add_argument("--max-retries", default=3)
parser.add_argument("--timeout", default=DEFAULT_TIMEOUT)


def legacy_export(path):
    pass
'''

CLI_AFTER = '''import argparse

DEFAULT_TIMEOUT = 60

parser = argparse.ArgumentParser()
parser.add_argument("--retries", default=3)
parser.add_argument("--timeout", default=DEFAULT_TIMEOUT)
'''

README = """# Tool

Run `tool --max-retries 5` to retry more often.
The --timeout flag defaults to 30 seconds.
Call legacy_export() to save results.
Use --timeout to wait longer.
Old notes mention max retries here too.
"""


def git(repo, *args):
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", *args],
        cwd=repo, check=True, capture_output=True,
    )


def make_repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "cli.py").write_text(CLI_BEFORE)
    (tmp_path / "README.md").write_text(README)
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "first")
    git(tmp_path, "checkout", "-q", "-b", "feature")
    (tmp_path / "cli.py").write_text(CLI_AFTER)
    # The PR already fixed the last README line, so it must not be reported
    (tmp_path / "README.md").write_text(README.replace("Old notes mention max retries here too.", "Old notes."))
    git(tmp_path, "commit", "-q", "-am", "rename flag, raise timeout, drop legacy_export")
    return tmp_path


def run(tmp_path, *extra):
    out = tmp_path / "report.md"
    assert main(["--repo", str(tmp_path), "--base", "main", "--head", "feature", "--no-llm", "--output", str(out), *extra]) == 0
    return out.read_text()


def test_finds_all_three_kinds_of_drift(tmp_path):
    report = run(make_repo(tmp_path))
    assert "Run `tool --max-retries 5` to retry more often." in report  # renamed flag
    assert "The --timeout flag defaults to 30 seconds." in report      # changed default, via the graph
    assert "Call legacy_export() to save results." in report           # removed function
    assert "indirect link" in report
    assert "`--max-retries = 3` → `--retries = 3`" in report
    assert "`DEFAULT_TIMEOUT = 30` → `DEFAULT_TIMEOUT = 60`" in report


def test_no_false_alarms(tmp_path):
    report = run(make_repo(tmp_path))
    assert "Use --timeout to wait longer." not in report  # still true
    assert "Old notes" not in report                        # already fixed in the PR


def test_saved_diff_mode(tmp_path):
    repo = make_repo(tmp_path)
    diff = subprocess.run(["git", "diff", "main...feature"], cwd=repo, capture_output=True, text=True).stdout
    (repo / "pr.diff").write_text(diff)
    out = repo / "report.md"
    main(["--repo", str(repo), "--diff", str(repo / "pr.diff"), "--no-llm", "--output", str(out)])
    assert "Run `tool --max-retries 5` to retry more often." in out.read_text()

"""Step 0: get the diff and read project files, either from git or from a folder."""
import difflib
import os
import subprocess

# Folders we never read
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "build", "dist"}


def run_git(repo, *args):
    """Run a git command in `repo` and return its output as text."""
    result = subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, text=True, check=True
    )
    return result.stdout


class GitTree:
    """Files as they are at one git commit (e.g. the base or head of a PR)."""

    def __init__(self, repo, ref):
        self.repo = repo
        self.ref = ref

    def list_files(self):
        out = run_git(self.repo, "ls-tree", "-r", "--name-only", self.ref)
        return [p for p in out.splitlines() if not set(p.split("/")) & SKIP_DIRS]

    def read(self, path):
        """Return the file's text, or None if it does not exist at this commit."""
        try:
            return run_git(self.repo, "show", f"{self.ref}:{path}")
        except (subprocess.CalledProcessError, UnicodeDecodeError):
            return None


class Folder:
    """Files as they are on disk (used with --diff, when there is no git history)."""

    def __init__(self, root):
        self.root = root

    def list_files(self):
        files = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                full = os.path.join(dirpath, name)
                files.append(os.path.relpath(full, self.root).replace(os.sep, "/"))
        return files

    def read(self, path):
        try:
            with open(os.path.join(self.root, path), encoding="utf-8") as f:
                return f.read()
        except (OSError, UnicodeDecodeError):
            return None


def is_git_repo(repo):
    """True if `repo` is inside a git repository."""
    return subprocess.run(["git", "-C", repo, "rev-parse", "--git-dir"], capture_output=True).returncode == 0


def ref_exists(repo, ref):
    """True if `ref` (a branch, tag or commit like abc123^) exists in the repository."""
    result = subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
                            capture_output=True)
    return result.returncode == 0


def merge_base(repo, base, head):
    """The commit where the PR branch started (what "base...head" compares against)."""
    return run_git(repo, "merge-base", base, head).strip()


def git_diff(repo, base, head):
    """The PR diff, same as `git diff base...head`."""
    return run_git(repo, "diff", f"{base}...{head}")


def folder_diff(old_root, new_root):
    """A unified diff between two folders (like `git diff`), for --old without git."""
    old, new = Folder(old_root), Folder(new_root)
    chunks = []
    for path in sorted(set(old.list_files()) | set(new.list_files())):
        before, after = old.read(path), new.read(path)
        if before == after:
            continue
        lines = difflib.unified_diff(
            (before or "").splitlines(), (after or "").splitlines(),
            f"a/{path}" if before is not None else "/dev/null",
            f"b/{path}" if after is not None else "/dev/null",
            lineterm="",
        )
        chunks.append(f"diff --git a/{path} b/{path}\n" + "\n".join(lines))
    return "\n".join(chunks) + "\n"


def commit_for(repo, base, head, path, new_line=None):
    """Short hash of the commit responsible for a change.

    If we know the new line number, `git blame` gives the exact commit.
    Otherwise (e.g. the line was deleted) use the last PR commit that touched the file.
    """
    if repo is None:
        return None
    try:
        if new_line:
            out = run_git(repo, "blame", "--porcelain", "-L", f"{new_line},{new_line}", head, "--", path)
            return out.split()[0][:7]
        out = run_git(repo, "log", "-1", "--format=%h", f"{base}..{head}", "--", path)
        return out.strip() or None
    except subprocess.CalledProcessError:
        return None

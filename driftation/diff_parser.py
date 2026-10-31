import re

# Matches a hunk header like "@@ -10,3 +10,4 @@" (a missing count means 1)
HUNK_RE = re.compile(r"^@@ -\d+(?:,(\d+))? \+\d+(?:,(\d+))? @@")


def parse_diff(diff_text):
    """Return {filename: {"removed": [...], "added": [...]}} from a unified git diff."""
    changes = {}
    current = None        # changes dict for the file being read
    named_by_git = False  # True if "diff --git" already gave us the file name
    old_path = None       # name from the "--- " line
    old_left = 0          # old-side lines still to read in this hunk
    new_left = 0          # new-side lines still to read in this hunk

    for line in diff_text.splitlines():
        # Inside a hunk, the "@@" counts tell us how many lines belong to it,
        # so a removed line like "-- note" (shown as "--- note") is not a file header.
        if old_left > 0 or new_left > 0:
            if line.startswith("-"):
                current["removed"].append(line[1:])
                old_left -= 1
            elif line.startswith("+"):
                current["added"].append(line[1:])
                new_left -= 1
            elif line.startswith("\\"):
                pass  # "\ No newline at end of file"
            else:
                old_left -= 1  # unchanged line counts on both sides
                new_left -= 1
            continue

        if line.startswith("diff --git "):
            # "diff --git a/app.py b/app.py" -> "app.py"
            current = _file(changes, line.split(" b/", 1)[-1])
            named_by_git = True
        elif line.startswith("--- "):
            old_path = _strip_prefix(line[4:])
        elif line.startswith("+++ "):
            if not named_by_git:
                # Plain diff without "diff --git"; a deleted file has "+++ /dev/null"
                new_path = _strip_prefix(line[4:])
                current = _file(changes, old_path if new_path == "/dev/null" else new_path)
            named_by_git = False
        elif line.startswith("@@") and current is not None:
            match = HUNK_RE.match(line)
            if match:
                old_left = int(match.group(1) or 1)
                new_left = int(match.group(2) or 1)
    return changes


def _file(changes, path):
    """Get (or create) the entry for one file."""
    return changes.setdefault(path, {"removed": [], "added": []})


def _strip_prefix(path):
    """Turn "a/app.py" or "b/app.py" into "app.py"."""
    path = path.strip().split("\t")[0]
    if path.startswith(("a/", "b/")):
        return path[2:]
    return path

"""Step 3: turn the diff into a list of meaningful code changes.

Each change is a dict:
  type:      "renamed", "removed", "value_changed", "signature_changed" or "behavior_changed"
  kind:      "function", "class", "constant", "flag", "param" or "setting" (config files)
  file, old_name, new_name, old_value, new_value, old_line, new_line, commit
  (behavior_changed also has old_code and new_code, so Gemma can compare them)
New items that did not exist before are ignored: they cannot make old docs wrong.
"""
import ast
import difflib

from .code_graph import extract
from .config_files import extract_config, is_config, settings_from_lines


def find_changes(diff, old_tree=None, new_tree=None, behavior=False):
    """`diff` comes from parse_diff_with_lines. Trees are used when we have both versions.

    behavior=True also reports functions whose code changed without any rename
    (only useful with Gemma, which reads the old and new code).
    """
    changes = []
    full = old_tree is not None and new_tree is not None
    for path, lines in diff.items():
        if path.endswith(".py"):
            if full:
                # Best case: compare the whole old file with the whole new file
                old, _ = extract(old_tree.read(path) or "")
                new, _ = extract(new_tree.read(path) or "")
            else:
                # Only a saved diff: look at the changed lines one by one
                old = symbols_from_lines(lines["removed"])
                new = symbols_from_lines(lines["added"])
        elif is_config(path):
            if full:
                old = extract_config(path, old_tree.read(path) or "")
                new = extract_config(path, new_tree.read(path) or "")
            else:
                old = settings_from_lines(lines["removed"])
                new = settings_from_lines(lines["added"])
        else:
            continue
        found = compare(path, old, new)
        if path.endswith(".py"):
            found += signature_changes(path, old, new)
            if behavior and full:
                found += behavior_changes(path, old, new, found)
        changes += found
    return changes


def compare(path, old, new):
    """Compare two symbol tables (from code_graph.extract or config_files.extract_config)."""
    changes = []
    removed = [key for key in old if key not in new]
    added = [key for key in new if key not in old]

    # Same name, different value: e.g. TIMEOUT = 30 -> TIMEOUT = 60
    for key in old:
        if key in new and old[key]["value"] != new[key]["value"]:
            changes.append(_change("value_changed", path, key, key, old, new))

    # A removed item and an added item of the same kind with a similar name is a rename
    for old_key in removed:
        candidates = [k for k in added if k[0] == old_key[0]]
        best = max(candidates, key=lambda k: _similarity(old_key, k, old, new), default=None)
        if best and _similarity(old_key, best, old, new) >= 0.5:
            added.remove(best)
            if old_key[0] == "param" and _arg(old_key) == _arg(best):
                continue  # same param, its function was renamed (reported separately)
            changes.append(_change("renamed", path, old_key, best, old, new))
        elif not _owner_removed(old_key, old, new):
            changes.append(_change("removed", path, old_key, None, old, new))
    return changes


def signature_changes(path, old, new):
    """A function that now needs an extra argument: old calls like fetch(city) break."""
    changes = []
    for key in old:
        if key[0] != "function" or key not in new:
            continue
        old_args, new_args = _required(old, key[1]), _required(new, key[1])
        if [a for a in new_args if a not in old_args]:
            change = _change("signature_changed", path, key, key, old, new)
            change["old_value"] = f"{key[1]}({', '.join(old_args)})"
            change["new_value"] = f"{key[1]}({', '.join(new_args)})"
            changes.append(change)
    return changes


def behavior_changes(path, old, new, already):
    """Functions whose code changed while their name, params and defaults did not."""
    touched = {c["old_name"].split(".")[0] for c in already if c["kind"] in ("function", "param")}
    changes = []
    for key in old:
        if key[0] != "function" or key not in new or key[1] in touched:
            continue
        if old[key].get("body") != new[key].get("body"):
            change = _change("behavior_changed", path, key, key, old, new)
            change["old_code"] = old[key].get("code", "")
            change["new_code"] = new[key].get("code", "")
            changes.append(change)
    return changes


def symbols_from_lines(numbered_lines):
    """Run code_graph.extract on single diff lines, keeping their real line numbers."""
    symbols = {}
    for number, text in numbered_lines:
        code = text.strip()
        # Also try closing an unfinished line, e.g. 'add_argument("--x", default=3,'
        for attempt in (code, code + " pass", code.rstrip(","), code.rstrip(",") + ")"):
            try:
                ast.parse(attempt)
            except SyntaxError:
                continue
            found, _ = extract(attempt)
            for key, info in found.items():
                symbols[key] = {"value": info["value"], "line": number}
            break
    return symbols


def _change(change_type, path, old_key, new_key, old, new):
    return {
        "type": change_type,
        "kind": old_key[0],
        "file": path,
        "old_name": old_key[1],
        "new_name": new_key[1] if new_key else None,
        "old_value": old[old_key]["value"],
        "new_value": new[new_key]["value"] if new_key else None,
        "old_line": old[old_key]["line"],
        "new_line": new[new_key]["line"] if new_key else None,
        "commit": None,
    }


def _required(symbols, func):
    """Names of the parameters of `func` that have no default, in order."""
    prefix = func + "."
    return [
        key[1][len(prefix):] for key, info in symbols.items()
        if key[0] == "param" and key[1].startswith(prefix) and info["value"] is None
    ]


def _similarity(old_key, new_key, old, new):
    """0..1 score: how likely new_key is the renamed version of old_key."""
    score = difflib.SequenceMatcher(None, _arg(old_key), _arg(new_key)).ratio()
    if old[old_key]["value"] is not None and old[old_key]["value"] == new[new_key]["value"]:
        score += 0.3  # same value is a strong hint of a rename
    return score


def _arg(key):
    """Short name: "fetch.timeout" -> "timeout", "--max-retries" -> "max-retries"."""
    return key[1].split(".")[-1].lstrip("-")


def _owner_removed(key, old, new):
    """A param whose whole function was removed is covered by the function's change."""
    if key[0] != "param":
        return False
    func = ("function", key[1].split(".")[0])
    return func in old and func not in new

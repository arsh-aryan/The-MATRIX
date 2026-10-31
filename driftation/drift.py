"""Steps 4 and 5: walk the graph from each change to doc sentences, then drop false alarms."""
import re

from .code_graph import display_name, node_id, walk
from .docs import contains_value, mentions


def find_drift(changes, graph, doc_sentences, edited_doc_lines):
    """Return a list of findings (one per outdated-looking doc sentence).

    graph:            code graph of the NEW code (code_graph.build_graph)
    doc_sentences:    [(path, line, sentence)] from the NEW docs and docstrings
    edited_doc_lines: {(path, line)} doc lines this PR already changed
    """
    findings = []
    seen = set()
    for change in changes:
        start = node_id(change["kind"], change["old_name"])

        # Filter: a renamed/removed name that still exists in the new code is still valid
        if change["type"] in ("renamed", "removed") and start in graph:
            continue

        # Signature and behaviour changes only affect docs that name the function itself
        only_direct = change["type"] in ("signature_changed", "behavior_changed")
        reach = {start: [start]} if only_direct else walk(graph, start)

        for node, path in reach.items():
            kind, name = node.split(":", 1)
            direct = node == start
            for doc, line, sentence in doc_sentences:
                term = _mention(sentence, kind, name)
                if not term:
                    continue
                # Filter: the PR already updated this doc line
                if (doc, line) in edited_doc_lines:
                    continue
                # A value change only matters if the doc states the old value,
                # and an indirect link (via another code item) needs that proof too
                if (change["type"] == "value_changed" or not direct) and not contains_value(
                    sentence, change["old_value"]
                ):
                    continue
                # A new required argument only breaks docs that show a call, e.g. fetch(city)
                if change["type"] == "signature_changed" and not _shows_old_call(
                    sentence, name, change["new_value"]
                ):
                    continue
                key = (doc, line, sentence, start)
                if key in seen:
                    continue
                seen.add(key)
                findings.append({
                    "doc": doc,
                    "line": line,
                    "sentence": sentence,
                    "matched": term,
                    "direct": direct,
                    "evidence": path + [f"doc:{doc}:{line}"],
                    "change": change,
                })
    # Direct mentions first, then by file and line
    findings.sort(key=lambda f: (not f["direct"], f["doc"], f["line"]))
    return findings


def _mention(sentence, kind, name):
    """Find the item in the sentence; a config key "server.port" may also be written "port"."""
    names = [display_name(kind, name)]
    if kind == "setting" and "." in name:
        names.append(name.split(".")[-1])
    for candidate in names:
        term = mentions(sentence, candidate)
        if term:
            return term
    return None


def _shows_old_call(sentence, func, new_signature):
    """True if the sentence shows a call to `func` with fewer arguments than it now needs."""
    needed = _count_args(new_signature[new_signature.index("(") + 1:-1])
    for match in re.finditer(r"(?<![\w.])" + re.escape(func) + r"\s*\(([^)]*)\)", sentence):
        if _count_args(match.group(1)) < needed:
            return True
    return False


def _count_args(text):
    return len([part for part in text.split(",") if part.strip()])

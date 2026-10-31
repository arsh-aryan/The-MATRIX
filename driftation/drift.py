"""Steps 4 and 5: walk the graph from each change to doc sentences, then drop false alarms."""
from .code_graph import display_name, node_id, walk
from .docs import contains_value, mentions


def find_drift(changes, graph, doc_sentences, edited_doc_lines):
    """Return a list of findings (one per outdated-looking doc sentence).

    graph:            code graph of the NEW code (code_graph.build_graph)
    doc_sentences:    [(path, line, sentence)] from the NEW docs
    edited_doc_lines: {(path, line)} doc lines this PR already changed
    """
    findings = []
    seen = set()
    for change in changes:
        start = node_id(change["kind"], change["old_name"])

        # Filter: a renamed/removed name that still exists in the new code is still valid
        if change["type"] in ("renamed", "removed") and start in graph:
            continue

        for node, path in walk(graph, start).items():
            kind, name = node.split(":", 1)
            direct = node == start
            for doc, line, sentence in doc_sentences:
                term = mentions(sentence, display_name(kind, name))
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

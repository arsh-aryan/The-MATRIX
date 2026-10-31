"""Command line entry point: python -m driftation --base main"""
import argparse
import sys

from .changes import find_changes
from .code_graph import build_graph
from .diff_parser import parse_diff_with_lines
from .docs import load_sentences
from .drift import find_drift
from .gemma import review
from .git_input import Folder, GitTree, commit_for, git_diff, merge_base
from .json_report import make_json
from .report import make_report


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="driftation", description="Find documentation made outdated by a pull request's code changes."
    )
    parser.add_argument("--base", default="main", help="branch or commit the PR is based on (default: main)")
    parser.add_argument("--head", default="HEAD", help="branch or commit with the changes (default: HEAD)")
    parser.add_argument("--diff", help="read a saved diff file instead of running git")
    parser.add_argument("--repo", default=".", help="project folder (default: current folder)")
    parser.add_argument("--no-llm", action="store_true", help="skip the Gemma review")
    parser.add_argument("--model", default="gemma4:e4b", help="Ollama model (default: gemma4:e4b)")
    parser.add_argument("--output", help="write the Markdown report to this file")
    parser.add_argument("--json", help="also write a JSON report to this file")
    args = parser.parse_args(argv)

    # Step 0: input
    if args.diff:
        with open(args.diff, encoding="utf-8") as f:
            diff_text = f.read()
        old_tree, new_tree, git_repo, base = None, Folder(args.repo), None, None
    else:
        base = merge_base(args.repo, args.base, args.head)
        diff_text = git_diff(args.repo, args.base, args.head)
        old_tree, new_tree, git_repo = GitTree(args.repo, base), GitTree(args.repo, args.head), args.repo

    # Step 3: what changed in the code
    diff = parse_diff_with_lines(diff_text)
    changes = find_changes(diff, old_tree, new_tree)
    for change in changes:
        line = _changed_line(diff, change)
        change["commit"] = commit_for(git_repo, base, args.head, change["file"], line)
    _log(f"{len(changes)} code change(s) found")

    # Steps 1, 2, 4, 5: graph, docs, walk, filter
    graph = build_graph(new_tree)
    doc_sentences = load_sentences(new_tree)
    edited = {(path, number) for path, lines in diff.items() for number, _ in lines["added"]}
    findings = find_drift(changes, graph, doc_sentences, edited)
    _log(f"{graph.number_of_nodes()} code items, {len(doc_sentences)} doc sentences, {len(findings)} candidate(s)")

    # Step 6: Gemma verdicts
    if findings and not args.no_llm:
        _log(f"Asking {args.model} via Ollama to review {len(findings)} candidate(s)...")
    review(findings, model=args.model, use_llm=not args.no_llm)

    # Step 7: report
    text = make_report(findings, changes)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        _log(f"Report written to {args.output}")
    else:
        print(text)
    if args.json:
        meta = {
            "model": None if args.no_llm else args.model,
            "base": None if args.diff else args.base,
            "head": None if args.diff else args.head,
        }
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(make_json(findings, changes, meta) + "\n")
        _log(f"JSON report written to {args.json}")
    return 0


def _changed_line(diff, change):
    """The added line in the diff closest to where the changed item is defined (for git blame)."""
    if not change["new_line"]:
        return None
    added = [n for n, _ in diff.get(change["file"], {}).get("added", [])]
    nearby = [n for n in added if change["new_line"] <= n <= change["new_line"] + 15]
    return min(nearby) if nearby else None


def _log(message):
    print(f"[driftation] {message}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())

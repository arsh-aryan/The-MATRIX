"""Step 7: write the findings as a Markdown report."""

ICONS = {
    "outdated": "🔴 outdated",
    "uncertain": "🟡 uncertain",
    "still_correct": "🟢 still correct",
    "unverified": "⚪ unverified",
    "not_checked": "⚪ not checked",
}


def make_report(findings, changes, title="Driftation report"):
    lines = [f"# {title}", ""]
    shown = [f for f in findings if f["review"]["verdict"] != "still_correct"]
    dismissed = [f for f in findings if f["review"]["verdict"] == "still_correct"]

    lines.append(
        f"Found **{len(changes)}** code change(s) and **{len(shown)}** possibly outdated "
        f"doc sentence(s)." + (f" Gemma dismissed {len(dismissed)} as still correct." if dismissed else "")
    )
    lines.append("")

    if changes:
        lines += ["## Code changes", "", "| Change | Item | Before | After | Where | Commit |", "|---|---|---|---|---|---|"]
        for c in changes:
            lines.append(
                f"| {c['type'].replace('_', ' ')} | {c['kind']} | {_code(c['old_name'], c['old_value'])} "
                f"| {_after(c)} | {_where(c)} | {c['commit'] or 'n/a'} |"
            )
        lines.append("")

    if not shown:
        lines += ["No outdated documentation found. ✅", ""]
    for number, f in enumerate(shown, start=1):
        lines += _finding(number, f)

    if dismissed:
        lines += ["## Dismissed by Gemma", ""]
        for f in dismissed:
            lines.append(f"- `{f['doc']}:{f['line']}` {f['sentence']} — {f['review']['explanation']}")
        lines.append("")
    return "\n".join(lines)


def _finding(number, f):
    c, review = f["change"], f["review"]
    out = [
        f"## {number}. `{f['doc']}` line {f['line']}",
        "",
        f"> {f['sentence']}",
        "",
        f"- **Verdict:** {ICONS.get(review['verdict'], review['verdict'])}"
        + (f" — {review['explanation']}" if review["explanation"] else ""),
        f"- **Caused by:** {c['type'].replace('_', ' ')} {c['kind']} in `{_where(c)}`"
        + (f", commit `{c['commit']}`" if c["commit"] else ""),
        f"- **What changed:** {_code(c['old_name'], c['old_value'])} → {_after(c)}",
        f"- **Evidence:** {'direct mention' if f['direct'] else 'indirect link'} of `{f['matched']}`: "
        + " → ".join(f"`{step}`" for step in f["evidence"]),
    ]
    if review["suggested_fix"]:
        out.append(f"- **Suggested fix:** {review['suggested_fix']}")
    return out + [""]


def _code(name, value):
    return f"`{name} = {value}`" if value is not None else f"`{name}`"


def _after(c):
    if c["type"] == "removed":
        return "*(removed)*"
    return _code(c["new_name"] or c["old_name"], c["new_value"])


def _where(c):
    line = c["new_line"] or c["old_line"]
    return f"{c['file']}:{line}" if line else c["file"]

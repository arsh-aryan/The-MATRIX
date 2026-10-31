"""Benchmark Driftation on real doc-drift cases from open-source history.

Each case is a code commit that made docs outdated, plus the later commit where a
human fixed those docs. We run Driftation on the code commit (before the fix
existed) and check whether it flagged the lines the human later fixed.

Usage (from the repository root):
    python benchmark/run_benchmark.py            # with Gemma (needs Ollama)
    python benchmark/run_benchmark.py --no-llm   # without Gemma

Projects are cloned (read-only) into benchmark/.repos/ on first run.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPOS = os.path.join(HERE, ".repos")


def norm(text):
    """Compare sentences loosely: ignore backticks, spacing and case."""
    return " ".join(text.replace("`", "").split()).lower()


def clone(project):
    path = os.path.join(REPOS, project.replace("/", "__"))
    if not os.path.isdir(path):
        os.makedirs(REPOS, exist_ok=True)
        subprocess.run(["git", "clone", "-q", f"https://github.com/{project}.git", path], check=True)
    return path


def run_case(case, use_llm):
    repo = clone(case["project"])
    out = os.path.join(tempfile.mkdtemp(), "report.json")
    cmd = [sys.executable, "-m", "driftation", "--repo", repo, "--base", case["code_commit"] + "^",
           "--head", case["code_commit"], "--json", out, "--output", os.devnull]
    if not use_llm:
        cmd.append("--no-llm")
    subprocess.run(cmd, check=True, capture_output=True)
    report = json.load(open(out))
    fixed = [norm(line) for line in case["fixed_lines"] if line.strip()]
    hits = [f for f in report["findings"]
            if any(norm(f["doc"]["sentence"]) in line or line in norm(f["doc"]["sentence"]) for line in fixed)]
    return {"caught": bool(hits), "hits": len(hits), "other": len(report["findings"]) - len(hits),
            "dismissed": report["summary"]["dismissed_by_gemma"]}


def main():
    use_llm = "--no-llm" not in sys.argv
    cases = json.load(open(os.path.join(HERE, "cases.json")))
    caught = 0
    print(f"{'project':<22} {'name':<18} {'result':<8} {'hits':>4} {'other':>5}")
    for case in cases:
        r = run_case(case, use_llm)
        caught += r["caught"]
        print(f"{case['project']:<22} {case['token']:<18} {'CAUGHT' if r['caught'] else 'missed':<8} "
              f"{r['hits']:>4} {r['other']:>5}")
    print(f"\nCaught {caught} of {len(cases)} real cases before the human doc fix.")


if __name__ == "__main__":
    main()

# Driftation

Driftation finds documentation that became outdated because of code changes
in a pull request, and points to the exact code change responsible.

## What it reports
For every potentially outdated sentence, Driftation shows:
- **Where the docs are wrong:** documentation file, line number, and the exact sentence
- **What caused it:** the code file, line, and commit that introduced the change
- **What changed:** the old and new name or value (e.g. `--max-retries` → `--retries`, default `3` → `5`)
- **Evidence:** the knowledge graph path linking the sentence to the changed code
- **Verdict:** outdated, still correct, or uncertain, judged by Gemma, with a suggested fix

## How it works
1. Builds a knowledge graph of the project's Python code with `ast` and `networkx`
   (functions, classes, constants, CLI flags, parameter defaults; edges for defines, calls, uses).
2. Splits documentation (`.md`, `.rst`, `.txt`) into sentences and matches code names,
   including variants like `max_retries`, `max-retries`, `--max-retries` and "max retries".
3. Reads the pull request diff and classifies each change: renamed, removed, or value changed.
4. Walks the graph up to 2 steps from each changed item to find affected sentences
   (e.g. a changed constant used as a flag's default reaches docs about that flag).
5. Filters false alarms: sentences already edited in the PR, names still used in the code,
   and value changes where the doc does not state the old value.
6. Asks gemma4:e4b, running locally via Ollama, to judge each candidate sentence.
   If Ollama is not running, results are marked "unverified" instead of crashing.

| Module | Step |
|---|---|
| `driftation/git_input.py` | read the diff and files from git (or a folder) |
| `driftation/diff_parser.py` | parse the unified diff |
| `driftation/changes.py` | classify code changes |
| `driftation/code_graph.py` | build and walk the knowledge graph |
| `driftation/docs.py` | split docs and match names |
| `driftation/drift.py` | find and filter affected sentences |
| `driftation/gemma.py` | Gemma verdicts via Ollama |
| `driftation/report.py` | Markdown report |

## Requirements
- Python 3.11+
- Ollama with gemma4:e4b (`ollama pull gemma4:e4b`); use `--model gemma4:e2b` on low-memory laptops

## Installation
```
pip install -r requirements.txt
```

## Usage
Run inside the project's git repository, on the PR branch:
```
python -m driftation --base main
```

Options:
- `--base REF` / `--head REF`: compare any two commits (default `main` and `HEAD`)
- `--diff FILE`: use a saved diff file instead of git (`--repo` is the project folder)
- `--repo PATH`: project folder (default: current folder)
- `--no-llm`: skip Gemma
- `--model NAME`: Ollama model (default `gemma4:e4b`)
- `--output FILE`: write the Markdown report to a file

## GitHub integration
`.github/workflows/driftation.yml` runs Driftation on every pull request in this repository
and shows the report on the workflow run's Summary page. GitHub's servers have no Ollama,
so this runs with `--no-llm`; run it locally to get Gemma's verdicts.

## Example
[`examples/basic`](examples/basic) has a sample project, a PR diff, and the real report
Driftation produced with gemma4:e4b (4 of 4 outdated sentences found):
```
python -m driftation --repo examples/basic/project --diff examples/basic/pr.diff
```

## Running tests
```
python -m pytest
```
Tests never need Ollama: the Gemma call is mocked.

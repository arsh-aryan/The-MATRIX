# Driftation

Driftation finds documentation that became outdated because of code changes
in a pull request, and points to the exact code change responsible.

On a real cookiecutter commit that renamed `--config` to `--config-file`, it flagged exactly the
2 doc lines a maintainer fixed 3 hours later, and Gemma's suggested fixes matched the maintainer's
word for word ([`examples/real-cookiecutter`](examples/real-cookiecutter)).

## Quick start
You need Python 3.11+ and git. Gemma is optional but recommended.

1. Install Driftation:
   ```
   pip install git+https://github.com/arsh-aryan/The-MATRIX.git
   ```
2. (Optional) Install [Ollama](https://ollama.com) and download Gemma (about 9.5 GB):
   ```
   ollama pull gemma4:e4b
   ```
3. Go to your own Python project, switch to your PR branch, and run:
   ```
   driftation --base main
   ```
4. Read the report, fix the docs it points to, and run it again.

No Ollama? Add `--no-llm` to get the findings without Gemma's verdicts.

## What it reports
For every potentially outdated sentence, Driftation shows:
- **Where the docs are wrong:** documentation file, line number, and the exact sentence
- **What caused it:** the code file, line, and commit that introduced the change
- **What changed:** the old and new name or value (e.g. `--max-retries` → `--retries`, default `3` → `5`)
- **Evidence:** the knowledge graph path linking the sentence to the changed code
- **Verdict:** outdated, still correct, or uncertain, judged by Gemma, with a suggested fix

The report is Markdown for people (`--output`) and JSON for scripts (`--json`).

## How it works
1. Builds a knowledge graph of the project's Python code with `ast` and `networkx`
   (functions, classes, constants, CLI flags, parameter defaults; edges for defines, calls, uses).
   The idea of turning code into a knowledge graph is inspired by Graphify.
2. Splits documentation (`.md`, `.rst`, `.txt`) into sentences and matches code names,
   including variants like `max_retries`, `max-retries`, `--max-retries` and "max retries".
   Plain single words (like `config`) only count when the doc writes them as code.
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
| `driftation/report.py` / `json_report.py` | Markdown and JSON reports |

## Usage
| Situation | Command |
|---|---|
| Check your PR branch against `main` | `driftation --base main` |
| Fast check without Gemma | `driftation --base main --no-llm` |
| Low-memory laptop | `driftation --base main --model gemma4:e2b` |
| Save reports | `driftation --base main --output report.md --json report.json` |
| Check any two commits | `driftation --base abc123 --head def456` |
| Only a saved diff file | `driftation --diff pr.diff --repo path/to/project` |

`python -m driftation` works the same as `driftation`.

## GitHub integration
`.github/workflows/driftation.yml` runs Driftation on every pull request in this repository
and shows the report on the workflow run's Summary page. It never posts comments.
GitHub's servers have no Ollama, so this runs with `--no-llm`; run it locally to get Gemma's verdicts.
To use it in another repository, copy that file and change the install step to
`pip install git+https://github.com/arsh-aryan/The-MATRIX.git`.

## Examples
- [`examples/real-cookiecutter`](examples/real-cookiecutter): a real drift case from cookiecutter's
  history, with the maintainer's later fix as the answer key.
- [`examples/basic`](examples/basic): a hand-made demo with all four kinds of drift
  (renamed flag, changed default, changed parameter, removed function).

Each has the input, and the real `report.md` and `report.json` produced with gemma4:e4b.

## Limitations
- Analyzes Python code only; CLI flags must be defined with argparse or click.
- Settings in config files (YAML, TOML) and docstrings are not checked yet.
- Plain single-word names in prose (e.g. "the config file") are skipped on purpose to avoid
  false alarms, so drift written only that way can be missed.
- Gemma can be wrong; its verdict is advice, and every finding shows its evidence.

## Development
```
git clone https://github.com/arsh-aryan/The-MATRIX.git
cd The-MATRIX
pip install -r requirements.txt
python -m pytest
```
Tests never need Ollama: the Gemma call is mocked.

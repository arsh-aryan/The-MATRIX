# Example: weather-cli (hand-made demo)

A small sample project we wrote to show every kind of drift in one place: a pull request that
changes its code without updating its docs. For a real-world case, see
[`../real-cookiecutter`](../real-cookiecutter).

| File | What it is |
|---|---|
| `project/` | The project **after** the PR: `cli.py` (code) and `README.md` (docs, not updated) |
| `pr.diff` | The PR's diff (`git diff main...feature`) |
| `report.md` / `report.json` | The **real** output of Driftation with gemma4:e4b running locally in Ollama |

## What the PR changed
1. Renamed the flag `--max-retries` to `--retries`
2. Raised `DEFAULT_TIMEOUT` from 30 to 60 (the default of `--timeout`)
3. Changed `fetch_forecast(days=3)` to `days=7`
4. Removed the `export_csv()` function

## What Driftation found
All 4 outdated sentences in `project/README.md`, each judged "outdated" by Gemma with a fix.
Two of them were found through the code graph (indirect links):
- "The --timeout flag defaults to 30 seconds." via `DEFAULT_TIMEOUT` → `--timeout`
- "Call fetch_forecast(city) to get a 3 day forecast." via `days` → `fetch_forecast`

Sentences that are still correct ("Use --units imperial...", "Units default to metric.")
were not reported.

## Run it yourself
From the repository root, with Ollama running and `gemma4:e4b` pulled:
```
driftation --repo examples/basic/project --diff examples/basic/pr.diff --output report.md --json report.json
```
Add `--no-llm` to skip Gemma. Commit hashes show "n/a" here because a saved diff has no git
history; when run inside a git repo (`--base main`), each change shows its commit.

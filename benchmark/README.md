# Benchmark: real documentation drift from open-source history

The judges test drift detection on real project histories, so we built the same test ourselves.

## How the cases were found
`mine` step (not part of the tool): we scanned the full git history of 21 public Python
projects for this pattern:

1. a **code commit** removes or renames a name (a CLI flag, parameter, option or function), and
2. within 14 days, a later **docs-only commit** changes doc lines that still used that old name.

The scan produced 13 candidates. We then **checked every one by hand** and excluded 4 that
were not real drift (file clean-ups and documentation reorganisations where the doc change was
unrelated to the code change). That leaves **9 real cases from 9 projects**, listed in
[`cases.json`](cases.json) with full commit hashes.

## The test
For each case, Driftation runs on the **code commit only** (`--base <commit>^ --head <commit>`),
before the human's doc fix existed. A case counts as **caught** if Driftation flags a sentence
that the human later fixed.

## Results

Run without Gemma (`--no-llm`), so the numbers are fully reproducible on any machine:

| Project | Code change | Hours until human fix | Result | Fixed lines flagged | Other findings |
|---|---|---|---|---|---|
| cookiecutter | `--config` → `--config-file` | 2.8 | **Caught** | 2 of 2 | 0 |
| google/yapf | `--noverify` removed | 10.8 | **Caught** | 3 of 3 | 0 |
| PyCQA/bandit | `--context` switch changed | 0.0 | **Caught** | 1 of 1 | 0 |
| PyCQA/isort | `file_contents` parameter renamed | 2.3 | **Caught** | 1 of 1 | 2 |
| httpie/cli | `--response-as` replaced | 174.1 | **Caught** | 3 of 4 | 2 |
| PyCQA/flake8 | built-in `--max-complexity` removed | 61.3 | **Caught** | 1 of 2 | 2 |
| nedbat/coveragepy | `[combine] ignore_errors` removed | 29.8 | **Caught** | 2 of 1* | 22 |
| pypa/pipx | `install --spec` removed | 67.2 | Missed | 0 of 6 | 4 |
| hhatto/autopep8 | `has_key` fixer removed | 0.2 | Missed | 0 of 2 | 0 |

**Caught 7 of 9 (78%)**, each one before the human doc fix existed. *coverage.py's fixed line
appears twice in the docs; both copies were flagged.

**With Gemma**, the extra findings drop while every catch stays: on the cases Gemma finished in
our run, httpie went from 2 extra findings to 0 and flake8 from 2 to 1, with all real catches kept.
The “other findings” are not all wrong: many point at sentences that mention the changed name and
deserve a look; Gemma’s job is to sort those.

## Why the two misses happened
- **pipx `--spec`**: the option was removed from `pipx install`, but `pipx run` still has a
  `--spec` option. Driftation sees the name still exists in the code, so its “still in use”
  filter stays quiet. Fixing this needs flags to be tracked per subcommand.
- **autopep8 `has_key`**: the removed name lived inside a dictionary of supported fixes
  (`'W601': ['has_key']`). Driftation tracks functions, constants, flags, parameters and
  settings, not entries inside data structures.

Both are honest limitations we would address next.

## Reproduce
From the repository root:
```
python benchmark/run_benchmark.py            # with Gemma (Ollama running)
python benchmark/run_benchmark.py --no-llm   # without Gemma
```
Projects are cloned read-only into `benchmark/.repos/` (git-ignored). Public data only;
nothing is posted to any project.

# Real-world example: cookiecutter `--config` → `--config-file`

A real case of documentation drift in [cookiecutter](https://github.com/cookiecutter/cookiecutter),
a popular open-source Python project (BSD-3-Clause). Public data only; nothing was posted to the project.

| | Commit | Date | What happened |
|---|---|---|---|
| Code change | [`64433b1`](https://github.com/cookiecutter/cookiecutter/commit/64433b162fee34660389f5c5220f9a24e00a0ff4) | 7 Nov 2015, 14:23 | Renamed the CLI option `--config` to `--config-file`, docs not updated |
| Doc fix | [`d4cfba2`](https://github.com/cookiecutter/cookiecutter/commit/d4cfba25552deb44c218f5d63c1608678d9d8f57) | 7 Nov 2015, 17:11 | A maintainer fixed 2 lines in `docs/advanced_usage.rst` |

## Files
| File | What it is |
|---|---|
| `pr.diff` | The input: the code change (`git diff 64433b1^ 64433b1`) |
| `doc_fix.diff` | The later doc fix by the maintainer, our "answer key" |
| `report.md` / `report.json` | The **real** Driftation output, with gemma4:e4b running locally in Ollama |

## Result
Driftation, run on the code change **before** the doc fix existed:
- flagged exactly the **2 lines the maintainer later fixed** (lines 73 and 75), and nothing else,
  out of 2,763 doc sentences (docs and docstrings) and 596 code items and settings;
- Gemma judged both "outdated", and its suggested fixes match the maintainer's fix word for word.

| Line | Maintainer's fix (`d4cfba2`) | Gemma's suggested fix |
|---|---|---|
| 73 | `...on the command line via ``--config-file``::` | `...on the command line via ``--config-file``::` |
| 75 | `$ cookiecutter --config-file /home/audreyr/my-custom-config.yaml ...` | `$ cookiecutter --config-file /home/audreyr/my-custom-config.yaml ...` |

**Honest note:** our first run flagged 29 sentences, because the function parameter `config` was
renamed too and "config" is an everyday word. That led to a rule in `driftation/docs.py`: a plain
single word only counts when the doc writes it as code (`` `config` ``, `config(`, `config=`).
With that rule the result is the 2 correct lines and no false alarms.

## Run it yourself
```
git clone https://github.com/cookiecutter/cookiecutter.git
cd cookiecutter
driftation --base 64433b1^ --head 64433b1 --output report.md --json report.json
```
(`64433b1^` means "the commit just before 64433b1".) Add `--no-llm` to skip Gemma.

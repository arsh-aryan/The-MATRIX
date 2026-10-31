# Driftation report

Found **4** code change(s) and **4** possibly outdated doc sentence(s).

## Code changes

| Change | Item | Before | After | Where | Commit |
|---|---|---|---|---|---|
| value changed | constant | `DEFAULT_TIMEOUT = 30` | `DEFAULT_TIMEOUT = 60` | cli.py:4 | n/a |
| value changed | param | `fetch_forecast.days = 3` | `fetch_forecast.days = 7` | cli.py:8 | n/a |
| removed | function | `export_csv` | *(removed)* | cli.py:13 | n/a |
| renamed | flag | `--max-retries = 3` | `--retries = 3` | cli.py:16 | n/a |

## 1. `README.md` line 6

> Run `weather London --max-retries 5` to retry failed requests more often.

- **Verdict:** 🔴 outdated — The documentation uses the old flag name `--max-retries` instead of the new name `--retries`.
- **Caused by:** renamed flag in `cli.py:16`
- **What changed:** `--max-retries = 3` → `--retries = 3`
- **Evidence:** direct mention of `--max-retries`: `flag:--max-retries` → `doc:README.md:6`
- **Suggested fix:** Run `weather London --retries 5` to retry failed requests more often.

## 2. `README.md` line 12

> Use export_csv(forecast, path) to save results to a spreadsheet.

- **Verdict:** 🔴 outdated — The function 'export_csv' was removed from the codebase.
- **Caused by:** removed function in `cli.py:13`
- **What changed:** `export_csv` → *(removed)*
- **Evidence:** direct mention of `export_csv`: `function:export_csv` → `doc:README.md:12`
- **Suggested fix:** Remove this sentence or update it to reflect the new method for saving results.

## 3. `README.md` line 7

> The --timeout flag defaults to 30 seconds.

- **Verdict:** 🔴 outdated — The code constant (DEFAULT_TIMEOUT) changed from 30 to 60, but the documentation did not update.
- **Caused by:** value changed constant in `cli.py:4`
- **What changed:** `DEFAULT_TIMEOUT = 30` → `DEFAULT_TIMEOUT = 60`
- **Evidence:** indirect link of `--timeout`: `constant:DEFAULT_TIMEOUT` → `flag:--timeout` → `doc:README.md:7`
- **Suggested fix:** The --timeout flag defaults to 60 seconds.

## 4. `README.md` line 11

> Call fetch_forecast(city) to get a 3 day forecast.

- **Verdict:** 🔴 outdated — The documented forecast duration (3 days) does not match the new parameter value (7 days).
- **Caused by:** value changed param in `cli.py:8`
- **What changed:** `fetch_forecast.days = 3` → `fetch_forecast.days = 7`
- **Evidence:** indirect link of `fetch_forecast`: `param:fetch_forecast.days` → `function:fetch_forecast` → `doc:README.md:11`
- **Suggested fix:** Call fetch_forecast(city) to get a 7 day forecast.


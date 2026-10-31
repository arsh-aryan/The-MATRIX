# Driftation report

Found **2** code change(s) and **2** possibly outdated doc sentence(s).

## Code changes

| Change | Item | Before | After | Where | Commit |
|---|---|---|---|---|---|
| renamed | param | `main.config` | `main.config_file` | cookiecutter/cli.py:71 | 64433b1 |
| renamed | flag | `--config = USER_CONFIG_PATH` | `--config-file = USER_CONFIG_PATH` | cookiecutter/cli.py:63 | 64433b1 |

## 1. `docs/advanced_usage.rst` line 73

> From version 1.3.0 you can also specify a config file on the command line via ``--config``::

- **Verdict:** 🔴 outdated — The flag mentioned in the documentation (--config) was renamed to --config-file in the code change.
- **Caused by:** renamed flag in `cookiecutter/cli.py:63`, commit `64433b1`
- **What changed:** `--config = USER_CONFIG_PATH` → `--config-file = USER_CONFIG_PATH`
- **Evidence:** direct mention of `--config`: `flag:--config` → `doc:docs/advanced_usage.rst:73`
- **Suggested fix:** From version 1.3.0 you can also specify a config file on the command line via ``--config-file``::

## 2. `docs/advanced_usage.rst` line 75

> $ cookiecutter --config /home/audreyr/my-custom-config.yaml cookiecutter-pypackage

- **Verdict:** 🔴 outdated — The CLI flag used, `--config`, was renamed to `--config-file` in the code.
- **Caused by:** renamed flag in `cookiecutter/cli.py:63`, commit `64433b1`
- **What changed:** `--config = USER_CONFIG_PATH` → `--config-file = USER_CONFIG_PATH`
- **Evidence:** direct mention of `--config`: `flag:--config` → `doc:docs/advanced_usage.rst:75`
- **Suggested fix:** $ cookiecutter --config-file /home/audreyr/my-custom-config.yaml cookiecutter-pypackage


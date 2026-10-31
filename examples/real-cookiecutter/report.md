# Driftation report

Found **3** code change(s) and **2** possibly outdated doc sentence(s).

## Code changes

| Change | Item | Before | After | Where | Commit |
|---|---|---|---|---|---|
| renamed | param | `main.config` | `main.config_file` | cookiecutter/cli.py:71 | 64433b1 |
| renamed | flag | `--config = USER_CONFIG_PATH` | `--config-file = USER_CONFIG_PATH` | cookiecutter/cli.py:63 | 64433b1 |
| signature changed | function | `main(template, no_input, checkout, verbose, replay, overwrite_if_exists, output_dir, config)` | `main(template, no_input, checkout, verbose, replay, overwrite_if_exists, output_dir, config_file, default_config)` | cookiecutter/cli.py:71 | 64433b1 |

## 1. `docs/advanced_usage.rst` line 73

> From version 1.3.0 you can also specify a config file on the command line via ``--config``::

- **Verdict:** 🔴 outdated — The command line flag was renamed from --config to --config-file.
- **Caused by:** renamed flag in `cookiecutter/cli.py:63`, commit `64433b1`
- **What changed:** `--config = USER_CONFIG_PATH` → `--config-file = USER_CONFIG_PATH`
- **Evidence:** direct mention of `--config`: `flag:--config` → `doc:docs/advanced_usage.rst:73`
- **Suggested fix:** From version 1.3.0 you can also specify a config file on the command line via ``--config-file``::

## 2. `docs/advanced_usage.rst` line 75

> $ cookiecutter --config /home/audreyr/my-custom-config.yaml cookiecutter-pypackage

- **Verdict:** 🔴 outdated — The command flag --config was renamed to --config-file in the underlying code.
- **Caused by:** renamed flag in `cookiecutter/cli.py:63`, commit `64433b1`
- **What changed:** `--config = USER_CONFIG_PATH` → `--config-file = USER_CONFIG_PATH`
- **Evidence:** direct mention of `--config`: `flag:--config` → `doc:docs/advanced_usage.rst:75`
- **Suggested fix:** $ cookiecutter --config-file /home/audreyr/my-custom-config.yaml cookiecutter-pypackage


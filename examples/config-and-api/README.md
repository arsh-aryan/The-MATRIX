# Example: notes-app (hand-made demo, config + API)

A small sample project showing the kinds of drift beyond renamed flags: config files,
config tables, function signatures, behaviour and docstrings.

| Folder / file | What it is |
|---|---|
| `before/` | The project before the change |
| `after/` | The project after the change (code and `config.yaml` changed, `README.md` not updated) |
| `report.md` / `report.json` | The **real** output of Driftation with gemma4:e4b running locally in Ollama |

## What the change did
| Change | Where |
|---|---|
| `server.port` 8080 → 9000 | `config.yaml` |
| `storage.path` renamed to `storage.db_path` | `config.yaml` |
| `create_note(title)` now needs `owner` too | `app.py` |
| `list_notes()` now sorts newest first (name unchanged) | `app.py` |
| `DEFAULT_PAGE_SIZE` 20 → 50 (default of `search(..., page_size)`) | `app.py` |

## What Driftation found (6 of 6, all judged "outdated" by Gemma)
1. Config table row `server.port | 8080`: changed value
2. Config table row `storage.path`: renamed key
3. "Call create_note(title) to add a note.": the call is missing the new required argument
4. "list_notes(notes) returns notes ... oldest first.": **behaviour change**. Gemma read the old
   and new code, saw `reverse=True`, and suggested "newest first"
5. "`search(notes, query)` returns up to 20 notes per page.": via the graph
   (`DEFAULT_PAGE_SIZE` → `search`)
6. The **docstring** in `app.py` line 19, "(default 20)": via the graph

The unchanged `server.debug` row is not reported.

## Run it yourself
From the repository root, with Ollama running:
```
driftation --old examples/config-and-api/before --repo examples/config-and-api/after
```
With `--no-llm` you get findings 1, 2, 3, 5 and 6; the behaviour change (4) needs Gemma.

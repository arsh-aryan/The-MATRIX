# Driftation report

Found **5** code change(s) and **6** possibly outdated doc sentence(s).

## Code changes

| Change | Item | Before | After | Where | Commit |
|---|---|---|---|---|---|
| value changed | constant | `DEFAULT_PAGE_SIZE = 20` | `DEFAULT_PAGE_SIZE = 50` | app.py:3 | n/a |
| signature changed | function | `create_note(title)` | `create_note(title, owner)` | app.py:6 | n/a |
| behavior changed | function | `list_notes` | `list_notes` *(code changed)* | app.py:11 | n/a |
| value changed | setting | `server.port = 8080` | `server.port = 9000` | config.yaml:2 | n/a |
| renamed | setting | `storage.path = ./notes.db` | `storage.db_path = ./notes.db` | config.yaml:5 | n/a |

## 1. `README.md` line 9

> | `server.port` | 8080 | Port the server listens on |

- **Verdict:** 🔴 outdated — The documented port value (8080) does not match the new value set in the configuration (9000).
- **Caused by:** value changed setting in `config.yaml:2`
- **What changed:** `server.port = 8080` → `server.port = 9000`
- **Evidence:** direct mention of `server.port`: `setting:server.port` → `doc:README.md:9`
- **Suggested fix:** |`server.port` | 9000 | Port the server listens on |

## 2. `README.md` line 11

> | `storage.path` | ./notes.db | Where notes are stored |

- **Verdict:** 🔴 outdated — The configuration key 'storage.path' was renamed to 'storage.db_path' in the code.
- **Caused by:** renamed setting in `config.yaml:5`
- **What changed:** `storage.path = ./notes.db` → `storage.db_path = ./notes.db`
- **Evidence:** direct mention of `storage.path`: `setting:storage.path` → `doc:README.md:11`
- **Suggested fix:** |"storage.db_path"| ./notes.db | Where notes are stored |

## 3. `README.md` line 14

> Call create_note(title) to add a note.

- **Verdict:** 🔴 outdated — The function now requires two arguments (title and owner) instead of just one.
- **Caused by:** signature changed function in `app.py:6`
- **What changed:** `create_note(title)` → `create_note(title, owner)`
- **Evidence:** direct mention of `create_note`: `function:create_note` → `doc:README.md:14`
- **Suggested fix:** Call create_note(title, owner) to add a note.

## 4. `README.md` line 15

> list_notes(notes) returns notes in the order they were created, oldest first.

- **Verdict:** 🔴 outdated — The new code sorts notes by creation date in reverse order (newest first), but the documentation claims 'oldest first'.
- **Caused by:** behavior changed function in `app.py:11`
- **What changed:** `list_notes` → `list_notes` *(code changed)*
- **Evidence:** direct mention of `list_notes`: `function:list_notes` → `doc:README.md:15`
- **Suggested fix:** list_notes(notes) returns notes in the order they were created, newest first.

## 5. `README.md` line 16

> `search(notes, query)` returns up to 20 notes per page.

- **Verdict:** 🔴 outdated — The documentation states 20, but the constant DEFAULT_PAGE_SIZE was updated from 20 to 50.
- **Caused by:** value changed constant in `app.py:3`
- **What changed:** `DEFAULT_PAGE_SIZE = 20` → `DEFAULT_PAGE_SIZE = 50`
- **Evidence:** indirect link of `search`: `constant:DEFAULT_PAGE_SIZE` → `function:search` → `doc:README.md:16`
- **Suggested fix:** "search(notes, query)" returns up to 50 notes per page.

## 6. `app.py` line 19

> Returns at most `page_size` notes (default 20).

- **Verdict:** 🔴 outdated — The default value in the documentation (20) does not match the constant value in the code (50).
- **Caused by:** value changed constant in `app.py:3`
- **What changed:** `DEFAULT_PAGE_SIZE = 20` → `DEFAULT_PAGE_SIZE = 50`
- **Evidence:** indirect link of `page_size`: `constant:DEFAULT_PAGE_SIZE` → `function:search` → `param:search.page_size` → `doc:app.py:19`
- **Suggested fix:** Returns at most `page_size` notes (default 50).


# notes-app

A tiny note-taking service.

## Configuration

| Setting | Default | Description |
|---|---|---|
| `server.port` | 8080 | Port the server listens on |
| `server.debug` | false | Print debug logs |
| `storage.path` | ./notes.db | Where notes are stored |

## API
Call create_note(title) to add a note.
list_notes(notes) returns notes in the order they were created, oldest first.
`search(notes, query)` returns up to 20 notes per page.

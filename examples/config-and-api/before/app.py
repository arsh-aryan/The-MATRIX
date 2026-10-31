"""notes-app: a tiny note-taking service."""

DEFAULT_PAGE_SIZE = 20


def create_note(title):
    """Create a note with `title` and return it."""
    return {"title": title}


def list_notes(notes):
    """Return all notes."""
    return list(notes)


def search(notes, query, page_size=DEFAULT_PAGE_SIZE):
    """Find notes whose title contains `query`.

    Returns at most `page_size` notes (default 20).
    """
    return [n for n in notes if query in n["title"]][:page_size]

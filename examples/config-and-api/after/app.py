"""notes-app: a tiny note-taking service."""

DEFAULT_PAGE_SIZE = 50


def create_note(title, owner):
    """Create a note with `title` and return it."""
    return {"title": title, "owner": owner}


def list_notes(notes):
    """Return all notes."""
    return sorted(notes, key=lambda n: n["created"], reverse=True)


def search(notes, query, page_size=DEFAULT_PAGE_SIZE):
    """Find notes whose title contains `query`.

    Returns at most `page_size` notes (default 20).
    """
    return [n for n in notes if query in n["title"]][:page_size]

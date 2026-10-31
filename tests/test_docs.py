from driftation.docs import contains_value, doc_files, mentions, sentences
from driftation.git_input import Folder


def test_mentions_name_variants():
    assert mentions("Use `--max-retries` to retry.", "--max-retries") == "--max-retries"
    assert mentions("Set max_retries in the config.", "--max-retries") == "max_retries"
    assert mentions("The Max retries option is 3.", "max_retries") is not None


def test_short_names_must_match_exactly():
    assert mentions("Your id is shown.", "ID") is None
    assert mentions("The ID is shown.", "ID") == "ID"


def test_no_partial_word_match():
    assert mentions("Set timeouts carefully.", "timeout") is None
    assert mentions("Use --max-retries-total.", "--max-retries") is None


def test_contains_value():
    assert contains_value("The default timeout is 30 seconds.", "30")
    assert not contains_value("The default timeout is 300 seconds.", "30")
    assert contains_value("Format defaults to json.", "'json'")
    assert contains_value("Debug is false by default.", "False")


def test_sentences_have_line_numbers():
    text = "# Title\n\nFirst sentence. Second sentence!\n"
    assert list(sentences(text)) == [(1, "# Title"), (3, "First sentence."), (3, "Second sentence!")]


def test_doc_files_skip_requirements(tmp_path):
    for name in ("README.md", "guide.rst", "notes.txt", "requirements.txt", "app.py"):
        (tmp_path / name).write_text("x")
    assert sorted(doc_files(Folder(str(tmp_path)))) == ["README.md", "guide.rst", "notes.txt"]

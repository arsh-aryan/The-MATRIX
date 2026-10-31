from driftation.docs import contains_value, doc_files, mentions, sentences
from driftation.git_input import Folder


def test_mentions_name_variants():
    assert mentions("Use `--max-retries` to retry.", "--max-retries") == "--max-retries"
    assert mentions("Set max_retries in the config.", "--max-retries") == "max_retries"
    assert mentions("The Max retries option is 3.", "max_retries") is not None


def test_code_looking_names_match_exactly():
    assert mentions("Set TIMEOUT in settings.py.", "TIMEOUT") == "TIMEOUT"
    assert mentions("Set the timeout in settings.py.", "TIMEOUT") is None
    assert mentions("Create an HttpClient first.", "HttpClient") == "HttpClient"


def test_single_words_must_look_like_code():
    # "config" is an everyday word: plain prose is not a mention, code formatting is
    assert mentions("Edit your user config file.", "config") is None
    assert mentions("Pass ``config`` to main().", "config") == "config"
    assert mentions("Pass `config` to main().", "config") == "config"
    assert mentions("Call main(config=path).", "config") == "config"
    assert mentions("Call export(data).", "export") == "export"
    assert mentions("Use --config to pick a file.", "--config") == "--config"


def test_no_partial_word_match():
    assert mentions("Set `timeouts` carefully.", "timeout") is None
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

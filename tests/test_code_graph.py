from driftation.code_graph import build_graph, extract, walk
from driftation.git_input import Folder

CODE = '''
import argparse

DEFAULT_RETRIES = 3


class Client:
    def fetch(self, url, timeout=30):
        return connect(url)


def connect(url):
    return DEFAULT_RETRIES


parser = argparse.ArgumentParser()
parser.add_argument("--max-retries", "-r", default=DEFAULT_RETRIES)
'''


def test_extract_finds_code_items():
    symbols, _ = extract(CODE)
    assert symbols[("constant", "DEFAULT_RETRIES")]["value"] == "3"
    assert ("class", "Client") in symbols
    assert symbols[("param", "fetch.timeout")]["value"] == "30"
    assert ("param", "fetch.self") not in symbols
    assert symbols[("flag", "--max-retries")]["value"] == "DEFAULT_RETRIES"


def test_extract_ignores_broken_code():
    assert extract("def broken(:") == ({}, [])


def test_graph_links_flag_to_constant(tmp_path):
    (tmp_path / "app.py").write_text(CODE)
    graph = build_graph(Folder(str(tmp_path)))
    assert graph.has_edge("flag:--max-retries", "constant:DEFAULT_RETRIES")
    assert graph.has_edge("function:fetch", "function:connect")
    assert graph.has_edge("function:connect", "constant:DEFAULT_RETRIES")
    # Two steps from the constant reaches fetch (through connect)
    paths = walk(graph, "constant:DEFAULT_RETRIES")
    assert paths["function:fetch"] == ["constant:DEFAULT_RETRIES", "function:connect", "function:fetch"]

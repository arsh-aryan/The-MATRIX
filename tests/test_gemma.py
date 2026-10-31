"""Gemma tests use fake HTTP responses, so they never need Ollama running."""
import json
from unittest import mock

import requests

from driftation import gemma

FINDING = {
    "doc": "README.md",
    "line": 3,
    "sentence": "Use --max-retries to set retries.",
    "matched": "--max-retries",
    "direct": True,
    "evidence": ["flag:--max-retries", "doc:README.md:3"],
    "change": {
        "type": "renamed", "kind": "flag", "file": "cli.py",
        "old_name": "--max-retries", "new_name": "--retries",
        "old_value": "3", "new_value": "3", "old_line": 4, "new_line": 4, "commit": "abc1234",
    },
}


def fake_response(payload):
    response = mock.Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"response": json.dumps(payload)}
    return response


def test_prompt_contains_change_and_sentence():
    prompt = gemma.build_prompt(FINDING)
    assert "--max-retries = 3" in prompt and "--retries = 3" in prompt
    assert "Use --max-retries to set retries." in prompt


def test_ask_gemma_reads_verdict():
    answer = {"verdict": "outdated", "explanation": "Flag renamed.", "suggested_fix": "Use --retries."}
    with mock.patch("driftation.gemma.requests.post", return_value=fake_response(answer)) as post:
        result = gemma.ask_gemma(dict(FINDING))
    assert result == answer
    assert post.call_args.kwargs["json"]["model"] == "gemma4:e4b"


def test_unknown_verdict_becomes_uncertain():
    with mock.patch("driftation.gemma.requests.post", return_value=fake_response({"verdict": "maybe"})):
        assert gemma.ask_gemma(dict(FINDING))["verdict"] == "uncertain"


def test_connection_error_is_unverified():
    with mock.patch("driftation.gemma.requests.post", side_effect=requests.ConnectionError("down")):
        assert gemma.ask_gemma(dict(FINDING))["verdict"] == "unverified"


def test_review_without_ollama_does_not_crash():
    with mock.patch("driftation.gemma.ollama_running", return_value=False):
        [finding] = gemma.review([dict(FINDING)])
    assert finding["review"]["verdict"] == "unverified"


def test_review_with_no_llm():
    [finding] = gemma.review([dict(FINDING)], use_llm=False)
    assert finding["review"]["verdict"] == "not_checked"

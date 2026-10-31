"""Step 6: ask Gemma (running locally in Ollama) whether each flagged sentence is really outdated."""
import json

import requests

OLLAMA_URL = "http://localhost:11434"
VERDICTS = {"outdated", "still_correct", "uncertain"}

PROMPT = """You check whether documentation is outdated after a code change.

Code change ({change_type} {kind} in {file}):
  before: {old}
  after:  {new}

Documentation sentence ({doc}, line {line}):
  "{sentence}"

How they are linked: {evidence}
{code}
Is this sentence now outdated because of the code change?
Answer with JSON only, in this exact shape:
{{"verdict": "outdated" | "still_correct" | "uncertain",
  "explanation": "one short sentence",
  "suggested_fix": "the corrected sentence, or empty if no fix is needed"}}
"""


def ollama_running(url=OLLAMA_URL):
    """True if the local Ollama server answers."""
    try:
        return requests.get(f"{url}/api/tags", timeout=3).ok
    except requests.RequestException:
        return False


def build_prompt(finding):
    change = finding["change"]
    return PROMPT.format(
        change_type=change["type"].replace("_", " "),
        kind=change["kind"],
        file=change["file"],
        old=_describe(change["old_name"], change["old_value"]),
        new=_describe(change["new_name"] or change["old_name"], change["new_value"])
        if change["type"] != "removed" else "(removed)",
        doc=finding["doc"],
        line=finding["line"],
        sentence=finding["sentence"],
        evidence=" -> ".join(finding["evidence"]),
        code=_code_section(change),
    )


def _code_section(change):
    """For behaviour changes, show Gemma the old and new code so it can judge what changed."""
    if change["type"] != "behavior_changed":
        return ""
    return (
        "\nThe function's name and parameters did not change, but its code did.\n"
        f"Old code:\n{change.get('old_code', '')}\n\nNew code:\n{change.get('new_code', '')}\n"
        "Only answer \"outdated\" if the sentence describes behaviour the new code no longer has.\n"
    )


def ask_gemma(finding, model="gemma4:e4b", url=OLLAMA_URL):
    """Return {"verdict", "explanation", "suggested_fix"} for one finding.

    Never crashes: if Ollama fails or answers badly, the verdict is "unverified".
    """
    try:
        response = requests.post(
            f"{url}/api/generate",
            json={"model": model, "prompt": build_prompt(finding), "stream": False, "format": "json"},
            timeout=180,
        )
        response.raise_for_status()
        answer = json.loads(response.json()["response"])
    except (requests.RequestException, KeyError, ValueError) as error:
        return {"verdict": "unverified", "explanation": f"Gemma call failed: {error}", "suggested_fix": ""}

    verdict = str(answer.get("verdict", "")).strip().lower()
    return {
        "verdict": verdict if verdict in VERDICTS else "uncertain",
        "explanation": str(answer.get("explanation", "")).strip(),
        "suggested_fix": str(answer.get("suggested_fix", "")).strip(),
    }


def review(findings, model="gemma4:e4b", use_llm=True, url=OLLAMA_URL):
    """Add a "review" to every finding (from Gemma, or a placeholder without it)."""
    if not use_llm:
        reason = "Not checked: run without --no-llm to let Gemma review it."
        for f in findings:
            f["review"] = {"verdict": "not_checked", "explanation": reason, "suggested_fix": ""}
        return findings
    if not ollama_running(url):
        reason = f"Ollama is not running at {url}, so Gemma could not check this."
        for f in findings:
            f["review"] = {"verdict": "unverified", "explanation": reason, "suggested_fix": ""}
        return findings
    for f in findings:
        f["review"] = ask_gemma(f, model=model, url=url)
    return findings


def _describe(name, value):
    return f"{name} = {value}" if value is not None else name

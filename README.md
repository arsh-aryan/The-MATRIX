# Driftation

> **Status:** in development. Stages 1-7 land in upcoming PRs.

Driftation finds documentation that became outdated because of code changes
in a pull request, and points to the exact code change responsible.

## What it reports
For every potentially outdated sentence, Driftation shows:
- **Where the docs are wrong:** documentation file, line number, and the exact sentence
- **What caused it:** the code file, line, and commit that introduced the change
- **What changed:** the old and new name or value (e.g. `--max-retries` → `--retries`, default `3` → `5`)
- **Evidence:** the knowledge graph path linking the sentence to the changed code
- **Verdict:** outdated, still correct, or uncertain, judged by Gemma, with a suggested fix

## How it works
1. Builds a knowledge graph of the project's code (functions, flags, defaults, calls).
2. Links documentation sentences to code nodes (exact name matches, plus Gemma for fuzzy matches).
3. Reads the pull request diff to find removed, renamed, or changed items.
4. Walks the graph from each changed node to find affected documentation.
5. Filters out sentences already fixed in the PR and names still used elsewhere.
6. Asks gemma4:e4b, running locally via Ollama, to judge each candidate sentence.

## Requirements
- Python 3.11+
- Ollama with gemma4:e4b (`ollama pull gemma4:e4b`)

## Installation
pip install -r requirements.txt

## Usage
python -m driftation --base main

## Example
See the `examples/` folder for a sample input and the real report it produced.

## Running tests
python -m pytest

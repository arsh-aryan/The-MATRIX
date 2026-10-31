# HACKATHON.md
**Team Name:** The MATRIX
**Member Details:**
- Arsh Aryan (Team Leader)
- Harshit Sharma

**Problem Statement:** Problem 5 - Automated Documentation Drift Detection

## AI Models Used

### gemma4:e4b (via Ollama)
**Role:** Reviews each documentation sentence flagged by our diff analyzer
and decides whether it is actually outdated after the code change. It also
writes a short explanation linking the sentence to the responsible change.

**Why we chose it:**
- Open-weight model, meeting the hackathon's open-source AI requirement.
- Runs fully locally through Ollama, so no project code is sent to a cloud service.
- Small enough to run on our laptops while still understanding both code and
  English text, which is needed to compare docs against code changes.

**Fallback:** gemma4:e2b on laptops with limited memory.

## AI Coding Assistants
- Claude Opus 5.5 (Anthropic): helped write and debug the code.
  Not used inside the product.

"""Step 2: read documentation files and find sentences that mention code names."""
import os
import re

DOC_EXTENSIONS = (".md", ".rst", ".txt")
# Split after . ! ? when the next sentence starts with a capital, backtick, dash or digit
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z`\-*0-9])")


def doc_files(tree):
    """Documentation files in a GitTree or Folder (requirements*.txt is not documentation)."""
    return [
        path for path in tree.list_files()
        if path.lower().endswith(DOC_EXTENSIONS)
        and not os.path.basename(path).lower().startswith(("requirements", "license"))
    ]


def sentences(text):
    """Yield (line_number, sentence) for every sentence in a doc file."""
    for number, line in enumerate(text.splitlines(), start=1):
        for sentence in SENTENCE_END.split(line.strip()):
            if sentence.strip():
                yield number, sentence.strip()


def load_sentences(tree):
    """All doc sentences in the project as (path, line, sentence)."""
    found = []
    for path in doc_files(tree):
        for number, sentence in sentences(tree.read(path) or ""):
            found.append((path, number, sentence))
    return found


def name_variants(name):
    """Ways a code name can be written in docs.

    "max_retries" -> max_retries, max-retries, --max-retries, "max retries"
    """
    base = name.lstrip("-")
    words = [w for w in re.split(r"[_\-]+", base) if w]
    variants = {name, base}
    if len(words) > 1:
        variants |= {"_".join(words), "-".join(words), "--" + "-".join(words), " ".join(words)}
    return variants


def mentions(sentence, name):
    """Return the variant of `name` found in `sentence`, or None.

    Multi-word and long names match in any case ("Max retries"); short single words
    like "id" must match exactly, to avoid false alarms.
    """
    for variant in sorted(name_variants(name), key=len, reverse=True):
        loose = " " in variant or "_" in variant or "-" in variant or len(variant) >= 4
        flags = re.IGNORECASE if loose else 0
        if re.search(r"(?<![\w-])" + re.escape(variant) + r"(?![\w-])", sentence, flags):
            return variant
    return None


def contains_value(sentence, value):
    """True if the sentence states this code value, e.g. "30" or "'json'" -> json."""
    if value is None:
        return False
    text = value.strip("'\"")
    if not text:
        return False
    flags = re.IGNORECASE if text in ("True", "False", "None") else 0
    return re.search(r"(?<![\w.])" + re.escape(text) + r"(?!\w|\.\d)", sentence, flags) is not None

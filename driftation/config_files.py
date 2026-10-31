"""Read settings from config files (YAML, TOML, JSON, .ini/.cfg, .env) as code items.

Each setting becomes a symbol ("setting", "server.port") with its value, so a renamed key,
a removed key, or a changed default is handled exactly like a Python constant.
"""
import configparser
import json
import os
import re
import tomllib

import yaml

CONFIG_EXTENSIONS = (".yaml", ".yml", ".toml", ".json", ".ini", ".cfg", ".env")
MAX_SIZE = 200_000  # skip huge generated files


def is_config(path):
    name = os.path.basename(path).lower()
    if "lock" in name or name in ("package.json", "tsconfig.json"):
        return False  # lock files and build metadata, not user settings
    if path.startswith(".github/"):
        return False  # CI workflows, not project settings
    return name.endswith(CONFIG_EXTENSIONS) or name == ".env" or name.startswith(".env.")


def extract_config(path, text):
    """Return {("setting", "dotted.key"): {"value": text, "line": int}} for one config file."""
    if not text or len(text) > MAX_SIZE:
        return {}
    try:
        data = _load(path, text)
    except Exception:  # a broken config file should never stop the tool
        return {}
    lines = text.splitlines()
    symbols = {}
    for key, value in _flatten(data):
        symbols[("setting", key)] = {"value": _value_text(value), "line": _find_line(lines, key)}
    return symbols


def settings_from_lines(numbered_lines):
    """For a saved diff: read simple "key: value", "key = value" or KEY=VALUE lines."""
    symbols = {}
    for number, text in numbered_lines:
        match = re.match(r"^\s*([A-Za-z_][\w.\-]*)\s*[:=]\s*(.+?)\s*$", text)
        if match and not text.lstrip().startswith("#"):
            value = match.group(2).strip().strip("'\"")
            symbols[("setting", match.group(1))] = {"value": value, "line": number}
    return symbols


def _load(path, text):
    name = os.path.basename(path).lower()
    if name.endswith((".yaml", ".yml")):
        return yaml.safe_load(text)
    if name.endswith(".toml"):
        return tomllib.loads(text)
    if name.endswith(".json"):
        return json.loads(text)
    if name.endswith((".ini", ".cfg")):
        parser = configparser.ConfigParser(interpolation=None)
        parser.read_string(text)
        return {section: dict(parser[section]) for section in parser.sections()}
    # .env: KEY=VALUE lines
    pairs = {}
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            pairs[key.strip().removeprefix("export ").strip()] = value.strip().strip("'\"")
    return pairs


def _flatten(data, prefix=""):
    """{"server": {"port": 8080}} -> [("server.port", 8080)]. Lists are kept as one value."""
    if not isinstance(data, dict):
        return []
    items = []
    for key, value in data.items():
        full = f"{prefix}{key}"
        if isinstance(value, dict):
            items += _flatten(value, full + ".")
        else:
            items.append((full, value))
    return items


def _value_text(value):
    if isinstance(value, str):
        return value
    return json.dumps(value)  # True -> "true", 3 -> "3", [1, 2] -> "[1, 2]"


def _find_line(lines, key):
    """Best guess of the line where the last part of the key is written."""
    leaf = re.escape(key.split(".")[-1])
    for number, line in enumerate(lines, start=1):
        if re.search(r"(^|[\s\"'\[])" + leaf + r"[\"'\]]?\s*[:=]", line):
            return number
    return None

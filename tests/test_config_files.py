from driftation.changes import compare
from driftation.config_files import extract_config, is_config, settings_from_lines


def test_yaml_settings_are_flattened():
    symbols = extract_config("config.yaml", "server:\n  port: 8080\n  debug: false\n")
    assert symbols[("setting", "server.port")] == {"value": "8080", "line": 2}
    assert symbols[("setting", "server.debug")]["value"] == "false"


def test_other_formats():
    assert extract_config("app.toml", "[db]\nhost = 'localhost'\n")[("setting", "db.host")]["value"] == "localhost"
    assert extract_config("app.json", '{"retries": 3}')[("setting", "retries")]["value"] == "3"
    assert extract_config("setup.ini", "[server]\nport = 80\n")[("setting", "server.port")]["value"] == "80"
    assert extract_config(".env", "export API_URL='https://x'\n")[("setting", "API_URL")]["value"] == "https://x"


def test_broken_config_is_ignored():
    assert extract_config("bad.yaml", "a: [unclosed") == {}


def test_lock_files_and_workflows_are_not_config():
    assert is_config("config.yaml") and is_config(".env.local")
    assert not is_config("poetry.lock") and not is_config("package-lock.json")
    assert not is_config(".github/workflows/ci.yml")


def test_renamed_and_changed_settings():
    old = extract_config("c.yaml", "storage:\n  path: ./a.db\nport: 8080\n")
    new = extract_config("c.yaml", "storage:\n  db_path: ./a.db\nport: 9000\n")
    found = {(c["type"], c["old_name"], c["new_name"]) for c in compare("c.yaml", old, new)}
    assert found == {("renamed", "storage.path", "storage.db_path"), ("value_changed", "port", "port")}


def test_settings_from_diff_lines():
    assert settings_from_lines([(2, "  port: 9000"), (3, "# note: x")]) == {("setting", "port"): {"value": "9000", "line": 2}}

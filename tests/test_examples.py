"""Makes sure the example in examples/basic still produces the findings in its report."""
from pathlib import Path

from driftation.__main__ import main

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "basic"


def test_basic_example_finds_all_four(tmp_path):
    out = tmp_path / "report.md"
    main(["--repo", str(EXAMPLE / "project"), "--diff", str(EXAMPLE / "pr.diff"), "--no-llm", "--output", str(out)])
    report = out.read_text()
    for sentence in [
        "Run `weather London --max-retries 5` to retry failed requests more often.",
        "Use export_csv(forecast, path) to save results to a spreadsheet.",
        "The --timeout flag defaults to 30 seconds.",
        "Call fetch_forecast(city) to get a 3 day forecast.",
    ]:
        assert sentence in report
        assert sentence in (EXAMPLE / "report.md").read_text()  # the saved Gemma report agrees
    assert "Units default to metric." not in report

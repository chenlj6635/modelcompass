from pathlib import Path

from modelcompass.cli import main


def test_report_command():
    output = Path("reports") / "test-report.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        assert main(["report", "--output", str(output)]) == 0
        assert output.exists()
    finally:
        output.unlink(missing_ok=True)
from pathlib import Path

from modelcompass.cli import main


def test_cli_commands():
    output_dir = Path("reports") / "test-cli"
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        assert main(["data-validate"]) == 0
        score_path = output_dir / "score.json"
        assert main(["score", "--output", str(score_path)]) == 0
        assert score_path.exists()
        assert main(["pareto"]) == 0
        output = output_dir / "report.html"
        assert main(["report", "--output", str(output)]) == 0
        assert output.exists()
        assert main(["serve"]) == 0
    finally:
        for path in output_dir.iterdir():
            path.unlink()
        output_dir.rmdir()
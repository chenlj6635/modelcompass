import json
from pathlib import Path

from modelcompass.cli import main


def test_cli_score_and_report():
    output_dir = Path("reports") / "test-cli"
    output_dir.mkdir(parents=True, exist_ok=True)
    observations = output_dir / "observations.json"
    observations.write_text(json.dumps([{
        "model_variant_id": "m/1/reasoning", "benchmark_id": "b", "ability_cluster": "general",
        "score": 80, "score_unit": "percent", "observed_at": "2026-10-01", "reported_at": "2026-10-01",
        "source_url": "https://example.org/a"
    }]), encoding="utf-8")
    score_path = output_dir / "score.json"
    report_path = output_dir / "report.html"
    try:
        assert main(["data-validate", "--file", str(observations)]) == 0
        assert main(["score", "--observations", str(observations), "--output", str(score_path)]) == 0
        data = json.loads(score_path.read_text(encoding="utf-8"))
        assert data[0]["quality"] == 0.8 and data[0]["evidence"]
        assert main(["report", "--input", str(score_path), "--output", str(report_path)]) == 0
        assert report_path.exists()
    finally:
        for path in output_dir.iterdir():
            if path != observations:
                path.unlink()
        observations.unlink()
        output_dir.rmdir()
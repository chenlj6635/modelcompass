from pathlib import Path

from modelcompass.report import render_html, write_report


def test_html_is_self_contained():
    output = render_html([{"model_variant_id": "m", "quality": 0.8}])
    assert "ModelCompass report" in output
    assert "model_variant_id" not in output


def test_json_and_csv_exports():
    output_dir = Path("reports") / "test-output"
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        rows = [{"model_variant_id": "m", "quality": 0.8}]
        assert write_report(rows, output_dir / "a.json", "json").exists()
        assert write_report(rows, output_dir / "a.csv", "csv").exists()
    finally:
        for path in output_dir.iterdir():
            path.unlink()
        output_dir.rmdir()
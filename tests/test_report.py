from pathlib import Path
from modelcompass.report import render_html, write_report

def test_html_contains_evidence_and_warning_fields():
    text=render_html([{"model_variant_id":"m","quality":.8,"coverage":.5,"confidence":.7,"sources":["https://example.org"],"warnings":["missing data"]}])
    assert "https://example.org" in text and "missing data" in text and "<script" not in text

def test_json_and_csv_exports(tmp_path: Path):
    rows=[{"model_variant_id":"m","quality":.8,"warnings":["x"]}]
    assert write_report(rows,tmp_path/"a.json","json").exists(); assert write_report(rows,tmp_path/"a.csv","csv").exists()
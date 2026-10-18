import shutil
from pathlib import Path
from modelcompass.report import render_html, write_report
REPORTS=Path(__file__).resolve().parents[1]/"reports"
def clean():
    for p in REPORTS.glob("test-report-*"):
        if p.is_dir(): shutil.rmtree(p)
        else: p.unlink(missing_ok=True)
def test_html_contains_evidence_and_warning_fields():
    text=render_html([{"model_variant_id":"m","quality":.8,"coverage":.5,"confidence":.7,"sources":["https://example.org"],"warnings":["missing data"]}]); assert "https://example.org" in text and "missing data" in text and "<script" not in text
def test_json_and_csv_exports():
    clean()
    try:
        rows=[{"model_variant_id":"m","quality":.8,"warnings":["x"]}]; assert write_report(rows,REPORTS/"test-report-a.json","json").exists(); assert write_report(rows,REPORTS/"test-report-a.csv","csv").exists()
    finally: clean()
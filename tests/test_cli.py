import json
from pathlib import Path
from modelcompass.cli import main

def test_report_command_writes_offline_html(tmp_path: Path):
    rows=tmp_path/"rows.json"; rows.write_text(json.dumps([{"model_variant_id":"m","quality":.8}]),encoding="utf-8")
    out=tmp_path/"report.html"; assert main(["report","--input",str(rows),"--output",str(out)])==0
    assert "ModelCompass report" in out.read_text(encoding="utf-8")

def test_data_validate(tmp_path: Path, capsys):
    bundle=tmp_path/"bundle.json"; bundle.write_text(json.dumps({"scenarios":[{"id":"s","name":"S","weights":{"reasoning":1}}]}),encoding="utf-8")
    assert main(["data","validate","--input",str(bundle)])==0; assert "valid" in capsys.readouterr().out
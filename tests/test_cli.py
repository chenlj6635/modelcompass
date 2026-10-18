import json, shutil, urllib.request
from pathlib import Path
from threading import Thread
from modelcompass.cli import create_server, main
REPORTS=Path(__file__).resolve().parents[1]/"reports"
def clean():
    for p in REPORTS.glob("test-cli-*"):
        if p.is_dir(): shutil.rmtree(p)
        else: p.unlink(missing_ok=True)
def test_report_command_writes_offline_html(capsys):
    clean(); src=REPORTS/"test-cli-rows.json"; out=REPORTS/"test-cli-report.html"
    try:
        src.write_text(json.dumps([{"model_variant_id":"m","quality":.8}]),encoding="utf-8"); assert main(["report","--input",str(src),"--output",str(out)])==0; assert "ModelCompass report" in out.read_text(encoding="utf-8")
    finally: clean()
def test_data_validate(capsys):
    clean(); src=REPORTS/"test-cli-bundle.json"
    try:
        src.write_text(json.dumps({"scenarios":[{"id":"s","name":"S","weights":{"reasoning":1}}]}),encoding="utf-8"); assert main(["data","validate","--input",str(src)])==0; assert "valid" in capsys.readouterr().out
    finally: clean()
def test_serve_serves_html_over_http():
    server=create_server("127.0.0.1",0,[{"model_variant_id":"m"}]); thread=Thread(target=server.serve_forever,daemon=True); thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}/report.html") as response: assert response.status==200 and b"ModelCompass report" in response.read()
    finally: server.shutdown(); server.server_close(); thread.join(timeout=2); clean()
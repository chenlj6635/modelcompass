from __future__ import annotations
import argparse, json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .report import load_bundle, pareto_rows, read_rows, render_html, score_bundle, write_report
def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(prog="modelcompass"); s=p.add_subparsers(dest="command",required=True); d=s.add_parser("data").add_subparsers(dest="operation",required=True); v=d.add_parser("validate"); v.add_argument("--input",type=Path,required=True)
    for name in ("score","pareto","report","serve"):
        c=s.add_parser(name); c.add_argument("--input",type=Path,required=name in ("score","pareto"));
        if name != "serve": c.add_argument("--output",type=Path,default=Path("report.html" if name=="report" else name+".json"))
        if name=="score": c.add_argument("--scenario")
        if name=="pareto": c.add_argument("--axes",nargs=2,action="append",required=True)
        if name=="report": c.add_argument("--format",choices=("json","csv","html"),default="html")
        if name=="serve": c.add_argument("--host",choices=("localhost","127.0.0.1"),default="127.0.0.1"); c.add_argument("--port",type=int,default=8000)
    a=p.parse_args(argv)
    try:
        if a.command=="data": load_bundle(a.input); print("valid")
        elif a.command=="score": write_report(score_bundle(load_bundle(a.input),a.scenario),a.output,"json")
        elif a.command=="pareto": write_report(pareto_rows(read_rows(a.input),a.axes),a.output,"json")
        elif a.command=="report": write_report(read_rows(a.input) if a.input else [],a.output,a.format)
        else:
            page=render_html(read_rows(a.input) if a.input else []).encode();
            class H(BaseHTTPRequestHandler):
                def do_GET(self): self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(page))); self.end_headers(); self.wfile.write(page)
            srv=ThreadingHTTPServer((a.host,a.port),H); print(f"http://{a.host}:{srv.server_port}",flush=True)
            try: srv.serve_forever()
            except KeyboardInterrupt: pass
            finally: srv.server_close()
    except (ValueError,OSError,RuntimeError) as exc: print(f"error: {exc}",file=sys.stderr); return 1
    return 0
if __name__ == "__main__": raise SystemExit(main())
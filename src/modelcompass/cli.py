from __future__ import annotations
import argparse, json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .report import load_bundle, pareto_rows, read_rows, render_html, score_bundle, write_report

def create_server(host: str, port: int, rows: list[dict]) -> ThreadingHTTPServer:
    page = render_html(rows).encode("utf-8")
    payload = json.dumps(rows, ensure_ascii=False, allow_nan=False).encode("utf-8")
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            routes = {"/": ("text/html; charset=utf-8", page), "/report.html": ("text/html; charset=utf-8", page), "/report.json": ("application/json; charset=utf-8", payload)}
            if self.path not in routes: self.send_error(404); return
            content_type, body = routes[self.path]; self.send_response(200); self.send_header("Content-Type", content_type); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        def log_message(self, format: str, *args: object) -> None: return
    return ThreadingHTTPServer((host, port), Handler)

def build_parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="modelcompass"); s=p.add_subparsers(dest="command",required=True); d=s.add_parser("data"); ds=d.add_subparsers(dest="operation",required=True); v=ds.add_parser("validate"); v.add_argument("--input",type=Path,required=True)
    x=s.add_parser("score"); x.add_argument("--input",type=Path,required=True); x.add_argument("--scenario"); x.add_argument("--output",type=Path,default=Path("score.json"))
    x=s.add_parser("pareto"); x.add_argument("--input",type=Path,required=True); x.add_argument("--axes",nargs=2,action="append",required=True); x.add_argument("--output",type=Path,default=Path("pareto.json"))
    x=s.add_parser("report"); x.add_argument("--input",type=Path); x.add_argument("--format",choices=("json","csv","html"),default="html"); x.add_argument("--output",type=Path,default=Path("report.html"))
    x=s.add_parser("serve"); x.add_argument("--input",type=Path); x.add_argument("--host",choices=("localhost","127.0.0.1"),default="127.0.0.1"); x.add_argument("--port",type=int,default=8000)
    return p

def main(argv: list[str] | None = None) -> int:
    a=build_parser().parse_args(argv)
    try:
        if a.command=="data": load_bundle(a.input); print("valid")
        elif a.command=="score": write_report(score_bundle(load_bundle(a.input),a.scenario),a.output,"json")
        elif a.command=="pareto": write_report(pareto_rows(read_rows(a.input),a.axes),a.output,"json")
        elif a.command=="report": write_report(read_rows(a.input) if a.input else [],a.output,a.format)
        else:
            server=create_server(a.host,a.port,read_rows(a.input) if a.input else []); print(f"http://{a.host}:{server.server_port}",flush=True)
            try: server.serve_forever()
            except KeyboardInterrupt: pass
            finally: server.server_close()
    except (ValueError,OSError,RuntimeError) as exc: print(f"error: {exc}",file=sys.stderr); return 1
    return 0
if __name__ == "__main__": raise SystemExit(main())
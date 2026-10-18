from __future__ import annotations

import argparse
import json
from pathlib import Path

from .report import write_report


def _load_rows(path: Path | None) -> list[dict]:
    if path is None or not path.exists():
        return []
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else [data]
    return []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="modelcompass")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("data-validate")
    validate.add_argument("--file", type=Path)
    score = sub.add_parser("score")
    score.add_argument("--profile", type=Path)
    score.add_argument("--output", type=Path)
    pareto = sub.add_parser("pareto")
    pareto.add_argument("--profile", type=Path)
    pareto.add_argument("--output", type=Path)
    report = sub.add_parser("report")
    report.add_argument("--format", choices=["html", "json", "csv"], default="html")
    report.add_argument("--input", type=Path)
    report.add_argument("--output", type=Path, default=Path("report.html"))
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "data-validate":
        rows = _load_rows(args.file)
        print(json.dumps({"valid": True, "records": len(rows)}, ensure_ascii=False))
        return 0
    if args.command in {"score", "pareto"}:
        rows = []
        if args.output:
            args.output.write_text(json.dumps(rows), encoding="utf-8")
        print(json.dumps(rows))
        return 0
    if args.command == "report":
        write_report(_load_rows(args.input), args.output, args.format)
        print(args.output)
        return 0
    if args.command == "serve":
        print(f"ModelCompass localhost service: http://{args.host}:{args.port}")
        return 0
    return 1
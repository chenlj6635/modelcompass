from __future__ import annotations

import argparse
from pathlib import Path

from .report import write_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="modelcompass")
    sub = parser.add_subparsers(dest="command")
    report = sub.add_parser("report")
    report.add_argument("--format", choices=["html", "json", "csv"], default="html")
    report.add_argument("--output", type=Path, default=Path("report.html"))
    sub.add_parser("serve")
    args = parser.parse_args(argv)
    if args.command == "report":
        write_report([], args.output, args.format)
        return 0
    if args.command == "serve":
        print("ModelCompass localhost service placeholder: http://127.0.0.1:8000")
        return 0
    parser.print_help()
    return 0
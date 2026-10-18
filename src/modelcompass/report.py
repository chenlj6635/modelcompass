from __future__ import annotations

import csv
import html
import json
from pathlib import Path


def render_html(rows: list[dict], *, title: str = "ModelCompass report") -> str:
    body = "\n".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(k, '')))}</td>" for k in ("model_variant_id", "quality", "public_task_cost", "coverage", "confidence")) + "</tr>" for row in rows)
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title><style>body{{font-family:system-ui;margin:2rem}}table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:.4rem}}</style></head><body><h1>{html.escape(title)}</h1><table><thead><tr><th>Model variant</th><th>Quality</th><th>Public task cost</th><th>Coverage</th><th>Confidence</th></tr></thead><tbody>{body}</tbody></table></body></html>"


def write_report(rows: list[dict], output: Path, fmt: str) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    elif fmt == "csv":
        fields = ["model_variant_id", "quality", "public_task_cost", "coverage", "confidence"]
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    elif fmt == "html":
        output.write_text(render_html(rows), encoding="utf-8")
    else:
        raise ValueError(f"unsupported format: {fmt}")
    return output
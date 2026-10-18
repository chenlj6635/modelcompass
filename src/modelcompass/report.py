from __future__ import annotations
import csv, html, json, math
from dataclasses import asdict
from pathlib import Path
from typing import Any
from . import schemas
SCHEMA_TYPES = {"model_identities": schemas.ModelIdentity, "model_variants": schemas.ModelVariant, "deployments": schemas.Deployment, "benchmarks": schemas.BenchmarkObservation, "prices": schemas.PriceObservation, "capabilities": schemas.CapabilityObservation, "task_costs": schemas.PublicTaskCostObservation, "scenarios": schemas.ScenarioProfile, "snapshots": schemas.SourceSnapshot}
FIELDS = ("model_variant_id", "quality", "public_task_cost", "coverage", "confidence", "sources", "warnings")
def _json(path: Path): return json.loads(path.read_text(encoding="utf-8-sig"))
def validate_bundle(bundle: dict) -> None:
    if not isinstance(bundle, dict) or not bundle: raise ValueError("bundle must be a non-empty JSON object")
    if set(bundle) - set(SCHEMA_TYPES): raise ValueError(f"unknown bundle collections: {sorted(set(bundle)-set(SCHEMA_TYPES))}")
    for key, values in bundle.items():
        if not isinstance(values, list): raise ValueError(f"{key} must be a list")
        for i, value in enumerate(values):
            try: SCHEMA_TYPES[key].model_validate(value)
            except ValueError as exc: raise ValueError(f"{key}[{i}]: {exc}") from exc
def load_bundle(path: Path) -> dict:
    payload = _json(path)
    if isinstance(payload, dict) and "source_id" in payload and "fetched_at" in payload:
        schemas.SourceSnapshot.model_validate(payload)
        return {"snapshots": [payload]}
    validate_bundle(payload)
    return payload
def read_rows(path: Path) -> list[dict]:
    rows = _json(path)
    if not isinstance(rows, list) or any(not isinstance(x, dict) for x in rows): raise ValueError("rows must be a JSON array of objects")
    return rows
def score_bundle(bundle: dict, scenario_id: str | None = None) -> list[dict]:
    from .scoring import score_scenario
    from .normalize import fixed_scale
    scenarios = bundle.get("scenarios", []); profile = next((x for x in scenarios if x["id"] == scenario_id), None) if scenario_id else (scenarios[0] if len(scenarios) == 1 else None)
    if profile is None: raise ValueError("choose --scenario unless the bundle has exactly one scenario")
    scenario = schemas.ScenarioProfile.model_validate(profile); rows = []
    for variant in bundle.get("model_variants", []):
        vid = variant["variant_id"]; obs = []; sources = []; warnings = []
        for raw in bundle.get("benchmarks", []):
            if raw["model_variant_id"] != vid: continue
            item = schemas.BenchmarkObservation.model_validate(raw); sources.append(item.source_url); scales = {"accuracy": (0, 1), "fraction": (0, 1), "percent": (0, 100), "percentage": (0, 100)}
            if item.score_unit not in scales: warnings.append(f"unsupported score unit: {item.score_unit}"); continue
            lo, hi = scales[item.score_unit]
            if not math.isfinite(item.score) or not lo <= item.score <= hi: warnings.append(f"out-of-scale benchmark: {item.benchmark_id}"); continue
            obs.append({**item.model_dump(mode="json"), "normalized_score": fixed_scale(item.score, lower=lo, upper=hi), "confidence_score": {"high": 1.0, "medium": .75, "low": .5}[item.confidence]})
        result = asdict(score_scenario(vid, obs, scenario.weights)); costs = [x for x in bundle.get("task_costs", []) if x["model_variant_id"] == vid]; sources.extend(x["source_url"] for x in costs); cost = costs[0]["cost_usd"] if len(costs) == 1 else None
        if len(costs) != 1: warnings.append("public task cost unknown or ambiguous")
        if result["coverage"] < 1: warnings.append("insufficient data: incomplete coverage")
        if result["quality"] is None: warnings.append("insufficient data: no quality estimate")
        warnings.extend(f"missing ability cluster: {x}" for x in result["missing_clusters"])
        rows.append({**result, "public_task_cost": cost, "sources": sources, "warnings": warnings})
    return rows
def pareto_rows(rows: list[dict], axes: list[tuple[str, str]]) -> list[dict]:
    from .pareto import pareto_front
    if len(axes) not in (2, 3) or any(d not in ("min", "max") for _, d in axes): raise ValueError("axes must contain 2 or 3 dimensions with min/max directions")
    complete = [r for r in rows if all(isinstance(r.get(n), (int, float)) and not isinstance(r.get(n), bool) and math.isfinite(r[n]) for n, _ in axes)]
    return pareto_front(complete, axes)
def _display(value: Any) -> str:
    if value is None: return "Unknown"
    return json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (list, dict)) else str(value)
def _warn(row: dict) -> list:
    out = list(row.get("warnings") or [])
    if row.get("quality") is None or row.get("coverage", 0) < 1: out.append("Insufficient data")
    if not row.get("sources"): out.append("Sources unavailable")
    return out
def render_html(rows: list[dict], *, title: str = "ModelCompass report") -> str:
    headers = ("Model variant", "Quality", "Public task cost", "Coverage", "Confidence", "Sources", "Warnings"); body = "".join("<tr>" + "".join(f"<td>{html.escape(_display({**r, 'warnings': _warn(r)}.get(k)))}</td>" for k in FIELDS) + "</tr>" for r in rows)
    if not body: body = '<tr><td colspan="7">Insufficient data: no model rows</td></tr>'
    head = "".join(f"<th>{x}</th>" for x in headers)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>body{{font:14px system-ui;margin:24px;color:#202124}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #cbd1d6;padding:10px;text-align:left;vertical-align:top;overflow-wrap:anywhere}}th{{background:#eef2f5}}</style></head><body><h1>{html.escape(title)}</h1><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></body></html>'''
def write_report(rows: list[dict], output: Path, fmt: str) -> Path:
    if fmt not in ("json", "csv", "html"): raise ValueError(f"unsupported format: {fmt}")
    rows = [{**r, "warnings": _warn(r)} for r in rows]; output.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json": output.write_text(json.dumps(rows, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    elif fmt == "html": output.write_text(render_html(rows), encoding="utf-8")
    else:
        with output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS); writer.writeheader(); writer.writerows({k: _display(r.get(k)) for k in FIELDS} for r in rows)
    return output
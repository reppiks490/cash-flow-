#!/usr/bin/env python3
"""Scan official permit sources and emit reviewable source-change reports."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from moneyfall.permit_watch import catalog_urls, compare_snapshots, scan_sources


ROOT = Path(__file__).resolve().parents[1]


def load_datasets(paths):
    datasets = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("municipalities"), list):
            raise ValueError(f"Invalid permit-friction dataset: {path}")
        datasets.append(payload)
    if not datasets:
        raise ValueError("No permit-friction datasets found")
    return datasets


def load_previous(path):
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Previous snapshot must be a JSON object")
    return payload


def write_summary(path, compared, retrieved_at):
    groups = {state: [] for state in ("changed", "error", "baseline", "unchanged")}
    for url, record in compared.items():
        groups.setdefault(record["state"], []).append((url, record))
    lines = [
        "# Permit source watch",
        "",
        f"Retrieved: `{retrieved_at}`",
        f"Sources checked: **{len(compared)}**",
        f"Changed: **{len(groups['changed'])}** · Errors: **{len(groups['error'])}** · Baseline: **{len(groups['baseline'])}** · Unchanged: **{len(groups['unchanged'])}**",
        "",
    ]
    for state in ("changed", "error", "baseline"):
        if not groups[state]:
            continue
        lines += [f"## {state.title()}", ""]
        for url, record in groups[state]:
            markets = ", ".join(record.get("markets", [])) or "unmapped"
            suffix = f" — {record.get('error')}" if record.get("error") else ""
            lines.append(f"- `{markets}` — {url}{suffix}")
        lines.append("")
    lines += [
        "Changed/error states are review triggers only. They do not automatically alter a municipal requirement or client-facing conclusion.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Monitor official permit sources for meaningful content changes")
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--fail-on-change", action="store_true")
    parser.add_argument("--dataset", action="append", type=Path, default=[])
    args = parser.parse_args(argv)

    dataset_paths = args.dataset or sorted((ROOT / "config").glob("permit_friction_*.json"))
    datasets = load_datasets(dataset_paths)
    catalog = catalog_urls(datasets)
    previous = load_previous(args.previous)
    current = scan_sources(catalog)
    compared = compare_snapshots(previous, current)
    retrieved_at = datetime.now(timezone.utc).isoformat()

    args.snapshot.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)

    stable_snapshot = {
        url: {k: v for k, v in record.items() if k != "state"}
        for url, record in compared.items()
        if not record.get("error")
    }
    # Preserve the last known good fingerprint when a fetch fails so recovery is
    # compared against the previous successful observation rather than rebased.
    for url, old in previous.items():
        if url not in stable_snapshot and isinstance(old, dict) and old.get("fingerprint"):
            stable_snapshot[url] = old

    args.snapshot.write_text(json.dumps(stable_snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = {
        "retrieved_at": retrieved_at,
        "source_count": len(compared),
        "states": compared,
    }
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary(args.summary, compared, retrieved_at)

    counts = {state: sum(1 for item in compared.values() if item["state"] == state) for state in ("changed", "error", "baseline", "unchanged")}
    print(json.dumps({"sources": len(compared), **counts}, sort_keys=True))
    if args.fail_on_change and (counts["changed"] or counts["error"]):
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"permit-source-watch error: {exc}", file=sys.stderr)
        raise SystemExit(1)

#!/usr/bin/env python3
"""Policy helpers for Achitic GGUF quantization wrappers."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


FALLBACK_RE = re.compile(r"\b(fallback|fall\s+back|falling\s+back)\b", re.IGNORECASE)
TENSOR_RE = re.compile(r"([A-Za-z0-9_./:-]*(?:weight|bias|norm)[A-Za-z0-9_./:-]*)")
TYPE_RE = re.compile(r"\b(?:to|as)\s+([IQF]?Q?[0-9][A-Za-z0-9_]*|F(?:16|32))\b", re.IGNORECASE)


def parse_fallbacks(text: str) -> list[dict[str, str]]:
    records = []
    for line_no,line in enumerate(text.splitlines(),1):
        if not FALLBACK_RE.search(line):
            continue
        tensor_match = TENSOR_RE.search(line)
        type_match = TYPE_RE.search(line)
        records.append({
            "line_no": line_no,
            "tensor": tensor_match.group(1) if tensor_match else "",
            "fallback_type": type_match.group(1) if type_match else "",
            "line": line.strip(),
        })
    return records


def load_report(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid verify report JSON: {path}: {exc}") from exc


def normal_metrics(report: dict) -> dict:
    normal = report.get("normal")
    if not isinstance(normal,dict):
        raise SystemExit("verify report must contain a normal metrics object")
    return normal


def cmd_check_fallback(args: argparse.Namespace) -> int:
    records = parse_fallbacks(Path(args.log).read_text(encoding="utf8",errors="replace"))
    summary = {"fallback_count": len(records), "fallbacks": records}
    if args.summary:
        Path(args.summary).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    if records:
        print("quantization fallback detected:",json.dumps(summary,ensure_ascii=False,sort_keys=True))
        return 0 if args.allow_experimental else 2
    print("quantization fallback check: no fallback records found")
    return 0


def cmd_check_report(args: argparse.Namespace) -> int:
    report = load_report(Path(args.report))
    normal = normal_metrics(report)
    status = report.get("status")
    max_delta = float(normal.get("max_abs_delta",float("inf")))
    top1 = float(normal.get("top1_match",-1.0))
    passed = status == "PASS" and max_delta <= args.max_delta and top1 >= args.top1_min
    payload = {
        "status": status,
        "max_abs_delta": max_delta,
        "max_delta_threshold": args.max_delta,
        "top1_match": top1,
        "top1_threshold": args.top1_min,
        "passed": passed,
    }
    print("quantization verification policy:",json.dumps(payload,ensure_ascii=False,sort_keys=True))
    if passed or args.allow_experimental:
        return 0
    return 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd",required=True)
    p = sub.add_parser("check-fallback")
    p.add_argument("--log",required=True)
    p.add_argument("--summary")
    p.add_argument("--allow-experimental",action="store_true")
    p = sub.add_parser("check-report")
    p.add_argument("--report",required=True)
    p.add_argument("--max-delta",type=float,required=True)
    p.add_argument("--top1-min",type=float,required=True)
    p.add_argument("--allow-experimental",action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.cmd == "check-fallback":
        raise SystemExit(cmd_check_fallback(args))
    if args.cmd == "check-report":
        raise SystemExit(cmd_check_report(args))
    raise SystemExit(f"unknown command {args.cmd}")


if __name__ == "__main__":
    main()

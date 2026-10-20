from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .audit import audit_manifest
from .github import collect_manifest
from .render import render_markdown


def _write(text: str, output: str | None) -> None:
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="" if text.endswith("\n") else "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="repo-proof", description="Audit GitHub repository and milestone evidence.")
    sub = parser.add_subparsers(dest="command", required=True)

    collect = sub.add_parser("collect", help="Collect an evidence manifest from GitHub.")
    collect.add_argument("repository", help="Repository in owner/name form.")
    collect.add_argument("--milestone", type=int, required=True, help="GitHub milestone number.")
    collect.add_argument("--output", "-o", required=True, help="Manifest JSON output path.")

    audit = sub.add_parser("audit", help="Audit a collected manifest.")
    audit.add_argument("manifest", help="Path to manifest JSON.")
    audit.add_argument("--format", choices=("markdown", "json"), default="markdown")
    audit.add_argument("--output", "-o", help="Report output path; defaults to stdout.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "collect":
            manifest = collect_manifest(args.repository, args.milestone)
            _write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", args.output)
            return 0

        path = Path(args.manifest)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        report = audit_manifest(manifest)
        if args.format == "json":
            output = json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n"
        else:
            output = render_markdown(report, source=str(path))
        _write(output, args.output)
        return 0 if report.decision == "accept" else 2
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"repo-proof: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

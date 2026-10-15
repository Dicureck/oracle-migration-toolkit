"""Offline CLI; only reads local files and generates reports/synthetic datasets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from . import __version__
from . import contracts, planner, reconcile, scanner, synthetic


def _save(body: str, output: str | None) -> None:
    if output:
        dest = Path(output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
        print(f"Written {dest}")
    else:
        print(body, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="oracle-migration-lab", description="Offline, review-only SQL Server → Oracle migration lab")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    assess = commands.add_parser("assess", help="Identify T-SQL migration risks in local SQL source")
    assess.add_argument("path", type=Path)
    assess.add_argument("--format", choices=["json", "markdown"], default="json")
    assess.add_argument("--output", help="Destination report path")
    plan = commands.add_parser("plan", help="Validate object inventory and compute dependency order")
    plan.add_argument("inventory", type=Path)
    plan.add_argument("--format", choices=["json", "markdown"], default="json")
    plan.add_argument("--output")
    verify = commands.add_parser("verify", help="Verify synthetic business-rule reference contracts")
    verify.add_argument("contracts", type=Path)
    verify.add_argument("--output")
    comparison = commands.add_parser("reconcile", help="Compare two exported CSV outputs including duplicate rows")
    comparison.add_argument("left", type=Path)
    comparison.add_argument("right", type=Path)
    comparison.add_argument("--output")
    generate = commands.add_parser("generate", help="Generate reproducible fake customer/order data")
    generate.add_argument("--out", type=Path, required=True)
    generate.add_argument("--customers", type=int, default=200)
    generate.add_argument("--orders", type=int, default=3000)
    generate.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)
    try:
        if args.command == "assess":
            report = scanner.assess(args.path)
            body = scanner.to_markdown(report) if args.format == "markdown" else json.dumps(report, indent=2) + "\n"
            _save(body, args.output)
        elif args.command == "plan":
            report = planner.as_dict(planner.make_plan(planner.load_inventory(args.inventory)))
            body = planner.to_markdown(report) if args.format == "markdown" else json.dumps(report, indent=2) + "\n"
            _save(body, args.output)
        elif args.command == "verify":
            report = contracts.verify_contracts(args.contracts)
            _save(json.dumps(report, indent=2) + "\n", args.output)
            return 1 if report["failed"] else 0
        elif args.command == "reconcile":
            report = reconcile.reconcile(args.left, args.right)
            _save(json.dumps(report, indent=2) + "\n", args.output)
            return 0 if report["matching"] else 1
        else:
            report = synthetic.generate(args.out, args.customers, args.orders, args.seed)
            _save(json.dumps(report, indent=2) + "\n", None)
    except (ValueError, FileNotFoundError, FileExistsError, KeyError, json.JSONDecodeError, PermissionError) as e:
        parser.exit(2, f"Error: {e}\n")
    return 0

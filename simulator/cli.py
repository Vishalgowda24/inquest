"""Command line entry point for the independent simulator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from simulator import __version__
from simulator.core.export import write_export
from simulator.scenarios.registry import SCENARIO_GENERATORS

SCENARIOS = SCENARIO_GENERATORS


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sim", description="Generate deterministic synthetic incident telemetry")
    parser.add_argument("command", choices=("list", "run"))
    parser.add_argument("--scenario", default="clean_bad_deploy")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--output", type=Path, help="export directory (default: scenario seed export folder)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "list":
        for name in SCENARIOS:
            sys.stdout.write(f"{name}\tavailable\n")
        return 0
    if args.scenario not in SCENARIOS:
        sys.stderr.write(f"unknown scenario {args.scenario!r}; available: {', '.join(SCENARIOS)}\n")
        return 2
    if args.seed < 0:
        sys.stderr.write("seed must be a nonnegative integer\n")
        return 2
    try:
        dataset = SCENARIOS[args.scenario](args.seed)
        scenario_id = dataset.manifest.scenario_id
        export_dir = args.output or Path("simulator/exports") / scenario_id / f"seed_{args.seed}" / "export"
        truth_path = Path("simulator/sim_truth") / args.scenario / f"seed_{args.seed}.truth.json"
        write_export(dataset, export_dir, truth_path)
    except (ValidationError, OSError, ValueError) as exc:
        sys.stderr.write(f"scenario generation failed: {exc}\n")
        return 1
    sys.stdout.write(f"generated {args.scenario} seed={args.seed} with {len(dataset.metrics)} metrics, {len(dataset.spans)} spans\n")
    sys.stdout.write(f"export: {export_dir}\ntruth: {truth_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

import logging
import shutil
from argparse import ArgumentParser
from pathlib import Path
from time import sleep

import failure_parser
from print_failures import print_failures
from tool_maven import Maven
from tool_pytest import Pytest


def main(args):
    tools = {"pytest": Pytest, "maven": Maven}

    # Environment setup
    directory = Path(args.directory)
    output_folder = Path(args.output_folder if args.output_folder else "./output")
    no_stress_runs = args.no_stress_runs
    stress_runs = args.stress_runs
    config_file = (
        Path(__file__).parent / "stressConfigurations.json" if stress_runs > 0 else None
    )

    arguments = ""

    tool = tools[args.tool](directory, arguments, config_file, output_folder)

    # Run tests

    logging.basicConfig(level=logging.DEBUG)
    logging.info(
        f"Running {args.tool} with {no_stress_runs} no-stress runs and {stress_runs} stress runs..."
    )

    sleep(2)

    for i in range(0, no_stress_runs):
        tool.no_stress(i)

    for i in range(0, stress_runs):
        tool.stress(i)

    # Show results
    failures = failure_parser.parse(output_folder)
    if len(failures) != 0:
        print_failures(failures, no_stress_runs, stress_runs, 4)
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "tool", choices=["pytest", "maven"], help="specify testing tool"
    )

    parser.add_argument("directory", help="specify directory")

    parser.add_argument("-e", "--extra-arguments", help="specify extra arguments")

    parser.add_argument(
        "-sr",
        "--stress-runs",
        type=int,
        default=1,
        help="specify number of stress runs",
    )

    parser.add_argument(
        "-nsr",
        "--no-stress-runs",
        type=int,
        default=1,
        help="specify number of no-stress runs",
    )

    parser.add_argument("-o", "--output-folder", help="specify output folder")

    args = parser.parse_args()

    main(args)

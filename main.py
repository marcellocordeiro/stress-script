#!/usr/bin/env python3

# from colorama import Fore, Back, Style
import logging
import shutil
from argparse import ArgumentParser
from pathlib import Path
from time import sleep

import failure_parser
from tool_maven import Maven
from tool_pytest import Pytest


def main(args):
    tools = {"pytest": Pytest, "maven": Maven}

    # Environment setup
    directory = Path(args.directory)
    output_folder = Path(args.output_folder if args.output_folder else "./output")
    no_stress_suns = args.no_stress_runs
    stress_runs = args.stress_runs
    config_file = (
        Path(__file__).parent / "stressConfigurations.json" if stress_runs > 0 else None
    )

    arguments = ""

    tool = tools[args.tool](directory, arguments, config_file, output_folder)

    # Run tests

    logging.basicConfig(level=logging.DEBUG)
    logging.info(
        f"Running {args.tool} with {no_stress_suns} no-stress runs and {stress_runs} stress runs..."
    )

    sleep(2)

    for i in range(0, no_stress_suns):
        tool.no_stress(i)

    for i in range(0, stress_runs):
        tool.stress(i)

    # Describe results

    failures = failure_parser.parse(output_folder)

    if len(failures) != 0:
        print("--- The following tests have failed ---")

        no_stress_failures = 0

        for failure in failures:
            print(f"stress-ng configuration: {failure.config}")
            print(f"run number: {failure.run_number}")
            print(f"classname: {failure.class_name}")
            print(f"name: {failure.name}")
            print(f"description: {failure.description[:200]}")
            print("==========================")

            if failure.config == "no-stress":
                no_stress_failures += 1

        print("\n--- Summary ---")
        print(f"{len(failures)} failures")
        if no_stress_failures != 0:
            print(
                f"...of which {no_stress_failures} failed under normal, no-stress, conditions"
            )

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

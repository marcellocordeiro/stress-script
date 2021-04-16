#!/usr/bin/env python3

import argparse
import json
import pathlib
import shutil
import time

from failureParser import parseFailures
from toolMaven import toolMaven
from toolPytest import pythonSetup, toolPytest
from util import subprocessPopen, subprocessRun


def noStress(directory, arguments, outputFolder, runNumber, toolFunction):
    toolFunction(directory, arguments, outputFolder /
                 f"report.no-stress.{runNumber}")


def stress(directory, arguments, outputFolder, configFile, runNumber, toolFunction):
    with open(configFile) as jsonFile:
        configurations = json.load(jsonFile)

    for i, config in enumerate(configurations):
        stressNgCommand = f"stress-ng --cpu {config['cpuWorkers']} --cpu-load {config['cpuLoad']} --vm {config['vmWorkers']} --vm-bytes {config['vmBytes']}%"
        stressNgSubprocess = subprocessPopen(stressNgCommand)

        time.sleep(1)

        toolFunction(directory, arguments, outputFolder /
                     f"report.{i}.{runNumber}")

        stressNgSubprocess.kill()


def main(args):
    directory = pathlib.Path(args.directory)
    outputFolder = pathlib.Path(
        args.output_folder if args.output_folder else './output')

    shutil.rmtree(outputFolder, ignore_errors=True)
    outputFolder.mkdir(parents=True, exist_ok=True)

    configFile = pathlib.Path(__file__).parent / 'stressConfigurations.json'

    arguments = ''

    noStressRuns = args.no_stress_runs
    stressRuns = args.no_stress_runs

    if args.tool == 'pytest':
        pythonSetup(directory)
        toolFunction = toolPytest
    elif args.tool == 'maven':
        toolFunction = toolMaven
    else:
        exit(1)

    print(
        f"Running {args.tool} with {noStressRuns} no-stress runs and {stressRuns} stress runs...")

    for i in range(0, noStressRuns):
        noStress(directory, arguments, outputFolder, i, toolFunction)

    for i in range(0, stressRuns):
        stress(directory, arguments, outputFolder, configFile, i, toolFunction)

    failures = parseFailures(outputFolder)

    if len(failures) != 0:
        print("--- The following tests have failed ---")

        noStressFailures = 0

        for failure in failures:
            print(f"stress-ng configuration: {failure.configuration}")
            print(f"run number: {failure.runNumber}")
            print(f"classname: {failure.className}")
            print(f"name: {failure.name}")
            print(f"description: {failure.description}")
            print('==========================')

            if failure.configuration == 'no-stress':
                noStressFailures = noStressFailures + 1

        print('\n--- Summary ---')
        print(f"{len(failures)} failures in ")
        if noStressFailures != 0:
            print(f"...of which {noStressFailures} failed under normal, no-stress, conditions")

        exit(1)
    else:
        exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'tool', choices=['pytest', 'maven'], help='specify testing tool')

    parser.add_argument('directory', help='specify directory')

    parser.add_argument('-e', '--extra-arguments',
                        help="specify extra arguments")

    parser.add_argument('-sr', '--stress-runs', type=int,
                        default=1, help='specify number of stress runs')

    parser.add_argument('-nsr', '--no-stress-runs', type=int,
                        default=1, help='specify number of no-stress runs')

    parser.add_argument('-o', '--output-folder', help="specify output folder")

    args = parser.parse_args()

    main(args)
